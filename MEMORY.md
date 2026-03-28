# MEMORY.md

这是系统的全局高层记忆与反思文件，用于记录长期的行为模式、系统级教训和持续优化的洞察。

## 反思洞察

### 2026-03-02

1. **子 Agent 稳定性与超时风险**：在派发 X 监控脚本部署和提示词库集成任务时，`deep` 和 `main` 均出现超时或 Tool not found 失败。**教训**：对于需要连续多步写文件和验证的任务，子 Agent 容易中途失败。**改进**：复杂代码任务尽量由主 Agent (jimmy) 拆解分步直写，或严格限制子任务的作用域（单次仅执行一个具体脚本的编写）。
2. **跨渠道推送权限壁垒**：在执行 `daily_digest_pipe` 任务后，尝试在 Telegram 绑定的会话中直接使用 `message` 工具向 Discord 推送长文失败（Cross-context messaging denied）。**教训**：跨渠道消息不可在受限会话中直接跨越。**改进**：未来的跨渠道自动化推送必须配置在 `isolated` session 的 cron 任务中，或者调用系统底层 API 完成，不能混用当前对话会话。
3. **外部信息的低成本摄取模式（零消耗查询）**：发现主节点由于顾虑 Token 消耗而较少主动调用外链验证。为此落地了《外链零消耗查询协议》。**模式**：需要海量外网长文本时，通过脚本/子 Agent 搜索 -> 写入 `memory/shared/` -> 主节点只读取摘要回复，保持主上下文清爽。

### 2026-03-03

1. **单点故障连锁瘫痪（连续第2天出现）**：早上所有付费 provider 同时失效 + exec 工具 module not found，系统完全瘫痪半天。**教训**：API key 失效 + 运行环境损坏可以同时发生，且没有自动恢复机制。**改进**：① 需要本地健康检查脚本（不依赖 OpenClaw 自身）作为最后防线；② 考虑 launchd 级别的 watchdog，检测 gateway 异常时自动重启。
2. **配置漂移是慢性毒药**：全量校准发现多个文件（排兵布阵.md、大脑中枢.md、.abstract）的 Agent 编制信息互相矛盾。**模式**：每次改 openclaw.json 后只更新了部分文件，日积月累导致系统认知分裂。**改进**：已建立全量校准 v6.0 流程，以 openclaw.json 为唯一真相源，其他文件必须同步更新。这个问题连续 3 天出现，考虑写入 SOUL.md。
3. **子 Agent 输出必须审查，不能盲信**：deep 写的 Lyra V5.4 有 6 个问题（工具混入模型表、视觉协议跑题、Token 原则绑定具体工具名）。**模式**：子 Agent 倾向于"看起来完整"但细节经不起推敲。**改进**：所有子 Agent 交付物必须由 jimmy 逐项审查，尤其是涉及架构/规则类文档。
4. **web_fetch 被代理拦截是常态**：今天尝试抓取 10+ 个外链全部被 Surge 代理拦截（resolves to private/internal IP）。**教训**：web_fetch 在当前网络环境下可靠性极低。**改进**：外链读取优先用 agent-reach（走独立通道），web_fetch 仅作为备选。
5. **质量导向 vs 数量导向**：谷歌一条龙方案从 v1（API 流水线）迭代到 v2（网页端+质量检查清单），核心转变是厂长明确要求"要质量不要数量"。**教训**：方案设计要先确认厂长的核心诉求，不要自作主张追求效率最大化。\n### 2026-03-05\n1. **用确定性脚本替代LLM执行IO操作**：引入了 `apply_manifest.py` 脚本统一执行文件落盘，将子Agent的职责限定为只输出严格的 JSON manifest。这解决了长期存在的子 Agent 写文件成功率极低（<30%）的问题。\n2. **打破"无界上下文积累"反模式**：在 Jimmy 的调度闭环中，不再将子 Agent 的完整 JSON 响应贴回上下文，而是只保留执行摘要和写入路径，极大延缓了上下文污染，保证长周期运行的智商稳定性。\n3. **建立校验门与有界重试机制 (Bounded Retry)**：单纯依赖提示词约束格式不可靠，升级为"脚本校验 → 若失败返回错误信息给原Agent → 重试1次 → 再失败则升级(escalate)"的工程化闭环，让系统具备容错和自愈能力。\n4. **按"决策风险"而非"能力标签"划分Agent边界**：将 logic 与 kitt 合并，消除了角色重叠导致的路由模糊。明确了使用"思考链(thinking)模型"的高成本Agent仅在超过2步推理或不可逆重大决策时才被触发。

### 2026-03-08

