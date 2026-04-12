# Perplexity (GPT-5.2) 第三段：v3.0 配置与目录结构

## 来源

- 平台：Perplexity Pro (GPT-5.2)
- 时间：2026-02-23 00:00

---

## 1) intent_routes.json v3.0 Schema

### 核心变化

- 顶层桶 + 二级子路由
- Triage 产出：bucket_id + sub_intent + op_type + risk/complexity
- 路由配置决定：DAG 模板、是否并行、是否 human_gate、工具白名单

### SC1 示例配置

```json
{
  "version": "3.0",
  "default": {
    "dag_template": "react_basic",
    "risk": 0.3,
    "complexity": 0.3,
    "need_parallel": false,
    "human_gate": { "enabled": false }
  },
  "buckets": [
    {
      "bucket_id": "SC1",
      "name": "供应链风险监控",
      "risk": 0.9,
      "complexity": 0.7,
      "need_parallel": true,
      "dag_template": "rewoo_guided_react_human_gate",
      "human_gate": {
        "enabled": true,
        "approver_role": "厂长",
        "gate_on_ops": ["mutation", "decision"],
        "tool_allowlist_pre_gate": ["read_only_tools", "search", "retrieval"],
        "tool_allowlist_post_gate": ["write_tools_scoped"]
      },
      "secondary_router": {
        "mode": "rules_first",
        "features": ["sub_intent", "op_type", "data_freshness", "confidence"],
        "routes": [
          {
            "subroute_id": "SC1.monitor",
            "when": { "sub_intent": "monitor", "op_type": "read" },
            "dag_template": "rewoo_strict",
            "need_parallel": true
          },
          {
            "subroute_id": "SC1.recommend",
            "when": { "sub_intent": "recommendation", "op_type": "decision" },
            "dag_template": "reflexion_bounded",
            "qc": { "min_score": 0.85 }
          }
        ]
      }
    },
    {
      "bucket_id": "SC2",
      "name": "供应商评估/替代",
      "risk": 0.95,
      "complexity": 0.85,
      "need_parallel": true,
      "dag_template": "rewoo_guided_react_human_gate",
      "human_gate": {
        "enabled": true,
        "approver_role": "厂长",
        "gate_on_ops": ["mutation", "decision"]
      },
      "secondary_router": {
        "routes": [
          {
            "subroute_id": "SC2.evaluate",
            "when": { "sub_intent": "evaluation", "op_type": "decision" },
            "dag_template": "hybrid_rewoo_reflexion",
            "qc": { "min_score": 0.9 }
          },
          {
            "subroute_id": "SC2.execute_switch",
            "when": { "sub_intent": "execute", "op_type": "mutation" },
            "dag_template": "rewoo_guided_react_human_gate",
            "qc": { "min_score": 0.95 }
          }
        ]
      }
    }
  ]
}
```

---

## 2) 每桶 DAG 模板选择

| 模板        | 适用场景               | 桶                                |
| ----------- | ---------------------- | --------------------------------- |
| ReWOO       | 高风险/强治理/工具链长 | SC1, SC2, IM1                     |
| Reflexion   | 多约束权衡/方案比较    | X1(舆情), S2(商机), M2(内容严)    |
| Hybrid      | 高风险+参数绑定复杂    | SC1/SC2 的评估→变更               |
| ReAct-basic | 低风险/简单问答        | M1(内容快), DEV1(代码), IM2(分析) |

### 10 桶完整映射

| 桶             | 模板                          | 风险 | 并行 | human_gate |
| -------------- | ----------------------------- | ---- | ---- | ---------- |
| S1 线索审查    | rewoo_strict                  | 0.5  | ✅   | ❌         |
| S2 商机话术    | reflexion_bounded             | 0.4  | ❌   | ❌         |
| SC1 风险监控   | rewoo_guided_react_human_gate | 0.9  | ✅   | ✅         |
| SC2 供应商评估 | hybrid_rewoo_reflexion        | 0.95 | ✅   | ✅         |
| IM1 制度流程   | rewoo_strict                  | 0.3  | ❌   | ❌         |
| IM2 经营分析   | react_basic                   | 0.3  | ✅   | ❌         |
| M1 内容快      | react_basic                   | 0.1  | ❌   | ❌         |
| M2 内容严      | reflexion_bounded             | 0.5  | ❌   | ✅         |
| X1 舆情        | reflexion_bounded             | 0.4  | ✅   | ❌         |
| DEV1 代码      | react_basic + reflexion       | 0.3  | ❌   | ❌         |

