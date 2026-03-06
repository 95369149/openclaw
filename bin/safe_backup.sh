#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <file>" >&2
  exit 1
fi

TARGET="$1"
if [ ! -f "$TARGET" ]; then
  echo "Target not found: $TARGET" >&2
  exit 2
fi

TS="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/Users/apple/.openclaw/workspace/memory/backup"
mkdir -p "$BACKUP_DIR"

BASE_NAME="$(basename "$TARGET")"
BACKUP_PATH="$BACKUP_DIR/${BASE_NAME}.${TS}.bak"
cp "$TARGET" "$BACKUP_PATH"

cat <<EOF
[OK] Backup created
Target: $TARGET
Backup: $BACKUP_PATH

One-line rollback:
cp "$BACKUP_PATH" "$TARGET"
EOF
