# Perplexity (GPT-5.2) 第二段：Fallback 链 + 两周冲刺

## 来源

- 平台：Perplexity Pro (GPT-5.2)
- 时间：2026-02-22 23:55
- 引用：16 个来源

---

## 任务4：智能 Fallback 链实现

### 4.1 失败类型与触发条件（5 类分层处理）

| 类型             | 触发条件                    | 策略                                 |
| ---------------- | --------------------------- | ------------------------------------ |
| A. 基础设施失败  | API 5xx、连接失败、429 限流 | 同模型退避重试 1-2 次 → 同桶次优模型 |
| B. 超时/预算耗尽 | 超 timeout_s、token 超预算  | 换更快模型 + "压缩模式"              |
| C. Schema 错误   | JSON 解析失败、缺字段       | 同模型 repair pass → 换格式更强模型  |
| D. 质量失败      | judge <0.3、pass=False      | 定向重试 blame_node → 逐级升级       |
| E. 不可恢复      | 缺参数、权限禁止            | 部分结果交付 + 转人工                |

### 4.2 预测性重试：低→中→高逐级升级

关键规则：

- SchemaError：repair（同模型低 token）→ 换格式更强模型
- Timeout：reduce-effort → 换更快模型 → 再升级
- QualityFail：定向重跑 blame_node → 换同价位 ELO 更高 → 再升价位

### 4.3 ELO 动态排序函数

```python
def elo_sorted_models(models, elo_table, bucket, health):
    def rank(m):
        elo = elo_table.get(m.model_id, {}).get(bucket, {}).get("elo", 1500.0)
        rel = 1.0 - health.get(m.model_id, {}).get("error_rate", 0.0)
        spd = m.speed
        cst = m.base_cost
        return (0.55 * (elo / 2000.0)) + (0.25 * rel) + (0.15 * spd) - (0.25 * cst)
    return sorted(models, key=rank, reverse=True)
```

权重：ELO 55% + 可靠性 25% + 速度 15% - 成本 25%

### 4.4 降级策略（全失败时）

- Planner 成功但 Worker 失败 → 交付 plan + 缺失原因 + 可执行清单
- Worker 有部分 evidence → 交付 evidence ledger + 置信度 + 未覆盖点
- 仅 schema 错误 → 交付自然语言摘要 + 可修复 JSON 片段
- 写入/变更类任务 → 安全降级（只读模式）+ 转人工

### 4.5 完整 smart_fallback 伪代码

```python
from dataclasses import dataclass
from enum import Enum

class FailType(str, Enum):
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SCHEMA_ERROR = "schema_error"
    QUALITY_FAIL = "quality_fail"
    MISSING_INFO = "missing_info"
    TOOL_UNAVAILABLE = "tool_unavailable"
    UNKNOWN = "unknown"

@dataclass
class AttemptResult:
    ok: bool
    output: dict | None
    fail_type: FailType | None
    error: str | None
    judge_score: float | None
    judge_pass: bool | None
    artifacts: dict  # {"plan":..., "evidence":..., "draft":..., "trace_id":...}
    usage: dict      # {"tokens":..., "latency_ms":..., "cost":...}
    blame_node: str | None

@dataclass
class ModelProfile:
    model_id: str
    tier: str        # "free"/"mid"/"premium"
    base_cost: float
    speed: float
    provider: str

@dataclass
class FallbackPolicy:
    max_attempts: int = 5
    infra_retries: int = 2
    backoff_base_s: float = 0.4
    qc_threshold: float = 0.3
    escalate_qc_threshold: float = 0.6

def smart_fallback(task_ctx, bucket, risk, model_pool, elo_table, health, policy):
    sorted_pool = elo_sorted_models(model_pool, elo_table, bucket, health)
    used = set()
    tier_cap = "free"
    effort_mode = "normal"
    last_good_artifacts = {"plan": None, "evidence": None}
    infra_retry_left = policy.infra_retries

    for attempt in range(policy.max_attempts):
        model = pick_next_model(sorted_pool, used, tier_cap)
        if model is None:
            break
        used.add(model.model_id)

        res = run_one_attempt(model, task_ctx, effort_mode, ...)

        # 保留部分工件
        if res.artifacts.get("plan"):
            last_good_artifacts["plan"] = res.artifacts["plan"]
        if res.artifacts.get("evidence"):
            last_good_artifacts["evidence"] = res.artifacts["evidence"]

        if res.ok:
            return res

        ft = res.fail_type or FailType.UNKNOWN

        # 1) Schema 错误：repair pass
        if ft == FailType.SCHEMA_ERROR:
            continue

        # 2) 基础设施失败：同层重试
        if ft in {FailType.API_ERROR, FailType.RATE_LIMIT} and infra_retry_left > 0:
            infra_retry_left -= 1
            continue

        # 3) 超时：降 effort 再升级
        if ft == FailType.TIMEOUT:
            effort_mode = "reduced"
            if tier_cap != "premium":
                tier_cap = next_tier(tier_cap)
            continue

        # 4) 质量失败：定向重试 → 升级
        if ft == FailType.QUALITY_FAIL:
            if tier_cap != "premium":
                tier_cap = next_tier(tier_cap)
            continue

        # 5) 不可恢复：停止
        if ft in {FailType.MISSING_INFO, FailType.TOOL_UNAVAILABLE}:
            break

    # 降级交付
    return AttemptResult(
        ok=False,
        output={
            "status": "degraded",
            "message": "已返回可用的阶段性结果与下一步建议",
            "plan": last_good_artifacts["plan"],
            "evidence": last_good_artifacts["evidence"],
        },
        fail_type=FailType.UNKNOWN,
        error="all attempts failed",
        ...
    )
```

