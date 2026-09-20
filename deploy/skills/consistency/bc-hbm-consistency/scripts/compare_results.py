#!/usr/bin/env python3
"""Compare order-independent keyed records or class-aware detections in JSON."""

import argparse
import json
import math
import sys
from pathlib import Path


def nested_value(value, field_path):
    current = value
    if not field_path:
        return current
    for part in field_path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


def load_records(path, records_path):
    document = json.loads(Path(path).read_text())
    records = nested_value(document, records_path)
    if not isinstance(records, list):
        raise ValueError("records path must resolve to a list")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError("every record must be a JSON object")
    return records


def equivalent(reference, candidate, atol, rtol):
    if isinstance(reference, (int, float)) and isinstance(candidate, (int, float)):
        return math.isclose(reference, candidate, abs_tol=atol, rel_tol=rtol)
    if type(reference) is not type(candidate):
        return False
    if isinstance(reference, list):
        return len(reference) == len(candidate) and all(
            equivalent(left, right, atol, rtol)
            for left, right in zip(reference, candidate)
        )
    if isinstance(reference, dict):
        return reference.keys() == candidate.keys() and all(
            equivalent(reference[key], candidate[key], atol, rtol)
            for key in reference
        )
    return reference == candidate


def select_values(record, fields):
    if not fields:
        return record
    return {field: nested_value(record, field) for field in fields}


def compare_keyed(args, reference_records, candidate_records):
    def build_index(records, label):
        result = {}
        for record in records:
            key = tuple(nested_value(record, field) for field in args.key_fields)
            if key in result:
                raise ValueError("{} contains duplicate key {}".format(label, key))
            result[key] = record
        return result

    reference_index = build_index(reference_records, "reference")
    candidate_index = build_index(candidate_records, "candidate")
    reference_keys = set(reference_index)
    candidate_keys = set(candidate_index)
    common_keys = sorted(reference_keys & candidate_keys, key=repr)
    mismatches = []
    for key in common_keys:
        left = select_values(reference_index[key], args.value_fields)
        right = select_values(candidate_index[key], args.value_fields)
        if not equivalent(left, right, args.atol, args.rtol):
            mismatches.append({"key": key, "reference": left, "candidate": right})

    result = {
        "mode": "keyed",
        "reference_count": len(reference_records),
        "candidate_count": len(candidate_records),
        "missing_keys": sorted(reference_keys - candidate_keys, key=repr)[:20],
        "extra_keys": sorted(candidate_keys - reference_keys, key=repr)[:20],
        "value_mismatch_count": len(mismatches),
        "value_mismatches": mismatches[:20],
    }
    result["pass"] = not (
        reference_keys - candidate_keys or candidate_keys - reference_keys or mismatches
    )
    return result


def compare_detections(args, reference_records, candidate_records):
    try:
        import numpy as np
        from scipy.optimize import linear_sum_assignment
    except ImportError as error:
        raise RuntimeError(
            "detection mode requires numpy and scipy; install scripts/requirements.txt"
        ) from error

    classes = sorted(
        {
            nested_value(record, args.class_field)
            for record in reference_records + candidate_records
        },
        key=repr,
    )
    matches = []
    unmatched_reference = []
    unmatched_candidate = []
    value_mismatches = []

    for class_value in classes:
        reference_group = [
            record
            for record in reference_records
            if nested_value(record, args.class_field) == class_value
        ]
        candidate_group = [
            record
            for record in candidate_records
            if nested_value(record, args.class_field) == class_value
        ]
        if not reference_group:
            unmatched_candidate.extend(candidate_group)
            continue
        if not candidate_group:
            unmatched_reference.extend(reference_group)
            continue

        reference_points = np.asarray(
            [
                [float(nested_value(record, field)) for field in args.coord_fields]
                for record in reference_group
            ]
        )
        candidate_points = np.asarray(
            [
                [float(nested_value(record, field)) for field in args.coord_fields]
                for record in candidate_group
            ]
        )
        costs = np.linalg.norm(
            reference_points[:, None, :] - candidate_points[None, :, :], axis=2
        )
        reference_indices, candidate_indices = linear_sum_assignment(costs)
        accepted_reference = set()
        accepted_candidate = set()
        for reference_index, candidate_index in zip(
            reference_indices.tolist(), candidate_indices.tolist()
        ):
            distance = float(costs[reference_index, candidate_index])
            if distance > args.max_distance:
                continue
            accepted_reference.add(reference_index)
            accepted_candidate.add(candidate_index)
            match = {
                "class": class_value,
                "reference_index": reference_index,
                "candidate_index": candidate_index,
                "distance": distance,
            }
            matches.append(match)
            left = select_values(reference_group[reference_index], args.value_fields)
            right = select_values(candidate_group[candidate_index], args.value_fields)
            if args.value_fields and not equivalent(left, right, args.atol, args.rtol):
                value_mismatches.append(
                    {"match": match, "reference": left, "candidate": right}
                )

        unmatched_reference.extend(
            record
            for index, record in enumerate(reference_group)
            if index not in accepted_reference
        )
        unmatched_candidate.extend(
            record
            for index, record in enumerate(candidate_group)
            if index not in accepted_candidate
        )

    result = {
        "mode": "detections",
        "reference_count": len(reference_records),
        "candidate_count": len(candidate_records),
        "matched_count": len(matches),
        "max_matched_distance": max(
            (match["distance"] for match in matches), default=0.0
        ),
        "unmatched_reference_count": len(unmatched_reference),
        "unmatched_candidate_count": len(unmatched_candidate),
        "value_mismatch_count": len(value_mismatches),
        "unmatched_reference": unmatched_reference[:20],
        "unmatched_candidate": unmatched_candidate[:20],
        "value_mismatches": value_mismatches[:20],
    }
    result["pass"] = not (
        unmatched_reference or unmatched_candidate or value_mismatches
    )
    return result


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)

    def add_common(subparser):
        subparser.add_argument("reference")
        subparser.add_argument("candidate")
        subparser.add_argument("--records-path", default="")
        subparser.add_argument("--value-fields", nargs="*", default=[])
        subparser.add_argument("--atol", type=float, default=0.0)
        subparser.add_argument("--rtol", type=float, default=0.0)

    keyed = subparsers.add_parser("keyed", help="compare records by stable keys")
    add_common(keyed)
    keyed.add_argument("--key-fields", nargs="+", required=True)

    detections = subparsers.add_parser(
        "detections", help="match detections by class and geometry"
    )
    add_common(detections)
    detections.add_argument("--class-field", required=True)
    detections.add_argument("--coord-fields", nargs="+", required=True)
    detections.add_argument("--max-distance", type=float, required=True)
    return parser


def main():
    args = build_parser().parse_args()
    try:
        reference_records = load_records(args.reference, args.records_path)
        candidate_records = load_records(args.candidate, args.records_path)
        if args.mode == "keyed":
            result = compare_keyed(args, reference_records, candidate_records)
        else:
            result = compare_detections(args, reference_records, candidate_records)
    except (OSError, ValueError, KeyError, IndexError, RuntimeError) as error:
        print(json.dumps({"pass": False, "error": str(error)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
