#!/usr/bin/env bash
# .claude/hooks/log-commands.sh
# 记录所有执行过的命令到 logs/claude-commands.log
set -euo pipefail

cmd=$(jq -r '.tool_input.command // ""' 2>/dev/null || echo "")
timestamp=$(date +"%Y-%m-%dT%H:%M:%S")
log_file="/Users/apple/.openclaw/workspace/logs/claude-commands.log"

mkdir -p "$(dirname "$log_file")"
echo "$timestamp | $cmd" >> "$log_file"
exit 0
