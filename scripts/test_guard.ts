#!/usr/bin/env npx ts-node --esm
/**
 * guard 验证脚本：测试 4 种场景
 * 1. 正常完成
 * 2. 失败后重试
 * 3. 达到 MAX_ATTEMPTS 进入 dead_letter
 * 4. 重置后可再次执行
 */
import {
  guardedRunIsolatedAgentJob,
  getGuardStatus,
  resetGuardRecord,
} from "../src/orchestrator/agent_job_guard.js";

const PASS = "✅";
const FAIL = "❌";

function assert(cond: boolean, msg: string) {
  if (!cond) {throw new Error(`ASSERT FAILED: ${msg}`);}
  console.log(`  ${PASS} ${msg}`);
}

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

// ── 场景 1：正常完成 ──────────────────────────────────────────────────
async function testNormal() {
  console.log("\n[场景1] 正常完成");
  const id = `test_normal_${Date.now()}`;
  const r = await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-normal",
    maxAttempts: 3,
    run: async () => "ok",
  });
  assert(r.status === "completed", `status=completed (got ${r.status})`);
  assert(r.result === "ok", `result=ok`);
  assert(r.attempts === 1, `attempts=1 (got ${r.attempts})`);
  const s = await getGuardStatus(id);
  assert(s?.status === "completed", `store.status=completed`);
}

// ── 场景 2：失败一次后重试成功 ────────────────────────────────────────
async function testRetry() {
  console.log("\n[场景2] 失败后重试");
  const id = `test_retry_${Date.now()}`;
  let calls = 0;

  // 第一次调用：失败
  const r1 = await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-retry",
    maxAttempts: 3,
    run: async () => {
      calls++;
      throw new Error("模拟失败");
    },
  });
  assert(r1.status === "failed", `第一次 status=failed (got ${r1.status})`);
  assert(r1.attempts === 1, `第一次 attempts=1 (got ${r1.attempts})`);

  // 第二次调用：成功
  const r2 = await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-retry",
    maxAttempts: 3,
    run: async () => {
      calls++;
      return "retry-ok";
    },
  });
  assert(r2.status === "completed", `第二次 status=completed (got ${r2.status})`);
  assert(r2.attempts === 2, `第二次 attempts=2 (got ${r2.attempts})`);
  assert(calls === 2, `总调用次数=2 (got ${calls})`);
}

// ── 场景 3：达到 MAX_ATTEMPTS 进入 dead_letter ────────────────────────
async function testDeadLetter() {
  console.log("\n[场景3] dead_letter");
  const id = `test_dead_${Date.now()}`;
  const maxAttempts = 2;

  for (let i = 1; i <= maxAttempts; i++) {
    const r = await guardedRunIsolatedAgentJob({
      cronJobId: id,
      cronJobName: "test-dead",
      maxAttempts,
      run: async () => {
        throw new Error(`失败 attempt ${i}`);
      },
    });
    if (i < maxAttempts) {
      assert(r.status === "failed", `attempt ${i} status=failed`);
    } else {
      assert(r.status === "dead_letter", `attempt ${i} status=dead_letter (got ${r.status})`);
    }
  }

  // 再调用一次，应该直接返回 dead_letter 不执行
  let extraCalled = false;
  const r = await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-dead",
    maxAttempts,
    run: async () => {
      extraCalled = true;
      return "should-not-run";
    },
  });
  assert(r.status === "dead_letter", `dead_letter 后不再执行`);
  assert(!extraCalled, `run 函数未被调用`);
}

// ── 场景 4：重置后可再次执行 ──────────────────────────────────────────
async function testReset() {
  console.log("\n[场景4] 重置后恢复");
  const id = `test_reset_${Date.now()}`;

  // 先打到 dead_letter
  await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-reset",
    maxAttempts: 1,
    run: async () => { throw new Error("打到 dead_letter"); },
  });
  const s1 = await getGuardStatus(id);
  assert(s1?.status === "dead_letter", `已进入 dead_letter`);

  // 重置
  await resetGuardRecord(id);
  const s2 = await getGuardStatus(id);
  assert(s2 === undefined, `重置后记录已清除`);

  // 重置后可正常执行
  const r = await guardedRunIsolatedAgentJob({
    cronJobId: id,
    cronJobName: "test-reset",
    maxAttempts: 1,
    run: async () => "reset-ok",
  });
  assert(r.status === "completed", `重置后执行成功`);
}

// ── 主流程 ────────────────────────────────────────────────────────────
async function main() {
  console.log("=== AgentGuard 验证开始 ===");
  try {
    await testNormal();
    await testRetry();
    await testDeadLetter();
    await testReset();
    console.log("\n=== 全部通过 ✅ ===");
    process.exit(0);
  } catch (e) {
    console.error(`\n${FAIL} 验证失败:`, e);
    process.exit(1);
  }
}

main();
