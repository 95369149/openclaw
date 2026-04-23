# Perplexity (GPT-5.2) Agent 调度系统审查报告

## 来源

- 平台：Perplexity Pro
- 模型：GPT-5.2 正在思考
- 时间：2026-02-22 23:40
- 引用：15 个来源（Anthropic、AWS Strands、Simon Willison 等）

---

## 1) 架构审查要点

当前链路（Triage → route → DAG(工兵+质检) → 交付）最大的优点是：路由与执行解耦、DAG 可控、质检可回路，且结构化日志为后续评测/归因打基础。

### 建议：补一层可治理工件（artifacts）

- 每个节点产出标准化 AgentResult（含输入摘要、证据引用、结构化输出、错误码、耗时、token）
- 最终汇总成 GraphResult 便于追踪整条链路
- Strands 的图执行模型强调节点/边、标准化结果与完整执行轨迹，支持 OpenTelemetry 做可观测性

### 建议：两级路由

- 粗分桶（10 类）→ 桶内细分子路由（子意图 + 风险级别 + 是否可并行）
- 对 intent_routes.json 做版本化与灰度，避免一次改动全量影响线上表现

---

## 2) 并行 subagent 设计

Anthropic 明确指出 multi-agent 对"广度优先、可并行探索"的 research 类问题更强，通过"lead 同时起 3-5 个 subagent + subagent 内并行工具调用"把复杂任务时间最多降低 90%。

### 哪些任务值得并行（建议默认并行，最后合并）

- **信息收集**：不同数据源/不同时间范围/不同语言的检索与摘要
- **方案生成**：同一问题生成多个候选解（内容/策略/舆情/销售话术），再由 judge 选优
- **约束检查**：合规/安全/业务规则/格式校验可与主执行并行跑
- **代码类**：并行做"修复方案 A/B、最小复现、风险评估、测试用例补全"

### 如何拆分

- lead 输出 SubtaskSpec[]：每个子任务包含目标、输入边界、允许工具、输出 schema、最大预算
- 以"互不依赖"为第一拆分原则；有依赖的子任务放到下一波（wave2）

### 如何合并（map-reduce + 冲突解决）

- Map：subagent 只产出结构化结果（要点、证据、置信度、已覆盖/未覆盖清单）
- Reduce：合并器先做去重与对齐，再对冲突点做"证据优先/置信度优先/再触发仲裁子任务"

### Python 伪代码

```python
import asyncio
from dataclasses import dataclass

@dataclass
class SubtaskSpec:
    name: str
    objective: str
    output_schema: dict
    budget: dict   # {"max_tokens":..., "max_tool_calls":..., "timeout_s":...}

async def run_subagent(spec: SubtaskSpec, task_ctx: dict) -> dict:
    return await subagent_runner(spec, task_ctx)

def merge_results(results: list[dict]) -> dict:
    merged = {"claims": [], "evidence": [], "missing": [], "conflicts": []}
    # 1) 去重（按 claim_id / hash）
    # 2) 冲突检测（同一字段多值）
    # 3) 生成合并后的 evidence ledger 与 missing 清单
    return merged

async def parallel_wave(subtasks: list[SubtaskSpec], task_ctx: dict) -> dict:
    coros = [run_subagent(s, task_ctx) for s in subtasks]
    results = await asyncio.gather(*coros, return_exceptions=True)
    cleaned = []
    for r in results:
        cleaned.append({"errors":[str(r)]} if isinstance(r, Exception) else r)
    return merge_results(cleaned)
```

---

## 3) 工兵 prompt 优化

### IM1（流程/制度类，6/10 → 8/10）

问题不在"写不出来"，而在：边界不清、缺少验收标准、缺少例外处理。

**ReWOO 思路拆分**：

- Plan（要做什么）→ Evidence（依据/约束）→ SOP（怎么做）→ Checks（如何验收）
- 质检 rubric 按这四块分别打分

### DEV1（代码类，3/10 → 7/10）

**Reflexion 模式**：

- 第一轮：生成代码
- 第二轮：自我审查（lint + 安全 + 依赖检查）
- 第三轮：修复问题
- 质检：运行测试 + 代码审查

### 质检升级：带诊断的定向重试

- 从"同提示词再来一次"升级为"带诊断的定向重试"
- Anthropic 用 LLM-as-judge 按 rubric 打 0-1 分并给出 pass/fail
- 单次 judge 调用更稳定、更接近人工一致性

---

## 4) ELO 评分系统

### 核心公式

```
R'_A = R_A + K * (S_A - E_A)
E_A = 1 / (1 + 10^((R_B - R_A) / 400))
```

### 维度设计

- 按 (model, bucket, role) 三维跟踪
- 例如：DeepSeek V3.2 在 M1(内容) 的工兵角色 ELO = 1350

### 冷启动策略

1. 初始分 1200
2. K=40（前 30 局），K=20（之后）
3. 基准测试集：每桶 5 个 case，共 50 个

### 衰减机制

- 超过 7 天未使用的模型 ELO 缓慢衰减（每天 -2）
- 防止"躺赢"

---

## 5) 成本优化策略

### 四步优化

1. **预算器**：Triage 除了 intent，再输出 complexity、risk、need_parallel、max_budget
2. **分层编排**：Planner 用便宜模型产出计划；Worker 用稳定模型；Solver 按风险升级
3. **并行动态阈值**：默认只开 3 个 subagent；当 missing 多或冲突多再开第二波
4. **缓存与复用**：对检索/规则解释/常见 SOP 做结果缓存

### 模型选择伪代码

```python
def choose_model(bucket, complexity, risk, elo_table):
    # 1) 先选免费模型里该桶 ELO 最高者
    candidates = ["DeepSeekV3_2_free", "GLM4_6_free", "Qwen3_32B_free"]
    best = max(candidates, key=lambda m: elo_table[m][bucket]["elo"])
    # 2) 高风险/高复杂度时允许直接上付费
    if risk >= 0.8 and complexity >= 0.7:
        return "Paid_Strong_Model"
    return best

def should_escalate(judge_score, pass_flag, risk):
    if not pass_flag: return True
    if risk >= 0.8 and judge_score < 0.85: return True
    return False
```

---

## 关键差异（vs Gemini 报告）

| 维度     | Gemini 建议               | Perplexity 建议                 |
| -------- | ------------------------- | ------------------------------- |
| 并行策略 | Coordinator + Synthesizer | lead + wave + map-reduce        |
| 质检升级 | ROLES prompt 模板         | 带诊断的定向重试 + LLM-as-judge |
| ELO 维度 | 全局评分                  | (model, bucket, role) 三维      |
| 成本优化 | 复杂度路由 + 语义缓存     | 预算器 + 分层编排 + 动态阈值    |
| 工兵优化 | ROLES 原则                | ReWOO(IM1) + Reflexion(DEV1)    |

---

**报告生成时间**: 2026-02-22 23:50
**来源**: Perplexity Pro (GPT-5.2)
