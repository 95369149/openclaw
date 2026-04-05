# Agent 调度系统 v2.0 优化方案

## 基于外部最佳实践（AWS + Anthropic + LangChain）

### 参考资料
- AWS: Multi-Agent collaboration patterns with Strands Agents
- Anthropic: How we built our multi-agent research system
- LangChain: Multi-agent patterns (Router + Subagents)

---

## 任务 1: 代码审查与优化建议

### 架构问题

**问题 1: 串行执行瓶颈**
- 当前 DAG 顺序执行，侦察任务无法并行
- 例如 S1 线索审查：需要同时查企查查、天眼查、工商信息
- 解决：实现并行 subagent（asyncio.gather）

**问题 2: 编排者单点故障**
- Triage 失败整个流程挂掉
- 解决：Triage 加 fallback（GLM 4.5 Air → Qwen3 32B → DS-SF）

**问题 3: 无失败恢复**
- 模型 API 错误直接返回 "[模型调用失败]"
- 解决：实现 fallback 链 + 重试（最多 3 次）

**问题 4: 上下文传递脆弱**
- 依赖字典 key 匹配（'工兵' vs '侦察'）
- 解决：用结构化 context 对象，带类型检查

### 性能瓶颈

**瓶颈 1: 串行等待**
- 每个 Agent 执行完才启动下一个
- 优化：侦察任务并行执行（3 个 subagent 同时跑）

**瓶颈 2: 固定 sleep(0.3)**
- 不管任务快慢都等 0.3 秒
- 优化：异步执行，按实际完成时间汇总

**瓶颈 3: 重复 JSON 解析**
- 每次都 split('```') 清理 markdown
- 优化：统一 JSON 解析函数，带容错

### 可靠性风险

**风险 1: API Key 硬编码**
- 泄露风险 + 无法切换账户
- 解决：从环境变量或配置文件读取

**风险 2: 无超时控制**
- 模型卡住会永久等待
- 解决：curl 加 --max-time 30

**风险 3: 质检解析失败默认通过**
- 可能放过低质量输出
- 解决：解析失败时调用备用质检模型

### 最佳实践（我们漏了什么）

**漏项 1: 结构化日志**
- 当前只有 print，无法追溯
- 补充：记录到 `memory/05_日常日志/agent_execution.jsonl`

**漏项 2: ELO 评分系统**
- 无法知道哪个模型表现好
- 补充：每次质检后更新 ELO 到 `模型绩效.md`

**漏项 3: Human gate**
- SC1/SC2/M2 需要人工审批
- 补充：发送 Telegram 消息，等待厂长回复

**漏项 4: 成本跟踪**
- 不知道每次调用花了多少钱
- 补充：记录 token 使用量，计算成本

---

## 任务 2: v2.0 功能优先级排序

按「价值/成本比」排序（P0 最高）：

### P0 - 立即实现（Week 1）

**1. Fallback 链（价值 9/10，成本 2/10）**
- 理由：防止单点故障，提升可靠性 90%
- 工作量：4 小时
- 依赖：无

**2. 质检重试（价值 8/10，成本 1/10）**
- 理由：<6 分打回重做，质量提升 30%
- 工作量：2 小时
- 依赖：Fallback 链

**3. 结构化日志（价值 7/10，成本 1/10）**
- 理由：可追溯、可调试、可分析
- 工作量：2 小时
- 依赖：无

### P1 - 第二周实现（Week 2）

**4. 并行 subagent（价值 8/10，成本 5/10）**
- 理由：侦察任务提速 3 倍，但实现复杂
- 工作量：8 小时
- 依赖：Fallback 链

**5. ELO 跟踪（价值 6/10，成本 2/10）**
- 理由：优化模型选择，长期降低成本
- 工作量：3 小时
- 依赖：结构化日志

**6. Human gate（价值 7/10，成本 3/10）**
- 理由：SC1/SC2/M2 必须人工审批
- 工作量：4 小时
- 依赖：Telegram 集成

### P2 - 后续迭代

**7. 侦察集成（价值 9/10，成本 7/10）**
- 理由：Perplexity/Grok 提升搜索质量，但需要 API key + 调试
- 工作量：12 小时
- 依赖：并行 subagent

**8. Excel 集成（价值 10/10，成本 8/10）**
- 理由：DataOps 读写 WPS，业务核心，但实现复杂
- 工作量：16 小时
- 依赖：无（独立模块）

---

## 任务 3: 并行 subagent 设计

### 触发条件

需要并行的意图桶：
- **S1 线索审查**：同时查企查查、天眼查、工商信息
- **S2 商机研究**：同时查公司背景、竞品对比、行业报告
- **SC1 风险监控**：同时查新闻、社交媒体、供应商公告
- **X1 抓取舆情**：同时查 X、微博、小红书

