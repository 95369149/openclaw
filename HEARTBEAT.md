# 心跳检查清单

> **原则：** 心跳做轻量检查 + 轻量自动修复。重大操作告警厂长。禁止在心跳周期内派发占用超过 1 分钟的重度任务，防止阻塞主线流程。
> **最后更新:** 2026-04-07 v4.0

---

## 每次心跳执行

### 1. 读 ops/state.json

- `memorySync.lastOkAt` 超过 90 分钟 → **自动修复**：运行 `bash memory/scripts/sync.sh auto`，修复后回写状态
- `opsHourlySweep.lastOkAt` 超过 2 小时 → 告警厂长："运维巡检异常"
- `opsHourlySweep.issues` 非空 → 简要报告最新问题

### 2. 检查运行中任务（v4.0 升级：改用 openclaw tasks）

- 运行 `openclaw tasks list` 查看运行中任务
- 有任务运行超过 30 分钟 → 查 `subagents list` 确认状态：
  - 子 agent 已完成 → **自动修复**：`openclaw tasks cancel <id>`，同步更新 task-board.json readyTasks 状态
  - 子 agent 失败 → **自动修复**：取消任务，告警厂长
  - 子 agent 仍在运行 → 继续等待，不干预
- task-board.json 只维护业务 backlog（readyTasks），不再手动维护 activeTasks
- 无活跃任务 → 跳过

### 3. Provider 状态检查（v4.0 新增）

- 运行 `bash memory/scripts/check-provider-status.sh`
- 读取 `ops/provider-status.json`
- 检查各 provider 状态：
  - `status: "ok"` → 正常
  - `status: "degraded"` → 降级，告警但不阻断
  - `status: "down"` → 不可用，从路由中临时移除
- 如果所有付费 provider 都 down → 告警厂长："所有付费 provider 不可用，今天只用 main(gemini)"
- 状态写入 `ops/state.json` 的 `providerStatus` 字段

### 4. Gateway 状态

- `openclaw gateway status`
- 异常时告警

---

## 心跳自动修复权限（v3.0 新增）

### ✅ 可以自动做的

- 重启 sync.sh（记忆同步卡住时）
- 更新 task-board.json 状态（子 agent 已完成/失败时）
- 标记 provider 不可用（ping 失败时）
- 回写 ops/state.json 状态

### ❌ 不能自动做的

- 重启 Gateway
- 修改 openclaw.json 配置
- 终止正在运行的子 agent
- 派发新任务
- 发消息给外部（Discord/WhatsApp）

---

## Cron 任务编制（v3.0）

| 任务                      | 频率        | 超时  | 职责                               |
| ------------------------- | ----------- | ----- | ---------------------------------- |
| ops_hourly_sweep          | 每1小时     | 2min  | 豆包检查+静态巡检+状态回写         |
| daily_digest_pipe         | 每天09:30   | 12min | 多源采集→去重→总结→分发 TG+Discord |
| learning_ingest_batch     | 每天11:00   | 15min | 收藏扫描+摘要+存档                 |
| morning_wisdom            | 每天07:00   | 2min  | 国学金句+英语2句                   |
| evening_management        | 每天21:30   | 2min  | 管理工具一条                       |
| nightly_ops_report        | 每天22:00   | 6min  | 余额+日志+成功率+阻塞项            |
| weekly_evolution_pipeline | 每周日20:00 | 45min | 进化+提示词+周刊+变更提案          |

记忆同步由 launchd (ai.openclaw.memory-sync) 每30分钟执行 sync.sh v2.0。
