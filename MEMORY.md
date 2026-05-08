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

### 2026-04-18 (Dream 自动整合)
- [2026-04-18_deep_X推文摘要] 2026-04-18 X 推文摘要：今天最有价值的信号，不在单条爆款观点，而在一个共同方向：AI 工具正在从“会聊天”快速切到“会执行、会验证、可复用、可编排”。这对红太阳有两层意义：第一，内部运营和内容生产都该尽快从单点提效升级到流程
- [2026-04-18_gbrain_daily_check] gbrain daily check — 2026-04-18：- Repo present: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-18_x_digest] X 情报日报 2026-04-18：抓取账号：11 个 | 通过过滤：22 条

### 2026-04-19 (Dream 自动整合)
- [2026-04-19_deep_X推文摘要] X 推文摘要｜2026-04-19：今天真正值得留的信号只有三类。
- [2026-04-19_gbrain_daily_check] gbrain daily check — 2026-04-19：- Repo exists: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-19_x_digest] X 情报日报 2026-04-19：抓取账号：11 个 | 通过过滤：19 条

### 2026-04-20 (Dream 自动整合)
- [2026-04-20_deep_X推文摘要] X 推文摘要日报｜2026-04-20：今日监控脚本已执行，`memory/ideas.md` 在 `## 2026-04-20 07:44 (v2.0 已过滤)` 下新增了 11 条推文。经二次人工过滤后，可用信息集中在 5 个方向：Ag
- [2026-04-20_gbrain_daily_check] gbrain daily check — 2026-04-20：- Repo present: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-20_x_digest] X 情报日报 2026-04-20：抓取账号：11 个 | 通过过滤：13 条

- [2026-04-20_learning_ingest] 2026-04-20 learning_ingest 摘要：- 本轮处理文件数：7（inbox/hermes_bridge_sync 全部）

### 2026-04-21 (Dream 自动整合)
- [2026-04-21_daily_lead_collect] 2026-04-21 每日线索自动采集：- 执行时间：2026-04-21 08:30 Asia/Shanghai
- [2026-04-21_deep_X推文摘要] 2026-04-21 X 推文摘要：生成时间：2026-04-21 07:43 Asia/Shanghai
- [2026-04-21_gbrain_daily_check] gbrain daily check - 2026-04-21：- Status: action needed
- [2026-04-21_x_digest] X 情报日报 2026-04-21：抓取账号：11 个 | 通过过滤：26 条

- [2026-04-21_learning_ingest] 本轮处理文件数：2（每日巡逻_2026-04-20.md、每日巡逻_2026-04-21.md）：新增概念：1（外贸AI获客工作流）；更新概念：5（生产级Agent框架、OpenClaw数字员工底座、Seedance视频模板化生产、场景化振动刀方案、外贸AI执行团队）

### 2026-04-22 (Dream 自动整合)
- [2026-04-22_daily_lead_collect] Daily Lead Collect - 2026-04-22：- Time: 2026-04-22T08:32:17+08:00
- [2026-04-22_deep_X推文摘要] 2026-04-22 X 推文摘要：今天真正有价值的信号不在泛泛而谈的投资鸡汤，而在三条主线：
- [2026-04-22_gbrain_daily_check] gbrain daily check — 2026-04-22：- Repo exists: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-22_x_digest] X 情报日报 2026-04-22：抓取账号：11 个 | 通过过滤：27 条

- [2026-04-22_learning_ingest] 每日知识编译报告｜2026-04-22：- **处理文件数**：3

- [2026-04-22_jimmy_多Agent协作学习笔记] 多 Agent 协作学习笔记：整理时间：2026-04-22
- [2026-04-22_jimmy_多Agent并发优化方案] 多 Agent 并发优化方案 v1.0：整理时间：2026-04-22

- [2026-04-22_jimmy_多Agent并发优化方案_v2] 多 Agent 并发优化方案 v2.0（基于官方文档验证）：整理时间：2026-04-22
- [2026-04-22_x_digest_parallel] X 情报日报 2026-04-22（并行采集测试版）：> 采集方式：Fan-Out 并行（4 个 scout 同时运行）

### 2026-04-23 (Dream 自动整合)
- [2026-04-23_learning_ingest] 本轮处理文件数：1：新增/更新概念数：3（新增 3，更新 0）

- [2026-04-23_sino_notebooklm_study_plan] NotebookLM 陪跑式专属老师落地方案：**目标对象**：小学三年级女孩

- [长方形周长_NotebookLM素材包] 长方形周长 · NotebookLM 素材包：> 适用对象：小学三年级 | 版本：v1.0 | 日期：2026-04-23

### 2026-04-24 (Dream 自动整合)
- [2026-04-24_daily_lead_collect] 每日线索自动采集报告：- 日期：2026-04-24
- [2026-04-24_deep_X推文摘要] 2026-04-24 X 推文摘要：今天新增内容里，真正有价值的信号集中在 4 条：
- [2026-04-24_gbrain_daily_check] gbrain daily check — 2026-04-24：- Repo present: `/Users/apple/.openclaw/workspace/gbrain`
- [2026-04-24_x_digest] X 情报日报 2026-04-24：抓取账号：11 个 | 通过过滤：37 条

