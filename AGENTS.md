# Repository Guidelines

Repo: https://github.com/openclaw/openclaw

## Project Structure

- Source: `src/` (CLI: `src/cli`, commands: `src/commands`, web: `src/provider-web.ts`, infra: `src/infra`, media: `src/media`)
- Tests: colocated `*.test.ts`. Docs: `docs/`. Built: `dist/`
- Plugins: `extensions/*` (workspace packages). Plugin deps in extension `package.json`
- Installers: sibling repo `../openclaw.ai` (`public/install.sh`, `public/install-cli.sh`, `public/install.ps1`)
- Channels: Core (`src/telegram`, `src/discord`, `src/slack`, `src/signal`, `src/imessage`, `src/web`) + Extensions (`extensions/*`)
- When adding channels/extensions/docs, update `.github/labeler.yml` and create matching GitHub labels

## Docs (Mintlify)

- Hosted at docs.openclaw.ai. Internal links: root-relative, no `.md`/`.mdx` (e.g. `[Config](/configuration)`)
- Anchors: `[Hooks](/configuration#hooks)`. Avoid em dashes/apostrophes in headings
- README: use absolute `https://docs.openclaw.ai/...` URLs
- i18n (`docs/zh-CN/**`): generated — don't edit unless asked. Pipeline: update English → adjust glossary → run `scripts/docs-i18n`

## Build & Dev

- Runtime: Node **22+**. Prefer Bun for TS execution
- Install: `pnpm install` (also: `bun install`, keep lockfiles in sync)
- Pre-commit: `prek install`
- Dev CLI: `pnpm openclaw ...` or `pnpm dev`
- Build/typecheck: `pnpm build` / `pnpm tsgo`
- Lint: `pnpm check` / Format: `pnpm format` / `pnpm format:fix`
- Tests: `pnpm test` / `pnpm test:coverage`
- Live tests: `CLAWDBOT_LIVE_TEST=1 pnpm test:live` or `LIVE=1 pnpm test:live`

## Coding Style

- TypeScript (ESM). Strict typing; avoid `any`. Never add `@ts-nocheck`
- Formatting/linting: Oxlint + Oxfmt; run `pnpm check` before commits
- No prototype mutation. Use explicit inheritance/composition
- Brief comments for tricky logic. Keep files under ~500-700 LOC
- Naming: **OpenClaw** for product/docs; `openclaw` for CLI/package/paths/config
- CLI progress: `src/cli/progress.ts`. Status tables: `src/terminal/table.ts`. Colors: `src/terminal/palette.ts`
- Tool schema: no `Type.Union` in tool inputs; no `anyOf`/`oneOf`/`allOf`. Use `stringEnum`/`optionalStringEnum`
- SwiftUI: prefer `Observation` framework (`@Observable`, `@Bindable`) over `ObservableObject`/`@StateObject`

## Testing

- Vitest with V8 coverage (70% threshold). Naming: `*.test.ts`; e2e: `*.e2e.test.ts`
- Run `pnpm test` before pushing. Max 16 test workers
- Prefer per-instance stubs over prototype mutation
- Prefer real connected devices over simulators
- Full details: `docs/testing.md`

## Release Channels

- **stable**: tagged `vYYYY.M.D`, npm `latest`
- **beta**: `vYYYY.M.D-beta.N`, npm `beta`
- **dev**: `main` branch head (no tag)

## Commits & PRs

- Create commits: `scripts/committer "<msg>" <file...>` (avoid manual `git add`/`git commit`)
- Concise, action-oriented messages (e.g. `CLI: add verbose flag to send`). Group related changes
- PR template: `.github/pull_request_template.md`. Issue templates: `.github/ISSUE_TEMPLATE/`
- Full maintainer workflow: `.agents/skills/PR_WORKFLOW.md`
- `sync` shorthand: commit dirty changes → `git pull --rebase` → `git push`

## Multi-Agent Safety

- **Do not** create/apply/drop `git stash` (including `--autostash`)
- **Do not** create/remove/modify `git worktree` or switch branches unless explicitly requested
- Scope commits to your changes only. Keep unrecognized files untouched
- Focus reports on your edits; brief "other files present" note only if relevant
- Lint/format churn: auto-resolve formatting-only diffs without asking

## Security & Config

- Web creds: `~/.openclaw/credentials/`. Pi sessions: `~/.openclaw/sessions/`
- Never commit real phone numbers, videos, or live config values — use fake placeholders
- Release flow: read `docs/reference/RELEASING.md` and `docs/platforms/mac/release.md` first
- Do not change version numbers without explicit consent. Always ask before npm publish/release
- Never send streaming/partial replies to external messaging — only final replies
- Before modifying `~/.openclaw/openclaw.json` or other startup-critical files, create a timestamped backup first, explain risk + rollback plan, and after changes run `openclaw gateway status`
- Any startup/config change must leave the user with a one-line rollback command, typically: `cp <backup> ~/.openclaw/openclaw.json && openclaw gateway restart`
- **配置变更绝不能导致系统卡死或失联（2026-04-09 教训，厂长第一要求）**：
  - 改配置前必须 `python3 -c "import json; json.load(open(...))"` 验证 JSON 可解析
  - 改完后必须确认 gateway 启动成功（读日志或 `openclaw gateway status`）
  - 绝不用 `nohup` 拉 gateway，只用 `openclaw gateway restart` 或 `launchctl kickstart`
  - 如果 gateway 启动后 3 分钟内日志无正常输出，立即回滚
  - 回滚命令必须在改配置的同一条消息里给出

