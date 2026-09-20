# Multimodal Preprocessing Alignment Checklist

本清单用于 LiDAR 之外的图像、投影、栅格地图和时序输入。按模型实际拥有的输入选择章节，不得假设所有多模态模型具有相同 Tensor 集合。

## 1. Binding and Model Selection

- 优先使用显式模型名；没有显式名称时，按必需 Tensor 名集合做唯一匹配。
- 不依赖 unordered map、registry 或文件系统的第一个元素推断模型。
- 对每个 binding 记录 name、index、valid shape、aligned shape、stride、aligned byte size、storage dtype、量化类型和 scale。
- 多输入 vector 的顺序必须与模型 binding 顺序一致；数量一致不能证明顺序一致。
- Padding 只能体现在 stride、aligned allocation 和写入步长，不得伪装成逻辑 shape。
- 写 Tensor 的 C++ 类型必须与 storage dtype 一致；相同字节宽度不代表相同语义。
- 输出量化参数应随 Tensor 元信息传递，由后处理读取，避免另建漂移的常量来源。
- 多模型并行 dump 时，frame id 按模型或 engine 独立计数并写入 manifest。

## 2. Image and GDC

逐项比较：

- 输入文件、颜色空间、位深和 channel order
- resize、crop、letterbox、有效 ROI 和参考尺寸
- mean、std、scale、cast 和 clipping
- NCHW/NHWC、batch 与 camera 维度展开方式
- GDC 标定、LUT/cache 版本、去畸变或 virtual-FOV 配置
- 输出 width、height、Y/UV stride、虚拟地址、物理地址与 owner 生命周期

如果后处理需要把坐标映射回原图，同时记录 `source ROI`、`model input size`、`regression reference size` 和输出是否 normalized。共享图像 Tensor 不意味着共享后处理尺度元数据。

Zero-copy view 或 crop 必须持有底层 owner；Reset 时先释放引用 frame 的 Tensor/cache，再释放图像处理器。

## 3. Camera Projection and LSS

明确约定：

- 内参对应 raw、去畸变还是 virtual pinhole 图像
- 内参标定尺寸与实际输出尺寸的缩放规则
- 外参方向、矩阵乘法约定和单位
- camera subset 及其顺序
- grid/depth 配置和边界规则
- reference point 的 logical shape 与量化方式
- high/low-bit split 矩阵的语义和顺序

将投影公式写在报告中并用已知点验证。raw distorted 图与去畸变/virtual-FOV 图属于不同坐标空间，不应期待 bbox 或 reference point 逐值相同。

Fallback shape 必须来自实际 binding 或受版本约束的模型契约，不能凭历史形态猜测维度。

## 4. Rasterized Map or Structured Inputs

动态栅格化难以定位时，先回放参考链路已经生成的栅格 Tensor，证明模型与后处理，再恢复目标侧栅格化。

恢复时逐项比较：

- 坐标系、原点、分辨率和网格轴顺序
- 输入元素的稳定身份和遍历顺序
- 线段与多边形裁剪算法及边界包含规则
- 属性映射、默认值、clamp、overlap 和覆盖优先级
- 空地图与非空真实地图两类样本

空输入只验证缺省路径，不能覆盖 dtype、裁剪、属性填充等条件分支。

## 5. Temporal Inputs and Cache

先单独验证首帧契约，再验证至少两个连续帧：

首帧通常需要明确：

- cache feature/anchor/confidence 的初始值
- mask 或 valid flag
- time interval
- relative transform 是否为 identity

后续帧需要比较：

- pose 方向与 `$T_{previous\rightarrow current}$` 公式
- timestamp 单位、差值和异常帧策略
- cache score threshold、top-k 和写回顺序
- reset、序列切换和 frame drop 行为
- 多帧 in-flight 时 cache 是否错误共享

单帧对齐不能证明 temporal cache 对齐。

## 6. Isolation Order

1. 回放全部参考 prepared inputs，验证推理和后处理。
2. 按图像、投影/LSS、LiDAR、地图栅格、时序等语义组恢复目标前处理。
3. 对首个失败组按本清单逐阶段 dump。
4. 修复最早差异并重跑首帧、连续多帧和缺失 Optional 输入。

## 7. Common Misdiagnoses

- 文件名一致不代表标定数值一致。
- shape 一致不代表 stride、aligned byte size 或 storage dtype 一致。
- 输入数量一致不代表 binding 顺序或 camera 顺序一致。
- 程序成功退出不代表 decode schema、数量和边界 score 一致。
- 可视化接近不代表 raw Tensor 或坐标空间契约一致。
