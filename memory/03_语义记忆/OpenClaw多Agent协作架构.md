# OpenClaw 多 Agent 协作架构解析

> 来源：余温 @gkxspace — https://x.com/gkxspace/status/2024093343118950463
> 日期：2026-02-18

## 核心架构
Single Gateway + 5 Agent + 5 独立 Workspace + 双通道（Discord+Telegram）

## 5 角色分工
- 总指挥（zongzhihui）：全局态势感知、任务拆解、派工、纠偏、收口
- 军师（junshi）：策略分析、方案评估、风险预判
- 工程师（engineer）：技术执行、代码实现、系统维护
- 创作官（creator）：内容创作、表达优化、对外输出
- 智库（zhiku）：知识审核、质量把关、合规检查

## 关键配置
- bindings：`channel + accountId -> agentId` 显式路由，入口层分诊
- dmScope：`per-account-channel-peer`（账号+渠道+对端 三维隔离）
- 群聊：总指挥 `requireMention=false` 全局监听，其他4角色 `requireMention=true` @触发
- mentionPatterns：每角色配中英文触发词
- agentToAgent ping-pong 限制设为 0，压制 AI 互相客套循环

## 双轨治理
- 配置轨（平台级）：channel policy / bindings / dmScope / ping-pong 限制
- 规则轨（行为级）：SOUL.md / AGENTS.md / ROLE-COLLAB-RULES.md / TEAM-RULEBOOK.md / TEAM-DIRECTORY.md

## Workspace 标准文件
SOUL.md / AGENTS.md / ROLE-COLLAB-RULES.md / IDENTITY.md / USER.md / TOOLS.md / MEMORY.md / GROUP_MEMORY.md / HEARTBEAT.md / memory/YYYY-MM-DD*.md

## 记忆分层
1. 短期流水（daily memory）→ 按日期文件
2. 长期记忆（MEMORY.md）→ 验证后的稳定信息
3. 群聊记忆（GROUP_MEMORY.md）→ 隐私隔离
4. 冷归档（archive）→ 防膨胀

## 对我们的启发
- 我们当前是单 Agent + spawn worker 模式，他是 5 Agent 并行
- 他的 TEAM-RULEBOOK.md / ROLE-COLLAB-RULES.md 值得借鉴——我们缺协作边界文件
- GROUP_MEMORY.md 隐私隔离思路好，群聊记忆和私聊记忆分开
- Discord 确实更适合多 Agent 可视化协作（角色身份可见、对话链可见）
- ping-pong=0 是个好实践，防止 AI 互相废话
