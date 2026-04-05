# evolution scout｜2026-03-18

- 时间：2026-03-18 21:00 Asia/Shanghai
- 任务：weekly_evolution_pipeline v2

## 一、本周最值得关注的外部新内容

### 1) Microsoft Research：PlugMem
- 链接：https://www.microsoft.com/en-us/research/blog/from-raw-interaction-to-reusable-knowledge-rethinking-memory-for-ai-agents/
- 核心：把原始交互历史转为结构化知识单元（facts + reusable skills），而不是长文本检索。
- 启发：我们的记忆系统不能只做“搜得到”，还要做“提炼后可复用”。

### 2) Context Engineering 近期实践总结
- 链接：https://www.instinctools.com/blog/context-engineering/
- 核心：模型出错常常不是模型弱，而是上下文污染、过载、失焦；重点在工具瘦身、上下文裁剪、摘要和外置记忆。
- 启发：Lyra 与 weekly/daily pipeline 要从 prompt 组织升级为 context 治理。

### 3) OpenClaw 生态安全/治理讨论升温
- 链接：https://vallettasoftware.com/blog/post/openclaw-2026-guide
- 核心：外部视角已明显把注意力放到 skill 供应链风险、默认暴露面、权限治理。
- 启发：OpenClaw 下一阶段竞争力不仅是能力，更是“可控、可审计、可维护”。

### 4) Scout 脚本自身失真
- 现象：`evolution_scout.py` 本轮只产出 1 条示例发现 `https://example.com`。
- 判断：侦察链路本身未完成真实化，是本周最明确的内部短板。
- 启发：先修 Scout，再谈高阶碰撞，否则会把高级模型预算浪费在低质输入上。

## 二、对 OpenClaw / Lyra / 记忆系统的潜在启发

### OpenClaw
- 补侦察质量和安全治理优先于继续加功能。
- 可以建立可信来源白名单，降低外部学习噪声。

### Lyra
- 把“提示词层”升级为“上下文编排层”。
- 要标准化：什么时候压缩、什么时候召回、什么时候只给 facts 不给原文。

### 记忆系统
- 从“文档记忆”进化到“知识单元记忆”。
- 应加入 recency、reuse frequency、decision relevance 三类信号。

## 三、建议优先级
- P0：修复 Scout 真实化；建立 facts/skills 结构化提炼；制定 context hygiene 规则。
- P1：加 weeklyEvolution 指标；建可信来源白名单；建待深度碰撞队列。
- P2：轻量知识图谱；风险打分；季度进化复盘。

## 四、结论
本周真正值得做的不是立刻开高级模型，而是先把输入质量、记忆提炼、上下文治理三件基础设施补齐。等基础稳了，再去 Perplexity 做多轮深挖，才不会高成本撞空气。
