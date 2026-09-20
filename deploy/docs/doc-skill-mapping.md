# dcv_cpp 文档技能提炼记录

## 目的

本文记录从 `dcv_cpp/doc/` 提炼到 Deploy Skills 的方法边界。源文档仍是项目事实和历史状态的权威来源；本仓只保留可跨模型、跨项目复用的工作流。

## 合并结果

| 源文档 | 可复用能力 | 合并位置 | 未合并内容 |
|--------|------------|----------|------------|
| `AGENT_GUIDE.md` | 仓库职责边界、环境分层、binding/stride/dtype 硬规则、Optional 输入风险 | `bc-hbm-consistency/references/multimodal-preprocess.md`、`pipeline-integration-consistency` | 本地绝对路径、主机、具体构建命令和项目类名 |
| `ALIGNMENT_GUIDE.md` | 从参考 dump 到 file replay、逐组恢复前处理、raw/semantic 分层验收、单帧与多帧区分 | `bc-hbm-consistency` 及其 references | 服务器命令、模型 Tensor shape、已对齐数值和兼容清理状态 |
| `CODE_STYLE.md` | Node/算法职责边界、Flow/slot 契约、Tensor 内存、zero-copy 生命周期、故障定位 | `pipeline-integration-consistency`、`graph-contract.md` | C++ 格式化风格、包名、具体二进制和部署目录 |
| `MODEL_STRUCTURE.md` | 图像/GDC、LSS、LiDAR、栅格地图、时序 cache 的对齐维度 | `multimodal-preprocess.md` 和 `lidar-preprocess.md` | 具体模型名、输出 shape、固定 grid/voxel 参数和项目公式结论 |
| `ref_and_pre2post_fix.md` | 共享像素前处理与模型私有坐标元数据的区分、先核验再修复 | `pipeline-integration-consistency/references/image-coordinate-contract.md` | 尚未复现的缺陷、具体模型分辨率和建议补丁 |
| `obs_od_roi_projection_plan.md` | 投影必须匹配实际消费图像空间、显式相机顺序、稳定 detection index、分阶段接入和兼容回归 | `pipeline-integration-consistency` 及其 references | 节点名、相机列表、配置数值、当前完成状态和车型业务逻辑 |
| `x86_trt_export_plan.md` | prepared-input 部署边界、显式 export mode、标准算子优先、plugin 协议、可复现 Engine 构建和逐层精度验收 | `model-export/x86-onnx-tensorrt` | 固定 TensorRT 版本、仓库路径、候选 plugin 名单和未落地决策 |
| `README.md` | 文档按主题维护和避免重复的原则 | 本映射文件与各 Skill 的渐进式 references | 项目文档导航本身 |

## Skill 路由摘要

### `bc-hbm-consistency`

用于模型调用边界内的 Python BC 与 C++ HBM 对齐，包括参考输入捕获、选择性回放、binding、图像/LSS/LiDAR/地图/时序前处理和 raw/semantic 输出比较。

### `pipeline-integration-consistency`

用于单模型正确但多节点链路异常的场景，包括 Flow/Subgraph 可达性、消息和 slot、共享前处理坐标元数据、ROI 投影、camera 顺序、稳定索引、Optional 输入、生命周期和兼容迁移。

### `x86-onnx-tensorrt`

用于 x86 部署态 wrapper、ONNX 导出、算子检查、TensorRT 原生/plugin 决策、Engine 构建、plugin 加载和逐层精度验收。

## 提炼原则

- 已验证的方法可以成为检查规则；一次实验的结果只能作为项目记录。
- 计划文档可以形成带前置核验的工作流，不能被描述成已实现能力。
- IP、账号、绝对路径、模型名、节点名、固定 Tensor index、固定参数和版本不进入通用 Skill。
- 可视化用于定位和人工复核，最终结论仍依赖 Tensor、schema 和业务字段。
- 项目行为变化后优先更新源文档；只有通用方法变化时才更新本仓 Skill。
