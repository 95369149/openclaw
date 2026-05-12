---
name: subagent-routing
version: 1.1
description: Decision table for when to inline, spawn subagents, use cron, and split execution vs grading.
---

# 子 agent 路由决策表

## 执行方式

| 场景                     | 决策                           |
| ------------------------ | ------------------------------ |
| 单次工具调用 <30s        | 内联执行                       |
| 只读查询                 | 内联                           |
| 多步骤、用户可以走开     | spawn subagent                 |
| 并行 2+ 流               | spawn subagent                 |
| 需要存活重启             | cron job                       |
| 高风险长任务需要独立验收 | 执行 agent + grader agent 拆开 |

## 能力路由

| 任务类型                    | 优先路由     |
| --------------------------- | ------------ |
| 低逻辑体力活                | deep / scout |
| 高推理 / 架构 / 审核        | kitt         |
| 中文专项                    | sino         |
| 外链 / 情报                 | scout        |
| 独立验收 / completion audit | kitt / main  |

## 使用说明

- 先判断是否必须保持主线程轻量；若是，优先考虑 subagent。
- 只读且快速可完成的任务，不要为了“形式正确”而额外拆分。
- 当任务天然可并行，优先拆给子 agent，减少主线程等待。
- 需要跨重启、跨时段持续运行的任务，不交给普通 subagent，直接用 cron job。
- 路由是默认值；若有明确上下文、权限或工具约束，以实际约束优先。

## goal / grader 原则

- 复杂任务默认拆成两段：`执行` 与 `验收`。
- 执行 agent 负责推进，不负责最终自证成功。
- grader agent 只看 `objective + 产物 + 证据`，尽量不看执行历史，降低 confirmation bias。
- 遇到“停下了”与“完成了”必须分开判断：`停止 != 完成`。
- 若存在不确定性，默认视为未完成，继续补证据或降级结论。

## 快速判断

1. 能否单次调用、30 秒内做完？能：内联。
2. 是否只是读数据、查状态、拿结果？是：内联。
3. 是否多步骤且用户无需盯着？是：spawn subagent。
4. 是否存在 2 条或以上可并行工作流？是：spawn subagent。
5. 是否要求任务跨重启继续存活？是：cron job。
6. 是否需要独立验收、防假完成、防自评偏差？是：再派 grader。
7. 再根据任务性质选 deep、scout、kitt、sino。
