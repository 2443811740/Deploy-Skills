# TensorRT Engine Build and Validation

## Reproducible Build Record

记录：

- source revision、wrapper 和 ONNX SHA256
- TensorRT、CUDA、driver、OS/container 和 GPU compute capability
- builder flags、precision、workspace 和 tactic sources
- static/dynamic profiles 的 min/opt/max
- calibration dataset/hash 和 cache（如使用 INT8）
- timing cache 来源与 hash
- plugin 库、hash、creator 和加载顺序
- 完整命令、日志和 Engine SHA256

## Build Checks

- parser 没有 error 或未处理 node。
- 每个 network input 都有对应 profile。
- profile 覆盖实际 representative 和边界 shape。
- 输出名、shape 和 dtype 与契约一致。
- precision fallback 符合策略，没有静默改变关键层精度。
- 构建失败不复用旧 Engine 冒充新产物。

## Accuracy Ladder

使用同一 prepared inputs 比较：

1. framework deploy wrapper
2. ONNX executor
3. TensorRT Engine
4. production C++ runtime
5. postprocess result

每层提前定义 atol/rtol 或任务指标。至少记录最大绝对误差、均值误差、失配元素数量和代表性输出。整数或索引 Tensor 默认要求精确一致，除非契约另有说明。

## Runtime Checks

- 目标环境在反序列化前成功加载 plugin。
- binding name/order/profile 与运行配置一致。
- buffer size、alignment、stream 和同步正确。
- representative、最小和最大 shape 都能运行。
- 重复运行和多 context 不共享错误状态。
- 输出经过完整后处理后仍通过结构化验收。

## Portability Boundary

Engine 的验证范围只覆盖记录的 TensorRT/CUDA/driver/GPU 组合。跨版本或跨 GPU 使用前重新构建或至少重新执行 load、smoke、accuracy 和 performance 验证。
