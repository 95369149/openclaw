# 语义记忆：多 Agent 协作架构（Common Ground + Issue Driven）

## 来源
@LotusDecoder / @ii_posts（Common Ground）+ @YuLin807（Issue Driven）+ @gkxspace（5实例实战）
2026-02-18 收藏，2026-02-21 消化

## Common Ground 框架（去中心化多 Agent 协作）
- 核心问题：多 Agent 缺的不是能力，是"神经系统"（协调机制）
- 范式转换：中心化编排 → 适度约束下的自由市场式 Agent 集群
- 三层架构：
  - Partner（策略层，面向用户）→ 我们的厂长
  - Principal（执行枢纽，拆解分配）→ 我们的组长/Kitt
  - Associates（专家 Agent 独立执行）→ 我们的 Worker
- 声明式 Agent 人格：YAML 定义行为/工具/决策，换角色不改代码
- 上下文交接协议：防止信息丢失/漂移
- 持久化过程记忆：存完整决策过程（不只结果），可复用为经验

## 记忆系统对比（qmd vs NowledgeMem）
- qmd = 人类知识检索（BM25+向量+rerank），给人查字典
- NowledgeMem = AI 上下文记忆体，给 AI 长脑子
- 我们当前走 qmd 路线（本地 memory_search），三层架构已跑通暂不换
- NowledgeMem 的跨工具同步值得关注

## D-U-D 进化循环（Dan Koe）
- Dissonance（失调）→ Uncertainty（不确定）→ Discovery（发现）
- 可类比 Agent 自我迭代：检测性能不达标 → 尝试新方案 → 固化为新规则

## 费曼技巧警示
- AI 知识库搬运 = 伪学习，短期有效长期致残
- AI 助手应促进思考而非替代：提问 > 给答案，引导 > 灌输
