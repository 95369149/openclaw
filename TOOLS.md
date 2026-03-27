# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### 浏览器工具选择铁律（2026-03-27 厂长拍板）

**优先级链（命中即停）：**

1. API / CLI 原生工具（零浏览器开销）
2. **agent-browser**（主刀 🔪）
3. OpenClaw browser evaluate（仅当页面已打开时）
4. browser-use（二期）
5. 手动操作（最后手段）

❌ 禁止跳过 agent-browser 直接用 web_fetch / browser snapshot
❌ 禁止 agent-browser 没启动就绕道，应先启动再用
❌ 禁止手搓低效方案当主链路

### agent-browser（主刀 · v0.15.2）

- **Executable**: `agent-browser`（全局 npm）
- **Skill Path**: `~/.openclaw/workspace/skills/agent-browser/SKILL.md`
- **核心优势**: Token 省 95%（~200 vs ~8000/页），Rust CLI <0.5s
- **Usage**:
  - `agent-browser open <url>` → 打开页面
  - `agent-browser snapshot -i` → 可交互元素语义树（最省 token）
  - `agent-browser fill @e2 "text"` → 填表
  - `agent-browser click @e3` → 点击
  - `agent-browser get text @e1` → 提取文本
  - `agent-browser eval "JS表达式"` → 执行 JS
  - `agent-browser screenshot /tmp/x.png` → 截图
  - `agent-browser close` → 关闭

### PinchTab（备用 · 服务不稳定）

- **Executable**: `~/bin/pinchtab`
- **Server URL**: `http://127.0.0.1:9867`
- **Skill Path**: `~/.openclaw/workspace/skills/pinchtab/SKILL.md`
- **Usage**:
  - `~/bin/pinchtab nav <url>` (Navigate)
  - `~/bin/pinchtab snap -i -c` (Get interactive elements)
  - `~/bin/pinchtab click <ref>` (Click element)
  - `~/bin/pinchtab text` (Extract readable text, ~800 tokens)
