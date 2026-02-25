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

## Version Locations

`package.json` (CLI), `apps/android/app/build.gradle.kts`, `apps/ios/Sources/Info.plist` + `apps/ios/Tests/Info.plist`, `apps/macos/Sources/OpenClaw/Resources/Info.plist`, `docs/install/updating.md`, `docs/platforms/mac/release.md`, Peekaboo Xcode Info.plists. "Bump everywhere" excludes `appcast.xml` (only for Sparkle releases)

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

- **主工作区路径**：`/Users/apple/.openclaw/workspace/`（记忆文件、配置文件都在这里，不是你自己的 workspace）
- **任务完成后必须写入** `/Users/apple/.openclaw/workspace/memory/shared/YYYY-MM-DD_<agentId>_<简述>.md`
- 内容包含：做了什么、结果、关键发现
- **不写视为任务未闭环**
- 读取记忆文件时使用绝对路径 `/Users/apple/.openclaw/workspace/memory/`

## 子 Agent 调度规则

- **派发后不傻等**：spawn 后继续处理其他事务
- **回报机制**：子 agent 完成后 OpenClaw 自动 announce 到厂长的聊天渠道
- **jimmy 验收**：用 `subagents list` 查状态，完成后读 `memory/shared/` 新文件验收
- **超时处理**：超过预期时间未完成，查 subagents list 状态，失败则换 agent 或降级自己做
- **注意**：子 agent 只注入 AGENTS.md + TOOLS.md，不注入 SOUL.md/IDENTITY.md/USER.md
- **sessions_send 不可用**：子 agent 默认没有 session 工具，这是设计如此，不要尝试开放
- **workspace 已共享**：所有 agent 共享 /Users/apple/.openclaw/workspace/，可互相读写记忆文件
