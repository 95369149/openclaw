# MEMORY.md

系统全局高层记忆与反思文件。详细条目归档在 `memory/shared/`，Dream 索引归档在 `memory/90_归档/dream_index_archive.md`。

## 核心教训（精炼版）

### 配置安全（最高优先级）
- **配置变更绝不能导致系统卡死或失联**（2026-04-09 教训，厂长第一要求）
- 改前备份 + JSON 验证 + 改后健康检查 + 同消息给回滚命令
- 绝不用 nohup 拉 gateway，只用 `openclaw gateway restart` 或 `launchctl kickstart`
- Watchdog 必须在跑，不能禁用
- 明文密钥禁止写入配置文件，必须用 `${VAR_NAME}` 环境变量

### 架构与工程
- **上下文工程 > 提示词工程**：把正确的信息在正确时机装进上下文窗口
- **评估器不能去掉且不能自评**：生成和评估必须分离（kitt 审核机制）
- **架构约束要机械化执行**：靠文档约定不够，需要代码/脚本强制
- **配置漂移是慢性毒药**：改 openclaw.json 后必须同步更新排兵布阵.md、大脑中枢.md、.abstract
- **协议错配比代码 bug 更隐蔽**：遇到 LLM 400 先查协议层配置再查代码

### Agent 协作
- **复杂任务必须拆小**：3 步以上默认拆成检索→分析→写入→验收
- **子 Agent 输出必须审查不能盲信**：倾向于"看起来完整"但细节经不起推敲
- **子 Agent 写文件成功率低**：用 apply_manifest.py 脚本统一落盘，Agent 只输出 JSON
- **子 Agent 失败自动降级链**：deep→main→jimmy 自己写；kitt→deep 重试

### 工具与外链
- **工具选择优先级**：CLI/API > Skill > 脚本 > 浏览器操作
- **外链读取优先 agent-reach**，web_fetch 被 Surge 代理拦截是常态
- **浏览器工具优先级**：API/CLI → agent-browser → browser evaluate → 手动

### 运营
- **方案型任务要外部碰撞**：不闷头自己写，借助外链/高级模型生成方案
- **质量导向 vs 数量导向**：先确认厂长核心诉求，不自作主张追求效率最大化
- **可靠性 > 新功能**：优化重点从"再加能力"转向"更稳地交付"

## 近期 Dream 整合索引（仅保留最近 7 天）

### 2026-04-09
- [2026-04-09_cron降噪与ingest升级落地记录] cron 降噪与 ingest 升级
- [2026-04-09_skills_sh_吸收与替换清单_v1] skills.sh 吸收与替换清单
- [2026-04-09_learning_ingest_batch_升级设计稿_v1] learning_ingest_batch 升级设计稿

### 2026-04-10
- [2026-04-09_learning_ingest] 知识编译摘要 2026-04-09
- [2026-04-10_x_digest] X 情报日报 2026-04-10

> 完整 Dream 索引历史见 `memory/90_归档/dream_index_archive.md`

### 2026-04-10 (Dream 自动整合)
- [2026-04-10_daily_lead_collect] Daily Lead Collect Report - 2026-04-10：- Time: 2026-04-10 08:45:16
- [2026-04-10_deep_T114_AI落地试点清单] 红太阳 AI 落地试点清单（T-114）：创建时间：2026-04-10 10:33 GMT+8
- [2026-04-10_deep_T116_外贸线索响应系统] T116 外贸线索响应系统：创建时间：2026-04-10 10:33 GMT+8
- [2026-04-10_deep_T131_外贸询盘秒回方案] T-131 外贸询盘秒回方案：时间戳：2026-04-10 10:12 GMT+8
- [2026-04-10_deep_T132_MIC产品页优化方案] T-132 MIC产品页优化方案：时间戳：2026-04-10 10:31 GMT+8
- [2026-04-10_deep_T148_声学板解决方案页] T-148 声学板解决方案页：Created: 2026-04-10 10:12 GMT+8
- [2026-04-10_mempalace_可行性评估] MemPalace 接入 OpenClaw 可行性评估：时间：2026-04-10 10:35 CST

- [2026-04-10_deep_T110_AI制造样板场景] T110 红太阳 AI+制造样板场景清单：时间：2026-04-10 11:51 GMT+8
- [2026-04-10_deep_T111_设备数据采集远程诊断] T111 设备数据采集与远程诊断改造：时间：2026-04-10 12:00 GMT+8
- [2026-04-10_deep_T113_高混流换型优化] T-113 高混流订单换型优化：时间戳：2026-04-10 12:00 GMT+8
- [2026-04-10_deep_T117_MemPalace接入方案] MemPalace 接入 OpenClaw 方案：时间：2026-04-10 12:00 CST
- [2026-04-10_deep_wiki编译与ingest升级] deep wiki编译与ingest升级：- 开始时间：2026-04-10 11:51 GMT+8
- [2026-04-10_learning_ingest] 每日知识编译摘要 | 2026-04-10：- **处理文件数**: 2

