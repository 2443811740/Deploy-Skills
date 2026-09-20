# Graph Execution and Edge Contract

## Reachability

- 从实际请求的顶层输出反向确认整条依赖链。
- 新分支若没有被顶层输出、下游消费者或显式 side effect 引用，可能不会执行。
- 区分节点已注册、已初始化、已调度和已完成四个状态。
- 为每个节点记录可证明执行的日志或计数器。

## Edge Schema

逐边记录并比较：

| Field | Questions |
|-------|-----------|
| Producer/consumer | 哪个 forward 产生，哪个 forward 消费？ |
| Slot | 外层名称与内部 slot 是否一一对应？ |
| Message | 运行时类型与注册类型是否一致？ |
| Cardinality | 单值、vector、map、batch 和 camera 数量如何表达？ |
| Optional | 缺失时 feed 空占位、跳过，还是使用默认值？ |
| Order | sensor、camera、tensor 和 batch 顺序由什么稳定定义？ |
| Identity | 过滤和重排后如何回到原 source index？ |
| Lifetime | view、frame、buffer、cache 的 owner 活到何时？ |

## Initialization

- 依赖模型 binding 或 registry 的节点必须在元数据注册后初始化。
- 初始化顺序应由图或显式配置保证，不能依赖容器遍历顺序。
- 配置解析失败、plugin 加载失败或必要 binding 缺失时明确失败，不静默 fallback。

## Optional and Collect

- Optional 输入的“当前帧缺失”与“这条边从未声明”是不同状态。
- 框架要求占位时，即使没有业务数据也必须 feed 正确类型的空消息。
- Collect/Subgraph 卡住时逐项检查每个声明输入是否在当前帧完成。
- 空输入路径必须有单独测试，不能只用全量传感器样本。

## Multi-output Forward

- 明确 slot 数量、每个 slot 的消息类型和名称。
- 外层 Subgraph 映射必须与内部 slot 保持一致。
- 调整 slot 或消息结构时同步修改配置、测试和消费者。

## Lifecycle

- Zero-copy slice/view 必须持有底层 buffer owner。
- Reset 时先释放引用外部处理器资源的消息和 cache，再销毁处理器。
- 跨帧 cache 要区分 stream、sequence 或 request，检查 in-flight 并发是否共享错误状态。