- [2026-04-24_learning_ingest] - 本轮处理文件数：2：- 新增/更新概念数：2/3

### 2026-04-25 (Dream 自动整合)
- [2026-04-25_deep_X推文摘要] 2026-04-25 X 推文消化摘要：> 来源：`memory/ideas.md` 今日尾部新增内容。监控脚本已触发，但本轮执行在约 2 分钟后被系统 SIGKILL；已基于已落盘内容完成消化。
- [2026-04-25_gbrain_daily_check] gbrain daily check - 2026-04-25：Finding: update/action may be needed.
- [2026-04-25_x_digest] X 情报日报 2026-04-25：抓取账号：11 个 | 通过过滤：30 条

- [2026-04-25_learning_ingest] 2026-04-25 11:00 每日知识编译：- 本轮处理文件数：3

### 2026-04-26 (Dream 自动整合)
- [2026-04-26_deep_X推文摘要] 2026-04-26 X 推文消化摘要：> 来源：`memory/ideas.md` 今日新增段落（2026-04-26 07:44，v2.0 已过滤）
- [2026-04-26_gbrain_daily_check] gbrain daily check — 2026-04-26：- Repo: `/Users/apple/.openclaw/workspace/gbrain` exists.

- [2026-04-26_jimmy_huashu_design学习笔记] Huashu Design 安装与学习笔记：- 时间：2026-04-26

- [2026-04-26_learning_ingest] learning_ingest_batch 2026-04-26 11:00：- 本轮处理文件数：2

### 2026-04-27 (Dream 自动整合)
- [2026-04-27_daily_lead_collect] 每日线索自动采集报告 — 2026-04-27：- 执行时间: 2026-04-27 08:32:06 CST → 08:32:18 CST
- [2026-04-27_deep_X推文摘要] 2026-04-27 X 推文消化摘要：- 任务时间：2026-04-27 07:47（Asia/Shanghai）
- [2026-04-27_gbrain_daily_check] gbrain daily check — 2026-04-27：- Repo: `/Users/apple/.openclaw/workspace/gbrain` exists.
- [2026-04-27_x_digest] X 情报日报 2026-04-27：抓取账号：11 个 | 通过过滤：19 条

- [2026-04-27_learning_ingest] 2026-04-27 11:01 learning_ingest：- 本轮处理文件数：2

### 2026-04-28 (Dream 自动整合)
- [2026-04-28_daily_lead_collect] 每日线索采集报告 — 2026-04-28 (周二)：**执行时间**: 08:30 CST | **耗时**: ~2 分钟
- [2026-04-28_deep_X推文摘要] X 情报日报 2026-04-28：> 抓取 12 账号 | 通过过滤 15 条 | 深度摘要 5 个信号
- [2026-04-28_gbrain_daily_check] gbrain Daily Health Check — 2026-04-28 07:15 CST：**Repo:** `/Users/apple/.openclaw/workspace/gbrain` — exists ✓

- [2026-04-28_learning_ingest] 2026-04-28 每日知识编译：- **处理文件数**：2

### 2026-04-29 (Dream 自动整合)
- [2026-04-29_daily_lead_collect] 每日线索采集报告 — 2026-04-29 (周三)：**执行时间**: 08:30 CST
- [2026-04-29_deep_X推文摘要] X 情报消化日报 — 2026-04-29：> 抓取账号：11 | 通过五维过滤：24条 | 过滤后精华：7条高价值信号
- [2026-04-29_gbrain_daily_check] gbrain Daily Health Check — 2026-04-29：**Time**: 07:21 CST
- [2026-04-29_x_digest] X 情报日报 2026-04-29：抓取账号：11 个 | 通过过滤：24 条

- [2026-04-29_learning_ingest] 每日知识编译摘要 — 2026-04-29：- **扫描文件数**：2（inbox 0 + 80_收藏/新增 2）

### 2026-04-30 (Dream 自动整合)
- [2026-04-30_daily_lead_collect] 每日线索采集报告 — 2026-04-30 (周四)：**执行时间**: 08:30 CST
- [2026-04-30_deep_X推文摘要] X 情报日报 2026-04-30：> 抓取账号：10 个 | 通过五维过滤：33 条 | 撰写时间：07:45
- [2026-04-30_gbrain_daily_check] gbrain Daily Health Check — 2026-04-30 07:15 CST：**Status**: ⚠️ Minor attention needed
- [2026-04-30_x_digest] X 情报日报 2026-04-30：抓取账号：11 个 | 通过过滤：34 条

