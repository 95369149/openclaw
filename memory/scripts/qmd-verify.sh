#!/bin/bash
# 验证 QMD 记忆文件索引是否有效，并抽取刚写入的记忆
# 用途：记忆写入后的闭环校验

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <query>"
  exit 1
fi

QUERY="$1"
qmd search "$QUERY" --limit 3 || {
  echo "❌ 检索验证失败或未找到内容: $QUERY"
  exit 1
}
echo "✅ 检索验证成功"
