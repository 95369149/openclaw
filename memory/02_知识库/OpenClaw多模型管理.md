# OpenClaw 多模型管理

## 1. 多模型切换时的上下文/记忆管理机制

### 上下文完整性传递
当 failover 切换模型时，**上下文是完整传递的**，因为 OpenClaw 的核心机制：
- **会话（Session）是状态容器**：所有对话历史、工具调用结果都存储在会话中
- **故障转移不重置会话**：模型切换（从主模型→回退模型）会保持完整的会话状态
- **会话转录文件（JSONL）**：`~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl` 存储完整对话历史

### 不同模型的 Token 计数差异处理
- **字符→Token 估算**：OpenClaw 默认按每个 token ≈ 4字符进行估算
- **模型特有 token 计数**：实际调用时由各模型 API 提供商返回准确的 token 用量
- **上下文字数估算**：使用 `/context list` 和 `/context detail` 查看各组成部分的字符数估算
- **自动修剪策略**：接近 context window 上限时，OpenClaw 会自动：
  - 修剪旧工具结果（session pruning）
  - 建议使用 `/compact` 压缩历史

### 配置示例：上下文管理
```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      // 自动压缩建议阈值（百分比）
      compaction: { thresholdPercent: 85 },
      // 大型文件注入限制
      bootstrapMaxChars: 20000,      // 单文件最大字符数
      bootstrapTotalMaxChars: 150000, // 所有文件总字符数
      // 图像降尺度，减少 vision token 使用
      imageMaxDimensionPx: 1200
    }
  }
}
```

## 2. Session 级别的模型使用统计

### Token 使用追踪
OpenClaw 提供多级使用统计：

#### 实时查看命令
```bash
# CLI 查看全局使用情况
openclaw status --usage
openclaw channels list         # 包含 provider 配额窗口

# Chat 命令查看会话统计
/status                        # 状态卡片（包含 tokens、上下文使用率、估计成本）
/usage tokens                  # 每次回复附加 token 用量脚注（会话级持久化）
/usage full                    # 完整统计（含成本估算）
/usage cost                    # 本地成本汇总（基于会话日志）
```

#### Provider 配额窗口
支持的 provider 配额查询：
- **Anthropic (Claude)**：OAuth tokens
- **GitHub Copilot**：OAuth tokens  
- **Gemini CLI**：OAuth tokens
- **OpenAI Codex**：OAuth tokens
- **MiniMax**：API key（5小时编码计划窗口）
- **z.ai**：API key

#### 模型调用次数和成本追踪
- **每回复统计**：存储在会话的 `responseUsage` 字段
- **会话级汇总**：查看 `/usage cost` 聚合统计
- **成本估算**：基于 `models.providers.<provider>.models[].cost` 配置
  ```json
  "cost": {
    "input": 0.000003,    // 每百万 input token 的 USD
    "output": 0.000015,   // 每百万 output token 的 USD
    "cacheRead": 0.000001,
    "cacheWrite": 0.000003
  }
  ```

### 配置示例：使用追踪
```json5
{
  models: {
    providers: {
      anthropic: {
        models: {
          "claude-3-5-sonnet-20241022": {
            cost: {
              input: 0.000003,
              output: 0.000015,
              cacheRead: 0.000001,
              cacheWrite: 0.000003
            }
          }
        }
      }
    }
  }
}
```

## 3. 模型故障转移与授权管理

### 故障转移层级
1. **Auth Profile 轮换**（同 provider 内）
   - OAuth profiles 优先于 API keys
   - 按 `usageStats.lastUsed` 最近最少使用轮换
   - Session stickiness：每个会话固定使用一个 profile（避免缓存失效）

2. **模型回退**（不同 provider/模型间）
   - 配置：`agents.defaults.model.fallbacks`
   - 顺序尝试直到 primary 模型

### 授权状态管理
- **冷却机制（Cooldown）**：失败后指数退避（1m → 5m → 25m → 1h cap）
- **禁用状态（Disabled）**：账单失败时禁用（5h → 24h 指数退避）
- **状态存储**：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
  ```json
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2,
      "disabledUntil": 1736178000000,
      "disabledReason": "billing"
    }
  }
  ```

