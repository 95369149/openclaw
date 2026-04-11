# 本机 brain 本地化落地计划（无 Supabase 版本）

## Executive Summary

在 Supabase 数据库连接暂未就位前，本机仍可按 Garry Tan 方法继续推进：先把 `brain/` 做成可读、可查、可持续写回的长期知识层，待后续再无缝接上 gbrain 数据库与检索能力。

## State

- 类型：项目计划
- 当前状态：执行中
- 重要性：P0
- 关键关系：brain、OpenClaw、memory、gbrain、cron

## Compiled Truth

- 数据库层是增强项，不是起步前提。
- 当前最有价值的动作是：继续扩充高价值 brain 页面、建立来源层、形成 brain-first 工作习惯。
- 等用户后续拿到连接串，再执行 `gbrain init --supabase` 和导入，不会推翻现有工作。
- 因为 `brain/` 已采用 resolver + schema + compiled truth + timeline 结构，后续接库成本很低。

## Open Threads

- [ ] 继续沉淀高价值 pages：客户、产品、制度、项目、内容资产。
- [ ] 建立来源页与成品页之间的引用关系。
- [ ] 后续补一个 brain-first 操作规范。
- [ ] 等连接串到位后再接 gbrain。

## See Also

- [按 Garry Tan 方法升级本机知识脑](./openclaw-kitt-brain-upgrade.md)
- [gbrain 本地接入状态](./gbrain-bootstrap-status.md)

---

## Timeline

- 2026-04-12 | 来源：用户明确放弃继续查找连接串 | 决定先走无 Supabase 的本地 brain 落地路线，后续再补数据库层。