---

## 3) ELO 维度设计

### 存储结构（model × bucket × role）

```json
// data/elo/ratings/deepseek-v3.2.json
{
  "model_id": "deepseek-v3.2",
  "updated_at": "2026-02-22T23:50:00Z",
  "ratings": {
    "M1": { "worker": { "elo": 1350, "games": 42, "k": 20 } },
    "DEV1": { "worker": { "elo": 1180, "games": 15, "k": 32 } },
    "SC1": { "worker": { "elo": 1220, "games": 8, "k": 40 } }
  }
}
```

### 事件日志

```jsonl
// data/elo/events/2026-02-22.jsonl
{"ts":"...","bucket":"M1","role":"worker","model_a":"deepseek-v3.2","model_b":"baseline","score_a":1,"judge_score":0.85}
```

### K-factor 策略

- games < 30 → K=40（快速定级）
- games 30-100 → K=20（稳定期）
- games > 100 → K=12（成熟期）
- 7 天未使用 → ELO 每天 -2（防躺赢）

---

## 4) 完整目录结构

```
agent_system/
  configs/
    intent_routes.v3.json          # 路由配置（强校验）
    models.yaml                    # 模型池（tier/cost/speed/provider）
    fallback_policies.yaml         # 按桶的 fallback 策略
    human_gate/
      policies.yaml                # SC1/SC2 审批规则
    dags/
      templates.yaml               # DAG 模板定义
      buckets/
        sc1.py                     # SC1 专属 DAG
        sc2.py
        m1.py
        dev1.py
        ...

  engine/
    triage.py                      # Triage + 复杂度评估
    router.py                      # 一级路由 + 二级子路由
    fallback.py                    # 智能 fallback
    budgeter.py                    # complexity/risk → 预算/并行度
    qc/
      judge.py                     # LLM-as-judge
      validators.py                # schema 校验、rubric 校验
    gate/
      human_gate.py                # 厂长审批节点
    tools/
      registry.py                  # 工具注册、分级
      policies.py                  # 工具白名单/黑名单
    cache/
      cache_store.py               # Redis/本地/Hybrid
      keys.py

  data/
    elo/
      events/                      # 对局事件日志
      ratings/                     # 模型评分
    cache/
      tool_results/                # 工具结果缓存
    artifacts/
      plans/                       # Planner 产物
      evidence_ledgers/            # 证据台账
      drafts/                      # Worker 草稿
      finals/                      # 最终交付
    eval/
      datasets/                    # 基准测试集
      reports/                     # 评测报告

  logs/
    app/
    traces/                        # trace 导出（JSONL/OTLP）
    qc/
    errors/

  scripts/
    offline_eval.py                # v2 vs v3 对比
    elo_update_job.py              # ELO 聚合更新
    backfill_routes.py             # 迁移/生成子路由

  tests/
    test_router.py
    test_qc_schema.py
    test_fallback_policy.py
    test_sc1_gate.py
```

### 落地要点

1. `configs/intent_routes.v3.json` 做强校验（启动时 + CI）
2. `data/artifacts/` 是降级交付的根：planner/worker 产物必须持久化
3. `configs/human_gate/policies.yaml` 让 SC1/SC2 的 gate 变成可审计配置

---

**Perplexity 还提出**：如果提供另外 8 个桶的典型请求（各 3 条），可以补全完整的 intent_routes.v3.json

**文档版本**: Perplexity 第三段
**生成时间**: 2026-02-23 00:05
