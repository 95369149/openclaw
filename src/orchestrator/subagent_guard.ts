// ═══════════════════════════════════════════════════════════════════════
// subagent_guard.ts
// 多 Agent 协同保护层
//
// 解决的问题：
//   jimmy 派 deep/kitt 跑任务，deep 断线 → 任务消失，jimmy 不知道，也没有重试。
//
// 使用方式（替换裸 sessions_spawn）：
//   import { guardedSpawnSubagent } from '../orchestrator/subagent_guard.js';
//
//   const result = await guardedSpawnSubagent({
//     task: '分析这份报告...',
//     agentId: 'deep',
//     maxAttempts: 3,
//     timeoutMs: 300_000,
//     ctx: { agentSessionKey, agentChannel, ... },
//   });
//
// 工作原理：
//   1. 调用 spawnSubagentDirect 派发子 agent
//   2. 轮询 subagent-registry 的 outcome，等待完成/失败
//   3. 失败/超时 → 指数退避重试，最多 maxAttempts 次
//   4. 全部失败 → 返回 dead_letter，调用方决定是否人工介入
//   5. 状态落盘到 agent_guard_store.json，watchdog 保护
// ═══════════════════════════════════════════════════════════════════════

import * as crypto from "crypto";
import * as os from "os";
import * as path from "path";
import {
  spawnSubagentDirect,
  SpawnSubagentParams,
  SpawnSubagentContext,
} from "../agents/subagent-spawn.js";
import { FileStore } from "./state_store.js";
import { PersistentStore, CURRENT_SCHEMA_VERSION } from "./types.js";
import { withTimeout, sleep } from "./utils.js";

// ── 配置 ─────────────────────────────────────────────────────────────

const STORE_PATH = path.join(
  os.homedir(),
  ".openclaw",
  "workspace",
  "data",
  "subagent_guard_store.json",
);

const DEFAULT_TIMEOUT_MS = 300_000; // 5分钟：子 agent 必须在此时间内完成
const DEFAULT_MAX_ATTEMPTS = 3; // 最多重试3次
const DEFAULT_POLL_INTERVAL_MS = 5_000; // 每5秒轮询一次 outcome
const INITIAL_BACKOFF_MS = 3_000;
const MAX_BACKOFF_MS = 30_000;

// ── 类型 ─────────────────────────────────────────────────────────────

export interface GuardedSpawnParams {
  /** 子 agent 的任务描述 */
  task: string;
  /** 目标 agent（deep/kitt/main 等） */
  agentId?: string;
  /** 可读标签，用于日志和状态追踪 */
  label?: string;
  /** 最大尝试次数（含首次），默认3 */
  maxAttempts?: number;
  /** 单次执行超时（ms），默认5分钟 */
  timeoutMs?: number;
  /** 轮询间隔（ms），默认5秒 */
  pollIntervalMs?: number;
  /** 幂等键：相同 key 不重复派发（已完成的任务直接返回结果） */
  idempotencyKey?: string;
  /** 透传给 spawnSubagentDirect 的上下文 */
  ctx: SpawnSubagentContext;
  /** 额外的 spawn 参数 */
  spawnParams?: Omit<SpawnSubagentParams, "task" | "agentId" | "label">;
}

export interface GuardedSpawnResult {
  status: "completed" | "failed" | "dead_letter";
  /** 子 agent 的最终输出（从 outcome 里提取） */
  output?: string;
  /** 失败原因 */
  error?: string;
  /** 实际执行次数 */
  attempts: number;
  /** 最终成功的 runId */
  runId?: string;
}

// ── 内部存储结构 ──────────────────────────────────────────────────────

