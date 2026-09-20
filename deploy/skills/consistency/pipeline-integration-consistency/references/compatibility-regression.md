# Compatibility and Regression Matrix

## Migration Rules

- 新字段缺省时保持旧行为；默认值变化必须被明确批准和记录。
- 新行为通过显式配置选择，不根据另一个不相关字段推断模式。
- 公共节点保持通用，模型特化逻辑放入独立节点或明确配置。
- 新旧消息类型并存时，分别验证解析、排序、过滤和输出结构。
- 不因测试夹具过时而把生产配置改回不真实的输入形式。

## Required Matrix

| Case | Purpose |
|------|---------|
| Old config + old input | 证明历史链路不回归 |
| New config + new input | 证明目标链路完整可用 |
| Missing new fields | 验证兼容默认值 |
| Explicit empty/invalid field | 验证初始化或运行时明确失败 |
| Empty Optional input | 验证不阻塞且输出语义正确 |
| Full sensor/input set | 验证正常路径 |
| Missing one sensor/input | 验证不复用上一帧数据 |
| First frame | 验证初始 cache/mask/identity |
| Consecutive frames | 验证顺序、时间和 cache 写回 |
| Reset/new sequence | 验证状态隔离 |

只有确实需要支持中间迁移版本时才增加 `old input + new config` 等组合，并在文档中说明退役条件。

## Output Checks

- frame/sample key
- 每层 vector/map 数量
- 显式 sensor/camera/batch 顺序
- source index 与下游回填 index
- 空项、占位和过滤项
- score、label、bbox/coords 等关键字段
- 多帧 cache 和生命周期

## Removing Compatibility Code

删除旧路径前必须：

1. 搜索所有配置、测试、上层仓库和发布包引用。
2. 确认替代路径已在目标环境运行。
3. 给出迁移说明和失败时回滚方式。
4. 删除旧路径后执行完整矩阵，而不只执行新链路 happy path。