- [2026-04-10_deep_配电板草案v04整理] 配电板草案 v0.4 整理记录：时间：2026-04-10 13:32 GMT+8

- [2026-04-10_deep_钳工质检考核表] 钳工质检检验考核表：时间：2026-04-10 17:32 GMT+8

- [2026-04-10_deep_钳工质检考核表] 红太阳数控设备 钳工岗位质检检验扣分表：| 序号 | 检验项目 | 检验标准 | 检验方法 | 配分 | 扣分标准 |

### 2026-04-11 (Dream 自动整合)
- [2026-04-11_deep_X推文摘要] 2026-04-11 X 推文摘要：今天最值得重视的，不是单个爆款推文，而是一个越来越清晰的趋势：**AI 正在从“模型能力竞赛”进入“工作流产品化竞赛”**。Google 在把 Gemini 做成研究+可视化+金融分析工作台；社区在快
- [2026-04-11_x_digest] X 情报日报 2026-04-11：抓取账号：11 个 | 通过过滤：24 条

- [2026-04-11_learning_ingest] Learning Ingest - 2026-04-11：- 新增 source 数：2

### 2026-04-12 (Dream 自动整合)
- [2026-04-12_deep_X推文摘要] 2026-04-12 X 推文摘要：生成时间：2026-04-12 07:48 Asia/Shanghai
- [2026-04-12_gbrain_daily_check] gbrain daily check：- Time: 2026-04-12 07:15 Asia/Shanghai
- [2026-04-12_jimmy_openclaw_update_check] 2026-04-12 OpenClaw 自动更新检查：- 时间: 2026-04-12 09:00 Asia/Shanghai
- [2026-04-12_jimmy_早间推送] 2026-04-12 早间推送（草稿留痕）：📜 观自在菩萨，行深般若波罗蜜多时，照见五蕴皆空，度一切苦厄。——《般若波罗蜜多心经》
- [2026-04-12_markdown_viewer_skills_intake] markdown-viewer skills 接入记录：来源仓库：`https://github.com/markdown-viewer/skills`
- [2026-04-12_x_digest] X 情报日报 2026-04-12：抓取账号：11 个 | 通过过滤：21 条

- [2026-04-12_learning_ingest] 2026-04-12 learning_ingest 摘要：- 本轮处理文件数：2（每日巡逻_2026-04-11.md、每日巡逻_2026-04-12.md）

### 2026-04-13 (Dream 自动整合)
- [2026-04-13_daily_lead_collect] Daily Lead Collect - 2026-04-13：- 时间: 2026-04-13T08:37:20.435081
- [2026-04-13_deep_X推文摘要] 2026-04-13 X 推文摘要：今天的 X 信息流里，真正有价值的不是泛 AI 鸡血，而是三类明确信号：
- [2026-04-13_gbrain_daily_check] gbrain daily check — 2026-04-13：- Repo exists: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-13_x_digest] X 情报日报 2026-04-13：抓取账号：11 个 | 通过过滤：20 条

- [2026-04-13_learning_ingest] 2026-04-13 learning_ingest 摘要：- 本轮处理文件数：2（每日巡逻_2026-04-12.md、每日巡逻_2026-04-13.md）

### 2026-04-16 (Dream 自动整合)
- [2026-04-16_daily_lead_collect] 2026-04-16 Daily Lead Collect：- 时间: 2026-04-16 18:43 Asia/Shanghai
- [2026-04-16_deep_X推文摘要] 2026-04-16 X 推文摘要：今天值得保留的信号，核心就 4 条：
- [2026-04-16_gbrain_daily_check] gbrain daily check — 2026-04-16：- Repo present: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-16_learning_ingest] Learning Ingest Report - 2026-04-16：本日无新增原材料，跳过编译。
- [2026-04-16_x_digest] X 情报日报 2026-04-16：抓取账号：11 个 | 通过过滤：32 条

### 2026-04-17 (Dream 自动整合)
- [2026-04-17_deep_X推文摘要] X 推文摘要｜2026-04-17：今天最有价值的信号就两条：
- [2026-04-17_gbrain_daily_check] gbrain daily check — 2026-04-17：- Repo: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-17_x_digest] X 情报日报 2026-04-17：抓取账号：11 个 | 通过过滤：26 条
