# Agent 调度系统 v3.0 规划（基于 Gemini 审查）

## 来源

- Gemini 3.0 Pro 审查报告：`外部模型审查_Gemini_Agent调度v2.md`
- 生成时间：2026-02-22 23:45

## v2.0 → v3.0 升级清单

### P0 - 立即实现

**1. ROLES 工兵 prompt 模板**

- 为每个意图桶定制专家级 prompt
- 包含：Role + Objective + Limitations + Examples + Structure
- 预期效果：IM1 从 6/10 → 8/10，DEV1 从 3/10 → 7/10

**2. 动态复杂度路由**

- Triage 同时输出 complexity (1-10)
- complexity ≤3 → Qwen3 32B（最快免费）
- complexity 4-6 → DeepSeek V3.2（最强免费）
- complexity 7-8 → GLM 4.6（高质量免费）
- complexity 9-10 → Claude Opus（付费兜底）

**3. 预测性重试**

- 质检不通过时：低成本 → 中成本 → 高成本
- 不直接跳最贵的模型
- 节省 30-50% 重试成本

### P1 - Week 2

**4. Coordinator + Synthesizer 架构**

- Coordinator Agent：任务分解（判断是否可并行）
- 并行执行：asyncio.gather
- Synthesizer Agent：结果合并
- 适用桶：S1/S2/SC1/SC2/IM2/M2/X1

**5. ELO 评分系统**

- 初始分：1200
- K 因子：新模型 32，成熟模型 16
- 按任务类型分别跟踪
- 冷启动：50 个 case 基准测试集

### P2 - 后续迭代

**6. 语义缓存**

- 计算请求 embedding
- 相似度 >0.95 直接返回缓存
- 降低重复请求成本

**7. 模型微调（长期）**

- 收集高质量 prompt-response 对
- 微调 Qwen/DeepSeek 开源模型
- 获得专属工兵模型

## 关键架构变化

### v2.0 架构

```
Triage → Route → DAG(串行) → 质检 → 交付
```

### v3.0 架构

```
Triage(+复杂度) → Coordinator(任务分解) → 并行DAG → Synthesizer(合并) → 质检(ELO) → 交付
                                              ↓
                                    [语义缓存命中则跳过]
```

## 实施优先级

| 序号 | 功能                      | 价值  | 成本 | 优先级 |
| ---- | ------------------------- | ----- | ---- | ------ |
| 1    | ROLES prompt 模板         | 9/10  | 2/10 | P0     |
| 2    | 动态复杂度路由            | 8/10  | 2/10 | P0     |
| 3    | 预测性重试                | 7/10  | 2/10 | P0     |
| 4    | Coordinator + Synthesizer | 9/10  | 6/10 | P1     |
| 5    | ELO 评分系统              | 7/10  | 4/10 | P1     |
| 6    | 语义缓存                  | 6/10  | 5/10 | P2     |
| 7    | 模型微调                  | 10/10 | 9/10 | P2     |

---

**文档版本**: v3.0 规划
**生成时间**: 2026-02-22 23:50
