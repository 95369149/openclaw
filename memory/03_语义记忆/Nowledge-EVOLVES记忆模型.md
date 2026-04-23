# 语义记忆：Nowledge EVOLVES 记忆模型

## 来源
Wey Gu / Nowledge Mem v0.6（2026-02-20 收藏消化）

## 核心架构：三层记忆
1. **Trace** — 原始记录（对话全量备份）→ 我们的 sessions/*.jsonl
2. **Unit** — 提炼后的原子知识点 → 我们的 03_semantic-memory/*.md
3. **Crystal** — 碎片积累够多后自动合成综合文档 → 我们还没做，可以借鉴

## EVOLVES 模型（核心亮点）
新旧记忆之间的四种关系：
- **Replaces（替代）**：新观点修正旧观点 → 标记 `[覆盖: 旧文件]`
- **Enriches（充实）**：补充更多细节 → 标记 `[追加到: 旧文件]`
- **Confirms（确认）**：再次验证 → 标记 `[验证: 旧文件]`
- **Challenges（反驳）**：相反证据 → 标记 `[质疑: 旧文件]`

## Working Memory 机制
- 每天自动生成当日工作记忆（最近关注点 + 未解决问题）
- Agent 启动时先读，立刻知道主人在忙啥
- 我们的 active-context.md 类似，但可以更自动化

## Smart Distill
- 不无脑存所有对话，逐轮评估只保留有价值内容
- 我们的 inbox → 消化 → 语义记忆 管线类似

## 技术选型参考
- 向量搜索：LanceDB
- 混合搜索：语义 + BM25 + RRF 排序融合
- Embedding：1024 维（Qwen3-Embedding / BGE-M3）

## 对我们系统的行动项
1. 在语义记忆更新时标注 EVOLVES 关系（替代/充实/确认/反驳）
2. 考虑引入 Crystal 机制：当某主题碎片超过 5 篇时自动合成综述
3. active-context.md 可以做成每日自动生成（cron job）
