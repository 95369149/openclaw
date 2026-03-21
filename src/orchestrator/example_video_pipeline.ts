// ═══════════════════════════════════════════════════════════════════════
// example_video_pipeline.ts
// 真实视频流水线：脚本生成 → Nano Banana 出图 → ffmpeg 合成视频
//
// 调用方式：
//   import { runVideoPipeline } from './example_video_pipeline.js';
//   const jobId = await runVideoPipeline({ productName: 'XC-3000', keywords: ['激光切割'] });
// ═══════════════════════════════════════════════════════════════════════

import { spawnSync } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { enqueueOpenClawJob, waitForJob, summarizeJob } from "./openclaw_integration.js";
import { StepDefinition, StepContext, CompensateContext } from "./types.js";

// ── 路径配置 ─────────────────────────────────────────────────────────

const WORKSPACE = path.join(os.homedir(), ".openclaw", "workspace");
const OUTPUT_DIR = path.join(WORKSPACE, "output", "video_pipeline");
const NANO_SCRIPT = path.join(
  WORKSPACE,
  "skills",
  "nano-banana-pro",
  "scripts",
  "generate_image.py",
);

function ensureOutputDir(): void {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// ── Step 1: 生成营销脚本 ──────────────────────────────────────────────

const stepGenerateScript: StepDefinition<{
  script: string;
  scriptPath: string;
  imagePrompts: string[];
  videoPrompt: string;
}> = {
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
    ctx.log(`生成脚本：${input.productName}`);

    // 生成3个关键帧图片提示词（英文，Nano Banana 用）
    const imagePrompts = [
      `A ${input.productName} CNC cutting machine in action, sparks flying in slow motion, dramatic side lighting from factory windows, wide angle shot, industrial documentary style, 4K ultra sharp, warm orange tones contrasting with cool blue steel`,
      `Close-up of precision cutting head slicing through material, shallow depth of field, volumetric light beams through dust particles, cinematic style, high detail, 4K`,
      `Full production line overview with ${input.keywords[0] ?? "automated cutting"} equipment, aerial perspective, clean industrial environment, editorial photography style, 4K sharp focus`,
    ];

    // 视频合成提示词（用于 ffmpeg 字幕）
    const videoPrompt = `${input.productName} — ${input.keywords.join("、")}`;

    const script = [
      `产品：${input.productName}`,
      `关键词：${input.keywords.join("、")}`,
      `脚本：高精度数控切割，适合中小制造企业，30秒抖音版。`,
      `前3秒：切割火花特写（视觉冲击）`,
      `中段：设备全景+精度展示`,
      `结尾：品牌+联系方式`,
    ].join("\n");

    const scriptPath = path.join(OUTPUT_DIR, `${ctx.jobId}_script.txt`);
    fs.writeFileSync(scriptPath, script, "utf-8");
    ctx.log(`脚本已保存：${scriptPath}`);

    return { script, scriptPath, imagePrompts, videoPrompt };
  },
};

// ── Step 2: Nano Banana 生成关键帧图片 ───────────────────────────────

const stepGenerateImages: StepDefinition<{ imagePaths: string[] }> = {
  id: "video_pipeline__generate_images",
  name: "生成产品图片（Nano Banana）",
  retryPolicy: {
    maxAttempts: 2,
    initialBackoffMs: 5_000,
    maxBackoffMs: 30_000,
    backoffMultiplier: 2,
  },

  async fn(ctx: StepContext) {
    ensureOutputDir();
    const { imagePrompts } = ctx.previousOutputs["video_pipeline__generate_script"] as {
      imagePrompts: string[];
    };

    const imagePaths: string[] = [];
    const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);

    for (let i = 0; i < imagePrompts.length; i++) {
      const prompt = imagePrompts[i];
      const filename = `${ts}-${ctx.jobId}-img${i}.png`;
      const outPath = path.join(OUTPUT_DIR, filename);

      ctx.log(`生成图片 ${i + 1}/${imagePrompts.length}...`);

      const result = spawnSync(
        "uv",
        ["run", NANO_SCRIPT, "--prompt", prompt, "--filename", outPath, "--resolution", "1K"],
        { encoding: "utf-8", timeout: 120_000 },
      );

      if (result.status !== 0) {
        throw new Error(`Nano Banana 失败（图片${i + 1}）: ${result.stderr?.slice(0, 300)}`);
      }

      if (!fs.existsSync(outPath)) {
        throw new Error(`图片文件未生成：${outPath}`);
      }

      ctx.log(`图片 ${i + 1} 已生成：${outPath}`);
      imagePaths.push(outPath);
    }

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
          ctx.log(`已删除：${p}`);
        }
      } catch {
        /* best effort */
      }
    }
  },
};

