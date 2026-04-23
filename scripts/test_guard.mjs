#!/usr/bin/env node
/**
 * guard 验证脚本（纯 JS，不依赖 ts-node）
 * 直接内联 guard 核心逻辑，验证 4 种场景：
 * 1. 正常完成
 * 2. 失败后重试
 * 3. 达到 maxAttempts 进入 dead_letter
 * 4. 重置后可再次执行
 */
import { createHash, randomBytes } from "crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync, renameSync } from "fs";
import { join } from "path";
import { homedir } from "os";

// ── 内联 FileStore ────────────────────────────────────────────────────
const STORE_PATH = join(homedir(), ".openclaw", "workspace", "data", "guard_test_store.json");
mkdirSync(join(homedir(), ".openclaw", "workspace", "data"), { recursive: true });

function readStore() {
  if (!existsSync(STORE_PATH)) {return { guards: {} };}
  try { return JSON.parse(readFileSync(STORE_PATH, "utf8")); } catch { return { guards: {} }; }
}

function writeStore(data) {
  const tmp = STORE_PATH + ".tmp";
  writeFileSync(tmp, JSON.stringify(data, null, 2), "utf8");
  renameSync(tmp, STORE_PATH);
}

function txStore(fn) {
  const data = readStore();
  const result = fn(data);
  writeStore(data);
  return result;
}

// ── 内联 guard 核心逻辑 ───────────────────────────────────────────────
const LEASE_TTL_MS = 90_000;
const HEARTBEAT_INTERVAL_MS = 20_000;
const MAX_ATTEMPTS = 3;
const INITIAL_BACKOFF_MS = 100; // 测试用小值
const MAX_BACKOFF_MS = 500;

function nowIso() { return new Date().toISOString(); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(`  [Guard] ${msg}`); }

async function guardedRun({ cronJobId, cronJobName = cronJobId, run, maxAttempts = MAX_ATTEMPTS }) {
  // 读取或初始化
  let record = txStore(data => {
    if (!data.guards[cronJobId]) {
      data.guards[cronJobId] = {
        cronJobId, name: cronJobName, status: "running",
        attempts: 0, maxAttempts, createdAt: nowIso(), updatedAt: nowIso(),
      };
    }
    return { ...data.guards[cronJobId] };
  });

  if (record.status === "dead_letter") {
    log(`[${cronJobName}] 已进入 dead_letter，跳过执行`);
    return { status: "dead_letter", error: record.lastError, attempts: record.attempts };
  }

  const leaseToken = randomBytes(4).toString("hex");
  txStore(data => {
    const g = data.guards[cronJobId];
    g.status = "running";
    g.attempts += 1;
    g.lease = { token: leaseToken, expiresAt: Date.now() + LEASE_TTL_MS, lastHeartbeatAt: Date.now() };
    g.updatedAt = nowIso();
  });

  record = txStore(data => ({ ...data.guards[cronJobId] }));
  const attempt = record.attempts;
  log(`[${cronJobName}] 开始 attempt ${attempt}/${maxAttempts}`);

  // 心跳
  const hb = setInterval(() => {
    txStore(data => {
      const g = data.guards[cronJobId];
      if (g?.lease?.token === leaseToken) {
        g.lease.expiresAt = Date.now() + LEASE_TTL_MS;
        g.lease.lastHeartbeatAt = Date.now();
      }
    });
  }, HEARTBEAT_INTERVAL_MS);

  try {
    const result = await run();
    clearInterval(hb);
    txStore(data => {
      const g = data.guards[cronJobId];
      g.status = "completed"; g.completedAt = nowIso(); g.updatedAt = nowIso();
      delete g.lease;
    });
    log(`[${cronJobName}] ✓ 成功 attempt ${attempt}`);
    return { status: "completed", result, attempts: attempt };
  } catch (err) {
    clearInterval(hb);
    const errorText = err instanceof Error ? err.message : String(err);
    const isDead = attempt >= maxAttempts;
    txStore(data => {
      const g = data.guards[cronJobId];
      g.status = isDead ? "dead_letter" : "failed";
      g.lastError = errorText; g.updatedAt = nowIso();
      delete g.lease;
    });
    if (isDead) {
      log(`[${cronJobName}] ✗ dead_letter（attempt ${attempt}/${maxAttempts}）`);
      return { status: "dead_letter", error: errorText, attempts: attempt };
    }
    const backoff = Math.min(INITIAL_BACKOFF_MS * Math.pow(2, attempt - 1), MAX_BACKOFF_MS);
    log(`[${cronJobName}] ✗ 失败，退避 ${backoff}ms`);
    await sleep(backoff);
    return { status: "failed", error: errorText, attempts: attempt };
  }
}

