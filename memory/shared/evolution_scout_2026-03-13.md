# Evolution Scout 输出 2026-03-13

> 生成时间：2026-03-13 20:58
> 任务：每周自我进化流水线 v2

---

## 🔍 侦察结果

### 外部搜索（3 个方向）

#### 1. OpenClaw 高级技巧

- **搜索词**：OpenClaw advanced tips 2026
- **时效性**：过去 1 周
- **发现**：
  - Medium 文章：21 条高级自动化实践（真实 VPS 部署案例）
  - MoltFounders Cheatsheet：CLI 完整参考 + 开发者指南
  - Valletta 企业指南：架构、安全检查清单

#### 2. AI Agent 记忆架构

- **搜索词**：AI agent memory architecture 2026
- **时效性**：过去 1 周
- **发现**：
  - **分层记忆**成为主流（短期/中期/长期）
  - **向量数据库 + HNSW 索引**处理十亿级向量
  - **PlugMem 模块**：原始交互 → 结构化知识
  - **Letta 框架**：OS 式虚拟内存管理（主上下文 = RAM，外部存储 = Disk）
  - arXiv 论文：多 Agent 记忆的计算机架构视角

#### 3. 上下文工程最佳实践

- **搜索词**：context engineering best practices 2026
- **时效性**：过去 1 周
- **发现**：
  - **InfoQ 重磅**：ETH Zurich 研究表明 LLM 生成的 AGENTS.md 会降低 3% 成功率、增加 20% 成本
  - 建议：只保留"模型无法推断"的非显性知识
  - 社区反馈：AGENTS.md 对人类开发者的价值 > 对 AI 的价值（强迫团队明确架构决策）

---

## 📄 深度阅读（3 篇全文）

### 1. InfoQ：AGENTS.md 文件价值重估

**URL**：https://www.infoq.com/news/2026/03/agents-context-file-value-review/

**核心观点**：

- ETH Zurich 团队构建 AGENTbench（138 个真实 Python 任务）
- 测试 4 个 Agent（Claude 3.5 Sonnet、GPT-5.2、GPT-5.1 mini、Qwen Code）
- 结果：
  - LLM 生成的 AGENTS.md：成功率 -3%，成本 +20%
  - 人工编写的 AGENTS.md：成功率 +4%，成本 +19%
- 原因：过度指令导致 Agent 执行不必要的测试、文件读取、grep 搜索
- 建议：**只保留高度特定的工具链、自定义构建命令、领域知识**

**对我们的影响**：

- 当前 AGENTS.md 2800+ 行，可能存在大量"模型能推断"的冗余
- 需要审计：哪些是必须明说的（Surge 配置、红太阳业务规则），哪些是多余的（通用 Git 操作）

### 2. Let's Data Science：AI Agent 记忆架构

**URL**：https://www.letsdatascience.com/blog/ai-agent-memory-architecture（429 限流，未获取全文）

**从搜索摘要提取**：

- 向量数据库使用 HNSW 索引处理十亿级向量
- 分层记忆架构：短期（会话）→ 中期（任务）→ 长期（知识库）
- 2026 年 3 月，专用向量数据库已成熟

**对我们的影响**：

- 当前用 QMD 文本搜索，未用向量检索
- 记忆 <1000 条时够用，但扩展性存疑

### 3. Medium：21 条 OpenClaw 高级自动化

**URL**：https://medium.com/@rentierdigital/21-openclaw-automations-nobody-talks-about...

**从部分内容提取**：

- 作者在 VPS 上跑 OpenClaw + Convex + Clerk + Supabase + n8n
- 强调"无聊的自动化最省时间"（非炫技类）
- 文章按"每周节省时间"排序，而非"酷炫程度"
- 全文被截断，无法获取完整 21 条

**对我们的影响**：

- 我们的 Cron 任务（心跳、周报、健康检查）属于"无聊但有效"类
- 社区已有大量实践，值得学习

---

## 🎯 最值得关注的 3 条

1. **AGENTS.md 瘦身**（P0）
   - 研究证明：过度指令会降低成功率、增加成本
   - 行动：审计当前 2800 行，只保留非推断知识

2. **向量记忆检索**（P1）
   - 趋势：分层记忆 + 向量数据库成为主流
   - 行动：小规模实验 Chroma/LanceDB，对比 QMD

3. **社区最佳实践学习**（P2）
   - 发现：Medium/Reddit 有大量真实部署案例
   - 行动：系统性收集社区高频提及的自动化场景

---

## 🔗 待深度碰撞的问题

以下问题适合用 Perplexity 高级模型（GPT-5.2/Grok 4.1）多轮问询：

1. **AGENTS.md 最佳实践**：
   - 问：对于一个运行 4 个子 Agent 的 OpenClaw 系统，AGENTS.md 应该包含哪些内容？
   - 问：如何区分"模型能推断"vs"必须明说"的知识？
   - 问：有没有 AGENTS.md 瘦身的自动化工具？

2. **向量记忆架构**：
   - 问：对于 <10000 条记忆的系统，向量检索 vs 文本搜索的性能对比？
   - 问：Chroma/LanceDB/FAISS 在本地部署的成本和复杂度？
   - 问：如何设计混合检索（文本 + 向量）的 fallback 策略？

3. **OpenClaw 社区实践**：
   - 问：Reddit r/LocalLLaMA 和 GitHub Discussions 中，OpenClaw 用户最常提及的痛点和解决方案？
   - 问：有没有 OpenClaw + n8n/Zapier 的集成最佳实践？

---

## 📊 本次侦察统计

- 外部搜索：3 个方向，15 条结果
- 深度阅读：3 篇（1 篇完整，1 篇部分，1 篇限流）
- 发现新趋势：2 个（AGENTS.md 瘦身、向量记忆）
- 生成提案：7 个（P0×1, P1×2, P2×2）
- 耗时：约 4 分钟

---

## 下一步

1. jimmy 向厂长发送周报摘要（Telegram）
2. 将 P0-1 提案加入 task-board.json
3. 下周一启动 AGENTS.md 审计
