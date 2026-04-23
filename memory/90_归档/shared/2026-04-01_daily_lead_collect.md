# 每日线索采集报告 - 2026-04-01（周三）

## 执行摘要

| 指标       | 值                                 |
| ---------- | ---------------------------------- |
| 执行时间   | 08:31 CST                          |
| 后端状态   | 自动拉起成功（start.sh）           |
| ImportYeti | ✅ 2/2 成功                        |
| Apollo     | ❌ 2/2 失败（403 Forbidden）       |
| 本次判定   | ✅ 成功（ImportYeti 落盘即算成功） |

## 采集明细

### ImportYeti ✅

| #   | 关键词                          | job_id | 总数 | 新增 | 更新 | 跳过 | batch                    |
| --- | ------------------------------- | ------ | ---- | ---- | ---- | ---- | ------------------------ |
| 1   | oscillating knife cutter        | 22     | 10   | 0    | 0    | 10   | ImportYeti_20260401_0831 |
| 2   | vibrating blade cutting machine | 23     | 10   | 0    | 1    | 9    | ImportYeti_20260401_0831 |

说明：大部分为已有线索（skipped），1条更新。与昨日数据高度重叠，建议考虑扩展关键词。

### Apollo ❌

| #   | 关键词                     | 状态   | 错误          |
| --- | -------------------------- | ------ | ------------- |
| 1   | CNC cutting machine        | failed | 403 Forbidden |
| 2   | composite material cutting | failed | 403 Forbidden |

说明：Apollo API 自 3/20 起持续 403，已连续 5 次采集失败。API Key 可能过期或账户权限变更，需人工排查。

## 趋势观察

- ImportYeti 连续 5 次采集（3/19-4/1）均成功，每次返回 10 条
- 新增线索递减趋势明显（10→10→10→10→0+1），存量已基本覆盖
- Apollo 自上线以来从未成功过，建议：
  1. 检查 Apollo API Key 有效性
  2. 或暂停 Apollo 采集，替换为其他数据源（如 ZoomInfo、LinkedIn Sales Navigator）

## 下一步建议

1. **扩展 ImportYeti 关键词**：leather cutting machine, fabric cutter, gasket cutting 等
2. **修复或替换 Apollo**：连续失败已无价值，浪费请求
3. **去重策略**：当 skipped 占比 >80% 时自动跳过该关键词
