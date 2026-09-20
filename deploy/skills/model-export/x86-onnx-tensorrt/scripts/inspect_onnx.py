#!/usr/bin/env python3
"""Inspect an ONNX graph contract and emit a JSON report."""

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def value_info(value):
    tensor_type = value.type.tensor_type
    shape = []
    if tensor_type.HasField("shape"):
        for dimension in tensor_type.shape.dim:
            if dimension.HasField("dim_value"):
                shape.append(dimension.dim_value)
            elif dimension.HasField("dim_param"):
                shape.append(dimension.dim_param)
            else:
                shape.append(None)
    return {
        "name": value.name,
        "element_type": tensor_type.elem_type,
        "shape": shape,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="run ONNX checker")
    args = parser.parse_args()

    try:
        import onnx
    except ImportError:
        print(
            "ERROR: missing optional dependency 'onnx'; install scripts/requirements.txt",
            file=sys.stderr,
        )
        return 2

    try:
        model = onnx.load(str(args.model), load_external_data=False)
        if args.check:
            onnx.checker.check_model(model)
    except (OSError, ValueError, onnx.checker.ValidationError) as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 2

    initializers = {initializer.name for initializer in model.graph.initializer}
    counter = collections.Counter(
        (node.domain or "ai.onnx", node.op_type) for node in model.graph.node
    )
    operators = [
        {"domain": domain, "op_type": op_type, "count": count}
        for (domain, op_type), count in sorted(counter.items())
    ]
    custom_nodes = [
        {
            "name": node.name,
            "domain": node.domain,
            "op_type": node.op_type,
            "inputs": list(node.input),
            "outputs": list(node.output),
        }
        for node in model.graph.node
        if node.domain not in ("", "ai.onnx", "ai.onnx.ml")
    ]
    report = {
        "file": str(args.model),
        "sha256": sha256_file(args.model),
        "ir_version": model.ir_version,
        "opsets": [
            {"domain": opset.domain or "ai.onnx", "version": opset.version}
            for opset in model.opset_import
        ],
        "inputs": [
            value_info(value)
            for value in model.graph.input
            if value.name not in initializers
        ],
        "outputs": [value_info(value) for value in model.graph.output],
        "operators": operators,
        "custom_nodes": custom_nodes,
        "node_count": len(model.graph.node),
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(encoded + "\n")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    sys.exit(main())
