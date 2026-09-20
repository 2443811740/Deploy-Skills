# Output Comparison Rules

## 1. Compare in Layers

Use this order so a later representation does not hide an earlier difference:

1. raw quantized runtime output
2. dequantized Tensor
3. decoded and filtered records
4. serialized result
5. visualization

If raw outputs match but decoded records do not, stop investigating input preprocessing and inspect postprocessing.

## 2. Tensor Metrics

For integer Tensors, require exact equality unless the model contract explicitly permits otherwise. For floating-point Tensors, record at least:

- shape and dtype equality
- mismatched element count
- maximum absolute error
- mean absolute error
- root mean square error
- relative tolerance and absolute tolerance used by the pass decision

Handle NaN and infinity explicitly. Thresholds must be selected before the candidate result is inspected.

## 3. Decode Contract

Compare the complete transformation, not only constants:

- dequantization scale and zero point
- units and unit conversion
- normalized-to-physical range mapping
- clipping bounds and clipping order
- lower/upper bound correction
- class mapping and filtering
- rounding and integer conversion

For height-like outputs, write both formulas side by side and evaluate representative boundary values. A shared raw Tensor does not imply matching physical heights.

## 4. OCC Comparison

Do not compare serialized list positions. Normalize each record to a stable grid key, such as level and grid coordinates, then compare:

- missing and extra keys
- class/category changes
- lower and upper height differences
- confidence differences when present

Duplicate grid keys are an error unless the schema explicitly permits them.

## 5. Detection Comparison

Do not compare detections by array position. Partition by class, construct a geometry-based cost matrix and perform one-to-one assignment. Record:

- unmatched reference detections
- unmatched candidate detections
- center distance, size error, yaw error and score error
- IoU when the schema provides sufficient geometry

Use an assignment threshold to reject implausible pairs. Prefer a proven assignment implementation such as SciPy's `linear_sum_assignment` over a custom order-dependent matcher.

## 6. Visualization

Render both results with identical camera, color map, scale, filtering and canvas size. Side-by-side images are useful for review, but the pass/fail result comes from Tensor and semantic metrics.

## 7. Reporting

Every comparison result must include:

- reference and candidate artifact hashes
- comparator version or command
- thresholds
- metrics
- pass/fail decision
- a bounded list of representative mismatches
