// ═══════════════════════════════════════════════════════════════════════
// example_video_pipeline.ts
// Example: video content pipeline using WorkflowOrchestrator
//
// How to use from a cron agentTurn job:
//   import { runVideoPipeline } from './example_video_pipeline.js';
//   const jobId = await runVideoPipeline({ productName: 'XC-3000', keywords: ['激光切割'] });
//
// Or enqueue and forget (fire-and-forget pattern):
//   runVideoPipeline({ ... }).then(jobId => console.log('Enqueued:', jobId));
// ═══════════════════════════════════════════════════════════════════════

import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { enqueueOpenClawJob, waitForJob, summarizeJob } from "./openclaw_integration.js";
import { StepDefinition, StepContext, CompensateContext } from "./types.js";

// ── Output directory ─────────────────────────────────────────────────

const OUTPUT_DIR = path.join(os.homedir(), ".openclaw", "workspace", "output", "video_pipeline");

function ensureOutputDir(): void {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// ── Step: Generate script ────────────────────────────────────────────

const stepGenerateScript: StepDefinition<{ script: string; scriptPath: string }> = {
  id: "video_pipeline__generate_script",
  name: "生成营销脚本",
  retryPolicy: {
    maxAttempts: 3,
    initialBackoffMs: 2_000,
    maxBackoffMs: 15_000,
    backoffMultiplier: 2,
  },

  async fn(ctx: StepContext) {
    ensureOutputDir();
    const input = ctx.workflowInput as { productName: string; keywords: string[] };
    ctx.log(`Generating script for: ${input.productName}`);

    // TODO: Replace with real LLM call (e.g. via OpenClaw agent or direct API)
    await new Promise<void>((r) => setTimeout(r, 500));

    const script = [
      `产品：${input.productName}`,
      `关键词：${input.keywords.join("、")}`,
      `脚本：高精度数控切割，适合中小制造企业，30秒抖音版。`,
    ].join("\n");

    const scriptPath = path.join(OUTPUT_DIR, `${ctx.jobId}_script.txt`);
    fs.writeFileSync(scriptPath, script, "utf-8");
    ctx.log(`Script saved: ${scriptPath}`);

    return { script, scriptPath };
  },
  // No compensate needed: text file is cheap to discard
};

// ── Step: Generate images ────────────────────────────────────────────

const stepGenerateImages: StepDefinition<{ imagePaths: string[] }> = {
  id: "video_pipeline__generate_images",
  name: "生成产品图片",
  retryPolicy: {
    maxAttempts: 2,
    initialBackoffMs: 5_000,
    maxBackoffMs: 30_000,
    backoffMultiplier: 2,
  },

  async fn(ctx: StepContext) {
    ensureOutputDir();
    const { script } = ctx.previousOutputs["video_pipeline__generate_script"] as {
      script: string;
    };
    ctx.log("Generating images...");

    // TODO: Replace with real image generation (e.g. Nano Banana Pro / Gemini Imagen)
    await new Promise<void>((r) => setTimeout(r, 800));

    const imagePaths = Array.from({ length: 3 }, (_, i) => {
      const p = path.join(OUTPUT_DIR, `${ctx.jobId}_img_${i}.png`);
      fs.writeFileSync(p, `placeholder image ${i} for: ${script.slice(0, 30)}`);
      return p;
    });

    ctx.log(`${imagePaths.length} images created`);
    return { imagePaths };
  },

  async compensate(ctx: CompensateContext) {
    const out = ctx.previousOutputs["video_pipeline__generate_images"] as
      | { imagePaths?: string[] }
      | undefined;
    for (const p of out?.imagePaths ?? []) {
      try {
        if (fs.existsSync(p)) {
          fs.unlinkSync(p);
          ctx.log(`Deleted: ${p}`);
        }
      } catch {
        /* best effort */
      }
    }
  },
};

// ── Step: Synthesize video (requires human review) ───────────────────

const stepSynthesizeVideo: StepDefinition<{ videoPath: string }> = {
  id: "video_pipeline__synthesize_video",
  name: "合成视频",
  retryPolicy: {
    maxAttempts: 2,
    initialBackoffMs: 10_000,
    maxBackoffMs: 60_000,
    backoffMultiplier: 2,
  },
  requiresHumanReview: true, // ⭐ job suspends here until human approves

  async fn(ctx: StepContext) {
    ensureOutputDir();
    const { script } = ctx.previousOutputs["video_pipeline__generate_script"] as { script: string };
    const { imagePaths } = ctx.previousOutputs["video_pipeline__generate_images"] as {
      imagePaths: string[];
    };
    ctx.log(`Synthesizing video from ${imagePaths.length} images...`);

    // TODO: Replace with real video synthesis (e.g. Veo / ffmpeg)
    await new Promise<void>((r) => setTimeout(r, 1_500));

    const videoPath = path.join(OUTPUT_DIR, `${ctx.jobId}_draft.mp4`);
    fs.writeFileSync(videoPath, `placeholder video: ${script.slice(0, 40)}`);
    ctx.log(`Video draft saved: ${videoPath}`);

    return { videoPath };
  },

  async compensate(ctx: CompensateContext) {
    const out = ctx.previousOutputs["video_pipeline__synthesize_video"] as
      | { videoPath?: string }
      | undefined;
    const p = out?.videoPath;
    if (p && fs.existsSync(p)) {
      fs.unlinkSync(p);
      ctx.log(`Deleted draft: ${p}`);
    }
  },
};

// ── All steps for this pipeline ──────────────────────────────────────

export const VIDEO_PIPELINE_STEPS: StepDefinition[] = [
  stepGenerateScript,
  stepGenerateImages,
  stepSynthesizeVideo,
];

// ── Public API ───────────────────────────────────────────────────────

export interface VideoPipelineInput {
  productName: string;
  keywords: string[];
  /** Optional: prevents duplicate jobs for the same product run */
  idempotencyKey?: string;
}

/**
 * Enqueue a video pipeline job and return the jobId immediately.
 * The job runs in the background via the singleton orchestrator.
 *
 * Use this from cron agentTurn jobs or agent tool handlers.
 */
export async function runVideoPipeline(input: VideoPipelineInput): Promise<string> {
  const jobId = await enqueueOpenClawJob({
    workflowId: "video_pipeline",
    input,
    steps: VIDEO_PIPELINE_STEPS,
    idempotencyKey: input.idempotencyKey,
  });
  return jobId;
}

/**
 * Enqueue and wait for the pipeline to reach a terminal or human-review state.
 * Returns a human-readable summary.
 *
 * Use this for short pipelines or when you need the result inline.
 * For long pipelines (video synthesis), prefer runVideoPipeline() + poll later.
 */
export async function runVideoPipelineAndWait(
  input: VideoPipelineInput,
  timeoutMs = 120_000,
): Promise<string> {
  const jobId = await runVideoPipeline(input);
  const job = await waitForJob(jobId, { timeoutMs });
  return summarizeJob(job);
}
