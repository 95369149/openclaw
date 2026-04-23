#!/bin/bash
# check-subagents.sh - 监控子 agent 状态，自动重试失败任务
# 用法: ./check-subagents.sh
# 建议: 每 10 分钟 cron 执行一次

set -euo pipefail

WORKSPACE="/Users/apple/.openclaw/workspace"
TASK_BOARD="$WORKSPACE/memory/task-board.json"
TEMP_BOARD="/tmp/task-board-update.json"

cd "$WORKSPACE"

# 检查 task-board.json 是否存在
if [[ ! -f "$TASK_BOARD" ]]; then
  echo "❌ task-board.json 不存在"
  exit 1
fi

# 读取活跃任务
ACTIVE_TASKS=$(jq -r '.activeTasks[] | @json' "$TASK_BOARD")

if [[ -z "$ACTIVE_TASKS" ]]; then
  echo "✅ 没有活跃任务"
  exit 0
fi

NEEDS_NOTIFICATION=false
NOTIFICATION_MSG=""

# 遍历每个活跃任务
while IFS= read -r task; do
  TASK_ID=$(echo "$task" | jq -r '.id')
  SESSION_KEY=$(echo "$task" | jq -r '.sessionKey')
  AGENT=$(echo "$task" | jq -r '.agent')
  TITLE=$(echo "$task" | jq -r '.title')
  RETRIES=$(echo "$task" | jq -r '.retries')
  MAX_RETRIES=$(echo "$task" | jq -r '.maxRetries')
  
  echo "🔍 检查任务 #$TASK_ID: $TITLE"
  
  # 通过 openclaw sessions list 检查 session 状态
  # 注意: 这里需要 OpenClaw 提供 sessions list 的 JSON 输出
  # 如果没有，可以用 subagents list 替代
  
  # 简化版: 检查任务是否超时（超过 30 分钟）
  STARTED_AT=$(echo "$task" | jq -r '.startedAt')
  STARTED_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S%z" "$STARTED_AT" +%s 2>/dev/null || echo 0)
  NOW_TS=$(date +%s)
  ELAPSED=$((NOW_TS - STARTED_TS))
  
  if [[ $ELAPSED -gt 1800 ]]; then
    echo "⚠️  任务 #$TASK_ID 运行超过 30 分钟"
    
    if [[ $RETRIES -lt $MAX_RETRIES ]]; then
      echo "🔄 准备重试（第 $((RETRIES + 1)) 次）"
      NEEDS_NOTIFICATION=true
      NOTIFICATION_MSG="${NOTIFICATION_MSG}任务 #$TASK_ID 超时，准备重试\n"
      
      # 这里应该调用 OpenClaw 重新派发任务
      # 暂时只记录，不自动重试（需要人工确认）
    else
      echo "❌ 任务 #$TASK_ID 已达到最大重试次数"
      NEEDS_NOTIFICATION=true
      NOTIFICATION_MSG="${NOTIFICATION_MSG}任务 #$TASK_ID 失败（已重试 $MAX_RETRIES 次）\n"
    fi
  fi
  
done <<< "$ACTIVE_TASKS"

# 如果需要通知，输出到 stdout（可以被 cron 捕获并发送到 Telegram）
if [[ "$NEEDS_NOTIFICATION" == true ]]; then
  echo -e "\n📢 需要人工介入:\n$NOTIFICATION_MSG"
  exit 2
fi

echo "✅ 所有任务正常运行"
exit 0
