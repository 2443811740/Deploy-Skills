# Deployment 工作区

## 1. 工作区概览

- 工作区根目录：`.deploy/`
- 版本文件：`.deploy/VERSION`
- Skill 索引：`.deploy/skill-index.json`
- 文档目录：`.deploy/docs/`
- Skill 目录：`.deploy/skills/`
- 本地候选日志：`.deploy/local/alignment-skill-candidates.md`（安装升级不覆盖）
- 当前版本：`0.5.0`

## 2. 新对话环境问询

- 每次新对话首次进入本工作区的开发任务时，必须先读取 `.deploy/skills/governance/deployment-session-intake/SKILL.md` 并询问使用者。
- 问询必须覆盖任务范围、编译环境与精确命令、Python/BC 服务器与精确推理命令、部署方式、板端环境准备与运行命令、验收标准。
- 每组答案标记为 `provided`、`not-applicable` 或 `unknown`；纯分析可在相关组为 `not-applicable` 后继续。
- 同一对话复用已确认答案，不重复询问；目标、版本、BC 服务器/命令或部署信息变化时只重问受影响组。
- 新对话必须重新询问，不静默沿用历史聊天、项目文档或自动探测值。
- 构建、BC 推理、上传或板端运行所需信息仍为 `unknown` 时，禁止执行对应阶段。
- 禁止通过对话、候选日志或项目文件收集密码、令牌、私钥和口令。

## 3. 路由规则

1. 部署相关任务先读取 `.deploy/skill-index.json`。
2. 根据索引中每个 Skill 的 `description` 匹配用户意图。
3. 命中模块级路由时，先读取模块 `SKILL.md`，再选择叶子 Skill。
4. 匹配后读取对应 `skillFile`，再执行任务。
5. 无法明确匹配时，使用 `.deploy/skills/deploy-router/SKILL.md`。
6. 未经本地 Skill、项目代码或可靠文档确认，不推测部署命令、参数或当前实现状态。

## 4. 验证规则

- 修改后执行与改动范围匹配的最小验证。
- 未执行验证时，明确说明原因和剩余风险。
- 不覆盖用户已有配置、产物或板端文件，除非用户明确授权。
- 一致性任务必须固定模型、配置、样本和版本，并保留可复现证据。
- 导出任务必须记录工具链、目标设备、输入 profile、plugin 和产物哈希。
- 静态分析、计划方案和目标端验证使用不同状态标识，不能相互替代。

## 5. 对齐 Skill 候选收集

- 每次使用本工作区规则完成开发任务后，在最终答复前评估本次是否产生新的可复用对齐能力。
- 评估必须在本次最小验证完成后进行，并与 `.deploy/skill-index.json`、相关正式 Skill 及已有候选去重。
- 命中候选门槛时，读取 `.deploy/skills/governance/alignment-skill-journal/SKILL.md`，追加或更新 `.deploy/local/alignment-skill-candidates.md`。
- 未产生新候选时不修改临时日志，也不写空记录。
- 临时日志不是正式规则；禁止在日常开发收尾中自动晋升。只有用户定期评审并明确执行晋升后，才能修改正式 Skill。
- 候选日志可以保留 sanitized 项目证据，但不得记录密码、令牌、私钥或真实凭据。

## 6. 扩展约定

- 业务 Skill 放在 `.deploy/skills/<module>/<skill-name>/`。
- 模块路由可放在 `.deploy/skills/<module>/SKILL.md`。
- 每个 Skill 必须包含 `SKILL.md`。
- 新增或移除 Skill 时同步维护 `.deploy/skill-index.json`。
- 具体部署规范、脚本、示例和参考资料由各 Skill 按需提供。
- 项目专属路径、设备、模型参数和阶段性结论保留在项目文档，不写成通用规则。

## 7. 内置 Skills

- `deploy-router@0.3.0` -> `.deploy/skills/deploy-router/SKILL.md`

### Inference Consistency

- `model-version-adaptation@0.1.0` -> `.deploy/skills/consistency/model-version-adaptation/SKILL.md`
- `consistency@0.3.0` -> `.deploy/skills/consistency/SKILL.md`
- `bc-hbm-consistency@0.1.0` -> `.deploy/skills/consistency/bc-hbm-consistency/SKILL.md`
- `pipeline-integration-consistency@0.1.0` -> `.deploy/skills/consistency/pipeline-integration-consistency/SKILL.md`

### Skill Governance

- `governance@0.2.0` -> `.deploy/skills/governance/SKILL.md`
- `deployment-session-intake@0.1.0` -> `.deploy/skills/governance/deployment-session-intake/SKILL.md`
- `alignment-skill-journal@0.1.0` -> `.deploy/skills/governance/alignment-skill-journal/SKILL.md`

### Model Export

- `model-export@0.1.0` -> `.deploy/skills/model-export/SKILL.md`
- `x86-onnx-tensorrt@0.1.0` -> `.deploy/skills/model-export/x86-onnx-tensorrt/SKILL.md`
