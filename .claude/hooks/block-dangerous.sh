#!/usr/bin/env bash
# .claude/hooks/block-dangerous.sh
# 拦截危险命令，exit 2 = block，exit 0 = 放行
set -euo pipefail

cmd=$(jq -r '.tool_input.command // ""' 2>/dev/null || echo "")

dangerous_patterns=(
  "rm -rf"
  "rm -fr"
  "git reset --hard"
  "git push.*--force"
  "git push.*-f"
  "DROP TABLE"
  "DROP DATABASE"
  "truncate table"
  "curl.*|.*sh"
  "wget.*|.*bash"
  "shutil.rmtree"
  "os.remove.*memory/10_项目"
  "os.remove.*task-board"
)

for pattern in "${dangerous_patterns[@]}"; do
  if echo "$cmd" | grep -qiE "$pattern"; then
    echo "🛡️ [fs_guard] Blocked: '$cmd' matches dangerous pattern '$pattern'. Propose a safer alternative." >&2
    exit 2
  fi
done
exit 0
