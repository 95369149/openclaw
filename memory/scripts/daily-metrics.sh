#!/bin/bash
# 每日产出指标记录脚本
# 用途：每日 23:00 cron 调用，统计当天产出

TODAY=$(date +%Y-%m-%d)
LOG_DIR="$HOME/.openclaw/workspace/memory/05_日常日志"
METRICS_FILE="$HOME/.openclaw/workspace/memory/scripts/engine_data/daily_metrics.jsonl"

# 确保目录存在
mkdir -p "$(dirname "$METRICS_FILE")"

# 统计 session 文件中今天的 agent 调用
SESSION_DIR="$HOME/.openclaw/agents"
AGENT_CALLS=0
if [ -d "$SESSION_DIR" ]; then
  for agent_dir in "$SESSION_DIR"/*/sessions; do
    if [ -d "$agent_dir" ]; then
      count=$(find "$agent_dir" -name "*.jsonl" -newer /tmp/.metrics_marker 2>/dev/null | wc -l)
      AGENT_CALLS=$((AGENT_CALLS + count))
    fi
  done
fi

# 统计 memory 文件变更数
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
FILES_CHANGED=$(find "$MEMORY_DIR" -name "*.md" -newer /tmp/.metrics_marker 2>/dev/null | wc -l)

# 统计任务完成数（从 task-board.json）
TASK_BOARD="$HOME/.openclaw/workspace/memory/task-board.json"
TASKS_DONE=0
TASKS_FAILED=0
if [ -f "$TASK_BOARD" ]; then
  TASKS_DONE=$(python3 -c "
import json
d=json.load(open('$TASK_BOARD'))
print(len([t for t in d.get('completedTasks',[]) if t.get('completedAt','').startswith('$TODAY')]))" 2>/dev/null || echo 0)
  TASKS_FAILED=$(python3 -c "
import json
d=json.load(open('$TASK_BOARD'))
print(len([t for t in d.get('failedTasks',[]) if t.get('failedAt','').startswith('$TODAY')]))" 2>/dev/null || echo 0)
fi

# 写入 JSONL
echo "{\"date\":\"$TODAY\",\"tasks_done\":$TASKS_DONE,\"tasks_failed\":$TASKS_FAILED,\"files_changed\":$FILES_CHANGED,\"agent_calls\":$AGENT_CALLS}" >> "$METRICS_FILE"

# 输出摘要
echo "📊 $TODAY 产出指标："
echo "  任务完成: $TASKS_DONE | 失败: $TASKS_FAILED"
echo "  文件变更: $FILES_CHANGED"
echo "  Agent 调用: $AGENT_CALLS"
