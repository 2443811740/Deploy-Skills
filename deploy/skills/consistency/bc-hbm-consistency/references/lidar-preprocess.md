# LiDAR Preprocessing Alignment Checklist

Compare stages in order and stop at the first stage that exceeds the agreed threshold. Do not jump directly from raw points to final pillar features.

## 1. Frame and Sensor State

- Confirm both flows use the same frame identifier and source files.
- Resolve relative paths from the data manifest directory, not the process working directory.
- Record which sensors are present in the current frame.
- Clear per-frame point-cloud containers before loading; a missing sensor must not reuse the previous frame.
- Confirm timestamp selection and synchronization rules.

## 2. Coordinate Frame

Record the declared input coordinate frame for every source:

- `sensor`: each cloud requires its own extrinsic transform.
- `ego`: clouds are already in a shared vehicle frame and must not be transformed again.

For a sensor-frame point, compare the exact operation:

$$
p_{ego} = R p_{sensor} + t
$$

Check matrix direction, row/column convention, multiplication order, units, precision and sensor-to-calibration mapping. Small calibration precision differences may be accepted only after their downstream error is measured against the threshold.

## 3. Merge and Range Filtering

- Compare sensor merge order only if later capacity limits make order observable.
- Compare minimum/maximum bounds per axis and whether each boundary is open or closed.
- Distinguish point filtering bounds from voxel-grid bounds.
- Record NaN, infinity, zero-point and intensity handling.

A configuration tuple must be interpreted from the owning code. Do not assume its final element is a normalization divisor merely because the value is numerically plausible.

## 4. Voxelization

Compare:

- voxel size and grid origin
- coordinate-index formula and rounding mode
- axis order in coordinates
- maximum points per voxel
- maximum voxel or pillar count
- overflow and truncation order
- deterministic ordering of emitted coordinates
- empty-voxel padding values

Compare coordinate sets by coordinate key before comparing list order.

## 5. Feature Construction

Build a channel table for both flows. For every channel, record its formula and units, including:

- raw or normalized `x`, `y`, `z`
- intensity transformation
- offsets from cluster mean
- offsets from voxel center
- masks and point counts
- constant or padding channels

Filtering range, voxel range and feature normalization are separate contracts. A value such as `$z / N$` is model-specific and belongs in the run report or explicit model configuration, never in this generic checklist.

## 6. Final Model Input

- Compare logical feature and coordinate arrays before quantization.
- Compare cast, clipping, scale, zero point and final integer arrays.
- Validate layout, valid shape, aligned shape, strides and padding.
- Verify cache maintenance after CPU writes on the target.

## 7. Acceptance Evidence

The report must identify the earliest divergent stage, its measured error, the expected threshold and the evidence that all earlier stages pass. A visual match alone is insufficient.
