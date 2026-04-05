# 语义记忆：OpenViking 上下文数据库 — 对照分析与升级路径

## 项目信息
- GitHub: https://github.com/volcengine/OpenViking
- 官网: https://openviking.ai
- 团队: 字节跳动 Viking 团队（VikingDB 向量数据库原班人马）
- 开源时间: 2026年1月
- 来源: @xxx111god (Jason Zuo) 推文 + 实战文章

## OpenViking 核心架构

### 设计哲学：Everything is a File
记忆、资源、技能统一抽象为虚拟文件系统（viking:// 协议），每个条目有唯一 URI。

### 四大核心能力

#### 1. 文件系统管理范式
- 摒弃传统 RAG 碎片化向量存储
- 统一管理 memory / resource / skill
- Agent 可用 list、find 等标准指令操作上下文
- 从"模糊语义匹配"升级为"确定性文件操作"

#### 2. L0/L1/L2 三层按需加载
- L0（摘要）：一句话概括，快速判断
- L1（概述）：核心信息+使用场景，规划决策用
- L2（详情）：完整原始数据，深入读取用
- 写入时自动处理为三层，按需加载，大幅省 token

#### 3. 目录递归检索
- 意图分析 → 生成多检索条件
- 向量检索定位高分目录
- 目录内二次检索 → 更新候选集
- 子目录逐层递归
- "先锁定目录、再精细探索"策略

#### 4. 可观测 + 自迭代
- 检索轨迹完整留存，可视化调试
- session.commit() 触发记忆自迭代
- 自动更新 User 和 Agent 的 /memory 目录
- 提取操作技巧、工具使用经验

## 与我们系统的对照

### 我们已有的（✅ 对齐）
| 维度 | 我们的实现 | OpenViking |
|------|-----------|------------|
| 文件系统范式 | memory/ 目录树 + MEMORY.md | viking:// 虚拟文件系统 |
| 分层加载 | L0-L4 分层（INDEX.md） | L0/L1/L2 三层 |
| 记忆分类 | 语义记忆/情景记忆/收藏/强制规则 | memory/resource/skill |
| 语义搜索 | memory_search（embedding） | find（向量+目录递归） |

### 我们缺的（❌ 需升级）
| 维度 | 差距 | 优先级 |
|------|------|--------|
| 三级索引（目录递归检索） | 我们只有扁平语义搜索，没有"先定位目录再精细搜索"的递归策略 | P0 |
| 自动摘要分层 | 我们手动写摘要，OpenViking 写入时自动生成 L0/L1/L2 | P1 |
| session.commit() 自迭代 | 我们靠 cron 手动整理，没有会话结束自动提取记忆的闭环 | P1 |
| 检索轨迹可观测 | 我们的 memory_search 是黑箱，无法看到为什么召回了某条 | P2 |
| 统一 URI 寻址 | 我们用文件路径，没有统一协议层 | P2 |

## 可落地的升级方案

### Phase 1: 三级索引（解决"怎么找"）
当前问题：memory_search 只做扁平向量匹配，记忆多了之后召回质量下降。
方案：
- 给每个 memory/ 子目录维护一个 INDEX.md（已有雏形）
- 搜索时先匹配目录级摘要，锁定 1-2 个最相关目录
- 再在目录内做精细语义搜索
- 实现：可在 HEARTBEAT 或搜索前加一层目录路由逻辑

### Phase 2: 写入时自动分层
当前问题：每次存记忆都是手写全文，没有自动摘要。
方案：
- 写入语义记忆时，自动在文件头部生成 1 行摘要（L0）+ 3-5 行概述（L1）
- 正文作为 L2
- 搜索时优先匹配 L0/L1，需要时再加载 L2

### Phase 3: 会话自迭代
当前问题：记忆提取靠人工触发或 cron。
方案：
- 每次重要会话结束时，自动提取：新学到的知识、用户偏好变化、工具使用经验
- 写入对应 memory/ 目录
- 可结合现有 memory-janitor cron 实现

## 持续关注
- GitHub: volcengine/OpenViking — star 并 watch releases
- 重点关注：Python SDK 更新、MCP 集成、session management 模块
- Jason Zuo (@xxx111god) 的后续实战分享
