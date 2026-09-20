#!/usr/bin/env python3
"""Validate an inference-consistency run manifest and its NPY files."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np


REQUIRED_TOP_LEVEL = (
    "schema_version",
    "run_id",
    "sample_id",
    "reference",
    "target",
    "tensors",
)
REQUIRED_SIDE_FIELDS = (
    "runtime",
    "code_revision",
    "command",
    "model_sha256",
    "config_sha256",
)
REQUIRED_TENSOR_FIELDS = (
    "name",
    "index",
    "group",
    "direction",
    "file",
    "dtype",
    "shape",
    "sha256",
)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_fields(value, fields, location, errors):
    if not isinstance(value, dict):
        errors.append("{} must be an object".format(location))
        return
    for field in fields:
        if field not in value:
            errors.append("{} is missing {}".format(location, field))


def validate_tensor(tensor, index, base_dir, seen, errors):
    location = "tensors[{}]".format(index)
    require_fields(tensor, REQUIRED_TENSOR_FIELDS, location, errors)
    if not isinstance(tensor, dict) or any(field not in tensor for field in REQUIRED_TENSOR_FIELDS):
        return

    identity = (tensor["direction"], tensor["name"])
    if identity in seen:
        errors.append("{} duplicates tensor {}:{}".format(location, *identity))
    seen.add(identity)

    relative_path = Path(tensor["file"])
    if relative_path.is_absolute():
        errors.append("{}.file must be relative to the manifest".format(location))
        return

    tensor_path = base_dir / relative_path
    if not tensor_path.is_file():
        errors.append("{} does not exist".format(tensor_path))
        return

    actual_hash = sha256_file(tensor_path)
    if actual_hash.lower() != str(tensor["sha256"]).lower():
        errors.append("{} SHA256 mismatch".format(tensor_path))

    if tensor_path.suffix != ".npy":
        return

    try:
        array = np.load(str(tensor_path), allow_pickle=False, mmap_mode="r")
    except (OSError, ValueError) as error:
        errors.append("{} cannot be loaded: {}".format(tensor_path, error))
        return

    expected_shape = tuple(tensor["shape"])
    if array.shape != expected_shape:
        errors.append(
            "{} shape mismatch: manifest={} file={}".format(
                tensor_path, expected_shape, array.shape
            )
        )
    if array.dtype.name != tensor["dtype"]:
        errors.append(
            "{} dtype mismatch: manifest={} file={}".format(
                tensor_path, tensor["dtype"], array.dtype.name
            )
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text())
    except (OSError, json.JSONDecodeError) as error:
        print("manifest error: {}".format(error), file=sys.stderr)
        return 2

    errors = []
    require_fields(manifest, REQUIRED_TOP_LEVEL, "manifest", errors)
    if not isinstance(manifest, dict):
        print("manifest must be a JSON object", file=sys.stderr)
        return 2

    for side in ("reference", "target"):
        if side in manifest:
            require_fields(manifest[side], REQUIRED_SIDE_FIELDS, side, errors)

    tensors = manifest.get("tensors")
    if not isinstance(tensors, list) or not tensors:
        errors.append("tensors must be a non-empty array")
    else:
        seen = set()
        for index, tensor in enumerate(tensors):
            validate_tensor(tensor, index, args.manifest.parent, seen, errors)

    if errors:
        for error in errors:
            print("FAIL: {}".format(error), file=sys.stderr)
        return 1

    print("PASS: validated {} tensor(s)".format(len(tensors)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
