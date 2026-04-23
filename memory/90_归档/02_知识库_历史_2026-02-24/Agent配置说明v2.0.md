# Agent 配置说明 v2.0

## Agent 列表

### 1. main（默认）

- **模型：** Gemini 2.5 Flash
- **职责：** 快速整理抓取的文章和学习资料，分类汇总
- **特点：** 速度快，免费，适合日常任务

### 2. jimmy（前台接待）

- **模型：** Groq Llama 3.3 70B
- **职责：** 前台接待，快速响应用户
- **特点：** 速度极快，能力不错，免费

### 3. logic（推理）

- **模型：** DeepSeek-R1
- **职责：** 复杂逻辑推理，深度思考
- **特点：** 推理能力强，免费

### 4. deep（深度分析）

- **模型：** DeepSeek-V3.2
- **职责：** 深度分析，复杂任务
- **特点：** 能力全面，免费

### 5. kitt（配置管理）

- **模型：** Claude Opus 4.6
- **职责：** 配置管理，系统优化，关键决策
- **特点：** 能力最强，付费，只有 Kitt 有权修改配置

## Scout 机制（大杀器）

### Scout-Perplexity（实时搜索）

- **调用方式：** 浏览器（Perplexity Pro 会员）
- **职责：** 实时搜索，最新信息
- **模型选择：** GPT-5.2, Sonar, Claude Sonnet 4.6

### Scout-Grok（X 内容）

- **调用方式：** 浏览器（X Premium）
- **职责：** X 推文分析，实时热点
- **模型：** Grok 4.1

### Scout-豆包（中文润色）

- **调用方式：** 浏览器
- **职责：** 中文内容润色
- **模型：** 豆包 2.0 Pro

## 调用规则

### Agent 调用

- 使用 `sessions_spawn` 创建子代理
- 适合：独立任务，需要隔离上下文

### Scout 调用

- 使用浏览器工具（openclaw profile）
- 适合：需要登录的外部服务（Perplexity, Grok, 豆包）
- Kitt 不直接操作，派 Scout 去执行

## 成本控制

### 免费优先

1. main（Gemini Flash）
2. jimmy（Groq Llama）
3. logic（DeepSeek-R1）
4. deep（DeepSeek-V3.2）

### 付费精准使用

5. kitt（Claude Opus）- 只用于配置管理和关键决策

## 更新日志

- 2026-02-22：重新打磨配置，移除无 API 的 agent，保持 Scout 机制
