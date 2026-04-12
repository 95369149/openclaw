# 2026-02-18 Portless: Vercel 端口转发工具 (@GeekBB)

## 来源

- Author: @GeekBB (Geek)
- Date: 2026-02-17
- Link: https://x.com/geekbb/status/2023645651092075008
- Project: **Portless** (Vercel Labs)

## 核心功能

用稳定的命名 URL (`.localhost`) 替代传统的 `localhost:port` 数字端口。

### 痛点解决

- **人类**：不再需要记 3000, 8080, 8081 这些随机端口，也避免了端口占用冲突。
- **AI Agent**：语义化的 URL (`myapp.localhost`) 更容易被 Agent 理解和访问，利于 Agent 自主进行本地开发调试。

### 工作原理

- 运行一个本地代理服务 (默认端口 1355)。
- 所有 `*.localhost` 请求路由至该代理。
- 代理根据子域名自动转发到实际的应用进程。

## Kitt 思考

- **开发环境标准化**：这不仅是个小工具，更是 Agent-Ready 的开发环境基础设施。如果未来我要在本地帮你跑多个 Web 服务（如 OpenClaw Dashboard, RF-DETR 监控流），用 Portless 管理会非常清晰。
- **关联**：这正是今天 GitHub Trending Top 1 的项目。
