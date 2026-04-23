#!/bin/bash
# 主动扫描待办脚本
# 用途：cron 每日 09:00 调用，扫描未完成事项并输出提醒

TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
TASK_BOARD="$MEMORY_DIR/task-board.json"
LOG_DIR="$MEMORY_DIR/05_日常日志"
ALERT=""

# 1. 扫描 task-board 中的 blocked 任务
if [ -f "$TASK_BOARD" ]; then
  BLOCKED=$(python3 -c "
import json
d=json.load(open('$TASK_BOARD'))
for t in d.get('blockedTasks',[]):
    print(f\"  🔒 {t.get('id','?')}: {t.get('title','?')} — {t.get('blockReason','未知原因')}\")
" 2>/dev/null)
  if [ -n "$BLOCKED" ]; then
    ALERT="${ALERT}📋 阻塞任务:\n${BLOCKED}\n\n"
  fi
fi

# 2. 扫描昨天日志中的"待完成"/"⏳"/"TODO"
for LOG_FILE in "$LOG_DIR/$YESTERDAY.md" "$LOG_DIR/$TODAY.md"; do
  if [ -f "$LOG_FILE" ]; then
    TODOS=$(grep -n '⏳\|待完成\|TODO\|待办\|未完成' "$LOG_FILE" 2>/dev/null | head -10)
    if [ -n "$TODOS" ]; then
      FNAME=$(basename "$LOG_FILE")
      ALERT="${ALERT}📝 ${FNAME} 中的待办:\n${TODOS}\n\n"
    fi
  fi
done

# 3. 扫描 pending_approval
PENDING="$MEMORY_DIR/01_强制规则/pending_approval.json"
if [ -f "$PENDING" ]; then
  PENDING_ITEMS=$(python3 -c "
import json
d=json.load(open('$PENDING'))
for p in d.get('pending',[]):
    print(f\"  ⏰ {p.get('action','?')}: {p.get('description','?')}\")
" 2>/dev/null)
  if [ -n "$PENDING_ITEMS" ]; then
    ALERT="${ALERT}🔐 待审批:\n${PENDING_ITEMS}\n\n"
  fi
fi

# 4. 输出
if [ -n "$ALERT" ]; then
  echo -e "🔍 待办扫描 $(date '+%Y-%m-%d %H:%M'):\n\n${ALERT}"
  exit 1
else
  echo "✅ 无待办事项"
  exit 0
fi
