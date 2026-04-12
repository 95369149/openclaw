# OpenViking 最新进展 - 2026-02-24

## 版本更新：v0.1.18（2026-02-23）

### 重大新功能
1. **Claude Memory Plugin 示例** — 官方出了 Claude 集成记忆插件的 example，直接对标我们的 Kitt 记忆体系
2. **Docker 支持** — 官方 Docker 化部署，可以一键起服务
3. **Jina AI Embedding** — 新增 Jina 向量化 provider，多了一个免费选择
4. **ZIP 上传 + 服务端解压** — `add-resource` 支持上传 zip 包，服务端自动解压
5. **TOS/OSS 存储支持** — 后端存储支持火山引擎 TOS 和阿里 OSS
6. **日志轮转** — LogConfig 封装，支持日志自动轮转
7. **K8s Helm Chart** — 简化版 K8s 部署方案
8. **多 Provider 支持** — 不再绑定单一 LLM provider，可配多个

### Bug 修复
- Windows 时间戳兼容（>6位小数秒）
- S3 后端 AGFS 错误修复
- 异步 Session.load() 防死锁
- 文件名冲突自动重命名
- search_by_id 空候选防护

### 对比上次跟踪（v0.1.17, 2026-02-14）
- 9天内发布了 1 个新版本 + 15+ commits
- 社区活跃度持续上升，新增多位贡献者
- 从"库"向"平台"演进：Docker + K8s + 多 Provider

## 对 Kitt 的启发

### 可直接借鉴
1. **Claude Memory Plugin** — 研究他们的集成方式，看能不能直接用在 OpenClaw 上
2. **三层记忆 L0/L1/L2** — 我们的失忆调查报告已经提出了这个方案，OpenViking 是参考实现
3. **向量化检索** — Jina AI embedding 免费可用，可以给 memory/ 做语义索引

### 架构差异
- OpenViking 是独立服务（需要部署），Kitt 是嵌入式（跑在 OpenClaw 里）
- OpenViking 用文件系统范式管理上下文，Kitt 用 markdown 文件 + memory_search
- OpenViking 有层次化上下文投递，Kitt 靠手动 read + memory_search

### 下一步
1. 研究 Claude Memory Plugin example 的代码
2. 评估是否值得在本地跑一个 OpenViking 实例作为 Kitt 的记忆后端
3. 先实现 L0 摘要机制（不依赖 OpenViking，纯文件方案）

## 参考链接
- GitHub: https://github.com/volcengine/OpenViking
- v0.1.18 Release: https://github.com/volcengine/OpenViking/releases/tag/v0.1.18
- Claude Plugin Example: https://github.com/volcengine/OpenViking/tree/main/examples
