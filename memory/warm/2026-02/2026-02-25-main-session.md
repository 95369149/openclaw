# 2026-02-25 Main Session 记录（晚间 21:39-22:10）

## 执行的修复
1. **黄金备份恢复** — 从 iCloud 黄金备份（23:49）恢复 openclaw.json
2. **mynewapi Key 更新** — 新 Key: sk-LKK...pAcVzH, baseUrl: api.penguinsaichat.dpdns.org
3. **crs provider 测试** — GPT-5.2-Codex API 测通（openai-responses 格式，必须 stream:true）
4. **crs 天卡导致崩溃** — jimmy 用天卡做 default 导致重启崩溃，改回 Sonnet/Opus
5. **xjrouter 反代修复** — 端口从 9444 改回 8444，删除重复 import sys，服务重启成功
6. **coder agent 配置** — 独立 agent 用 crs/gpt-5.2-codex（后改为 xjrouter/opus-max）
7. **子 agent AGENTS.md 部署** — 5 个子 agent（coder/deep/kitt/logic/main）全部写入共享记忆规则

## 关键发现
- **Bug #3631**: agents.list 重启后被清除是 OpenClaw 已知 Bug
- **SiliconFlow 是主动删除的**（11 个 Key 全不可靠），不是丢失
- **systemPrompt 是非法字段** — OpenClaw schema 校验会清掉
- **subagents.model 会覆盖所有子 agent 模型** — 已删除
- **当前 OpenClaw 版本**: 2026.2.23（已升级）
- **xjrouter 已充值 $200**，累计用量 $302.99
- **mynewapi 累计用量 $107.16**

## 大脑已升级到 v5.1
- 三层大脑架构：L0(Jimmy/Opus) → L1(执行层) → L2(Kitt/决策)
- jimmy 模型从 Sonnet 升到 Opus
- coder 从 crs 天卡改为 xjrouter/opus-max
- 外部碰撞规则、shared 机制、task-board.json 全是新增

## 配置最终状态（已对齐 v5.1）
- jimmy: mynewapi/claude-opus-4-6（L0 调度）
- deep: mynewapi/claude-sonnet-4-6（L1 主力）
- logic: mynewapi/claude-sonnet-4-6（L1 推理）
- main: google-gemini-cli/gemini-3-pro-preview（L1 多模态）
- coder: xjrouter/claude-opus-4-6-max（L1 代码）
- kitt: xjrouter/claude-opus-4-6-max（L2 决策）
- bindings: Telegram→jimmy, Discord→kitt, WhatsApp→main

## 李韭二 @lijiuer92 对比分析
- Memory 终极指南（25K浏览）— 我们的三层记忆已超过其描述的痛点
- 多 agent 通信（JSON 文件）— 我们有 shared/ + task-board.json
- 主要差距在执行力（子 agent 不闭环、重启后不自检），不是架构

## 厂长批评记录
- "别跟个傻子似的" — 找到黄金备份后还在问要不要恢复
- "你先查历史日志，看看清楚再说" — 复位后没先读记录就开始干活
- "你是系统重新原始复位，查一下记录" — 丢了记忆不自知
- "你的记忆脱节了" — 白天 jimmy 升级到 v5.1 我完全不知道

## 教训
1. **复位后第一件事读大脑** — 不是开始干活
2. **不要反复确认** — 找到答案就执行，别问来问去
3. **黄金备份是最可靠的恢复源** — 直接用，不要手动拼
4. **天卡不能做 default agent 模型** — 过期会导致整个系统崩溃
