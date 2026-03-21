// ═══════════════════════════════════════════════════════════════════════
// workflow_orchestrator.ts
// Durable Single-Process Orchestrator
// ═══════════════════════════════════════════════════════════════════════

import * as crypto from "crypto";
import * as path from "path";
import { FileStore } from "./state_store.js";
import {
  JobStatus,
  RetryPolicy,
  StepDefinition,
  StepRecord,
  JobRecord,
  StepContext,
  CompensateContext,
  DEFAULT_RETRY_POLICY,
} from "./types.js";

function sleep(ms: number): Promise<void> {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}

function nowIso(): string {
  return new Date().toISOString();
}

function uid(prefix: string): string {
  return `${prefix}_${Date.now()}_${crypto.randomBytes(4).toString("hex")}`;
}

function mergeRetryPolicy(p?: Partial<RetryPolicy>): RetryPolicy {
  return { ...DEFAULT_RETRY_POLICY, ...p };
}

function computeBackoff(policy: RetryPolicy, attempt: number): number {
  const factor = Math.pow(policy.backoffMultiplier, attempt - 1);
  return Math.min(policy.initialBackoffMs * factor, policy.maxBackoffMs);
}

export interface OrchestratorOptions {
  storePath?: string;
  leaseTtlMs?: number;
  heartbeatIntervalMs?: number;
  watchdogIntervalMs?: number;
  maxConcurrentJobs?: number;
  workerId?: string;
}

export class WorkflowOrchestrator {
  private readonly db: FileStore;
  private readonly workerId: string;
  private readonly leaseTtlMs: number;
  private readonly heartbeatIntervalMs: number;
  private readonly watchdogIntervalMs: number;
  private readonly maxConcurrentJobs: number;
  private readonly activeJobIds: Set<string> = new Set();
  private readonly heartbeatTimers: Map<string, NodeJS.Timeout> = new Map();
  private watchdogTimer?: NodeJS.Timeout;
  private running = false;
  private readonly stepRegistry: Map<string, StepDefinition> = new Map();

  constructor(options: OrchestratorOptions = {}) {
    const storePath = options.storePath ?? path.join(process.cwd(), "data", "orch_store.json");
    this.db = new FileStore(storePath);
    this.workerId = options.workerId ?? uid("worker");
    this.leaseTtlMs = options.leaseTtlMs ?? 30_000;
    this.heartbeatIntervalMs = options.heartbeatIntervalMs ?? 10_000;
    this.watchdogIntervalMs = options.watchdogIntervalMs ?? 15_000;
    this.maxConcurrentJobs = options.maxConcurrentJobs ?? 3;
  }

  registerSteps(steps: StepDefinition[]): this {
    for (const s of steps) {
      if (this.stepRegistry.has(s.id)) {
        throw new Error(`Duplicate step id: ${s.id}`);
      }
      this.stepRegistry.set(s.id, s);
    }
    return this;
  }

  async enqueue(params: {
    workflowId: string;
    input: unknown;
    stepIds: string[];
    idempotencyKey?: string;
  }): Promise<string> {
    const { workflowId, input, stepIds, idempotencyKey } = params;

    return this.db.tx<string>((store) => {
      if (idempotencyKey) {
        for (const job of Object.values(store.jobs)) {
          if (job.idempotencyKey === idempotencyKey) {
            return job.id;
          }
        }
      }

      const jobId = uid("job");
      const steps: StepRecord[] = stepIds.map((stepId) => {
        const def = this.stepRegistry.get(stepId);
        if (!def) {
          throw new Error(`Step "${stepId}" not registered`);
        }
        return { id: def.id, name: def.name, status: "pending", attempts: 0 };
      });

      store.jobs[jobId] = {
        id: jobId,
        workflowId,
        status: "queued",
        input,
        steps,
        idempotencyKey,
        createdAt: nowIso(),
        updatedAt: nowIso(),
      };

      this.log(`Enqueued job ${jobId} [${workflowId}]`);
      return jobId;
    });
  }

  start(): this {
    if (this.running) {
      return this;
    }
    this.running = true;
    this.log(`Worker ${this.workerId} started`);
    this.startWatchdog();
    this.pollingLoop();
    return this;
  }

