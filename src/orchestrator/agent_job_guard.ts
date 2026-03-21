// ═══════════════════════════════════════════════════════════════════════
// agent_job_guard.ts
// 用 orchestrator 的 lease/heartbeat/watchdog 保护 cron isolated-agent job
//
// 解决的问题：
//   - agent 断线/失联后任务静默消失，无人知晓
//   - 超时后没有自动重试机制
//   - 无法从断点续跑
//
// 使用方式（在 server-cron.ts 的 runIsolatedAgentJob 里调用）：
//   import { guardedRunIsolatedAgentJob } from '../orchestrator/agent_job_guard.js';
//
//   runIsolatedAgentJob: async ({ job, message }) => {
//     const { agentId, cfg: runtimeConfig } = resolveCronAgent(job.agentId);
//     return await guardedRunIsolatedAgentJob({
//       cronJob: job,
//       message,
//       run: () => runCronIsolatedAgentTurn({ cfg: runtimeConfig, ... }),
//     });
//   }
// ═══════════════════════════════════════════════════════════════════════

import * as crypto from "crypto";
import * as os from "os";
import * as path from "path";
import { FileStore } from "./state_store.js";
import { LeaseRecord, PersistentStore, CURRENT_SCHEMA_VERSION } from "./types.js";

// ── 配置 ─────────────────────────────────────────────────────────────

const STORE_PATH = path.join(
  os.homedir(),
  ".openclaw",
  "workspace",
  "data",
  "agent_guard_store.json",
);

/** 租约有效期：agent 必须在此时间内完成或续租，否则视为失联 */
const LEASE_TTL_MS = 90_000; // 90秒

/** 心跳间隔：每隔多久续租一次 */
const HEARTBEAT_INTERVAL_MS = 20_000; // 20秒

/** Watchdog 扫描间隔：多久扫一次过期租约 */
const WATCHDOG_INTERVAL_MS = 30_000; // 30秒

/** 单个 cron job 最多重试次数（含首次执行） */
const MAX_ATTEMPTS = 3;

/** 重试退避：初始1秒，指数增长，上限30秒 */
const INITIAL_BACKOFF_MS = 1_000;
const MAX_BACKOFF_MS = 30_000;

// ── 类型 ─────────────────────────────────────────────────────────────

export interface GuardedRunParams<TResult> {
  /** cron job 的唯一 ID（用作幂等键） */
  cronJobId: string;
  /** 可读名称，用于日志 */
  cronJobName?: string;
  /** 实际执行 agent 的函数 */
  run: () => Promise<TResult>;
  /** 可选：覆盖默认最大重试次数 */
  maxAttempts?: number;
}

export interface GuardedRunResult<TResult> {
  status: "completed" | "failed" | "dead_letter";
  result?: TResult;
  error?: string;
  attempts: number;
}

// ── 内部存储结构 ──────────────────────────────────────────────────────

