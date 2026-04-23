# Windows 部署 Kitt 指南

## 前提
- Windows 10/11
- 已安装 Git
- 已安装 Node.js 22+

## 步骤

### 1. 安装 OpenClaw
```powershell
# PowerShell（管理员）
npm install -g openclaw
```

### 2. 克隆大脑
```powershell
cd %USERPROFILE%\.openclaw
git clone https://github.com/95369149/kitt-brain.git workspace
```

### 3. 初始化 OpenClaw
```powershell
openclaw init
```

### 4. 配置模型（和 Mac 一致）
```powershell
# 主模型
openclaw config set agents.defaults.model.primary "xjrouter/claude-opus-4-6-max"

# SiliconFlow
openclaw config set models.providers.siliconflow.apiKey "sk-你的key"

# xjrouter（需要先启动 HTTPS 代理，或直接用 SiliconFlow）
```

### 5. 配置消息通道
```powershell
# Discord（和 Mac 用同一个 Bot Token 会冲突！）
# 建议：Mac 用 Discord，Windows 用 Telegram，或者反过来
# 或者：两台机器不同时运行 Gateway

openclaw config set telegram.token "你的bot-token"
```

### 6. 启动
```powershell
openclaw gateway run
```

### 7. 日常同步大脑
```powershell
cd %USERPROFILE%\.openclaw\workspace
git pull origin main
```

## ⚠️ 注意事项

1. **不要两台机器同时连同一个 Bot**（Discord/Telegram），会抢消息
2. **改了记忆要 push**：Mac 改完 → `bash memory/scripts/sync-brain.sh` → Windows `git pull`
3. **配置文件不共享**：`openclaw.json` 包含本机路径和端口，每台机器独立配置
4. **API Key 共享**：SiliconFlow/xjrouter 的 Key 两台机器可以用同一个
5. **HTTPS 代理**：Windows 上也需要单独启动 xjrouter 代理（或直接用 SiliconFlow 做主力）

## 推荐分工

| | Mac（当前） | Windows（新） |
|---|---|---|
| 通道 | Discord + WhatsApp | Telegram |
| 角色 | 主脑（7×24） | 备用/办公室专用 |
| 同步 | push | pull |