1. **安全危机与脱敏原则**：Opus 审计报告揭示配置文件中的 API Key 全部为明文，暴露了明文密钥在复杂环境中的风险（尤其是供应链投毒）。**教训/模式**：所有凭据必须外置并以 `SecretRef` (环境变量) 的形式引用，系统必须定期由高级 Agent (Opus) 审查密钥存放状态与配置一致性。
2. **配置权威源冲突（持续存在）**：排兵布阵文档与 `openclaw.json` 在 `logic` 等 Agent 编制上仍未对齐（连续多日发现）。**教训/模式**：文档记录与配置文件之间的"记忆漂移"是顽疾，单次校准无法根治，必须在系统层面将 `openclaw.json` 设为唯一"真值(Source of Truth)"，在变更时强制触发连带审计更新。此模式反复出现，应写入 SOUL.md。
3. **"真"路由模式与主模型切换授权**：厂长明确授权，不仅是子 Agent 派发，主 Agent 也可以根据任务（如方案PK、高难度推理）主动调用更强的模型（如 Opus）做仲裁或接管。**教训/模式**：打破"默认模型必须一直在线"的执念，按"模型特质×擅长领域×网络稳定性"灵活调度，并引入 Opus 作为高阶仲裁器。

### 2026-03-11

1. **上下文工程 > 提示词工程**（来源：Karpathy、Gleeson 等多篇 X 帖子交叉验证）：工业级 LLM 应用的核心不是"写一句神 prompt"，而是**把正确的信息、工具、状态、历史，在正确时机装进上下文窗口**。子 Agent 开工前只读最相关 2-3 份记忆；长任务中间态写 shared/；规划与执行分离。这是系统下一阶段的主矛盾。
2. **复杂任务必须拆小，单 Agent 不吞多步**（来源：Pierno、Yashwanth）：3 步以上任务默认拆成"检索→分析→写入→验收"4 段。单任务 Agent 比全能 Agent 更稳。新 skill/自动化走"四步法"：单 Agent 原型 → 结构化输出 → 多工具 → 多 Agent 编排。
3. **可靠性 > 新功能**（来源：OpenClaw 社区帖、Konzelmann、AlphaClaw）：当前最大短板不是能力不足，而是任务闭环和可视化管理。下一阶段优化重点从"再加能力"转向"更稳地交付"：任务创建→状态→超时→失败重试→结果验收→共享记忆落盘，逐项补齐。
4. **Provider 全线故障的正确应对**：mynewapi 502 + mygptapi 401 导致断联 6 小时。**教训**：Fallback 链必须把免费稳定 provider（gemini-cli）排第一位，不能排最后。已修复。
5. **记忆整合层落地**：从 Google Always-On Memory Agent 项目获得启发，不照搬技术栈，而是在现有体系上补"主动整合层"：定时扫描 shared/ → 提取结构化信息 → 生成日摘要 → 沉淀 insights。已写脚本 + 配 cron 每晚 22:00 自动跑。
6. **路由模式必须开启，不能等厂长指令**：厂长明确要求"开路由模式，以后不用再说了"。**模式**：收到任务后 3 秒内完成路由决策，自己能搞定就直接做，需要派发就按意图桶匹配 agent，不再问"你要哪个方案"。这是对"Context, not Control"的落地。
7. **外链读取能力是刚需**：今天多次遇到 X 链接读不到内容（fxtwitter 失效、web_fetch 被拦截），最终用 agent-reach 解决。**教训**：外链读取工具必须有多层兜底（fxtwitter → agent-reach → browser），单一工具不可靠。已验证 agent-reach 可用。

### 2026-03-12

1. **工具选择优先级错误**：厂长要求从 NotebookLM 下载文件，我选择了操作网页版浏览器（最笨、最浪费 token），而不是直接用 `notebooklm` CLI 或 skill。**教训**：遇到任务先检查是否有现成工具/CLI/skill，优先用自动化工具，网页操作是最后选择。
2. **notebooklm CLI 连接失败**：`notebooklm artifact list` 和 `notebooklm source list` 报错 "Connection failed"，可能是认证过期或网络问题。**改进**：遇到 CLI 失败时，先 `notebooklm status` 检查认证状态，必要时 `notebooklm login` 重新登录。
3. **效率原则**：厂长明确要求"不能拣选最笨最浪费 token 的办法，要高效"。**模式**：任务执行前必须评估工具选择，优先级：CLI/API > Skill > 脚本 > 浏览器操作。浏览器操作仅用于无其他选择时。

### 2026-03-15

