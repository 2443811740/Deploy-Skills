# Deployment Workspace Agent Setup

本文档供 Agent 初始化项目时使用。

## 1. 定位资源目录

将本文件所在目录记为 `RESOURCE_DIR`。

## 2. 确认项目根目录

根据用户当前目录、`AGENTS.md` 或 `CLAUDE.md` 确定候选 `PROJECT_ROOT`，并在安装前向用户确认。

## 3. 准备 Agent 入口文件

如果 `PROJECT_ROOT` 下不存在 `AGENTS.md` 或 `CLAUDE.md`，根据当前 Agent 类型创建其中一个空文件。

## 4. 执行安装

```bash
bash "$RESOURCE_DIR/setup.sh" "$PROJECT_ROOT"
```

## 5. 安装后检查

```bash
test -f "$PROJECT_ROOT/.deploy/DEPLOY.md"
test -f "$PROJECT_ROOT/.deploy/VERSION"
test -f "$PROJECT_ROOT/.deploy/skill-index.json"
test -f "$PROJECT_ROOT/.deploy/skills/deploy-router/SKILL.md"
test -f "$PROJECT_ROOT/.deploy/candidate-drop.conf"
test -x "$PROJECT_ROOT/.deploy/skills/governance/alignment-skill-journal/scripts/create_candidate.py"
test -d /home/public/zjj/skills_pr
test -w /home/public/zjj/skills_pr
```

## 6. 使用入口

1. 读取 `.deploy/DEPLOY.md`。
2. 通过 `.deploy/skill-index.json` 查找 Skill。
3. 无法直接匹配时，读取 `.deploy/skills/deploy-router/SKILL.md`。
