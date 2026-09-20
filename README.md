# Deploy Skills

面向部署任务的 Agent Skills 集合，采用“安装包 + 工作区资源 + JSON 索引 + 分级路由 + 叶子 Skill”的组织方式。当前版本为 `0.5.0`。

## 目录结构

```text
deploy_skills/
├── README.md
├── README.en.md
├── agent-setup.md
├── setup.sh
├── deploy/
│   ├── DEPLOY.md
│   ├── VERSION
│   ├── skill-index.json
│   ├── docs/
│   └── skills/
│       ├── deploy-router/
│       ├── consistency/
│       └── model-export/
└── templates/
```

## 已有模块

### Inference Consistency

- `model-version-adaptation`：从变更文档和新旧版本差异出发完成 C++ 最小适配、板端结构化/可视化验收；失败时依次进入开环代码分析、闭环 BC dump/HBM 回放和异构后端三方实验。
- `bc-hbm-consistency`：Python BC 与 C++ HBM 的 Tensor 边界捕获、NPY 选择性回放、binding、图像/LSS/LiDAR/地图/时序前处理和 raw/semantic 输出对齐。
- `pipeline-integration-consistency`：共享前处理、Flow/Subgraph、消息/slot、图像坐标、ROI 投影、camera 顺序、稳定索引、Optional 输入、生命周期和兼容迁移。

### Skill Governance

- `deployment-session-intake`：每次新对话开始时收集编译命令、BC 服务器与推理命令、部署方式、板端环境和验收标准；同一对话复用，跨对话重新询问。
- `alignment-skill-journal`：每次开发验证后评估并记录新的对齐 Skill 候选，正式 Skill 只在人工评审后晋升。

### Model Export

- `x86-onnx-tensorrt`：部署态 wrapper、prepared-input 边界、ONNX 图检查、标准算子/plugin 决策、可复现 Engine 构建和逐层精度验收。

具体模型参数、设备地址、部署路径和某次实验结论不会固化在通用 Skill 中。源文档的提炼边界见 [doc 技能映射](deploy/docs/doc-skill-mapping.md)。

## 安装

```bash
bash setup.sh <project-root>
```

安装后，`deploy/` 中的资源会复制到目标项目的 `.deploy/`，并向已有的 `AGENTS.md` 或 `CLAUDE.md` 注入入口规则。重复执行不会重复注入规则。`skill-index.json` 中的路径以安装后的项目根目录为基准，因此使用 `.deploy/`，不是源码包中的 `deploy/`。

安装采用覆盖更新，不主动删除目标 `.deploy/` 中源包已不存在的文件，避免误删项目自有资源；升级后以 `skill-index.json` 中已注册的 Skill 为准。

## 可选脚本依赖

```text
deploy/skills/consistency/bc-hbm-consistency/scripts/requirements.txt
deploy/skills/model-export/x86-onnx-tensorrt/scripts/requirements.txt
```

只有实际运行相应脚本时才需要安装依赖；框架安装本身不修改 Python 环境。

## 扩展

新增模块或 Skill 时，从 `templates/` 复制对应模板，并同步更新：

1. `deploy/skill-index.json`
2. `deploy/DEPLOY.md`
3. 对应模块路由表
