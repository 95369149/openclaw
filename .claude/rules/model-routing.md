---
description: 模型路由规则
globs: ["**/*"]
---

# 模型路由规则

## 原则：按任务匹配模型，不用高级模型做小事

| 任务类型 | 模型 | 原因 |
|---------|------|------|
| 定时任务/巡检/报告 | google-gemini/gemini-2.5-flash | 免费，够用 |
| 中文内容/早报/文案 | kimi/kimi-k2.5 | 免费，中文强 |
| 代码/执行/批处理 | mygptapi/gpt-5.4 | 免费，执行强 |
| 主对话/调度 | mynewapi/claude-sonnet-4-6 | 低成本，均衡 |
| 架构/终审/重大决策 | mynewapi/claude-opus-4-6 | 高成本，只用于关键决策 |
| 安全审计/配置变更 | mynewapi/claude-opus-4-6 | 高风险必须最强模型 |

## Fallback 链
Sonnet → gpt-5.4 → Gemini → GLM-4.7
