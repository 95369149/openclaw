// ═══════════════════════════════════════════════════════════════════════
// utils.ts
// 通用工具函数：超时保护、内容校验、子进程包装
// ═══════════════════════════════════════════════════════════════════════

import { spawnSync } from "child_process";

/**
 * 给任意 Promise 加超时保护。
 * 超时后抛 Error，触发 Orchestrator 的 retry 机制。
 *
 * @example
 * const result = await withTimeout(callLLM(prompt), 30_000, 'LLM call');
 */
export function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  label = "operation",
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`${label} 超时（${timeoutMs}ms）`)), timeoutMs),
  );
  return Promise.race([promise, timeout]);
}

/**
 * 校验 LLM 输出内容是否有效。
 * 空字符串、拒绝回答等情况直接抛错，触发重试。
 */
export function assertLLMOutput(content: string | undefined | null, label = "LLM output"): string {
  if (!content || content.trim().length === 0) {
    throw new Error(`${label}：返回空内容`);
  }
  const refusalPatterns = [
    "抱歉，我无法",
    "我不能帮助",
    "I cannot",
    "I am unable to",
    "As an AI",
    "作为AI",
  ];
  for (const pattern of refusalPatterns) {
    if (content.includes(pattern)) {
      throw new Error(`${label}：LLM 拒绝回答（${pattern}）`);
    }
  }
  return content.trim();
}

/**
 * 带超时的子进程调用（用于 Nano Banana / ffmpeg 等）。
 * 超时或非零退出码均抛错，触发 Orchestrator retry。
 */
export function spawnWithTimeout(
  cmd: string,
  args: string[],
  options: { timeoutMs?: number; label?: string } = {},
): { stdout: string; stderr: string } {
  const { timeoutMs = 120_000, label = cmd } = options;

  const result = spawnSync(cmd, args, { encoding: "utf-8", timeout: timeoutMs });

  if (result.signal === "SIGTERM") {
    throw new Error(`${label} 超时（${timeoutMs}ms）`);
  }
  if (result.status !== 0) {
    throw new Error(`${label} 失败（exit ${result.status}）: ${result.stderr?.slice(0, 400)}`);
  }

  return { stdout: result.stdout ?? "", stderr: result.stderr ?? "" };
}

/** sleep */
export function sleep(ms: number): Promise<void> {
  return new Promise<void>((r) => setTimeout(r, ms));
}
