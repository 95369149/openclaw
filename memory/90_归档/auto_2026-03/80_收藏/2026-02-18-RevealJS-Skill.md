# 2026-02-18 Reveal.js Skill (告别 PPT)

## 来源

- Author: @QingQ77
- Date: 2026-02-18
- Link: https://x.com/qingq77/status/2023947577285374155
- GitHub: https://github.com/ryanbbrown/revealjs-skill

## 核心功能

一个 Claude Code skill，利用 Reveal.js 框架，让 AI 直接生成网页版演示文稿 (Slides)。

### 使用场景

用户只需输入自然语言指令：

- "制作一份关于可再生能源趋势的10页幻灯片"
- "为 SaaS 初创公司制作 Pitch Deck"
- "生成季度复盘 PPT"

### 价值

- **Text-to-Slide**：从文本直接生成结构化的演示代码。
- **无需 PPT**：生成的 HTML 文件可直接在浏览器播放，支持 markdown 语法。
- **自动化**：结合 OpenClaw 的搜索/总结能力，可以实现"搜索资料 -> 总结 -> 生成 PPT"的全自动流。

## Kitt 思考

- **移植计划**：这原本是为 Claude Code 设计的，但 OpenClaw 理论上也能跑。需要检查其实现方式（是简单的 prompt 还是复杂的工具调用），尝试移植到我们的 `skills/` 目录。
- **演示场景**：下次汇报工作（如 Kitt 进化日志）时，可以试着用这个生成一份 Slide。

<!-- digested: 2026-02-21 -->
