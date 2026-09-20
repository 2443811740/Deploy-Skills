# Candidate Evaluation and Promotion

## Novelty Types

| Type | 说明 | 常见晋升位置 |
|------|------|--------------|
| `new-skill` | 现有模块没有该完整工作流 | 新叶子 Skill |
| `skill-extension` | 现有 Skill 缺少阶段、分支或限制 | 目标 `SKILL.md` |
| `routing-trigger` | 已有能力无法被正确发现 | router description/table |
| `discriminating-check` | 新的低成本检查可区分多个根因 | reference 或 script |
| `failure-mode` | 新的可复现故障模式与恢复路径 | reference |
| `backend-boundary` | 新的异构实现、容差或共同边界 | reference |
| `automation` | 稳定重复步骤可自动校验 | script + procedure |

## Candidate Gate

对每项回答：

1. 正式 Skill 是否已有语义等价规则？
2. 去掉当前项目名、路径和参数后，方法是否仍成立？
3. 是否能指出最便宜的判别检查？
4. 是否有至少一份可核验的证据？
5. 是否知道何时不应使用？
6. 是否能说明应新增还是扩展哪个正式 Skill？

前四项任一为否时，不进入候选日志；可在本次任务报告中保留为项目事实。

## Deduplication

候选键由“建议目标 + 核心不变量”生成，例如：

```text
bc-hbm-consistency/compare-runtime-boundary-before-preprocess
model-version-adaptation/three-way-cpu-control-for-cuda-differences
```

不要使用日期、文件名、模型名或 issue 编号作为核心键。发现相同键时更新原条目：

- `last_seen`
- `occurrence_count`
- `evidence_level`
- `occurrences`
- `promotion_requirements`

## Promotion Checklist

- [ ] 触发与不适用条件清晰
- [ ] 至少达到 `validated`
- [ ] 已与正式 Skill 和其他候选去重
- [ ] 通用规则与项目证据分离
- [ ] 有可执行步骤和判别检查
- [ ] 有成功标准、失败分支和限制
- [ ] 不包含秘密或环境专属值
- [ ] 正式索引、版本和安装回归已更新

`repeated` 是强晋升信号，但不是硬性要求；高风险故障只验证一次也可以晋升，前提是证据完整且适用边界明确。