function getStatus(cronJobId) {
  return readStore().guards[cronJobId];
}

function resetRecord(cronJobId) {
  txStore(data => { delete data.guards[cronJobId]; });
}

// ── 断言工具 ──────────────────────────────────────────────────────────
let passed = 0, failed = 0;
function assert(cond, msg) {
  if (!cond) { console.log(`  ❌ FAIL: ${msg}`); failed++; }
  else { console.log(`  ✅ ${msg}`); passed++; }
}

// ── 场景 1：正常完成 ──────────────────────────────────────────────────
async function testNormal() {
  console.log("\n[场景1] 正常完成");
  const id = `normal_${Date.now()}`;
  const r = await guardedRun({ cronJobId: id, cronJobName: "test-normal", maxAttempts: 3, run: async () => "ok" });
  assert(r.status === "completed", `status=completed (got ${r.status})`);
  assert(r.result === "ok", `result=ok`);
  assert(r.attempts === 1, `attempts=1 (got ${r.attempts})`);
  assert(getStatus(id)?.status === "completed", `store.status=completed`);
}

// ── 场景 2：失败后重试成功 ────────────────────────────────────────────
async function testRetry() {
  console.log("\n[场景2] 失败后重试");
  const id = `retry_${Date.now()}`;
  let calls = 0;

  const r1 = await guardedRun({
    cronJobId: id, cronJobName: "test-retry", maxAttempts: 3,
    run: async () => { calls++; throw new Error("模拟失败"); },
  });
  assert(r1.status === "failed", `第一次 status=failed (got ${r1.status})`);
  assert(r1.attempts === 1, `第一次 attempts=1`);

  const r2 = await guardedRun({
    cronJobId: id, cronJobName: "test-retry", maxAttempts: 3,
    run: async () => { calls++; return "retry-ok"; },
  });
  assert(r2.status === "completed", `第二次 status=completed (got ${r2.status})`);
  assert(r2.attempts === 2, `第二次 attempts=2 (got ${r2.attempts})`);
  assert(calls === 2, `总调用次数=2 (got ${calls})`);
}

// ── 场景 3：dead_letter ───────────────────────────────────────────────
async function testDeadLetter() {
  console.log("\n[场景3] dead_letter");
  const id = `dead_${Date.now()}`;
  const maxAttempts = 2;

  const r1 = await guardedRun({ cronJobId: id, cronJobName: "test-dead", maxAttempts, run: async () => { throw new Error("失败1"); } });
  assert(r1.status === "failed", `attempt 1 status=failed`);

  const r2 = await guardedRun({ cronJobId: id, cronJobName: "test-dead", maxAttempts, run: async () => { throw new Error("失败2"); } });
  assert(r2.status === "dead_letter", `attempt 2 status=dead_letter (got ${r2.status})`);

  let extraCalled = false;
  const r3 = await guardedRun({ cronJobId: id, cronJobName: "test-dead", maxAttempts, run: async () => { extraCalled = true; return "x"; } });
  assert(r3.status === "dead_letter", `dead_letter 后不再执行`);
  assert(!extraCalled, `run 函数未被调用`);
}

// ── 场景 4：重置后恢复 ────────────────────────────────────────────────
async function testReset() {
  console.log("\n[场景4] 重置后恢复");
  const id = `reset_${Date.now()}`;

  await guardedRun({ cronJobId: id, cronJobName: "test-reset", maxAttempts: 1, run: async () => { throw new Error("打到 dead_letter"); } });
  assert(getStatus(id)?.status === "dead_letter", `已进入 dead_letter`);

  resetRecord(id);
  assert(getStatus(id) === undefined, `重置后记录已清除`);

  const r = await guardedRun({ cronJobId: id, cronJobName: "test-reset", maxAttempts: 1, run: async () => "reset-ok" });
  assert(r.status === "completed", `重置后执行成功 (got ${r.status})`);
}

// ── 主流程 ────────────────────────────────────────────────────────────
async function main() {
  console.log("=== AgentGuard 验证开始 ===");
  await testNormal();
  await testRetry();
  await testDeadLetter();
  await testReset();
  console.log(`\n=== 结果：${passed} 通过 / ${failed} 失败 ===`);
  process.exit(failed > 0 ? 1 : 0);
}

main().catch(e => { console.error("FATAL:", e); process.exit(1); });
