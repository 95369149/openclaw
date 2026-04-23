#!/bin/bash
# OpenClaw Gateway 健康监控脚本
# 每 5 分钟检查一次，崩溃自动重启

LOG="/tmp/gateway-watchdog.log"

while true; do
    # 检查 Gateway 是否在运行
    if ! pgrep -f "openclaw-gateway" > /dev/null; then
        echo "[$(date)] ⚠️  Gateway 未运行，尝试重启..." >> "$LOG"
        
        # 尝试通过 launchd 重启
        launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway 2>&1 >> "$LOG"
        
        sleep 10
        
        # 验证是否启动成功
        if pgrep -f "openclaw-gateway" > /dev/null; then
            echo "[$(date)] ✅ Gateway 重启成功" >> "$LOG"
        else
            echo "[$(date)] ❌ Gateway 重启失败" >> "$LOG"
        fi
    fi
    
    # 每 5 分钟检查一次
    sleep 300
done
