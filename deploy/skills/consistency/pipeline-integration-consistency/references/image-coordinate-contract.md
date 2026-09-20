# Image Coordinate and ROI Contract

## Name Every Coordinate Space

至少区分：

- raw distorted image
- undistorted image
- virtual pinhole or virtual-FOV image
- cropped/letterboxed valid ROI
- resized model input
- normalized model output
- original image result

每个 bbox、点、内参和尺寸都必须标注所属空间。两个空间的图像内容相似，不代表数值坐标可直接比较。

## Shared Preprocessing

共享前处理前，分别记录每个消费者的：

- color/layout/normalization
- crop、resize 和 letterbox
- 模型输入尺寸
- 回归 reference size
- 输出是 normalized 还是 absolute
- 后处理需要的 source ROI、scale 和 offset

多个模型可以共享像素 Tensor，但仍可能需要各自的后处理尺度元数据。不要在没有现场证据时增加第二套 reference 真值来源。

## Projection Contract

- 投影使用的图像必须与下游实际 crop 的图像相同。
- raw 图使用 raw intrinsics/distortion；去畸变图使用对应新内参且不重复畸变。
- virtual-FOV 图使用与图像生成阶段相同的 virtual camera 参数。
- 标定尺寸与实际输出尺寸不同时，明确内参缩放公式。
- 外参方向、矩阵约定、单位和 timestamp 必须一致。
- 裁剪使用运行时图像实际宽高，不使用未验证的配置尺寸。

## ROI and Stable Identity

- 相机顺序显式配置，并由生产者和消费者共同使用。
- 每个源检测保留稳定 `source_index`；过滤后用占位或映射表保持回填关系。
- 一个目标是否只能选择一个相机必须写入契约。
- 明确 bbox 使用 `(x1,y1,x2,y2)` 还是 `(x,y,w,h)`，以及右下边界是否包含。
- 验证 label 范围、bbox 有效性、crop clipping、重复回填和越界 index。
- 排序、top-k、扩框和遮挡过滤必须发生在已记录的阶段。

## Staged Validation

1. 在真正消费的图像上画最终 ROI。
2. 验证系统性偏移、尺寸、目标唯一性和过滤结果。
3. 再连接下游 crop/classification。
4. 下游异常时 dump 最终 crop，而不是先改已验证的投影。
5. 最终使用结构化数量、index 对应和模型结果验收；可视化只是辅助证据。
