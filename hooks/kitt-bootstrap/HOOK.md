---
name: kitt-bootstrap
description: "新 session / 模型切换后强制读取记忆，防止失忆"
metadata:
  { "openclaw": { "emoji": "🧠", "events": ["agent:bootstrap"], "requires": { "bins": ["python3"] } } }
---

# Kitt Bootstrap

每次 agent:bootstrap 事件触发时，自动执行 memory bootstrap，
确保 .abstract / task-board / shared 已注入上下文。
