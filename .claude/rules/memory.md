---
description: 记忆写入规则，适用于所有路径
globs: ["**/*"]
---

# 记忆写入规则

1. 任务完成后必须写入 memory/shared/YYYY-MM-DD_<agent>_<简述>.md
2. 写完后必须验证文件已落盘（read 或 ls 确认）
3. 每次犯错后写一条结构化教训到 memory/shared/lessons.jsonl
4. 格式：{"date":"YYYY-MM-DD","agent":"xxx","error":"xxx","lesson":"xxx"}
