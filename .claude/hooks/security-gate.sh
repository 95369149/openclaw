#!/bin/bash
# block-dangerous-bash.sh
# 拦截危险 Bash 命令：rm -rf / curl|sh / sudo

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# 空命令直接放行
[ -z "$CMD" ] && exit 0

# ── Rule 1: rm -rf (支持 -rf / -fr / -r -f 等变体) ────────────────
if echo "$CMD" | grep -qE '(^|[;&|`\s])rm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+|-r\s+-f|-f\s+-r)'; then
  echo "BLOCKED [security]: 'rm -rf' variant detected." >&2
  echo "Command: $CMD" >&2
  exit 2
fi

# ── Rule 2: curl * | sh / bash (远程代码执行) ──────────────────────
if echo "$CMD" | grep -qE 'curl\s[^|#]+\|\s*(ba)?sh(\s|$)'; then
  echo "BLOCKED [security]: Remote code execution via 'curl | sh' detected." >&2
  echo "Command: $CMD" >&2
  exit 2
fi

# wget 变体也一并拦截
if echo "$CMD" | grep -qE 'wget\s[^|#]+\|\s*(ba)?sh(\s|$)'; then
  echo "BLOCKED [security]: Remote code execution via 'wget | sh' detected." >&2
  echo "Command: $CMD" >&2
  exit 2
fi

# ── Rule 3: sudo ──────────────────────────────────────────────────
if echo "$CMD" | grep -qE '(^|[;&|`\s])sudo\s'; then
  echo "BLOCKED [security]: 'sudo' is not allowed in this project." >&2
  echo "Command: $CMD" >&2
  exit 2
fi

exit 0
