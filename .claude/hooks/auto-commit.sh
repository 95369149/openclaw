#!/usr/bin/env bash
# .claude/hooks/auto-commit.sh
# 任务完成后自动 git commit（Stop 事件触发）
set -euo pipefail

cd /Users/apple/.openclaw/workspace

# 有未提交变更才提交
if git diff --quiet && git diff --cached --quiet; then
  exit 0
fi

timestamp=$(date +"%Y-%m-%d %H:%M")
git add -A
git commit -m "auto: kitt session changes $timestamp" --no-verify 2>/dev/null || true
exit 0
