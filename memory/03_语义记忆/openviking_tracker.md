# OpenViking 项目追踪
> GitHub: volcengine/OpenViking
> 描述: AI Agent 上下文数据库，文件系统范式管理记忆/资源/技能
> 首次记录: 2026-02-25

## 项目概况
- ⭐ 3746 stars | 🍴 285 forks
- 最新版本: v0.1.18 (2026-02-23)
- 最新推送: 2026-02-25

## 最新动态 (2026-02-25)

### 最近 Commits
1. `feat: break change, remove is_leaf scalar and use level instead` (#271) — 重构层级标识
2. `tests(parsers): add unit tests for office extensions` (#273) — 办公文档解析测试
3. `feat: add parts support to http api` (#270) — HTTP API 增强
4. `fix: claude code memory-plugin example` (#268) — Claude Code 插件修复
5. `feat: concurrent embedding, GitHub ZIP download, read offset/limit, code parser optimization` (#267) — 并发嵌入+代码解析优化

### Releases
- v0.1.18 (2026-02-23) — 最新
- v0.1.17 (2026-02-14)
- CLI v0.1.0 (2026-02-14)

## 与我们的关联
- L0/L1/L2 分层加载 → 我们可以用 .abstract 索引文件实现
- P0/P1/P2 保质期 → 我们可以用清理脚本实现
- 共享记忆层 → 我们可以用 memory/shared/ 实现
- 详见: memory/03_语义记忆/Elvis_Agent_Swarm_深度分析.md

## 关注重点
- 新 release 版本
- Claude Code / OpenClaw 相关的 commit
- 记忆分层和清理机制的改进
- 共享记忆的实现方式
