---
name: governance
description: "Deploy Skills 治理路由。Use when: 新对话开始需要收集编译、Python/BC 参考链路、部署和板端环境，或开发结束需要评估、记录、去重和晋升新的对齐 Skill 候选。"
version: 0.2.0
---

# Skill Governance Router

## 路由表

| Skill | 触发条件 |
|-------|----------|
| `deployment-session-intake` | 每次新对话首次进入部署相关开发时，收集任务范围、编译命令、BC 服务器与推理命令、部署方式、板端环境和验收标准 |
| `alignment-skill-journal` | 每次开发结束时评估新对齐经验；或用户要求查看、整理、去重、评审、提炼候选 Skill |

## 路由规则

1. 新对话开始时由 `.deploy/DEPLOY.md` 直接触发 [deployment-session-intake](./deployment-session-intake/SKILL.md)。
2. 开发任务结束时由 `.deploy/DEPLOY.md` 直接触发 [alignment-skill-journal](./alignment-skill-journal/SKILL.md)。
3. 会话问询答案只在当前对话内复用；候选经验写入工作区本地日志。
4. 候选日志不能自动修改正式 Skill，晋升必须经过独立评审和验证。
