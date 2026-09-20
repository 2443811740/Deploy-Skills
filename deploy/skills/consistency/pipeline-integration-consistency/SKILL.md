---
name: pipeline-integration-consistency
description: "验证多节点或多模型部署链路的接口一致性。Use when: 共享前处理、Flow/Subgraph 接线、3D 到 2D ROI 投影、属性模型串联、相机顺序、坐标空间、Optional 输入、跨节点索引回填或兼容迁移出现结果错位、空输出、框偏移或阻塞。"
version: 0.1.0
---

# Pipeline Integration Consistency

## 目标

在不混淆模型算法、节点编排和上层调度职责的前提下，定位多节点部署链路中最早违反契约的边界。重点验证消息类型、slot、顺序、坐标空间、稳定身份、生命周期和兼容行为，而不是直接修改最后一个报错节点。

## 适用范围

- 多个模型共享图像、GDC、resize 或其他前处理后结果异常。
- Flow、Subgraph、Collect 或 Optional 输入导致节点未执行、阻塞或空输出。
- 3D 结果投影成 2D ROI 后发生整体偏移、相机错位或分类回填错位。
- 消息结构、slot、节点名或配置迁移需要兼容旧链路。
- 单模型推理正确，但串联后的最终业务结果不正确。

如果模型调用边界内的输入或 raw output 已经不一致，先使用 `../bc-hbm-consistency/SKILL.md`。

## 必需信息

开始修改前记录：

- 各仓库或组件的职责、版本和构建产物。
- 实际运行的顶层入口、Flow/Subgraph 配置和目标输出。
- 生产者、消费者及每条边的 slot、消息类型和 Optional 语义。
- 图像、投影、ROI 和 bbox 所属坐标空间。
- camera/sensor/batch 顺序和跨节点稳定身份字段。
- 新旧链路各自必须保持的行为和验收样本。
- 能执行静态检查、构建、目标端运行和可视化的环境。

从 [边契约模板](./assets/edge-contract.md.template) 创建本次契约表。缺少上述信息时先追踪实际执行路径，不根据类名或历史配置猜测。

## 工作流

### 1. 划定职责与验证环境

1. 确认问题分别属于模型仓、部署节点、图执行框架还是上层 pipeline。
2. 明确每个仓库负责修改、构建、打包、部署和运行的哪一段。
3. 静态结论只标记为静态结论；依赖硬件、驱动或模型运行时的行为必须在对应环境验证。
4. 不把框架调度、跨帧缓存或发布逻辑伪装成单个算法节点修复。

### 2. 画出实际执行图

1. 从用户真正读取的顶层输出反向追踪依赖，确认新增分支可达。
2. 记录 Subgraph 外层名称与内部 slot 的映射。
3. 记录多输出 forward 的 slot 编号和消息封装。
4. 记录依赖模型 binding 的节点初始化顺序。
5. 对每条 Optional 边明确“缺失时仍需 feed 空占位”还是“整条分支跳过”。

使用 [图执行与边契约检查表](./references/graph-contract.md)。节点成功初始化不代表其 `Forward` 被执行。

### 3. 固化每条边的契约

为每条边填写：

- producer、consumer、forward、slot 和消息类型
- shape、dtype、layout、数量和 Optional 语义
- camera/sensor/batch 的显式顺序
- 坐标空间、单位、reference size 和 normalized/absolute 语义
- 稳定身份，例如 source index、detection index 或 frame id
- owner、zero-copy view、cache 和 reset 生命周期

契约中不得使用“按 map 当前顺序”“第一个模型”或“应该是同一个尺寸”这类隐含假设。

### 4. 逐边隔离差异

1. 固定同一帧和同一组配置，在生产者输出端 dump。
2. 在消费者入口再次 dump，先证明传输、顺序和生命周期没有改变数据。
3. 临时绕过新增节点或恢复独立前处理，形成单变量对照组。
4. 从最上游边开始，找到第一个超过阈值或违反 schema 的边界。
5. 只修复这个最早边界，再重跑同一检查。

### 5. 验证共享图像前处理

共享像素 Tensor 和共享后处理元数据是两件事。对每个消费模型分别确认：

- 实际输入图像的 raw、去畸变、virtual-FOV、crop 或 letterbox 空间
- 模型 resize 尺寸、回归 reference size 和输出是否 normalized
- source ROI、scale、offset 和 bbox 边界定义
- GDC/LUT/calibration 版本及输出 width、height、stride

使用 [图像坐标与 ROI 检查表](./references/image-coordinate-contract.md)。只有现场数据证明共享元数据无法表达多个消费者契约时，才增加模型私有 reference 配置。

### 6. 验证投影、ROI 与属性串联

1. 投影节点必须消费与下游 crop 完全相同的图像空间。
2. 内参、畸变模型、virtual-FOV 和实际图像尺寸必须属于该空间。
3. camera/sensor 顺序由显式配置或稳定标识决定，不能依赖容器偶然遍历顺序。
4. 每个源目标保留稳定 index；过滤后用占位或显式映射保持回填关系。
5. 校验无效 label、非法 bbox、越界 index、重复回填和空相机结果。
6. 第一阶段只输出最终消费的 ROI debug 图；投影确认后再连接属性模型。
7. 属性异常时优先检查最终 crop、camera batch 和 index 映射，不重复修改已证明正确的投影。

### 7. 实施兼容迁移

1. 新配置缺省时保持旧行为，除非明确批准默认值变化。
2. 新标准消息路径与旧兼容路径分别有测试，不用无关配置项猜测输入格式。
3. 顺序、截断、扩框和过滤策略都显式配置或记录默认值。
4. 修改 class、forward、slot、消息类型或输出结构时同步检查 Flow、Subgraph、测试和外层消费者。
5. 只有证明无外部依赖后才删除旧入口。

使用 [兼容与回归矩阵](./references/compatibility-regression.md)。

### 8. 分层验收

按以下层级收集证据：

1. 图可达性和每个节点执行日志。
2. 每条边的消息 schema、数量、顺序、稳定身份和空输入行为。
3. 坐标、ROI、crop 或其他中间结果的数值与可视化。
4. 下游模型输入与 raw output。
5. 最终结构化结果及多帧状态。
6. 旧链路回归、缺失输入、reset 和并发/in-flight 场景。

程序退出码为 0 只证明流程完成，不证明契约一致。

## 完成标准

- 实际执行图与边契约表完整。
- 已找到最早违反契约的边界并有可复现证据。
- 新链路在目标环境通过中间结果和最终结果验收。
- 旧链路、缺失 Optional 输入和多帧/reset 行为已回归。
- 没有依赖隐含容器顺序、偶然初始化顺序或临时 debug 开关。
- 跨仓修改、构建产物和部署顺序记录清楚。
