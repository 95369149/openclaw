# 语义记忆：Discord 配置踩坑

## 教训（2026-02-16）

### 1. 字段名不要猜
- Discord channel 的 token 字段名是 `token`，不是 `botToken`
- 必须查源码或文档确认，不能照搬其他 channel 的命名

### 2. bot_require_code_grant 陷阱
- 新建 Application 时如果不小心开了这个，Bot 邀请链接会静默失败
- guilds API 返回空 ≠ token 无效，可能是 Bot 根本没加入服务器
- 解法：删掉 Application 重建，新建默认 false

### 3. groupPolicy: allowlist 需要配 guilds
- 设了 allowlist 但没配 guilds 白名单 = 所有消息被静默丢弃
- 初期用 open，稳定后再改 allowlist + guilds

### 4. Discord WebSocket 不走 HTTP_PROXY
- Node.js 的 WebSocket 不读 HTTP_PROXY 环境变量
- OpenClaw 支持 `channels.discord.proxy` 字段，必须显式配置
- IPv6 连接超时是典型症状

### 5. gateway 配置会被 doctor/wizard 覆盖
- 直接编辑 JSON 加的字段如果不在 schema 里会被删掉
- 用 python 脚本改 JSON 后要立即验证
