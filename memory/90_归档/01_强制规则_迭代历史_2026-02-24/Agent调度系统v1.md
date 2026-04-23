# Agent 调度系统 v1.0

## 版本信息

- 版本: 1.0
- 日期: 2026-02-22
- 测试状态: ✅ 通过（M1 内容生产流程）
- 参考: Anthropic multi-agent research system

## 架构

### 完整流程

```
用户输入
  → Triage 分类（GLM 4.5 Air，<1s，100% 准确）
  → 查路由配置（intent_routes.json）
  → 执行 DAG（Kitt → 侦察/工兵 → 质检）
  → 质检评分（≥6 通过，<6 打回）
  → 交付物返回
```

### 核心组件

1. **Triage 模块**
   - 模型: GLM 4.5 Air (¥0.5/0.5)
   - 准确率: 100% (10/10)
   - 输出: `{"intent_bucket": "S1", "confidence": "high"}`

2. **路由查询**
   - 配置: `intent_routes.json`
   - 包含: DAG、模型分配、验收标准、截止时间、human_gate

3. **DAG 执行器**
   - 上下文传递: 每个 Agent 的输出传给下游
   - 并行支持: 未实现（v1.0 串行执行）
   - 失败重试: 未实现（v1.0 无 fallback）

4. **质检模块**
   - 输入: 工兵输出 + 验收标准
   - 输出: `{"score": 10, "passed": true, "issues": [], "summary": "..."}`
   - 阈值: ≥6 通过

## 测试结果

### M1 内容生产（快）测试

**输入**

```
写条朋友圈文案，推下新产品
```

**Triage**

- 意图桶: M1
- 置信度: high

**DAG 执行**

1. Kitt: 明确受众+平台+调性 → ✅
2. 工兵(DS-SF): 出稿 → ✅
3. 质检(GLM 4.6): 品牌调性+错别字 → ✅

**工兵输出**

```
【新品首发 | 效率革命，就此开启】
✅ 一键连接多设备，文件秒传
✅ 离线也能同步协作，断电不慌
✅ 隐私加密芯片，数据只属于你
👇点击预约，限时尝鲜价解锁
```

**质检结果**

- 评分: 10/10
- 状态: ✅ 通过
- 问题: 无
- 总结: 文案质量优秀，完全符合平台调性与验收标准

## 关键设计（参考 Anthropic）

### 1. 上下文传递

每个 Agent 的输出保存到 `context` 字典，下游 Agent 可以访问：

```python
context = {"user_input": user_input}
context['工兵'] = output  # 工兵输出
# 质检拿到工兵输出
upstream_output = context.get('工兵', '[无上游输出]')
```

### 2. 质检 Prompt 结构

```
你是质检 Agent，任务：品牌调性+错别字

用户需求：{user_input}

工兵输出的内容：
---
{upstream_output}
---

验收标准：{route['acceptance']}

请按以下格式输出 JSON：
{"score": <1-10>, "passed": <true|false>, "issues": [...], "summary": "..."}
```

### 3. 模型分配

- Triage: GLM 4.5 Air (最便宜)
- 工兵: DeepSeek V3.2 (性价比)
- 质检: GLM 4.6 (替代 Gemini Flash)
- 侦察: Perplexity/Grok (外部搜索)

## 已知限制（v1.0）

1. **串行执行** — DAG 步骤顺序执行，未实现并行（Anthropic 的 subagent 是并行的）
2. **无 fallback** — 模型失败不会自动切换备选
3. **无重试** — 质检不通过不会打回重做
4. **无 ELO 跟踪** — 模型性能评分未实现
5. **无 human_gate** — SC1/SC2/M2 的人工审批未实现
6. **侦察未实现** — Perplexity/Grok 调用需要外部 API

## 下一步（v2.0 规划）

1. **并行 subagent** — 侦察任务并行执行（参考 Anthropic）
2. **Fallback 链** — 模型失败自动切换备选
3. **质检重试** — <6 分打回工兵重做（最多 2 次）
4. **ELO 跟踪** — 记录模型评分到 `memory/05_日常日志/模型绩效.md`
5. **Human gate** — SC1/SC2/M2 发送审批请求到 Telegram
6. **侦察集成** — 接入 Perplexity/Grok API
7. **Excel 集成** — DataOps 读写 WPS 文件

## 文件位置

- 调度器脚本: `memory/01_强制规则/agent_dispatcher.py`
- Triage prompt: `memory/01_强制规则/Triage_Prompt_v2.md`
- 路由配置: `memory/01_强制规则/intent_routes.json`
- 协作体系: `memory/01_强制规则/多Agent协作体系v3.md`

## 使用方法

```bash
# 测试单个任务
python3 memory/01_强制规则/agent_dispatcher.py

# 集成到 Kitt（待实现）
# Kitt 收到消息 → 调用 triage() → 调用 execute_dag() → 返回结果
```

## 成本估算

**M1 内容生产（快）单次成本**

- Triage: GLM 4.5 Air ~50 tokens → ¥0.00003
- 工兵: DeepSeek V3.2 ~300 tokens → ¥0.0006
- 质检: GLM 4.6 ~200 tokens → ¥0.0004
- **总计: ~¥0.001 (0.1 分钱)**

**对比**

- 单 Agent (Sonnet 4.6): ~¥0.05 (5 分钱)
- 多 Agent 系统: ~¥0.001 (0.1 分钱)
- **成本降低 50 倍，质量提升（有质检）**

## 参考资料

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Azure: AI Agent Orchestration Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
- 内部文档: `memory/01_强制规则/意图桶与场景DAG.md`
