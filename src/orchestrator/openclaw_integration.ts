// ═══════════════════════════════════════════════════════════════════════
// openclaw_integration.ts
// OpenClaw integration layer for WorkflowOrchestrator
//
// Usage:
//   import { getOrchestrator, enqueueOpenClawJob } from './openclaw_integration.js';
//
// This module provides a singleton orchestrator instance scoped to the
// OpenClaw gateway process. It is designed to be used from:
//   - cron isolated-agent jobs (long-running pipelines)
//   - agent tool handlers (enqueue + poll pattern)
//   - manual CLI triggers
//
// Store location: ~/.openclaw/workspace/data/orch_store.json
// ═══════════════════════════════════════════════════════════════════════

import * as os from "os";
import * as path from "path";
import { StepDefinition, JobRecord, JobStatus } from "./types.js";
import { WorkflowOrchestrator, OrchestratorOptions } from "./workflow_orchestrator.js";

// ── Singleton ────────────────────────────────────────────────────────

let _instance: WorkflowOrchestrator | null = null;

const DEFAULT_STORE_PATH = path.join(
  os.homedir(),
  ".openclaw",
  "workspace",
  "data",
  "orch_store.json",
);

/**
 * Get (or lazily create) the singleton orchestrator.
 * Call registerSteps() before the first enqueue.
 */
export function getOrchestrator(options?: OrchestratorOptions): WorkflowOrchestrator {
  if (!_instance) {
    _instance = new WorkflowOrchestrator({
      storePath: DEFAULT_STORE_PATH,
      leaseTtlMs: 60_000,
      heartbeatIntervalMs: 15_000,
      watchdogIntervalMs: 20_000,
      maxConcurrentJobs: 3,
      workerId: "openclaw_main",
      ...options,
    });
    _instance.start();
  }
  return _instance;
}

/**
 * Gracefully stop the singleton orchestrator.
 * Call this on gateway shutdown.
 */
export function stopOrchestrator(): void {
  if (_instance) {
    _instance.stop();
    _instance = null;
  }
}

// ── Convenience helpers ──────────────────────────────────────────────

/**
 * Register steps and enqueue a job in one call.
 * Safe to call multiple times with the same idempotencyKey.
 *
 * @example
 * const jobId = await enqueueOpenClawJob({
 *   workflowId: 'video_pipeline',
 *   input: { productName: 'XC-3000', keywords: ['激光切割'] },
 *   steps: [stepGenerateScript, stepGenerateImages, stepSynthesizeVideo],
 *   idempotencyKey: 'video_xc3000_20260322',
 * });
 */
export async function enqueueOpenClawJob(params: {
  workflowId: string;
  input: unknown;
  steps: StepDefinition[];
  idempotencyKey?: string;
}): Promise<string> {
  const orch = getOrchestrator();
  // registerSteps is idempotent per id — safe to call on every enqueue
  // (duplicate ids are caught; we skip already-registered steps)
  for (const step of params.steps) {
    try {
      orch.registerSteps([step]);
    } catch (e) {
      // Ignore "Duplicate step id" — step already registered
      if (!(e instanceof Error && e.message.startsWith("Duplicate step id"))) {
        throw e;
      }
    }
  }

  return orch.enqueue({
    workflowId: params.workflowId,
    input: params.input,
    stepIds: params.steps.map((s) => s.id),
    idempotencyKey: params.idempotencyKey,
  });
}

/**
 * Poll a job until it reaches a terminal or human-review state.
 * Returns the final JobRecord.
 *
 * Useful for agent tools that need to wait for a result.
 * Max wait: timeoutMs (default 5 min). Polls every pollIntervalMs (default 3s).
 */
export async function waitForJob(
  jobId: string,
  options: { timeoutMs?: number; pollIntervalMs?: number } = {},
): Promise<JobRecord> {
  const { timeoutMs = 300_000, pollIntervalMs = 3_000 } = options;
  const orch = getOrchestrator();
  const deadline = Date.now() + timeoutMs;

  const terminalStates: JobStatus[] = new Set([
    "completed",
    "failed",
    "dead_letter",
    "pending_human_review",
  ]);

  while (Date.now() < deadline) {
    const job = orch.getJob(jobId);
    if (!job) {
      throw new Error(`Job not found: ${jobId}`);
    }
    if (terminalStates.has(job.status)) {
      return job;
    }
    await new Promise<void>((r) => setTimeout(r, pollIntervalMs));
  }

  throw new Error(`waitForJob timed out after ${timeoutMs}ms for job ${jobId}`);
}

/**
 * Get a human-readable summary of a job for agent replies.
 */
export function summarizeJob(job: JobRecord): string {
  const lines: string[] = [
    `Job: ${job.id}`,
    `Workflow: ${job.workflowId}`,
    `Status: ${job.status}`,
  ];

  if (job.deadLetterReason) {
    lines.push(`Dead letter reason: ${job.deadLetterReason}`);
  }

  for (const step of job.steps) {
    const icon =
      step.status === "completed"
        ? "✓"
        : step.status === "failed"
          ? "✗"
          : step.status === "compensated"
            ? "⟲"
            : step.status === "pending_human_review"
              ? "⏸"
              : step.status === "running"
                ? "→"
                : "○";
    lines.push(`  ${icon} [${step.name}] ${step.status}${step.error ? ` — ${step.error}` : ""}`);
  }

  return lines.join("\n");
}
