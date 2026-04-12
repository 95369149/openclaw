# 子 Agent 上下文自动注入规则 v1.0

> 创建时间：2026-03-22
> 目的：解决子 agent 开工前靠"自觉读文件"成功率低的问题

## 核心原则

**派发时主动注入上下文，不依赖子 agent 自觉读文件。**

子 agent 开工前需要的上下文，由 jimmy 在派发时自动构建并注入 task 字段。

## 工具

```bash
node /Users/apple/.openclaw/workspace/bin/build_agent_context.mjs [选项]
```

选项：
- `--task=T-xxx`：指定当前任务 ID，优先注入相关 shared 文件
- `--compact`：精简模式，每个文件只取前 10 行（节省 token）
- `--max=N`：最多注入 N 个 shared 文件（默认 3）

## 派发模板（v3.0 上下文注入版）

```javascript
// 1. 先构建上下文
import { buildAgentContext } from '/Users/apple/.openclaw/workspace/bin/build_agent_context.mjs';
const ctx = buildAgentContext({ taskId: "T-xxx", compact: true, maxSharedFiles: 2 });

// 2. 注入到 task 字段
sessions_spawn(agentId="<agent>", task=`
${ctx}

━━━ 执行规则（最高优先级）━━━
⛔ 禁止调用任何文件写入工具（write/exec/bash/shell 等）
⛔ 禁止输出 JSON 以外的任何字符
✅ 你必须输出且只输出 1 个 manifest JSON（schema_version=1.0）

━━━ 任务 ━━━
任务：<一句话任务描述>
背景：<必要上下文，1-2句>
输出要求：<格式/长度/质量标准>

━━━ 唯一合法输出：manifest JSON ━━━
{
  "schema_version": "1.0",
  "task_id": "<YYYYMMDD_HHmm_<agent>_<简述>",
  "status": "done",
  "files": [...],
  "summary": "<一句话>",
  "notes": ""
}
`)
```

## 注入内容说明

自动注入的上下文包含：

1. **任务板快照**
   - activeTasks 列表
   - readyTasks 前 5 项
   - 当前任务详情（如指定 taskId）

2. **相关 shared 文件**
   - 优先选包含 taskId 的文件
   - 补充最新的 shared 文件
   - compact 模式下每文件只取前 10 行

3. **额外指定文件**（可选）
   - 通过 `extraFiles` 参数传入绝对路径

## 何时使用

- 所有需要落盘的子 agent 任务
- 任务涉及多步骤、需要了解当前系统状态
- 任务需要参考历史 shared 文件

## 何时不用

- 纯分析类任务（不需要了解任务板状态）
- 极简单任务（单步、无状态）
- token 极度紧张时（改用 compact 模式）

## 效果

- 子 agent 开工前不再需要"第一步读文件"
- 上下文由 jimmy 统一构建，质量可控
- 减少子 agent 因读文件失败导致的任务失败