## Version Locations

`package.json` (CLI), `apps/android/app/build.gradle.kts`, `apps/ios/Sources/Info.plist` + `apps/ios/Tests/Info.plist`, `apps/macos/Sources/OpenClaw/Resources/Info.plist`, `docs/install/updating.md`, `docs/platforms/mac/release.md`, Peekaboo Xcode Info.plists. "Bump everywhere" excludes `appcast.xml` (only for Sparkle releases)

## 可复用工作铁律（Garry Tan 法则，2026-04-10）

> 一次构建，永久运行，系统不断复利增长。

1. **禁止一次性工作**：如果某件事以后可能重复，必须：第1次手动做3-10个样本 → 给厂长看结果 → 批准后写成 `SKILL.md` 放入 `workspace/skills/` → 周期性任务用 `openclaw cron add` 加定时任务
2. **MECE 原则**：每类工作只有一个 Skill 负责，不重叠不遗漏。创建新 Skill 前先检查现有 Skill，能扩展就扩展
3. **失败判定**：同一件事厂长问第二次 = 失败。第一次是发现需求，第二次说明早该变成 Skill
4. **标准流程**：Concept → Prototype → Evaluate → Codify（SKILL.md）→ Cron → Monitor

## Agent Notes

- Vocabulary: "makeup" = "mac app"
- Never edit `node_modules`. Skill notes go in `TOOLS.md` or `AGENTS.md`
- When adding `AGENTS.md` anywhere, also add a `CLAUDE.md` symlink
- When working on GitHub Issue/PR, print full URL at end
- Respond with high-confidence answers only; verify in code, don't guess
- Session files: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
- Changelog: user-facing changes only; pure test additions don't need entries

## NPM Publish & Plugin Release

- Use 1password skill; all `op` commands in fresh tmux session
- Sign in: `eval "$(op signin --account my.1password.com)"`
- OTP: `op read 'op://Private/Npmjs/one-time password?attribute=otp'`
- Publish: `npm publish --access public --otp="<otp>"` from package dir
- Verify: `npm view <pkg> version --userconfig "$(mktemp)"`
- Plugin fast path: release only already-on-npm plugins (list in `docs/reference/RELEASING.md`). Compare local version to npm; only publish when different

## Changelog & Release

- Mac beta: tag `vYYYY.M.D-beta.N`, create prerelease, attach `.zip` + `.dSYM.zip` (+ `.dmg` if available)
- `CHANGELOG.md`: `### Changes` first, then `### Fixes` (deduped, user-facing first)
- Pre-release checks: `pnpm release:check`, `pnpm test:install:smoke`

## exe.dev VM Ops

- Access: `ssh exe.dev` → `ssh vm-name`. Keep tmux for long ops
- Update: `sudo npm i -g openclaw@latest`. Config: `openclaw config set ...`; ensure `gateway.mode=local`
- Restart: `pkill -9 -f openclaw-gateway || true; nohup openclaw gateway run --bind loopback --port 18789 --force > /tmp/openclaw-gateway.log 2>&1 &`
- Verify: `openclaw channels status --probe`

## GHSA Advisory Patches

- Fetch: `gh api /repos/openclaw/openclaw/security-advisories/<GHSA>`
- Private fork PRs must be closed before publish. Build patch JSON via jq with heredoc for description
- Patch+publish: `gh api -X PATCH .../<GHSA> --input /tmp/ghsa.patch.json` (include `"state":"published"`)

## Troubleshooting

- Run `openclaw doctor` for rebrand/migration issues (see `docs/gateway/doctor.md`)
- macOS gateway: start/stop via app or `scripts/restart-mac.sh`; verify with `launchctl print gui/$UID | grep openclaw`
- macOS logs: `./scripts/clawlog.sh`
- GitHub issues/comments/PR comments: use literal multiline strings or `-F - <<'EOF'` for real newlines; never embed `\\n`

## 子 Agent 强制规则

> **详细协议见**：`/Users/apple/.openclaw/workspace/memory/01_强制规则/多Agent协同与公共记忆协议.md`

