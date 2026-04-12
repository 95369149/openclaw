# 强制规则：Fallback 链配置（2026-02-24 v2.1）

## 核心原则

**免费模型优先，付费模型兜底，确保不失联**

## 当前资源（2026-02-24）

### 免费资源

1. **硅基流动**（1个 API key，待恢复轮动）
   - DeepSeek-V3.2（免费，中文强）
   - DeepSeek-R1（免费，推理）
   - Qwen3-32B（免费）
   - Kimi-K2.5 / Kimi-K2-Thinking（免费）

2. **Google Gemini**（免费额度）
   - gemini-2.5-flash（API Key）
   - gemini-2.5-pro（API Key）
   - gemini-3-pro-preview（OAuth，main 专用）

3. **Groq**（免费）
   - Llama 3.3 70B
   - Qwen3 32B

### 付费资源

1. **mynewapi**（https://api.penguinsaichat.dpdns.org）
   - Claude Sonnet 4.6（jimmy 主力）
   - Claude Opus 4.6（终极兜底）
2. **xjrouter**（http://127.0.0.1:8444/v1 → 47.86.25.153）
   - Claude Opus 4.6 Max（kitt 专用）

## 推荐 Fallback 链配置

### 方案 1：保守型（推荐）

```json
{
  "primary": "siliconflow/deepseek-ai/DeepSeek-V3.2",
  "fallbacks": [
    "groq/llama-3.3-70b-versatile",
    "google-gemini/gemini-2.5-pro",
    "groq/qwen/qwen3-32b",
    "siliconflow/deepseek-ai/DeepSeek-R1",
    "mynewapi/claude-sonnet-4-6",
    "mynewapi/claude-opus-4-6"
  ]
}
```

**理由：**

- 主力用免费的 DeepSeek-V3.2（硅基流动，2个key轮动）
- 前4个都是免费模型
- Claude 作为最后兜底（成本高但可靠）

### 方案 2：平衡型

```json
{
  "primary": "mynewapi/claude-sonnet-4-6",
  "fallbacks": [
    "siliconflow/deepseek-ai/DeepSeek-V3.2",
    "groq/llama-3.3-70b-versatile",
    "google-gemini/gemini-2.5-pro",
    "groq/qwen/qwen3-32b",
    "mynewapi/claude-opus-4-6"
  ]
}
```

**理由：**

- 主力用 Claude Sonnet（质量高）
- 失败后立即切换到免费模型
- Opus 作为最后兜底

### 方案 3：激进型（不推荐）

```json
{
  "primary": "mynewapi/claude-sonnet-4-6",
  "fallbacks": ["mynewapi/claude-opus-4-6"]
}
```

**理由：**

- 只用付费模型，质量最高
- ❌ 风险：两个都失败就失联

## 推荐：方案 1（保守型）

**优势：**

1. ✅ 主力免费（DeepSeek-V3.2，硅基流动2个key轮动）
2. ✅ 4层免费备份（Groq, Gemini, DeepSeek-R1）
3. ✅ Claude 兜底（最后保障）
4. ✅ 不会失联（6层保护）

**成本：**

- 日常：$0（免费模型）
- 极端情况：Claude 兜底（偶尔）

## 注意事项

### Gemini 2.5 Flash 限制

- 20次/天限制
- **不要放在 Fallback 链**（会很快用完）
- 仅用于定时任务

### 硅基流动轮动

- 2个 API key 自动轮动
- 环境变量已配置：`SILICONFLOW_API_KEYS`
- 一个失败自动切换另一个

### 定期检查

- 每周检查付费模型余额
- 每月检查免费模型额度

## 更新日志

- 2026-02-22：基于当前资源重新设计，确保不失联
