# 2026-02-18 本地 Issue Driven 开发 (@YuLin807)

## 来源

- Author: @YuLin807 (Qingyue)
- Date: 2026-02-18
- Link: https://x.com/yulin807/status/2023941489198592111

## 核心理念：结构化主动性

通过建立本地化的 Issue 追踪系统，让低端模型 (Minimax) 通过流程获得类似高端模型 (Opus) 的主动性。

### 架构设计

1. **角色分工**：
   - **大龙虾 (Manager)**：负责巡查、发现问题、创建 Issue。
   - **小弟 (Workers)**：认领 Issue、执行任务、反馈结果。
2. **流程**：
   - Create Issue (Markdown 文件) -> Dispatch (派发给 Sub-agent) -> Execute -> Close Issue。
3. **价值**：
   - **可追踪**：Issue Closed = 进化证据。
   - **可视化**：每天的任务进度一目了然。
   - **低成本**：用流程弥补模型智商，用 cheap model 跑 worker。

## Kitt 思考

- **现有缺陷**：目前我们的任务管理主要依赖 `active-context.md` 的文本列表，缺乏状态管理和并发执行能力。
- **落地计划**：
  1. 在 workspace 建立 `issues/` 目录。
  2. 定义 Issue 模板 (Title, Status, Assignee, Context, Result)。
  3. 编写 `issue` 工具 (Skill)，支持 create/list/claim/close 操作。
  4. 将心跳检测 (Heartbeat) 升级为 "Issue 调度器"。

<!-- digested: 2026-02-21 -->
