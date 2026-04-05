# 强制规则：Fallback 链安全策略

## 历史教训
- 2026-02-18 14:28：Claude/DeepSeek/Gemini 同时不可用，Kitt 失联 65 分钟
- 2026-02-18 18:15：恢复旧黄金备份导致 Groq/SiliconFlow 被清除，失联 3 小时
- 2026-02-18 23:11：SiliconFlow 免费版限流，整条链堵塞

## 当前 Fallback 链 (2026-02-19 更新)
```
主力: siliconflow/deepseek-ai/DeepSeek-V3.2 (免费，日常前台)
备用1: siliconflow/Pro/deepseek-ai/DeepSeek-V3.2 (付费，免费版限流时秒切)
备用2: siliconflow/Qwen/Qwen3-32B (免费)
备用3: groq/llama-3.3-70b-versatile (免费，独立平台)
备用4: groq/qwen/qwen3-32b (免费，独立平台)
备用5: mynewapi/claude-sonnet-4-6 (付费)
备用6: mynewapi/claude-opus-4-6 (付费，大脑，最后手段)
备用7: google-gemini/gemini-2.5-flash (免费，易限流)
备用8: google-gemini-cli/gemini-3-pro-preview (免费 OAuth，易限流)
```

## 规则
1. 免费模型排前面，付费模型排后面
2. 同平台免费+付费配对（SiliconFlow 免费→Pro）
3. 跨平台交替排列（SiliconFlow→Groq→mynewapi→Google）
4. Claude Opus 永远不能被移除（大脑角色）
5. 欠费模型立即移除，不浪费重试时间
6. 黄金备份必须包含所有 provider，更新后立即同步

## 禁止事项
- 禁止把所有免费模型放在同一个平台（单点故障）
- 禁止恢复旧黄金备份而不检查 provider 完整性
- 禁止在 google-gemini API 模式下配 Preview 模型（会崩溃）
