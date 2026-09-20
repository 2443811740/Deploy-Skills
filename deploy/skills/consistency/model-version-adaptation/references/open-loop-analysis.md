# Open-loop Python/C++ Analysis

开环分析不把 Python 数据注入 C++。目标是通过代码、配置、metadata 和现有结果找到明确差异，成本低于闭环插桩。

## 1. Confirm Actual Paths

- 从启动脚本和配置追踪真正执行的 Python BC 分支。
- 从测试/应用入口追踪真正执行的 C++ Node、backend 和 decode。
- 标注备用路径、训练路径和未命中的条件分支，不把它们作为当前证据。
- 对两侧模型、配置和标定计算哈希。

## 2. Build a Side-by-side Table

| Stage | Python BC | C++ target | Evidence | Difference |
|-------|-----------|------------|----------|------------|
| Input selection | | | | |
| Preprocess | | | | |
| Quantization/layout | | | | |
| Runtime binding | | | | |
| Raw output interpretation | | | | |
| Decode/filter | | | | |
| Coordinate mapping | | | | |
| Serialization/visualization | | | | |

每个单元格写真实公式、参数、单位、边界包含规则和调用位置，不写“基本相同”。

## 3. High-value Checks

- 同一帧、传感器集合和文件解析方式
- calibration 数值而非文件名
- normalized/absolute 坐标及 reference size
- dtype、量化状态、valid/aligned shape、stride 和 Tensor 顺序
- clipping、rounding、top-k、score threshold 和 class mapping
- 首帧、后续帧和 reset 的 cache 行为
- 可视化是否读取了与被比较结果相同的 schema

## 4. Exit Criteria

满足任一条件即可结束开环阶段：

- 找到唯一差异，能通过单点修改和板端复验验证。
- 证明模型调用前输入一致，问题转向 runtime 或后处理。
- 存在多个无法由静态证据区分的候选差异，进入闭环调试。
- 一侧实现由不可见 kernel 或第三方 runtime 控制，需要构造共同边界实验。

不要因为开环分析耗时而直接修改多个候选点；无法区分时应升级到闭环数据实验。
