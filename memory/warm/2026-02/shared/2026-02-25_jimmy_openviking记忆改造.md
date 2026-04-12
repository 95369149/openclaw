# Jimmy: OpenViking 记忆范式落地

## 做了什么
基于 @jungeAGI 的 OpenViking × OpenClaw 文章，落地三层记忆管理：
1. L0 索引文件 `memory/.abstract` — 启动只读索引
2. 共享记忆层 `memory/shared/` — agent 间通信
3. 清理脚本 `memory-cleanup.sh` — P0/P1/P2 保质期自动归档
4. AGENTS.md 新增 Memory Protocol 规则

## 结果
- 预期 token 消耗降 50%+（不再全量读 memory）
- 3 个过期文件已自动归档
- 所有 agent 后续会自觉写共享记忆

## 关键发现
- OpenViking 项目很活跃（v0.1.18），后续可能出 OpenClaw 原生插件
- 已设每日 cron 追踪项目更新