判断标准：DAG 中有多个「侦察」任务，且任务间无依赖

### 并行策略

**拆分方式**：按数据源拆分
```python
# S1 线索审查示例
subagents = [
    {"name": "侦察-企查查", "task": "查企查查获取公司资质"},
    {"name": "侦察-天眼查", "task": "查天眼查获取风险信息"},
    {"name": "侦察-工商", "task": "查工商局获取注册信息"},
]
```

**并行执行**：用 asyncio.gather
```python
import asyncio

async def run_subagent(subagent, user_input):
    # 调用模型
    result = await call_model_async(subagent['model'], prompt)
    return {"name": subagent['name'], "result": result}

# 并行执行
results = await asyncio.gather(*[
    run_subagent(sa, user_input) for sa in subagents
])
```

### 汇总逻辑

Lead agent（Kitt）合并 subagent 结果：
```python
def merge_subagent_results(results, route):
    """合并 subagent 结果"""
    # 1. 去重（相同信息只保留一份）
    # 2. 排序（按可信度/时效性）
    # 3. 压缩（提取关键信息，丢弃冗余）
    
    merged = {
        "sources": [r['name'] for r in results],
        "key_findings": extract_key_findings(results),
        "evidence": [r['result'][:200] for r in results],  # 截断
    }
    
    # 调用工兵，基于合并结果生成最终输出
    return merged
```

### 失败处理

**策略 1: 部分失败继续**
- 3 个 subagent，1 个失败，2 个成功 → 继续
- 阈值：至少 50% subagent 成功

**策略 2: 失败 subagent 重试**
- 失败的 subagent 用 fallback 模型重试 1 次
- 仍失败 → 标记为 "[数据源不可用]"

**策略 3: 全部失败降级**
- 所有 subagent 都失败 → 用单个强模型（Opus）兜底

### 伪代码

```python
async def execute_parallel_subagents(subagents, user_input, route):
    """并行执行 subagent"""
    
    async def run_one(subagent):
        model = route['dispatch'][subagent['role']]['model']
        fallbacks = route['dispatch'][subagent['role']]['fallback']
        
        # 尝试主模型
        try:
            result = await call_model_async(model, subagent['prompt'])
            return {"name": subagent['name'], "result": result, "status": "ok"}
        except Exception as e:
            # 尝试 fallback
            for fb_model in fallbacks:
                try:
                    result = await call_model_async(fb_model, subagent['prompt'])
                    return {"name": subagent['name'], "result": result, "status": "fallback"}
                except:
                    continue
            # 全部失败
            return {"name": subagent['name'], "result": None, "status": "failed"}
    
    # 并行执行
    results = await asyncio.gather(*[run_one(sa) for sa in subagents])
    
    # 检查成功率
    success_count = sum(1 for r in results if r['status'] != 'failed')
    if success_count < len(subagents) * 0.5:
        # 成功率 <50%，降级到单模型
        return await fallback_to_single_model(user_input, route)
    
    # 合并结果
    return merge_subagent_results(results, route)
```

---

## 任务 4: Fallback 链实现方案

### 触发条件

什么算「失败」？
1. **API 错误**：HTTP 5xx、超时、网络错误
2. **输出格式错误**：JSON 解析失败、缺少必需字段
3. **质检低分**：质检评分 <3 分（严重问题）

### Fallback 顺序

从 `intent_routes.json` 的 dispatch 配置读取：
```json
{
  "dispatch": {
    "工兵": {
      "model": "ds-sf",
      "fallback": ["qwen-32b-groq", "qwen-32b", "flash"]
    }
  }
}
```

执行顺序：ds-sf → qwen-32b-groq → qwen-32b → flash

### 重试次数

- **主模型**：1 次（不重试，直接 fallback）
- **Fallback 模型**：每个 1 次
- **最大尝试**：1 + len(fallbacks) = 4 次

### 降级策略

所有 fallback 都失败怎么办？
1. **记录日志**：写入 `agent_execution.jsonl`
2. **通知厂长**：发 Telegram 消息
3. **返回部分结果**：如果有上游输出，返回上游结果 + 错误提示
4. **人工介入**：等待厂长指令

### 伪代码