### 配置示例：故障转移
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: [
          "openai/gpt-5.2",
          "gemini-2.5-flash"  // 免费回退选项
        ]
      },
      models: {
        // 模型允许列表 + 别名
        "anthropic/claude-sonnet-4-5": { alias: "Sonnet" },
        "openai/gpt-5.2": { alias: "GPT" },
        "gemini-2.5-flash": { alias: "Gemini" }
      }
    }
  },
  auth: {
    cooldowns: {
      // 账单失败后退避时间
      billingBackoffHours: 5,
      billingMaxHours: 24,
      // 失败统计窗口
      failureWindowHours: 24
    }
  }
}
```

## 4. 最新版本 2026.2.18 新功能

### 主要新功能
1. **Apple Watch 伴侣应用**
   - Watch inbox UI
   - Watch 通知中继处理
   - Gateway 命令表面支持 watch status/send 流程

2. **配对的设备卫生管理**
   - `device.pair.remove` 流程
   - `openclaw devices remove` 命令
   - 受保护的 `openclaw devices clear --yes [--pending]`

3. **技能加固**
   - 移除可能将不受信任的 issue 文本直接插值到命令字符串中的 shell 命令示例

### 重要修复和改进
1. **iOS/Onboarding 稳定性**
   - 重置陈旧的配对请求状态
   - 连接失败时断开 operator 和 node gateways
   - 避免重复的配对循环

2. **浏览器/中继重用**
   - 当端口已被另一个 OpenClaw 进程占用时重用正在运行的扩展中继

3. **Telegram 话题目标支持**
   - Cron 和 Heartbeat 时支持显式的 Telegram 话题目标 (`<chatId>:topic:<threadId>`)

4. **安全加固**
   - Exec 工具：要求 `tools.exec.safeBins` 二进制文件从可信 bin 目录解析
   - SSRF 防护：阻止通过 NAT64、6to4、Teredo IPv6 过渡地址的绕过
   - Cron Webhooks：使用 SSRF 防护的 outbound fetch

## 5. 最佳实践配置

### 安全多用户 DM 配置
```json5
{
  session: {
    // 推荐：每个频道+发送者独立会话，防止信息泄露
    dmScope: "per-channel-peer",
    
    // 可选：跨频道统一用户身份
    identityLinks: {
      "alice": ["telegram:123456789", "discord:987654321012345678"]
    },
    
    // 会话重置策略
    reset: {
      mode: "daily",
      atHour: 4,          // 网关主机本地时间 4:00 AM
      idleMinutes: 120    // 滑动空闲窗口
    }
  }
}
```

### 降低 Token 压力配置
```json5
{
  agents: {
    defaults: {
      // 文件注入限制
      bootstrapMaxChars: 15000,
      bootstrapTotalMaxChars: 100000,
      
      // 图像降尺度
      imageMaxDimensionPx: 800,
      
      // 自动压缩阈值
      compaction: { thresholdPercent: 80 }
    }
  },
  
  // 工具结果自动修剪
  tools: {
    results: {
      maxCharsPerResult: 5000,
      maxResultsKept: 20
    }
  }
}
```

### Sub-Agent 嵌套配置
```json5
{
  agents: {
    defaults: {
      subagents: {
        // 允许子代理生成孙子代理（编排模式）
        maxSpawnDepth: 2,
        
        // 每个会话最大活动子代理数
        maxChildrenPerAgent: 5,
        
        // 全局并发限制
        maxConcurrent: 8,
        
        // 子代理默认模型（节约成本）
        model: "gemini-2.5-flash",
        
        // 自动归档
        archiveAfterMinutes: 60
      }
    }
  }
}
```

## 6. 常用诊断命令

### 会话状态检查
```bash
# 查看所有活跃会话
openclaw sessions --active 30

# 查看会话存储路径
openclaw status

# 获取运行中网关的会话列表
openclaw gateway call sessions.list --params '{}'
```

### 上下文分析
```
/context list          # 上下文构成概览
/context detail        # 详细分量分析（文件/工具/技能占比）
/compact [指令]        # 压缩历史，释放窗口空间
/status                # 上下文使用率 + 最近 token 使用
```

### 模型管理
```
/model                 # 模型选择器（带编号）
/model list           # 可用模型列表（带别名）
/model status         # 详细状态（授权候选+端点）
/model anthropic/claude-opus-4-6  # 切换到指定模型
```

---

## 要点总结

1. **上下文完整性**：模型切换时会话历史完全保留
2. **使用统计**：会话级 token 追踪，支持 `/usage` 命令和成本估算
3. **故障转移**：分层架构（auth profile 轮换 → 模型回退）
4. **安全隔离**：多用户需要使用 `dmScope: "per-channel-peer"` 防止信息泄露
5. **新版本特性**：Apple Watch 支持、设备管理工具、Telegram 话题改进

以上配置知识可直接在 `~/.openclaw/openclaw.json` 中应用或通过 `openclaw config set` CLI 命令设置。