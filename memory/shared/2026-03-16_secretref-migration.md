# SecretRef 格式迁移记录

**时间**: 2026-03-16 13:48  
**操作者**: jimmy  
**事件**: SecretRef 格式全面升级 + 明文密钥分离

## 背景

上午配置使用 `${VAR_NAME}` 字符串引用格式，有人误把 `env.vars` 里的明文也改成了 `${VAR_NAME}`，导致自引用死锁，Gateway 无法解析密钥。

## 解决方案

### 第一步：修正 env.vars 自引用
从 `openclaw.json.bak.4`（上午 09:37 稳定版）恢复 `env.vars` 明文值，保持 providers/gateway/channels 的 `${VAR}` 引用不动。

### 第二步：升级到正式 SecretRef 对象格式
将所有 `${VAR_NAME}` 字符串改为 OpenClaw 官方 SecretRef 对象：
```json
{
  "source": "env",
  "provider": "default",
  "id": "VAR_NAME"
}
```

### 第三步：明文物理分离
- 将 13 个敏感密钥从 `openclaw.json` 的 `env.vars` 抽出
- 写入 `~/.openclaw/.env` 文件（权限 600）
- `openclaw.json` 只保留 4 个非敏感配置（代理、项目ID）

## 当前架构

### 密钥管理
- **格式**: SecretRef 对象 `{"source":"env","provider":"default","id":"VAR_NAME"}`
- **明文存放**: `~/.openclaw/.env` (权限 600)
- **配置文件**: `openclaw.json` 零敏感信息，可随意分享

### 分离的密钥（13个）
```
BRAVE_API_KEY, MYNEWAPI_API_KEY, GOOGLE_GEMINI_API_KEY,
GROQ_API_KEY, DOUBAO_API_KEY, DOUBAO_WEB_API_KEY,
NANASHIWANG_API_KEY, CRS_API_KEY, MYGPTAPI_API_KEY,
GEMINIFLASH_API_KEY, TELEGRAM_BOT_TOKEN, DISCORD_BOT_TOKEN,
OPENCLAW_GATEWAY_TOKEN
```

### 保留在 openclaw.json 的非敏感配置
```
HTTPS_PROXY, HTTP_PROXY, GOOGLE_CLOUD_PROJECT, NO_PROXY
```

## 验证结果
- Gateway: running (pid 12234)
- RPC probe: ok
- API 测试: HTTP 200
- 无报错（13:39 的 401 已解决）

## 回滚路径

### 回滚到分离前（SecretRef对象 + env.vars明文）
```bash
cp ~/.openclaw/openclaw.json.bak-envsplit-20260316-134520 ~/.openclaw/openclaw.json
rm ~/.openclaw/.env
openclaw gateway restart
```

### 回滚到上午稳定版（${VAR}字符串 + env.vars明文）
```bash
cp ~/.openclaw/openclaw.json.bak.4 ~/.openclaw/openclaw.json
rm ~/.openclaw/.env
openclaw gateway restart
```

## 关键备份文件
- `.bak-envsplit-20260316-134520` - 分离前最后稳定版（SecretRef对象格式）
- `.bak.4` - 上午 09:37 稳定版（${VAR}字符串格式）
- `~/.openclaw/.env` - 当前明文密钥文件

## 教训

1. **env.vars 不能自引用**: `env.vars` 里写 `${VAR}` 引用自己会死锁，必须写明文
2. **SecretRef 有两种格式**:
   - 简化格式: `"${VAR_NAME}"` 字符串（上午用的，也能跑）
   - 正式格式: `{"source":"env","provider":"default","id":"VAR_NAME"}` 对象（现在用的）
3. **明文分离是可选的**: Gateway 会自动读取 `~/.openclaw/.env`，不需要手动配置
4. **重启时序问题**: 重启瞬间可能出现短暂 401，等几秒自动恢复

## 安全收益

- `openclaw.json` 可以安全提交到 Git（已零敏感信息）
- `~/.openclaw/.env` 权限 600，仅当前用户可读
- 符合 OpenClaw 官方推荐的 SecretRef 最佳实践
