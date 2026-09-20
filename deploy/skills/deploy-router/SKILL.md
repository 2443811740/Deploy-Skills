---
name: deploy-router
description: "部署任务顶层路由入口。用户提出模型版本升级、变更文档适配、环境检查、设备部署、运行验证、推理一致性、共享前处理、Flow 集成、ONNX/TensorRT 导出、Engine 构建、回滚、结果采集或部署故障排查等请求，但尚未明确对应具体 Skill 时使用。"
version: 0.3.0
---

# Deployment Router

## 职责

本 Skill 只负责路由，不包含具体部署实现。

## 路由流程

1. 读取 `.deploy/skill-index.json`。
2. 根据 `paths.*.description` 匹配用户意图。
3. 命中模块级路由时，先读取模块 `SKILL.md`。
4. 读取最终命中项的 `skillFile`，再按目标 Skill 执行和验证。
5. 没有匹配项时，说明当前框架缺少对应 Skill，并收集创建该 Skill 所需的信息。

## 已注册模块

| 模块 | 典型触发词 | 路由入口 |
|------|------------|----------|
| 推理与集成一致性 | 模型升级、变更文档、上板可视化、开环/闭环调试、BC/HBM、Python/C++、共享前处理、Flow/Subgraph、ROI/坐标错位 | `.deploy/skills/consistency/SKILL.md` |
| Skill 治理 | 新对话环境问询、编译/BC/部署/板端契约、候选经验收集、定期晋升 | `.deploy/skills/governance/SKILL.md` |
| 模型导出 | ONNX 导出、TensorRT、Engine 构建、custom op、plugin、prepared inputs | `.deploy/skills/model-export/SKILL.md` |

## 约束

- 不根据 Skill 名称猜测行为。
- 不在未读取目标 `SKILL.md` 时执行部署操作。
- 不把模板目录作为可执行 Skill。
- 多个 Skill 同时命中时，先确定依赖顺序，再依次执行。
- 不把计划、候选实现或历史命令描述成已验证能力。
