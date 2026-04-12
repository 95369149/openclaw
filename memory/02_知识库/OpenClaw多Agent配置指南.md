# OpenClaw 多 Agent 配置指南

## 核心概念

### 1. 什么是 Agent？
一个 **Agent** 是拥有完整独立环境的智能体，包含：
- **工作空间 (Workspace)**: 文件、AGENTS.md/SOUL.md/USER.md、本地笔记、人格规则
- **状态目录 (agentDir)**: 认证配置文件、模型注册表、每个 Agent 的配置
- **会话存储 (Session store)**: 聊天历史 + 路由状态，位于 `~/.openclaw/agents/<agentId>/sessions`

### 2. 路径结构
- **配置**: `~/.openclaw/openclaw.json`
- **状态目录**: `~/.openclaw` (或 `OPENCLAW_STATE_DIR`)
- **工作空间**: `~/.openclaw/workspace` (或 `~/.openclaw/workspace-<agentId>`)
- **Agent 目录**: `~/.openclaw/agents/<agentId>/agent` (或 `agents.list[].agentDir`)
- **会话**: `~/.openclaw/agents/<agentId>/sessions`

## 单 Agent 模式 (默认)

不做任何配置时，OpenClaw 运行单一 Agent:
- `agentId` 默认为 `main`
- 会话键格式：`agent:main:<mainKey>`
- 工作空间：`~/.openclaw/workspace`
- 状态目录：`~/.openclaw/agents/main/agent`

## 多 Agent 配置步骤

### 步骤 1：创建 Agent 工作空间

```bash
# 使用向导创建新的隔离 Agent
openclaw agents add work
openclaw agents add coding
openclaw agents add social
```

每个 Agent 获得自己的：
- 工作空间 + `SOUL.md`, `AGENTS.md`, `USER.md`
- 独立的 `agentDir`
- `~/.openclaw/agents/<agentId>` 下的会话存储

### 步骤 2：创建频道账户

为每个 Agent 创建独立的频道账户：

```bash
# 每个 Agent 的 WhatsApp 账户
openclaw channels login --channel whatsapp --account work
openclaw channels login --channel whatsapp --account personal

# 每个 Agent 的 Telegram Bot
# 通过 BotFather 创建不同的 Bot，获取不同的 token
```

### 步骤 3：配置 Agent、账户和路由绑定

## 配置示例

### 基础示例：两个 WhatsApp 号码对应两个 Agent

```json5
{
  agents: {
    list: [
      {
        id: "home",
        default: true,
        name: "Home",
        workspace: "~/.openclaw/workspace-home",
        agentDir: "~/.openclaw/agents/home/agent",
      },
      {
        id: "work",
        name: "Work",
        workspace: "~/.openclaw/workspace-work",
        agentDir: "~/.openclaw/agents/work/agent",
      },
    ],
  },

  // 确定性路由：第一个匹配项获胜（最具体优先）
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },

    // 可选：特定群组重定向到工作 Agent
    {
      agentId: "work",
      match: {
        channel: "whatsapp",
        accountId: "personal",
        peer: { kind: "group", id: "1203630...@g.us" },
      },
    },
  ],

  channels: {
    whatsapp: {
      accounts: {
        personal: {
          // 可选覆盖，默认：~/.openclaw/credentials/whatsapp/personal
          // authDir: "~/.openclaw/credentials/whatsapp/personal",
        },
        biz: {
          // 可选覆盖，默认：~/.openclaw/credentials/whatsapp/biz
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

### 示例：WhatsApp 日常聊天 + Telegram 深度工作

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-5",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    { agentId: "chat", match: { channel: "whatsapp" } },
    { agentId: "opus", match: { channel: "telegram" } },
  ],
}
```

### 示例：同一频道，特定私聊路由到高级模型

```json5
{
  agents: {
    list: [
      {
        id: "chat",
        name: "Everyday",
        workspace: "~/.openclaw/workspace-chat",
        model: "anthropic/claude-sonnet-4-5",
      },
      {
        id: "opus",
        name: "Deep Work",
        workspace: "~/.openclaw/workspace-opus",
        model: "anthropic/claude-opus-4-6",
      },
    ],
  },
  bindings: [
    {
      agentId: "opus",
      match: { channel: "whatsapp", peer: { kind: "direct", id: "+15551234567" } },
    },
    { agentId: "chat", match: { channel: "whatsapp" } }, // 频道级规则在后
  ],
}
```

