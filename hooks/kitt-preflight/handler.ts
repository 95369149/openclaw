import { execFileSync } from "child_process";
import { existsSync } from "fs";

const WORKSPACE = "/Users/apple/.openclaw/workspace";
const CLASSIFIER = `${WORKSPACE}/runtime/task_classifier.py`;
const POLICY = `${WORKSPACE}/runtime/policy_engine.py`;

const handler = async (event) => {
  if (event.type !== "message" || event.action !== "received") {return;}

  const text = event.context?.content || "";
  if (!text.trim()) {return;}

  try {
    // 1. task classify
    if (!existsSync(CLASSIFIER)) {return;}
    const classifyOut = execFileSync("python3", [CLASSIFIER, text], {
      cwd: WORKSPACE,
      timeout: 5000,
      encoding: "utf-8",
    });
    const meta = JSON.parse(classifyOut);

    // 2. 高风险任务注入提示
    if (meta.route_mode === "FULL" || meta.enforce_review) {
      const agents = meta.required_agents?.join(", ") || "";
      const note = `[preflight] risk=${meta.risk_level} route=${meta.route_mode}${agents ? ` agents=${agents}` : ""}`;
      console.log(note);

      // 配置变更：注入警告到 bootstrap files
      if (meta.risk_level === "high_config") {
        event.messages = event.messages || [];
        // 不阻断，只记录，让 review_gate 在执行层拦截
      }
    }
  } catch (e) {
    // preflight 失败不阻断消息，只记录
    console.error("[kitt-preflight] error:", e.message);
  }
};

export default handler;
