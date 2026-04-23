---
name: kitt-preflight
description: "消息进入前执行任务分类 + 策略判断 + 项目保护检查"
metadata:
  { "openclaw": { "emoji": "🛡️", "events": ["message:received"], "requires": { "bins": ["python3"] } } }
---

# Kitt Preflight

每条入站消息触发时，执行：
1. task_classifier：分类任务类型
2. policy_engine：判断路由和审核链
3. fs_guard：如果涉及文件操作，检查项目保护
