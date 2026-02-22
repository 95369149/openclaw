#!/usr/bin/env bash
# Kitt 急救脚本 — 厂长专用
# 用途：Kitt 失联时，SSH 到 Mac 执行此脚本一键恢复
# 用法：bash kitt-rescue.sh [reset-model]
#
# 无参数：重启 Gateway
# reset-model：重置模型到默认 fallback 链（解决 403/限流卡死）

set -euo pipefail

OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
CONFIG="$OPENCLAW_HOME/openclaw.json"
LOG="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; }

# --- 1. 诊断 ---
echo "=== Kitt 急救 ==="
echo ""

# 检查 Gateway 进程
GW_PID=$(pgrep -f "openclaw-gateway" 2>/dev/null || true)
if [ -n "$GW_PID" ]; then
  info "Gateway 进程存在 (PID: $GW_PID)"
else
  warn "Gateway 进程不存在"
fi

# 检查端口
PORT_CHECK=$(lsof -i :18789 -t 2>/dev/null || true)
if [ -n "$PORT_CHECK" ]; then
  info "端口 18789 被占用 (PID: $PORT_CHECK)"
else
  warn "端口 18789 空闲"
fi

# 最近错误
if [ -f "$LOG" ]; then
  RECENT_ERRORS=$(grep -c '"logLevelName":"ERROR"' "$LOG" 2>/dev/null || echo "0")
  LAST_ERROR=$(grep '"logLevelName":"ERROR"' "$LOG" 2>/dev/null | tail -1 | python3 -c "
import sys,json
try:
  obj=json.loads(sys.stdin.read().strip())
  print(obj.get('time','?'), obj.get('1','')[:100] if isinstance(obj.get('1'),str) else str(obj.get('1',''))[:100])
except: print('无法解析')
" 2>/dev/null || echo "无日志")
  echo "  今日错误数: $RECENT_ERRORS"
  echo "  最近错误: $LAST_ERROR"
fi

echo ""

# --- 2. 重置模型（可选）---
if [ "${1:-}" = "reset-model" ]; then
  warn "重置模型配置到安全 fallback 链..."
  python3 -c "
import json
with open('$CONFIG') as f:
    cfg = json.load(f)
cfg.setdefault('agents', {}).setdefault('defaults', {})['model'] = {
    'primary': 'mynewapi/claude-opus-4-6',
    'fallbacks': [
        'google-gemini/gemini-2.5-flash',
        'siliconflow/deepseek-ai/DeepSeek-V3.2',
        'groq/llama-3.3-70b-versatile',
        'siliconflow/Qwen/Qwen3-32B',
        'groq/qwen/qwen3-32b',
        'mynewapi/claude-sonnet-4-6'
    ]
}
with open('$CONFIG', 'w') as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
  "
  info "模型配置已重置"
fi

# --- 3. 杀掉所有残留进程 ---
warn "清理残留进程..."
pkill -9 -f "openclaw-gateway" 2>/dev/null && info "已杀掉旧 Gateway" || info "无残留 Gateway"
pkill -9 -f "kilo" 2>/dev/null && info "已杀掉 kilo 进程" || true
sleep 2

# 确认端口释放
for i in 1 2 3; do
  if lsof -i :18789 -t >/dev/null 2>&1; then
    warn "端口仍被占用，等待... ($i/3)"
    sleep 2
  else
    break
  fi
done

# --- 4. 重启 Gateway ---
info "启动 Gateway..."
if command -v openclaw >/dev/null 2>&1; then
  openclaw gateway start 2>&1 || {
    warn "openclaw gateway start 失败，尝试直接启动..."
    nohup openclaw gateway run --bind loopback --port 18789 --force > /tmp/openclaw-gateway.log 2>&1 &
    sleep 3
  }
else
  error "openclaw 命令不存在！请先安装: npm i -g openclaw"
  exit 1
fi

# --- 5. 验证 ---
sleep 5
NEW_PID=$(pgrep -f "openclaw-gateway" 2>/dev/null || true)
if [ -n "$NEW_PID" ]; then
  info "Gateway 已恢复 (PID: $NEW_PID)"
else
  error "Gateway 启动失败，查看日志: tail -50 $LOG"
  exit 1
fi

# 检查通道
if command -v openclaw >/dev/null 2>&1; then
  echo ""
  openclaw channels status --probe 2>&1 || true
fi

echo ""
info "急救完成。Kitt 应该已经恢复在线。"
echo "  如果仍然失联，查看日志: tail -100 $LOG"
