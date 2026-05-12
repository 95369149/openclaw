---
name: spawn-template
version: 1.0.0
description: 所有 spawn 子 agent 的 task 必须遵循的标准模板，强制引用 conventions 目录。
---

# 子 Agent Spawn 模板

## 规则

**每次 spawn 子 agent，task 开头必须包含 conventions 引用块。**

## 标准 task 开头模板

```
在开始任务前，先读取以下工程规矩文件：
- /Users/apple/.openclaw/workspace/skills/conventions/read-before-write.md
- /Users/apple/.openclaw/workspace/skills/conventions/scope-lock.md
- /Users/apple/.openclaw/workspace/skills/conventions/no-guessing.md
- /Users/apple/.openclaw/workspace/skills/conventions/proof-of-delivery.md

读完后再执行以下任务：

[任务正文]
```

## 高风险任务额外引用

涉及配置/删除/cron 时，额外加：

```
- /Users/apple/.openclaw/workspace/skills/conventions/risk-gate.md
- /Users/apple/.openclaw/workspace/skills/conventions/plan-first.md
```

## 碰撞会 spawn 规则（2026-05-12 定稿）

碰撞会**必须 spawn 真实子 agent**，不同模型才有真实碰撞价值。

固定模型分配：

- kitt → `opus`（claude-opus-4-6）
- deep → `gpt54`（gpt-5.4）
- guard / scout → `sonnet`（claude-sonnet-4-6）

每路子 agent 必须：

- `runTimeoutSeconds=300`
- `context="isolated"`（不用 fork）
- task 开头引用 conventions 目录
- 超时视为失败，jimmy 主进程接管该路视角

## 禁止行为

- ❌ spawn 子 agent 时不传 conventions 路径
- ❌ 碰撞会用免费/低级模型
- ❌ 无限等待子 agent，不设超时
- ❌ 子 agent 超时后装死不降级

## 验证方式

spawn 前检查 task 字符串：

- 是否包含 conventions 路径引用
- 是否是碰撞会场景（如果是，改为主进程执行）
