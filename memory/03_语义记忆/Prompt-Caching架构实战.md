# 语义记忆：Prompt Caching 架构实战

## 来源
Claude Code 团队 Thariq 分享（2026-02-20 收藏消化）

## 核心原则
Prompt caching 通过前缀匹配工作 — 内容顺序决定缓存命中率。

## 最佳排列顺序
1. Static system prompt & Tools（全局缓存）
2. 项目级上下文（如 CLAUDE.md）
3. Session context（会话内缓存）
4. Conversation messages（动态内容）

## 8 条铁律（对我们的指导）

| # | 规则 | 对 Kitt 系统的意义 |
|---|------|-------------------|
| 1 | 静态在前，动态在后 | SOUL.md/TOOLS.md 放最前，不要加时间戳 |
| 2 | 用系统消息更新信息 | 不改核心提示词，用 reminder 追加 |
| 3 | 不要在会话中切换模型 | 每个模型缓存独立，切模型=全价重算 |
| 4 | 不要增删工具 | 工具是缓存前缀的一部分，动了就全废 |
| 5 | Plan Mode 用工具实现 | 不换工具集，用 EnterPlanMode 工具切换 |
| 6 | 延迟加载工具 | 发轻量存根，按需加载完整 schema |
| 7 | Cache-Safe Forking | 压缩上下文时保持相同前缀，只追加压缩提示 |
| 8 | 监控缓存命中率 | 当核心指标看，低了就是事故 |

## 对我们系统的行动项
- 提示词文件顺序已优化（SOUL → TOOLS → AGENTS → 动态）✓
- 避免在 SOUL.md 中放时间戳或动态内容
- 子 agent 切模型比主会话切模型更省（已有 fallback 链）
- 上下文压缩时保持前缀不变（OpenClaw 的 context 保留机制）
