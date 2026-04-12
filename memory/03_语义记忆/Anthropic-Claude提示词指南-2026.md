# Anthropic Claude 提示词工程指南 2026

> 来源：platform.claude.com 官方文档 | 整理日期：2026-02-19

## 核心技巧（按效果排序）

### 1. 清晰、直接、详细
- 把 Claude 当成一个聪明但没有上下文的新员工
- 提供背景信息：任务目的、受众、工作流位置、成功标准
- 用编号步骤给出指令，而非模糊描述
- 黄金法则：把 prompt 给一个不了解背景的同事看，如果他困惑，Claude 也会困惑

### 2. 多示例提示（Multishot）
- 提供 2-5 个输入→输出示例
- 示例越多样，Claude 越能泛化
- 示例应覆盖边界情况

### 3. 让 Claude 思考（Chain of Thought）
三个层级：
- 基础：加 "Think step-by-step"
- 引导：描述具体思考步骤
- 结构化：用 `<thinking>` 和 `<answer>` XML 标签分离推理和答案

适用场景：复杂数学、多步分析、多因素决策
不适用：简单查询（增加延迟无收益）

⚠️ 关键：必须让 Claude 输出思考过程，不输出 = 没思考

### 4. XML 标签结构化
- 用 `<instructions>`、`<example>`、`<data>` 等标签分隔 prompt 各部分
- 标签名无固定要求，语义清晰即可
- 嵌套标签处理层级内容
- 在引用时指明标签名："Using the contract in `<contract>` tags..."
- 输出也可要求用 XML 标签，方便后处理解析

### 5. 角色提示（System Prompt）
- 用 `system` 参数设定角色，而非在 user 消息中
- 角色越具体越好："Fortune 500 公司的总法律顾问" > "律师"
- 角色影响：准确度、语气、关注点
- system prompt 只放角色定义，任务指令放 user turn

### 6. 链式提示（Chain Prompts）
- 复杂任务拆成多个步骤，每步一个 prompt
- 前一步输出作为后一步输入
- 适合：多阶段分析、文档处理管线

### 7. 长上下文技巧
- 长文档放 prompt 顶部，查询/指令放底部（可提升 30% 质量）
- 多文档用 XML 包裹：`<document index="1"><source>...</source><document_content>...</document_content></document>`
- 要求 Claude 先引用相关段落再回答（grounding）

## Prompt Caching

### 机制
- 在 system prompt 或 messages 中标记 `cache_control: {"type": "ephemeral"}`
- 首次调用创建缓存（`cache_creation_input_tokens`）
- 后续调用命中缓存（`cache_read_input_tokens`），成本降 90%

### 最佳实践
- 把不变的大块内容（文档、规则、示例）放在前面并标记缓存
- 变化的查询放在后面
- 缓存 TTL 默认 5 分钟（ephemeral）
- 最小缓存块：1024 tokens（Sonnet/Opus）、2048 tokens（Haiku）

### OpenClaw 中的应用
- `cacheRetention: "long"` 已在 Opus 配置中启用 ✅
- `contextPruning.mode: "cache-ttl"` 配合 pruning 优化缓存命中 ✅

## Kitt 优化建议

### 已做得好的
1. SOUL.md 用了角色定义（搭档、随性风格）✅
2. 记忆分层加载减少上下文噪音 ✅
3. Opus 配置了 cacheRetention ✅
4. 指令用了编号步骤（AGENTS.md）✅

### 可优化的
1. **SOUL.md 可加 XML 标签结构化**
   - 当前用 markdown 分节，对 Claude 来说 XML 标签更精确
   - 建议：`<identity>`, `<rules>`, `<style>`, `<memory_protocol>` 包裹各节
   - 但注意：OpenClaw 的 system prompt 是自动拼接的，需要确认是否支持

2. **子 agent 任务 prompt 可加结构化思考**
   - 学习任务加 `<thinking>` 标签要求先分析再输出
   - 但注意：非 Claude 模型（DeepSeek/Qwen/Llama）对 XML 标签的遵从度不如 Claude

3. **长文档处理时用 grounding 技巧**
   - 分析长文档前要求先引用关键段落
   - 减少幻觉，提高准确度

4. **HEARTBEAT.md 可更结构化**
   - 当前是 markdown 列表，可改为带优先级的结构化格式
   - 但当前格式已经够用，改动收益不大

### 不建议改的
- SOUL.md 的 markdown 格式：当前简洁易读，对 DeepSeek（主力模型）来说 markdown 和 XML 效果差异不大
- 子 agent prompt 加 XML：主要用 Groq Llama，XML 标签遵从度不稳定
