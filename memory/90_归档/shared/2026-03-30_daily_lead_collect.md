# 每日线索采集报告 2026-03-30

**执行时间**: 2026-03-30 08:30 (Asia/Shanghai)
**Job ID**: cron:32e5b925-15ce-4b7b-9901-ea601c77b601

---

## 后端状态

- 启动时未运行 → 自动拉起成功（start.sh）
- 健康检查: ✅ `{"status":"ok"}`

## Source Connector 健康

| 平台 | 状态 | 渠道 | 备注 |
|------|------|------|------|
| ImportYeti | ✅ OK | apify_fallback | token configured |
| Apollo | ❌ 不可用 | api | 无配置 |

---

## 采集结果

### ImportYeti ✅

| # | 关键词 | Job ID | 状态 | 新增 | 跳过 | Batch |
|---|--------|--------|------|------|------|-------|
| 1 | oscillating knife cutter | 12 | done | 10 | 0 | ImportYeti_20260330_0831 |
| 2 | vibrating blade cutting machine | 13 | done | 10 | 0 | ImportYeti_20260330_0831 |

**ImportYeti 合计：新增 20 条线索**

### Apollo ⚠️ 403 Forbidden（已知权限问题，不影响 job 状态）

| # | 关键词 | 错误 |
|---|--------|------|
| 1 | CNC cutting machine | 403 Forbidden - api.apollo.io |
| 2 | composite material cutting | 403 Forbidden - api.apollo.io |

> Apollo API Key 未配置或已过期，需在后端 settings 中更新。

---

## 汇总

- **Job 状态**: ✅ 成功（ImportYeti 落盘）
- **总新增线索**: 20 条
- **耗时**: ~3 分钟
- **待处理**: Apollo API Key 需更新