// ── Step 3: ffmpeg 合成视频（需人工审核） ────────────────────────────

const stepSynthesizeVideo: StepDefinition<{ videoPath: string; verticalPath: string }> = {
  id: "video_pipeline__synthesize_video",
  name: "合成视频（ffmpeg）",
  retryPolicy: {
    maxAttempts: 2,
    initialBackoffMs: 5_000,
    maxBackoffMs: 30_000,
    backoffMultiplier: 2,
  },
  requiresHumanReview: true, // 合成后暂停，人工确认质量再继续

  async fn(ctx: StepContext) {
    ensureOutputDir();
    const { imagePaths } = ctx.previousOutputs["video_pipeline__generate_images"] as {
      imagePaths: string[];
    };
    const { videoPrompt } = ctx.previousOutputs["video_pipeline__generate_script"] as {
      videoPrompt: string;
    };

    const ts = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
    const videoPath = path.join(OUTPUT_DIR, `${ts}-${ctx.jobId}-draft.mp4`);
    const verticalPath = path.join(OUTPUT_DIR, `${ts}-${ctx.jobId}-vertical.mp4`);

    // 生成图片列表文件（ffmpeg concat 格式）
    const listPath = path.join(OUTPUT_DIR, `${ctx.jobId}_imglist.txt`);
    const listContent = imagePaths.map((p) => `file '${p}'\nduration 3`).join("\n");
    fs.writeFileSync(listPath, listContent, "utf-8");

    ctx.log(`合成横屏视频（${imagePaths.length} 张图，每张3秒）...`);

    // 横屏版：图片序列 → MP4，加字幕
    const ffmpegResult = spawnSync(
      "ffmpeg",
      [
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        listPath,
        "-vf",
        `scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=text='${videoPrompt}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h-80:shadowcolor=black:shadowx=2:shadowy=2`,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "30",
        videoPath,
      ],
      { encoding: "utf-8", timeout: 120_000 },
    );

    if (ffmpegResult.status !== 0) {
      throw new Error(`ffmpeg 横屏合成失败: ${ffmpegResult.stderr?.slice(0, 300)}`);
    }

    ctx.log(`横屏视频已生成：${videoPath}`);

    // 竖屏版（抖音 9:16）
    const ffmpegVertical = spawnSync(
      "ffmpeg",
      [
        "-y",
        "-i",
        videoPath,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:a",
        "copy",
        verticalPath,
      ],
      { encoding: "utf-8", timeout: 60_000 },
    );

    if (ffmpegVertical.status !== 0) {
      ctx.log(`竖屏转换失败（非致命）: ${ffmpegVertical.stderr?.slice(0, 200)}`);
    } else {
      ctx.log(`竖屏视频已生成：${verticalPath}`);
    }

    // 清理临时文件
    try {
      fs.unlinkSync(listPath);
    } catch {
      /* ignore */
    }

    return { videoPath, verticalPath };
  },

  async compensate(ctx: CompensateContext) {
    const out = ctx.previousOutputs["video_pipeline__synthesize_video"] as
      | { videoPath?: string; verticalPath?: string }
      | undefined;
    for (const p of [out?.videoPath, out?.verticalPath]) {
      if (p && fs.existsSync(p)) {
        fs.unlinkSync(p);
        ctx.log(`已删除草稿：${p}`);
      }
    }
  },
};

// ── 导出 ─────────────────────────────────────────────────────────────

export const VIDEO_PIPELINE_STEPS: StepDefinition[] = [
  stepGenerateScript,
  stepGenerateImages,
  stepSynthesizeVideo,
];

export interface VideoPipelineInput {
  productName: string;
  keywords: string[];
  idempotencyKey?: string;
}

/** 入队后立即返回 jobId，后台异步执行 */
export async function runVideoPipeline(input: VideoPipelineInput): Promise<string> {
  return enqueueOpenClawJob({
    workflowId: "video_pipeline",
    input,
    steps: VIDEO_PIPELINE_STEPS,
    idempotencyKey: input.idempotencyKey,
  });
}

/** 入队并等待结果（适合短流水线或调试用） */
export async function runVideoPipelineAndWait(
  input: VideoPipelineInput,
  timeoutMs = 300_000,
): Promise<string> {
  const jobId = await runVideoPipeline(input);
  const job = await waitForJob(jobId, { timeoutMs });
  return summarizeJob(job);
}
