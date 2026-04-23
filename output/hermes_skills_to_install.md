# Hermes 需要安装的 Skills 清单

> 来源：Mac/Kitt 近期常用功能整理
> 时间：2026-04-12
> 用途：Hermes 端自行安装，与 Mac 侧功能对齐

---

## 一、核心必装（日常高频）

| Skill | 功能 | 安装来源 |
|-------|------|---------|
| `x-reader` | 读取 X/Twitter 链接，自动解读内容 | `~/.openclaw/skills/x-reader/` |
| `x-writer` | 发布/草拟 X 推文 | `~/.openclaw/skills/x-writer/` |
| `github` | GitHub 仓库操作、PR、Issues | clawhub |
| `gh-issues` | GitHub Issues 管理 | clawhub |
| `weather` | 天气查询 | clawhub |
| `coding-agent` | 代码生成与调试 | `workspace/skills/coding-agent/` |
| `screenshot` | 截图与页面快照 | clawhub |

---

## 二、文档处理（常用）

| Skill | 功能 | 安装来源 |
|-------|------|---------|
| `docx` | 读写 Word 文档 | `workspace/skills/docx/` |
| `xlsx` | 读写 Excel 文档 | `workspace/skills/xlsx/` |
| `pdf` | PDF 解析与提取 | clawhub |
| `biz-reporter` | 商业报告生成 | `workspace/skills/biz-reporter/` |

---

## 三、内容生成（按需）

| Skill | 功能 | 安装来源 |
|-------|------|---------|
| `imagegen` | AI 图片生成 | clawhub |
| `video-factory` | 视频生成与处理 | `workspace/skills/video-factory/` |
| `slides` | PPT/幻灯片生成 | clawhub |
| `baoyu-translate` | 多语言翻译 | clawhub |
| `baoyu-url-to-markdown` | 网页转 Markdown | clawhub |

---

## 四、浏览器与搜索

| Skill | 功能 | 安装来源 |
|-------|------|---------|
| `agent-browser` | 轻量浏览器操作（主刀）| `workspace/skills/agent-browser/` |
| `defuddle` | 网页内容提取 | clawhub |
| `yt-search-download` | YouTube 搜索下载 | clawhub |
| `bibi` | B站视频处理 | clawhub |

---

## 五、talk-normal（回答风格规则）

直接把以下内容加入 Hermes 的 `AGENTS.md` 或 system prompt：

```
Be direct and informative. No filler, no fluff, but give enough to be useful.

- Lead with the answer, then add context only if it genuinely helps
- Kill all filler: "I'd be happy to", "Great question", "Certainly", "Of course", "首先我们需要", "值得注意的是", "综上所述"
- Never restate the question
- Yes/no questions: answer first, one sentence of reasoning
- Explanations: 3-5 sentences max
- Do not end with hypothetical follow-up offers
- Do not use summary-stamp closings: "一句话总结", "总结一下", "简而言之", "In conclusion"
- Prefer direct positive claims. Avoid "不是X，而是Y" — just state the positive claim directly
```

---

## 六、bridge 仓库同步（必须）

```bash
git clone https://github.com/95369149/hty-hermes-bridge.git C:\hermes-bridge
cd C:\hermes-bridge
git pull
```

任务流程：
- `inbox/` → 放入待处理任务
- `done/` → 处理结果写回
- `knowledge/aftersales/` → 售后知识库（3623条原始记录已在里面）
- `TASK_README.md` → 清洗任务说明书

---

## 七、ENV 配置

所有 API key 已在 `hermes_.env` 里，直接复制到 Hermes 的 `.env` 文件。