```python
def call_model_with_fallback(model_alias, prompt, route, role):
    """带 fallback 的模型调用"""
    
    # 主模型
    models_to_try = [model_alias]
    
    # 添加 fallback
    if role in route['dispatch']:
        fallbacks = route['dispatch'][role].get('fallback', [])
        models_to_try.extend(fallbacks)
    
    last_error = None
    
    for i, model in enumerate(models_to_try):
        try:
            result = call_model(model, prompt, max_tokens=500, timeout=30)
            
            # 验证输出格式
            if not validate_output(result, role):
                raise ValueError(f"输出格式错误: {result[:100]}")
            
            # 成功，记录使用的模型
            log_model_usage(model, role, success=True, fallback_index=i)
            return result
            
        except Exception as e:
            last_error = e
            log_model_usage(model, role, success=False, error=str(e))
            
            # 如果不是最后一个，继续尝试
            if i < len(models_to_try) - 1:
                print(f"  ⚠️ {model} 失败，尝试 fallback: {models_to_try[i+1]}")
                continue
    
    # 所有模型都失败
    notify_failure(role, models_to_try, last_error)
    raise Exception(f"所有模型失败: {last_error}")

def validate_output(result, role):
    """验证输出格式"""
    if role == '质检':
        # 质检必须返回 JSON
        try:
            data = json.loads(result)
            return 'score' in data and 'passed' in data
        except:
            return False
    # 其他角色暂时不验证
    return True

def notify_failure(role, models, error):
    """通知厂长失败"""
    message = f"""
⚠️ Agent 执行失败

角色: {role}
尝试模型: {', '.join(models)}
错误: {error}

请检查配置或手动处理。
"""
    # 发送 Telegram 消息（待实现）
    # send_telegram(message)
    
    # 记录日志
    log_to_file({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "models_tried": models,
        "error": str(error),
        "status": "all_failed"
    })
```

---

## 任务 5: 两周冲刺计划

### Week 1: 最小可用版本（MVP）

**目标**：v2.0 核心功能，可靠性提升 90%

#### Day 1-2: Fallback 链 + 结构化日志
- [ ] 实现 `call_model_with_fallback()`
- [ ] 添加超时控制（30s）
- [ ] 实现 `log_to_file()` 写入 JSONL
- [ ] 测试 3 个意图桶（M1/IM1/S1）

#### Day 3: 质检重试
- [ ] 质检 <6 分打回工兵重做
- [ ] 最多重试 2 次
- [ ] 记录重试次数到日志

#### Day 4-5: 集成测试 + 修 bug
- [ ] 跑完 10 个意图桶测试
- [ ] 修复发现的问题
- [ ] 更新文档

**Week 1 交付物**
- agent_dispatcher_v2.py（带 fallback + 重试）
- agent_execution.jsonl（结构化日志）
- 测试报告（10 个桶全部通过）

---

### Week 2: 生产就绪（Production-ready）

**目标**：并行执行 + Human gate + ELO 跟踪

#### Day 6-7: 并行 subagent
- [ ] 实现 `execute_parallel_subagents()`
- [ ] 用 asyncio.gather 并行执行
- [ ] 实现 `merge_subagent_results()`
- [ ] 测试 S1/S2/SC1/X1 四个桶

#### Day 8: ELO 跟踪
- [ ] 质检后更新 ELO 到 `模型绩效.md`
- [ ] 实现 ELO 计算公式
- [ ] 可视化 ELO 趋势（可选）

#### Day 9: Human gate
- [ ] SC1/SC2/M2 发送 Telegram 审批请求
- [ ] 等待厂长回复（approve/reject）
- [ ] 超时处理（24h 无回复自动拒绝）

#### Day 10: 集成测试 + 文档
- [ ] 完整流程测试（包括 human gate）
- [ ] 性能测试（并行 vs 串行对比）
- [ ] 更新所有文档
- [ ] 部署到生产环境

**Week 2 交付物**
- agent_dispatcher_v2.1.py（完整版）
- 模型绩效.md（ELO 跟踪）
- Human gate 审批流程文档
- 性能测试报告

---

### 依赖关系图

```
Day 1-2: Fallback 链 + 日志
    ↓
Day 3: 质检重试（依赖 Fallback）
    ↓
Day 4-5: 集成测试
    ↓
Day 6-7: 并行 subagent（依赖 Fallback）
    ↓
Day 8: ELO 跟踪（依赖日志）
    ↓
Day 9: Human gate（独立）
    ↓
Day 10: 最终集成测试
```

---

## 总结

### 优先级排序（最终）
1. **P0**: Fallback 链、质检重试、结构化日志（Week 1）
2. **P1**: 并行 subagent、ELO 跟踪、Human gate（Week 2）
3. **P2**: 侦察集成、Excel 集成（后续迭代）

### 预期收益
- **可靠性**：从 80% → 99%（fallback + 重试）
- **速度**：侦察任务提速 3 倍（并行执行）
- **质量**：质检重试 + ELO 优化，输出质量提升 30%
- **成本**：ELO 跟踪后，长期降低 20% 成本

### 风险
- **并行复杂度**：asyncio 调试困难，预留 buffer 时间
- **Human gate 延迟**：厂长不在线时任务阻塞，需要超时机制
- **ELO 冷启动**：初期数据少，评分不准，需要至少 30 次执行

---

**文档版本**: v2.0
**生成时间**: 2026-02-22 23:15
**参考**: AWS + Anthropic + LangChain 最佳实践