### 示例：Discord 每个 Bot 对应一个 Agent

```json5
{
  agents: {
    list: [
      { id: "main", workspace: "~/.openclaw/workspace-main" },
      { id: "coding", workspace: "~/.openclaw/workspace-coding" },
    ],
  },
  bindings: [
    { agentId: "main", match: { channel: "discord", accountId: "default" } },
    { agentId: "coding", match: { channel: "discord", accountId: "coding" } },
  ],
  channels: {
    discord: {
      groupPolicy: "allowlist",
      accounts: {
        default: {
          token: "DISCORD_BOT_TOKEN_MAIN",
          guilds: {
            "123456789012345678": {
              channels: {
                "222222222222222222": { allow: true, requireMention: false },
              },
            },
          },
        },
        coding: {
          token: "DISCORD_BOT_TOKEN_CODING",
          guilds: {
            "123456789012345678": {
              channels: {
                "333333333333333333": { allow: true, requireMention: false },
              },
            },
          },
        },
      },
    },
  },
}
```

## 路由规则 (消息如何选择 Agent)

**确定性路由：最具体优先**：

1. `peer` 匹配 (精确 DM/群组/频道 ID)
2. `parentPeer` 匹配 (线程继承)
3. `guildId + roles` (Discord 角色路由)
4. `guildId` (Discord)
5. `teamId` (Slack)
6. `accountId` 频道账户匹配
7. 频道级匹配 (`accountId: "*"`)
8. 回退到默认 Agent (`agents.list[].default`，否则第一个列表条目，默认：`main`)

如果多个绑定在同一层级匹配，**配置顺序第一个获胜**。

## 会话隔离 (dmScope)

### 安全 DM 模式 (多用户设置推荐)

当 Agent 能接收**多个用户**的私聊时，启用安全 DM 模式：

```json5
{
  session: {
    // 安全 DM 模式：按频道+发送者隔离 DM 上下文
    dmScope: "per-channel-peer",
  },
}
```

### dmScope 选项

- `"main"` (默认): 所有 DM 共享主会话（单用户设置适用）
- `"per-peer"`: 按发送者 ID 隔离（跨频道）
- `"per-channel-peer"`: 按频道+发送者隔离（多用户收件箱推荐）
- `"per-account-channel-peer"`: 按账户+频道+发送者隔离（多账户收件箱推荐）

### 使用 identityLinks 跨频道识别同一用户

```json5
{
  session: {
    dmScope: "per-channel-peer",
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
  },
}
```

## 每个 Agent 的沙盒和工具配置

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: {
          mode: "off",  // 个人 Agent 不需要沙盒
        },
        // 无工具限制 - 所有工具可用
      },
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",     // 始终沙盒化
          scope: "agent",  // 每个 Agent 一个容器
        },
        tools: {
          allow: ["read"],  // 只允许 read 工具
          deny: ["exec", "write", "edit", "apply_patch"],  // 拒绝其他
        },
      },
    ],
  },
}
```

## 子 Agent (Sub-Agents)

### 基础配置

```json5
{
  agents: {
    defaults: {
      subagents: {
        maxSpawnDepth: 2,      // 允许子 Agent 生成子子 Agent (默认: 1)
        maxChildrenPerAgent: 5, // 每个 Agent 会话的最大活跃子 Agent (默认: 5)
        maxConcurrent: 8,       // 全局并发限制 (默认: 8)
        archiveAfterMinutes: 60, // 子 Agent 会话自动归档时间 (默认: 60)
      },
    },
  },
}
```

### 深度级别

| 深度 | 会话键格式 | 角色 | 能否生成？ |
|------|-----------|------|-----------|
| 0 | `agent:<id>:main` | 主 Agent | 总是 |
| 1 | `agent:<id>:subagent:<uuid>` | 子 Agent (调度器) | 当 `maxSpawnDepth >= 2` |
| 2 | `agent:<id>:subagent:<uuid>:subagent:<uuid>` | 子子 Agent (工作者) | 从不 |

### 工具使用

```json5
{
  tools: {
    subagents: {
      tools: {
        // deny 优先
        deny: ["gateway", "cron"],
        // 如果设置了 allow，则变为仅允许列表 (deny 仍然优先)
        // allow: ["read", "exec", "process"]
      },
    },
  },
}
```

## Agent-to-Agent 通信

默认关闭，需要显式启用：

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,       // 默认关闭
      allow: ["home", "work"],  // 允许的 Agent ID 列表
    },
  },
}
```

