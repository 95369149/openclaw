# evolution_scout 周侦察记录｜2026-03-25

- 时间：2026-03-25 21:00 Asia/Shanghai
- 类型：weekly_evolution_pipeline v2
- 模式：Scout-first / 外部碰撞预备版

## 运行结果

- `evolution_scout.py` 已运行，但当前输出仍为占位型结果：`示例发现 / 待实现：真实搜索结果`。
- 因此本周结论主要来自补充外链学习，而非脚本本体产出。

## 补充外链学习（已读）

1. OpenClaw 2026.3 Advanced Practice  
   https://eastondev.com/blog/en/posts/ai/20260318-openclaw-2026-3-advanced/
2. State of Context Engineering in 2026  
   https://www.newsletter.swirlai.com/p/state-of-context-engineering-in-2026
3. Why your multi-agent AI system has a memory problem  
   https://www.resultsense.com/insights/2026-03-19-multi-agent-memory-computer-architecture-perspective

## 本周最值得关注的发现

1. **Context engineering 主流范式已收敛**：最近上下文保留原文，更早内容做摘要压缩，技能/资料按需激活，不再把所有东西一次性塞进窗口。
2. **错误轨迹应保留而非压缩掉**：外部实践明确指出，失败调用和错误栈保留在上下文里，有助于避免重复犯错。
3. **多 Agent 记忆应分层**：I/O、Cache、Memory 三层明确分工，否则共享存储会带来脏读、冲突和重复计算。
4. **共享记忆需要协议而非默契**：谁能读、谁能写、何时可见、如何覆盖旧版本，需要规则化。
5. **OpenClaw 生态关注点转向治理能力**：smart pruning、secrets workflow、sandbox 多后端、人类在环，说明稳定性和安全性已成主线。

## 对 OpenClaw / Lyra / 记忆系统的启发

- OpenClaw：优先做上下文裁剪与工具输出治理，而不是继续堆功能。
- Lyra：适合引入“手动深碰撞包”，由日常 Scout 先收集材料，再在交互场景调用高端模型做深推理。
- 记忆系统：当前 `shared/` 更像协作文档层，不应直接等同长期记忆；需要 facts/skills 双层提炼。

## 建议动作

### P0

- 修复 `evolution_scout.py` 真实侦察输出
- shared/ops 记忆增加版本元数据与覆盖关系
- 明确 I/O / Cache / Memory 三层边界

### P1

- 上下文卫生规则产品化（保留最近原文、压缩旧历史、保留错误轨迹）
- 把长期高价值内容提炼成 facts/skills
- 每周自动生成 Perplexity 预碰撞包

### P2

- skill 激活冲突治理
- sandbox 风险分级
- secrets/config 继续收口

## 对外发送说明

按本次 cron 指令：**不实际外发消息**。应备注去向：`telegram:8184569453`。
建议发送摘要：本周发现 + 最值得做的 3 条改进 + “如需深度碰撞，再由 jimmy 手动去 Perplexity 用高级模型多轮问询”。
