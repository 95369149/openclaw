# OpenClaw Cron / Heartbeat / Compaction 配置指南

> 来源：docs.openclaw.ai 官方文档 | 整理日期：2026-02-19

## 一、Cron vs Heartbeat 选择指南

| 场景 | 推荐 | 原因 |
|------|------|------|
| 每30分钟检查收件箱 | Heartbeat | 可批量检查，有上下文 |
| 每天9点发日报 | Cron (isolated) | 需要精确时间 |
| 20分钟后提醒我 | Cron (main, --at) | 一次性精确定时 |
| 每周深度分析 | Cron (isolated) | 独立任务，可用不同模型 |
| 后台项目健康检查 | Heartbeat | 搭便车，不额外开销 |

## 二、Cron Jobs

### 存储位置
`~/.openclaw/cron/jobs.json`（Gateway 管理，运行时勿手动编辑）

### 三种 Schedule
```json
// 1. 一次性（at）— 默认执行后自动删除
{ "kind": "at", "at": "2026-02-19T09:00:00+08:00" }

// 2. 固定间隔（every）
{ "kind": "every", "everyMs": 3600000 }

// 3. Cron 表达式（5/6字段）
{ "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Shanghai" }
```

⚠️ ISO 时间戳不带时区 → 按 UTC 处理
⚠️ 整点 cron 自动错开 0-5 分钟（防负载尖峰），用 `staggerMs: 0` 或 `--exact` 强制精确

### 两种执行模式

#### Main Session（systemEvent）
- 注入系统事件到主会话，通过心跳处理
- `wakeMode: "now"` → 立即触发心跳
- `wakeMode: "next-heartbeat"` → 等下次心跳

```json
{
  "name": "提醒",
  "schedule": { "kind": "at", "at": "2026-02-19T16:00:00+08:00" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": { "kind": "systemEvent", "text": "提醒：检查文档" }
}
```

#### Isolated Session（agentTurn）
- 独立会话 `cron:<jobId>`，每次运行新 sessionId
- 不污染主会话历史
- 可覆盖 model / thinking

```json
{
  "name": "每日简报",
  "schedule": { "kind": "cron", "expr": "0 7 * * *", "tz": "Asia/Shanghai" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "生成今日简报",
    "model": "flash"
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "channel:1472878438112296992"
  }
}
```

### Delivery 模式
| 模式 | 说明 |
|------|------|
| `announce` | 投递到目标频道 + 主会话摘要（isolated 默认） |
| `webhook` | POST 到 URL |
| `none` | 静默，不投递 |

### Target 格式提醒
- Discord/Slack: `channel:<id>` 或 `user:<id>`
- Telegram topic: `-1001234567890:topic:123`
- `delivery.bestEffort: true` → 投递失败不算任务失败

## 三、Heartbeat

### 核心机制
- 在主会话中定期运行 agent turn
- 默认间隔 30m（Anthropic OAuth 默认 1h）
- 读 HEARTBEAT.md 执行检查清单
- 无事回复 `HEARTBEAT_OK`（被 Gateway 吞掉不投递）

### 配置
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "55m",
        "model": "google-gemini/gemini-2.5-flash",
        "target": "last",
        "activeHours": { "start": "08:00", "end": "23:00" }
      }
    }
  }
}
```

### 关键字段
- `every`: 间隔（`0m` 禁用）
- `model`: 覆盖模型（建议用便宜模型）
- `target`: `last`（最后活跃频道）| `none` | 具体频道
- `activeHours`: 活跃时段（本地时区），时段外跳过
- `ackMaxChars`: HEARTBEAT_OK 后允许的最大字符数（默认 300）
- `prompt`: 自定义心跳提示词（默认读 HEARTBEAT.md）

### HEARTBEAT_OK 规则
- 出现在回复开头/结尾 → 被识别为 ack，内容 ≤ ackMaxChars 则丢弃
- 出现在中间 → 不特殊处理
- 有告警时不要包含 HEARTBEAT_OK

## 四、Compaction（上下文压缩）

### 机制
- 当会话接近模型 context window 时自动触发
- 将旧对话总结为摘要，保留近期消息
- 摘要持久化到 JSONL 历史

### 配置
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "mode": "safeguard",
        "reserveTokensFloor": 24000,
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 5000,
          "prompt": "Write any lasting notes to memory/YYYY-MM-DD.md",
          "systemPrompt": "Pre-compaction memory flush..."
        }
      }
    }
  }
}
```

### 关键概念
- `mode: "safeguard"` → 默认，接近上限时触发
- `reserveTokensFloor` → 压缩后至少保留的 token 数
- `memoryFlush` → 压缩前先让 agent 把重要信息写入文件（防丢失）
- 手动压缩：发 `/compact` 命令

### Compaction vs Pruning
| | Compaction | Pruning |
|---|---|---|
| 作用 | 总结旧对话 | 裁剪旧工具输出 |
| 持久化 | ✅ 写入 JSONL | ❌ 仅内存中 |
| 触发 | 接近 context window | 每次 LLM 调用前 |
| 影响 | 所有消息 | 仅 toolResult |

## 五、Session Pruning（会话裁剪）

### 机制
- 仅裁剪旧的 `toolResult` 消息，不改 JSONL
- 仅对 Anthropic API 生效
- `cache-ttl` 模式：上次 Anthropic 调用超过 TTL 后才裁剪

### 配置
```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "10m"
      }
    }
  }
}
```

### 默认参数
- `keepLastAssistants`: 3（保护最近3条 assistant 消息的工具结果）
- `softTrimRatio`: 0.3
- `hardClearRatio`: 0.5
- `minPrunableToolChars`: 50000
- 含图片的工具结果不裁剪

## 六、Session 生命周期

### 重置策略
- 默认每日 4:00 AM 本地时间重置
- 可选 `idleMinutes` 滑动窗口
- 两者同时配置时，先到期的触发重置
- `/new` 或 `/reset` 手动重置
- Isolated cron 每次运行都是新 sessionId

### dmScope（DM 会话隔离）
| 模式 | 说明 |
|------|------|
| `main` | 所有 DM 共享主会话（默认，单用户） |
| `per-peer` | 按发送者隔离 |
| `per-channel-peer` | 按频道+发送者隔离（多用户推荐） |
| `per-account-channel-peer` | 按账号+频道+发送者（多账号推荐） |

## 七、Kitt 当前配置对照

我们的配置：
- Heartbeat: 55m, Gemini Flash, target=last ✅
- Compaction: safeguard, reserveTokensFloor=24000, memoryFlush=enabled ✅
- Pruning: cache-ttl, ttl=10m ✅
- 缺少 `activeHours` → 建议添加 `{ "start": "08:00", "end": "23:00" }`（与安静模式对齐）

### 建议优化
1. 心跳添加 `activeHours`，与 HEARTBEAT.md 安静模式规则对齐
2. 考虑给高频 Cron job 加 `delivery.bestEffort: true` 防止投递失败导致任务失败