  stop(): void {
    this.running = false;
    if (this.watchdogTimer) {
      clearInterval(this.watchdogTimer);
      this.watchdogTimer = undefined;
    }
    for (const timer of this.heartbeatTimers.values()) {
      clearInterval(timer);
    }
    this.heartbeatTimers.clear();
    this.log("Orchestrator stopped");
  }

  async resumeFromHumanReview(params: {
    jobId: string;
    stepId: string;
    approved: boolean;
    reviewerNote?: string;
    overrideOutput?: unknown;
  }): Promise<JobRecord> {
    const { jobId, stepId, approved, reviewerNote, overrideOutput } = params;

    return this.db.tx<JobRecord>((store) => {
      const job = store.jobs[jobId];
      if (!job) {
        throw new Error(`Job not found: ${jobId}`);
      }
      if (job.status !== "pending_human_review") {
        throw new Error(`Job ${jobId} not in pending_human_review (current: ${job.status})`);
      }

      const step = job.steps.find((s) => s.id === stepId);
      if (!step) {
        throw new Error(`Step not found: ${stepId}`);
      }
      if (step.status !== "pending_human_review") {
        throw new Error(`Step ${stepId} not in pending_human_review`);
      }

      step.humanReviewPayload = { approved, reviewerNote, reviewedAt: nowIso() };

      if (approved) {
        step.status = "completed";
        if (overrideOutput !== undefined) {
          step.output = overrideOutput;
        }
        step.completedAt = nowIso();
        job.status = "queued";
        delete job.lease;
      } else {
        step.status = "failed";
        step.error = reviewerNote ?? "Human rejected";
        job.status = "dead_letter";
        job.deadLetterReason = `Human rejected step [${step.name}]: ${reviewerNote ?? "(no note)"}`;
      }

      job.updatedAt = nowIso();
      this.log(`Human review job ${jobId} step ${stepId}: ${approved ? "APPROVED" : "REJECTED"}`);
      return { ...job };
    });
  }

  getJob(jobId: string): JobRecord | undefined {
    return this.db.getJob(jobId);
  }

  listJobs(filter?: { status?: JobStatus; workflowId?: string }): JobRecord[] {
    const all = this.db.listJobs();
    if (!filter) {
      return all;
    }
    return all.filter((j) => {
      if (filter.status && j.status !== filter.status) {
        return false;
      }
      if (filter.workflowId && j.workflowId !== filter.workflowId) {
        return false;
      }
      return true;
    });
  }

  getStats(): Partial<Record<JobStatus, number>> {
    const stats: Partial<Record<JobStatus, number>> = {};
    for (const job of this.db.listJobs()) {
      stats[job.status] = (stats[job.status] ?? 0) + 1;
    }
    return stats;
  }

  private pollingLoop(): void {
    const tick = async () => {
      if (!this.running) {
        return;
      }
      if (this.activeJobIds.size < this.maxConcurrentJobs) {
        const job = await this.acquireLease();
        if (job) {
          this.activeJobIds.add(job.id);
          this.startHeartbeat(job.id);
          void this.executeJob(job).finally(() => {
            this.activeJobIds.delete(job.id);
            this.stopHeartbeat(job.id);
          });
        }
      }
      setTimeout(tick, 2_000);
    };
    void tick();
  }

  private async acquireLease(): Promise<JobRecord | null> {
    return this.db.tx<JobRecord | null>((store) => {
      const job = Object.values(store.jobs).find(
        (j) => j.status === "queued" && !this.activeJobIds.has(j.id),
      );
      if (!job) {
        return null;
      }

      const now = Date.now();
      job.lease = {
        ownerId: this.workerId,
        token: uid("lease"),
        expiresAt: now + this.leaseTtlMs,
        lastHeartbeatAt: now,
      };
      job.status = "leased";
      job.updatedAt = nowIso();
      this.log(`Leased job ${job.id}`);
      return { ...job };
    });
  }

  private startHeartbeat(jobId: string): void {
    if (this.heartbeatTimers.has(jobId)) {
      return;
    }
    const timer = setInterval(async () => {
      if (!this.running) {
        return;
      }
      await this.db.tx((store) => {
        const job = store.jobs[jobId];
        if (!job?.lease) {
          return;
        }
        if (job.lease.ownerId !== this.workerId) {
          return;
        }
        const now = Date.now();
        job.lease.expiresAt = now + this.leaseTtlMs;
        job.lease.lastHeartbeatAt = now;
        job.updatedAt = nowIso();
      });
    }, this.heartbeatIntervalMs);
    this.heartbeatTimers.set(jobId, timer);
  }

