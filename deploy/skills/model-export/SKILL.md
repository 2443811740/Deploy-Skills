---
name: model-export
description: "模型导出与运行时产物构建模块路由。Use when: ONNX 导出、TensorRT engine 构建、算子兼容、custom op、plugin 选择、部署 wrapper、prepared inputs 或导出后精度验证。"
version: 0.1.0
---

# Model Export Router

## 路由表

| Skill | 触发条件 |
|-------|----------|
| `x86-onnx-tensorrt` | x86 模型需要从部署态 ONNX 构建 TensorRT engine，或需要判断标准算子、custom op 与 TensorRT plugin |

## 路由规则

1. 先确认目标平台和运行时，避免把 J6/HBM 与 x86/TensorRT 流程混用。
2. x86 ONNX/TensorRT 任务读取 [x86-onnx-tensorrt](./x86-onnx-tensorrt/SKILL.md)。
3. 当前只注册 x86 ONNX/TensorRT；其他平台没有匹配项时停止并收集环境、模型格式和目标产物信息。
