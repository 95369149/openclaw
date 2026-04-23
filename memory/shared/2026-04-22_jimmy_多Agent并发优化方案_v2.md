# 多 Agent 并发优化方案 v2.0（基于官方文档验证）

整理时间：2026-04-22
验证来源：OpenClaw 官方文档 + Azure 官方示例 + LangGraph 生产实践

---

## 一、已验证的核心事实

### 来源 1：OpenClaw 官方文档（learnopenclaw.com）

**确认的事实：**
- `sessions_spawn` 支持并行派发，主 Agent 可以继续做其他事
- 实际并发上限：**3-5 个并发子 Agent**（官方推荐，超过会 hit rate limit）
- 子 Agent 不能 spawn 子 Agent（目前限制，未来会放开）
- 子 Agent 之间不能直接通信，必须通过主 Agent 中转
- **成本优化策略**：协调者用贵模型（Opus/GPT-4），工人用便宜模型（GPT-4o-mini）

**官方推荐的 4 种架构模式：**

| 模式 | 用途 | 我们的对应场景 |
|------|------|----------------|
| **Coordinator + Workers** | 主 Agent 派发任务给多个工人 | jimmy → scout/deep/main |
| **Pipeline** | A → B → C 顺序处理 | 调研 → 写作 → 审核 |
| **Specialist Routing** | 根据任务类型路由到不同专家 | 图片→main, 代码→deep |
| **Fan-Out / Fan-In** | 并行派发 N 个任务，汇总结果 | X 日报 11 账号并行抓取 |

### 来源 2：Azure CosmosDB 多 Agent 示例（微软官方）

**验证的生产架构：**
```
用户请求 → Triage Agent（分流）→ 三种 Specialist Agent
                              ↳ Product Agent（RAG 查询）
                              ↳ Refund Agent（退款处理）
                              ↳ Sales Agent（下单处理）
```

**关键设计：**
- **Triage Agent 只做一件事**：判断请求类型，然后 handoff（移交）
- **每个 Specialist 有独立工具集**：Product Agent 有 RAG，Refund Agent 有数据库写权限
- **状态持久化**：用 CosmosDB 存对话状态，支持长时间运行和故障恢复

### 来源 3：LangGraph 生产实践（Klarna/Replit/Elastic 在用）

**验证的技术特性：**
- **Durable execution**：Agent 崩溃后能从断点恢复
- **Human-in-the-loop**：关键节点可以暂停等人审批
- **Comprehensive memory**：短期工作记忆 + 长期持久记忆

---

## 二、针对红太阳 Kitt 的优化方案

### 现状 vs 目标

| 维度 | 现状 | 目标（基于官方最佳实践） |
|------|------|------------------------|
| 派发方式 | 串行等待 | Fan-Out 并行（3-5 个并发） |
| 模型策略 | 全用 GPT-4/Opus | 协调者贵，工人便宜 |
| 状态管理 | 无持久化 | 关键任务加 checkpoint |
| 失败处理 | 超时卡死 | 局部失败 + 降级 |
| 工人通信 | 不支持（符合设计） | 通过主 Agent 中转 |

### 立即可落地的三项改造

#### 改造 1：Fan-Out 并行派发（官方 Pattern 4）

**OpenClaw 官方示例代码结构：**
```javascript
// 三个并行研究任务
sessions_spawn({
  instruction: "Research competitor pricing...",
  model: "gpt-4o-mini",  // 工人用便宜模型
  onComplete: "Add to report"
})

sessions_spawn({
  instruction: "Analyze support tickets...",
  model: "gpt-4o-mini",
  onComplete: "Add to report"
})

sessions_spawn({
  instruction: "Summarize metrics...",
  model: "gpt-4o-mini",
  onComplete: "Add to report"
})

// 主 Agent 继续工作，等结果 push 回来
```

**我们的落地：**
- X 日报：11 个账号分 3 批（4+4+3），每批内部并行
- 竞品调研：同时 spawn 3 个 scout，分别查不同竞品
- 多文件处理：同时 spawn 多个 deep，分别处理不同文件

#### 改造 2：模型分层策略（官方成本优化）

| 角色 | 当前模型 | 建议模型 | 成本节省 |
|------|---------|---------|---------|
| jimmy（协调者） | GPT-5.4 | GPT-5.4 | 基准 |
| scout（信息收集） | Gemini 3 Pro | Gemini 3 Flash | ~70% |
| deep（代码执行） | GPT-5.4 | GPT-4o-mini | ~90% |
| main（多模态） | Gemini 3 Pro | Gemini 3 Pro | 不变 |
| sino（中文改写） | kimi-k2.6 | kimi-k2.6 | 不变 |

