# Durable Workflow Orchestrator

OpenClaw 内置的持久化工作流调度器，用于解决长任务断点恢复、Agent 失联、浏览器卡死等稳定性问题。

## 文件结构

```
src/orchestrator/
├── types.ts                  # 类型定义
├── state_store.ts            # 原子 JSON 文件存储（单进程安全）
├── workflow_orchestrator.ts  # 核心调度器
├── openclaw_integration.ts   # OpenClaw 集成入口（推荐使用这个）
└── README.md
```

## 核心能力

| 能力 | 说明 |
|------|------|
| **Checkpoint** | 每步完成后落盘，崩溃后从最近完成步骤续跑 |
| **Lease + Heartbeat** | Worker 持有租约并定时续租，超时自动回收 |
| **Watchdog** | 独立定时器扫描过期租约，防止任务静默卡死 |
| **Retry Budget** | 指数退避重试，可配置最大次数和退避上限 |
| **Compensate** | 重试耗尽后执行补偿函数（回滚副作用） |
| **Human Review** | 步骤完成后可挂起等待人工审核，审核后继续 |
| **Idempotent Enqueue** | 相同 idempotencyKey 不重复创建 job |

## 快速使用

```typescript
import { enqueueOpenClawJob, waitForJob, summarizeJob } from './orchestrator/openclaw_integration.js';
import { StepDefinition, StepContext } from './orchestrator/types.js';

// 1. 定义步骤
const stepA: StepDefinition<{ result: string }> = {
  id: 'step_a',
  name: '第一步',
  retryPolicy: { maxAttempts: 3, initialBackoffMs: 1000, maxBackoffMs: 10000, backoffMultiplier: 2 },
  async fn(ctx: StepContext) {
    ctx.log('执行第一步...');
    return { result: 'done' };
  },
};

// 2. 入队
const jobId = await enqueueOpenClawJob({
  workflowId: 'my_pipeline',
  input: { productName: 'XC-3000' },
  steps: [stepA],
  idempotencyKey: 'my_pipeline_001', // 防重复
});

// 3. 等待结果（可选，适合短任务）
const job = await waitForJob(jobId, { timeoutMs: 60_000 });
console.log(summarizeJob(job));
```

## 状态流转

```
queued → leased → running → completed
                          ↘ failed → dead_letter
                          ↘ pending_human_review → (human approves) → queued
                                                 → (human rejects) → dead_letter
```

## 数据存储位置

```
~/.openclaw/workspace/data/orch_store.json
~/.openclaw/workspace/data/store_backups/   # 损坏文件自动备份
```

## 注意事项

- **单进程安全**：FileStore 使用进程内自旋锁，不支持多 Node.js 实例并发写同一文件
- **分布式扩展**：如需多进程，替换 FileStore 为 Redis/Postgres 后端并加分布式锁
- **步骤幂等性**：步骤 fn 应设计为幂等，相同输入多次执行结果一致