interface SubagentGuardRecord {
  idempotencyKey: string;
  label: string;
  agentId: string;
  status: "running" | "completed" | "failed" | "dead_letter";
  attempts: number;
  maxAttempts: number;
  lastRunId?: string;
  lastError?: string;
  output?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

interface SubagentGuardStore {
  version: number;
  schemaVersion: number;
  createdAt: string;
  guards: Record<string, SubagentGuardRecord>;
}

// ── 单例 store ────────────────────────────────────────────────────────

let _store: FileStore | null = null;
function getStore(): FileStore {
  if (!_store) {
    _store = new FileStore(STORE_PATH);
  }
  return _store;
}

function ensureStore(raw: PersistentStore): SubagentGuardStore {
  const gs = raw as unknown as SubagentGuardStore;
  if (!gs.guards) {
    gs.guards = {};
  }
  if (!gs.schemaVersion) {
    gs.schemaVersion = CURRENT_SCHEMA_VERSION;
  }
  return gs;
}

// ── 核心：带保护的子 agent 派发 ───────────────────────────────────────

/**
 * 派发子 agent 并等待结果，失败自动重试。
 *
 * 相比裸 sessions_spawn：
 * - 等待子 agent 真正完成（不是 fire-and-forget）
 * - 失败/超时自动重试，最多 maxAttempts 次
 * - 状态落盘，重启后可查询历史
 * - 相同 idempotencyKey 不重复派发
 */
export async function guardedSpawnSubagent(
  params: GuardedSpawnParams,
): Promise<GuardedSpawnResult> {
  const {
    task,
    agentId = "deep",
    label = task.slice(0, 40),
    maxAttempts = DEFAULT_MAX_ATTEMPTS,
    timeoutMs = DEFAULT_TIMEOUT_MS,
    pollIntervalMs = DEFAULT_POLL_INTERVAL_MS,
    idempotencyKey = crypto.randomUUID(),
    ctx,
    spawnParams = {},
  } = params;

  const store = getStore();

  // 幂等检查：已完成的任务直接返回
  const existing = await store.tx<SubagentGuardRecord | null>((raw) => {
    const gs = ensureStore(raw);
    const rec = gs.guards[idempotencyKey];
    if (!rec) {
      return null;
    }
    if (rec.status === "completed" || rec.status === "dead_letter") {
      return { ...rec };
    }
    return null;
  });

  if (existing?.status === "completed") {
    log(`[${label}] 幂等命中，直接返回已完成结果`);
    return {
      status: "completed",
      output: existing.output,
      attempts: existing.attempts,
      runId: existing.lastRunId,
    };
  }
  if (existing?.status === "dead_letter") {
    log(`[${label}] 幂等命中，任务已进 dead_letter`);
    return { status: "dead_letter", error: existing.lastError, attempts: existing.attempts };
  }

  // 初始化记录
  await store.tx((raw) => {
    const gs = ensureStore(raw);
    if (!gs.guards[idempotencyKey]) {
      gs.guards[idempotencyKey] = {
        idempotencyKey,
        label,
        agentId,
        status: "running",
        attempts: 0,
        maxAttempts,
        createdAt: nowIso(),
        updatedAt: nowIso(),
      };
    }
  });

  // 重试循环
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    log(`[${label}] 派发 ${agentId}，attempt ${attempt}/${maxAttempts}`);

    await store.tx((raw) => {
      const gs = ensureStore(raw);
      const rec = gs.guards[idempotencyKey];
      if (rec) {
        rec.attempts = attempt;
        rec.updatedAt = nowIso();
      }
    });

    // 1. 派发子 agent
    let runId: string | undefined;
    try {
      const spawnResult = await withTimeout(
        spawnSubagentDirect({ task, agentId, label, ...spawnParams }, ctx),
        15_000,
        `spawn ${agentId}`,
      );

      if (spawnResult.status !== "accepted") {
        throw new Error(`spawn 被拒绝: ${spawnResult.error ?? spawnResult.status}`);
      }

      runId = spawnResult.runId;
      log(`[${label}] 已派发，runId=${runId}`);

      await store.tx((raw) => {
        const gs = ensureStore(raw);
        const rec = gs.guards[idempotencyKey];
        if (rec) {
          rec.lastRunId = runId;
          rec.updatedAt = nowIso();
        }
      });
    } catch (err) {
      const errText = err instanceof Error ? err.message : String(err);
      log(`[${label}] 派发失败（attempt ${attempt}）: ${errText}`);
      await markAttemptFailed(store, idempotencyKey, errText, attempt >= maxAttempts);
      if (attempt < maxAttempts) {
        await sleep(computeBackoff(attempt));
        continue;
      }
      return { status: "dead_letter", error: errText, attempts: attempt };
    }

    // 2. 轮询等待子 agent 完成
    try {
      const output = await withTimeout(
        pollSubagentOutcome(runId, pollIntervalMs),
        timeoutMs,
        `${agentId} 执行`,
      );

      // 成功
      await store.tx((raw) => {
        const gs = ensureStore(raw);
        const rec = gs.guards[idempotencyKey];
        if (rec) {
          rec.status = "completed";
          rec.output = output;
          rec.completedAt = nowIso();
          rec.updatedAt = nowIso();
        }
      });

      log(`[${label}] ✓ 完成（attempt ${attempt}）`);
      return { status: "completed", output, attempts: attempt, runId };
    } catch (err) {
      const errText = err instanceof Error ? err.message : String(err);
      log(`[${label}] ✗ 执行失败（attempt ${attempt}）: ${errText}`);
      await markAttemptFailed(store, idempotencyKey, errText, attempt >= maxAttempts);

      if (attempt < maxAttempts) {
        const backoff = computeBackoff(attempt);
        log(`[${label}] ${backoff}ms 后重试...`);
        await sleep(backoff);
      }
    }
  }

