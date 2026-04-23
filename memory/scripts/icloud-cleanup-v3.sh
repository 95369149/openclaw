#!/bin/bash
# iCloud 套娃清理脚本 v3.0
# 清理旧的 latest/weekly/monthly 结构，只保留 rolling/weekly/monthly

set -e

CLOUD=~/Library/Mobile\ Documents/com~apple~CloudDocs/OpenClaw_Memory

echo "🔍 清理 iCloud 套娃和旧备份结构..."

# 1. 删除旧的备份目录（latest）
if [ -d "$CLOUD/黄金备份/latest" ]; then
    echo "🗑 删除旧备份: latest"
    rm -rf "$CLOUD/黄金备份/latest"
fi

# 2. 删除所有带数字后缀的重复目录
echo "清理重复目录（* 2, * 3, * 4...）"
find "$CLOUD" -type d \( -name "* 2" -o -name "* 3" -o -name "* 4" -o -name "* 5" \) -print0 2>/dev/null | while IFS= read -r -d '' dir; do
    echo "🗑 删除: $dir"
    rm -rf "$dir"
done

# 3. 删除递归嵌套的黄金备份
echo "清理递归嵌套..."
find "$CLOUD/黄金备份" -mindepth 2 -type d -name "黄金备份" -print0 2>/dev/null | while IFS= read -r -d '' dir; do
    echo "🗑 删除嵌套: $dir"
    rm -rf "$dir"
done

# 4. 删除agents目录下的memory子目录（不应该存在）
if [ -d "$CLOUD/agents" ]; then
    find "$CLOUD/agents" -type d -name "memory" -print0 2>/dev/null | while IFS= read -r -d '' dir; do
        echo "🗑 删除agents下的memory: $dir"
        rm -rf "$dir"
    done
fi

# 5. 删除根目录下不应该存在的目录（只保留agents和黄金备份）
echo "清理根目录垃圾..."
for item in "$CLOUD"/*; do
    basename=$(basename "$item")
    if [ "$basename" != "agents" ] && [ "$basename" != "黄金备份" ] && [ "$basename" != ".DS_Store" ]; then
        echo "🗑 删除根目录垃圾: $item"
        rm -rf "$item"
    fi
done

# 6. 确保新的备份结构存在
mkdir -p "$CLOUD/黄金备份"/{rolling,weekly,monthly}

echo "✅ iCloud 清理完成"
echo ""
echo "当前结构："
ls -la "$CLOUD/" 2>/dev/null | grep -v "^total" | grep -v "^\."
echo ""
echo "黄金备份结构："
ls -la "$CLOUD/黄金备份/" 2>/dev/null | grep -v "^total" | grep -v "^\."
