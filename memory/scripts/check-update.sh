#!/bin/bash
# OpenClaw 版本更新检查
# 有新版本时通过 Telegram 通知厂长

CURRENT=$(openclaw --version 2>/dev/null)
LATEST=$(npm view openclaw version 2>/dev/null)
STATE_FILE="/tmp/openclaw-version-notified"

if [ -z "$CURRENT" ] || [ -z "$LATEST" ]; then
    echo "❌ 无法获取版本信息"
    exit 1
fi

echo "当前: $CURRENT | 最新: $LATEST"

if [ "$CURRENT" = "$LATEST" ]; then
    echo "✅ 已是最新版本"
    rm -f "$STATE_FILE"
    exit 0
fi

# 检查上次通知时间，未更新则每小时通知一次
if [ -f "$STATE_FILE" ]; then
    LAST_NOTIFY=$(stat -f %m "$STATE_FILE" 2>/dev/null || stat -c %Y "$STATE_FILE" 2>/dev/null)
    NOW_TS=$(date +%s)
    DIFF=$(( NOW_TS - LAST_NOTIFY ))
    if [ "$DIFF" -lt 3600 ]; then
        echo "⏭️ 距上次通知不到1小时（${DIFF}s），跳过"
        exit 0
    fi
fi

# 新版本，记录并退出码 2 表示需要通知
echo "$LATEST" > "$STATE_FILE"
echo "🆕 发现新版本: $CURRENT → $LATEST"
exit 2
