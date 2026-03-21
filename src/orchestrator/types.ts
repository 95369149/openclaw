// ═══════════════════════════════════════════════════════════════════════
// types.ts
// Pure type definitions for the Durable Single-Process Orchestrator
// ═══════════════════════════════════════════════════════════════════════

export type StepStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "compensated"
  | "pending_human_review";

export type JobStatus =
  | "queued"
  | "leased"
  | "running"
  | "completed"
  | "failed"
  | "dead_letter"
  | "pending_human_review";

export interface RetryPolicy {
  maxAttempts: number;
  initialBackoffMs: number;
  maxBackoffMs: number;
  backoffMultiplier: number;
}

export const DEFAULT_RETRY_POLICY: RetryPolicy = {
  maxAttempts: 3,
  initialBackoffMs: 1_000,
  maxBackoffMs: 30_000,
  backoffMultiplier: 2,
};

export interface StepContext {
  jobId: string;
  stepId: string;
  attempt: number;
  workflowInput: unknown;
  previousOutputs: Record<string, unknown>;
  log: (msg: string) => void;
}

export interface CompensateContext extends Omit<StepContext, "attempt"> {
  failedAttempt: number;
  lastError: string;
  stepRecordSnapshot: StepRecord;
}

export interface StepDefinition<TOut = unknown> {
  id: string;
  name: string;
  retryPolicy?: Partial<RetryPolicy>;
  requiresHumanReview?: boolean;
  fn: (ctx: StepContext) => Promise<TOut>;
  compensate?: (ctx: CompensateContext) => Promise<void>;
}

export interface StepRecord {
  id: string;
  name: string;
  status: StepStatus;
  attempts: number;
  output?: unknown;
  error?: string;
  startedAt?: string;
  completedAt?: string;
  humanReviewPayload?: {
    approved: boolean;
    reviewerNote?: string;
    reviewedAt: string;
  };
}

export interface LeaseRecord {
  ownerId: string;
  token: string;
  expiresAt: number;
  lastHeartbeatAt: number;
}

export interface JobRecord {
  id: string;
  workflowId: string;
  status: JobStatus;
  input: unknown;
  steps: StepRecord[];
  lease?: LeaseRecord;
  idempotencyKey?: string;
  deadLetterReason?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface PersistentStore {
  version: number;
  createdAt: string;
  schemaVersion: number;
  jobs: Record<string, JobRecord>;
}

export const CURRENT_SCHEMA_VERSION = 1;