### 2026-05-01 (Dream 自动整合)
- [2026-05-01_gbrain_daily_check] gbrain Daily Check — 2026-05-01：- **Repo**: `/Users/apple/.openclaw/workspace/gbrain` — exists, clean working tree

- [2026-05-01_daily_lead_collect] 每日线索自动采集报告：**日期**: 2026-05-01 (周五, 工作日)
- [2026-05-01_deep_X推文摘要] X 情报日报 2026-05-01：> 抓取账号：10 个 | 通过过滤：29 条 | 扫描时间 07:42

## Promoted From Short-Term Memory (2026-05-02)

<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:4:4 -->
- 三条公开抓取链路，不走官方 X API，不需要 cookie： [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:4-4]
<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:8:8 -->
- curl -s "https://api.fxtwitter.com/status/<tweet_id>" [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:8-8]
<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:10:10 -->
- 返回 JSON，含 tweet.text、article.content.blocks [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:10-10]
<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:14:14 -->
- curl -s "https://r.jina.ai/http://x.com/<user>/status/<tweet_id>" [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:14-14]
<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:16:16 -->
- 返回 Markdown 可读文本 [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:16-16]
<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:20:20 -->
- curl -s "https://cdn.syndication.twimg.com/tweet-result?id=<tweet_id>&token=x" [score=0.822 recalls=0 avg=0.620 source=memory/2026-04-27.md:20-20]

### 2026-05-02 (Dream 自动整合)
- [2026-05-02_gbrain_daily_check] gbrain Daily Check — 2026-05-02 07:15 CST：- **Repo**: ✅ Present at `/Users/apple/.openclaw/workspace/gbrain`

- [2026-05-02_deep_X推文摘要] X 推文每日消化简报 — 2026-05-02：> 来源：ideas.md v2.0 已过滤 | 扫描时间 07:42 CST
- [2026-05-02_x_digest] X 情报日报 2026-05-02：抓取账号：11 个 | 通过过滤：46 条

## Promoted From Short-Term Memory (2026-05-03)

<!-- openclaw-memory-promotion:memory:memory/2026-04-27.md:23:23 -->
- 优先级：FxTwitter > Jina > 其他工具（agent-reach/bird/x-to-markdown/agent-browser 均需要 cookie） [score=0.856 recalls=0 avg=0.620 source=memory/2026-04-27.md:23-23]

### 2026-05-03 (Dream 自动整合)
- [2026-05-03_deep_X推文摘要] X 情报日报 2026-05-03（周日）：> 抓取时间：09:00 CST | 监控账号：10 个 | 通过过滤：13 条
- [2026-05-03_gbrain_daily_check] gbrain Daily Health Check — 2026-05-03：**Status**: ⚠️ Update available

### 2026-05-04 (Dream 自动整合)
- [2026-05-04_github_management_baseline] GitHub 托管基线 - 2026-05-04：厂长已授权 Kitt 按自己的节奏完全管理 GitHub 账号 `95369149`（简单）。

- [2026-05-04_openrouterfree_xiaoxiaodong01_提示词资产提纯] @xiaoxiaodong01 提示词资产提纯报告：**生成时间**: 2026-05-04 15:37 GMT+8
- [2026-05-04_xiaoxiaodong01_提示词倒序抓取落地] @xiaoxiaodong01 提示词相关倒序抓取落地：抓取时间：2026-05-04
- [2026-05-04_xiaoxiaodong01_最近一周提示词资产提纯] @xiaoxiaodong01 最近一周提示词资产提纯：生成时间：2026-05-04
- [2026-05-04_zhongying14_AI人像Prompt拍摄方案框架] AI 人像 Prompt 拍摄方案框架｜麻酱AI实验室：来源：`https://x.com/zhongying14/status/2050973647548866765`

### 2026-05-07 (Dream 自动整合)
- [red_sun_ai_project_validation_template] 红太阳 AI 项目验证模板（借鉴 codex-startup-pressure-test-skill）：> 核心思想：在写代码前，先验证 idea 是不是幻觉。
- [x_digest_optimization] X 情报日报优化方案：1. **0-10 分评分机制**

- [2026-05-07_kitt_v2.2_灰度收关复盘] v2.2 排兵布阵灰度收关复盘：> 审核人：Kitt | 日期：2026-05-07 | 灰度起始：2026-03-26 | 运行天数：42 天

### 2026-05-08 (Dream 自动整合)
- [2026-05-08_kitt_anthropic_skill_guide_精要] Anthropic 官方《Skill 构建完全指南》33 页 · 精要 + Kitt 系统优化清单：- 日期：2026-05-08
- [2026-05-08_kitt_md2wechat_skill_评估] md2wechat-skill · 公众号自动化 CLI（极客杰尼） · 评估报告：- 日期：2026-05-08

### 2026-05-09 (Dream 自动整合)
- [2026-05-09_kitt_notebooklm_skill_P0优化与归档] notebooklm-kitt Skill P0 优化 + 废弃目录归档：- 日期：2026-05-09 00:30 GMT+8
