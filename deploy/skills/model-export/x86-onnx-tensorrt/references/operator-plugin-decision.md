# Operator and Plugin Decision Guide

## Decision Order

1. 检查 ONNX node 的 domain、op type、attributes 和 opset。
2. 确认目标 TensorRT 版本的原生 parser/layer 支持。
3. 尝试无 plugin 构建并运行精度测试。
4. 只有 parser、精度或性能证据要求时才引入 plugin。
5. custom op 无匹配 plugin 时，先修改 export symbolic 或 graph rewrite。

## Native Operator Checks

“支持该算子”还不够，至少核对：

- interpolation 或 reduction mode
- padding/border behavior
- coordinate/alignment convention
- axes、broadcast 和 dynamic shape
- supported dtype/precision
- empty tensor 和 boundary values

## Plugin Protocol

逐项建立 ONNX custom node 与 creator 的协议表：

| Contract | ONNX node | TensorRT plugin |
|----------|-----------|-----------------|
| name | | |
| version | | |
| namespace/domain | | |
| input order | | |
| output order | | |
| dtype/format | | |
| attributes | | |
| dynamic shape | | |
| serialization | | |

任一项不清楚时，不把候选 plugin 标为可复用。

## Important Distinctions

- PyTorch CUDA extension 与 TensorRT plugin 是两套运行时协议。
- 历史 `.so` 可被加载不代表 creator 与当前 ONNX 节点匹配。
- build 阶段加载 plugin 不代表 runtime 反序列化阶段会自动加载。
- 环境变量预加载可用于诊断，但不应成为没有记录的生产依赖。

## Plugin Lifecycle

- build 前加载 creator 所在库。
- deserialize 前加载相同库。
- 使用立即符号解析和全局可见性时，明确平台 API 和失败策略。
- 动态库句柄存活时间覆盖 runtime、engine 和 context。
- 日志打印库路径、hash 和已注册 creator。