1. **跨渠道消息继承是隐蔽的系统性风险**：Discord 400 根因不是参数串台，而是大量 job/session 默认持有 `to/lastTo=telegram:8184569453`，在 delivery 继承链路中被复用。**教训**：normalize 层必须做渠道硬校验，不能只依赖上游 `channel === lastChannel` 判断。**改进**：已在 `discord.ts` 新增 `FOREIGN_CHANNEL_PREFIX_RE` 硬拒绝外渠道前缀，后续需在 `targets.ts` / `agent-delivery.ts` 补同渠道继承限制。
2. **"聊几句就失灵"的真凶是 tool item id 格式不兼容**：获得关键报错 `HTTP 400: Invalid 'input[4].id': 'tooluse...' Expected an ID that begins with 'fc'`，证明问题不是模型能力或用户设置，而是 provider replay/normalize 层在处理带工具历史的会话时，未将 `tooluse...` 转换为上游要求的 `fc...` 格式。**教训**：协议层兼容问题比模型参数问题更隐蔽，必须拿到原始错误体才能定位。**改进**：下一步需进入代码层搜索并修补 `tooluse` / `input[*].id` / replay normalize 逻辑。
3. **Chrome CDP 打通但 Perplexity 被风控是两个独立问题**：成功修改 `chrome-cdp-skill` 支持连接 `127.0.0.1:9869` 的 PinchTab 实例，CDP 本身已通；但 Perplexity 进入 Cloudflare Managed Challenge，点击验证后仍未放行。**教训**：自动化浏览器（PinchTab/headless）指纹重，容易被强风控站点拦截；真实用户态 Chrome 应作为主刀，自动化实例只做备用。**改进**：外链碰撞工具路由应固定为：CLI/agent-reach 先读 → 真实用户态 Chrome 补登录态 → 外部模型做内容碰撞 → 自动化浏览器只做补刀。
4. **方案型任务必须外部碰撞，不能闷头自己写**：厂长明确要求外贸拓客系统不要主 Agent 自己写，应借助外链高级模型/外部框架生成方案，主 Agent 只负责提要求、验收、搬运。**教训**：方案型任务要看动作和产出，不要停留在表态；遇到问题要自己想办法而不是卡住。**改进**：已整理出《红太阳外贸拓客系统 V1 框架》并写入 `memory/shared/`，后续类似任务优先走外部碰撞链路。
5. **浏览器调试问题应尽早查端口/进程/用户目录**：`chrome-cdp-skill` 默认找 `DevToolsActivePort`，但机器上真正开启调试的是 PinchTab 的 `9869` 实例，主 Chrome 未开远程调试。**教训**：不能一直靠"你再开一下开关"推进，应该 5 分钟内直接查端口/进程把根因钉死。**改进**：已修改脚本支持 `CHROME_CDP_BROWSER_WS_URL` 和 `CHROME_CDP_PORT` 环境变量，可直接指定 CDP 实例。

### 2026-03-16

1. **协议错配比代码 bug 更隐蔽**：Opus 400 错误追查了多轮，最终根因不是 replay/tool id 代码问题，而是 `mynewapi` provider 被配成 `openai-completions`，但实际后端要求 `anthropic-messages`。**教训**：遇到 LLM 调用 400，先查协议层配置（api 类型、baseUrl 格式、maxTokens），再查代码逻辑。协议错配在日志里不会直接说"协议不对"，只会给一个看似代码问题的 400。
2. **配置变更必须最小化+备份+验证三步走**：今天 mynewapi 修复走了正确流程：先备份（.bak.时间戳）→ 最小补丁（只改必要字段）→ config.get 验证结构可解析 → gateway restart。这个流程有效避免了"改废了"的风险。**模式**：任何 openclaw.json 变更都必须走这三步，不能跳过。
3. **密钥脱敏是一次性工程，不是反复修**：今天 SecretRef 迁移完成，13 个密钥从 openclaw.json 抽出写入 ~/.openclaw/.env。**教训**：明文密钥一旦进配置文件就会随备份/日志扩散，必须在第一次配置时就用 SecretRef，不能等到审计发现再补救。
4. **外贸拓客的核心差距是海关数据**：外链碰撞发现现有方案完全缺失海关数据这条线索来源。海关数据能直接查到"谁在进口振动刀设备"，精准度远超 LinkedIn 盲搜。**改进**：T-116 升级方案补入海关数据（ImportYeti 免费版先跑通），作为线索抓取第一优先级。
5. **sessions_spawn subagent 的 streamTo 参数只支持 runtime=acp**：今天三次尝试用 streamTo=parent 做 subagent 冒烟测试全部失败。**教训**：subagent 模式不支持 streamTo，需要用 sessions_history 轮询结果，或改用 runtime=acp。记住这个参数限制，不要再踩。
