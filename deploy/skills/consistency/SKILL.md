---
name: consistency
description: "部署适配、推理与多节点集成一致性模块路由。Use when: 根据模型变更文档适配 C++ 并上板验证，Python/C++ 或服务器/板端结果不一致，或共享前处理、Flow/Subgraph、ROI、坐标和顺序出现异常。"
version: 0.3.0
---

# Inference Consistency Router

## 职责

将模型版本适配、运行时对齐和多节点集成问题路由到对应叶子 Skill。本 Skill 只负责识别问题阶段和选择子 Skill。

## 路由表

| Skill | 触发条件 |
|-------|----------|
| `model-version-adaptation` | 有变更文档、release notes 或明确的新旧模型版本，需要修改 C++、上板看效果，并在失败时逐级定位 |
| `bc-hbm-consistency` | 没有版本适配上下文，已经确认 Python BC 与 C++ HBM 的 raw/semantic 结果不一致；需要 dump、回放或前后处理对齐 |
| `pipeline-integration-consistency` | 单模型可用，但共享前处理、Flow/Subgraph、ROI/属性串联、顺序、坐标、Optional 输入或索引回填异常 |

## 路由流程

1. 有版本变更文档或模型升级目标时，读取 [model-version-adaptation](./model-version-adaptation/SKILL.md)。
2. 直接定位 BC/HBM Tensor 差异时，读取 [bc-hbm-consistency](./bc-hbm-consistency/SKILL.md)。
3. 节点接线、消息和坐标契约异常时，读取 [pipeline-integration-consistency](./pipeline-integration-consistency/SKILL.md)。
4. 版本适配 Skill 在闭环阶段会调用 BC/HBM Skill；不要一开始就跳过文档差异和板端基线。
5. 多类问题同时存在时，先证明单模型边界，再恢复多节点集成。

## 约束

- 不把某次问题的根因当成所有模型的固定规则。
- 不跳过版本、模型、配置、样本和实际执行分支确认。
- 不使用可视化相似代替 Tensor 或语义结果验收。
- 不把 GDC/OpenCV、CUDA/CPU 的差异未经实验直接归为可接受误差。