**注意**：OpenClaw 官方说"协调者用贵模型，工人用便宜模型"，但我们工人也要做复杂任务，不能一刀切。建议 scout 查简单网页时用 Flash，查复杂仓库时用 Pro。

#### 改造 3：局部失败处理（Azure 模式借鉴）

Azure 示例中的错误处理：
```python
# 每个 Specialist Agent 返回结构
{
  "status": "success|failed",
  "result": "...",
  "error": "..."  // 失败时填
}

# Triage Agent 汇总时跳过 failed，报告哪些失败了
```

**我们的落地：**
```json
// scout 返回的 manifest
{
  "status": "success|failed|timeout",
  "key_findings": [...],
  "error_context": "...",
  "produced_by": "scout",
  "produced_at": "..."
}

// jimmy 汇总逻辑
successful = [m for m in manifests if m.status == "success"]
failed = [m for m in manifests if m.status != "success"]

if len(failed) > 3:
  return "以下任务失败，需要人工处理：..."
else:
  return 用 successful 生成报告 + "注：以下任务失败已跳过：..."
```

---

## 三、具体场景改造计划

### 场景 1：X 日报生成（Fan-Out 经典场景）

**当前：** 串行抓 11 个账号，~3 分钟
**目标：** 并行抓，~20 秒

**分批策略（遵守 3-5 并发上限）：**
```
Batch 1: dotey, shao__meng, op7418, Yangyixxxx
Batch 2: vista8, wwwgoubuli, tuturetom, balconychy
Batch 3: aigclink, HiDangChen, Gorden_Sun
```

**每批内部并行**，批间串行（避免 hit rate limit）。

### 场景 2：竞品调研（Coordinator + Workers）

**当前：** jimmy 自己查完再写报告
**目标：** 同时 spawn 3 个 scout，分别查：
- scout_1：竞品 A 的产品特性
- scout_2：竞品 B 的定价策略
- scout_3：竞品 C 的市场定位

jimmy 汇总三家结果，生成对比报告。

### 场景 3：多文件处理（Pipeline + Fan-Out 混合）

**示例：处理 10 份销售报告**
```
Step 1（Fan-Out）：同时 spawn 5 个 deep，分别处理 2 份报告 → 提取关键数据
Step 2（Pipeline）：main 汇总所有数据 → 生成图表
Step 3（Pipeline）：sino 润色 → 生成最终报告
```

---

## 四、风险与规避

| 风险 | 来源 | 规避方案 |
|------|------|---------|
| 子 Agent 超时 | OpenClaw 官方限制 | 每个 spawn 加 timeout 参数 |
| Rate limit | OpenClaw 官方警告 | 控制并发 3-5 个，分批执行 |
| 子 Agent 不能 spawn 子 Agent | OpenClaw 当前限制 | 所有分解在主 Agent 完成 |
| 状态不持久 | 当前无 checkpoint | 关键任务让子 Agent 写文件落盘 |
| 成本失控 | 并行 = 同时扣费 | 工人用便宜模型，控制并发数 |

---

## 五、实施优先级（基于验证来源）

| 优先级 | 改造项 | 难度 | 验证来源 |
|--------|--------|------|---------|
| P0 | 控制并发 3-5 个 | 5分钟 | OpenClaw 官方 |
| P1 | X 日报 Fan-Out 改造 | 2小时 | OpenClaw Pattern 4 |
| P2 | 模型分层（scout→Flash） | 30分钟 | OpenClaw 成本优化 |
| P3 | 局部失败处理 | 2小时 | Azure 示例 |
| P4 | 状态持久化（checkpoint） | 1天 | LangGraph 特性 |

---

## 六、参考链接

1. **OpenClaw 官方 Sub-Agent 文档**：https://learnopenclaw.com/advanced/sub-agents
2. **Azure CosmosDB 多 Agent 示例**：https://github.com/AzureCosmosDB/multi-agent-langgraph
3. **LangGraph 官方仓库**：https://github.com/langchain-ai/langgraph
4. **OpenClaw GitHub Issue #8968**（maxConcurrent 未强制执行）：https://github.com/openclaw/openclaw/issues/8968
