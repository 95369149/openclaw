# 心跳检查清单

> **原则：** 心跳只做轻量读检查，不执行重任务。发现异常告警，不自己修。
> **最后更新:** 2026-02-25

---

## 每次心跳执行

### 1. 读 ops/state.json
- `memorySync.lastOkAt` 超过 90 分钟 → 告警："记忆同步可能卡住"
- `opsHourlySweep.lastOkAt` 超过 2 小时 → 告警："运维巡检异常"
- `opsHourlySweep.issues` 非空 → 简要报告最新问题

### 2. 读 task-board.json
- `activeTasks` 中有任务运行超过 30 分钟 → 报告任务名和启动时间
- 不分析、不处理，只报告

### 3. 轻量 Provider Ping
- mynewapi: 发一次最短请求（max_tokens:1），5s 超时
- xjrouter: 发一次最短请求（max_tokens:1），5s 超时
- 失败 → 告警并建议："今天避免跑 evolution，日报只发短版"

### 4. Gateway 状态
- `openclaw gateway status`
- 异常时告警

---

## 心跳不做的事
- ❌ 日报采集/总结
- ❌ 升级/编译/重构
- ❌ 批量学习/扫描
- ❌ 任何大量调用模型/网络的动作
- ❌ 写入大文件
- ❌ 派发新任务

---

## Cron 任务编制（v2.0）

| 任务 | 频率 | 超时 | 职责 |
|------|------|------|------|
| ops_hourly_sweep | 每1小时 | 2min | 豆包检查+静态巡检+状态回写 |
| daily_digest_pipe | 每天09:30 | 12min | 多源采集→去重→总结→分发 TG+Discord |
| learning_ingest_batch | 每天11:00 | 15min | 收藏扫描+摘要+存档 |
| nightly_ops_report | 每天22:00 | 6min | 余额+日志+成功率+阻塞项 |
| weekly_evolution_pipeline | 每周日20:00 | 45min | 进化+提示词+周刊+变更提案 |

记忆同步由 launchd (ai.openclaw.memory-sync) 每30分钟执行 sync.sh v2.0。
