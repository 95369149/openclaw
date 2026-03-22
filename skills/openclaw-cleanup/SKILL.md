---
name: openclaw-cleanup
description: Safely inspect and clean OpenClaw junk files, caches, old logs, temporary workspaces, and optional bulky directories. Use when the user asks to clean storage, free disk space, prune old OpenClaw files, or set up periodic cleanup via cron.
---

# OpenClaw Cleanup

用于清理 OpenClaw 运行过程中积累的缓存、旧日志、临时目录和废弃工作区。

## 何时使用

- 用户说“清理 OpenClaw 占用空间”
- 用户说“删掉没用的缓存/日志/临时文件”
- 用户说“定期自动清理”
- 用户说“看看哪些目录最占空间”

## 安全规则

- **先 dry-run，再 apply**。不要一上来就删。
- **默认只清高把握垃圾**：浏览器缓存、旧日志、kitt 临时目录。
- **以下路径严禁删**：
  - `~/.openclaw/credentials`
  - `~/.openclaw/openclaw.json`
  - `~/.openclaw/.env`
  - `~/.openclaw/workspace/memory`
  - `~/.openclaw/agents`
  - `~/.openclaw/cron`
- `workspace/node_modules`、`MediaCrawler`、旧媒体文件属于**可选项**，删前要明确告诉用户。

## 脚本

使用脚本：`scripts/cleanup.py`

### 1) 看默认可清内容（dry-run）

```bash
python3 /Users/apple/.openclaw/workspace/skills/openclaw-cleanup/scripts/cleanup.py --defaults
```

### 2) 看默认可清内容（JSON）

```bash
python3 /Users/apple/.openclaw/workspace/skills/openclaw-cleanup/scripts/cleanup.py --defaults --json
```

### 3) 真删默认安全项

```bash
python3 /Users/apple/.openclaw/workspace/skills/openclaw-cleanup/scripts/cleanup.py --defaults --apply
```

### 4) 加上可选大目录

```bash
python3 /Users/apple/.openclaw/workspace/skills/openclaw-cleanup/scripts/cleanup.py \
  --include browser-cache \
  --include workspace-kitt-projects \
  --include workspace-kitt-tmp \
  --include logs-old \
  --include workspace-node-modules \
  --include mediacrawler
```

## 可用 key

- `browser-cache`
- `workspace-kitt-projects`
- `workspace-kitt-tmp`
- `logs-old`
- `media-old`
- `workspace-node-modules`
- `mediacrawler`

## 定期清理建议

优先每周跑一次默认安全项：

- 浏览器缓存
- 14 天前日志
- kitt 临时目录

如果用户确认不再用某个历史项目，再把它加入 cron。

## 输出要求

汇报时用结果式：

- 哪些目录可清
- 预计释放多少空间
- 哪些已经删
- 哪些因为安全原因没动
