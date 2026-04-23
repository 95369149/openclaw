# Agent 可靠性规律

> 最后更新：2026-03-11

## 子 Agent 失败模式

### 1. 超时（最常见）
- deep 在大文件重构任务上容易超时（>5min）
- 原因：输出 token 过多 + 多步文件操作
- 对策：单次任务控制在 1000 字以内，复杂任务拆成 2-3 个子任务

### 2. 文件写入失败
- 子 Agent 直接写文件成功率历史上 <30%
- 已引入 manifest + apply_manifest.py 方案改善
- 当前推荐：子 Agent 输出 JSON manifest，jimmy 用脚本落盘

### 3. 路径错误
- 子 Agent 经常用相对路径或错误路径
- 对策：任务描述中必须写绝对路径 `/Users/apple/.openclaw/workspace/`

### 4. 上下文污染
- 子 Agent 返回大段 JSON/代码 → jimmy 上下文膨胀 → 后续回复质量下降
- 对策：jimmy 只保留摘要，不复述完整内容

## 最佳派发粒度
- 单次任务：1 个明确目标 + 1 个输出文件
- 输出控制：<1000 字（中文）或 <2000 tokens
- 前置读取：最多 3 个文件（task-board + 1 shared + 1 规则）

## 降级链
- deep 失败 → main 重试 → jimmy 自己写
- kitt 失败 → deep 重试 → 报告厂长
- 同一任务最多重试 2 次

## Provider 故障规律
- mynewapi：偶发 502（上游问题，非配置问题）
- mygptapi：偶发 401（key 过期或余额耗尽）
- geminiflash：偶发 503
- google-gemini / google-gemini-cli：最稳定，免费
- 教训：fallback 链必须把免费稳定 provider 排前面
