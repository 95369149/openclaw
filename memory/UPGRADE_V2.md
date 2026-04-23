# Memory System V2.0 升级计划
# 融合 OpenViking 优势 + 保持现有架构

时间：2026-03-13
参考：OpenViking (ByteDance) 开源项目

---

## 当前优势（保持）

✅ **三层加载**：`.abstract`(L0) → 目录(L1) → 文件(L2)
✅ **文件系统范式**：编号目录 + 优先级标记
✅ **多 Agent 共享**：`shared/` 目录
✅ **运维状态**：`ops/state.json`
✅ **Token 优化**：启动只读摘要，不全量加载

---

## 待补强（OpenViking 启发）

### 1. 自动会话管理 ⚠️
**现状**：手动写 `shared/` 文件，没有自动从对话提取长期记忆
**目标**：每次会话结束后，自动压缩对话、提取关键信息、沉淀到 `03_语义记忆/`

**实施**：
- 新增 `scripts/session_digest.py`（已创建骨架）
- 在 cron `nightly_ops_report` 后触发
- 调用 LLM 提取：偏好/决策/模式/学习点

### 2. 可视化检索轨迹 ⚠️
**现状**：`memory_search` 是黑盒，不知道为什么选了这些结果
**目标**：每次检索都记录：query → 命中文件 → score → 返回行数

**实施**：
- 新增 `retrieval_trace.log`（已创建）
- 修改 `memory_search` 工具，每次调用追加日志
- 厂长可以随时 `cat retrieval_trace.log` 看检索路径

### 3. 语义搜索增强 ⚠️
**现状**：`memory_search` 是文本匹配，不是向量检索
**目标**：引入轻量向量 DB（如 LanceDB / Chroma），支持语义相似度搜索

**实施**（Phase 2）：
- 评估 LanceDB（OpenClaw 已测试过）
- 或直接用 OpenViking 作为 memory backend
- 保持文件系统范式不变，向量 DB 只做检索加速

---

## 迁移路径

### Phase 1: 可观测性（本周）
- ✅ 创建 `retrieval_trace.log`
- ⏳ 修改 `memory_search` 工具记录轨迹
- ⏳ 创建 `session_digest.py` 骨架

### Phase 2: 自动提取（下周）
- 实现 `session_digest.py` 的 LLM 调用
- 接入 cron 自动触发
- 验证提取质量

### Phase 3: 向量检索（待评估）
- 对比 LanceDB / OpenViking
- 小范围测试
- 全量迁移

---

## 一句话总结

**我们的记忆系统架构已经很接近 OpenViking，现在补上"自动提取 + 可观测性 + 向量检索"三块短板，就能达到工业级水平。**