interface GuardRecord {
  cronJobId: string;
  name: string;
  status: "running" | "completed" | "failed" | "dead_letter";
  attempts: number;
  maxAttempts: number;
  lease?: LeaseRecord;
  lastError?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

interface GuardStore {
  version: number;
  schemaVersion: number;
  createdAt: string;
  guards: Record<string, GuardRecord>;
}

// ── 单例 store ────────────────────────────────────────────────────────

let _store: FileStore | null = null;

function getStore(): FileStore {
  if (!_store) {
    _store = new FileStore(STORE_PATH);
  }
  return _store;
}

// ── Watchdog（单例定时器） ─────────────────────────────────────────────

let _watchdogTimer: NodeJS.Timeout | null = null;
const _activeGuards: Set<string> = new Set();

function startWatchdogIfNeeded(): void {
  if (_watchdogTimer) {
    return;
  }
  _watchdogTimer = setInterval(async () => {
    const store = getStore();
    await store.tx((raw) => {
      const gs = raw as unknown as GuardStore;
      if (!gs.guards) {
        return;
      }
      let reclaimed = 0;
      for (const g of Object.values(gs.guards)) {
        if (g.status !== "running") {
          continue;
        }
        if (_activeGuards.has(g.cronJobId)) {
          continue;
        }
        if (!g.lease) {
          continue;
        }
        if (g.lease.expiresAt < Date.now()) {
          log(`Watchdog: 回收失联任务 [${g.name}] cronJobId=${g.cronJobId}`);
          g.status = "failed";
          g.lastError = `Watchdog: 租约过期（失联超过 ${LEASE_TTL_MS / 1000}s）`;
          g.updatedAt = nowIso();
          delete g.lease;
          reclaimed++;
        }
      }
      if (reclaimed > 0) {
        log(`Watchdog: 共回收 ${reclaimed} 个失联任务`);
      }
    });
  }, WATCHDOG_INTERVAL_MS);
}

// ── 核心：带保护的 agent 执行 ─────────────────────────────────────────

/**
 * 用 lease/heartbeat/watchdog/retry 保护一次 agent 执行。
 *
 * - 执行前获取租约，执行中定时续租
 * - 失联/超时后 watchdog 标记失败，下次 cron 触发时自动重试
 * - 超过 maxAttempts 后进入 dead_letter，不再重试
 */
export async function guardedRunIsolatedAgentJob<TResult>(
  params: GuardedRunParams<TResult>,
): Promise<GuardedRunResult<TResult>> {
  const { cronJobId, cronJobName = cronJobId, run, maxAttempts = MAX_ATTEMPTS } = params;
  const store = getStore();
  startWatchdogIfNeeded();

  // 读取或初始化 guard 记录
  let record = await store.tx<GuardRecord>((raw) => {
    const gs = ensureGuardStore(raw);
    if (!gs.guards[cronJobId]) {
      gs.guards[cronJobId] = {
        cronJobId,
        name: cronJobName,
        status: "running",
        attempts: 0,
        maxAttempts,
        createdAt: nowIso(),
        updatedAt: nowIso(),
      };
    }
    return { ...gs.guards[cronJobId] };
  });

  // 检查是否已超过重试上限
  if (record.status === "dead_letter") {
    log(`[${cronJobName}] 已进入 dead_letter，跳过执行`);
    return { status: "dead_letter", error: record.lastError, attempts: record.attempts };
  }

  // 获取租约
  const workerId = `guard_${crypto.randomBytes(4).toString("hex")}`;
  const leaseToken = uid("lease");
  await store.tx((raw) => {
    const gs = ensureGuardStore(raw);
    const g = gs.guards[cronJobId];
    if (!g) {
      return;
    }
    g.status = "running";
    g.attempts += 1;
    g.lease = {
      ownerId: workerId,
      token: leaseToken,
      expiresAt: Date.now() + LEASE_TTL_MS,
      lastHeartbeatAt: Date.now(),
    };
    g.updatedAt = nowIso();
  });

  _activeGuards.add(cronJobId);

  // 启动心跳
  const heartbeatTimer = setInterval(async () => {
    await store.tx((raw) => {
      const gs = ensureGuardStore(raw);
      const g = gs.guards[cronJobId];
      if (!g?.lease || g.lease.token !== leaseToken) {
        return;
      }
      g.lease.expiresAt = Date.now() + LEASE_TTL_MS;
      g.lease.lastHeartbeatAt = Date.now();
      g.updatedAt = nowIso();
    });
  }, HEARTBEAT_INTERVAL_MS);

  record = await store.tx<GuardRecord>((raw) => ({ ...ensureGuardStore(raw).guards[cronJobId] }));
  const attempt = record.attempts;
  log(`[${cronJobName}] 开始执行 attempt ${attempt}/${maxAttempts}`);

  try {
    const result = await run();

    // 成功
    clearInterval(heartbeatTimer);
    _activeGuards.delete(cronJobId);

    await store.tx((raw) => {
      const gs = ensureGuardStore(raw);
      const g = gs.guards[cronJobId];
      if (!g) {
        return;
      }
      g.status = "completed";
      g.completedAt = nowIso();
      g.updatedAt = nowIso();
      delete g.lease;
    });

    log(`[${cronJobName}] ✓ 执行成功（attempt ${attempt}）`);
    return { status: "completed", result, attempts: attempt };
  } catch (err) {
    clearInterval(heartbeatTimer);
    _activeGuards.delete(cronJobId);

    const errorText = err instanceof Error ? err.message : String(err);
    log(`[${cronJobName}] ✗ 执行失败（attempt ${attempt}）: ${errorText}`);

    const isDead = attempt >= maxAttempts;
    await store.tx((raw) => {
      const gs = ensureGuardStore(raw);
      const g = gs.guards[cronJobId];
      if (!g) {
        return;
      }
      g.status = isDead ? "dead_letter" : "failed";
      g.lastError = errorText;
      g.updatedAt = nowIso();
      delete g.lease;
    });

    if (isDead) {
      log(`[${cronJobName}] ✗ 已达最大重试次数（${maxAttempts}），进入 dead_letter`);
      return { status: "dead_letter", error: errorText, attempts: attempt };
    }

    // 指数退避后返回 failed，等下次 cron 触发重试
    const backoffMs = Math.min(INITIAL_BACKOFF_MS * Math.pow(2, attempt - 1), MAX_BACKOFF_MS);
    log(`[${cronJobName}] 将在 ${backoffMs}ms 后可重试`);
    await sleep(backoffMs);

    return { status: "failed", error: errorText, attempts: attempt };
  }
}

/**
 * 重置某个 cron job 的 dead_letter 状态，允许重新执行。
 * 用于人工干预后恢复。
 */
export async function resetGuardRecord(cronJobId: string): Promise<void> {
  const store = getStore();
  await store.tx((raw) => {
    const gs = ensureGuardStore(raw);
    delete gs.guards[cronJobId];
  });
  log(`Guard record reset for cronJobId=${cronJobId}`);
}

/**
 * 查询某个 cron job 的保护状态。
 */
export async function getGuardStatus(cronJobId: string): Promise<GuardRecord | undefined> {
  const store = getStore();
  const raw = store.read();
  const gs = raw as unknown as GuardStore;
  return gs.guards?.[cronJobId];
}

// ── 工具函数 ──────────────────────────────────────────────────────────

function ensureGuardStore(raw: PersistentStore): GuardStore {
  const gs = raw as unknown as GuardStore;
  if (!gs.guards) {
    gs.guards = {};
  }
  if (!gs.schemaVersion) {
    gs.schemaVersion = CURRENT_SCHEMA_VERSION;
  }
  return gs;
}

function nowIso(): string {
  return new Date().toISOString();
}

function uid(prefix: string): string {
  return `${prefix}_${Date.now()}_${crypto.randomBytes(4).toString("hex")}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise<void>((r) => setTimeout(r, ms));
}

function log(msg: string): void {
  console.log(`[AgentGuard] ${msg}`);
}
