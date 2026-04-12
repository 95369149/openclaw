# 强制规则：Fallback 链安全策略

## 2026-02-18 血的教训

Claude API 欠费后，整个 Fallback 链全军覆没，导致 Kitt 失联 30+ 分钟。

## 规则

1. **免费模型永远排在前面**：Gemini Flash → Gemini Pro → Groq (Llama/Qwen) → 最后才是付费模型。
2. **付费模型只作为最后手段**：Claude Opus 永远排在 Fallback 链最后一位。
3. **欠费模型立即移除**：一旦发现某个模型报 403/余额不足，立刻从 Fallback 链中移除或移到最后，不要让它浪费重试时间。
4. **v1api (DeepSeek) 已废弃**：余额 $0.028，不再使用。已从 Fallback 链移除。
5. **定期检查余额**：每周检查一次付费模型的余额状态。

## 当前 Fallback 链 (2026-02-18 更新)

```
主力: google-gemini-cli/gemini-3-pro-preview (免费 OAuth)
备用1: google-gemini/gemini-2.5-flash (免费 API)
备用2: google-gemini/gemini-2.5-pro (免费 API)
备用3: groq/llama-3.3-70b-versatile (免费)
备用4: groq/qwen/qwen3-32b (免费)
备用5: mynewapi/claude-opus-4-6 (付费，最后手段)
```

## 禁止事项

- **禁止**把付费模型放在免费模型前面
- **禁止**在 Fallback 链中保留已知欠费的模型
