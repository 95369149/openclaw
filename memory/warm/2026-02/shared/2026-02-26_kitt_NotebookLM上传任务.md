# 任务：上传文件到 NotebookLM

厂长要求用浏览器自动化上传以下文件到 Google NotebookLM：

1. `memory/02_知识库/实战提示词系统v2.md`
2. `memory/02_知识库/实战提示词系统v3_补充.md`
3. `memory/00_数字分身.md`（v2.4）

**问题：**
- Kitt 没有 browser 工具权限（只有 jimmy 有）
- Kitt 没有 sessions_spawn 权限（不能派 jimmy）

**解决方案：**
需要 jimmy 来执行这个任务。

**给 jimmy 的指令：**
```
任务：用 browser 工具上传3个文件到 NotebookLM

1. 打开 https://notebooklm.google.com
2. 登录（如果需要）
3. 创建新笔记本，命名"红太阳提示词系统+数字分身"
4. 上传文件：
   - /Users/apple/.openclaw/workspace/memory/02_知识库/实战提示词系统v2.md
   - /Users/apple/.openclaw/workspace/memory/02_知识库/实战提示词系统v3_补充.md
   - /Users/apple/.openclaw/workspace/memory/00_数字分身.md
5. 完成后截图确认

注意：
- NotebookLM 可能需要 Google 账号登录
- 上传可能需要点击"Add source" → "Upload" → 选择文件
- 如果浏览器自动化失败，告诉厂长需要手动上传
```

**状态：** 等待 jimmy 执行