  private stopHeartbeat(jobId: string): void {
    const timer = this.heartbeatTimers.get(jobId);
    if (timer) {
      clearInterval(timer);
      this.heartbeatTimers.delete(jobId);
    }
  }

  private startWatchdog(): void {
    if (this.watchdogTimer) {
      clearInterval(this.watchdogTimer);
    }
    this.watchdogTimer = setInterval(async () => {
      if (!this.running) {
        return;
      }
      await this.db.tx((store) => {
        let reclaimed = 0;
        for (const job of Object.values(store.jobs)) {
          if (!["leased", "running"].includes(job.status)) {
            continue;
          }
          if (this.activeJobIds.has(job.id)) {
            continue;
          }
          if (!job.lease) {
            continue;
          }
          if (job.lease.expiresAt < Date.now()) {
            this.log(`Watchdog: reclaiming job ${job.id}`);
            for (const step of job.steps) {
              if (step.status === "running") {
                step.status = "pending";
                step.attempts = 0;
                delete step.startedAt;
                delete step.completedAt;
                delete step.error;
                delete step.output;
              }
            }
            job.status = "queued";
            delete job.lease;
            job.updatedAt = nowIso();
            reclaimed++;
          }
        }
        if (reclaimed > 0) {
          this.log(`Watchdog: reclaimed ${reclaimed} stale job(s)`);
        }
      });
    }, this.watchdogIntervalMs);
  }

  private async executeJob(initialSnapshot: JobRecord): Promise<void> {
    const jobId = initialSnapshot.id;

    await this.db.tx((store) => {
      const job = store.jobs[jobId];
      if (job) {
        job.status = "running";
        job.updatedAt = nowIso();
      }
    });

    const previousOutputs: Record<string, unknown> = {};
    const currentJob = this.db.read().jobs[jobId];
    if (!currentJob) {
      this.log(`Job ${jobId} disappeared`);
      return;
    }

    for (const step of currentJob.steps) {
      if (step.status === "completed" && step.output !== undefined) {
        previousOutputs[step.id] = step.output;
      }
    }

    for (const stepRecord of currentJob.steps) {
      const stepDef = this.stepRegistry.get(stepRecord.id);
      if (!stepDef) {
        await this.markDead(jobId, `Step not found: ${stepRecord.id}`);
        return;
      }

      if (stepRecord.status === "completed") {
        this.log(` ↷ [${stepDef.name}] already completed — skipped`);
        continue;
      }

      if (stepRecord.status === "pending_human_review") {
        this.log(` ⏸ [${stepDef.name}] pending_human_review — suspending`);
        await this.db.tx((store) => {
          const job = store.jobs[jobId];
          if (job) {
            job.status = "pending_human_review";
            delete job.lease;
            job.updatedAt = nowIso();
          }
        });
        return;
      }

      if (stepRecord.status === "running") {
        await this.db.tx((store) => {
          const step = store.jobs[jobId]?.steps.find((s) => s.id === stepRecord.id);
          if (step) {
            step.status = "pending";
            step.attempts = 0;
            delete step.startedAt;
            delete step.completedAt;
            delete step.error;
            delete step.output;
          }
        });
      }

      const ok = await this.runStepWithRetry(jobId, stepDef, previousOutputs);
      if (!ok) {
        await this.compensateStep(jobId, stepDef, previousOutputs);
        await this.markDead(jobId, `Step [${stepDef.name}] exhausted retry budget`);
        return;
      }

      const freshStep = this.db.read().jobs[jobId]?.steps.find((s) => s.id === stepDef.id);
      if (freshStep?.output !== undefined) {
        previousOutputs[stepDef.id] = freshStep.output;
      }

      if (stepDef.requiresHumanReview) {
        this.log(` ⏸ [${stepDef.name}] requires human review — suspending`);
        await this.db.tx((store) => {
          const job = store.jobs[jobId];
          const step = job?.steps.find((s) => s.id === stepDef.id);
          if (step) {
            step.status = "pending_human_review";
          }
          if (job) {
            job.status = "pending_human_review";
            delete job.lease;
            job.updatedAt = nowIso();
          }
        });
        return;
      }
    }

    await this.db.tx((store) => {
      const job = store.jobs[jobId];
      if (job) {
        job.status = "completed";
        job.completedAt = nowIso();
        delete job.lease;
        job.updatedAt = nowIso();
      }
    });
    this.log(`✓ Job ${jobId} completed`);
  }