  const rec = (getStore().read() as unknown as SubagentGuardStore).guards[idempotencyKey];
  return {
    status: "dead_letter",
    error: rec?.lastError ?? "超过最大重试次数",
    attempts: maxAttempts,
  };
}

/**
 * 重置 dead_letter 记录，允许重新派发。
 */
export async function resetSubagentGuard(idempotencyKey: string): Promise<void> {
  const store = getStore();
  await store.tx((raw) => {
    const gs = ensureStore(raw);
    delete gs.guards[idempotencyKey];
  });
  log(`Guard record reset: ${idempotencyKey}`);
}

/**
 * 查询子 agent 保护状态。
 */
export async function getSubagentGuardStatus(
  idempotencyKey: string,
): Promise<SubagentGuardRecord | undefined> {
  const raw = getStore().read();
  return (raw as unknown as SubagentGuardStore).guards?.[idempotencyKey];
}

// ── 内部：轮询 subagent-registry outcome ─────────────────────────────

async function pollSubagentOutcome(runId: string, pollIntervalMs: number): Promise<string> {
  // 动态 import subagent-registry（避免循环依赖）
  const { getSubagentRunById } = await import("../agents/subagent-registry.js");

  while (true) {
    const record = getSubagentRunById(runId);

    if (!record) {
      // runId 不在 registry 里，可能是 gateway 重启后 registry 被清空
      // 等一轮再看，如果持续不存在则视为失败
      await sleep(pollIntervalMs);
      const retry = getSubagentRunById(runId);
      if (!retry) {
        throw new Error(`runId ${runId} 不在 registry 中（可能 gateway 已重启）`);
      }
      continue;
    }

    if (record.endedAt && record.outcome) {
      if (record.outcome.status === "ok") {
        return `runId=${runId} completed`;
      }
      if (record.outcome.status === "timeout") {
        throw new Error(`子 agent 超时: runId=${runId}`);
      }
      throw new Error(`子 agent 失败: ${record.outcome.error ?? "unknown error"}`);
    }

    await sleep(pollIntervalMs);
  }
}

// ── 工具函数 ──────────────────────────────────────────────────────────

async function markAttemptFailed(
  store: FileStore,
  key: string,
  error: string,
  isDead: boolean,
): Promise<void> {
  await store.tx((raw) => {
    const gs = ensureStore(raw);
    const rec = gs.guards[key];
    if (!rec) {
      return;
    }
    rec.status = isDead ? "dead_letter" : "failed";
    rec.lastError = error;
    rec.updatedAt = nowIso();
  });
}

function computeBackoff(attempt: number): number {
  return Math.min(INITIAL_BACKOFF_MS * Math.pow(2, attempt - 1), MAX_BACKOFF_MS);
}

function nowIso(): string {
  return new Date().toISOString();
}

function log(msg: string): void {
  console.log(`[SubagentGuard] ${msg}`);
}
