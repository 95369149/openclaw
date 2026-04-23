# 语义记忆：OpenClaw 架构深度分析（v2026.2.15）

## 来源

@0xCherry 架构吐槽 + @BillTheInvestor 更新解读（2026-02-18 收藏，2026-02-21 消化）

## 架构真相（@0xCherry 祛魅）

- Agent Loop 本质：基于 pi-ai SDK 的连续工具调用，无复杂推理规划层
- 伪异步：30 分钟定时轮询，非事件驱动（解释了 Cron 延迟）
- 核心工具三板斧：Browser + File + Cmd（与 Claude Code 高度重合）
- 唯一创新：File Driven — 文件下载/截图/多模态深度融入架构
- Vibe Coding 产物，代码健壮性存疑

## v2026.2.15 六大升级（@BillTheInvestor）

1. 智能上下文缓存：Token 砍 30-60%
2. 子代理调度：事件驱动 + 休眠唤醒（修复轮询问题），省 40-70% Token
3. 并行工具调用 + 结果裁剪
4. 成本感知路由：按复杂度自动切模型
5. Discord Components v2：原生按钮/菜单/Modal
6. 企业级安全：修复 SSRF、容器逃逸

## 对我们的指导

- File Driven 是 OpenClaw 亮点，我们的 memory 架构正好契合
- 新版成本感知路由 = 我们的军师调度模式，未来可能原生支持
- 升级后 Token 消耗降 40-70%，月成本可降至几十美元
- 代码健壮性不足 → 保持黄金备份习惯，做好容灾
