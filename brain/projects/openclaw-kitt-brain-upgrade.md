# 按 Garry Tan 方法升级本机知识脑

## Executive Summary

这个项目的目标不是照抄 Garry Tan 的全部环境，而是把他“brain repo + 检索层 + agent 工作流”的方法迁到厂长这台 OpenClaw 电脑上。

## State

- 类型：项目
- 当前状态：启动中
- 重要性：P0
- 负责人：Kitt / Jimmy

## Compiled Truth

- 这台机器已经具备做 brain 的前提：大量 markdown、长期对话、cron、agent 执行能力。
- 正确路径不是先上数据库，而是先把现有知识整理成独立的 `brain/` 目录与 schema。
- `memory/` 保持 agent 运行记忆职责；`brain/` 承接长期知识；`gbrain` 作为后续检索层接入。
- 第一阶段重点是：建骨架、建 resolver、建 schema、沉淀核心页面。
- 第二阶段再接 Supabase + gbrain import/query/sync/update-check。

## Open Threads

- [ ] 补全 `brain/` 首批目录与代表性页面。
- [ ] 逐步把高价值长期知识从 memory 中迁出到 brain。
- [ ] 待用户提供 Supabase 连接串后，接 gbrain 数据库层。
- [ ] 增加按 Garry 方法工作的 cron 与 enrichment 流程。

## See Also

- [厂长](../people/changzhang.md)
- [济南红太阳数控设备有限公司](../companies/jinan-red-sun-cnc.md)

---

## Timeline

- 2026-04-11 | 来源：用户指令 + gbrain README + GBRAIN_SKILLPACK + GBRAIN_RECOMMENDED_SCHEMA | 确认采用“brain repo + gbrain 检索层 + OpenClaw 工作流”的三层方案，不照搬而是本地化落地。
