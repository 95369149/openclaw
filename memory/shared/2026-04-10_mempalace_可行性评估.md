# MemPalace 接入 OpenClaw 可行性评估

时间：2026-04-10 10:35 CST

## 结论
**可行，接入成本低，建议列入 T-117 第一阶段。**

## 环境检查
- Python 3.9.6 ✅
- ChromaDB 1.5.1 已安装 ✅
- mempalace 未安装（pip install mempalace 即可）

## 核心价值
| 现在（markdown 平铺） | MemPalace |
|---|---|
| Agent 靠自觉读文件 | 语义搜索自动召回 |
| O(n) 扫描 | 向量检索 |
| 靠 agent 记得去哪找 | 问什么找什么 |
| 记忆写入靠手动 | 自动索引 |

LongMemEval 96.6%（raw mode），比任何付费方案都高。

## 接入方案（最小可用）
1. `pip install mempalace`
2. `mempalace init ~/.openclaw/workspace` — 初始化 Palace
3. 把现有 `memory/shared/*.md` 批量导入 ChromaDB
4. 在 SOUL.md 加一条：重要决策/任务完成后调用 `mempalace add` 写入
5. 查记忆时用 `mempalace search "关键词"` 替代手动 grep

## MCP 接入（进阶）
MemPalace 有 MCP server，可以直接让 Claude/Codex 调用记忆工具，不需要 agent 手动读文件。

## 风险
- Python 3.9 是否完全兼容（官方推荐 3.10+），需测试
- 现有 memory/ 目录结构迁移需要一次性脚本
- 不替换现有体系，作为检索层叠加

## 建议
T-117 启动时，第一步先跑 `pip install mempalace && mempalace init` 测试兼容性，再决定是否全量迁移。
