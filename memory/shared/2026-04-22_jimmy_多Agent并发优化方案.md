# 多 Agent 并发优化方案 v1.0

整理时间：2026-04-22
适用系统：红太阳 Kitt / OpenClaw

---

## 一、当前问题诊断

| 问题 | 现状 | 影响 |
|------|------|------|
| 串行派发 | jimmy 等一个子 Agent 完成再派下一个 | 3 个独立任务需要 3x 时间 |
| 无结构化交接 | Agent 间靠自然语言传数据 | 汇总出错、信息丢失 |
| 无并发上限控制 | `subagents.maxConcurrent` 未配置 | 可能失控、成本超支 |
| 无局部失败处理 | 一个子 Agent 超时 → 整批卡死 | 可靠性差 |

---

## 二、核心优化：Fan-out 并行模式

### 原理
```
串行（现状）：
jimmy → scout_1 → (等待) → scout_2 → (等待) → scout_3 → 汇总
总耗时 = T1 + T2 + T3

并行（目标）：
jimmy → scout_1 ↘
       → scout_2 → (同时跑) → 汇总
       → scout_3 ↗
总耗时 = max(T1, T2, T3)  ← 节省 60-80%
```

### 适用场景（必须满足：子任务互相独立）
- X 日报：同时抓 11 个账号
- 竞品调研：同时搜多个竞品
- 多文件处理：同时分析多个文档
- 多语言翻译：同时翻译多个段落

### 不适用场景
- 任务 B 依赖任务 A 的输出
- 强耦合配置操作
- 极短任务（spawn 开销 > 执行时间）

---

## 三、立即可落地的三项改造

### 改造 1：配置并发上限（今天就能做）

在 `openclaw.json` 的 `agents.defaults` 里加：

```json
"subagents": {
  "maxConcurrent": 5,
  "timeoutSeconds": 120
}
```

防止失控，同时允许最多 5 个子 Agent 并行。

---

### 改造 2：jimmy 派发改并行（核心改造）

**现在的写法（串行）：**
```
1. sessions_spawn(scout, task_A)  ← 等完成
2. sessions_spawn(scout, task_B)  ← 等完成
3. sessions_spawn(scout, task_C)  ← 等完成
```

**改成（并行）：**
```
同一轮工具调用里同时发出三个 sessions_spawn：
sessions_spawn(scout, task_A)
sessions_spawn(scout, task_B)   ← 三个同时发，不等待
sessions_spawn(scout, task_C)

然后 sessions_yield() 等待所有完成事件推送回来
```

OpenClaw 的 sessions_spawn 支持在同一轮同时调用多次，结果通过 push 事件返回，不需要轮询。

---

### 改造 3：子 Agent 输出结构化（防止汇总出错）

每个子 Agent 的 task prompt 末尾加：

```
完成后将结果写入：
/Users/apple/.openclaw/workspace/memory/shared/YYYY-MM-DD_<agentId>_<taskId>_manifest.json

格式：
{
  "status": "success|failed",
  "key_findings": ["要点1", "要点2"],
  "summary": "一句话结论",
  "produced_by": "<agentId>",
  "produced_at": "<timestamp>"
}
```

jimmy 汇总时直接读 JSON，不靠解析自然语言。

---

## 四、X 日报并行化改造（具体案例）

### 现状
X 日报脚本串行抓 11 个账号，每个账号约 10-15 秒，总耗时 2-3 分钟。

### 改造后
11 个账号同时派发给 scout，并行抓取，总耗时降到 15-20 秒。

### 改造步骤

**Step 1**：把 X 日报的账号列表拆成独立任务

```python
accounts = [
    "dotey", "shao__meng", "op7418", "Yangyixxxx",
    "vista8", "wwwgoubuli", "tuturetom", "balconychy",
    "aigclink", "HiDangChen", "Gorden_Sun"
]

tasks = [
    {
        "agentId": "scout",
        "task": f"用 agent-reach 读取 @{acc} 最新 3 条推文，提取有价值内容，写入 shared/x_digest_{acc}.json",
        "label": f"x_digest_{acc}"
    }
    for acc in accounts
]
```

**Step 2**：jimmy 同一轮同时 spawn 所有任务（最多 5 个一批）

**Step 3**：等所有 manifest 落盘后，jimmy 读取汇总，生成日报

---

## 五、局部失败处理策略

并行跑时某个子 Agent 超时/失败，不能让整批卡死：

```
子 Agent 超时 → manifest 写入 status: "failed"
jimmy 汇总时 → 跳过 failed 的，用剩余结果生成报告
报告末尾注明 → "以下账号抓取失败：xxx，已跳过"
```

**降级链：**
- scout 失败 → jimmy 自己用 agent-reach 补抓
- 超过 3 个失败 → 报告厂长，不强行生成残缺报告

---

## 六、实施优先级

| 优先级 | 改造项 | 难度 | 收益 |
|--------|--------|------|------|
| P0 | 配置 maxConcurrent=5 | 5分钟 | 防失控 |
| P1 | jimmy 派发改并行 | 1小时 | 速度提升 60-80% |
| P2 | X 日报并行化 | 2小时 | 日报从 3 分钟→20 秒 |
| P3 | 子 Agent 结构化输出 | 半天 | 汇总可靠性大幅提升 |
| P4 | 局部失败降级链 | 半天 | 系统稳定性 |

---

## 七、一个注意事项

OpenClaw 的 `sessions_spawn` 有已知 bug（issue #8968）：`maxConcurrent` 配置在 spawn 入口未强制执行。
临时规避方案：jimmy 自己控制批次大小，每批最多 5 个，等一批完成再发下一批。
