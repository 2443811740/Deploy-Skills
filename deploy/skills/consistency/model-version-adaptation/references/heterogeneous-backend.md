# Heterogeneous Backend Alignment

## Problem Classes

常见异构差异包括：

- 硬件 GDC 与 OpenCV 去畸变/resize
- Python CUDA kernel 与 C++ CPU 实现
- GPU reduction、sorting 或 atomic 操作与 CPU 顺序
- BPU/GPU/CPU 的量化、插值、rounding 和边界行为

不能只根据实现后端不同就接受差异，也不能默认要求所有中间值逐位一致。

## Three-way Experiment

建立三条链路并保持其他条件不变：

| Lane | Backend | Purpose |
|------|---------|---------|
| A | Python production backend | 当前参考生产结果 |
| B | Python CPU-equivalent backend | 消除 CUDA/硬件 kernel 差异的共同算法边界 |
| C | C++ target implementation | 最终部署实现 |

判定：

- `B ≈ C` 且 `A` 不同：差异主要来自异构后端或算法实现。
- `A ≈ B` 且 `C` 不同：C++ 实现或其输入契约存在差异。
- 三者都不同：样本、参数、实现或比较边界仍未统一。
- 仅最终业务结果一致：记录中间差异及为何不影响验收，不能声称中间 Tensor 对齐。

“≈”必须使用预先定义的数值、几何或业务阈值。

## GDC versus OpenCV

先对齐契约：

- 输入图像与标定版本
- raw/undistorted/virtual-FOV 目标空间
- 输出尺寸、有效 ROI、crop 和 padding
- interpolation、border mode 和像素中心约定
- 内参缩放、畸变模型和 LUT 生成方式
- stride、颜色格式和量化

建议分三层验收：

1. 几何：已知点、网格线或 ROI 在目标空间的位置误差。
2. 像素：共同有效区域的误差分布，排除 border 后单独统计。
3. 业务：同一模型输入后的 raw output 与结构化结果。

像素不逐位一致但几何和业务均在阈值内时，可以接受并记录；只看两张图“差不多”不能接受。

## CUDA versus CPU

- Python CPU 对照必须调用与 C++ 等价的算法，不只是把 Tensor 移到 CPU 后仍走不同逻辑。
- 固定 dtype、精度、排序、seed、线程和 deterministic 配置（环境支持时）。
- 比较 CPU 对照和 C++ 的每个中间阶段，再比较生产 CUDA。
- reduction、top-k、NMS、voxel 边界和原子写入等顺序敏感操作单独设阈值。
- 强制 CPU 开关只用于诊断；最终报告同时保留生产后端与目标 C++ 的结果。

## When CPU Fallback Is Not Available

1. 找到两侧最靠近的共同输入输出边界。
2. 向不可见实现输入完全相同的数据。
3. 用统计、几何和业务三层指标描述误差。
4. 测试边界值、空输入、密集输入和重复运行稳定性。
5. 将无法验证的 kernel 行为列为残余风险，不捏造等价结论。

## Finalization

- 删除或关闭诊断用强制 CPU 和 dump 开关。
- 恢复 Python 生产后端和 C++ 原生路径分别运行。
- 报告三方 hash、命令、阈值和结果。
- 明确最终目标是算法契约一致、业务一致还是逐位一致。
