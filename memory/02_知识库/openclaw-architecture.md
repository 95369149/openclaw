# OpenClaw 配置架构说明（2026-02-19）

## 系统概览
- **版本**：OpenClaw 2026.2.14
- **部署**：本地 Mac（M1 16GB）
- **用途**：制造业企业（红太阳数控）AI 助手 + 自动化学习管线

## 四角色分工体系

| 角色 | 模型 | 职责 | 成本 | 备注 |
|---|---|---|---|---|
| 日常主力 | Claude Sonnet 4.6 (mynewapi) | 前台对话、日常任务 | 免费 | Primary |
| 调度员 | Qwen3-32B (SiliconFlow) | Fallback 第一位，搜索任务 | 免费 | 避免 Gemini rate limit |
| 学习员 | 豆包 Web (Playwright) | 文档摘要、归档 | 免费 | 本地 8100 端口 |
| 架构师 | Claude Opus 4.6 (mynewapi) | 改配置、汇总决策 | 免费 | Fallback 兜底 |

## Fallback 链设计（9层）

```
Sonnet 4.6 (主力)
  ↓ 失败
Qwen3-32B (免费调度员)
  ↓
DeepSeek V3.2 (便宜付费 $0.55/M)
  ↓
Gemini 3 Pro (免费 OAuth)
  ↓
Llama 70B (Groq 免费)
  ↓
Gemini Flash (免费)
  ↓
Qwen3-32B (Groq 免费)
  ↓
Kimi K2 Thinking (免费)
  ↓
Opus 4.6 (兜底)
```

**跨平台容错**：4 个独立平台（mynewapi / SiliconFlow / Google / Groq），任一平台挂不影响其他。

## 模型 Provider 配置

### 1. mynewapi（主力）
- **API**: Anthropic Messages
- **模型**: Opus 4.6 (兜底) + Sonnet 4.6 (主力)
- **成本**: 免费额度
- **特点**: 200K context, Opus 支持 reasoning

### 2. SiliconFlow（中国服务）
- **API**: OpenAI Completions
- **模型**: DeepSeek V3.2 ($0.55/M) + Qwen3-32B (免费) + Kimi K2.5/K2-Thinking
- **特点**: 国内访问快，免费模型多

### 3. Google Gemini
- **API**: Google Generative AI + CLI OAuth
- **模型**: Flash / Pro / Flash Lite
- **成本**: 免费
- **特点**: 1M context, 多模态

### 4. Groq（速度快）
- **API**: OpenAI Completions
- **模型**: Llama 70B + Qwen3-32B
- **成本**: 免费
- **特点**: 推理速度极快

### 5. v1api（备用）
- **API**: OpenAI Completions
- **模型**: DeepSeek V3.2/R1, Grok 4, o4-mini, Sonnet 4.5
- **成本**: 付费（$0.28-$4.4/M）
- **特点**: 多模型聚合

### 6. 豆包 Web（本地代理）
- **API**: OpenAI Completions (本地 Playwright 代理)
- **端口**: 8100
- **成本**: 免费
- **特点**: Web 自动化，需 Cookie 维护

### 7. 火山引擎豆包（官方 API）
- **API**: OpenAI Completions
- **模型**: Doubao 2.0 Pro/Lite
- **成本**: 付费（$0.4-$16/M）
- **特点**: 官方 API，稳定但贵

## Cron 任务分流策略

### 走豆包 Web（50%）
- 收藏扫描学习（每2小时）
- Telegram 文档学习（每2小时半点）
- GitHub Trending
- AI 社区热点

### 走 Qwen3-32B（50%）
- 管理技能学习
- Kitt 自我进化
- OpenViking 追踪
- TikTok 素材挖掘

**原因**：分散单点故障风险，豆包挂了不影响整体运转。

## 健康检查与容错

### 豆包健康检查（每30分钟）
1. 正常 → 清除 fallback 标记
2. 异常 → 自动重启服务（最多3次）
3. 连续3次失败 → 切换到 Qwen3 fallback + Telegram 通知

### 余额监控（每天22:00）
- 检查 mynewapi 余额
- 低于 $5 → Telegram 通知厂长充值

### 滚动备份（每4小时）
- 配置：`~/.openclaw/黄金备份/rolling/`
- Memory：Git 版本控制 + iCloud 同步

## 关键参数

- **Context**: 200K tokens
- **Compaction**: 24K tokens 保留
- **Heartbeat**: 55分钟（Gemini Flash）
- **Sub-agents**: 最多12个并发，60分钟后归档
- **Memory Search**: 本地语义搜索，50K 缓存

## 已知风险与缓解

| 风险 | 缓解措施 |
|---|---|
| 豆包 Web 反爬 | 健康检查 + 自动重启 + Qwen3 fallback |
| mynewapi 欠费 | 余额监控 + 9层 fallback |
| Gemini rate limit | 调度员改用 Qwen3，Gemini 降为第3位 |
| 配置损坏 | 滚动备份 + Git 版本控制 + iCloud |
| Cookie 过期 | Telegram 通知 + 手动重新登录 |

## 优化建议征集点

1. **Fallback 链顺序**：当前按成本排序，是否需要按速度或质量调整？
2. **Cron 分流比例**：50/50 是否合理？是否需要动态调整？
3. **健康检查频率**：30分钟是否太频繁？
4. **余额阈值**：$5 是否合适？
5. **Sub-agent 模型**：DeepSeek V3.2 是否最优？
6. **Context 管理**：200K 是否够用？Compaction 策略是否合理？
7. **豆包 Web 架构**：是否需要多实例部署（Kimi/ChatGPT/Gemini）？
8. **成本优化**：是否有更便宜的替代方案？

## 附件
- 脱敏配置文件：`/tmp/openclaw-redacted.json`
- 急救手册：`memory/01_强制规则/急救手册.md`
- 豆包健康检查：`~/bin/doubao-healthcheck.py`
- 余额监控：`~/bin/balance-monitor.py`