- **主工作区路径**：`/Users/apple/.openclaw/workspace/`（记忆文件、配置文件都在这里，不是你自己的 workspace）
- **权限边界铁律**：除了 Jimmy，其他子 Agent 绝对禁止修改 `openclaw.json` 和 `task-board.json`。
- **开始任务前必须先读公共记忆**：
  ```
  1. cat memory/task-board.json     → 了解当前任务全局状态
  2. ls -t memory/shared/ | head -5 → 看最新的共享记忆
  3. 读取与当前任务相关的 shared/ 文件
  ```
  **不读就开始干活 = 重复劳动 + 浪费 token**
- **任务中必须留痕**：执行多步任务时，随时追加写入中间态到 `shared/`。
- **任务完成后必须闭环**：
  1. 写入 `/Users/apple/.openclaw/workspace/memory/shared/YYYY-MM-DD_<agentId>_<简述>.md`
  2. 写完后必须调用 `read` 或检索工具验证文件已落盘
  3. **不写或不验，视为任务未完成**

## ⚠️ 压缩后恢复铁律（所有 Agent 必须执行）

**每次上下文压缩/重启/新 session 后，第一步必须读记忆，不读完不许回复任何消息。**

```
1. read memory/.abstract          → 系统架构、agent 编制
2. read memory/task-board.json    → 当前任务状态
3. read memory/2026-MM-DD.md      → 今日工作日志（不存在读昨天）
4. session_status                 → 确认当前模型
```

**违反后果：用过时信息操作，改坏配置，浪费厂长时间。**
**2026-02-26 教训：kitt 压缩后没读记忆，用旧数据把 jimmy 模型改错、写重复文件、改坏 channels 配置。**

## 子 Agent 调度规则

- **派发后不傻等**：spawn 后继续处理其他事务
- **回报机制**：子 agent 完成后静默落盘到 memory/shared/，由 jimmy 验收并向厂长汇报摘要，系统绝对禁止自动 announce 原始信息打扰厂长。
- **jimmy 验收**：用 `subagents list` 查状态，完成后读 `memory/shared/` 新文件验收
- **超时处理**：超过预期时间未完成，查 subagents list 状态，失败则换 agent 或降级自己做
- **注意**：子 agent 只注入 AGENTS.md + TOOLS.md，不注入 SOUL.md/IDENTITY.md/USER.md
- **sessions_send 不可用**：子 agent 默认没有 session 工具，这是设计如此，不要尝试开放
- **workspace 已共享**：所有 agent 共享 /Users/apple/.openclaw/workspace/，可互相读写记忆文件

### 子 Agent 写文件兜底机制（v1.0）

子 agent 写文件成功率低（实测 <30%），必须有兜底流程。

**派发规则：**

1. 任务描述第一句就写"⚠️ 第一步：创建文件 memory/shared/xxx.md 并写入标题"
2. 输出要求控制在 1000 字以内（减少 token 耗尽风险）
3. 复杂任务拆成 2-3 个子任务分别派发

**验收流程（子 agent 完成后 jimmy 必须执行）：**

```
1. ls memory/shared/ | grep "<预期文件名>"
2. 文件存在 → 读取验收质量
3. 文件不存在 → sessions_history(sessionKey, limit=5, includeTools=true)
4. 从 history 提取有价值内容 → jimmy 自己写入文件
5. 更新 task-board.json
```

**派发模板（v2.0 强制读记忆版）：**

```
sessions_spawn(agentId="<agent>", task="
⚠️ 强制前置步骤（不执行则任务无效）：
1. read /Users/apple/.openclaw/workspace/memory/task-board.json
2. exec: ls /Users/apple/.openclaw/workspace/memory/shared/ | tail -5
3. 创建文件 /Users/apple/.openclaw/workspace/memory/shared/2026-MM-DD_<agent>_<简述>.md，写入标题和时间戳

然后开始任务：<一句话任务描述>
背景：<1-2句>
输出：<格式要求，控制在1000字以内>
每完成一个章节就追加写入文件，不要等全部完成再写。
所有文件路径必须使用绝对路径 /Users/apple/.openclaw/workspace/
")
```

### 交叉审核机制（Reality Checker 模式）

借鉴 `agency-agents` 最佳实践，系统引入**现实检查器（Reality Checker）**机制来防止幻觉和质量下降：

**核心原则**：

- **执行与审核分离**：干活的 Agent 不能自己审核自己。
- **Kitt 负责终审**：涉及架构设计、复杂代码、长文报告、对外发布的内容，Jimmy/Deep 完成初稿后，必须提交给 Kitt 审查。
- **只审结果，不接管任务**：Kitt 的职责是挑刺、找漏洞、查文档一致性，而不是替 Deep 写代码。
- **一键回炉**：Kitt 发现问题后，输出修正要求，由原 Agent 重做。

**典型流程**：

1. Jimmy 派发编写代码任务给 Deep
2. Deep 完成并输出到 `memory/tmp/`
3. Jimmy 触发 Kitt 审核："请作为 Reality Checker 审查该输出，重点看红线安全和架构规范"
4. 审核通过 → 写入最终路径；审核失败 → 打回重做
