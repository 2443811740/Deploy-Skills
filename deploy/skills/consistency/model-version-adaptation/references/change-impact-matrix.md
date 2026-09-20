# Change Document and Impact Matrix

## Evidence Priority

变更文档用于发现候选差异，最终契约按以下证据优先级确认：

1. 新旧模型 metadata、binding 或正式接口 spec
2. 新旧版本真实执行代码和配置
3. 可复现的输入输出 dump
4. release notes 或变更说明
5. 历史经验和推测

高优先级证据冲突时停止修改并记录冲突；不能选择更方便的一项。

## Version Baseline

| Item | Baseline | Target | Evidence |
|------|----------|--------|----------|
| Code revision | | | |
| Model file/hash | | | |
| Config file/hash | | | |
| Runtime/toolchain | | | |
| Dataset/sample | | | |
| Result schema | | | |

## Impact Categories

逐条把变更归入以下一类或多类：

- 输入名称、数量、顺序、shape、dtype、layout 或量化
- 图像、LiDAR、投影、地图或时序前处理
- 模型输出 Tensor 或语义
- 反量化、decode、过滤、坐标映射或序列化
- 配置字段、默认值、标定或文件组织
- runtime、内存、cache、plugin 或硬件要求
- Flow/消息/slot 或上层消费者契约
- 可视化、性能或结果验收标准

## Matrix

| Change ID | Document statement | Status | Confirming evidence | C++ owner | Config/Flow | Test impact | Planned change | Validation |
|-----------|--------------------|--------|---------------------|-----------|-------------|-------------|----------------|------------|
| | | confirmed/assumed/unknown | | | | | | |

## Review Rules

- 每个代码修改至少对应一个 Change ID。
- `assumed` 和 `unknown` 项不能直接驱动破坏兼容的修改。
- 文档未提到但 metadata/code 明确变化的内容同样加入矩阵，并标记来源。
- 删除、重命名和默认值变化必须检查所有调用方及旧配置。
- 变更项验证完成后填写证据，不只写“已验证”。