## 实用 CLI 命令

```bash
# 列出所有 Agent 及其绑定
openclaw agents list --bindings

# 添加新 Agent
openclaw agents add <name>

# 删除 Agent
openclaw agents delete <name>

# 验证 Agent 路由
openclaw agents list

# 检查频道状态
openclaw channels status --probe

# 重启 Gateway
openclaw gateway restart

# 安全审计 (检查 DM 隔离)
openclaw security audit
```

## 最佳实践

### 1. **为每个独立用例创建单独的 Agent**
- 不同的手机号码/账户（每个频道 `accountId`）
- 不同的人格（每个 Agent 的工作空间文件）
- 分离的认证 + 会话（无交叉干扰）

### 2. **启用安全 DM 模式**
对于多用户设置，始终设置：
```json5
{ session: { dmScope: "per-channel-peer" } }
```

### 3. **为生产环境配置沙盒**
```json5
{
  sandbox: {
    mode: "all",
    scope: "agent",
    docker: {
      setupCommand: "apt-get update && apt-get install -y git curl",
    },
  },
}
```

### 4. **按需求配置工具权限**
- 家庭 Agent：限制工具集
- 工作 Agent：完整权限
- 公开 Agent：只读权限

### 5. **使用合适的模型**
- 日常聊天：经济型模型（Claude Sonnet）
- 深度工作：高质量模型（Claude Opus）
- 子 Agent：廉价模型

### 6. **工作空间版本控制**
```bash
cd ~/.openclaw/workspace-<agentId>
git init
git add .
git commit -m "初始提交"
# 推送到私有仓库
```

## 常见问题

### 1. **认证配置是每个 Agent 独立的**
- 存储在：`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **不要**跨 Agent 重用 `agentDir`

### 2. **会话键格式**
- 私聊：`agent:<agentId>:<mainKey>`
- 群聊：`agent:<agentId>:<channel>:group:<id>`
- 子 Agent：`agent:<agentId>:subagent:<uuid>`

### 3. **频道账户**
- WhatsApp：每个 `accountId` 对应一个手机号码
- Telegram：每个 `accountId` 对应一个 Bot token
- Discord：每个 `accountId` 对应一个 Bot token

### 4. **重置策略**
- 每日重置：默认每天 4:00 AM（网关主机本地时间）
- 空闲重置：`session.reset.idleMinutes`
- 按类型覆盖：`resetByType`
- 按频道覆盖：`resetByChannel`

### 5. **调试**
```bash
# 检查会话
openclaw sessions --json

# 检查状态
openclaw status

# 发送 /status 到聊天窗口
```

## 配置文件结构总结

```json5
{
  agents: {
    defaults: {
      // 所有 Agent 的默认设置
    },
    list: [
      {
        id: "agent1",
        name: "Agent 1",
        workspace: "path/to/workspace",
        agentDir: "path/to/agent/dir",
        sandbox: {
          mode: "all",
          scope: "agent",
        },
        tools: {
          allow: ["read"],
          deny: ["exec", "write"],
        },
        model: "anthropic/claude-sonnet-4-5",
        // 其他 Agent 特定配置
      },
      // 更多 Agent
    ],
  },
  bindings: [
    {
      agentId: "agent1",
      match: {
        channel: "whatsapp",
        accountId: "personal",
        peer: { kind: "direct", id: "+1234567890" },
      },
    },
    // 更多绑定
  ],
  session: {
    dmScope: "per-channel-peer",
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
  },
  channels: {
    whatsapp: {
      accounts: {
        personal: {
          // WhatsApp 个人账户
        },
        biz: {
          // WhatsApp 商业账户
        },
      },
    },
    // 其他频道
  },
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["agent1", "agent2"],
    },
    subagents: {
      maxSpawnDepth: 2,
      maxConcurrent: 8,
    },
  },
}
```

## 总结

OpenClaw 的多 Agent 系统提供了强大的隔离和路由功能：

1. **完全隔离**: 每个 Agent 有独立的工作空间、认证、会话
2. **灵活路由**: 基于频道、账户、用户、群组等多维度路由
3. **安全控制**: 沙盒隔离、工具权限控制、DM 会话隔离
4. **成本优化**: 为不同用途分配不同模型
5. **扩展性**: 支持子 Agent 和多级嵌套

遵循这些最佳实践，可以构建安全、灵活、可扩展的多 Agent 系统。

*最后更新: 2026-02-19*