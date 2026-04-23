# Perplexity 多Agent架构升级完整对话存档
> 来源：https://www.perplexity.ai/search/ni-shi-yi-ge-aiduo-agentxi-ton-nr1yrNX2QZaSyczjySBC6A
> 提取时间：2026-03-05 19:50
> 模型：Claude Sonnet 4.6 Thinking + GPT-5.2 Thinking（多轮）

---

## 第一轮：七个痛点根因分析 + 五个改进建议 + TOP3优先改造

### 七个痛点根因
1. 工具调用次数限制 vs 外链读取需求 → 规则粒度太粗，对不同任务类型用了同一个配额
2. logic 和 kitt 职责模糊 → 按能力维度而非决策权维度划分，边界重叠
3. 子 agent 写文件成功率 <30% → 原子性缺失，token耗尽时写文件tool call未执行
4. jimmy 上下文污染 → 无界上下文积累反模式（Unbounded Context Accumulation）
5. 记忆系统碎片化（5套机制）→ 按工具可用性而非访问模式演化
6. 心跳每55分钟消耗大量 token → 用完整LLM推理做连接保持
7. deep 的 Responses API 协议不匹配 → 缺少协议适配层

### 五个改进建议
A. logic+kitt 合并为 sage（按触发条件而非能力标签）
B. 子 agent 只返回 JSON，jimmy 统一写文件
C. 记忆系统精简为三层（长期事实层/任务状态层/临时数据层）
D. 引入上下文压缩+摘要接力（而非硬性轮换）
E. 心跳降频 + 改为轻量级状态检查脚本

### TOP3 优先改造
🥇 P1：修复子agent写文件（JSON返回 + jimmy统一写）
🥈 P2：解决jimmy上下文污染（结构化结果提取 + 水位监控）
🥉 P3：统一deep协议适配（已由框架自动处理）

### 路线图
第1周：修复子agent写文件
第2周：deep协议适配层
第3周：logic+kitt合并为sage
第4周：jimmy上下文水位监控+压缩机制
第5-6周：记忆系统三层重构+心跳轻量化

---

## 第二轮：具体实施方案（基于OpenClaw约束）

### 确认：deep协议问题已由框架解决
api: "openai-responses" 配置已处理，不需要额外操作。

### 新的派发模板
- 模板A（文件任务）：强制子agent只返回JSON，禁止写文件工具
- 模板B（纯分析）：直接输出自然语言

### 子Agent SOUL.md 追加内容
统一的【文件输出规则】块，禁止写文件，强制JSON输出。

### Jimmy 结果回收协议
Step 1：判断返回类型（JSON vs 纯文本）
Step 2：解析JSON并写文件
Step 3：更新task-board和会话日志（只写摘要）
Step 4：上下文管理（只保留摘要，不复述完整内容）
Step 5：上下文水位自检（每10轮触发一次）

---

## 第三轮：GPT-5.2 Thinking 的升级建议

### 关键隐患
1. 只靠提示词约束JSON输出，缺少schema校验门
2. jimmy手工解析JSON仍是概率系统做确定性工作
3. echo写JSONL容易被引号/换行击穿

### 升级方案：manifest + apply_manifest.py
- 增加 schema_version（版本化）
- files[].encoding 支持 utf-8 或 base64（避免转义地狱）
- 每个文件可带 sha256（可选校验）
- 原子写：先写临时文件再 os.replace
- 文件锁：防并发冲突
- 路径白名单：只允许写入指定目录

### 失败恢复（bounded retry）
1. jimmy 把子agent原样输出写到 tmp/agent_manifest.json
2. exec: python3 apply_manifest.py 进行落地
3. 若 ok=false：把错误转发回原agent要求修复JSON，重试1次
4. 再失败升级sage修复

### 新版派发模板（强制base64 manifest）
- schema_version=1.0
- encoding=base64（推荐）
- action=overwrite/create/append

### Jimmy 回收 SOP
Step A：保存原样输出到tmp
Step B：调用apply_manifest.py
Step C：一次修复重试（同一agent）→ 升级sage
Step D：上下文管理（只汇报摘要）

---

## 第四轮：Python模块方案（源码级，当前不可用）

提供了三个Python模块：
1. deep_adapter.py - deep协议适配器
2. jimmy_context_manager.py - 上下文水位管理器
3. manifest_validator.py - manifest校验器

**结论：由于我们无法修改OpenClaw源码，这些模块暂不可用。但设计思路可以通过SOUL.md规则+脚本层面实现。**

---

## 第五轮：长文档续写流水线

### 问题：子agent单次token不够写完长文档
### 方案：Phase1先出大纲 → Phase2按##逐节续写

### 工具：next_section.py
- 对比大纲与已写入的##标题，输出下一个待写章节
- jimmy用这个脚本驱动续写循环

### 会议纪要模板（8个##章节）
1. 基本信息 2. 会议目的与背景 3. 议程与讨论要点 4. 决议/决定
5. 行动项 6. 风险与依赖 7. 下一步与下次会议 8. 附件/参考资料

### 制度/SOP模板（9个##章节）
1. 目的 2. 适用范围 3. 定义与术语 4. 职责 5. 流程与操作步骤
6. 记录与表单 7. 培训与生效要求 8. 相关文件与引用 9. 修订历史

---

## 当前已完成的改造

| 改造项 | 状态 | 说明 |
|--------|------|------|
| 子agent只返回JSON | ✅ 已完成 | 所有子agent SOUL.md已更新 |
| apply_manifest.py | ✅ 已完成 | 脚本已部署并测试通过 |
| jimmy派发模板升级 | ✅ 已完成 | base64 manifest格式 |
| jimmy回收SOP | ✅ 已完成 | 确定性执行+有界重试 |
| deep协议适配 | ✅ 无需操作 | 框架自动处理 |
| logic+kitt合并sage | ⏳ 待执行 | 需要改openclaw.json |
| 上下文水位监控 | ⏳ 待执行 | 需要在SOUL.md加规则 |
| 心跳轻量化 | ⏳ 待执行 | 需要改HEARTBEAT.md |
| 记忆系统三层重构 | ⏳ 待执行 | 迁移成本最高，放最后 |
| next_section.py | ⏳ 待部署 | 长文档续写工具 |
