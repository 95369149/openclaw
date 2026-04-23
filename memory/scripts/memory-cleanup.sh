#!/bin/bash
# 记忆保质期清理脚本
# P0: 永不删 | P1: 30天归档 | P2: 7天清理
# 用途: cron 每周日执行

MEMORY_DIR="$HOME/.openclaw/workspace/memory"
ARCHIVE_DIR="$MEMORY_DIR/90_归档/auto_$(date +%Y-%m)"
TODAY=$(date +%s)
MOVED=0
CLEANED=0

# P1 目录: 30天后归档到 90_归档/
P1_DIRS=("05_日常日志" "07_版本控制" "03_语义记忆")
for dir in "${P1_DIRS[@]}"; do
  DIR_PATH="$MEMORY_DIR/$dir"
  [ ! -d "$DIR_PATH" ] && continue
  
  find "$DIR_PATH" -name "*.md" -type f -mtime +30 ! -name "README.md" ! -name "_INDEX.md" | while read f; do
    mkdir -p "$ARCHIVE_DIR/$dir"
    mv "$f" "$ARCHIVE_DIR/$dir/"
    MOVED=$((MOVED + 1))
    echo "📦 归档: $f"
  done
done

# P2 目录: 7天后清理（移到归档，不直接删）
P2_DIRS=("04_内容素材" "04_情景记忆" "80_收藏")
for dir in "${P2_DIRS[@]}"; do
  DIR_PATH="$MEMORY_DIR/$dir"
  [ ! -d "$DIR_PATH" ] && continue
  
  find "$DIR_PATH" -name "*.md" -type f -mtime +7 ! -name "README.md" ! -name "_INDEX.md" | while read f; do
    mkdir -p "$ARCHIVE_DIR/$dir"
    mv "$f" "$ARCHIVE_DIR/$dir/"
    CLEANED=$((CLEANED + 1))
    echo "🗑️ 清理: $f"
  done
done

# 清理空的归档子目录
find "$ARCHIVE_DIR" -type d -empty -delete 2>/dev/null

# 轮转本地临时 backup（四层保留位）
if [ -x "$MEMORY_DIR/scripts/backup-rotate.sh" ]; then
  echo "🔄 轮转本地 backup..."
  "$MEMORY_DIR/scripts/backup-rotate.sh" "$MEMORY_DIR/backup" || echo "⚠️ backup 轮转失败"
fi

# 更新 .abstract 的时间戳
touch "$MEMORY_DIR/.abstract"

# 汇报
if [ $MOVED -eq 0 ] && [ $CLEANED -eq 0 ]; then
  echo "✅ 记忆清理完成，无需处理"
else
  echo "📊 记忆清理: 归档 $MOVED 个 P1 文件, 清理 $CLEANED 个 P2 文件"
fi
