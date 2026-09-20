# Tensor Boundary and Replay Contract

## 1. Select the Real Boundary

The reference boundary is the argument passed to the model runtime, not an earlier training tensor or an assumed preprocessing output.

For a BC reference flow, trace the active launch script until the actual `.feed()` call. Capture only the branch executed by the selected sample and configuration. For the HBM target flow, capture metadata immediately before model submission and raw outputs immediately after completion.

## 2. Capture Levels

| Level | Reference data | Purpose |
|-------|----------------|---------|
| Source | Original image, point cloud, calibration and frame metadata | Prove both flows use the same sample |
| Model input | Exact runtime inputs after preprocessing and quantization | Replay and localize preprocessing differences |
| Raw output | Runtime outputs before dequantization or decoding | Separate runtime differences from postprocessing |
| Semantic output | Decoded OCC, detection or other task records | Validate user-visible behavior |

Always label the level explicitly. Never compare tensors from different levels as if they were equivalent.

## 3. Required Tensor Metadata

Record these fields for every captured Tensor:

- `name` and runtime `index`
- semantic `group`, such as camera, lidar, temporal or map
- `direction`: input or output
- file path relative to the manifest
- `dtype`, logical `shape` and `layout`
- quantization state, scale and zero point when applicable
- target `valid_shape`, `aligned_shape` and strides when available
- file SHA256

The Tensor name is the primary identity. An index is evidence only after both model metadata lists have been compared.

## 4. Quantization Questions

Before replay, answer all of the following:

1. Was the dump captured before or after quantization?
2. Is the stored dtype signed, unsigned or floating point?
3. Is quantization per-tensor or per-channel?
4. Which axis owns per-channel scales?
5. Has the reference runtime already applied clipping or saturation?

A Tensor captured at the BC model-call boundary is commonly already quantized. Do not apply a second scale without direct code or metadata evidence.

## 5. Safe Target Buffer Writes

- Validate dtype and logical shape before touching the target buffer.
- Clear the complete aligned buffer so padding is deterministic.
- Copy logical values using the target strides; do not assume the aligned buffer is contiguous in logical order.
- Reject a file larger than the available target allocation.
- Flush or clean the CPU cache after the final write and before inference submission.
- Log the Tensor name, index, source file, shape and SHA256 for every replacement.

## 6. Transfer Integrity

Calculate SHA256 before transfer and again on the target. A replay result is invalid if the dump, model or configuration hashes cannot be connected to the run manifest.

## 7. Minimum Evidence

A valid replay experiment contains:

- the completed run manifest
- source and target model metadata
- replacement logs
- raw output comparison
- semantic output comparison when applicable
- an experiment-table row with one explicit conclusion
