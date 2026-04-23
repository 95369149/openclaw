#!/usr/bin/env bash
# .claude/hooks/protect-files.sh
# 保护敏感文件，exit 2 = block
set -euo pipefail

file=$(jq -r '.tool_input.file_path // .tool_input.path // ""' 2>/dev/null || echo "")

protected=(
  ".*\.env.*"
  ".*\.key$"
  ".*\.pem$"
  ".*secrets/.*"
  ".*openclaw\.json$"
  ".*task-board\.json$"
  ".*SOUL\.md$"
  ".*IDENTITY\.md$"
  ".*AGENTS\.md$"
  ".*memory/10_项目/.*"
  ".*memory/01_强制规则/.*"
)

for pattern in "${protected[@]}"; do
  if echo "$file" | grep -qE "$pattern"; then
    echo "🛡️ [fs_guard] Blocked: '$file' is protected. Explain why this edit is necessary and get approval first." >&2
    exit 2
  fi
done
exit 0
