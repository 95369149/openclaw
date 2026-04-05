# 每日线索采集报告 2026-03-31

**执行时间**: 2026-03-31 08:30 (Asia/Shanghai)
**Job 状态**: ✅ 成功（ImportYeti 落盘，Apollo 403 已记录）

---

## 采集汇总

| # | 平台 | 关键词 | 状态 | 采集 | 入库 | 跳过 |
|---|------|--------|------|------|------|------|
| 18 | ImportYeti | oscillating knife cutter | ✅ done | 10 | 10 | 0 |
| 19 | ImportYeti | vibrating blade cutting machine | ✅ done | 10 | 10 | 0 |
| 20 | Apollo | CNC cutting machine | ❌ 403 | 0 | 0 | 0 |
| 21 | Apollo | composite material cutting | ❌ 403 | 0 | 0 | 0 |

**今日新增线索**: 20 条（全部来自 ImportYeti，batch: ImportYeti_20260331_0831）

---

## 后端状态

- 启动时后端未运行，自动执行 `start.sh` 拉起成功
- 健康检查: `GET /api/health` → `{"status":"ok"}`
- Source Connectors:
  - ImportYeti: ✅ ok (channel: apify_fallback, token configured)
  - Apollo: ✅ connector ok，但 API 调用返回 403 Forbidden

---

## Apollo 403 详情

```
Client error '403 Forbidden' for url 'https://api.apollo.io/api/v1/mixed_people/search'
```

**可能原因**: API Key 权限不足 / 套餐限制 / Key 已过期。建议厂长检查 Apollo API Key 配置。

---

## 结论

- ImportYeti 2 个关键词全部成功，共入库 20 条新线索
- Apollo 403 权限问题，已记录，不影响本次 job 成功判定
- 总账户库现有 ~98 条记录
