import { execFileSync } from "child_process";
import { existsSync } from "fs";

const WORKSPACE = "/Users/apple/.openclaw/workspace";
const BOOTSTRAP = `${WORKSPACE}/runtime/bootstrap.py`;

const handler = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") {return;}

  try {
    if (!existsSync(BOOTSTRAP)) {return;}

    const sessionId = event.sessionKey || "default";
    const modelId = event.context?.cfg?.agents?.jimmy?.model || "claude-sonnet";

    // 触发 memory bootstrap
    const out = execFileSync("python3", [BOOTSTRAP, sessionId, modelId], {
      cwd: WORKSPACE,
      timeout: 10000,
      encoding: "utf-8",
    });

    const state = JSON.parse(out);
    const digest = state.digest || "";

    // 把 memory 摘要注入 bootstrap files
    if (digest && event.context?.bootstrapFiles) {
      // OpenClaw 要求 bootstrapFile 必须有 path 字段
      const tmpPath = `/tmp/kitt-memory-bootstrap-${sessionId}.md`;
      const { writeFileSync } = await import("fs");
      writeFileSync(tmpPath, digest, "utf-8");
      event.context.bootstrapFiles.push({
        path: tmpPath,
        role: "system",
      });
    }

    console.log(`[kitt-bootstrap] bootstrapped session=${sessionId} model=${modelId}`);
  } catch (e) {
    console.error("[kitt-bootstrap] error:", e.message);
  }
};

export default handler;
