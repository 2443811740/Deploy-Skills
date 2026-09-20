# Deployment Boundary Checklist

## Start from the Consumer

从目标 runtime 的 binding 和后处理反推部署模型契约，而不是从训练模型顺向导出所有逻辑。

为每个输入记录：

- name、order、dtype、layout 和 static/dynamic shape
- 单位、数值范围和量化状态
- 谁生成、何时更新、是否跨帧
- 是否已有经过验证的 C++/Python 实现
- 放入图内的收益与引入的算子、动态 shape 和维护成本

## Prepared Inputs

适合优先留在图外的候选通常包括：

- 强数据依赖、动态数量或复杂控制流的预处理
- 需要标定、图结构、地图或传感器聚合的逻辑
- 目标 runtime 已有稳定实现的体素、投影或 cache 构造
- 为了导出会引入大量 custom op、但并非模型核心计算的步骤

这不是固定禁用列表。只有测量和维护证据才能决定最终边界。

## Image Contract

即使图像进入 backbone，也要明确图外完成的：

- RGB/BGR/YUV 和 channel order
- raw/undistorted/virtual image 空间
- resize、crop、letterbox
- NCHW/NHWC 与 camera/batch 展开
- mean、std、scale、cast 和 clipping

## Temporal Contract

- 首帧 cache 初值、mask 和 relative pose
- 后续帧更新时间、单位、坐标方向和 write-back
- dynamic profile 是否覆盖 cache shape
- sequence reset 与多 stream 隔离

## Wrapper Rules

- Wrapper 只暴露部署需要的显式 Tensor，不读取隐藏全局配置或文件。
- 输入输出名稳定且与 runtime 约定一致。
- 训练专用 loss、augmentation、data structure 和日志不进入导出图。
- 导出模式显式、可恢复、可单元测试。
- 使用 representative inputs 覆盖非空条件分支和动态 profile 边界。