---

## 任务5：两周冲刺计划

### Week 1：MVP（必须先做）

目标：智能 fallback + 失败分类 + 工件复用 + 最小 ELO 采集

| Day  | 任务                                                                      | 依赖   |
| ---- | ------------------------------------------------------------------------- | ------ |
| Day1 | 定义数据契约（AttemptResult、FailType、artifacts schema、trace_id）       | 无     |
| Day2 | 实现 schema_validate() + classify_failure() + repair pass                 | Day1   |
| Day3 | 实现 smart_fallback() 骨架（逐级升级 + infra 重试 + timeout 降 effort）   | Day2   |
| Day4 | 质检统一为 judge（score 0-1 + pass/fail + blame_node + fix_instructions） | Day1   |
| Day5 | 最小评测闭环：20 条样本，v2.0 vs v3.0-MVP 对比                            | Day3+4 |
| Day6 | 灰度发布（1-5% 流量）+ 告警                                               | Day5   |
| Day7 | 修复灰度问题 + 固化阈值 + 文档                                            | Day6   |

### Week 2：生产就绪

目标：ELO 数据驱动 + 并行 subagent + 缓存 + 可观测性

| Day   | 任务                                                   | 依赖  |
| ----- | ------------------------------------------------------ | ----- |
| Day8  | ELO 计算 job + judge 分数映射                          | Week1 |
| Day9  | ELO 接入 elo_sorted_models() + 冷启动 + K-factor 衰减  | Day8  |
| Day10 | 2 个高价值桶引入并行 subagent（3-5 个）                | Day9  |
| Day11 | 缓存：工具结果幂等缓存 + 检索缓存 + artifacts 引用复用 | Day10 |
| Day12 | 可观测性：trace 串联 + 超时/错误率报警                 | Day11 |
| Day13 | 压测与故障演练（注入 429、工具挂掉、慢查询）           | Day12 |
| Day14 | 全量发布准备 + SLO 签字 + 回滚策略                     | Day13 |

### 风险点与缓解

| 风险                     | 缓解                                                  |
| ------------------------ | ----------------------------------------------------- |
| judge 误判导致无谓升级   | judge 输出含 reasons + blame_node，高风险桶加人工抽检 |
| 并行 subagent token 失控 | 限定桶 + 限 subagent 数 + 工具调用上限                |
| 超时/工具不稳定级联失败  | 工具层统一超时/熔断/隔离                              |
| 部署中断运行中长任务     | 版本化 DAG + 灰度切流 + 可回滚                        |

---

## 引用来源（16 个）

1. Anthropic: How we built our multi-agent research system
2. Simon Willison: Anthropic multi-agent research system
3. arXiv: Why Do Multi-Agent LLM Systems Fail?
4. ByteByteGo: How Anthropic Built a Multi-Agent Research System
5. ZenML: Building a Multi-Agent Research System
6. YouTube: Building Multi-Agent AI Research Systems at Anthropic
7. AWS: Strands Agents SDK technical deep dive
8. AWS: Customize agent workflows with Strands Agents
9. YouTube: Anthropic How to Build Multi Agent Systems
10. AWS: Strands Agents SDK architectures and observability
11. REWOO Agent Pattern documentation
12. 译文: Anthropic 多 Agent Research 系统
13. YouTube: Tracing AWS Strands AI Agents with OpenTelemetry
14. Strands: Multi-agent Patterns
15. SoftwareSeni: Orchestration Patterns for Multi-Agent Systems
16. AWS: Advanced orchestration with Strands Agents

---

**文档版本**: Perplexity 第二段
**生成时间**: 2026-02-22 23:55
