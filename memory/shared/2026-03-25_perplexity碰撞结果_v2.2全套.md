# Perplexity 碰撞结果汇总（2026-03-25）

> 来源：厂长将 v2.1 方案送 Perplexity 做 Reality Checker 审核
> 评分：**8.5 / 10**
> 结论：继承做得扎实，但落地前还差"守门/终审决策树"和"可执行路由/熔断规则"

---

## 一、审核意见摘要

### 🔴 blocker（3 条）

1. **guard 与 kitt 的高风险决策边界模糊**
   - "哪些风险 guard 可以自行放行，哪些必须升级 kitt/人类"没有决策表
   - 会导致责任真空

2. **缺"可执行路由矩阵"**
   - 文字版路由有了，但没有 task_type × risk_level × size 的机器可读矩阵
   - 直接回写 openclaw.json 会导致路由不一致

3. **规则停留在"人话版约束"，缺与 openclaw.json 的字段映射**
   - 需要 risk_level、needs_scout、needs_guard、needs_kitt、chain_profile 等字段定义

### 🟡 suggestion（7 条）

1. Agent persona 与模型池应拆开，避免"按 agent 定死模型"
2. 先侦察后执行需要"豁免规则"和"默认短链"
3. scout 不应成为所有任务的强制前缀
4. guard 高影响改动应再经 kitt 语义裁决
5. 失败处理改为"失败结果 SLA"而非"当轮立刻处理"
6. kitt 增加"抽查低风险 + 全审高风险"量化规则
7. 缺负载/配额/降级策略

### ✅ 保留确认

- 四员骨架完整保留 ✅
- Reality Checker 分层反馈 ✅
- Project Shepherd 闭环 ✅
- 先侦察后执行 ✅
- manifest 统一落地 ✅
- 特质路由 ✅
- sino/scout/guard 三个新岗解决真实问题 ✅

---

## 二、v2.2 升级要点（相对 v2.1 的增量）

1. **任务元数据标准化**：taskType / riskLevel / size / needs_scout / needs_guard / needs_kitt / chain_profile
2. **路由矩阵**：FAST vs FULL 两类链路，按 task_type × risk × size 映射
3. **守门决策表**：CFG_LOW / CFG_MEDIUM / CFG_HIGH → guard/kitt/human 签收矩阵
4. **错误分类与熔断**：RETRIABLE / NON_RETRIABLE / RISK_ESCALATION + 有界重试 + 熔断
5. **负载降级策略**：kitt/scout/guard 超载时的分级处理
6. **监控与版本化**：结构化日志 + 配置版本 + 回滚指针
7. **Post-mortem 流程**：jimmy 建任务 → scout 收证据 → kitt 根因 → guard 审配置 → 写回规则

---

## 三、产出清单

| 产出                             | 说明                                                                                            |
| -------------------------------- | ----------------------------------------------------------------------------------------------- |
| v2.2 英文标准                    | 15 章完整规范                                                                                   |
| v2.2 中文正式稿                  | 可直接回写 memory 的权威版                                                                      |
| openclaw.json 增量配置           | 6 大新增 key：taskClassification/routing/guardRules/realityChecker/fallbackPolicy/loggingPolicy |
| jimmy system prompt v2.2         | 含 task_meta 打标 + 路由选择 + 派单 + 收口全流程                                                |
| jimmy 内部工具调用约定           | manifest 格式、错误分类、日志友好格式                                                           |
| kitt Reality Checker prompt v2.2 | 6 轴审核 + 3 层输出 + 风险深度分级                                                              |
| kitt 输出模板 ×3                 | 代码改造、配置变更、对外长文 三种典型 case                                                      |

---

## 四、落地建议（Perplexity 原文）

1. 先在 memory 写入 v2.2 标准全文作为强制规则
2. 基于标准增补 openclaw.json 的任务元数据、路由模板、fallback/熔断规则
3. 通过 1-2 个真实项目灰度试运行
4. 用 post-mortem 机制继续微调
