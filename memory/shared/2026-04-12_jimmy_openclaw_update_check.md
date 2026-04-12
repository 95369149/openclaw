# 2026-04-12 OpenClaw 自动更新检查

- 时间: 2026-04-12 09:00 Asia/Shanghai
- npm 最新版本: 2026.4.11
- 当前版本: 2026.4.8
- 结论: 存在新版本，需升级
- 执行结果: 当前 cron 会话所在运行时禁用 elevated，`sudo npm install -g openclaw@latest` 无法执行
- 后续动作: 需要在支持 elevated 的会话中运行升级命令，升级后再确认 `openclaw --version`