  private async runStepWithRetry(
    jobId: string,
    stepDef: StepDefinition,
    previousOutputs: Record<string, unknown>,
  ): Promise<boolean> {
    const policy = mergeRetryPolicy(stepDef.retryPolicy);

    for (let attempt = 1; attempt <= policy.maxAttempts; attempt++) {
      await this.db.tx((store) => {
        const step = store.jobs[jobId]?.steps.find((s) => s.id === stepDef.id);
        if (step) {
          step.status = "running";
          step.attempts = attempt;
          step.startedAt = nowIso();
          delete step.error;
        }
      });

      const currentJob = this.db.read().jobs[jobId];
      if (!currentJob) {
        return false;
      }

      const ctx: StepContext = {
        jobId,
        stepId: stepDef.id,
        attempt,
        workflowInput: currentJob.input,
        previousOutputs: { ...previousOutputs },
        log: (msg) => this.log(` [${stepDef.name}][${attempt}/${policy.maxAttempts}] ${msg}`),
      };

      try {
        this.log(` → [${stepDef.name}] attempt ${attempt}/${policy.maxAttempts}`);
        const output = await stepDef.fn(ctx);
        await this.db.tx((store) => {
          const step = store.jobs[jobId]?.steps.find((s) => s.id === stepDef.id);
          if (step) {
            step.status = "completed";
            step.output = output;
            step.completedAt = nowIso();
          }
        });
        this.log(` ✓ [${stepDef.name}] completed`);
        return true;
      } catch (err) {
        const errorText = err instanceof Error ? err.message : String(err);
        this.log(` ✗ [${stepDef.name}] attempt ${attempt} failed: ${errorText}`);
        await this.db.tx((store) => {
          const step = store.jobs[jobId]?.steps.find((s) => s.id === stepDef.id);
          if (step) {
            step.status = "failed";
            step.error = errorText;
          }
        });
        if (attempt < policy.maxAttempts) {
          const backoffMs = computeBackoff(policy, attempt);
          this.log(` ↻ retry in ${backoffMs}ms`);
          await sleep(backoffMs);
        }
      }
    }
    return false;
  }

  private async compensateStep(
    jobId: string,
    stepDef: StepDefinition,
    previousOutputs: Record<string, unknown>,
  ): Promise<void> {
    if (!stepDef.compensate) {
      this.log(` ⟲ [${stepDef.name}] no compensate defined`);
      return;
    }

    const currentJob = this.db.read().jobs[jobId];
    if (!currentJob) {
      return;
    }

    const failedStep = currentJob.steps.find((s) => s.id === stepDef.id);
    if (!failedStep) {
      return;
    }

    const ctx: CompensateContext = {
      jobId,
      stepId: stepDef.id,
      failedAttempt: failedStep.attempts || mergeRetryPolicy(stepDef.retryPolicy).maxAttempts,
      workflowInput: currentJob.input,
      previousOutputs: { ...previousOutputs },
      lastError: failedStep.error ?? "Unknown error",
      stepRecordSnapshot: { ...failedStep },
      log: (msg) => this.log(` [${stepDef.name}][compensate] ${msg}`),
    };

    try {
      await stepDef.compensate(ctx);
      await this.db.tx((store) => {
        const step = store.jobs[jobId]?.steps.find((s) => s.id === stepDef.id);
        if (step) {
          step.status = "compensated";
          step.completedAt = nowIso();
        }
      });
      this.log(` ✓ [${stepDef.name}] compensation completed`);
    } catch (err) {
      this.log(
        ` ✗ [${stepDef.name}] compensation failed: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  private async markDead(jobId: string, reason: string): Promise<void> {
    await this.db.tx((store) => {
      const job = store.jobs[jobId];
      if (job) {
        job.status = "dead_letter";
        job.deadLetterReason = reason;
        delete job.lease;
        job.updatedAt = nowIso();
      }
    });
    this.log(`✗ Job ${jobId} → dead_letter: ${reason}`);
  }

  private log(msg: string): void {
    console.log(`[Orch][${this.workerId}] ${msg}`);
  }
}
