# Brain-First 工作协议

## Executive Summary

Brain-first 的意思不是“有了知识库”，而是每次遇到人、公司、项目、制度、概念问题时，先查 brain，再回答，再把新事实写回去，让系统随着每次对话变聪明。

## State

- 类型：工作协议 / 方法论
- 当前状态：已形成初版，待逐步嵌入 AGENTS 执行习惯
- 重要性：P0
- 关键关系：brain、memory、OpenClaw、Kitt、gbrain

## Compiled Truth

- 关于长期知识的问题，优先查 `brain/`，不是只靠上下文记忆硬答。
- `memory/` 负责运行态和任务态；`brain/` 负责长期知识与编译结论。
- 新事实优先更新已有页面，不轻易新建重复页。
- 原始材料先进 `sources/`，结论写回实体页，这是“来源层”和“知识层”的分工。
- 未来接入 gbrain 后，这套协议不变，只是查找方式更强。

## Open Threads

- [ ] 后续把协议补进 AGENTS 或技能层约束。
- [ ] 给常见工作流补 brain-first 示例。

## See Also

- [本机 brain 本地化落地计划（无 Supabase 版本）](../projects/local-brain-rollout-plan.md)
- [按 Garry Tan 方法升级本机知识脑](../projects/openclaw-kitt-brain-upgrade.md)

---

## Timeline

- 2026-04-12 | 来源：本机 brain 落地过程总结 | 正式抽象出 brain-first 工作协议，作为后续本地与数据库版本共用的方法论。
