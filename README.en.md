# Deploy Skills

An Agent Skills collection for deployment workflows, organized as an installable workspace package with a JSON index, progressive routers, leaf skills, references, assets, and scripts. Current version: `0.5.0`.

## Included Modules

### Inference Consistency

- `model-version-adaptation`: change-document-driven C++ adaptation, target-board structured/visual validation, open-loop code analysis, closed-loop BC dump/HBM replay, and three-way heterogeneous-backend experiments.
- `bc-hbm-consistency`: runtime-boundary capture, selective NPY replay, binding validation, multimodal preprocessing, and raw/semantic output alignment between Python BC and C++ HBM.
- `pipeline-integration-consistency`: shared preprocessing, Flow/Subgraph edges, message and slot contracts, image coordinates, ROI projection, explicit ordering, stable identity, Optional inputs, lifetime, and compatibility migration.

### Skill Governance

- `deployment-session-intake`: at the start of every new conversation, collect build commands, BC server and inference commands, deployment method, target environment, and acceptance criteria; reuse only within that conversation.
- `alignment-skill-journal`: after validated development work, evaluate and record new alignment Skill candidates for later human promotion.

### Model Export

- `x86-onnx-tensorrt`: deploy wrappers, prepared-input boundaries, ONNX graph inspection, native-operator/plugin decisions, reproducible TensorRT Engine builds, and layered accuracy validation.

Model-specific constants, device addresses, deployment paths, and one-off experiment conclusions are intentionally excluded. See the [source-document mapping](deploy/docs/doc-skill-mapping.md) for extraction boundaries.

## Installation

```bash
bash setup.sh <project-root>
```

Resources are installed under `<project-root>/.deploy/`. Existing `AGENTS.md` or `CLAUDE.md` files receive an idempotent routing rule. Paths in `skill-index.json` are relative to the installed project root, so they intentionally use `.deploy/` rather than the source package's `deploy/` directory.

Installation overwrites managed files but does not delete files that no longer exist in the source package, avoiding accidental removal of project-owned resources. The registered entries in `skill-index.json` remain authoritative after an upgrade.

Optional dependencies are declared next to each Skill's scripts. Installing the framework does not modify the Python environment.
