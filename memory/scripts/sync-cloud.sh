#!/bin/bash
# iCloud 同步脚本 v5.0 - 简化备份策略
# 只保留：滚动备份 + 每周快照 + 每月快照

set -e

WORKSPACE=/Users/apple/.openclaw/workspace
CLOUD=~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw_Memory
BACKUP_DIR="$CLOUD/黄金备份"

# 确保目标目录存在
mkdir -p "$BACKUP_DIR"/{rolling,weekly,monthly}

# 1. 滚动备份（实时覆盖）
echo "📦 滚动备份..."
rm -rf "$BACKUP_DIR/rolling/memory"
rsync -a --delete \
  --exclude-from="$WORKSPACE/.rsync-exclude" \
  "$WORKSPACE/memory/" "$BACKUP_DIR/rolling/memory/"

# 2. 每周快照（每周一执行）
if [ "$(date +%u)" = "1" ]; then
    echo "📅 每周快照..."
    WEEK_TAG=$(date +%Y-W%V)
    rm -rf "$BACKUP_DIR/weekly/memory"
    rsync -a "$BACKUP_DIR/rolling/memory/" "$BACKUP_DIR/weekly/memory/"
    echo "$WEEK_TAG" > "$BACKUP_DIR/weekly/snapshot.txt"
fi

# 3. 每月快照（每月1号执行）
if [ "$(date +%d)" = "01" ]; then
    echo "📅 每月快照..."
    MONTH_TAG=$(date +%Y-%m)
    rm -rf "$BACKUP_DIR/monthly/memory"
    rsync -a "$BACKUP_DIR/rolling/memory/" "$BACKUP_DIR/monthly/memory/"
    echo "$MONTH_TAG" > "$BACKUP_DIR/monthly/snapshot.txt"
fi

echo "✅ iCloud 同步完成 $(date '+%Y-%m-%d %H:%M:%S')"
