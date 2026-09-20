---
name: x86-onnx-tensorrt
description: "构建并验证 x86 部署态 ONNX 与 TensorRT engine。Use when: 从 PyTorch deploy wrapper 导出 ONNX、划定 prepared-input 边界、检查 ONNX 算子、选择原生 TensorRT 或 plugin、构建 engine、加载 plugin 并与参考推理做 raw output 对齐。"
version: 0.1.0
---

# x86 ONNX to TensorRT

## 目标

建立可复现的 `deploy wrapper -> ONNX -> TensorRT engine -> runtime` 链路。默认策略是明确 prepared-input 契约、优先标准算子、最少 custom op，并用相同输入逐层验证精度。

## 状态原则

历史文档中的版本、模型结构、plugin 和方案可能尚未实施。执行前必须重新核对当前代码、目标 TensorRT/CUDA/GPU 环境和现有产物，不得把计划、候选实现或旧 CI 命令描述成当前能力。

## 适用范围

- 从 PyTorch 或其他框架导出面向 x86 TensorRT 的部署 ONNX。
- 需要决定哪些动态前处理放在模型图外。
- ONNX 包含 `GridSample`、deformable attention 或其他潜在 custom op。
- TensorRT parser/build 因算子、plugin、profile 或 precision 失败。
- Engine 可以构建但加载失败，或 raw output 与参考链路不一致。

J6/HBIR/HBM 导出和板端运行不使用本 Skill。只有推理一致性问题且已有可运行模型产物时，转到 `../../consistency/bc-hbm-consistency/SKILL.md` 的比较方法。

## 必需信息

执行前锁定：

- 源模型/checkpoint、代码 revision 和 deploy wrapper。
- 目标 TensorRT、CUDA、driver、GPU compute capability 和容器镜像。
- 输入名称、顺序、shape/profile、dtype、layout 和预处理契约。
- 输出名称、语义及需要比较的 raw outputs。
- precision policy、workspace、timing cache 和 calibration 策略。
- 允许使用的 plugin 库及其 creator name/version/namespace。
- ONNX、Engine、plugin 和配置的存放与版本管理方式。

从 [Engine 构建清单模板](./assets/engine-build-manifest.json.template) 创建本次记录。缺少目标环境或输入 profile 时，不声称 Engine 可部署。

## 工作流

### 1. 划定部署边界

使用 [部署边界检查表](./references/deployment-boundary.md)：

1. 从目标 C++ runtime 反推真正需要的模型输入和输出。
2. 新建或确认部署态 wrapper，不直接导出训练/评估图。
3. 将不稳定、数据依赖或已有可靠 C++ 实现的动态前处理作为 prepared inputs，除非有证据必须进入 TensorRT 图。
4. 图像仍进入 backbone 时，明确图外完成的颜色、resize/crop、layout 和 normalize。
5. 为投影、voxel、地图和 temporal/cache 输入写出 name、shape、dtype、单位和更新规则。

边界选择是项目决策，不能把某个历史模型的图外算子列表当成所有模型的固定规则。

### 2. 固定显式导出模式

1. 导出行为由 wrapper 或模块的显式 `export_mode` 控制，不依赖“恰好没有 CUDA”等环境偶然条件。
2. 需要 fallback 的模块在导出前递归切换，并打印模块数量与完整路径。
3. 导出后检查实际图，证明预期分支被采用。
4. 临时 monkey patch 只适合验证；长期实现使用可测试、可恢复的显式模式。
5. 导出结束后恢复模型状态，避免影响同进程其他推理。

### 3. 导出并验证 ONNX 契约

1. 固定 opset、输入输出名、dynamic axes 或 optimization profile 边界。
2. 使用真实 representative prepared inputs 导出。
3. 运行 ONNX checker 和 shape inference（环境支持时）。
4. 列出所有 `(domain, op_type)`、graph inputs、outputs 和 unresolved custom nodes。
5. 使用 [ONNX 检查脚本](./scripts/inspect_onnx.py) 生成机器可读报告。
6. 将 ONNX SHA256 和检查报告写入构建清单。
7. 用 ONNX Runtime 或项目认可的 ONNX 执行器跑同一输入，先证明导出图与 wrapper 一致；无法执行时明确记录验证缺口。

### 4. 决定原生算子还是 plugin

按照 [算子与 plugin 决策表](./references/operator-plugin-decision.md)：

1. 标准 domain 且目标 TensorRT 原生支持的算子，先尝试无 plugin parse/build。
2. 对边界敏感算子核对 interpolation、padding、alignment、axis、dtype 和精度。
3. parser 不支持、精度不达标或性能证据不足时，才评估 plugin。
4. PyTorch CUDA extension 不是 TensorRT plugin，不能直接复用二进制或调用协议。
5. custom node 必须与 plugin creator 的 name、version、namespace、输入顺序、shape、dtype 和属性逐项匹配。
6. 未识别的 custom node 先补 symbolic/export rewrite，不盲目尝试 Engine build。

### 5. 构建可复现 Engine

1. 使用独立、可复现的构建工具，不把 Engine build 隐式塞进业务 runtime 初始化。
2. 构建前显式加载需要的 plugin，并记录加载顺序和路径。
3. 记录 ONNX hash、工具链、GPU、precision、workspace、profiles、flags、timing cache 和 plugin 清单。
4. parser error、未消费输入、profile 不覆盖或 plugin 缺失均视为失败。
5. 保存构建日志和 Engine SHA256。
6. 不把序列化 Engine 当作天然跨 TensorRT、CUDA、driver 或 GPU 可移植产物。

### 6. 验证 Runtime 加载

1. Runtime 在反序列化 Engine 前显式加载相同 plugin 集合。
2. plugin 动态库句柄至少存活到 runtime、engine 和 execution context 全部销毁。
3. plugin 加载或反序列化失败时初始化明确失败，不静默继续。
4. 校验 binding 名称、顺序、profile、dtype、shape 和缓冲区大小。
5. 在目标 GPU/driver/runtime 组合执行 smoke test。

### 7. 做逐层精度验收

对完全相同的 prepared inputs，依次比较：

1. deploy wrapper raw outputs
2. ONNX raw outputs
3. TensorRT raw outputs
4. C++ runtime raw outputs
5. C++ postprocess 结构化结果

先比较所有业务关键 raw outputs，再比较最终 JSON 或可视化。使用 [Engine 验收清单](./references/engine-validation.md) 记录阈值、误差、性能和可移植性边界。

### 8. 收口

- 删除临时导出 patch 和隐式环境依赖。
- 固化 wrapper、导出命令、检查报告、构建命令和 manifest。
- 保存 ONNX/Engine/plugin/config 哈希。
- 在目标环境重跑构建和加载验证。
- 写明尚未支持的 shape、precision、算子或设备组合。

## 完成标准

- 部署边界和输入输出契约明确。
- ONNX 图已检查，所有 custom domain/op 都有决策。
- Engine 构建环境和参数可复现。
- plugin 协议和加载生命周期有验证证据。
- wrapper、ONNX、TensorRT 与 C++ runtime 的关键 raw outputs 达到预定阈值。
- 目标 GPU 上可加载运行，最终结构化结果通过验收。
- 未把历史计划、未验证版本或候选 plugin 声称为已落地能力。
