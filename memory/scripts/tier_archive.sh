#!/bin/bash
# 热数据/冷数据自动归档脚本 v1.0
# 用途：每天自动将旧数据归档到 warm/ 和 cold/
# 执行：bash memory/scripts/tier_archive.sh

set -e

MEMORY_ROOT="/Users/apple/.openclaw/workspace/memory"
NOW=$(date +%s)
SEVEN_DAYS_AGO=$((NOW - 7 * 86400))
THIRTY_DAYS_AGO=$((NOW - 30 * 86400))

echo "=== 热数据/冷数据归档开始 ==="
echo "时间：$(date '+%Y-%m-%d %H:%M:%S')"

# 归档 7 天前的日志到 warm/
echo ""
echo "📦 归档 7 天前的日志到 warm/..."
for file in "$MEMORY_ROOT"/*.md; do
    [ -f "$file" ] || continue
    filename=$(basename "$file")
    
    # 跳过特殊文件
    if [[ "$filename" == ".abstract" ]] || [[ "$filename" == "MEMORY.md" ]]; then
        continue
    fi
    
    # 检查文件修改时间
    if [[ "$OSTYPE" == "darwin"* ]]; then
        file_time=$(stat -f %m "$file")
    else
        file_time=$(stat -c %Y "$file")
    fi
    
    if [ "$file_time" -lt "$SEVEN_DAYS_AGO" ]; then
        # 提取年月
        year_month=$(echo "$filename" | grep -oE '202[0-9]-[0-9]{2}' | head -1)
        if [ -n "$year_month" ]; then
            target_dir="$MEMORY_ROOT/warm/$year_month"
            mkdir -p "$target_dir"
            mv "$file" "$target_dir/"
            echo "  ✓ $filename → warm/$year_month/"
        fi
    fi
done

# 归档 7 天前的 shared/ 文件到 warm/
echo ""
echo "📦 归档 7 天前的 shared/ 文件到 warm/..."
if [ -d "$MEMORY_ROOT/shared" ]; then
    for file in "$MEMORY_ROOT/shared"/*.md; do
        [ -f "$file" ] || continue
        filename=$(basename "$file")
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            file_time=$(stat -f %m "$file")
        else
            file_time=$(stat -c %Y "$file")
        fi
        
        if [ "$file_time" -lt "$SEVEN_DAYS_AGO" ]; then
            year_month=$(echo "$filename" | grep -oE '202[0-9]-[0-9]{2}' | head -1)
            if [ -n "$year_month" ]; then
                target_dir="$MEMORY_ROOT/warm/$year_month/shared"
                mkdir -p "$target_dir"
                mv "$file" "$target_dir/"
                echo "  ✓ $filename → warm/$year_month/shared/"
            fi
        fi
    done
fi

# 归档 30 天前的 warm/ 文件到 cold/
echo ""
echo "🧊 归档 30 天前的 warm/ 文件到 cold/..."
if [ -d "$MEMORY_ROOT/warm" ]; then
    for year_month_dir in "$MEMORY_ROOT/warm"/*; do
        [ -d "$year_month_dir" ] || continue
        year_month=$(basename "$year_month_dir")
        
        # 检查目录中最新文件的时间
        latest_file=$(find "$year_month_dir" -type f -name "*.md" -print0 | xargs -0 stat -f %m 2>/dev/null | sort -n | tail -1)
        
        if [ -n "$latest_file" ] && [ "$latest_file" -lt "$THIRTY_DAYS_AGO" ]; then
            target_dir="$MEMORY_ROOT/cold/$year_month"
            mkdir -p "$target_dir"
            mv "$year_month_dir"/* "$target_dir/" 2>/dev/null || true
            rmdir "$year_month_dir" 2>/dev/null || true
            echo "  ✓ warm/$year_month/ → cold/$year_month/"
        fi
    done
fi

# 统计
echo ""
echo "=== 归档完成 ==="
echo "hot/ 文件数：$(find "$MEMORY_ROOT" -maxdepth 1 -name "*.md" | wc -l | tr -d ' ')"
echo "warm/ 文件数：$(find "$MEMORY_ROOT/warm" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
echo "cold/ 文件数：$(find "$MEMORY_ROOT/cold" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')"
