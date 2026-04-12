# OpenViking Claude Memory Plugin 研究笔记

> 来源: https://github.com/volcengine/OpenViking/tree/main/examples/claude-memory-plugin
> 日期: 2026-02-24

## 架构

基于 OpenViking Session Memory 的 Claude Code 插件，通过 hooks 机制实现自动记忆。

### 工作流
1. **SessionStart** — 创建 OpenViking session，自动检测后端（HTTP/本地）
2. **UserPromptSubmit** — 注入"记忆可用"提示
3. **Stop**（异步）— 解析对话，用 haiku 摘要，写入 session
4. **SessionEnd** — commit session，提取长期记忆

### 记忆检索
`memory-recall` skill 搜索 `viking://user/memories/` 和 `viking://agent/memories/`，返回带来源的摘要。

## 对 Kitt 的启发

### 可借鉴
1. **Hook 机制** — 每轮对话结束自动摘要写入，不依赖手动。我们可以在心跳里做类似的事
2. **双模式后端** — HTTP 优先，本地 fallback。我们可以考虑本地跑 OpenViking 实例
3. **自动去重** — 按 user turn UUID 去重，避免重复记忆

### 不适用
1. 它是 Claude Code 插件，我们是 OpenClaw，hook 机制不同
2. 依赖 `claude -p` CLI，我们不用这个
3. 需要 `ov.conf` 配置 OpenViking server

### 结论
核心思路（自动摘要+分层记忆+语义检索）我们已经用 L0/memory_search 实现了。OpenViking 的优势在于向量化检索和 session 级别的记忆管理，但对我们当前规模（300 文件）来说，markdown + memory_search 够用。

等文件量超过 1000 或需要跨 agent 共享记忆时，再考虑接入 OpenViking 作为后端。
