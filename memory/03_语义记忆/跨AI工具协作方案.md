# 语义记忆：跨 AI 工具协作方案

## 来源
@blackanger（2026-02-18 收藏，2026-02-21 消化）

## 核心方法
- 创建 `~/.teams/projects/` 共享目录作为 bridge
- Claude Code 说"交接" → session 摘要写入 bridge
- Codex 说"cowork sync" → 读取 bridge 接手
- 封装成 skill，一句话触发

## 本质
跨工具协作的关键 = 共享状态文件
- 我们的 memory/ + iCloud 同步本质相同
- 可以给 Kitt 加"交接"指令：当前上下文摘要写入指定文件，供外部 AI 读取

## 行动项
- 考虑建立标准化交接格式（当前任务 + 上下文 + 待办）
- 与 NotebookLM 数字分身的知识同步也是同一思路
