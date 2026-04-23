# SiliconFlow API Key 轮动操作手册

## 原理

每个 14 元 Key 注册为独立 provider（siliconflow / siliconflow-2 / siliconflow-3...），交替放在 fallback 链里。Key 1 限流 → 自动跳 Key 2 → 自动跳 Key 3。用完的 Key 删掉，换新的。

## 添加新 Key

厂长给 Kitt 新 Key 后，Kitt 执行：

```bash
# 添加 siliconflow-N（N=2,3,4...）
openclaw config set models.providers.siliconflow-N '{"baseUrl":"https://api.siliconflow.cn/v1","apiKey":"sk-新的key","api":"openai-completions","models":[{"id":"deepseek-ai/DeepSeek-V3.2","name":"DeepSeek V3.2 (KeyN)","input":["text"],"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0},"contextWindow":131072,"maxTokens":8192},{"id":"Qwen/Qwen3-32B","name":"Qwen3 32B (KeyN)","input":["text"],"cost":{"input":0,"output":0,"cacheRead":0,"cacheWrite":0},"contextWindow":131072,"maxTokens":8192}]}'

# 加到 fallback 链（插到 SiliconFlow 后面）
# 需要重新设置整个 fallback 数组
```

## 删除用完的 Key

```bash
openclaw config unset models.providers.siliconflow-N
# 同时从 fallback 链中移除
```

## 当前状态

- siliconflow（主）: sk-walotb...（14元额度）
- 待添加：厂长提供新 Key 后配置

## Python 调度系统（独立轮动）

`agent_dispatcher_v3.py` 的 `_SILICONFLOW_KEYS` 列表也需要同步更新新 Key。
限流/余额耗尽时自动切换 + 熔断器重置。

## 自动管理规则

1. Key 欠费/余额耗尽 → 立即从 OpenClaw + Python 调度系统中删除
2. 剩余可用 Key ≤ 2 个时 → 立即提醒厂长买新 Key
3. 每次心跳检查各 Key 可用性（发 ping 请求测试）
4. 删除/添加 Key 后自动重启 Gateway

## 注意

- 只有 Kitt 有权操作
- 添加后需要 `openclaw gateway restart`
- 重启前必须审查配置
