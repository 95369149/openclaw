# 语义记忆：PPT 生成方案

## 核心方案：Reveal.js Skill

- **来源**：memory/收藏/2026-02-18-RevealJS-Skill.md
- **仓库**：github.com/ryanbbrown/revealjs-skill
- **原理**：LLM 生成 Reveal.js (HTML/JS) 代码，浏览器直接渲染为幻灯片。
- **状态**：待移植（原为 Claude Code skill）。

## 备选方案

### 1. Markdown to Slide (Marp)

- 使用 VSCode Marp 插件，将 Markdown 转为 PPT/PDF。
- 优点：格式通用，不仅限于 Skill。
- Kitt 可直接生成符合 Marp 语法的 Markdown。

### 2. Gamma / Tome (在线工具)

- 优点：排版精美，模板多。
- 缺点：需要登录，不易通过 API 自动化。

## 触发场景

当用户指令包含：

- "做个 PPT"
- "生成演示文稿"
- "准备个胶片"
- "Slide" / "Deck"

## 执行策略

优先尝试 **Reveal.js Skill**（如果已移植成功），其次使用 **Marp 格式 Markdown** 输出。
