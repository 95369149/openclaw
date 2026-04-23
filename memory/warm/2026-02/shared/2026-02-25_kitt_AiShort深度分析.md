# AiShort (ChatGPT-Shortcut) 深度分析

**来源**: https://github.com/rockbenben/ChatGPT-Shortcut
**Stars**: 7997 | **语言**: TypeScript | **框架**: Docusaurus
**官网**: https://www.aishort.top/
**分析时间**: 2026-02-25

---

## 项目架构

- Docusaurus 静态站点 + React 前端
- 提示词数据：`src/data/cards/` 下 278 个 JSON 文件（按 ID 编号）
- 标签系统：`src/data/tags.tsx` 定义 25 个分类标签
- 多语言：18 种语言，`i18n/` 目录
- 数据处理：`CodeUpdateHandler.py` 负责提示词分割和多语言转换

## 提示词数据结构

```json
{
  "id": 1,
  "zh-Hans": {
    "title": "英语翻译/修改",
    "prompt": "I want you to act as...",
    "description": "描述说明",
    "remark": "简短备注"
  },
  "tags": ["language"],
  "website": "来源链接",
  "count": 使用次数
}
```

每个提示词包含：标题、完整 prompt、描述、备注、标签、来源、使用统计。

## 25 个标签分类

| 标签 | 中文名 | 与数控制造业相关度 |
|------|--------|------------------|
| write | 写作辅助 | ⭐⭐ 产品文案、技术文档 |
| article | 文章/报告 | ⭐⭐⭐ 行业报告、白皮书 |
| code | IT/编程 | ⭐⭐ 自动化脚本 |
| ai | AI | ⭐ |
| living | 生活质量 | - |
| interesting | 趣味科普 | - |
| life | 生活百科 | - |
| social | 心理/社交 | ⭐ 客户沟通 |
| philosophy | 哲学/宗教 | - |
| mind | 思维训练 | ⭐ 决策分析 |
| pedagogy | 教育/学生 | ⭐ 培训 |
| academic | 学术/教师 | ⭐ |
| games | 趣味游戏 | - |
| tool | 效率工具 | ⭐⭐⭐ 直接可用 |
| interpreter | 终端/解释器 | ⭐ |
| language | 语言/翻译 | ⭐⭐ 外贸翻译 |
| speech | 辩论/演讲 | ⭐⭐ 销售话术 |
| comments | 点评/评鉴 | ⭐ 供应商评估 |
| text | 文本/词语 | ⭐ |
| company | 企业职能 | ⭐⭐⭐ 直接对口 |
| seo | SEO | ⭐⭐ 线上推广 |
| doctor | 医疗健康 | - |
| finance | 金融顾问 | ⭐ |
| music | 音乐艺术 | - |
| professional | 专业顾问 | ⭐⭐ |
| contribute | 用户分享 | - |

## 对数控制造业直接有用的标签

高相关度（⭐⭐⭐）：
- **company（企业职能）**：HR、管理、运营相关提示词
- **article（文章/报告）**：行业分析、技术报告
- **tool（效率工具）**：Excel、数据处理、自动化

中相关度（⭐⭐）：
- **write（写作辅助）**：产品文案、技术文档润色
- **language（语言/翻译）**：外贸客户沟通、多语言文档
- **speech（辩论/演讲）**：销售话术、客户拜访准备
- **seo（SEO）**：线上推广、关键词优化
- **professional（专业顾问）**：行业咨询

## 可落地建议

### 1. 提取高价值提示词到 Kitt Skill
从 278 个提示词中筛选 company/article/tool/write/language/speech 标签的，预计 50-80 个直接可用。

### 2. 定制数控行业提示词
基于 AiShort 的数据结构，创建数控设备专用提示词：
- 客户背景调查模板
- 竞品对比分析模板
- 报价策略生成模板
- 售后问题诊断模板
- 外贸邮件模板

### 3. 复用到 Skill 系统
AiShort 的 JSON 结构可以直接映射到 OpenClaw Skill：
- `prompt` → Skill 的 systemPrompt
- `tags` → Skill 的 description/触发条件
- `remark` → Skill 的使用说明

### 4. 搭建内部提示词库
Fork 仓库后，删除无关分类，添加数控行业专用提示词，部署为内部工具。

## 技术亮点（可借鉴）
- 提示词按 ID 独立 JSON 文件，便于管理和版本控制
- 标签系统简洁（25 个），不过度分类
- 多语言方案成熟（18 种语言自动转换）
- 用户贡献机制（contribute 标签）
