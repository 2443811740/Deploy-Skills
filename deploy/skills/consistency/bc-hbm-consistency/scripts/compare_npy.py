#!/usr/bin/env python3
"""Compare two NPY tensors and emit machine-readable metrics."""

import argparse
import json
import sys

import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference")
    parser.add_argument("candidate")
    parser.add_argument("--atol", type=float, default=0.0)
    parser.add_argument("--rtol", type=float, default=0.0)
    parser.add_argument("--equal-nan", action="store_true")
    parser.add_argument("--allow-dtype-mismatch", action="store_true")
    args = parser.parse_args()

    try:
        reference = np.load(args.reference, allow_pickle=False)
        candidate = np.load(args.candidate, allow_pickle=False)
    except (OSError, ValueError) as error:
        print(json.dumps({"pass": False, "error": str(error)}))
        return 2

    result = {
        "reference_shape": list(reference.shape),
        "candidate_shape": list(candidate.shape),
        "reference_dtype": reference.dtype.name,
        "candidate_dtype": candidate.dtype.name,
    }

    if reference.shape != candidate.shape:
        result.update({"pass": False, "reason": "shape-mismatch"})
        print(json.dumps(result, sort_keys=True))
        return 1

    dtype_equal = reference.dtype == candidate.dtype
    result["dtype_equal"] = dtype_equal

    numeric = np.issubdtype(reference.dtype, np.number) and np.issubdtype(
        candidate.dtype, np.number
    )
    if not numeric:
        values_equal = bool(np.array_equal(reference, candidate))
        result.update({"values_equal": values_equal})
        result["pass"] = values_equal and (dtype_equal or args.allow_dtype_mismatch)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["pass"] else 1

    reference_values = reference.astype(np.float64, copy=False)
    candidate_values = candidate.astype(np.float64, copy=False)
    integer_exact = (
        np.issubdtype(reference.dtype, np.integer)
        and np.issubdtype(candidate.dtype, np.integer)
        and args.atol == 0.0
        and args.rtol == 0.0
    )
    if integer_exact:
        close = reference == candidate
    else:
        close = np.isclose(
            reference_values,
            candidate_values,
            atol=args.atol,
            rtol=args.rtol,
            equal_nan=args.equal_nan,
        )
    difference = np.abs(reference_values - candidate_values)
    finite_difference = difference[np.isfinite(difference)]

    mismatch_count = int(close.size - np.count_nonzero(close))
    result.update(
        {
            "element_count": int(close.size),
            "mismatch_count": mismatch_count,
            "max_abs_error": float(finite_difference.max()) if finite_difference.size else 0.0,
            "mean_abs_error": float(finite_difference.mean()) if finite_difference.size else 0.0,
            "rmse": float(np.sqrt(np.mean(np.square(finite_difference))))
            if finite_difference.size
            else 0.0,
            "atol": args.atol,
            "rtol": args.rtol,
        }
    )
    result["pass"] = mismatch_count == 0 and (
        dtype_equal or args.allow_dtype_mismatch
    )

    print(json.dumps(result, sort_keys=True))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
