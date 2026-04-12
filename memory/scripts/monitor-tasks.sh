#!/bin/bash
# 确定性任务监控脚本 — 不用 AI，纯 bash
# 用途：cron 调用，检查 subagent 和任务状态，只在异常时输出
# 灵感来源：Elvis @elvissun 的 Agent Swarm 监控方案

TASK_BOARD="$HOME/.openclaw/workspace/memory/task-board.json"
LOG_DIR="$HOME/.openclaw/workspace/memory/05_日常日志"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%s)
ALERT=""

# 1. 检查 task-board.json 是否存在
if [ ! -f "$TASK_BOARD" ]; then
  echo "⚠️ task-board.json 不存在"
  exit 1
fi

# 2. 检查活跃任务是否超时（>30分钟）
ACTIVE_COUNT=$(python3 -c "
import json,sys
try:
    d=json.load(open('$TASK_BOARD'))
    tasks=d.get('activeTasks',[])
    print(len(tasks))
except: print(0)
" 2>/dev/null)

if [ "$ACTIVE_COUNT" -gt 0 ]; then
  TIMEOUT_TASKS=$(python3 -c "
import json,time
d=json.load(open('$TASK_BOARD'))
now=time.time()
for t in d.get('activeTasks',[]):
    started=t.get('startedAt','')
    if started:
        # ISO format to timestamp
        import datetime
        try:
            dt=datetime.datetime.fromisoformat(started.replace('Z','+00:00'))
            elapsed=(now-dt.timestamp())/60
            if elapsed>30:
                print(f\"⏰ 任务 {t.get('id','?')} 已运行 {int(elapsed)} 分钟: {t.get('name','?')}\")
        except: pass
" 2>/dev/null)
  if [ -n "$TIMEOUT_TASKS" ]; then
    ALERT="${ALERT}${TIMEOUT_TASKS}\n"
  fi
fi

# 3. 检查 Gateway 状态
GW_STATUS=$(openclaw gateway status 2>&1)
if echo "$GW_STATUS" | grep -qi "not running\|error\|failed"; then
  ALERT="${ALERT}🔴 Gateway 异常: ${GW_STATUS}\n"
fi

# 4. 检查待审批项（pending_approval.json）
PENDING="$HOME/.openclaw/workspace/memory/01_强制规则/pending_approval.json"
if [ -f "$PENDING" ]; then
  PENDING_COUNT=$(python3 -c "
import json
d=json.load(open('$PENDING'))
items=d.get('pending',[])
if items: print(len(items))
else: print(0)
" 2>/dev/null)
  if [ "$PENDING_COUNT" -gt 0 ]; then
    ALERT="${ALERT}📋 有 ${PENDING_COUNT} 项待审批\n"
  fi
fi

# 5. 输出结果
if [ -n "$ALERT" ]; then
  echo -e "🚨 监控告警 $(date '+%H:%M'):\n${ALERT}"
  exit 2  # 非零退出码表示有告警
else
  exit 0  # 静默退出，一切正常
fi
