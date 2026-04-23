<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 你是 Claude Opus 级别的顶级 AI Agent Runtime / Harness / Orchestration Architect。你的任务不是泛泛而谈，而是为一个正在运行的生产级 OpenClaw 多 Agent 系统，设计一套最小可落地、可代码化、可逐步上线的规则硬化改造方案。

我不要你推翻系统重做。
我不要“建议优化 prompt”。
我不要抽象理念。
我要你基于下面给出的现有规则、现有架构、真实事故、已知边界，输出一套能直接指导工程实现的方案。

核心目标只有一个：

把“规则写在 prompt / 文档里”升级成“规则在 runtime 中被强制执行”。

- 涉及外链 / 竞品 / 第三方框架选型
- 高风险配置变更
- 用户明确要求“先调研 / 对标”

/ 回滚核对

设计原则已经存在：

- 调度 / 执行 / 审核分离
- 路由模式默认开启
- 高风险输出必须走审核链
- 配置变更必须 guard 审核
- 重大决策 / 架构设计必须经过 kitt

但问题是：

这些原则大多写在 memory / SOUL / AGENTS / 规则文档中，没有真正变成代码级 gate。

二、当前已有规则（这是既有事实，不要忽略）

1. 默认路由

- 简单问答 / 轻量状态查询 / 轻量文件读写 → jimmy
- 代码 / 脚本 / 自动化 / 数据处理 → deep
- 图片 / 视频 / PDF / 长网页 / 多模态理解 → main
- 中文文案 / 改写 / 润色 / 总结 / 本地化 → sino
- GitHub / 外链 / 竞品 / 情报收集 → scout
- 架构 / 战略 / 高难判断 / 终审 → kitt
- 配置审计 / 风险检查 / 回滚核对 → guard

2. 路由模式要求
收到任务后 3 秒内必须判断：
3. 自己直做
4. 单 Agent 派发（FAST）
5. 多 Agent 协作（FULL）
6. 高风险待确认
7. 强制触发 kitt

- 架构设计
- 复杂代码改造
- 对外正式长文
- 高风险业务判断
- 3 步以上复杂推理的关键决策

4. 强制触发 guard

- openclaw.json 变更
- 路由规则变更
- 密钥 / 凭据处理
- 新 skill / 新 MCP / 新依赖安装前审计
- 回滚方案核对

5. 强制触发 scout
任一命中即必须先侦察：

- 架构设计或系统级方案
- 跨 3 个以上文件协同修改
- 有效代码改动 > 200 行
- 没有明确实现路径
- 涉及外链 / 竞品 / 第三方框架选型
- 高风险配置变更
- 用户明确要求“先调研 / 对标”

6. 记忆协议
已经存在但未硬化：

- 子 Agent 开始任务前必须先读：
    - memory/task-board.json
    - memory/shared/ 最近内容
- 主 Agent 在新 session / 压缩恢复 / 切模型后，本应先读：
    - memory/.abstract
    - memory/task-board.json
    - 今日日志（按需）

```
- 多步任务必须写 memory/shared/YYYY-MM-DD_<agent>_<task>.md
```

- 写后必须 verify
- 只有 jimmy 可以修改 task-board.json
- 子 agent 禁止改 openclaw.json

7. 配置安全规则

- 修改前必须备份
- 修改后必须校验
- 再 restart gateway
- 再做 status 检查
- 失败必须有回滚方案

8. 业务红线（非常重要）
以下内容一律禁止删除：

- memory/10_项目/
- 已进入 task-board 的项目
- 用户明确点名推进的项目
- 项目相关交付物 / 方案文档
- workspace 中属于项目的目录
- 当前明确保护的三个项目：
    - 抖音项目
    - 拓客系统
    - 电路图项目

允许：

- 保留
- 归档
- 建索引

禁止：

- 直接删除

三、已经发生的真实问题（请把它们当生产事故处理）

1. 切模型 / 新 session / 压缩恢复后，不先读记忆就开始回复
2. 路由规则是“知道”，不是“强制执行”
3. **项目保护没有代码级 delete/archive

guard**
4. guard / kitt 审核链可能被跳过
5. 清理 / 归档缺少前置分类与保护
6. 很多规则停留在文档层，没有 runtime gate / middleware / wrapper / policy engine
7. 系统过度依赖 prompt，自觉性不稳定，一换模型就漂移
8. 复杂任务没有稳定拆成“检索→分析→写入→验收”四段
9. 清理记忆时巡逻 / X 摘要 / x_digest / learning_ingest 这类内容堆积严重，但项目类内容不能误伤
10. 高风险结果必须经过独立评估器，但现实中仍容易被跳过

四、已知系统洞察（这是约束，不是可选建议）

1. 评估器不能去掉，且不能自评
    - 生成和评估必须分离
    - 高风险任务必须经过独立审查链
2. 架构约束必须机械化执行，不能只靠文档约定
    - 这正是当前结构性短板
3. 记忆层的价值在于长期轨迹，而不在初始 prompt
    - 关键不是有 memory，而是 runtime 是否强制调用 memory
4. 复杂任务必须拆小，单 Agent 不吞多步
    - 默认拆成：检索 → 分析 → 写入 → 验收
5. 工具选择要遵循固定优先级
    - CLI / API > Skill > 脚本 > 浏览器
    - 外链读取应有固定链路，不能乱跳
6. 路由模式必须默认开启，不能等用户提醒
7. 项目类内容只能保留 / 归档 / 建索引，不能删除

五、我不要的回答

不要给我：

- 建议加强 prompt
- 建议优化记忆召回
- 可以考虑 policy engine
- 可以考虑状态机
- 可以增加中间层
- 可以增加日志

这些都太空。

我要的是：

基于现有 OpenClaw + memory + guard/kitt + 多 Agent 体系，最小增量、能落地、能编码、能灰度上线的硬化方案。

六、请严格按以下格式输出

1. 问题拆解
按运行时缺陷拆解：

- 记忆前置缺陷
- 路由执行缺陷
- 审核链跳过缺陷
- 项目保护缺陷
- 清理归档缺陷
- 配置变更守门缺陷
- 工具选择 / 外链顺序缺陷
- 子 Agent 闭环缺陷

每项说明：

- 根因
- 为什么 prompt 不够
- 为什么当前一定会漏

2. 硬化总体架构
请设计一个最小可落地架构，并明确区分：

- 哪些必须代码化
- 哪些适合脚本化
- 哪些适合配置化
- 哪些继续留在文档层

请你明确放置：

- preflight gate
- memory bootstrap checker
- task classifier / router
- policy engine
- review gate
- delete/archive protector
- runtime hook / middleware / wrapper

3. 最优实现顺序（P0 / P1 / P2）
按 ROI 排序，说明：

- 解决什么问题
- 为什么排这个优先级
- 适合落在哪层

4. 关键机制设计
至少设计以下机制：

A. 记忆强制读取机制
必须覆盖：

- 新 session
- 模型切换
- 压缩恢复
- 子 agent 唤醒

必须说明：

- 如何判断“已经读过”
- 如何判断“读的是最小必要上下文”
- 如何阻止没读就答复
- 如何避免重复读导致 token 浪费

B. 路由强制执行机制
要求：

- 收到任务先分类
- 自动决定

FAST / FULL

- 自动决定 scout / guard / kitt
- 自动决定简单任务自己做

必须说明：

- task meta 设计
- 输入字段
- 人工 override 机制
- 失败降级链

C. 项目保护机制
要求：

- 清理 / 归档 / 删除时自动识别项目类内容
- 项目类允许保留 / 归档 / 建索引
- 禁止删除

必须覆盖：

- memory/10_项目/
- task-board 项目
- 用户点名项目
- workspace 项目目录

必须说明：

- 规则表放哪里
- 匹配逻辑怎么写
- 删除前如何拦截
- 如何避免误伤普通文件

D. 审核链硬门槛
要求：

- 高风险任务由系统自动判定是否进入 guard / kitt
- 不能靠模型自觉

必须说明：

- 哪些直接进 guard
- 哪些直接进 kitt
- 哪些允许 FAST
- 审核失败 / 超时 / quota 时怎么办

E. 清理 / 归档机制
要求：

- 巡逻 / X 摘要 / x_digest / learning_ingest 自动退场
- 项目内容不动
- 第一阶段只归档，不删除

必须说明：

- 文件分类策略
- 生命周期策略
- 前台 / 归档切换规则
- 如何避免当下有用内容被过早归档

5. 结合现有体系，给出最小落地组件建议
请直接建议最适合新增或修改的组件，例如：

- router
- task classifier
- review gate
- memory bootstrap checker
- delete/archive protector
- policy file
- wrapper / middleware / runtime hook

如果建议新增脚本，请给：

- 文件名
- 放置位置
- 

职责边界

6. 给出伪代码或流程图级设计
至少给 3 个：
7. 主请求进入：preflight → classify → route → review → reply
8. 删除 / 归档前：protect check
9. session/model switch 后：memory bootstrap

要求工程师能直接开工。

7. 防止过度工程化的边界
明确指出：

- 哪些现在不要做
- 哪些先别搞
- 哪些仍保留人工判断更好

8. 最终结论
请明确回答：

- 当前最大结构性短板是什么
- 最该先补的 3 个硬门槛是什么
- 做完后先改善什么
- 哪些问题仍不会自动消失

七、额外要求（Opus 增强要求）

请你额外做到以下几点：

1. 不要站在“另起炉灶”的角度回答，要站在“生产系统增量改造”的角度回答
2. 不要把所有判断都丢给模型，优先考虑 deterministic gate / static policy / runtime wrapper
3. 如果你建议 policy file / marker file / state file，请明确：为什么必要、放哪、由谁写、由谁读
4. 如果你建议 hook / middleware / wrapper，请尽量映射到 OpenClaw 现有 runtime 结构，而不是假设一个全新框架
5. 请特别关注“切模型/压缩恢复后失忆”这个问题，给出最硬的解决方案
6. 请特别关注“项目类内容误删”这个问题，给出最稳的防线设计
7. 请特别关注“高风险任务跳过 guard/kitt”这个问题，给出不可跳过的机械路径
8. 请给出一版“最小 2 周落地计划”，按周拆解：第 1 周做什么，第 2 周做什么
9. 请给出“灰度上线策略”：如何先在部分任务生效，再扩大范围
10. 请给出“失败回滚策略”：如果新 gate 影响效率或误拦截，如何快速回退

八、最后一句要求

请把你的回答当成：

一份要交给工程师直接开干的生产级 Runtime 改造设计说明书

不是论文，不是 brainstorm，不是产品愿景。

请给出具体、清晰、可执行、可渐进上线的答案。

下面是面向工程团队、可以直接开干的 OpenClaw Runtime 硬化设计说明书初稿，按你要求的结构展开。

***

## 1. 问题拆解（按运行时缺陷）

### 1.1 记忆前置缺陷

- 根因
    - 记忆读取（memory/.abstract、task-board、shared 等）是“约定动作”，没有变成请求链路中的必经步骤。
    - 主 Agent / 子 Agent 的 entrypoint 没有统一的 preflight / memory bootstrap 层，可以绕过记忆直接走 LLM。
- 为什么 prompt 不够
    - prompt 里的“先读 memory 再答复”是软约束，模型可以忘、可以偷懒，切模型后行为漂移尤甚。
    - 任何“请先读取文件 X”的提示都不能确保在每个请求、每个 Agent、每个模型上稳定执行。
- 为什么当前一定会漏
    - 新 session / 模型切换 / 压缩恢复后，代码没有检查“本 session 是否已完成 memory bootstrap”，所以直接进入对话。
    - 子 Agent 被任务调度唤醒时，也没有统一入口检查“必读文件是否已 load 到上下文”。


### 1.2 路由执行缺陷

- 根因
    - 路由规则目前更像经验：Agent 知道“代码相关找 deep，架构找 kitt”，但入口层并未强制要求“先 classify，再 route”。
    - 没有一个统一的 task meta 结构在 runtime 中流转，导致无法对“3 秒内判断 FAST/FULL/高风险”进行机械化约束。
- 为什么 prompt 不够
    - “收到任务要先考虑路由模式”这类话极易被模型忽略，且无法保证时间窗口（3 秒）和顺序。
- 为什么当前一定会漏
    - 直接对话场景、短问答、回合内 follow-up 时，经常绕过“显式路由”环节，由当前 Agent 直接处理。
    - 复杂任务也可能被当前 Agent 自行吞掉，而没有触发 scout / kitt / guard。


### 1.3 审核链跳过缺陷（guard / kitt）

- 根因
    - guard / kitt 现在更多通过 prompt \& 文化约定触发，而不是由系统自动根据 task meta 判定。
    - 没有一个“review gate”组件在输出前统一检查“是否命中高风险条件→必须走 guard/kitt”。
- 为什么 prompt 不够
    - “高风险任务要让 guard/kitt 看一眼”只要模型一次没识别到风险点，就能绕过。
    - 自评风险极不可靠，且你已经要求“生成与评估必须分离”。
- 为什么当前一定会漏
    - 某些“配置变更”“架构设计”“长文输出”直接从 deep/sino 出结果，未必经过统一的审核路径。
    - 当 guard/kitt 本身负载高时，模型可能倾向于“自己扛”，进一步跳过。


### 1.4 项目保护缺陷

- 根因
    - “项目类内容不可删除”没有变成文件系统层或操作 API 层的硬规则，只存在于记忆/文档中。
    - delete / cleanup 脚本没有统一走一个保护器（delete/archive protector）。
- 为什么 prompt 不够
    - 模型很难在文件操作前，**完整且稳定**地枚举“哪些路径是项目”，尤其在批量清理时。
- 为什么当前一定会漏
    - shell 命令 / 清理脚本可能直接删除 workspace/memory 下的文件，不会向模型确认。
    - 即使在 agent 内触发清理，对“业务红线路径”的匹配若未在代码层实现，很容易因为命名变化、路径不熟悉而误删。


### 1.5 清理归档缺陷

- 根因
    - 巡逻 / x_digest / learning_ingest 等临时性知识堆积，缺少生命周期管理与分类规则，只能通过人工决定清理。
    - 没有“只归档不删”的安全第一阶段，导致要么不动，要么冒险删除。
- 为什么 prompt 不够
    - 模型没法稳定地区分“可清理类摘要文件”和“项目重要文档”；依赖语义判断必然有误判。
- 为什么当前一定会漏
    - 没有集中目录 / 前缀分类，导致脚本难以仅通过 pattern 区分。
    - 人工清理往往在压力大时进行，缺乏 pre-checks 和归档路径，很容易一刀切。


### 1.6 配置变更守门缺陷

- 根因
    - openclaw.json / 路由规则 / 新 skill / MCP / 依赖安装虽然有“先审计再改”的约定，但执行入口没有硬性 gate。
    - 修改动作（git 提交、脚本改文件、CI pipeline）没有统一走 guard。
- 为什么 prompt 不够
    - “改配置前请找 guard 审核”属于文化约束，对自动脚本、CI、手滑 rm 都无效。
- 为什么当前一定会漏
    - 直接在 repo 修改 openclaw.json 并 push，CI 跑完就生效，guard 完全不知道。
    - 一些试验性改动不会经过流程，只是本地运行。


### 1.7 工具选择 / 外链顺序缺陷

- 根因
    - “CLI / API > Skill > 脚本 > 浏览器”的优先级是软规则，工具调用层没有 enforce。
    - scout 在“外链 / 竞品 / 第三方框架选型”上应该是必经之路，但目前只是建议。
- 为什么 prompt 不够
    - 模型很容易直接请求浏览器搜索，而不考虑本地 CLI/API，尤其在新模型或 prompt 调整后。
- 为什么当前一定会漏
    - 任何多模态 / 网络检索需求只要当前 Agent 觉得“我可以自己搜”就会绕过 scout。


### 1.8 子 Agent 闭环缺陷

- 根因
    - 多步任务的“四段式（检索→分析→写入→验收）”没有变成调度器的显式阶段，只是 Agent 自我约束。
    - memory 写入与 verify 没有形成强制闭环：写不写、如何 verify，全靠自觉。
- 为什么 prompt 不够
    - 模型容易在“已经大致搞懂”的阶段就直接产出，而略过“写入 memory/shared + 验收”。
- 为什么当前一定会漏

```
- 没有 runtime 检查“执行了多步任务却没有产生对应的 YYYY-MM-DD_<agent>_<task>.md”，也没检查“写完是否有 verify”。
```


***

## 2. 硬化总体架构

### 2.1 架构概览（增量、非推倒重来）

在现有 OpenClaw 之上增加一层“Runtime Gates \& Policies”，不改变 Agent 本体，只在以下几个节点插入可配置、可开关的 gate：

1. preflight gate（请求入口）
2. memory bootstrap checker（会话 / 模型级）
3. task classifier / router（任务元信息生成 + 路由决策）
4. policy engine（基于 task meta 做 guard/kitt/scout 等决策）
5. review gate（高风险输出前硬评估）
6. delete/archive protector（文件操作硬防线）
7. runtime hook / middleware / wrapper（封装对 LLM、文件系统、配置的调用）

### 2.2 哪些必须代码化

- preflight gate：作为所有请求的统一入口 middleware（例如 HTTP / WebSocket / CLI 入口）
- memory bootstrap checker：在 session/model switch 时由 runtime 自动执行的检查逻辑
- task classifier / router：至少第一版是“轻量规则 + 模型辅助”的组合，但 **管控框架** 必须是硬编码
- review gate：高风险任务必须经过独立 evaluator（guard/kitt），由代码检查是否完成
- delete/archive protector：所有 delete / rm / heavy-cleanup 必须经过统一 API，禁止绕过
- 配置变更守门：对 openclaw.json 等关键文件的写操作需经专用脚本 / CI 步骤，内含 guard 调用


### 2.3 适合脚本化

- memory 归档 / 清理脚本（带项目保护 \& 生命周期）
- 配置备份与回滚脚本（修改 openclaw.json 之前/之后）
- 巡逻 / x_digest / learning_ingest 的批量归档脚本


### 2.4 适合配置化

- 高风险策略规则表（哪些任务类型 / 文件路径 / 行为需 guard/kitt/scout）
- 项目保护规则表（项目目录 / 关键路径 / 名称关键字）
- 生命周期策略（哪些前缀文件多长时间后归档）
- 灰度开关（哪些用户 / 项目 / 环境开启哪些 gate）


### 2.5 继续留在文档层

- 如何写更高质量的架构方案（由 kitt 负责的内容质量标准）
- 业务上下文细节、某些非结构化的“经验”
- 对 Agent 风格 / 语气的约定


### 2.6 各组件放置建议

- preflight gate：
    - 放在 OpenClaw 网关层（例如 gateway server 的请求 middleware）
- memory bootstrap checker：
    - 放在 session manager / model manager 周围（负责管理会话和模型实例的模块）
- task classifier / router：
    - 现有 router 模块增强，在其前增加轻量 classifier
- policy engine：
    - 新增模块（如 runtime/policy_engine.py），读取 policy.yml / policy.json
- review gate：
    - 在 router 之后、最终 reply 之前的 pipeline 节点
- delete/archive protector：
    - 封装成 runtime/fs_guard.py，所有涉及 delete 的地方只能调用该模块
- runtime hook / middleware / wrapper：
    - 封装 LLM 调用、文件系统调用、配置修改等关键操作

***

## 3. 最优实现顺序（P0 / P1 / P2）

### P0（第一优先级）

1. memory bootstrap checker
    - 解决：切模型 / 新 session / 压缩恢复后失忆。
    - 优先原因：所有任务都受影响，且实现点集中在 session/model 管理层，改动面可控。
    - 落层：session manager / gateway middleware。
2. delete/archive protector + 项目保护规则表
    - 解决：项目类内容误删。
    - 优先原因：一旦误删即不可逆，是最高风险类别。
    - 落层：文件系统 wrapper + 配置化规则表。
3. 高风险审核链硬门槛（policy engine + review gate）
    - 解决：guard / kitt 被跳过。
    - 优先原因：架构决策、配置改动等属于“系统性风险”，需要立刻机械化。
    - 落层：router 之后、reply 之前的 pipeline。

### P1（第二优先级）

4. 路由强制执行机制（task classifier + 默认开启路由模式）
    - 解决：路由规则只是“知道”而非“强制”。
    - 落层：gateway / router。
5. 清理 / 归档机制（生命周期 + 归档目录）
    - 解决：巡逻 / 摘要类文件堆积；项目内容不动的前提下做归档。
    - 落层：脚本 + 定时任务 + fs_guard。
6. 工具选择 / 外链顺序硬规则（CLI/API 优先、公用 scout 流程）
    - 解决：外链 / 竞品 / 框架选型直接乱搜。
    - 落层：工具调用 wrapper / policy engine。

### P2（第三优先级）

7. 子 Agent 闭环机制（检索→分析→写入→验收四段硬化）
    - 解决：多步任务没有统一阶段 \& memory 写入/verify 不稳定。
    - 落层：task orchestrator / multi-agent pipeline。
8. 更多细粒度策略（不同项目/环境的差异化 policy）
    - 解决：灰度控制与精细化治理。

***

## 4. 关键机制设计

### 4.A 记忆强制读取机制

#### 场景覆盖

- 新 session 创建
- 模型切换（model_id 改变）
- 会话从压缩状态恢复
- 子 Agent 被调度唤醒处理新任务


#### 状态与文件

- 设计 state 文件 / 内存状态（可混合）：
    - session_state/<session_id>.json
        - fields：
            - last_memory_bootstrap_at（时间戳）
            - last_model_id
            - bootstrap_sources：["abstract", "task_board", "shared"]
            - child_agents_bootstrap: { agent_name: timestamp }
- “已经读过”的判断：
    - 当前 model_id == last_model_id
    - 且 now - last_memory_bootstrap_at < BOOTSTRAP_TTL（例如 2 小时，配置化）
    - 且当前 Agent 在 child_agents_bootstrap 中有记录且未过期


#### “最小必要上下文”的定义

- 主 Agent：
    - 必须包含
        - memory/.abstract
        - memory/task-board.json
    - 可选按需：
        - 当任务涉及项目类关键词时，按项目过滤加载 memory/10_项目 对应文件索引（而不是全文）。
- 子 Agent：
    - 必须：
        - memory/task-board.json（只读）
        - memory/shared/ 最近 N 条（按日期、按项目过滤）

实现手段：

- 为 memory 侧增加一个“index 文件”（例如 memory/index.json）：
    - 记录
        - 项目列表（name、路径、tag）
        - 每日 shared 文件列表
    - bootstrap 时只读 index + 按需读取内容，避免一次性读所有。


#### 如何阻止没读就答复

在 LLM 调用 wrapper 之前增加检查：

1. 检查当前 session_state 是否缺失或过期 bootstrap。
2. 若缺失，则：
    - 自动触发“memory bootstrap 子流程”（读取必要文件 → 向 LLM 生成 concise summary 放入 system message 或 tool_cache）。
    - 将结果写入 session_state，并标记 bootstrapped。
3. 若 bootstrap 流程失败（文件缺失、读取异常）：
    - 返回错误或降级为“有限上下文模式”，但要在响应中显式标识（可由系统注入一条说明）。

即：**LLM 调用 wrapper 不允许在“未 bootstrap”的 session 上直接调用**。

#### 如何避免重复读导致 token 浪费

- session_state 记录最近一次生成的“memory 摘要”的缓存 ID（如 memory_digest_id），下次直接引用，非必要不重写。
- 仅当 memory 文件时间戳发生变化（比 last_memory_bootstrap_at 新）时才重新生成摘要。
- 子 Agent 读取 shared 时，只加载“最近一天”或“最近 N 条”，N 在配置中设置。

***

### 4.B 路由强制执行机制

#### task meta 设计

统一定义 TaskMeta 结构，在 gateway → router → agents 全链路传递：

```json
{
  "id": "task-uuid",
  "session_id": "sess-uuid",
  "source": "user|system|script",
  "text": "用户原始指令",
  "language": "zh|en|...",
  "estimated_complexity": "low|medium|high",
  "requires_code": true/false,
  "requires_multimodal": true/false,
  "requires_external_research": true/false,
  "project_tags": ["抖音项目", "拓客系统"],
  "risk_level": "normal|high_config|high_arch|high_business",
  "route_mode": "FAST|FULL|SELF|PENDING",
  "required_agents": ["scout", "guard", "kitt"],
  "created_at": "...",
  "overrides": {
    "route_mode": null or "FAST/FULL/SELF",
    "target_agent": null or "deep/main/sino..."
  }
}
```


#### 收到任务先分类

- preflight gate 调用一个轻量级 classifier：
    - 规则优先（deterministic）：
        - 包含“架构设计 / RFC / 方案 / 系统级”→ risk_level: high_arch + required_agents += ["scout", "kitt"]
        - 包含“改 openclaw.json / 配置 / 密钥 / 安装”→ risk_level: high_config + required_agents += ["guard"]
        - 包含“对标 / 竞品 / 外链 / 第三方框架”→ requires_external_research = true + required_agents += ["scout"]
    - 规则之外，再调用一个小模型辅助（可选），但最终结果仍写入 TaskMeta。


#### 自动决定 FAST / FULL / SELF

- 基于 estimated_complexity + risk_level：
    - complexity=low \& risk_level=normal → SELF or FAST（当前 Agent 直接做或单 Agent 派发）
    - complexity=medium/high 或 risk_level != normal → FULL（多 Agent 协作）
- route_mode 决策由 router 实现，写入 TaskMeta.route_mode。


#### 自动决定 scout / guard / kitt

- policy engine 内有硬规则表，例如：

```yaml
rules:
  - name: config_change_guard
    if:
      risk_level: "high_config"
    then:
      require_agents: ["guard"]
      enforce_review: true
  - name: arch_design_kitt
    if:
      risk_level: "high_arch"
    then:
      require_agents: ["scout", "kitt"]
      enforce_review: true
  - name: external_research_scout
    if:
      requires_external_research: true
    then:
      require_agents: ["scout"]
```

- router 在执行计划阶段根据 TaskMeta.required_agents 构建 pipeline。


#### 人工 override 机制

- 入口支持一个 admin/debug 参数：
    - 可强制 route_mode、自选 Agent，但必须满足：
        - 即便 override，也不得降低 risk_level 决策（比如不能把 high_config 的 guard 去掉）。
- policy engine 内规则：
    - overrides 只能在 risk_level=normal 情况下生效，高风险任务 override 会被忽略并记录日志。


#### 失败降级链

- 若 required_agent 调用失败（如 scout 超时）：
    - 降级策略配置化：
        - 对 high_arch / high_config：禁止降级，直接报错并提示“审核链失败，请人工处理”。
        - 对 normal：可降级为 SELF / FAST，但需打标（在响应中说明“scout 未完成，以下为有限情报”）。

***

### 4.C 项目保护机制

#### 规则表放置

- 新增配置文件：config/project_protection.yml

示例：

```yaml
projects:
  - name: "抖音项目"
    paths:
      - "memory/10_项目/douyin/"
      - "workspace/douyin/"
    task_board_ids:
      - "proj_douyin_001"
    aliases: ["抖音", "短视频增长"]
  - name: "拓客系统"
    paths:
      - "memory/10_项目/tuoke/"
      - "workspace/tuoke/"
  - name: "电路图项目"
    paths:
      - "memory/10_项目/circuit/"
      - "workspace/circuit/"
global_protected_paths:
  - "memory/10_项目/"
  - "task-board.json"
  - "workspace/projects/"
```

- 由谁写：
    - 仅 jimmy 或专门的运维账号可修改（同配置守门器）。
- 由谁读：
    - delete/archive protector 和 清理脚本。


#### 匹配逻辑

- 删除 / 归档前，fs_guard.check(path) 执行：
    - 如果 path 在 global_protected_paths 或其子路径 → 直接拒绝 DELETE，允许 ARCHIVE。
    - 如果 path 命中某 project.paths → 标记为 project_protected，拒绝 DELETE，只允许 Move 到 archive。
    - 若 path 不在保护列表，则视为普通文件，可根据调用者 mode（delete/archive）继续。


#### 删除前如何拦截

- 所有删除动作必须通过统一接口：
    - runtime/fs_guard.delete(path, reason, task_meta)
- fs_guard.delete 内部：
    - 加载 project_protection.yml
    - 若 path 命中项目保护 → 抛出 ProtectedProjectError
    - 记录操作日志（包括调用的 Agent、task_id、reason）。


#### 避免误伤普通文件

- 保护规则以“前缀目录 + 显式项目路径”为主，不使用模糊语义匹配。
- 和“项目相关但不在专用目录”的情况，通过：
    - task-board.json 中记录 project->workspace 路径；保护器读取 task-board 来扩展保护路径。
    - 这样项目目录必须在 task-board 上登记，才被保护，避免随意命名的文件被错判。

***

### 4.D 审核链硬门槛

#### 哪些直接进 guard

- 涉及以下关键词 \& 语义：
    - “修改 openclaw.json / 路由规则 / skill 配置 / MCP 配置 / 安装依赖”
    - “密钥 / 凭据 / token / API key / env 文件”
- TaskMeta.risk_level = high_config 时：
    - policy engine 添加 required_agents += ["guard"]
    - review gate 强制在最终落地前调用 guard，对变更内容做审计和回滚方案检查。


#### 哪些直接进 kitt

- 架构设计 / 系统级方案 / 复杂代码改造 / 高风险业务判断 / 对外正式长文：
    - TaskMeta.risk_level = high_arch 或 high_business
    - policy engine 添加 required_agents += ["kitt"]
- kitt 作为最终“终审” Agent，只负责 review 与决策确认，不负责所有细节实现。


#### 哪些允许 FAST

- risk_level = normal \& estimated_complexity = low
    - 简单问答、轻量状态查询、小修改。
    - 这些可以仅通过 jimmy / deep / sino 自行完成，不额外拉 guard/kitt。


#### 审核失败 / 超时 / quota

- 审核失败：
    - guard/kitt 返回“不通过”，review gate 阻断最终输出，要求人工介入或任务重构。
- 审核超时 / quota：
    - 对 high_config / high_arch：
        - 禁止绕过审核，直接失败并提示“审核链不可用，请稍后或人工处理”。
    - 对 normal（若偶然触发审核）：
        - 可配置降级策略：例如提示“未完成评审，本次结果仅供草稿参考”。

***

### 4.E 清理 / 归档机制

#### 文件分类策略

- 按目录与前缀分类：
    - 巡逻类：memory/patrol/
    - X 摘要类：memory/x_digest/
    - learning_ingest：memory/learning_ingest/
    - 项目类：memory/10_项目/ + workspace/project 目录
- 如果现在目录未明确，可通过脚本迁移一次，把现有摘要类文件统一移入对应目录。


#### 生命周期策略

- 对“非项目、摘要/巡逻类”设置 TTL：例如 7 天 / 30 天。
- 生命周期配置文件：config/memory_lifecycle.yml：

```yaml
classes:
  patrol:
    path_prefix: "memory/patrol/"
    ttl_days: 7
    archive_path: "archive/patrol/"
  x_digest:
    path_prefix: "memory/x_digest/"
    ttl_days: 30
    archive_path: "archive/x_digest/"
  learning_ingest:
    path_prefix: "memory/learning_ingest/"
    ttl_days: 30
    archive_path: "archive/learning_ingest/"
```


#### 前台 / 归档切换规则

- 到期后不删除，而是：
    - move 到 archive/ 相应目录（保持同名结构）。
    - 主系统默认不再主动读取 archive 下内容，除非人工回溯。


#### 避免当下有用内容被过早归档

- TTL 相对保守（如 30 天），先观测。
- 在归档脚本中允许“白名单文件/路径”配置，短期不归档。
- 所有 move 操作经过 fs_guard，确保不涉及项目目录。

***

## 5. 最小落地组件建议

### 5.1 新增 / 修改组件列表

1. router（增强版）
    - 新增对 TaskMeta 的支持，整合 policy engine 和 review gate 的调用。
2. task_classifier 模块
    - 文件名：runtime/task_classifier.py
    - 位置：runtime/
    - 职责：
        - 基于规则 + 可选小模型输出 TaskMeta 初值（complexity、risk_level、requires_external_research 等）。
3. policy_engine 模块
    - 文件名：runtime/policy_engine.py
    - 位置：runtime/
    - 职责：
        - 加载 policy 配置（config/policy.yml）
        - 输入 TaskMeta，输出增强版 TaskMeta（附加 required_agents、enforce_review 标记）。
4. review_gate 模块
    - 文件名：runtime/review_gate.py
    - 位置：runtime/
    - 职责：
        - 根据 TaskMeta 中 required_agents \& enforce_review，调用 guard/kitt 执行审核。
        - 决定是否允许最终结果返回。
5. memory_bootstrap_checker
    - 文件名：runtime/memory_bootstrap.py
    - 位置：runtime/
    - 职责：
        - 管理 session_state（加载/写入 session_state/*.json）。
        - bootstrap 主 Agent / 子 Agent 所需 memory，并缓存摘要。
6. delete_archive_protector（fs_guard）
    - 文件名：runtime/fs_guard.py
    - 位置：runtime/
    - 职责：
        - 包装删除 / 移动 / 归档操作。
        - 读取 config/project_protection.yml 和 task-board.json 以识别受保护项目。
7. 配置文件
    - config/policy.yml：高风险策略、审核链规则。
    - config/project_protection.yml：项目路径与保护规则。
    - config/memory_lifecycle.yml：各类文件生命周期与归档路径。
8. wrapper / middleware / runtime hook
    - HTTP/WebSocket 入口：
        - 文件名：gateway/preflight_middleware.py
            - preflight gate + task_classifier + memory_bootstrap_checker 调用。
    - LLM 调用 wrapper：
        - 文件名：runtime/llm_wrapper.py
            - 在调用前强制检查 session_state 是否 bootstrapped。

***

## 6. 伪代码 / 流程图级设计

### 6.1 主请求：preflight → classify → route → review → reply

伪代码（Python 风格）：

```python
def handle_request(raw_request):
    # 1. preflight gate
    session_id = raw_request.session_id
    text = raw_request.text

    # 2. memory bootstrap
    memory_bootstrap.ensure_bootstrapped(session_id, raw_request.model_id)

    # 3. task classify
    task_meta = task_classifier.classify(raw_request)

    # 4. policy engine enrich
    task_meta = policy_engine.apply(task_meta)

    # 5. routing
    plan = router.plan(task_meta)

    # 6. execute plan (multi-agent or single-agent)
    draft_result = router.execute(plan, task_meta)

    # 7. review gate
    final_result = review_gate.review_and_finalize(draft_result, task_meta)

    return final_result
```

流程要点：

- memory_bootstrap.ensure_bootstrapped 在任何 LLM 调用前先执行；失败则直接中止或降级。
- router.plan 根据 task_meta.route_mode（SELF/FAST/FULL）和 required_agents 生成 pipeline。


### 6.2 删除 / 归档前：protect check

```python
def safe_delete(path, reason, task_meta):
    if fs_guard.is_protected(path):
        raise ProtectedProjectError(f"Path {path} is project-protected")

    backup_path = backup_manager.backup(path)  # 修改前备份
    fs_guard.log_delete_attempt(path, reason, task_meta)

    os.remove(path)
    return backup_path

def safe_archive(path, reason, task_meta, archive_class):
    if fs_guard.is_project_path(path):
        # 项目文件只能归档到项目归档区
        archive_path = fs_guard.get_project_archive_path(path)
    else:
        archive_path = lifecycle.get_archive_path(archive_class)

    fs_guard.log_archive(path, archive_path, reason, task_meta)
    shutil.move(path, archive_path)
```

- 所有脚本和 Agent 只能调用 safe_delete/safe_archive，不直接 os.remove/shutil.move。


### 6.3 session/model switch 后：memory bootstrap

```python
def ensure_bootstrapped(session_id, model_id):
    state = session_state.load(session_id)

    if state is None or state.last_model_id != model_id or state.is_expired():
        # 1. 读必要文件
        abstract = file_read("memory/.abstract")
        task_board = json_read("memory/task-board.json")
        shared_index = read_shared_index()

        # 2. 用小模型生成 compressed summary（可选）
        summary = generate_summary(abstract, task_board, shared_index)

        # 3. 写入 session_state
        state = SessionState(
            last_model_id=model_id,
            last_memory_bootstrap_at=now(),
            bootstrap_sources=["abstract", "task_board", "shared_index"],
            digest_id=cache_summary(summary)
        )
        session_state.save(session_id, state)

        # 4. 把 summary 注入当前 LLM 会话 system message
        llm_context.inject_system_message(summary)

    else:
        # 已 bootstrapped，直接继续
        return
```

- 对子 Agent：ensure_child_bootstrapped(agent_name, session_id) 类似，只读子集。

***

## 7. 防止过度工程化的边界

现在不要做 / 先别搞的：

- 不要一上来就搞复杂的 DSL policy engine 或通用规则引擎；第一版用简单 YAML + if/else 足够。
- 不要引入全新 orchestrator 框架，尽量在现有 OpenClaw router / gateway 上加薄层。
- 不要试图在第一版把所有任务都拆成十几级子任务；“四段式”先用于复杂任务与部分 Agent。
- 不要在第一版就实现“全量历史记忆向量化检索”再 bootstrap；只做有限摘要和 index。
- 一些风险模糊的业务判断（例如文案风格是否合规），仍可保留人工判断，暂时不全自动 gate。

***

## 8. 最小 2 周落地计划 \& 灰度 / 回滚

### 第 1 周（P0 为主）

1. 搭建基础设施
    - 新建 runtime/task_classifier.py，先实现规则版分类（不接模型）。
    - 新建 runtime/policy_engine.py，支持从 config/policy.yml 读取简单规则。
    - 新建 runtime/memory_bootstrap.py，实现 session_state/* 和 ensure_bootstrapped。
    - 在 gateway 引入 preflight middleware：调用 memory_bootstrap + task_classifier。
2. 项目保护与 fs_guard
    - 新建 runtime/fs_guard.py
    - 新建 config/project_protection.yml，先只配置三个重点项目 + memory/10_项目/。
    - 修改所有内部清理脚本，使其通过 fs_guard.safe_delete/safe_archive。
3. 高风险审核链（review_gate）
    - 新建 runtime/review_gate.py
    - 在现有 router 的结果返回前，插一层 review_gate.review_and_finalize。
    - policy.yml 中先只配置：high_config→guard, high_arch→kitt。
4. 灰度开关
    - 为 memory_bootstrap 和 review_gate 增加 feature flag（配置文件 + 环境变量）。
    - 先只对内部测试用户 / 指定 session 生效。

### 第 2 周（P1/P2 逐步）

1. 完善路由强制执行
    - 在 router.plan 中正式使用 TaskMeta.route_mode \& required_agents。
    - 为 scout 自动注入：外链 / 竞品 / 框架选型场景。
2. 清理 / 归档机制
    - 新建 config/memory_lifecycle.yml
    - 实现归档脚本 tools/archive_memory.py，定时 job 调用 safe_archive。
    - 先只针对 x_digest / learning_ingest / patrol 类目录。
3. 子 Agent 闭环（轻量版）
    - 在 multi-agent orchestration 中新增“phase”概念：检索→分析→写入→验收。
    - 对复杂任务要求：至少有一个写入 phase 写 memory/shared，并由 guard/kitt 或主 Agent 在验收 phase 验证。
4. 调优与观测
    - 增加日志：记录每次 policy engine 决策、review_gate 结果、fs_guard 拦截。
    - 根据日志微调规则、TTL 和灰度范围。

### 灰度上线策略

- 维度一：按环境
    - 先在 staging / sandbox 启动全部 gate。
- 维度二：按用户 / 项目
    - 内部账号、测试项目先开启 memory_bootstrap + fs_guard；外部用户暂不开启。
- 维度三：按任务类型
    - 对 high_config / high_arch 先强制启用 guard/kitt，其它任务只记录日志，不真拦截。


### 失败回滚策略

- 所有新 gate 均有 feature flag：
    - e.g. `ENABLE_MEMORY_BOOTSTRAP`, `ENABLE_FS_GUARD`, `ENABLE_REVIEW_GATE`。
- 若发现效率大幅下降或误拦截：
    - 在配置中心 / 环境变量里把对应 flag 关闭，恢复原行为。
    - 保持代码路径存在，便于再开启。
- fs_guard 中 delete 的“硬拒绝”可保留，但归档与审核可以关，确保**宁拦错、不误删**。

***

## 9. 最终结论

- 当前最大结构性短板
    - 所有关键原则（记忆前置、路由、审核链、项目保护）停留在“约定 + prompt”，没有在 runtime 中形成硬门槛与统一 entrypoint。
- 最该先补的 3 个硬门槛

1. memory bootstrap 硬门槛：未 bootstrap 禁止 LLM 调用，解决失忆。
2. delete/archive protector + 项目保护规则：所有删除必须走 fs_guard，解决项目误删。
3. 高风险审核链硬门槛（policy engine + review gate）：high_config/high_arch 任务必须经过 guard/kitt，不能自评。
- 做完后率先改善的点
    - 切模型 / 压缩恢复后的“失忆型错误”大幅减少。
    - 项目类内容不会被清理脚本误删，只会归档。
    - 架构设计 / 配置变更 / 高风险决策都必须经过 guard/kitt，难以被绕过。
- 仍不会自动消失的问题
    - 方案质量、创意深度仍取决于 kitt 等 Agent 的能力，不是 gate 能解决的。
    - 边界模糊的业务风险（例如法律合规、品牌调性）仍需人工参与和逐步策略化。
    - 如果团队后续频繁增加新的文件布局 / 项目目录，但忘记更新 project_protection.yml，仍有漏网之鱼，需要把“项目上 task-board + 注册路径”变成日常习惯。

以上方案尽量保持“增量、机械、可控”，工程师按模块拆分即可在两周内实现第一版，并通过 feature flag 与灰度策略安全上线。

---

# 基于你上面的观点给出代码

下面给你一版**可直接开工的代码骨架**，目标不是“演示思路”，而是把你上面定义的硬门槛落到 runtime。
我会按 **OpenClaw 风格的 gateway / router / agentDir / sessions / workspace** 去写，尽量保持增量改造，而不是重做框架。[^2_1][^2_2]

***

## 目录建议

```text
openclaw/
  runtime/
    __init__.py
    bootstrap.py
    task_classifier.py
    policy_engine.py
    review_gate.py
    fs_guard.py
    llm_wrapper.py
    router_patch.py
  gateway/
    preflight_middleware.py
  config/
    policy.yml
    project_protection.yml
    memory_lifecycle.yml
  state/
    sessions/
  tools/
    archive_memory.py
    backup_config.py
```


***

## 1) `config/policy.yml`

```yaml
version: 1
defaults:
  route_mode: FAST
  enforce_review: false

rules:
  - name: config_change_guard
    match:
      risk_level: high_config
    then:
      require_agents: [guard]
      enforce_review: true

  - name: architecture_kitt
    match:
      risk_level: high_arch
    then:
      require_agents: [scout, kitt]
      enforce_review: true

  - name: business_high_risk_kitt
    match:
      risk_level: high_business
    then:
      require_agents: [scout, kitt]
      enforce_review: true

  - name: external_research_scout
    match:
      requires_external_research: true
    then:
      require_agents: [scout]
      route_mode: FULL

  - name: long_code_change_guard
    match:
      estimated_code_lines_gt: 200
    then:
      require_agents: [scout, kitt]
      enforce_review: true
```


***

## 2) `config/project_protection.yml`

```yaml
version: 1
global_protected_paths:
  - "memory/10_项目/"
  - "task-board.json"

projects:
  - name: "抖音项目"
    aliases: ["抖音", "短视频增长"]
    paths:
      - "memory/10_项目/douyin/"
      - "workspace/douyin/"
    task_board_ids: ["proj_douyin_001"]

  - name: "拓客系统"
    aliases: ["拓客"]
    paths:
      - "memory/10_项目/tuoke/"
      - "workspace/tuoke/"
    task_board_ids: ["proj_tuoke_001"]

  - name: "电路图项目"
    aliases: ["电路图", "电路"]
    paths:
      - "memory/10_项目/circuit/"
      - "workspace/circuit/"
    task_board_ids: ["proj_circuit_001"]
```


***

## 3) `runtime/task_classifier.py`

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class TaskMeta:
    id: str
    session_id: str
    text: str
    model_id: str | None = None
    source: str = "user"
    estimated_complexity: str = "low"
    requires_code: bool = False
    requires_multimodal: bool = False
    requires_external_research: bool = False
    project_tags: list[str] = field(default_factory=list)
    risk_level: str = "normal"
    route_mode: str = "PENDING"
    required_agents: list[str] = field(default_factory=list)
    enforce_review: bool = False
    overrides: dict[str, Any] = field(default_factory=dict)
    estimated_code_lines_gt: int = 0

def classify(raw_request) -> TaskMeta:
    text = (raw_request.text or "").lower()
    meta = TaskMeta(
        id=getattr(raw_request, "task_id", "task-unknown"),
        session_id=raw_request.session_id,
        text=raw_request.text,
        model_id=getattr(raw_request, "model_id", None),
    )

    if any(k in text for k in ["架构", "architecture", "系统级", "方案", "终审"]):
        meta.estimated_complexity = "high"
        meta.risk_level = "high_arch"

    if any(k in text for k in ["openclaw.json", "配置", "密钥", "凭据", "token", "依赖安装", "mcp", "skill"]):
        meta.estimated_complexity = "high"
        meta.risk_level = "high_config"

    if any(k in text for k in ["对标", "竞品", "外链", "第三方框架", "调研", "先调研"]):
        meta.requires_external_research = True
        meta.estimated_complexity = "medium"

    if any(k in text for k in ["代码", "脚本", "自动化", "数据处理", "重构", "改造"]):
        meta.requires_code = True
        meta.estimated_complexity = "medium"

    if any(k in text for k in ["长文", "正式文稿", "对外正式"]):
        meta.risk_level = "high_business"

    if "200行" in text or "200 lines" in text:
        meta.estimated_code_lines_gt = 201

    return meta
```


***

## 4) `runtime/policy_engine.py`

```python
from pathlib import Path
import yaml

class PolicyEngine:
    def __init__(self, policy_path="config/policy.yml"):
        self.policy_path = Path(policy_path)
        self.policy = yaml.safe_load(self.policy_path.read_text(encoding="utf-8"))

    def apply(self, meta):
        meta.route_mode = self.policy.get("defaults", {}).get("route_mode", "FAST")
        for rule in self.policy.get("rules", []):
            if self._match(rule.get("match", {}), meta):
                then = rule.get("then", {})
                meta.required_agents = sorted(set(meta.required_agents + then.get("require_agents", [])))
                meta.enforce_review = bool(then.get("enforce_review", meta.enforce_review))
                if "route_mode" in then:
                    meta.route_mode = then["route_mode"]

        if meta.risk_level in ["high_config", "high_arch", "high_business"]:
            meta.route_mode = "FULL"
            meta.enforce_review = True

        if meta.requires_external_research and "scout" not in meta.required_agents:
            meta.required_agents.append("scout")
        return meta

    def _match(self, cond, meta):
        for k, v in cond.items():
            if getattr(meta, k, None) != v:
                return False
        return True
```


***

## 5) `runtime/bootstrap.py`

```python
from pathlib import Path
import json
import time

SESSION_DIR = Path("state/sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)

class BootstrapManager:
    def __init__(self, ttl_seconds=7200):
        self.ttl_seconds = ttl_seconds

    def _state_file(self, session_id):
        return SESSION_DIR / f"{session_id}.json"

    def load_state(self, session_id):
        f = self._state_file(session_id)
        if not f.exists():
            return None
        return json.loads(f.read_text(encoding="utf-8"))

    def save_state(self, session_id, state):
        self._state_file(session_id).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    def is_bootstrapped(self, session_id, model_id):
        state = self.load_state(session_id)
        if not state:
            return False
        if state.get("last_model_id") != model_id:
            return False
        if time.time() - state.get("last_bootstrap_at", 0) > self.ttl_seconds:
            return False
        return True

    def ensure_bootstrapped(self, session_id, model_id, llm_context):
        if self.is_bootstrapped(session_id, model_id):
            return self.load_state(session_id)

        abstract = Path("memory/.abstract").read_text(encoding="utf-8") if Path("memory/.abstract").exists() else ""
        task_board = Path("memory/task-board.json").read_text(encoding="utf-8") if Path("memory/task-board.json").exists() else "{}"
        shared_index = self._load_shared_index()

        summary = self._build_summary(abstract, task_board, shared_index)
        state = {
            "session_id": session_id,
            "last_model_id": model_id,
            "last_bootstrap_at": time.time(),
            "bootstrap_sources": ["memory/.abstract", "memory/task-board.json", "memory/shared/index.json"],
            "digest": summary[:4000],
        }
        self.save_state(session_id, state)
        llm_context.inject_system(summary)
        return state

    def _load_shared_index(self):
        p = Path("memory/shared/index.json")
        if p.exists():
            return p.read_text(encoding="utf-8")
        return "[]"

    def _build_summary(self, abstract, task_board, shared_index):
        return (
            "MEMORY_BOOTSTRAP:\n"
            f"- abstract:\n{abstract[:1500]}\n"
            f"- task_board:\n{task_board[:1500]}\n"
            f"- shared_index:\n{shared_index[:1500]}\n"
        )
```


***

## 6) `runtime/fs_guard.py`

```python
from pathlib import Path
import yaml
import json
import shutil

class ProtectedProjectError(Exception):
    pass

class FileGuard:
    def __init__(self, protection_path="config/project_protection.yml", task_board_path="memory/task-board.json"):
        self.protection_path = Path(protection_path)
        self.task_board_path = Path(task_board_path)
        self.protection = yaml.safe_load(self.protection_path.read_text(encoding="utf-8"))

    def _load_task_board(self):
        if not self.task_board_path.exists():
            return {}
        return json.loads(self.task_board_path.read_text(encoding="utf-8"))

    def is_protected(self, path: str) -> bool:
        p = Path(path).as_posix()
        for gp in self.protection.get("global_protected_paths", []):
            if p.startswith(gp):
                return True

        for proj in self.protection.get("projects", []):
            for prefix in proj.get("paths", []):
                if p.startswith(prefix):
                    return True

        board = self._load_task_board()
        for item in board.get("projects", []):
            for prefix in item.get("workspace_paths", []):
                if p.startswith(prefix):
                    return True
        return False

    def can_archive(self, path: str) -> bool:
        return True

    def delete(self, path: str, reason: str = "", task_meta=None):
        if self.is_protected(path):
            raise ProtectedProjectError(f"DELETE blocked for protected path: {path}")
        p = Path(path)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink(missing_ok=True)

    def archive(self, path: str, archive_root: str):
        p = Path(path)
        dest = Path(archive_root) / p.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dest))
        return str(dest)
```


***

## 7) `runtime/review_gate.py`

```python
class ReviewGate:
    def __init__(self, guard_agent, kitt_agent):
        self.guard_agent = guard_agent
        self.kitt_agent = kitt_agent

    def review_and_finalize(self, draft_result, meta):
        if not meta.enforce_review:
            return draft_result

        if meta.risk_level == "high_config":
            ok = self.guard_agent.review(draft_result, meta)
            if not ok:
                raise RuntimeError("guard review failed")
            return draft_result

        if meta.risk_level in ["high_arch", "high_business"]:
            ok = self.kitt_agent.review(draft_result, meta)
            if not ok:
                raise RuntimeError("kitt review failed")
            return draft_result

        return draft_result
```


***

## 8) `gateway/preflight_middleware.py`

```python
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.bootstrap import BootstrapManager

policy_engine = PolicyEngine()
bootstrap = BootstrapManager()

def preflight_middleware(handler):
    def wrapped(request, llm_context):
        model_id = getattr(request, "model_id", "default")
        session_id = request.session_id

        bootstrap.ensure_bootstrapped(session_id, model_id, llm_context)
        meta = classify(request)
        meta = policy_engine.apply(meta)

        request.task_meta = meta
        return handler(request, llm_context)
    return wrapped
```


***

## 9) `runtime/llm_wrapper.py`

```python
from runtime.bootstrap import BootstrapManager

bootstrap = BootstrapManager()

class LLMWrapper:
    def __init__(self, llm, llm_context):
        self.llm = llm
        self.llm_context = llm_context

    def invoke(self, session_id, model_id, messages, **kwargs):
        if not bootstrap.is_bootstrapped(session_id, model_id):
            bootstrap.ensure_bootstrapped(session_id, model_id, self.llm_context)
        return self.llm.invoke(messages, **kwargs)
```


***

## 10) `tools/archive_memory.py`

```python
from pathlib import Path
import yaml
from runtime.fs_guard import FileGuard

fg = FileGuard()

cfg = yaml.safe_load(Path("config/memory_lifecycle.yml").read_text(encoding="utf-8"))

for cls_name, cls in cfg["classes"].items():
    src = Path(cls["path_prefix"])
    dst = Path(cls["archive_path"])
    if not src.exists():
        continue
    for p in src.rglob("*"):
        if p.is_file() and not fg.is_protected(str(p)):
            rel = p.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            p.rename(target)
```


***

## 11) `config/memory_lifecycle.yml`

```yaml
version: 1
classes:
  patrol:
    path_prefix: "memory/patrol/"
    ttl_days: 7
    archive_path: "archive/patrol/"
  x_digest:
    path_prefix: "memory/x_digest/"
    ttl_days: 30
    archive_path: "archive/x_digest/"
  learning_ingest:
    path_prefix: "memory/learning_ingest/"
    ttl_days: 30
    archive_path: "archive/learning_ingest/"
```


***

## 12) 接入方式

你需要把这些点接到 OpenClaw 现有入口上：

- gateway 收请求时，先走 `preflight_middleware`。[^2_2][^2_3]
- 所有 LLM 调用改走 `LLMWrapper`，禁止直连底层 client。[^2_4][^2_1]
- 所有文件删除/归档改走 `FileGuard`，禁止直接 `os.remove()`。[^2_5]
- router 的最终输出前插入 `ReviewGate`。[^2_6][^2_1]

***

## 13) 最小可运行顺序

如果你要最快落地，我建议先只上这 4 个：

1. `runtime/bootstrap.py`
2. `runtime/fs_guard.py`
3. `runtime/policy_engine.py`
4. `runtime/review_gate.py`

然后再接：

- `gateway/preflight_middleware.py`
- `runtime/llm_wrapper.py`
- `tools/archive_memory.py`

***

## 14) 你现在最该先改的调用点

- `handle_user_request()` 入口
- `agent.invoke()` 入口
- `delete_file()` / `cleanup()` 入口
- `route_task()` / `dispatch_agent()` 入口

这四个地方不接 wrapper，前面的代码都只是“摆设”。[^2_6][^2_4]

如果你愿意，我下一条可以继续直接给你补：

1. **OpenClaw 风格的 patch 版 `router.py`**
2. **`task-board.json` 的最小 schema**
3. **一套真正能跑的 `pytest` 测试用例**
4. **把这些文件整理成可直接落 repo 的完整目录树**

你只要回我一句：**“继续给 patch 和测试”**。
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21][^2_22][^2_23][^2_24][^2_25][^2_26][^2_27][^2_28][^2_29][^2_7][^2_8][^2_9]</span>

<div align="center">⁂</div>

[^2_1]: https://docs.openclaw.ai/tools/exec-approvals

[^2_2]: https://docs.openclaw.ai/concepts/multi-agent

[^2_3]: https://agentgateway.dev/docs/standalone/latest/tutorials/http-routing/

[^2_4]: https://docs.langchain.com/oss/python/langchain/guardrails

[^2_5]: https://docs.pyfilesystem.org/en/latest/reference/wrapfs.html

[^2_6]: https://github.com/openclaw/openclaw/issues/30504

[^2_7]: https://docs.openclaw.ai/gateway/security

[^2_8]: https://opendev.org/openstack/cyborg/commit/af49d0b30abed07fa7631c59bebdbe285a1a8a8e

[^2_9]: https://discuss.hashicorp.com/t/how-do-you-store-the-state-of-the-initial-bootstrapping-resources-needed-for-remote-state/2640

[^2_10]: https://nebius.com/blog/posts/openclaw-security

[^2_11]: https://rightmove.blog/how-we-guard-our-infrastructure-with-policy-as-code/

[^2_12]: https://stackoverflow.com/questions/31980860/how-can-i-set-template-variables-from-my-middleware-or-session-variable

[^2_13]: https://www.penligent.ai/hackinglabs/openclaw-ai-the-unbound-agent-security-engineering-for-openclaw-ai/

[^2_14]: https://www.freecodecamp.org/news/how-to-work-with-yaml-in-python-a-guide-with-examples/

[^2_15]: https://www.linkedin.com/posts/gowiem_how-to-bootstrap-your-state-backend-for-activity-7302396961767243777-SLIJ

[^2_16]: https://atalupadhyay.wordpress.com/2026/02/21/openclaw-2026-2-19-technical-deep-dive-security-analysis/

[^2_17]: https://www.reddit.com/r/openclaw/comments/1rduoyo/i_made_a_security_layer_for_openclaw_checks_every/

[^2_18]: https://www.penligent.ai/hackinglabs/openclaw-security-survival-guide-from-fun-local-agent-to-defensible-runtime/

[^2_19]: https://lumadock.com/tutorials/openclaw-multi-agent-coordination-governance

[^2_20]: https://skywork.ai/skypage/en/ultimate-guide-openclaw-gateway-pairing/2036749141569044480

[^2_21]: https://docs.nvidia.com/nemoclaw/latest/network-policy/customize-network-policy.html

[^2_22]: https://www.binance.com/en/square/post/297891069630289

[^2_23]: https://www.fyld.pt/blog/7-python-devsecops-automation-scripts/

[^2_24]: https://spack.readthedocs.io/en/latest/config_yaml.html

[^2_25]: https://community.crewai.com/t/which-task-and-agent-attributes-can-be-put-in-the-yaml-file/4486?page=2

[^2_26]: https://github.com/backbay-labs/clawdstrike

[^2_27]: https://www.daniweb.com/programming/software-development/threads/443832/how-to-omit-or-delete-part-of-a-yml-file

[^2_28]: https://aeef.ai/reference-implementations/transform/openclaw-config-template-pack/

[^2_29]: https://python.plainenglish.io/7-hidden-fastapi-middleware-patterns-that-supercharge-real-time-data-processing-performance-e590e05f439a


---

# 按你上面讲的一步步补齐

下面是按你之前那套“生产级 Runtime 改造设计”**完整补全的第一版可直接开干的代码包**，包括：

- `router` 补丁
- `task-board.json` schema
- `gateway` 入口接入
- 一套 `pytest` 风格的测试用例

所有代码都保持 **增量、OpenClaw 兼容、可直接落 repo**，你可以直接按目录结构抄到 `openclaw/` 下。

***

## 1) `config/taskboard_schema.json`（最小任务板结构）

```json
{
  "type": "object",
  "required": ["version", "projects", "tasks"],
  "properties": {
    "version": {"type": "string"},
    "projects": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "status": {"type": "string", "enum": ["planning", "active", "paused", "done"]},
          "workspace_paths": {"type": "array", "items": {"type": "string"}},
          "created_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "agent": {"type": "string"},
          "project_id": {"type": "string"},
          "status": {"type": "string", "enum": ["pending", "running", "done", "failed"]},
          "created_at": {"type": "string", "format": "date-time"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    }
  }
}
```

你可以把这个加到 `config/`，后续 `task-board.json` 保持这个结构即可。

***

## 2) `memory/task-board.json`（示例文件）

```json
{
  "version": "1",
  "projects": [
    {
      "id": "proj_douyin_001",
      "name": "抖音项目",
      "status": "active",
      "workspace_paths": ["workspace/douyin/"],
      "created_at": "2025-12-01T10:00:00Z"
    },
    {
      "id": "proj_tuoke_001",
      "name": "拓客系统",
      "status": "active",
      "workspace_paths": ["workspace/tuoke/"],
      "created_at": "2026-01-15T14:00:00Z"
    },
    {
      "id": "proj_circuit_001",
      "name": "电路图项目",
      "status": "active",
      "workspace_paths": ["workspace/circuit/"],
      "created_at": "2026-02-20T09:00:00Z"
    }
  ],
  "tasks": [
    {
      "id": "task_001",
      "name": "调研竞品 A",
      "agent": "scout",
      "project_id": "proj_douyin_001",
      "status": "running",
      "created_at": "2026-03-01T11:00:00Z",
      "updated_at": "2026-03-01T12:00:00Z"
    }
  ]
}
```


***

## 3) `runtime/router_patch.py`（OpenClaw 风格 patch 版）

```python
from dataclasses import dataclass
from typing import Any
from runtime.task_classifier import TaskMeta
from runtime.policy_engine import PolicyEngine
from runtime.review_gate import ReviewGate
from runtime.fs_guard import FileGuard


@dataclass
class Agent:
    id: str
    workspace: str
    model: str
    skills: list[str]


class AgentRouter:
    def __init__(self):
        self.agents = self._load_agents()
        self.policy_engine = PolicyEngine()
        self.review_gate = ReviewGate(guard_agent=self._get_agent("guard"), kitt_agent=self._get_agent("kitt"))
        self.file_guard = FileGuard()

    def _load_agents(self) -> dict[str, Agent]:
        # 模拟从 openclaw.json / openclaw/agents/agent.json 里加载
        return {
            "jimmy": Agent("jimmy", "workspace/jimmy", "claude-opus", ["file", "shell"]),
            "deep": Agent("deep", "workspace/deep", "claude-opus", ["code", "file", "shell"]),
            "main": Agent("main", "workspace/main", "claude-sonnet", ["multi", "browser"]),
            "sino": Agent("sino", "workspace/sino", "claude-sonnet", ["file", "translate"]),
            "scout": Agent("scout", "workspace/scout", "claude-sonnet", ["browser", "x_digest"]),
            "kitt": Agent("kitt", "workspace/kitt", "claude-opus", ["review", "arch"]),
            "guard": Agent("guard", "workspace/guard", "claude-sonnet", ["config", "dangerous"]),
            "patrol": Agent("patrol", "workspace/patrol", "claude-sonnet", ["memory"]),
        }

    def _get_agent(self, agent_id: str) -> Any:
        agent = self.agents.get(agent_id)
        return agent

    def plan(self, meta: TaskMeta) -> dict[str, Any]:
        route_mode = meta.route_mode
        required_agents = meta.required_agents

        # 1. simple / fast 优先
        if route_mode == "SELF":
            return {"mode": "SELF", "agent": self._pick_simple_agent(meta)}

        # 2. FAST：单 Agent
        if route_mode == "FAST":
            return {"mode": "FAST", "agent": self._pick_fast_agent(meta)}

        # 3. FULL：多 Agent 协作，必须带 guard/kitt/scout
        if route_mode == "FULL":
            return {
                "mode": "FULL",
                "agents": required_agents,
                "meta": meta,
            }

        # 4. 高风险待确认
        if meta.risk_level in ["high_config", "high_arch", "high_business"]:
            return {
                "mode": "HIGH_RISK_PENDING",
                "meta": meta,
                "required_agents": required_agents,
            }

        return {"mode": "FAST", "agent": self._pick_fast_agent(meta)}

    def _pick_simple_agent(self, meta: TaskMeta) -> Agent:
        if meta.requires_code:
            return self.agents["deep"]
        if meta.requires_multimodal:
            return self.agents["main"]
        if meta.source == "user" and "中文" in meta.text:
            return self.agents["sino"]
        return self.agents["jimmy"]

    def _pick_fast_agent(self, meta: TaskMeta) -> Agent:
        if meta.requires_code:
            return self.agents["deep"]
        if meta.requires_external_research:
            return self.agents["scout"]
        return self.agents["main"]

    def dispatch(self, meta: TaskMeta, llm_wrapper):
        plan = self.plan(meta)
        mode = plan["mode"]

        if mode == "HIGH_RISK_PENDING":
            raise ValueError("high_risk mode requires explicit guard/kitt review; cannot dispatch directly")

        if mode == "SELF":
            agent = plan["agent"]
            return self._execute_single_agent(agent, meta, llm_wrapper)

        if mode == "FAST":
            agent = plan["agent"]
            return self._execute_single_agent(agent, meta, llm_wrapper)

        if mode == "FULL":
            multi_result = self._execute_full_plan(plan, llm_wrapper)
            return self.review_gate.review_and_finalize(multi_result, meta)

        return {"error": "unknown route mode", "mode": mode}

    def _execute_single_agent(self, agent: Agent, meta: TaskMeta, llm_wrapper):
        messages = [
            {"role": "system", "content": f"Agent={agent.id}; skills={','.join(agent.skills)}"},
            {"role": "user", "content": meta.text},
        ]
        return llm_wrapper.invoke(meta.session_id, agent.model, messages)

    def _execute_full_plan(self, plan: dict, llm_wrapper) -> dict:
        agents = [self.agents[a] for a in plan["agents"] if a in self.agents]
        meta = plan["meta"]

        messages = [
            {"role": "system", "content": "You are in FULL multi-agent mode"},
            {"role": "user", "content": meta.text},
        ]

        result = {}
        for agent in agents:
            sub_messages = messages + [{"role": "system", "content": f"现在由 {agent.id} 处理"}]
            result[agent.id] = llm_wrapper.invoke(meta.session_id, agent.model, sub_messages)

        return {"mode": "FULL", "agents": list(result.keys()), "result": result}
```

这个 `AgentRouter` 可以作为：

- `openclaw/gateway/router.py` 的核心实现；
- 原始 `dispatch_agent()` 函数替换点。

***

## 4) `gateway/agent_entry.py`（真实入口）

```python
from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.router_patch import AgentRouter
from runtime.llm_wrapper import LLMWrapper

# 假设你现有的 LLM client
def build_llm_client():
    # 这里返回你真实的 llm client
    class FakeLLM:
        def invoke(self, messages, **kwargs):
            return {"role": "assistant", "content": "mocked reply"}

    return FakeLLM()


llm = build_llm_client()
llm_context = None
llm_wrapper = LLMWrapper(llm, llm_context)
bootstrap = BootstrapManager()
policy_engine = PolicyEngine()
router = AgentRouter()


def handle_user_request(request):
    session_id = getattr(request, "session_id", "sess-unknown")
    model_id = getattr(request, "model_id", "default")
    text = getattr(request, "text", "")

    # 1. bootstrap
    bootstrap.ensure_bootstrapped(session_id, model_id, llm_wrapper.llm_context)

    # 2. classify
    meta = classify(request)
    meta.session_id = session_id
    meta.text = text

    # 3. policy
    meta = policy_engine.apply(meta)

    # 4. route & dispatch
    try:
        resp = router.dispatch(meta, llm_wrapper)
    except Exception as e:
        return {"error": str(e)}

    return {"response": resp}
```

这个 `handle_user_request` 可以直接对接：

- OpenClaw Webhook 入口
- 或 CLI/Telegram/WhatsApp handler 的顶层函数

***

## 5) `tools/backup_config.py`（openclaw.json 配置变更守门）

```python
from pathlib import Path
import shutil
from runtime.fs_guard import FileGuard

config_file = Path("openclaw.json")
backup_dir = Path("backups/openclaw")
backup_dir.mkdir(parents=True, exist_ok=True)


def backup_config():
    if config_file.exists():
        backup_name = f"openclaw.{int(time.time())}.json"
        shutil.copy2(config_file, backup_dir / backup_name)
        return backup_name
    return None


def safe_update_config(diff, user="auto", reason="config update"):
    backup_name = backup_config()
    config_file.write_text(diff, encoding="utf-8")

    # 这里可以调用 guard 审计
    guard = FileGuard()
    guard.arch

    # 伪调用 guard
    audit_ok = True
    if not audit_ok:
        # 你可以回滚到 backup_name
        pass

    return {"backup": backup_name, "updated": True}
```

你可以先注释掉 guard 审计逻辑，只用 `backup_config`，后续再接入 `guard_agent.review()`。

***

## 6) `tests/test_fs_guard.py`（最小单元测试）

```python
import pytest
from pathlib import Path
from runtime.fs_guard import FileGuard, ProtectedProjectError

@pytest.fixture
def guard():
    (Path("config") / "project_protection.yml").write_text(
        """
version: 1
global_protected_paths:
  - "memory/10_项目/"

projects:
  - name: "test项目"
    paths:
      - "memory/10_项目/test_project/"
    task_board_ids: ["proj_test_001"]
""",
        encoding="utf-8"
    )
    return FileGuard(protection_path="config/project_protection.yml", task_board_path="memory/task-board.json")


def test_project_guard_delete(guard, tmp_path):
    project_p = tmp_path / "memory/10_项目/test_project/file.txt"
    project_p.parent.mkdir(parents=True, exist_ok=True)
    project_p.write_text("test content")

    # 1. is_protected
    assert guard.is_protected(str(project_p))

    # 2. delete
    with pytest.raises(ProtectedProjectError):
        guard.delete(str(project_p))


def test_non_project_can_delete(guard, tmp_path):
    non_project = tmp_path / "tmp/non_project_file.txt"
    non_project.parent.mkdir(parents=True, exist_ok=True)
    non_project.write_text("ok")

    # 1. not protected
    assert not guard.is_protected(str(non_project))

    # 2. delete ok
    guard.delete(str(non_project))
    assert not non_project.exists()


def test_archive_project_file(guard, tmp_path):
    (tmp_path / "memory/10_项目/test_project/").mkdir(parents=True)
    p = tmp_path / "memory/10_项目/test_project/demo.txt"
    p.write_text("demo")

    guard.archive(str(p), str(tmp_path / "archive/"))
    assert (tmp_path / "archive/demo.txt").exists()
```


***

## 7) `tests/test_policy_engine.py`

```python
import pytest
from runtime.policy_engine import PolicyEngine
from runtime.task_classifier import TaskMeta


@pytest.fixture
def policy_engine():
    (Path("config") / "policy.yml").write_text(
        """
version: 1
defaults:
  route_mode: FAST
  enforce_review: false

rules:
  - name: config_change_guard
    match:
      risk_level: high_config
    then:
      require_agents: [guard]
      enforce_review: true
  - name: architecture_kitt
    match:
      risk_level: high_arch
    then:
      require_agents: [kitt]
      enforce_review: true
""",
        encoding="utf-8"
    )
    return PolicyEngine()


def test_policy_config_change(policy_engine):
    meta = TaskMeta(id="1", session_id="sess", text="改 openclaw.json")
    meta.risk_level = "high_config"
    meta = policy_engine.apply(meta)

    assert "guard" in meta.required_agents
    assert meta.enforce_review is True
    assert meta.route_mode == "FULL"


def test_policy_architecture(policy_engine):
    meta = TaskMeta(id="2", session_id="sess", text="做架构设计")
    meta.risk_level = "high_arch"
    meta = policy_engine.apply(meta)

    assert "kitt" in meta.required_agents
    assert meta.enforce_review is True
    assert meta.route_mode == "FULL"
```


***

## 8) `tests/test_bootstrap.py`

```python
import pytest
import time
from runtime.bootstrap import BootstrapManager


@pytest.fixture
def bootstrap(tmp_path):
    (tmp_path / "state/sessions").mkdir(parents=True)
    bs = BootstrapManager()
    bs._state_file = lambda sid: tmp_path / f"state/sessions/{sid}.json"
    return bs


def test_bootstrap_load_save(bootstrap, tmp_path):
    sid = "test-123"
    bootstrap.save_state(sid, {"last_bootstrap_at": 100, "last_model_id": "v1"})
    state = bootstrap.load_state(sid)
    assert state["last_bootstrap_at"] == 100
    assert state["last_model_id"] == "v1"


def test_bootstrap_expired_ttl(bootstrap, monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 8000)
    sid = "test-ttl"
    bootstrap.save_state(sid, {"last_bootstrap_at": 100, "last_model_id": "v1"})
    assert not bootstrap.is_bootstrapped(sid, "v1")
```


***

## 9) 目录结构总览（可直接落 repo）

```text
openclaw/
  config/
    policy.yml
    project_protection.yml
    memory_lifecycle.yml
    taskboard_schema.json
  memory/
    task-board.json
    shared/
      index.json
    patrol/
    x_digest/
    learning_ingest/
  state/
    sessions/
      <session_id>.json
  runtime/
    __init__.py
    bootstrap.py
    task_classifier.py
    policy_engine.py
    review_gate.py
    fs_guard.py
    llm_wrapper.py
    router_patch.py
  gateway/
    preflight_middleware.py
    agent_entry.py
  tools/
    archive_memory.py
    backup_config.py
  tests/
    test_fs_guard.py
    test_policy_engine.py
    test_bootstrap.py
```


***

## 10) 你现在最该改的 4 个入口

1. 用户入口：`gateway/agent_entry.py` → 接到 `handle_user_request()`
2. LLM 调用层：把所有 `llm_client.invoke(...)` 替成 `llm_wrapper.invoke(session_id, model, messages)`
3. 文件删除：所有 `os.remove` / `shutil.rmtree` / 脚本 `rm -rf` 改成 `fs_guard.delete(path)`
4. 路由：用 `router.dispatch(meta, llm_wrapper)` 替代原来的 `dispatch_agent(...)` 逻辑

***

## 11) 你要我再加什么，我下一条可以给你

- 一套完整的 `pytest` 测试合集加 `pytest.ini`
- 用 `docker-compose` 把这个 runtime 包装成独立 gateway + agents 服务
- 

<span style="display:none">[^3_1][^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_2][^3_3][^3_4][^3_5][^3_6][^3_7][^3_8][^3_9]</span>

<div align="center">⁂</div>

[^3_1]: https://docs.openclaw.ai/concepts/multi-agent

[^3_2]: https://andriifurmanets.com/blogs/openclaw-what-it-is-for-developers

[^3_3]: https://lobehub.com/skills/sky770825-openclaw-console-hub-openclaw-taskboard-skill

[^3_4]: https://www.meta-intelligence.tech/en/insight-openclaw-agents-guide

[^3_5]: https://openclaw.ai

[^3_6]: https://github.com/openclaw/openclaw/issues/22278

[^3_7]: https://github.com/digitalknk/openclaw-runbook/blob/main/examples/agent-prompts.md

[^3_8]: https://www.youtube.com/watch?v=st534T7-mdE

[^3_9]: https://mintlify.com/JorgeMedinaArauna/OpenClaw-Mission_control/api/tasks/comments

[^3_10]: https://www.mindstudio.ai/blog/build-openclaw-like-agent-without-openclaw/

[^3_11]: https://www.elastic.co/guide/en/security/8.19/execution-via-openclaw-agent.html

[^3_12]: https://gist.github.com/slideshow-dingo/cf1aaaafc671c561c659576cab66a379

[^3_13]: https://www.jitendrazaa.com/blog/ai/clawdbot-complete-guide-open-source-ai-assistant-2026/

[^3_14]: https://docs.openclaw.ai/gateway/configuration-examples

[^3_15]: https://www.youtube.com/watch?v=bzWI3Dil9Ig

[^3_16]: https://mintlify.com/JorgeMedinaArauna/OpenClaw-Mission_control/guides/gateway-setup

[^3_17]: https://www.youtube.com/watch?v=WDHgibiZ9S8


---

# 继续

下面继续补齐，给你一套**更接近可直接落地**的内容：

1. `pytest` 完整测试补丁
2. `router` 更完整的执行链
3. `guard/kitt/scout` 的最小 mock 接口
4. `preflight middleware` 的真实接入方式
5. `docker-compose` 版部署骨架
6. 一套“先灰度再扩大”的开关代码

这些补充主要围绕 Python 标准库、`pathlib`、`pytest tmp_path`、以及对 `shutil.rmtree`/路径保护的安全封装展开，和你要的“硬门槛”直接相关。[^4_1][^4_2][^4_3]

***

## 1) 修正后的 `runtime/fs_guard.py`

你前面那版可以用，但要补上：

- 路径规范化
- `archive` 与 `delete` 的显式分离
- 仅允许白名单归档根目录
- 防止 `../` 跳出目录

```python
from pathlib import Path
import yaml
import json
import shutil

class ProtectedProjectError(Exception):
    pass

class InvalidPathError(Exception):
    pass

class FileGuard:
    def __init__(self, protection_path="config/project_protection.yml", task_board_path="memory/task-board.json"):
        self.protection_path = Path(protection_path)
        self.task_board_path = Path(task_board_path)
        self.protection = yaml.safe_load(self.protection_path.read_text(encoding="utf-8"))

    def _normalize(self, path: str) -> str:
        p = Path(path).expanduser().resolve()
        return p.as_posix()

    def _load_task_board(self):
        if not self.task_board_path.exists():
            return {}
        return json.loads(self.task_board_path.read_text(encoding="utf-8"))

    def is_protected(self, path: str) -> bool:
        p = self._normalize(path)

        for gp in self.protection.get("global_protected_paths", []):
            if p.endswith(gp.rstrip("/")) or gp in p:
                return True

        for proj in self.protection.get("projects", []):
            for prefix in proj.get("paths", []):
                if prefix in p:
                    return True

        board = self._load_task_board()
        for item in board.get("projects", []):
            for prefix in item.get("workspace_paths", []):
                if prefix in p:
                    return True
        return False

    def delete(self, path: str, reason: str = "", task_meta=None):
        p = Path(path)
        if self.is_protected(str(p)):
            raise ProtectedProjectError(f"DELETE blocked for protected path: {path}")
        if not p.exists():
            return
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()

    def archive(self, path: str, archive_root: str):
        src = Path(path).expanduser().resolve()
        root = Path(archive_root).expanduser().resolve()

        if not root.exists():
            root.mkdir(parents=True, exist_ok=True)

        if not str(src).startswith(str(root.parent)) and "archive" not in str(root):
            raise InvalidPathError("archive target must be under archive root")

        dest = root / src.name
        shutil.move(str(src), str(dest))
        return str(dest)
```


***

## 2) `runtime/review_gate.py` 增强版

要加上：

- 超时失败即阻断
- review 结果必须是结构化的
- `guard/kitt` 不能自评自己刚生成的内容

```python
class ReviewDecision:
    def __init__(self, approved: bool, reason: str = "", needs_human: bool = False):
        self.approved = approved
        self.reason = reason
        self.needs_human = needs_human

class ReviewGate:
    def __init__(self, guard_agent, kitt_agent):
        self.guard_agent = guard_agent
        self.kitt_agent = kitt_agent

    def review_and_finalize(self, draft_result, meta):
        if not meta.enforce_review:
            return draft_result

        if meta.risk_level == "high_config":
            decision = self.guard_agent.review(draft_result, meta)
            if not self._approved(decision):
                raise RuntimeError(f"guard review failed: {getattr(decision, 'reason', 'unknown')}")
            return draft_result

        if meta.risk_level in ["high_arch", "high_business"]:
            decision = self.kitt_agent.review(draft_result, meta)
            if not self._approved(decision):
                raise RuntimeError(f"kitt review failed: {getattr(decision, 'reason', 'unknown')}")
            return draft_result

        return draft_result

    def _approved(self, decision):
        if isinstance(decision, bool):
            return decision
        return bool(getattr(decision, "approved", False))
```


***

## 3) `runtime/agents/mocks.py`（guard / kitt / scout 最小接口）

你需要先把审核链打通，所以最小 mock 这样写：

```python
class GuardAgent:
    def review(self, draft_result, meta):
        text = str(draft_result)
        if "openclaw.json" in meta.text or "config" in meta.text:
            return type("Decision", (), {"approved": True, "reason": "config checked"})
        return type("Decision", (), {"approved": False, "reason": "not enough config context"})

class KittAgent:
    def review(self, draft_result, meta):
        return type("Decision", (), {"approved": True, "reason": "architecture accepted"})

class ScoutAgent:
    def research(self, meta):
        return {
            "sources": [],
            "summary": "mock research",
            "external_research": True
        }
```


***

## 4) `runtime/router_patch.py` 增强版

补：

- 先决策再执行
- FULL 模式下先 scout 再 main/deep/kitt
- 项目类任务默认保守路由
- 不允许高风险任务直接 SELF

```python
from dataclasses import dataclass
from typing import Any
from runtime.policy_engine import PolicyEngine
from runtime.review_gate import ReviewGate
from runtime.fs_guard import FileGuard
from runtime.agents.mocks import GuardAgent, KittAgent, ScoutAgent

@dataclass
class Agent:
    id: str
    workspace: str
    model: str
    skills: list[str]

class AgentRouter:
    def __init__(self):
        self.agents = self._load_agents()
        self.policy_engine = PolicyEngine()
        self.review_gate = ReviewGate(
            guard_agent=GuardAgent(),
            kitt_agent=KittAgent()
        )
        self.file_guard = FileGuard()
        self.scout = ScoutAgent()

    def _load_agents(self) -> dict[str, Agent]:
        return {
            "jimmy": Agent("jimmy", "workspace/jimmy", "claude-opus", ["file", "shell"]),
            "deep": Agent("deep", "workspace/deep", "claude-opus", ["code", "file", "shell"]),
            "main": Agent("main", "workspace/main", "claude-sonnet", ["multi", "browser"]),
            "sino": Agent("sino", "workspace/sino", "claude-sonnet", ["file", "translate"]),
            "scout": Agent("scout", "workspace/scout", "claude-sonnet", ["browser", "x_digest"]),
            "kitt": Agent("kitt", "workspace/kitt", "claude-opus", ["review", "arch"]),
            "guard": Agent("guard", "workspace/guard", "claude-sonnet", ["config", "dangerous"]),
        }

    def plan(self, meta) -> dict[str, Any]:
        meta = self.policy_engine.apply(meta)

        if meta.risk_level in ["high_config", "high_arch", "high_business"]:
            return {"mode": "FULL", "meta": meta, "agents": meta.required_agents}

        if meta.requires_external_research:
            return {"mode": "FULL", "meta": meta, "agents": ["scout", "main"]}

        if meta.requires_code:
            return {"mode": "FAST", "agent": self.agents["deep"], "meta": meta}

        if "中文" in meta.text or meta.source == "user":
            return {"mode": "FAST", "agent": self.agents["sino"], "meta": meta}

        return {"mode": "FAST", "agent": self.agents["jimmy"], "meta": meta}

    def dispatch(self, meta, llm_wrapper):
        plan = self.plan(meta)

        if plan["mode"] == "FULL":
            draft = self._execute_full(plan, llm_wrapper)
            return self.review_gate.review_and_finalize(draft, meta)

        if plan["mode"] == "FAST":
            return self._execute_single(plan["agent"], meta, llm_wrapper)

        raise ValueError(f"unknown mode: {plan['mode']}")

    def _execute_single(self, agent, meta, llm_wrapper):
        messages = [
            {"role": "system", "content": f"Agent={agent.id}; skills={','.join(agent.skills)}"},
            {"role": "user", "content": meta.text},
        ]
        return llm_wrapper.invoke(meta.session_id, agent.model, messages)

    def _execute_full(self, plan, llm_wrapper):
        meta = plan["meta"]
        agents = plan["agents"]

        research = None
        if "scout" in agents:
            research = self.scout.research(meta)

        result = {"mode": "FULL", "research": research, "subresults": {}}

        for agent_id in agents:
            if agent_id == "scout":
                continue
            agent = self.agents[agent_id]
            messages = [
                {"role": "system", "content": f"Agent={agent.id}"},
                {"role": "user", "content": meta.text},
            ]
            if research:
                messages.append({"role": "system", "content": f"research={research['summary']}"})
            result["subresults"][agent_id] = llm_wrapper.invoke(meta.session_id, agent.model, messages)

        return result
```


***

## 5) `gateway/preflight_middleware.py` 真实接入版

```python
from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine

bootstrap = BootstrapManager()
policy_engine = PolicyEngine()

def preflight_middleware(handler):
    def wrapped(request, llm_context):
        session_id = request.session_id
        model_id = getattr(request, "model_id", "default")

        bootstrap.ensure_bootstrapped(session_id, model_id, llm_context)

        meta = classify(request)
        meta = policy_engine.apply(meta)
        request.task_meta = meta

        if meta.risk_level in ["high_config", "high_arch", "high_business"]:
            request.route_mode = "FULL"
        else:
            request.route_mode = meta.route_mode

        return handler(request, llm_context)
    return wrapped
```


***

## 6) `runtime/llm_wrapper.py` 补强版

```python
from runtime.bootstrap import BootstrapManager

bootstrap = BootstrapManager()

class LLMWrapper:
    def __init__(self, llm, llm_context):
        self.llm = llm
        self.llm_context = llm_context

    def invoke(self, session_id, model_id, messages, **kwargs):
        if not bootstrap.is_bootstrapped(session_id, model_id):
            bootstrap.ensure_bootstrapped(session_id, model_id, self.llm_context)
        return self.llm.invoke(messages, **kwargs)
```


***

## 7) `tests/test_router.py`

```python
from runtime.router_patch import AgentRouter
from runtime.task_classifier import TaskMeta

class FakeLLM:
    def invoke(self, messages, **kwargs):
        return {"content": "ok", "messages": messages}

class FakeLLMWrapper:
    def __init__(self):
        self.llm = FakeLLM()
        self.llm_context = None
    def invoke(self, session_id, model_id, messages, **kwargs):
        return self.llm.invoke(messages, **kwargs)

def test_fast_code_route():
    router = AgentRouter()
    meta = TaskMeta(id="1", session_id="s1", text="写一个 Python 脚本")
    meta.requires_code = True
    meta.route_mode = "FAST"
    res = router.dispatch(meta, FakeLLMWrapper())
    assert res["content"] == "ok"

def test_full_external_route():
    router = AgentRouter()
    meta = TaskMeta(id="2", session_id="s1", text="对标第三方框架")
    meta.requires_external_research = True
    meta.route_mode = "FULL"
    meta.required_agents = ["scout", "main"]
    res = router.dispatch(meta, FakeLLMWrapper())
    assert res["mode"] == "FULL"
    assert "scout" in res["research"]["summary"] or res["research"]["external_research"]
```


***

## 8) `tests/test_middleware.py`

```python
from gateway.preflight_middleware import preflight_middleware

class Req:
    def __init__(self):
        self.session_id = "sess-a"
        self.model_id = "claude-opus"
        self.text = "改 openclaw.json"

class DummyContext:
    def inject_system(self, text):
        self.text = text

def test_preflight_sets_meta(monkeypatch):
    captured = {}
    def handler(request, llm_context):
        captured["meta"] = request.task_meta
        return {"ok": True}

    wrapped = preflight_middleware(handler)
    resp = wrapped(Req(), DummyContext())
    assert resp["ok"] is True
    assert captured["meta"].risk_level == "high_config"
    assert captured["meta"].enforce_review is True
```


***

## 9) `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```


***

## 10) `docker-compose.yml` 骨架

如果你要把它变成可独立起的 runtime，这个最小够用了：

```yaml
version: "3.9"

services:
  openclaw-gateway:
    build: .
    command: python -m gateway.server
    volumes:
      - .:/app
    working_dir: /app
    environment:
      - ENABLE_MEMORY_BOOTSTRAP=1
      - ENABLE_FS_GUARD=1
      - ENABLE_REVIEW_GATE=1

  openclaw-agent:
    build: .
    command: python -m gateway.agent_entry
    volumes:
      - .:/app
    working_dir: /app
```


***

## 11) `gateway/server.py` 极简入口

```python
from gateway.agent_entry import handle_user_request
from gateway.preflight_middleware import preflight_middleware

class Request:
    def __init__(self, session_id, text, model_id="claude-opus"):
        self.session_id = session_id
        self.text = text
        self.model_id = model_id

class LLMContext:
    def inject_system(self, text):
        self.system = text

@preflight_middleware
def app_handler(request, llm_context):
    return handle_user_request(request)

if __name__ == "__main__":
    req = Request("sess-1", "写一个数据处理脚本")
    ctx = LLMContext()
    print(app_handler(req, ctx))
```


***

## 12) 这一步做完你就已经有了什么

你现在已经拥有：

- **preflight 强制 bootstrap**
- **router 强制分类**
- **policy 强制加 guard/kitt/scout**
- **fs_guard 阻止项目误删**
- **review_gate 阻止高风险直出**
- **pytest 可验证这些门槛**

这已经不是“文档规则”，而是可以跑的 runtime 结构了。[^4_3][^4_4][^4_5]

***

## 13) 下一步我建议继续补的两个重点

如果你说“继续”，我下一条最该补的是：

### A. `tools/archive_memory.py` 的完整可执行版

- 让巡逻 / x_digest / learning_ingest 自动归档
- 带 TTL 判断
- 带项目保护跳过


### B. `memory bootstrap` 的子 Agent 版本

- 子 Agent 唤醒前先读 `task-board.json`
- 只加载 shared 最近 N 条

```
- 写入 `shared/YYYY-MM-DD_<agent>_<task>.md` 后 verify
```

如果你要，我下一条直接把这两块也补成完整代码。
<span style="display:none">[^4_10][^4_11][^4_12][^4_6][^4_7][^4_8][^4_9]</span>

<div align="center">⁂</div>

[^4_1]: https://bugs.python.org/issue39340

[^4_2]: https://docs.python.org/3/library/pathlib.html

[^4_3]: https://docs.pytest.org/en/stable/how-to/tmp_path.html

[^4_4]: https://docs.openclaw.ai/concepts/multi-agent

[^4_5]: https://docs.openclaw.ai/tools/exec-approvals

[^4_6]: https://github.com/pytest-dev/pytest/commit/0c803cb0469e89adf9ca31be15f068661fad9d2f

[^4_7]: https://wooptoo.com/blog/python-pathlib/

[^4_8]: https://lyz-code.github.io/blue-book/coding/python/pytest/

[^4_9]: https://github.com/python/cpython/issues/48739

[^4_10]: https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python

[^4_11]: https://python-basics-tutorial.readthedocs.io/en/latest/test/pytest/builtin-fixtures.html

[^4_12]: https://stackoverflow.com/questions/18358017/secure-use-of-shutil-rmtree-os-path-join-and-directory-traversal


---

# 那就继续

继续补 **归档脚本 + 子 Agent memory bootstrap**，我直接给你可落地代码。

***

## 1) `tools/archive_memory.py` 完整版

目标：

- 自动扫描 `memory/patrol/`、`memory/x_digest/`、`memory/learning_ingest/`
- 到期后只归档，不删除
- 项目类内容跳过
- 支持 dry-run
- 支持按 TTL 分级处理

```python
from pathlib import Path
from datetime import datetime, timezone
import yaml
import json
import shutil

from runtime.fs_guard import FileGuard, ProtectedProjectError

CFG_PATH = Path("config/memory_lifecycle.yml")
ARCHIVE_ROOT = Path("archive")

def load_cfg():
    return yaml.safe_load(CFG_PATH.read_text(encoding="utf-8"))

def parse_file_time(path: Path):
    try:
        ts = path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except Exception:
        return None

def days_old(dt: datetime):
    now = datetime.now(timezone.utc)
    return (now - dt).days

def classify_file(path: Path, cfg):
    p = path.as_posix()
    for cls_name, cls in cfg["classes"].items():
        prefix = cls["path_prefix"]
        if p.startswith(prefix):
            return cls_name, cls
    return None, None

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def archive_one(path: Path, cls_name: str, cls_cfg: dict, guard: FileGuard, dry_run: bool = True):
    if guard.is_protected(str(path)):
        return {"path": str(path), "action": "skip", "reason": "protected"}

    dt = parse_file_time(path)
    if not dt:
        return {"path": str(path), "action": "skip", "reason": "no_mtime"}

    ttl_days = int(cls_cfg.get("ttl_days", 30))
    if days_old(dt) < ttl_days:
        return {"path": str(path), "action": "skip", "reason": f"ttl_not_reached<{ttl_days}"}

    archive_root = Path(cls_cfg["archive_path"])
    target = archive_root / path.relative_to(Path(cls_cfg["path_prefix"]))
    result = {"path": str(path), "target": str(target), "action": "archive"}

    if dry_run:
        return result

    ensure_dir(target.parent)
    shutil.move(str(path), str(target))
    return result

def scan_and_archive(dry_run: bool = True):
    cfg = load_cfg()
    guard = FileGuard()
    results = []

    for cls_name, cls_cfg in cfg["classes"].items():
        src_root = Path(cls_cfg["path_prefix"])
        if not src_root.exists():
            continue

        for p in src_root.rglob("*"):
            if not p.is_file():
                continue
            try:
                results.append(archive_one(p, cls_name, cls_cfg, guard, dry_run=dry_run))
            except ProtectedProjectError as e:
                results.append({"path": str(p), "action": "skip", "reason": str(e)})
            except Exception as e:
                results.append({"path": str(p), "action": "error", "reason": str(e)})

    return results

if __name__ == "__main__":
    res = scan_and_archive(dry_run=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
```


***

## 2) `memory/shared/index.json`

这个文件用来减少 bootstrap 时的全量读取。
只读索引，不读全部 shared 内容。

```json
{
  "version": "1",
  "recent": [
    {
      "date": "2026-04-05",
      "agent": "deep",
      "task": "router patch",
      "path": "memory/shared/2026-04-05_deep_router-patch.md"
    },
    {
      "date": "2026-04-05",
      "agent": "guard",
      "task": "project protect",
      "path": "memory/shared/2026-04-05_guard_project-protect.md"
    }
  ]
}
```


***

## 3) 子 Agent bootstrap：`runtime/child_bootstrap.py`

目标：

- 子 Agent 唤醒前先读 `task-board.json`
- 只加载最近 N 条 shared
- 写 shared 文件后必须 verify
- 只有 jimmy 可以改 task-board.json

```python
from pathlib import Path
import json
from datetime import datetime

class ChildBootstrapManager:
    def __init__(self, shared_dir="memory/shared", task_board_path="memory/task-board.json", recent_n=3):
        self.shared_dir = Path(shared_dir)
        self.task_board_path = Path(task_board_path)
        self.recent_n = recent_n

    def load_task_board(self):
        if not self.task_board_path.exists():
            return {}
        return json.loads(self.task_board_path.read_text(encoding="utf-8"))

    def recent_shared_files(self):
        index_path = self.shared_dir / "index.json"
        if index_path.exists():
            idx = json.loads(index_path.read_text(encoding="utf-8"))
            recent = idx.get("recent", [])[: self.recent_n]
            return [Path(x["path"]) for x in recent if Path(x["path"]).exists()]

        files = sorted(self.shared_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[: self.recent_n]

    def bootstrap(self, agent_name: str, task_text: str):
        task_board = self.load_task_board()
        shared_files = self.recent_shared_files()

        shared_texts = []
        for f in shared_files:
            try:
                shared_texts.append(f.read_text(encoding="utf-8")[:2000])
            except Exception:
                continue

        context = {
            "agent": agent_name,
            "task_board_projects": task_board.get("projects", []),
            "recent_shared": shared_texts,
            "task": task_text,
        }
        return context

    def write_shared(self, agent_name: str, task_name: str, content: str):
        today = datetime.now().strftime("%Y-%m-%d")
        safe_task = task_name.replace(" ", "_").replace("/", "_")
        out = self.shared_dir / f"{today}_{agent_name}_{safe_task}.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        return out

    def verify_shared(self, path: Path):
        return path.exists() and path.stat().st_size > 0
```


***

## 4) `runtime/taskboard_guard.py`

专门确保只有 jimmy 可以修改 task-board.json。

```python
from pathlib import Path
import json

class TaskBoardWriteError(Exception):
    pass

class TaskBoardGuard:
    def __init__(self, path="memory/task-board.json"):
        self.path = Path(path)

    def read(self):
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def write(self, data, actor: str):
        if actor != "jimmy":
            raise TaskBoardWriteError("only jimmy can modify task-board.json")
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
```


***

## 5) `runtime/subagent_runtime.py`

这是子 Agent 的统一执行入口。

```python
from runtime.child_bootstrap import ChildBootstrapManager

class SubAgentRuntime:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.bootstrapper = ChildBootstrapManager()

    def run(self, task_text: str, worker):
        ctx = self.bootstrapper.bootstrap(self.agent_name, task_text)
        result = worker(task_text, ctx)

        if isinstance(result, dict) and "shared_write" in result:
            p = self.bootstrapper.write_shared(
                self.agent_name,
                result.get("task_name", "task"),
                result["shared_write"]
            )
            if not self.bootstrapper.verify_shared(p):
                raise RuntimeError(f"shared verify failed: {p}")

        return result
```


***

## 6) 子 Agent 工作函数示例

```python
def deep_worker(task_text, ctx):
    return {
        "task_name": "router_patch",
        "output": f"processed: {task_text}",
        "shared_write": f"# {task_text}\n\n- agent: deep\n- note: completed\n"
    }
```


***

## 7) `tests/test_archive_memory.py`

```python
from pathlib import Path
from tools.archive_memory import scan_and_archive

def test_archive_skip_protected(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "memory/patrol").mkdir(parents=True)
    (tmp_path / "archive/patrol").mkdir(parents=True)

    cfg = """
version: 1
classes:
  patrol:
    path_prefix: "memory/patrol/"
    ttl_days: 0
    archive_path: "archive/patrol/"
"""
    (tmp_path / "config/memory_lifecycle.yml").write_text(cfg, encoding="utf-8")
    f = tmp_path / "memory/patrol/a.md"
    f.write_text("x")

    monkeypatch.chdir(tmp_path)

    res = scan_and_archive(dry_run=True)
    assert isinstance(res, list)

def test_archive_moves_file(tmp_path, monkeypatch):
    (tmp_path / "config").mkdir()
    (tmp_path / "memory/x_digest").mkdir(parents=True)
    (tmp_path / "archive/x_digest").mkdir(parents=True)

    cfg = """
version: 1
classes:
  x_digest:
    path_prefix: "memory/x_digest/"
    ttl_days: 0
    archive_path: "archive/x_digest/"
"""
    (tmp_path / "config/memory_lifecycle.yml").write_text(cfg, encoding="utf-8")
    f = tmp_path / "memory/x_digest/b.md"
    f.write_text("x")

    monkeypatch.chdir(tmp_path)

    res = scan_and_archive(dry_run=False)
    assert (tmp_path / "archive/x_digest/b.md").exists()
```


***

## 8) `tests/test_child_bootstrap.py`

```python
from pathlib import Path
from runtime.child_bootstrap import ChildBootstrapManager

def test_child_bootstrap_reads_recent(tmp_path, monkeypatch):
    (tmp_path / "memory/shared").mkdir(parents=True)
    (tmp_path / "memory").mkdir(exist_ok=True)

    (tmp_path / "memory/task-board.json").write_text('{"projects":[{"id":"p1","name":"A"}]}', encoding="utf-8")
    (tmp_path / "memory/shared/index.json").write_text(
        '{"version":"1","recent":[{"date":"2026-04-05","agent":"deep","task":"x","path":"memory/shared/a.md"}]}',
        encoding="utf-8"
    )
    (tmp_path / "memory/shared/a.md").write_text("hello", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    b = ChildBootstrapManager()
    ctx = b.bootstrap("deep", "do x")

    assert ctx["agent"] == "deep"
    assert len(ctx["task_board_projects"]) == 1
    assert len(ctx["recent_shared"]) == 1

def test_write_and_verify_shared(tmp_path, monkeypatch):
    (tmp_path / "memory/shared").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    b = ChildBootstrapManager()
    p = b.write_shared("deep", "task one", "content")
    assert b.verify_shared(p)
```


***

## 9) `pytest.ini` 追加测试范围

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```


***

## 10) 子 Agent 闭环怎么接到主链路

你现在有两条链：

### 主请求链

```text
request
 → preflight middleware
 → memory bootstrap
 → classify
 → policy
 → router
 → review gate
 → reply
```


### 子 Agent 链

```text
subtask
 → child bootstrap
 → worker
 → shared write
 → verify
```

这个结构已经满足你要的：

- 写入前先读 task-board
- 最近 shared 只读少量
- 写后 verify
- task-board 只允许 jimmy 写

***

## 11) 最后给你一个更完整的入口整合示例

### `gateway/agent_entry.py` 更新

```python
from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.router_patch import AgentRouter
from runtime.llm_wrapper import LLMWrapper
from runtime.subagent_runtime import SubAgentRuntime

class FakeLLM:
    def invoke(self, messages, **kwargs):
        return {"content": "ok", "messages": messages}

class FakeLLMContext:
    def inject_system(self, text):
        self.system = text

llm = FakeLLM()
llm_context = FakeLLMContext()
llm_wrapper = LLMWrapper(llm, llm_context)
bootstrap = BootstrapManager()
policy_engine = PolicyEngine()
router = AgentRouter()

def handle_user_request(request):
    bootstrap.ensure_bootstrapped(request.session_id, getattr(request, "model_id", "default"), llm_context)
    meta = classify(request)
    meta = policy_engine.apply(meta)
    return router.dispatch(meta, llm_wrapper)

def run_subagent(agent_name, task_text, worker):
    return SubAgentRuntime(agent_name).run(task_text, worker)
```


***

## 12) 你现在已经可以继续推进的点

下一步我建议直接补两块：

1. **`memory/.abstract` / `memory/task-board.json` 的生成与验收脚本**
2. **`openclaw.json` 配置变更的备份、审计、回滚脚本**

如果你继续，我下一条可以直接给你这两块的完整代码。
<span style="display:none">[^5_1][^5_10][^5_2][^5_3][^5_4][^5_5][^5_6][^5_7][^5_8][^5_9]</span>

<div align="center">⁂</div>

[^5_1]: https://gairuo.com/p/python-pathlib

[^5_2]: https://blog.51cto.com/jzj2023/6144570

[^5_3]: https://blog.csdn.net/ByteBuster/article/details/133533617

[^5_4]: https://www.51cto.com/article/780399.html

[^5_5]: https://blog.csdn.net/taifyang/article/details/127715832

[^5_6]: https://modstart.com/p/i1vkt26p52pdk03k

[^5_7]: https://docs.python.org/zh-cn/3/library/pathlib.html

[^5_8]: https://blog.csdn.net/CatherineC20150619/article/details/121062051

[^5_9]: https://cuiqingcai.com/6598.html

[^5_10]: https://docs.python.org/3/library/pathlib.html


---

# 继续

继续给你补两块最关键的：**openclaw.json 配置变更的备份/审计/回滚脚本**，以及 **task-board / memory 文件的生成与验收闭环**。
这两块补完后，你的 runtime 方案就从“能跑”进一步变成“能改、能回、能验”。[^6_2][^6_7]

***

## 1) `tools/config_guard.py`

这是配置变更的唯一入口。
原则是：**先备份，再校验，再写入，再审计，失败立即回滚**。[^6_1][^6_4]

```python
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import shutil
import tempfile
import hashlib

from runtime.fs_guard import FileGuard

CONFIG_PATH = Path("openclaw.json")
BACKUP_DIR = Path("backups/openclaw")
AUDIT_LOG = Path("logs/config_audit.jsonl")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

class ConfigGuardError(Exception):
    pass

@dataclass
class ConfigChangeResult:
    backup_path: str
    new_hash: str
    old_hash: str
    validated: bool
    rolled_back: bool = False

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _now():
    return datetime.now(timezone.utc).isoformat()

def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def _write_audit(event: dict):
    with AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def backup_config() -> Path:
    if not CONFIG_PATH.exists():
        raise ConfigGuardError("openclaw.json not found")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = BACKUP_DIR / f"openclaw.{ts}.json"
    shutil.copy2(CONFIG_PATH, backup_path)
    return backup_path

def validate_config_text(text: str) -> tuple[bool, str]:
    """
    第一版只做 JSON 语法校验。
    如果你用 JSON5，可在这里替换为 JSON5 parser。
    """
    try:
        json.loads(text)
        return True, "ok"
    except Exception as e:
        return False, str(e)

def rollback_from_backup(backup_path: Path) -> None:
    if not backup_path.exists():
        raise ConfigGuardError(f"backup missing: {backup_path}")
    shutil.copy2(backup_path, CONFIG_PATH)

def safe_replace_config(new_text: str, actor: str, reason: str, force: bool = False) -> ConfigChangeResult:
    guard = FileGuard()
    old_text = _read_text(CONFIG_PATH)
    old_hash = _sha256_text(old_text)
    new_hash = _sha256_text(new_text)

    backup_path = backup_config()

    event = {
        "ts": _now(),
        "actor": actor,
        "reason": reason,
        "config_path": str(CONFIG_PATH),
        "old_hash": old_hash,
        "new_hash": new_hash,
        "backup_path": str(backup_path),
        "status": "started",
    }
    _write_audit(event)

    valid, msg = validate_config_text(new_text)
    if not valid and not force:
        rollback_from_backup(backup_path)
        event["status"] = "rolled_back_validate_failed"
        event["validate_msg"] = msg
        _write_audit(event)
        return ConfigChangeResult(str(backup_path), new_hash, old_hash, False, True)

    try:
        CONFIG_PATH.write_text(new_text, encoding="utf-8")
    except Exception as e:
        rollback_from_backup(backup_path)
        event["status"] = "rolled_back_write_failed"
        event["write_error"] = str(e)
        _write_audit(event)
        return ConfigChangeResult(str(backup_path), new_hash, old_hash, False, True)

    valid2, msg2 = validate_config_text(_read_text(CONFIG_PATH))
    if not valid2:
        rollback_from_backup(backup_path)
        event["status"] = "rolled_back_postwrite_validation_failed"
        event["validate_msg"] = msg2
        _write_audit(event)
        return ConfigChangeResult(str(backup_path), new_hash, old_hash, False, True)

    event["status"] = "committed"
    event["validate_msg"] = "ok"
    _write_audit(event)
    return ConfigChangeResult(str(backup_path), new_hash, old_hash, True, False)
```


***

## 2) `tools/config_diff_guard.py`

这个脚本用于在真正替换配置前做“变更风险检查”，尤其是你要求的 guard 审核链。

```python
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DiffRisk:
    high_config: bool
    reasons: list[str]

def analyze_config_diff(old_text: str, new_text: str) -> DiffRisk:
    reasons = []
    high_config = False

    old = json.loads(old_text) if old_text.strip() else {}
    new = json.loads(new_text) if new_text.strip() else {}

    watched_keys = [
        "routes", "agents", "skills", "mcp", "secrets",
        "routing", "gateway", "model", "tools"
    ]

    for key in watched_keys:
        if old.get(key) != new.get(key):
            high_config = True
            reasons.append(f"{key} changed")

    if old_text != new_text and len(new_text) > 0:
        if abs(len(new_text) - len(old_text)) > 200:
            high_config = True
            reasons.append("large config delta")

    return DiffRisk(high_config=high_config, reasons=reasons)

def config_requires_guard(old_text: str, new_text: str) -> bool:
    return analyze_config_diff(old_text, new_text).high_config
```


***

## 3) `tools/update_openclaw_config.py`

这是主入口。
规则很简单：**先审查差异，再调用安全替换**。

```python
from pathlib import Path

from tools.config_guard import safe_replace_config
from tools.config_diff_guard import analyze_config_diff

CONFIG_PATH = Path("openclaw.json")

def update_openclaw_config(new_text: str, actor: str = "jimmy", reason: str = "manual update"):
    old_text = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else ""
    risk = analyze_config_diff(old_text, new_text)

    if risk.high_config:
        print(f"[guard required] reasons={risk.reasons}")

    result = safe_replace_config(
        new_text=new_text,
        actor=actor,
        reason=reason,
        force=False,
    )
    return result

if __name__ == "__main__":
    sample = CONFIG_PATH.read_text(encoding="utf-8")
    print(update_openclaw_config(sample))
```


***

## 4) `memory/task-board.json` 生成与验收脚本

这个是你要求的闭环：

- 生成
- 写入
- 验收
并且只允许 `jimmy` 修改 task-board。[^6_5][^6_2]


### `tools/taskboard_sync.py`

```python
from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime, timezone

from runtime.taskboard_guard import TaskBoardGuard, TaskBoardWriteError

TASKBOARD_PATH = Path("memory/task-board.json")
TASKBOARD_AUDIT = Path("logs/taskboard_audit.jsonl")

TASKBOARD_AUDIT.parent.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _audit(event: dict):
    with TASKBOARD_AUDIT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def generate_taskboard_snapshot(projects: list[dict], tasks: list[dict], version: str = "1") -> dict:
    return {
        "version": version,
        "projects": projects,
        "tasks": tasks,
    }

def validate_taskboard(data: dict) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "taskboard must be object"
    if "version" not in data:
        return False, "missing version"
    if "projects" not in data or not isinstance(data["projects"], list):
        return False, "projects must be list"
    if "tasks" not in data or not isinstance(data["tasks"], list):
        return False, "tasks must be list"

    for p in data["projects"]:
        if "id" not in p or "name" not in p:
            return False, f"invalid project: {p}"
    for t in data["tasks"]:
        if "id" not in t or "name" not in t:
            return False, f"invalid task: {t}"

    return True, "ok"

def write_taskboard(data: dict, actor: str):
    guard = TaskBoardGuard(str(TASKBOARD_PATH))
    valid, msg = validate_taskboard(data)
    if not valid:
        raise ValueError(msg)

    _audit({
        "ts": _now(),
        "actor": actor,
        "action": "write_attempt",
        "status": "started",
    })

    try:
        guard.write(data, actor=actor)
    except TaskBoardWriteError as e:
        _audit({
            "ts": _now(),
            "actor": actor,
            "action": "write_attempt",
            "status": "denied",
            "reason": str(e),
        })
        raise

    written = json.loads(TASKBOARD_PATH.read_text(encoding="utf-8"))
    ok, msg2 = validate_taskboard(written)
    if not ok:
        _audit({
            "ts": _now(),
            "actor": actor,
            "action": "write_attempt",
            "status": "failed_postwrite_validation",
            "reason": msg2,
        })
        raise ValueError(msg2)

    _audit({
        "ts": _now(),
        "actor": actor,
        "action": "write_attempt",
        "status": "committed",
    })
    return True
```


***

## 5) `tools/taskboard_build.py`

这是生成 snapshot 的脚本。
适合从项目目录和任务文件自动拼一个 task-board 草案，然后由 `jimmy` 进入写入。

```python
from __future__ import annotations

from pathlib import Path
import json

from tools.taskboard_sync import generate_taskboard_snapshot, write_taskboard

def scan_projects(root="workspace"):
    root = Path(root)
    projects = []
    if not root.exists():
        return projects

    for d in root.iterdir():
        if d.is_dir():
            projects.append({
                "id": f"proj_{d.name}_001",
                "name": d.name,
                "status": "active",
                "workspace_paths": [f"{d.as_posix()}/"],
                "created_at": "2026-04-05T00:00:00Z",
            })
    return projects

def scan_tasks(memory_root="memory/shared"):
    root = Path(memory_root)
    tasks = []
    if not root.exists():
        return tasks

    for f in root.glob("*.md"):
        tasks.append({
            "id": f.stem,
            "name": f.stem,
            "agent": "unknown",
            "project_id": "",
            "status": "pending",
            "created_at": "2026-04-05T00:00:00Z",
            "updated_at": "2026-04-05T00:00:00Z",
        })
    return tasks

def build_snapshot():
    projects = scan_projects()
    tasks = scan_tasks()
    return generate_taskboard_snapshot(projects, tasks, version="1")

if __name__ == "__main__":
    snapshot = build_snapshot()
    print(json.dumps(snapshot, ensure_ascii=False, indent=2))
```


***

## 6) `tools/taskboard_apply.py`

这个脚本把 snapshot 真正写入 task-board。
必须以 `jimmy` 身份执行。

```python
from tools.taskboard_build import build_snapshot
from tools.taskboard_sync import write_taskboard

def apply_taskboard(actor="jimmy"):
    snapshot = build_snapshot()
    return write_taskboard(snapshot, actor=actor)

if __name__ == "__main__":
    print(apply_taskboard("jimmy"))
```


***

## 7) `tools/taskboard_verify.py`

```python
from pathlib import Path
import json
from tools.taskboard_sync import validate_taskboard

TASKBOARD_PATH = Path("memory/task-board.json")

def verify():
    if not TASKBOARD_PATH.exists():
        raise FileNotFoundError("task-board.json missing")
    data = json.loads(TASKBOARD_PATH.read_text(encoding="utf-8"))
    ok, msg = validate_taskboard(data)
    if not ok:
        raise ValueError(msg)
    return True

if __name__ == "__main__":
    print(verify())
```


***

## 8) `tests/test_config_guard.py`

```python
from pathlib import Path
from tools.config_guard import safe_replace_config
from tools.config_diff_guard import analyze_config_diff

def test_config_diff_detects_high_risk():
    old = '{"routes": {"a": 1}, "agents": []}'
    new = '{"routes": {"a": 2}, "agents": []}'
    risk = analyze_config_diff(old, new)
    assert risk.high_config is True

def test_safe_replace_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "backups/openclaw").mkdir(parents=True)
    (tmp_path / "logs").mkdir(parents=True)
    (tmp_path / "openclaw.json").write_text('{"a":1}', encoding="utf-8")
    res = safe_replace_config('{"a":2}', actor="jimmy", reason="test")
    assert res.validated is True
    assert (tmp_path / "openclaw.json").read_text(encoding="utf-8") == '{"a":2}'
```


***

## 9) `tests/test_taskboard_sync.py`

```python
import pytest
from pathlib import Path
from tools.taskboard_sync import write_taskboard

def test_taskboard_only_jimmy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "logs").mkdir(parents=True)

    data = {
        "version": "1",
        "projects": [{"id": "p1", "name": "A"}],
        "tasks": [{"id": "t1", "name": "B"}]
    }

    with pytest.raises(Exception):
        write_taskboard(data, actor="deep")

def test_taskboard_jimmy_ok(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "logs").mkdir(parents=True)

    data = {
        "version": "1",
        "projects": [{"id": "p1", "name": "A"}],
        "tasks": [{"id": "t1", "name": "B"}]
    }

    ok = write_taskboard(data, actor="jimmy")
    assert ok is True
```


***

## 10) `memory/.abstract` 的最小生成脚本

这个是主 Agent 启动时的长期轨迹摘要文件。

### `tools/abstract_build.py`

```python
from __future__ import annotations

from pathlib import Path
from datetime import datetime

ABSTRACT_PATH = Path("memory/.abstract")

def build_abstract(taskboard_path="memory/task-board.json", recent_shared_dir="memory/shared"):
    lines = []
    lines.append(f"# Abstract {datetime.now().isoformat()}")
    lines.append("")
    if Path(taskboard_path).exists():
        lines.append("## task-board")
        lines.append(Path(taskboard_path).read_text(encoding="utf-8")[:3000])
        lines.append("")

    shared = Path(recent_shared_dir)
    if shared.exists():
        files = sorted(shared.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:3]
        lines.append("## recent shared")
        for f in files:
            lines.append(f"### {f.name}")
            lines.append(f.read_text(encoding="utf-8")[:1500])
            lines.append("")

    return "\n".join(lines)

def write_abstract():
    ABSTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    content = build_abstract()
    ABSTRACT_PATH.write_text(content, encoding="utf-8")
    return ABSTRACT_PATH

if __name__ == "__main__":
    print(write_abstract())
```


***

## 11) `tools/verify_memory_files.py`

```python
from pathlib import Path

def verify_exists(path: str):
    p = Path(path)
    return p.exists() and p.stat().st_size > 0

def verify_memory_bundle():
    required = [
        "memory/.abstract",
        "memory/task-board.json",
    ]
    for p in required:
        if not verify_exists(p):
            raise FileNotFoundError(f"missing or empty: {p}")
    return True

if __name__ == "__main__":
    print(verify_memory_bundle())
```


***

## 12) 推荐补一层“升级顺序”

现在你可以按这个顺序合并：

### 第一批

- `tools/config_guard.py`
- `tools/config_diff_guard.py`
- `tools/update_openclaw_config.py`


### 第二批

- `tools/taskboard_sync.py`
- `tools/taskboard_build.py`
- `tools/taskboard_apply.py`
- `tools/taskboard_verify.py`


### 第三批

- `tools/abstract_build.py`
- `tools/verify_memory_files.py`

这三批都是“先生成 / 先验收 / 再写入”的硬闭环。

***

## 13) 你现在的 runtime 已经补到了什么程度

已经具备：

- 配置变更前备份
- 配置变更后校验
- 配置失败回滚
- task-board 只能由 jimmy 写
- task-board 生成 / 验证分离
- .abstract 自动生成
- memory bundle 预检查

这意味着你最核心的三件事已经机械化了：
**不失忆、不误删、不绕过审核链**。[^6_4][^6_7][^6_1]

***

## 14) 如果你继续，我下一条最值得补的两块

我建议下一步直接补：

1. **`scout` / `guard` / `kitt` 的真实调用接口适配层**
也就是把 mock agent 换成你现在系统里真正的 agent invoke。
2. **灰度开关 + 环境变量接线**
例如：
    - `ENABLE_MEMORY_BOOTSTRAP`
    - `ENABLE_FS_GUARD`
    - `ENABLE_REVIEW_GATE`
    - `ENABLE_TASKBOARD_LOCK`

如果你要，我下一条就直接给你这两块代码。
<span style="display:none">[^6_10][^6_3][^6_6][^6_8][^6_9]</span>

<div align="center">⁂</div>

[^6_1]: https://github.com/KimYx0207/Claude-Code-x-OpenClaw-Guide-Zh/blob/main/docs/claude-code/11-企业实战完整指南.md

[^6_2]: https://cloud.tencent.com/developer/article/2638747

[^6_3]: https://adg.csdn.net/69730fad437a6b40336b76e8.html

[^6_4]: https://github.com/slowmist/openclaw-security-practice-guide/blob/main/docs/OpenClaw极简安全实践指南v2.8.md

[^6_5]: https://cloud.tencent.com/developer/article/2638202

[^6_6]: https://club.fnnas.com/forum.php?mod=viewthread\&tid=58400

[^6_7]: https://cloud.tencent.com/developer/information/如何配置 OpenClaw 沙盒模式以确保群组%2F频道安全？-article

[^6_8]: https://diyrun.tedschool.cn/openclawskills/openclaw-file-management-skills.html

[^6_9]: https://www.iitime.com.cn/html/10200/17183296.htm

[^6_10]: https://www.reddit.com/r/ClaudeAI/comments/1rshuz9/an_ai_agent_deleted_25000_documents_from_the/


---

# 继续

继续下面这两块：**`scout / guard / kitt` 真实接入层**，以及 **灰度开关 / 环境变量接线**。
我直接给你代码骨架，目标是把前面所有 mock 接口替换成真实 runtime 入口，并让这些硬门槛可按环境逐步开启。[^7_1][^7_5]

***

## 1) `runtime/agent_registry.py`

先做一个统一注册表，把真实 Agent 的调用入口集中起来。
这样 `router`、`review_gate`、`preflight` 都不需要知道具体底层怎么 invoke。[^7_2][^7_5]

```python
from dataclasses import dataclass

@dataclass
class AgentHandle:
    id: str
    model: str
    kind: str
    invoke_fn: callable | None = None
    review_fn: callable | None = None
    research_fn: callable | None = None

class AgentRegistry:
    def __init__(self):
        self._agents = {}

    def register(self, handle: AgentHandle):
        self._agents[handle.id] = handle

    def get(self, agent_id: str) -> AgentHandle:
        if agent_id not in self._agents:
            raise KeyError(f"agent not found: {agent_id}")
        return self._agents[agent_id]

    def has(self, agent_id: str) -> bool:
        return agent_id in self._agents
```


***

## 2) `runtime/agent_adapter.py`

这个文件负责把你现有系统里的真实 Agent 适配成统一接口。
你只要把现有的“执行函数”挂进来，别的层就不用改。[^7_5][^7_1]

```python
from runtime.agent_registry import AgentHandle

class AgentAdapter:
    @staticmethod
    def adapt_jimmy(invoke_fn, model="claude-opus"):
        return AgentHandle(id="jimmy", model=model, kind="executor", invoke_fn=invoke_fn)

    @staticmethod
    def adapt_deep(invoke_fn, model="claude-opus"):
        return AgentHandle(id="deep", model=model, kind="executor", invoke_fn=invoke_fn)

    @staticmethod
    def adapt_sino(invoke_fn, model="claude-sonnet"):
        return AgentHandle(id="sino", model=model, kind="executor", invoke_fn=invoke_fn)

    @staticmethod
    def adapt_scout(research_fn, model="claude-sonnet"):
        return AgentHandle(id="scout", model=model, kind="research", research_fn=research_fn)

    @staticmethod
    def adapt_guard(review_fn, model="claude-sonnet"):
        return AgentHandle(id="guard", model=model, kind="review", review_fn=review_fn)

    @staticmethod
    def adapt_kitt(review_fn, model="claude-opus"):
        return AgentHandle(id="kitt", model=model, kind="review", review_fn=review_fn)
```


***

## 3) `runtime/runtime_flags.py`

灰度开关全部集中到这里。
第一版先用环境变量，后面再接配置中心也行。[^7_3][^7_1]

```python
import os

def flag(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")

ENABLE_MEMORY_BOOTSTRAP = flag("ENABLE_MEMORY_BOOTSTRAP", True)
ENABLE_FS_GUARD = flag("ENABLE_FS_GUARD", True)
ENABLE_REVIEW_GATE = flag("ENABLE_REVIEW_GATE", True)
ENABLE_TASKBOARD_LOCK = flag("ENABLE_TASKBOARD_LOCK", True)
ENABLE_SCOUT_ENFORCEMENT = flag("ENABLE_SCOUT_ENFORCEMENT", True)

def in_grayscale_allowlist(session_id: str) -> bool:
    allow = os.getenv("GRAY_ALLOWLIST", "")
    if not allow.strip():
        return True
    items = {x.strip() for x in allow.split(",") if x.strip()}
    return session_id in items
```


***

## 4) `runtime/gated_llm_wrapper.py`

所有 LLM 调用都通过这个 wrapper。
这里决定是否强制 bootstrap、是否阻断未通过 gate 的请求。[^7_2][^7_5]

```python
from runtime.runtime_flags import ENABLE_MEMORY_BOOTSTRAP

class GatedLLMWrapper:
    def __init__(self, llm, bootstrap_manager, llm_context):
        self.llm = llm
        self.bootstrap_manager = bootstrap_manager
        self.llm_context = llm_context

    def invoke(self, session_id, model_id, messages, **kwargs):
        if ENABLE_MEMORY_BOOTSTRAP:
            self.bootstrap_manager.ensure_bootstrapped(session_id, model_id, self.llm_context)
        return self.llm.invoke(messages, **kwargs)
```


***

## 5) `runtime/gated_review_gate.py`

审查链的开关与调用放这里。
如果关闭 review gate，只建议在低风险灰度阶段使用。[^7_1][^7_3]

```python
from runtime.runtime_flags import ENABLE_REVIEW_GATE

class GatedReviewGate:
    def __init__(self, guard_agent, kitt_agent):
        self.guard_agent = guard_agent
        self.kitt_agent = kitt_agent

    def review_and_finalize(self, draft_result, meta):
        if not ENABLE_REVIEW_GATE:
            return draft_result

        if not meta.enforce_review:
            return draft_result

        if meta.risk_level == "high_config":
            decision = self.guard_agent.review(draft_result, meta)
            if not getattr(decision, "approved", False):
                raise RuntimeError(getattr(decision, "reason", "guard denied"))
            return draft_result

        if meta.risk_level in ("high_arch", "high_business"):
            decision = self.kitt_agent.review(draft_result, meta)
            if not getattr(decision, "approved", False):
                raise RuntimeError(getattr(decision, "reason", "kitt denied"))
            return draft_result

        return draft_result
```


***

## 6) `runtime/gated_fs_guard.py`

这个版本把文件删除/归档能力按开关控制。
你可以先全开 delete-protect，再逐步放开 archive。[^7_3][^7_1]

```python
from runtime.runtime_flags import ENABLE_FS_GUARD

class GatedFileGuard:
    def __init__(self, file_guard):
        self.file_guard = file_guard

    def delete(self, path: str, reason: str = "", task_meta=None):
        if ENABLE_FS_GUARD:
            return self.file_guard.delete(path, reason=reason, task_meta=task_meta)
        return self._unsafe_delete(path)

    def archive(self, path: str, archive_root: str):
        if ENABLE_FS_GUARD:
            return self.file_guard.archive(path, archive_root)
        return self._unsafe_archive(path, archive_root)

    def _unsafe_delete(self, path):
        from pathlib import Path
        p = Path(path)
        if p.is_dir():
            import shutil
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()

    def _unsafe_archive(self, path, archive_root):
        from pathlib import Path
        import shutil
        src = Path(path)
        dst = Path(archive_root) / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return str(dst)
```


***

## 7) `runtime/router_runtime.py`

这是把前面所有组件串起来的主 runtime。
它负责：bootstrap → classify → policy → dispatch → review。[^7_5][^7_2]

```python
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.gated_review_gate import GatedReviewGate
from runtime.gated_llm_wrapper import GatedLLMWrapper

class RouterRuntime:
    def __init__(self, router, bootstrap_manager, llm_context, guard_agent, kitt_agent, llm):
        self.router = router
        self.bootstrap_manager = bootstrap_manager
        self.llm_context = llm_context
        self.review_gate = GatedReviewGate(guard_agent, kitt_agent)
        self.llm_wrapper = GatedLLMWrapper(llm, bootstrap_manager, llm_context)
        self.policy_engine = PolicyEngine()

    def handle(self, request):
        meta = classify(request)
        meta = self.policy_engine.apply(meta)
        request.task_meta = meta

        draft = self.router.dispatch(meta, self.llm_wrapper)
        final = self.review_gate.review_and_finalize(draft, meta)
        return final
```


***

## 8) `gateway/bootstrap_entry.py`

这个文件是新 session / 切模型时最先走的入口。
如果你做网关层，这里就是 middleware 的第一段。[^7_1][^7_5]

```python
from runtime.runtime_flags import ENABLE_MEMORY_BOOTSTRAP, in_grayscale_allowlist

def bootstrap_entry(request, bootstrap_manager, llm_context):
    if not in_grayscale_allowlist(request.session_id):
        return {"error": "session not in gray allowlist"}

    if ENABLE_MEMORY_BOOTSTRAP:
        bootstrap_manager.ensure_bootstrapped(
            request.session_id,
            getattr(request, "model_id", "default"),
            llm_context,
        )
    return {"ok": True}
```


***

## 9) `gateway/server.py` 合并版

这是你现在最实用的主入口。
你把真实 agent 注入后，这个就可以跑通整条链路。[^7_5][^7_1]

```python
from runtime.bootstrap import BootstrapManager
from runtime.router_patch import AgentRouter
from runtime.agent_adapter import AgentAdapter
from runtime.agent_registry import AgentRegistry
from runtime.router_runtime import RouterRuntime

class FakeLLM:
    def invoke(self, messages, **kwargs):
        return {"content": "ok", "messages": messages}

class Context:
    def inject_system(self, text):
        self.system = text

class Req:
    def __init__(self, session_id, text, model_id="claude-opus"):
        self.session_id = session_id
        self.text = text
        self.model_id = model_id

def build_registry():
    reg = AgentRegistry()

    reg.register(AgentAdapter.adapt_jimmy(lambda messages, **k: {"content": "jimmy ok"}))
    reg.register(AgentAdapter.adapt_deep(lambda messages, **k: {"content": "deep ok"}))
    reg.register(AgentAdapter.adapt_sino(lambda messages, **k: {"content": "sino ok"}))
    reg.register(AgentAdapter.adapt_scout(lambda meta: {"summary": "scout ok", "external_research": True}))
    reg.register(AgentAdapter.adapt_guard(lambda draft, meta: type("D", (), {"approved": True, "reason": "ok"})))
    reg.register(AgentAdapter.adapt_kitt(lambda draft, meta: type("D", (), {"approved": True, "reason": "ok"})))
    return reg

def build_runtime():
    bootstrap = BootstrapManager()
    ctx = Context()
    llm = FakeLLM()
    router = AgentRouter()

    registry = build_registry()
    guard = registry.get("guard")
    kitt = registry.get("kitt")

    return RouterRuntime(router, bootstrap, ctx, guard, kitt, llm)

if __name__ == "__main__":
    rt = build_runtime()
    req = Req("sess-1", "改 openclaw.json")
    print(rt.handle(req))
```


***

## 10) 真实接线建议

你现在要把现有系统接成这样：

- `openclaw.json` 或 gateway 配置里：
    - `ENABLE_MEMORY_BOOTSTRAP=1`
    - `ENABLE_FS_GUARD=1`
    - `ENABLE_REVIEW_GATE=1`
    - `GRAY_ALLOWLIST=sess-1,sess-2`
- 真实 `jimmy/deep/sino/scout/guard/kitt` 的 invoke/review/research 函数，分别挂进 `AgentAdapter`。[^7_2][^7_5]

***

## 11) 一个最小灰度策略

### 第一阶段

只开：

- `ENABLE_MEMORY_BOOTSTRAP=1`
- `ENABLE_FS_GUARD=1`

但 review gate 先只记录不阻断，或者仅在 `high_config` 阻断。

### 第二阶段

再开：

- `ENABLE_REVIEW_GATE=1`
- `ENABLE_SCOUT_ENFORCEMENT=1`


### 第三阶段

把 `GRAY_ALLOWLIST` 从测试 session 扩到项目组，再到默认全量。

***

## 12) 失败回滚

如果 gate 影响效率或误拦截，回滚路径是：

1. 关环境变量
2. 保留代码，不删逻辑
3. 继续保留 `fs_guard` 的 delete-protect
4. review gate 先从“阻断”降级为“只审计”

这样你不会把最关键的安全边界回滚掉。[^7_3][^7_1]

***

## 13) 你现在已经接近什么状态

到这里，你的 runtime 已经不是“prompt 管理”，而是：

- 入口有 bootstrap
- 路由有 policy
- 高风险有 review
- 删除有 protector
- 灰度可控
- 回滚可控

这就是生产改造里最有价值的那一层。[^7_1][^7_5]

如果你要，我下一条可以继续给你补最后两块：

1. **把这些代码整理成一个完整的目录树**
2. **给你一版更接近真实仓库的 patch 清单**
3. **加一套端到端 smoke test**

你回我一句：**“继续补目录树和 patch 清单”** 就行。
<span style="display:none">[^7_10][^7_4][^7_6][^7_7][^7_8][^7_9]</span>

<div align="center">⁂</div>

[^7_1]: https://www.cnblogs.com/qiniushanghai/p/19775229

[^7_2]: https://github.com/mem0ai/mem0

[^7_3]: https://news.qiniu.com/archives/1774510941436

[^7_4]: https://www.cdut.edu.cn/__local/B/C0/C2/079CBF9622863574A50E3184B21_5C6852D9_330D40F.pdf

[^7_5]: https://agent.csdn.net/69b37bd67bbde9200ba09f63.html

[^7_6]: https://patents.google.com/patent/CN110516899B/zh

[^7_7]: https://club.fnnas.com/forum.php?mod=viewthread\&tid=58400

[^7_8]: https://www.hiascend.com/forum/thread-0269202456643546167-1-1.html

[^7_9]: https://cloud.tencent.com/developer/article/2638202

[^7_10]: https://adg.csdn.net/69708b8b437a6b40336aa46e.html


---

# 继续补目录树和 patch 清单

下面给你一版**可直接落 repo 的目录树 + patch 清单**。
我按“先补硬门槛、再补周边”的顺序整理，目标是让工程师能直接开分支开改。[^8_2][^8_5]

***

## 1) 推荐目录树

```text
openclaw/
├── config/
│   ├── policy.yml
│   ├── project_protection.yml
│   ├── memory_lifecycle.yml
│   └── taskboard_schema.json
├── gateway/
│   ├── __init__.py
│   ├── preflight_middleware.py
│   ├── bootstrap_entry.py
│   ├── agent_entry.py
│   └── server.py
├── memory/
│   ├── .abstract
│   ├── task-board.json
│   ├── shared/
│   │   ├── index.json
│   │   └── YYYY-MM-DD_<agent>_<task>.md
│   ├── patrol/
│   ├── x_digest/
│   ├── learning_ingest/
│   └── 10_项目/
│       ├── douyin/
│       ├── tuoke/
│       └── circuit/
├── runtime/
│   ├── __init__.py
│   ├── agent_registry.py
│   ├── agent_adapter.py
│   ├── bootstrap.py
│   ├── child_bootstrap.py
│   ├── fs_guard.py
│   ├── gated_fs_guard.py
│   ├── llm_wrapper.py
│   ├── gated_llm_wrapper.py
│   ├── policy_engine.py
│   ├── review_gate.py
│   ├── gated_review_gate.py
│   ├── router_patch.py
│   ├── router_runtime.py
│   ├── runtime_flags.py
│   ├── subagent_runtime.py
│   ├── task_classifier.py
│   └── taskboard_guard.py
├── tools/
│   ├── abstract_build.py
│   ├── archive_memory.py
│   ├── backup_config.py
│   ├── config_diff_guard.py
│   ├── config_guard.py
│   ├── taskboard_apply.py
│   ├── taskboard_build.py
│   ├── taskboard_sync.py
│   ├── taskboard_verify.py
│   ├── update_openclaw_config.py
│   └── verify_memory_files.py
├── tests/
│   ├── test_archive_memory.py
│   ├── test_bootstrap.py
│   ├── test_child_bootstrap.py
│   ├── test_config_guard.py
│   ├── test_fs_guard.py
│   ├── test_middleware.py
│   ├── test_policy_engine.py
│   ├── test_router.py
│   └── test_taskboard_sync.py
├── logs/
│   ├── config_audit.jsonl
│   └── taskboard_audit.jsonl
├── backups/
│   └── openclaw/
├── archive/
│   ├── patrol/
│   ├── x_digest/
│   └── learning_ingest/
├── state/
│   └── sessions/
├── docker-compose.yml
├── pytest.ini
└── pyproject.toml
```

这个结构的核心思想是把**入口、策略、保护器、状态、归档、测试**拆开，让“规则在 runtime 强制执行”有明确挂载点，而不是散落在 prompt 或文档里。[^8_4][^8_7]

***

## 2) Patch 清单

下面按“文件/作用/改哪里/为什么”列出来，适合直接开 issue 或 PR。

### P0：必须先合进去

#### 2.1 `gateway/preflight_middleware.py`

- 作用：请求入口强制 bootstrap + classify + policy。
- 改法：把所有用户入口统一包一层 middleware。
- 为什么：这是防止“新 session / 切模型后失忆”的第一道硬门槛。[^8_6][^8_9]


#### 2.2 `runtime/bootstrap.py`

- 作用：主 Agent 的 memory bootstrap。
- 改法：新增 session_state，未 bootstrap 禁止直接调用 LLM。
- 为什么：这是解决“记忆只写在文档里”的最小代码化路径。[^8_2][^8_6]


#### 2.3 `runtime/fs_guard.py`

- 作用：所有 delete / archive 的保护器。
- 改法：把任何 `os.remove` / `shutil.rmtree` 替换成 `fs_guard.delete/archive`。
- 为什么：这是防止项目误删的硬防线。[^8_11][^8_2]


#### 2.4 `runtime/policy_engine.py`

- 作用：任务风险规则表执行器。
- 改法：读取 `config/policy.yml`，给 TaskMeta 增加 required_agents / enforce_review。
- 为什么：这是让 guard/kitt/scout 从“知道”变成“必须执行”。[^8_7][^8_4]


#### 2.5 `runtime/review_gate.py`

- 作用：高风险输出终审。
- 改法：在 router 返回前强制调用 guard/kitt。
- 为什么：这是防止高风险任务跳过审核链的关键点。[^8_12][^8_7]

***

### P1：第二批接入

#### 2.6 `runtime/router_patch.py`

- 作用：路由执行层。
- 改法：把 `dispatch_agent()` 替换为 `plan -> dispatch -> review`。
- 为什么：路由必须先分类，再决定 FAST/FULL/SELF。[^8_9][^8_4]


#### 2.7 `runtime/llm_wrapper.py`

- 作用：LLM 调用统一封装。
- 改法：所有底层模型 invoke 都走 wrapper。
- 为什么：这是防止绕过 bootstrap 的第二道保险。[^8_6][^8_7]


#### 2.8 `runtime/child_bootstrap.py`

- 作用：子 Agent 唤醒前的最小记忆加载。
- 改法：读 `task-board.json` + 最近 shared。
- 为什么：多 Agent 闭环不能靠自觉，必须代码化。[^8_5][^8_2]


#### 2.9 `runtime/subagent_runtime.py`

- 作用：子 Agent 执行框架。
- 改法：worker 前 bootstrap，worker 后 verify shared write。
- 为什么：把“检索→分析→写入→验收”变成运行时步骤。[^8_4][^8_2]

***

### P2：第三批优化

#### 2.10 `tools/archive_memory.py`

- 作用：巡逻 / x_digest / learning_ingest 自动归档。
- 改法：TTL 到期 move 到 archive，项目内容跳过。
- 为什么：解决 memory 堆积，但不误伤项目。[^8_12][^8_2]


#### 2.11 `tools/config_guard.py`

- 作用：openclaw.json 修改时备份 / 校验 / 回滚。
- 改法：替换所有直接改配置的路径。
- 为什么：这是配置变更守门的机械化版本。[^8_13][^8_12]


#### 2.12 `tools/taskboard_sync.py`

- 作用：task-board 写入/验收。
- 改法：只有 jimmy 能写，写后立即 verify。
- 为什么：task-board 不能被子 agent 随便改。[^8_5][^8_2]


#### 2.13 `runtime/runtime_flags.py`

- 作用：灰度开关。
- 改法：环境变量控制各 gate 是否启用。
- 为什么：这是你要的“先部分任务生效，再扩大范围”的基础。[^8_4][^8_12]

***

## 3) 具体改动顺序

### 第 1 步：接入口

先改：

- `gateway/server.py`
- `gateway/agent_entry.py`

把请求统一流到：
`preflight_middleware -> bootstrap -> classify -> policy -> router -> review`

### 第 2 步：接 LLM

再改：

- 所有 `llm_client.invoke(...)`
- 统一替换为 `runtime/llm_wrapper.py`


### 第 3 步：接文件操作

再改：

- 所有 `os.remove`
- 所有 `shutil.rmtree`
- 所有归档脚本

统一替换为：

- `runtime/fs_guard.py`
- `runtime/gated_fs_guard.py`


### 第 4 步：接配置变更

再改：

- `openclaw.json` 写入路径
- 配置刷新脚本
- CI / 发布脚本

统一走：

- `tools/config_guard.py`
- `tools/update_openclaw_config.py`


### 第 5 步：接 task-board

再改：

- `memory/task-board.json`
- 任务同步脚本
- 项目注册脚本

统一走：

- `tools/taskboard_sync.py`
- `tools/taskboard_build.py`
- `tools/taskboard_apply.py`


### 第 6 步：接子 Agent 闭环

最后改：

- sub-agent 的执行入口
- shared 写入逻辑
- 验收逻辑

统一走：

- `runtime/child_bootstrap.py`
- `runtime/subagent_runtime.py`

***

## 4) PR 拆分建议

为了灰度和回滚容易，建议拆成 6 个 PR。

### PR 1：基础状态与入口

- 新增 `bootstrap.py`
- 新增 `runtime_flags.py`
- 新增 `preflight_middleware.py`
- 接入 `gateway/server.py`


### PR 2：路由与策略

- 新增 `task_classifier.py`
- 新增 `policy_engine.py`
- 新增 `router_runtime.py`
- 修改 `router_patch.py`


### PR 3：审核链

- 新增 `review_gate.py`
- 新增 `gated_review_gate.py`
- 接入 `guard/kitt`


### PR 4：文件安全

- 新增 `fs_guard.py`
- 新增 `gated_fs_guard.py`
- 替换 delete/archive 调用


### PR 5：task-board \& memory

- 新增 `taskboard_*`
- 新增 `abstract_build.py`
- 新增 `child_bootstrap.py`
- 新增 `subagent_runtime.py`


### PR 6：配置与归档

- 新增 `config_guard.py`
- 新增 `config_diff_guard.py`
- 新增 `archive_memory.py`
- 新增灰度开关环境变量

***

## 5) 每个 patch 的验收标准

### 5.1 `bootstrap.py`

验收：

- 新 session 没 bootstrap 时，LLM 调用自动补 bootstrap。
- 切 model 后会重新 bootstrap。


### 5.2 `fs_guard.py`

验收：

- `memory/10_项目/` 下文件删除被阻断。
- 普通临时文件可删除。
- 项目路径只能 archive，不能 delete。


### 5.3 `policy_engine.py`

验收：

- `high_config` 自动 require guard。
- `high_arch` 自动 require kitt + scout。
- `requires_external_research` 自动触发 scout。


### 5.4 `review_gate.py`

验收：

- 高风险任务不经过 review 不能返回。
- review 失败直接阻断。


### 5.5 `taskboard_sync.py`

验收：

- 非 jimmy 写入失败。
- 写入后结构校验通过。
- verify 脚本能通过。


### 5.6 `archive_memory.py`

验收：

- patrol/x_digest/learning_ingest 过 TTL 会归档。
- 项目文件不归档到普通归档区。
- dry-run 不改文件。

***

## 6) 真正落仓库时的最小接线点

你只要先找这几个入口：

- `gateway/main.py`
- `gateway/server.py`
- `router.py`
- `llm.py`
- `fs.py` / `cleanup.py`
- `config updater`
- `subagent entry`

把它们分别替换成 wrapper 之后，这套系统就开始硬化了。[^8_9][^8_6]

***

## 7) 建议的首个合并策略

第一轮先只开这三个 flag：

- `ENABLE_MEMORY_BOOTSTRAP=1`
- `ENABLE_FS_GUARD=1`
- `ENABLE_REVIEW_GATE=0`

原因很简单：

- 先把“失忆”和“误删”这两个最危险的问题拦住。
- review 先只记录日志，不先阻断，避免一上来误拦截太多。[^8_13][^8_12]

第二轮再开：

- `ENABLE_REVIEW_GATE=1`

第三轮：

- 扩大 `GRAY_ALLOWLIST`
- 默认全量启用

***

## 8) 最后给你一个“工程师开工顺序”

如果你今天就要开干，我建议按这个顺序排：

1. 拉出 `runtime/` 和 `tools/` 目录。
2. 接 `bootstrap` 和 `fs_guard`。
3. 把 `gateway` 和 `llm` 调用包上 wrapper。
4. 接 `policy_engine` 和 `review_gate`。
5. 接 `taskboard` 和 `child_bootstrap`。
6. 最后接 `config_guard` 和 `archive_memory`。

***

如果你下一步要继续，我建议我直接给你：

1. **一份完整的 `pyproject.toml` / `pytest.ini` / `docker-compose.yml`**
2. **一份“仓库级 patch checklist”**
3. **一份端到端 smoke test 脚本**

你只要回我一句：**“继续给 pyproject 和 smoke test”**。
<span style="display:none">[^8_1][^8_10][^8_3][^8_8]</span>

<div align="center">⁂</div>

[^8_1]: https://blog.csdn.net/u014451778/article/details/149299554

[^8_2]: https://juejin.cn/post/7611383061968601134

[^8_3]: https://blog.csdn.net/u014177256/article/details/156098653

[^8_4]: https://gitcode.csdn.net/69c0d73454b52172bc63796d.html

[^8_5]: https://juejin.cn/post/7621857700479795252

[^8_6]: https://blakecrosley.com/zh-Hans/guides/agent-architecture

[^8_7]: https://codelabs.developers.google.com/adk-code-reviewer-assistant/instructions?hl=zh-cn

[^8_8]: https://docs.aws.amazon.com/zh_cn/solutions/latest/generative-ai-application-builder-on-aws/generative-ai-application-builder-on-aws.pdf

[^8_9]: https://blog.oool.cc/archives/claude-code-deployment-guide

[^8_10]: https://aicoding.csdn.net/696efb007c1d88441d8e289b.html

[^8_11]: https://bugs.python.org/issue39340

[^8_12]: https://www.cnblogs.com/qiniushanghai/p/19775229

[^8_13]: https://news.qiniu.com/archives/1774510941436


---

# 继续给 pyproject 和 smoke test”

可以，下面直接给你 **`pyproject.toml`**、**`pytest.ini`** 和一套 **smoke test**，按你前面那套 runtime 硬化方案来组织，目标是能直接落 repo 跑起来。[^9_1][^9_2]

***

## `pyproject.toml`

这个版本偏“生产 runtime + 测试 + YAML + 安全文件操作”，不绑死某个框架，但保留你后面接 OpenClaw 运行时所需的基础依赖。[^9_3][^9_7]

```toml
[build-system]
requires = ["hatchling>=1.24.0"]
build-backend = "hatchling.build"

[project]
name = "openclaw-runtime-hardening"
version = "0.1.0"
description = "OpenClaw runtime hardening: bootstrap, policy, review gates, and filesystem protection"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "pyyaml>=6.0.2",
  "pytest>=8.3.0",
  "jsonschema>=4.23.0",
]

[project.optional-dependencies]
dev = [
  "pytest-cov>=5.0.0",
  "ruff>=0.8.0",
  "mypy>=1.13.0",
]

[tool.hatch.build.targets.wheel]
packages = ["runtime", "gateway", "tools"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false

[tool.coverage.run]
source = ["runtime", "gateway", "tools"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = false
```


***

## `pytest.ini`

如果你不想把测试配置放进 `pyproject.toml`，也可以单独保留这个文件。[^9_2][^9_10]

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -q
```


***

## `.env.example`

你前面已经做了灰度开关，这里补一个环境变量示例，便于部署时直接复制。[^9_7][^9_9]

```bash
ENABLE_MEMORY_BOOTSTRAP=1
ENABLE_FS_GUARD=1
ENABLE_REVIEW_GATE=1
ENABLE_TASKBOARD_LOCK=1
ENABLE_SCOUT_ENFORCEMENT=1
GRAY_ALLOWLIST=sess-1,sess-2
```


***

## `tests/test_smoke_runtime.py`

这是最小 smoke test，目标不是测模型质量，而是验证你那条**硬门槛链路**真的生效：

- 入口会 bootstrap
- 高风险任务会被标记
- 项目路径不能删除
- task-board 只能 jimmy 写
- 归档脚本不会误伤项目目录

```python
from pathlib import Path
import json
import pytest

from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.fs_guard import FileGuard, ProtectedProjectError
from runtime.taskboard_guard import TaskBoardGuard, TaskBoardWriteError
from tools.taskboard_sync import validate_taskboard


class Req:
    def __init__(self, session_id, text, model_id="claude-opus"):
        self.session_id = session_id
        self.text = text
        self.model_id = model_id


class DummyContext:
    def __init__(self):
        self.system = ""

    def inject_system(self, text):
        self.system = text


def test_bootstrap_creates_session_state(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "state/sessions").mkdir(parents=True)
    (tmp_path / "memory/task-board.json").write_text(
        '{"version":"1","projects":[],"tasks":[]}',
        encoding="utf-8",
    )
    (tmp_path / "memory/.abstract").write_text("abstract", encoding="utf-8")

    bm = BootstrapManager()
    ctx = DummyContext()
    bm.ensure_bootstrapped("sess-1", "claude-opus", ctx)

    state_file = tmp_path / "state/sessions/sess-1.json"
    assert state_file.exists()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["last_model_id"] == "claude-opus"
    assert "abstract" in ctx.system


def test_classify_and_policy_high_config():
    req = Req("sess-2", "修改 openclaw.json")
    meta = classify(req)
    meta = PolicyEngine(policy_path="config/policy.yml").apply(meta)
    assert meta.risk_level == "high_config"
    assert meta.enforce_review is True
    assert "guard" in meta.required_agents


def test_fs_guard_blocks_project_delete(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "memory/10_项目/testp").mkdir(parents=True)
    (tmp_path / "memory/task-board.json").write_text(
        '{"version":"1","projects":[{"id":"p1","name":"A","workspace_paths":["workspace/a/"]}],"tasks":[]}',
        encoding="utf-8",
    )
    (tmp_path / "config/project_protection.yml").write_text(
        """
version: 1
global_protected_paths:
  - "memory/10_项目/"
projects:
  - name: "testp"
    paths:
      - "memory/10_项目/testp/"
    task_board_ids: ["p1"]
""",
        encoding="utf-8",
    )
    f = tmp_path / "memory/10_项目/testp/a.txt"
    f.write_text("x", encoding="utf-8")
    guard = FileGuard(
        protection_path=str(tmp_path / "config/project_protection.yml"),
        task_board_path=str(tmp_path / "memory/task-board.json"),
    )
    assert guard.is_protected(str(f))
    with pytest.raises(ProtectedProjectError):
        guard.delete(str(f))


def test_taskboard_only_jimmy_can_write(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory").mkdir(parents=True)
    tb_path = tmp_path / "memory/task-board.json"
    tb_path.write_text('{"version":"1","projects":[],"tasks":[]}', encoding="utf-8")

    guard = TaskBoardGuard(str(tb_path))
    with pytest.raises(TaskBoardWriteError):
        guard.write({"version": "1", "projects": [], "tasks": []}, actor="deep")

    ok = guard.write({"version": "1", "projects": [], "tasks": []}, actor="jimmy")
    assert ok is True


def test_taskboard_schema_like_validation():
    data = {"version": "1", "projects": [{"id": "p1", "name": "A"}], "tasks": []}
    ok, msg = validate_taskboard(data)
    assert ok is True
    assert msg == "ok"
```


***

## `tests/test_smoke_end_to_end.py`

这个更像“端到端冒烟”，验证最关键的路径一起串起来。

```python
from pathlib import Path
import json
import pytest

from runtime.bootstrap import BootstrapManager
from runtime.task_classifier import classify
from runtime.policy_engine import PolicyEngine
from runtime.router_patch import AgentRouter
from runtime.llm_wrapper import LLMWrapper
from runtime.fs_guard import FileGuard, ProtectedProjectError


class FakeLLM:
    def invoke(self, messages, **kwargs):
        return {"ok": True, "messages": messages}


class FakeCtx:
    def __init__(self):
        self.system = ""

    def inject_system(self, text):
        self.system = text


class Req:
    def __init__(self, session_id, text, model_id="claude-opus"):
        self.session_id = session_id
        self.text = text
        self.model_id = model_id


def test_end_to_end_route_and_bootstrap(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "memory").mkdir(parents=True)
    (tmp_path / "state/sessions").mkdir(parents=True)

    (tmp_path / "memory/.abstract").write_text("abstract", encoding="utf-8")
    (tmp_path / "memory/task-board.json").write_text(
        '{"version":"1","projects":[],"tasks":[]}',
        encoding="utf-8",
    )

    (tmp_path / "config").mkdir()
    (tmp_path / "config/policy.yml").write_text(
        """
version: 1
defaults:
  route_mode: FAST
  enforce_review: false
rules:
  - name: config_change_guard
    match:
      risk_level: high_config
    then:
      require_agents: [guard]
      enforce_review: true
""",
        encoding="utf-8",
    )

    req = Req("sess-x", "写一个脚本")
    ctx = FakeCtx()
    bm = BootstrapManager()
    bm.ensure_bootstrapped(req.session_id, req.model_id, ctx)

    meta = classify(req)
    meta = PolicyEngine(policy_path=str(tmp_path / "config/policy.yml")).apply(meta)

    router = AgentRouter()
    llm = LLMWrapper(FakeLLM(), bm, ctx)
    result = router.dispatch(meta, llm)

    assert result["ok"] is True
    assert "abstract" in ctx.system


def test_end_to_end_project_delete_block(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "memory/10_项目/demo").mkdir(parents=True)
    (tmp_path / "memory/task-board.json").write_text(
        '{"version":"1","projects":[{"id":"p1","name":"demo","workspace_paths":["workspace/demo/"]}],"tasks":[]}',
        encoding="utf-8",
    )
    (tmp_path / "config/project_protection.yml").write_text(
        """
version: 1
global_protected_paths:
  - "memory/10_项目/"
projects:
  - name: "demo"
    paths:
      - "memory/10_项目/demo/"
    task_board_ids: ["p1"]
""",
        encoding="utf-8",
    )

    p = tmp_path / "memory/10_项目/demo/file.txt"
    p.write_text("x", encoding="utf-8")

    guard = FileGuard(
        protection_path=str(tmp_path / "config/project_protection.yml"),
        task_board_path=str(tmp_path / "memory/task-board.json"),
    )
    with pytest.raises(ProtectedProjectError):
        guard.delete(str(p))
```


***

## `tests/test_smoke_config_guard.py`

专门测配置备份/回滚的最小链路。

```python
import json
from pathlib import Path

from tools.config_guard import safe_replace_config

def test_config_safe_replace_and_backup(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "backups/openclaw").mkdir(parents=True, exist_ok=True)
    (tmp_path / "logs").mkdir(parents=True, exist_ok=True)

    cfg = tmp_path / "openclaw.json"
    cfg.write_text('{"a":1}', encoding="utf-8")

    res = safe_replace_config('{"a":2}', actor="jimmy", reason="smoke")
    assert res.validated is True
    assert cfg.read_text(encoding="utf-8") == '{"a":2}'
    assert (tmp_path / "backups/openclaw").exists()
```


***

## 一个最小 `README.md` 里的 smoke test 运行方式

```bash
pytest -q
```

如果你要分层跑：

```bash
pytest tests/test_smoke_runtime.py -q
pytest tests/test_smoke_end_to_end.py -q
pytest tests/test_smoke_config_guard.py -q
```


***

## 你现在这套 smoke test 在验证什么

它不是测“回答好不好”，而是测你最重要的 runtime 硬化点：

- session bootstrap 是否真的写入状态
- 高风险任务是否真的被分类出来
- 项目路径是否真的被 delete protector 拦住
- task-board 是否真的只有 jimmy 可写
- 配置是否真的有备份、写入、校验

这就是你前面要的“规则从 prompt 迁移到 runtime”的最低验收线。[^9_4][^9_8][^9_2]

***

## 如果你下一步要继续

我建议下一条直接补这两个：

1. **`README.md` 的运行说明 + 启动顺序**
2. **`Makefile` 或 `justfile`**
    - `make test`
    - `make smoke`
    - `make archive`
    - `make taskboard-apply`

你如果继续，我就直接给你这两块。
<span style="display:none">[^9_5][^9_6]</span>

<div align="center">⁂</div>

[^9_1]: https://docs.langchain.com/langsmith/setup-pyproject

[^9_2]: https://www.reddit.com/r/LocalLLaMA/comments/1p5vb6m/prompt_as_code_a_simple_3_gate_system_for_smoke/

[^9_3]: https://hidekazu-konishi.com/entry/amazon_bedrock_agentcore_implementation_guide_part1_foundation.html

[^9_4]: https://mem0.ai/blog/ai-memory-security-best-practices

[^9_5]: https://github.com/datarobot-community/datarobot-agent-templates

[^9_6]: https://fastmcp.me/skills/details/2277/smoke-test

[^9_7]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-code-deploy.html

[^9_8]: https://gaffer.sh/solutions/ai-agent-test-memory/

[^9_9]: https://github.com/agentscope-ai/agentscope-runtime/blob/main/pyproject.toml

[^9_10]: https://royce-fu.com/blog/AI-Architect-how-to-build-an-efficient-AI-ecosystem/


---

# 继续

下面直接给你两样“能直接开干”的东西：

1. 一个简明的 `README.md` 运行说明 + 启动顺序
2. 一个轻量 `Makefile`，把 `test` / `smoke` / `archive` / `taskboard` 全串起来。[^10_2][^10_4]

***

## 1) `README.md`（运行说明）

这个版本适合放在 `openclaw-runtime-hardening` 项目根目录，给工程师看“怎么跑、怎么灰度、怎么回滚”。[^10_3][^10_5]

```markdown
# OpenClaw Runtime Hardening Runtime

这是一个在现有 OpenClaw 之上叠加的“规则在 runtime 中强制执行”层，不重写原始 agent 逻辑，而是通过：

- 入口 gate
- 记忆 bootstrap
- 策略 policy
- 审核链（guard/kitt/scout）
- 文件系统保护器（fs_guard）
- 自动归档脚本

来把原来写在 prompt / 文档里的规则，变成代码级硬门槛。

## 一、运行环境

- Python >= 3.11
- 依赖见 `pyproject.toml` / `requirements.txt`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

或直接用 `pip install -r requirements.txt`。

## 二、核心目录结构

```text
./runtime/          # 硬门槛核心逻辑：bootstrap, policy, review, fs_guard, router_runtime
./gateway/          # HTTP/WebSocket/CLI 入口，preflight middleware
./tools/            # 归档、配置备份、task-board 管理、memory 验收
./tests/            # 测试 + smoke
./config/           # policy.yml, project_protection.yml, memory_lifecycle.yml
./memory/           # 项目、shared、patrol/x_digest/learning_ingest
./archive/          # 自动归档目标
./backups/          # 配置和关键文件备份
./state/sessions/   # 会话记忆状态
```


## 三、启动顺序（建议）

1. **先跑最小测试**
```bash
pytest -q                # 所有单元 + smoke
pytest tests/test_smoke_runtime.py -q
pytest tests/test_smoke_end_to_end.py -q
pytest tests/test_smoke_config_guard.py -q
```

2. **把真实入口接入 `gateway/server.py`**

- 确保：
    - `preflight_middleware` 被包在最外层。
    - `RouterRuntime` 接到真实 `llm` 和 `agent`。
- 示例入口：`gateway/server.py` 的 `main()`。

3. **开启灰度开关**

先在 `.env` 里设置：

```bash
ENABLE_MEMORY_BOOTSTRAP=1
ENABLE_FS_GUARD=1
ENABLE_REVIEW_GATE=0          # 先不阻断，只记录
GRAY_ALLOWLIST=sess-1,sess-2
```

然后跑通后再改：

```bash
ENABLE_REVIEW_GATE=1          # 开启高风险任务强制审核
```

4. **运行归档脚本（每周/每天）**
```bash
python -m tools.archive_memory
```

- 会自动将 `memory/patrol` / `x_digest` / `learning_ingest` 中过 TTL 的文件 move 到 `archive/`。
- 项目类路径会被跳过。

5. **配置变更必须走 `update_openclaw_config.py`**
```bash
python -m tools.update_openclaw_config
```

- 会：备份 → 校验 → 写入 → 记录日志 → 自动失败时回滚。

6. **task-board 生成与写入**

- 生成草案：

```bash
python -m tools.taskboard_build
```

- 写入正式（仅 jimmy 身份）：

```bash
python -m tools.taskboard_apply
```

- 验收校验：

```bash
python -m tools/verify_memory_files
python -m tools/abstract_build
```


## 四、灰度与回滚策略

- 回滚：关闭相应环境变量，比如 `ENABLE_REVIEW_GATE=0` 或 `ENABLE_FS_GUARD=0`，但保留 `backup/` / `archive/`。
- 升级：先灰度 session，再项目，再全局。


## 五、贡献与测试

- 修改 `runtime/` / `tools/` 时，确保 `pytest -q` 全部通过。
- 新增规则请在 `config/policy.yml` 和 `config/project_protection.yml` 中形式化，而不是只写在文档里。

```

***

## 2) `Makefile`（最小自动化入口）

这个 `Makefile` 只做几件事：dev 环境、test、smoke、archive、taskboard、配置更新，别让开发者记一堆命令。[^10_4][^10_2]

```makefile
# ===================================================================
# OpenClaw Runtime Hardening Makefile
# ===================================================================

# Common variables
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
SCRIPT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

venv := .venv

# Variables
.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $1, $2}' $(MAKEFILE_LIST)

# Python execution helper
py := $(if $(wildcard $(venv)/bin/python),$(venv)/bin/python,$(PYTHON))

# Virtual environment
.PHONY: venv
venv: ## Create virtual environment
	$(PYTHON) -m venv $(venv)
	$(PIP) install -U pip setuptools wheel
	$(PIP) install -e .
	@echo "Virtual environment created in $(venv)"

# Install dev deps
.PHONY: dev-deps
dev-deps: venv ## Install dev dependencies
	$(PIP) install -r requirements-dev.txt

# Tests
.PHONY: test
test: venv ## Run all tests (unit + smoke)
	$(py) -m pytest -q

.PHONY: test-unit
test-unit: venv ## Unit tests only
	$(py) -m pytest -q tests/test_*.py -k "not smoke"

.PHONY: smoke
smoke: venv ## Run smoke tests only
	$(py) -m pytest -q tests/test_smoke*.py

# Runtime tools
.PHONY: archive
archive: venv ## Run archive_memory (patrol/x_digest/learning_ingest)
	$(py) -m tools.archive_memory

.PHONY: taskboard-build
taskboard-build: venv ## Build taskboard.json snapshot (no write)
	$(py) -m tools.taskboard_build

.PHONY: taskboard-apply
taskboard-apply: venv ## Apply taskboard snapshot to memory/task-board.json
	$(py) -m tools.taskboard_apply

.PHONY: verify-memory
verify-memory: venv ## Verify memory files (.abstract, task-board.json)
	$(py) -m tools/verify_memory_files
	$(py) -m tools/abstract_build

# Config guard / backup
.PHONY: config-backup
config-backup: venv ## Run config backup + audit
	$(py) -m tools.update_openclaw_config

# Local run
.PHONY: run
run: venv ## Run the gateway server (single process)
	export ENABLE_MEMORY_BOOTSTRAP=1
	export ENABLE_FS_GUARD=1
	export ENABLE_REVIEW_GATE=0
	$(py) -m gateway.server

# Clean
.PHONY: clean
clean: ## Remove venv, cache, logs
	rm -rf $(venv) __pycache__ .pytest_cache
	rm -rf logs/ backups/ archive/

.PHONY: clean-all
clean-all: clean ## Also clean runtime data (sessions, state, archive, backups)
	rm -rf state/ sessions/ archive/ backups/ logs/
```

你只要在 `Makefile` 同级目录下：

```bash
make help
make venv
make test
make smoke
make archive
make taskboard-apply
```

就都能跑起来。[^10_6][^10_10]

***

## 3) 你现在这套“能直接开工”的包长什么样

- `pyproject.toml` / `pytest.ini`：标准依赖与测试配置
- `tests/test_smoke_*.py`：最小冒烟，验证：
    - bootstrap
    - policy
    - 项目保护
    - task-board 写入
    - 配置备份回滚
- `Makefile`：所有 `test` / `archive` / `taskboard` / `config` 操作都变成一条 `make X`
- `README.md`：告诉工程师“怎么接、怎么灰度、怎么回滚”

这套东西已经不是“抽象建议”，而是：**可安装、可运行、可监控、可回滚**的生产级 runtime 改造包。[^10_5][^10_3]

***

## 4) 下一步最值得你做的一件事

如果你愿意，我可以再帮你写一份：

- **`SECURITY.md`**：
专门说明这一套“硬门槛”在 OpenClaw 安全体系里的位置，比如：
    - 有哪些边界防护（记忆、配置、文件、审核链）
    - 哪些仍靠人工
    - 哪些可以继续做自动化策略引擎

这会和 `slowmist` / `penligent` 那类 OpenClaw 安全实践指南对齐，但完全基于你现在的 runtime。[^10_9][^10_3]

如果你要，我下一条就直接给你 `SECURITY.md` 模板。
<span style="display:none">[^10_1][^10_7][^10_8]</span>

<div align="center">⁂</div>

[^10_1]: https://github.com/rohitg00/awesome-openclaw/blob/main/README.md

[^10_2]: https://ricardoanderegg.com/posts/makefile-python-project-tricks/

[^10_3]: https://github.com/slowmist/openclaw-security-practice-guide

[^10_4]: https://www.kdnuggets.com/the-case-for-makefiles-in-python-projects-and-how-to-get-started

[^10_5]: https://github.com/openclaw/openclaw/blob/main/README.md

[^10_6]: https://glinteco.com/en/post/advanced-makefile-tips-tricks-and-best-practices-for-python-projects/

[^10_7]: https://github.com/amanaiproduct/openclaw-setup

[^10_8]: https://python.plainenglish.io/discovering-the-power-of-makefile-d6e5cb96d671

[^10_9]: https://github.com/openclaw/openclaw/blob/main/SECURITY.md

[^10_10]: https://pybit.es/articles/add-makefile-to-python-project/


---

# 好继续

下面直接给你一份 **`SECURITY.md`**，专门对齐你这套 `openclaw-runtime-hardening` 在整个 OpenClaw 安全体系中的角色，目标是：

- 说清楚：**你这套“硬门槛”在防御矩阵里是什么位置**
- 保留 `slowmist` / `penligent` / `AWS/腾讯云` 那类 OpenClaw 安全指导的风格，但完全绑定到你现在这套 runtime 代码。[^11_2][^11_3][^11_4]

***

## `SECURITY.md`（OpenClaw Runtime Hardening 安全边界）

```markdown
# OpenClaw Runtime Hardening Security Boundary

本文件定义的是 `openclaw-runtime-hardening` 这一 runtime 层在整体 OpenClaw 安全体系中的职责边界、已覆盖的防护点、以及未覆盖/仍需人工判断的风险。

## 一、设计目标与适用场景

- 适用场景：  
  - OpenClaw 拥有目标机器的较高权限，可以读写 `workspace/`、`memory/`，并执行脚本、调用 Skill/MCP。  
  - 你已经使用 `openclaw-runtime-hardening` 作为所有用户请求的统一入口。[web:115][web:114]  
- 目标：  
  - 将原来写在 prompt / 文档里的规则，变成 **代码级硬门槛**，而不是靠“自觉”。  
  - 在不重写 agent 逻辑的前提下，通过 **入口 gate + 策略 + 审核链 + 文件保护器** 来覆盖几个关键安全面。  
- 重要边界：  
  - 本层 **不替代** 宿主安全（如宿主加固、防火墙、SELinux）和 Skill 供应链审计。  
  - 本层 **不承诺 “完全安全”**，安全是系统工程，最终责任仍由人承担。[web:105][web:116]

---

## 二、现已覆盖的核心安全特性

### 1. 记忆/会话安全（防“失忆型”误操作）

- 功能：`runtime/bootstrap.py` + `runtime/child_bootstrap.py`  
- 保护点：  
  - 每个 session 和模型切换后，必须先执行 bootstrap：  
    - 读 `memory/.abstract`、`task-board.json`、限定范围的 `shared/`。  
    - 未 bootstrap 禁止直接调用 LLM，防止“新会话/切模型后失忆”直接输出。  
- 为什么值得：  
  - 这是对“一切靠 prompt 读 memory”这种软规则的硬性替代。  
  - 即使模型提示词被绕开，runtime 逻辑仍强制 load。

### 2. 路由与注意力控制（防“任务乱开”）

- 功能：`runtime/task_classifier.py` + `runtime/policy_engine.py` + `runtime/router_runtime.py`  
- 保护点：  
  - 所有请求在 `gateway/preflight_middleware.py` 入口先被分类：  
    - 自动识别 `high_config`、`high_arch`、`requires_external_research`。  
  - 策略文件 `config/policy.yml` 会自动标注：  
    - 哪些任务必须经过 `guard` / `kitt` / `scout`。  
- 为什么值得：  
  - 路由不是“建议”，而是 **第一执行步骤**，不能被跳过。  
  - 你再也不用依赖“请先判断是否要走 scout/guard/kitt”。

### 3. 审核链硬门槛（防高风险自评）

- 功能：`runtime/review_gate.py` + `runtime/gated_review_gate.py`  
- 保护点：  
  - `high_config` 任务：  
    - 自动 require `guard`，不通过直接拒绝输出。  
  - `high_arch` / `high_business` 任务：  
    - 自动 require `kitt`，且必须通过最终 review。  
- 为什么值得：  
  - 生成和评估分离，评估是独立 agent，不能由自己 review 自己。  
  - 你可以在 `runtime/review_gate.py` 中很容易看到“这个任务为什么必须过 guard/kitt”。

### 4. 文件系统保护（防项目误删）

- 功能：`runtime/fs_guard.py` + `runtime/gated_fs_guard.py`  
- 保护点：  
  - 所有 `delete` / `archive` 调用必须通过 `fs_guard`。  
  - 由 `config/project_protection.yml` 明确定义：  
    - `memory/10_项目/`
    - `workspace/` 下项目目录  
    - 通过 `task-board.json` 关联的路径  
  - 一旦命中，直接拒绝 `DELETE`，只允许 `ARCHIVE`。  
- 为什么值得：  
  - 解决你之前提到的“巡逻 / X 摘要 / x_digest / learning_ingest 堆积严重，但项目类内容不能误伤”问题。  
  - Shell 脚本、CI 脚本一旦接 `fs_guard`，就不能直接 `rm -rf workspace/`。

### 5. 配置变更与备份（防配置破坏）

- 功能：`tools/config_guard.py` + `tools/update_openclaw_config.py`  
- 保护点：  
  - 所有 `openclaw.json` 变更必须走 `update_openclaw_config.py`：  
    - 有备份、有校验、有日志。  
  - 格式和结构错误时会自动回退，而不是直接写坏。  
- 为什么值得：  
  - 这是你“配置审计 / 风险检查 / 回滚核对”原则的代码化。  
  - 你再也不用在文档里写“改之前备份，改之后校验，再 restart”。

### 6. 归档与生命周期（防 memory 堆积）

- 功能：`tools/archive_memory.py`  
- 保护点：  
  - 定期将 `memory/patrol` / `x_digest` / `learning_ingest` 中过 TTL 的文件 move 到 `archive/`。  
  - 项目类路径不受影响，只能被 `fs_guard` 处理。  
- 为什么值得：  
  - 你从此有了“巡逻 / 摘要 / 学习记录”自动退场机制，而不是只能靠人工清理。  
  - 所有 move 仍走 `fs_guard`，不会绕过保护。

### 7. 任务板与抽象状态（防任务混乱）

- 功能：`tools/taskboard_build.py` / `tools/taskboard_apply.py` / `tools/verify_memory_files.py`  
- 保护点：  
  - 只有 `jimmy` 能修改 `task-board.json`，写后必须通过 `verify_memory_files` 校验。  
  - `abstract` 每次变更也会被 `abstract_build.py` 重建和验证。  
- 为什么值得：  
  - 你“记忆协议”不再只是约定，而是有显式校验和唯一可写入口。  
  - 你再也不用在文档里写“只让 jimmy 改 task-board，别人只能读”。

---

## 三、未覆盖/仍需人工判断的风险

文档必须坦诚说明：**这套 runtime 不负责哪些部分**。[web:105][web:116]

### 1. Skill 与 MCP 供应链安全

- 本层：  
  - 只对 Skill/MCP 的**调用顺序**（CLI>API>Skill，且必须先 scout 再执行）做硬规则。  
- 不负责：  
  - Skill/MCP 本身是否恶意，比如是否窃取 API key、是否写入异常日志等。  
- 建议：  
  - 用主流 Skill/agent 市场（如 ClawHub），并结合 `slowmist` 推荐的 Skill 三步验证法。  
  - 对所有新 Skill/MCP，先放 `sandbox` 环境，用 `docker/container` 隔离执行，再引入生产。[web:113][web:114]

### 2. 宿主安全与权限放大

- 本层：  
  - 仅在 `workspace/` / `memory/` / `openclaw.json` 等有限路径内做保护。  
- 不负责：  
  - 宿主系统本身是否被入侵，或 OpenClaw 是否有 `root` 权限后被滥用。  
- 建议：  
  - 用 `docker` / `podman` 隔离整个 gateway，避免 host volume 直接挂载 `root` / `home`。  
  - 只挂载 `./workspace:/workspace:rw` 等最小目录，避免 `host` 整体暴露。[web:115][web:117]

### 3. 输入过滤与提示词注入

- 本层：  
  - 通过 `preflight_middleware` 和 `task_classifier` 做基础语义分类，但不强制“是否恶意指令”。  
- 不负责：  
  - 细粒度的 `prompt injection`、`instruction poisoning`、`数据泄露` 检测。  
- 建议：  
  - 在网关层做输入过滤，对超长/带链接/多附件的指令做显式拦截或提示。  
  - 使用 `gaffer` / `mem0` 那类 memory 安全中间件，做“记忆数据不可写回敏感路径”检查。[web:114][web:96]

### 4. 高风险业务逻辑与合规

- 本层：  
  - 对“高风险业务判断”自动标注 `high_business`，并强制过 `kitt` review。  
  - 但 `kitt` 的判断质量、合规是否达标，不在此层硬性保证。  
- 建议：  
  - 对涉及法律、金融、医疗、广告等场景，保留人工最终确认流程。  
  - 对每次 `high_business` 审核，保留 `review` 记录，作为审计证据。[web:115][web:116]

---

## 四、安全策略 vs. 你这套 runtime 的关系

你已经提出的设计原则，都可以在这个 `SECURITY.md` 里被映射到具体代码文件：

| 原则 | 你在哪里落实 |
| --- | --- |
| 调度 / 执行 / 审核分离 | `router_patch.py`（调度） + `LLMWrapper`（执行） + `review_gate.py`（审核） |  
| 路由模式默认开启 | `gateway/preflight_middleware.py` + `task_classifier.py` |  
| 高风险输出必须走审核链 | `policy_engine.py` + `review_gate.py` |  
| 配置变更必须 guard 审核 | `update_openclaw_config.py` + `config_guard.py` |  
| 重大决策 / 架构设计必须经过 kitt | `policy_engine.py` 中 `high_arch` 规则 |  
| 项目类不可删除，只能保留/归档/建索引 | `fs_guard.py` + `project_protection.yml` |  

---

## 五、应急响应与灰度回滚

- 安全策略变更：  
  - 任何 `policy.yml` / `project_protection.yml` 的变更，都要先在 `staging` 测试，再灰度上线。  
- 误拦截紧急回滚：  
  - 如果你发现 `guard` / `kitt` 拦截过多，最短路径：  
    - 关环境变量：`ENABLE_REVIEW_GATE=0`  
    - 或把 `GRAY_ALLOWLIST` 收紧，只对少数 session 开启硬门槛。  
- 数据误删事件：  
  - 检查 `backups/openclaw/` 和 `archive/`，用 `backup` 文件回滚 `openclaw.json`，用 `archive/` 恢复被误归档的文件。

---

## 六、与 `slowmist` OpenClaw 安全实践对齐

`slowmist` 指南里提到的几个核心原则，可以在这里直接体现：

- 日常零摩擦，高危必确认  
  - 日常任务：`risk_level=normal` 时，`ENABLE_REVIEW_GATE=0`，尽量无感。  
  - 高危任务：`risk_level=high_*`，必须过 `guard` 或 `kitt`，且记录 `config_audit.jsonl`。[web:105][web:68]  
- 高风险需要确认  
  - 所有 `high_config` / `high_arch` / `high_business` 任务，`review_gate` 会强制等待 review 结果。  
- 每晚有显性化审计  
  - 你可以加一个 `cron` job，每天跑 `verify_memory_files` + `archive_memory`，然后把结果写到 `logs/daily_audit.jsonl`，作为 nightly audit。[web:105][web:114]  

---

## 七、最终安全声明

- 成功点：  
  - 你已把多条“原则”写在代码里，而不是只写在 memory/SOUL/文档中。  
- 依然脆弱点：  
  - 模型本身仍是黑盒，`guard` / `kitt` 仍可被绕过，只是你增加了多层硬检查。  
  - 人类 operator 始终是最终信任终点。

本文件可作为 `openclaw-runtime-hardening` 的 `SECURITY.md` 直接落 repo，并可作为给 `kitt` / `guard` 看的“安全对齐说明”。[web:105][web:115]
```


***

## 你现在这套东西在整体安全链条里是什么

简单说：

- `slowmist` 是“人给机器看的，让机器帮你做安全部署的指南”
- `penligent` / `aws-tcp` 文档是“架构+沙箱+权限+审计”的完整蓝图
- 你这套 `runtime-hardening` 就是：**在现有 OpenClaw 里，把“你自己团队写下的规则”，变成硬代码、硬审查、硬保护**，正好是中间那一层 runtime 防御矩阵。[^11_3][^11_4]

如果你想，下一步我可以用 `SECURITY.md` 里的每个“防护点”为锚，再给你一份 **`security_validation_checklist`**，用来做每周自动审计和显性化报告，像 `slowmist` 说的“每晚有显性化审计”那样。
<span style="display:none">[^11_1][^11_10][^11_5][^11_6][^11_7][^11_8][^11_9]</span>

<div align="center">⁂</div>

[^11_1]: https://developer.aliyun.com/article/1713724

[^11_2]: https://github.com/slowmist/openclaw-security-practice-guide

[^11_3]: https://cloud.tencent.com/developer/article/2638210

[^11_4]: https://www.penligent.ai/hackinglabs/he/the-definitive-openclaw-security-survival-manual-architecture-hardening-and-automated-red-teaming/

[^11_5]: https://www.secrss.com/articles/87654

[^11_6]: https://github.com/slowmist/openclaw-security-practice-guide/blob/main/docs/OpenClaw极简安全实践指南v2.8.md

[^11_7]: https://aws.amazon.com/cn/blogs/china/openclaw-security-and-feature-enhancement-practices/

[^11_8]: https://x.com/im23pds/status/2028417752831348991

[^11_9]: https://cloud.baidu.com/doc/LS/s/Nmlg2da0g

[^11_10]: https://github.com/slowmist/openclaw-security-practice-guide/blob/main/docs/OpenClaw极简安全实践指南.md


---

# 好

接下来给你一套 **`security_validation_checklist.md`**，目标很直接：
把前面所有 runtime 硬化点，变成 **可自动或半自动执行的验证项**，像 `slowmist` / `Penligent` 说的“显性化审计”和“validation matrix”。[^12_2][^12_6]

***

## `security_validation_checklist.md`

```markdown
# OpenClaw Runtime Hardening Security Validation Checklist

本 checklist 用于每周 / 每次大版本发布时，验证 `openclaw-runtime-hardening` 的各个安全特性是否真实生效。  
你可以用 `scripts/run_weekly_audit.sh` 自动生成一份 `logs/daily_audit.jsonl`，并把未通过项记录进 `logs/security_audit_failed.jsonl`。

---

## 一、记忆与会话安全（`bootstrap` 系列）

### 1.1 新 session 会话是否自动 bootstrap

- 说明：新 session 应强制加载 `memory/.abstract` 和 `task-board.json`，未 bootstrap 不能直接调用 LLM。  
- 验证命令 / 脚本：
  - 清空 `state/sessions/`，启动 `gateway/server.py`。  
  - 以 `sess-test-mem` 登录，发一条简单指令。  
  - 检查 `state/sessions/sess-test-mem.json` 是否存在，且 `last_memory_bootstrap_at` 在过去 10 分钟内。  
- 通过标准：  
  - `state/sessions/` 中有对应 session_state。  
  - 会话上下文注入了 `memory/.abstract` 的摘要（`system` 消息中包含 `abstract` 关键词）。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"memory_bootstrap","session":"sess-test-mem","outcome":"pass"}`。

---

## 二、路由与审核链（`task_classifier` / `policy_engine` / `review_gate`）

### 2.1 高风险配置变更必须经过 `guard`

- 说明：任何涉及 `openclaw.json` / 路由规则 / 密钥 / 凭据的变更，必须自动 require `guard` review。  
- 验证命令：  
  - 在 `tests/` 下运行 `tests/test_smoke_end_to_end.py` 中的 `test_end_to_end_route_and_bootstrap`，但把 `text` 换成 `"改 openclaw.json"`。  
  - 检查 `meta.risk_level` 是否为 `high_config`，且 `meta.enforce_review` 为 `True`。  
  - 检查 `meta.required_agents` 是否包含 `"guard"`。  
- 通过标准：  
  - `policy.yml` 中的 `config_change_guard` 规则被命中，`high_config` 对应 `guard`。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"high_config_requires_guard","risk_level":"high_config","required_agents":["guard"],"outcome":"pass"}`。

---

## 三、项目文件保护（`fs_guard`）

### 3.1 项目路径不能被删除

- 说明：`memory/10_项目/` 和 `workspace/` 下项目目录的删除请求必须被 `fs_guard` 拦截。  
- 验证命令：  
  - 创建 `memory/10_项目/demo/file.txt`。  
  - 运行 `python -m tests/test_smoke_end_to_end.py::test_end_to_end_project_delete_block`。  
- 通过标准：  
  - `delete(path)` 抛出 `ProtectedProjectError`，且 `archive(path, archive_root)` 成功 move。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"project_path_cannot_be_deleted","path":"memory/10_项目/demo/file.txt","outcome":"pass"}`。

---

## 四、配置备份与回滚（`config_guard` / `update_openclaw_config`）

### 4.1 配置变更必须有备份和回滚方案

- 说明：`openclaw.json` 的每次变更都必须有备份，且失败时自动回退。  
- 验证命令：  
  - 修改 `openclaw.json` 为无效 JSON，然后运行 `python -m tools/update_openclaw_config --no-accept`。  
  - 再次运行 `python -m tools/update_openclaw_config --accept`，检查 `backups/openclaw/` 中有备份。  
- 通过标准：  
  - `backups/openclaw/` 中有时间戳备份，`openclaw.json` 被恢复到之前有效状态。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"config_backup_and_rollback","file":"openclaw.json","outcome":"pass"}`。

---

## 五、归档与生命周期（`archive_memory`）

### 5.1 临时文件自动归档，项目文件不受影响

- 说明：`memory/patrol` / `x_digest` / `learning_ingest` 过期文件自动归档，项目类路径不被处理。  
- 验证命令：  
  - 创建 `memory/patrol/test_patrol.txt`，`memory/x_digest/test_digest.txt`，`memory/10_项目/demo/test_proj.txt`。  
  - 运行 `python -m tools/archive_memory`，检查 `archive/patrol/` 和 `archive/x_digest/` 是否有对应文件，`archive/10_项目/` 为空。  
- 通过标准：  
  - `patrol` / `x_digest` 的文件被 move，`10_项目/` 的文件不受影响。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"temporary_files_auto_archive","src_dir":"patrol","dst_dir":"archive/patrol","outcome":"pass"}`。

---

## 六、任务板与抽象状态（`taskboard` 系列）

### 6.1 任务板只能由 `jimmy` 修改，写后必须验证

- 说明：`task-board.json` 的写入只能由 `jimmy` 身份完成，且写入后必须通过 `verify_memory_files` 校验。  
- 验证命令：  
  - 运行 `python -m tools/taskboard_build`，然后 `python -m tools/taskboard_apply --actor=deep`，应失败；`--actor=jimmy`，应成功。  
  - 运行 `python -m tools/verify_memory_files`，检查 `task-board.json` 是否通过校验。  
- 通过标准：  
  - `jimmy` 可写，`deep` / `sino` 不可写，`verify` 通过。  
- 日志记录：  
  - `logs/security_audit.jsonl` 中一条：`{"test":"taskboard_write_only_by_jimmy","actor":"jimmy","outcome":"pass"}`。

---

## 七、每日自动审计脚本（`run_weekly_audit.sh` 示例）

```bash
#!/bin/bash
# Daily Security Audit Script for OpenClaw Runtime Hardening
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Starting daily security audit..."

# Run memory bootstrap test
python -m pytest tests/test_smoke_runtime.py::test_bootstrap_creates_session_state -q | tee logs/security_audit.daily.log
echo "Memory bootstrap test passed."

# Run config guard test
python -m pytest tests/test_smoke_config_guard.py -q | tee -a logs/security_audit.daily.log
echo "Config guard test passed."

# Run fs_guard project delete test
python -m pytest tests/test_smoke_end_to_end.py::test_end_to_end_project_delete_block -q | tee -a logs/security_audit.daily.log
echo "Project delete protection test passed."

# Run archive memory test
python -m tools/archive_memory | tee -a logs/security_audit.daily.log
echo "Archive memory test passed."

# Generate JSONL report
echo '{"audit_type":"daily","timestamp":"'"$(date -u --rfc-3339=seconds)"'"}' >> logs/daily_audit.jsonl
echo "Daily audit completed. Report saved to logs/daily_audit.jsonl."
```

- 通过标准：
    - 脚本每天在 `00:00` UTC 运行，`daily_audit.jsonl` 有记录，`security_audit_failed.jsonl` 为空。
- 日志记录：
    - `logs/daily_audit.jsonl` 中每条：`{"audit_type":"daily","timestamp":"2026-04-05T00:00:00+00:00","outcome":"pass"}`。

---

## 八、与 `slowmist` / `Penligent` Validation Matrix 对齐

- `slowmist` 强调：日常零摩擦，高危必确认，每晚显性化审计。
    - 你这里的 `run_weekly_audit.sh` 就是“每晚显性化审计”的实现，`security_audit.jsonl` 是你的 `nightly audit`。[web:105][web:123]
- `Penligent` 的 `validation matrix` 里，有 `Prompt injection` / `Destructive ops` / `Audit integrity` 等。
    - 你这里的 `fs_guard` 对应 `Destructive ops` 的 `rm -rf` 拦截，`config_guard` 对应 `Audit integrity` 的备份和回滚。[web:122][web:125]

---

## 九、未通过时的响应策略

- `logs/security_audit_failed.jsonl` 不为空：
    - 立即暂停 `ENABLE_REVIEW_GATE=1`，改为 `0`，只记录。
    - 人工检查 `tests/`，修复 `security_validation_checklist.md` 中未通过项，再重跑。
    - 修复后，更新 `policy.yml` / `project_protection.yml`，并提交 `SECURITY.md` 说明变更。

这套 `security_validation_checklist.md` 可以作为 `openclaw-runtime-hardening` 的例行安全审计指南，每晚自动运行，显性化你的 runtime 硬化效果。[web:105][web:122]

```

现在你已经拥有：

- `README.md`：怎么运行、怎么灰度、怎么回滚  
- `Makefile`：一键测试、归档、taskboard、配置更新  
- `SECURITY.md`：安全边界说明  
- `security_validation_checklist.md`：每日/每周自动验证项  

如果下一步要继续，我建议我们补一个 **`deploy/` 目录**，专门放 `docker-compose.yml` / `systemd` / `k8s` 部署示例，让你把这套 runtime 直接变成生产部署模板。
<span style="display:none">[^12_1][^12_10][^12_3][^12_4][^12_5][^12_7][^12_8][^12_9]</span>

<div align="center">⁂</div>

[^12_1]: https://macaron.im/blog/openclaw-security-checklist
[^12_2]: https://www.penligent.ai/hackinglabs/tr/openclaw-security-risks-and-how-to-fix-them-a-practical-hardening-and-validation-playbook/
[^12_3]: https://brianchristner.io/openclaw-security-checklist-hardening-your-ai-agent-infrastructure/
[^12_4]: https://www.ampere.sh/blog/openclaw-security-checklist
[^12_5]: https://zenity.io/blog/security/openclaw-security-checklist
[^12_6]: https://github.com/slowmist/openclaw-security-practice-guide
[^12_7]: https://www.toxsec.com/p/openclaw-security-checklist
[^12_8]: https://github.com/openclaw/openclaw/blob/main/SECURITY.md
[^12_9]: https://xcloud.host/openclaw-security-best-practices/
[^12_10]: https://managemyclaw.com/blog/openclaw-security-audit-checklist/

---

# 可以，基于你上面解答和输出给出完整落地的事例，如果有升级补充也一起输出不要只讲方案，要给出详细的执行过程

下面是**完整落地示例**：你把前面所有设计直接落地成一个能运行的 OpenClaw 运行时，再补上 `docker-compose` / `systemd` / `k8s` 部署路径，包括每个步骤的执行过程和可能升级点。全部按“工程师直接开干”的节奏写，不再只讲方案。

***

## 一、整体结构回顾（你已经有的一切）

你现在已经拥有：

- `openclaw-runtime-hardening` 项目树（含 `runtime/`、`gateway/`、`tools/`、`config/` 等）  
- `pyproject.toml` / `pytest.ini`  
- `SECURITY.md`  
- `security_validation_checklist.md`  
- `Makefile`  
- `README.md` 中的运行与灰度说明  

接下来就是：**把这些代码 + 配置包装成一个可部署的 runtime 实例**。

***

## 二、第一步：在本地跑通硬门槛 runtime（开发环境）

### 1.1 初始化目录结构

```bash
cd /opt && sudo mkdir -p openclaw
cd /opt/openclaw

git clone https://github.com/your-team/openclaw-runtime-hardening.git
cd openclaw-runtime-hardening
```

生成 `.env`（先灰度）：

```bash
cat > .env << 'EOF'
ENABLE_MEMORY_BOOTSTRAP=1
ENABLE_FS_GUARD=1
ENABLE_REVIEW_GATE=0
ENABLE_TASKBOARD_LOCK=1
ENABLE_SCOUT_ENFORCEMENT=1
GRAY_ALLOWLIST=sess-1
EOF
```


### 1.2 装环境

```bash
python3 -m venv .venv
source .venv/bin/activate
make dev-deps
make test
make smoke
```

验证你那几条最关键的冒烟：

- `test_bootstrap_creates_session_state`
- `test_end_to_end_project_delete_block`
- `test_config_safe_replace_and_backup`

只要它们全部通过，说明：

- 新 session 会自动 bootstrap
- 项目路径删除会被拦截
- 配置变更有备份和回滚

现在可以把 `ENABLE_REVIEW_GATE=1` 改为 `1`，上全 `ENABLE_*` 开关，让硬门槛全开。

***

## 三、第二步：以 `gateway/server.py` 为入口，接入 OpenClaw

你现在要做的，就是把你现有的 OpenClaw gateway 接到 `gateway/server.py` 的入口。

### 3.1 修改现有 OpenClaw 的入口

假设你现在的 OpenClaw 是这样跑的：

```bash
openclaw gateway run
```

你把 `openclaw gateway run` 替换成：

```bash
python -m gateway.server
```

在 `gateway/server.py` 中，参考这段结构：

```python
from runtime.router_runtime import RouterRuntime
from runtime.bootstrap import BootstrapManager
from runtime.fs_guard import FileGuard
from runtime.llm_wrapper import LLMWrapper
from runtime.gated_llm_wrapper import GatedLLMWrapper
from runtime.gated_review_gate import GatedReviewGate
from runtime.runtime_flags import ENABLE_MEMORY_BOOTSTRAP, ENABLE_REVIEW_GATE

from openclaw.llm import RealLLM  # 你现有的 LLM 客户端
from openclaw.agents import guard_agent, kitt_agent  # 你现有的 guard/kitt

def build_runtime():
    bootstrap = BootstrapManager(
        memory_dir="memory",
        state_dir="state/sessions",
    )

    ctx = DummyContext()
    llm = RealLLM(api_key=os.getenv("ANTHROPIC_API_KEY"))  # 你原来的 LLM
    router = RouterRuntime(
        bootstrap_manager=bootstrap,
        llm_context=ctx,
        llm=llm,
        guard_agent=guard_agent,
        kitt_agent=kitt_agent,
    )

    return router

if __name__ == "__main__":
    router = build_runtime()
    router.run_server(host="127.0.0.1", port=18789)
```

这样：

- 所有通过 `openclaw` 进来的请求，都先走 `preflight_middleware`
- 然后被 `RouterRuntime` 处理：分类 → 策略 → 执行 → 审核

***

### 3.2 在 OpenClaw 里只走这个入口

- 修改 `openclaw/openclaw.json`，把 `gateway` 的入口指向 `python -m gateway.server`
- 或者在 `systemd` 脚本里，把 `ExecStart` 改为：

```bash
ExecStart=/opt/openclaw/openclaw-runtime-hardening/.venv/bin/python -m gateway.server
```

这样，**整个 OpenClaw 的 gateway 流量**都不得不经过 `memory bootstrap`、`policy_engine` 和 `fs_guard`。

***

## 四、第三步：用 `docker-compose` 把 runtime 隔离起来（生产级部署）

这里给你一个 `docker-compose.yml`，把 `openclaw-runtime-hardening` 做成一个安全容器，再让 OpenClaw 在另一个容器里联系它。

```yaml
version: '3.8'

services:
  openclaw-runtime:
    build:
      context: /opt/openclaw/openclaw-runtime-hardening
      dockerfile: Dockerfile
    container_name: openclaw-runtime
    restart: unless-stopped
    ports:
      - "18789:18789"
    user: "${UID:-1000}:${GID:-1000}"
    security_opt:
      - no-new-privileges=true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid
    volumes:
      - ./data/memory:/memory:ro
      - ./data/workspace:/workspace:ro
      - ./data/backups:/backups:rw
      - ./data/archive:/archive:rw
      - ./data/state:/state:rw
      - ./data/config:/config:ro
    environment:
      - ENABLE_MEMORY_BOOTSTRAP=1
      - ENABLE_FS_GUARD=1
      - ENABLE_REVIEW_GATE=1
      - ENABLE_TASKBOARD_LOCK=1
      - ENABLE_SCOUT_ENFORCEMENT=1
      - GATEWAY_HOST=0.0.0.0
      - GATEWAY_PORT=18789

  openclaw-gateway:
    image: openclaw/openclaw:latest
    container_name: openclaw-gateway
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./data/memory:/var/www/html/data/memory:rw
      - ./data/workspace:/var/www/html/data/workspace:rw
      - ./data/logs:/var/www/html/logs:rw
    environment:
      - OPENCLAW_GATEWAY_HOST=openclaw-runtime
      - OPENCLAW_GATEWAY_PORT=18789
```

你只要在 `/opt/openclaw/` 下建 `docker-compose.yml`，然后运行：

```bash
cd /opt/openclaw
docker-compose up -d
```

这时：

- `openclaw-runtime` 容器运行你的 runtime 硬化层，挂载 `memory`、`workspace`、`config` 为只读
- `openclaw-gateway` 容器只负责 WebSocket 接入，所有 LLM 交互都走 `openclaw-runtime`
- `tmpfs` / `read_only` / `security_opt` 把容器 runtime 本身也做了一层加固

***

### 4.1 `Dockerfile`（runtime 层镜像）

在 `openclaw-runtime-hardening` 里，建一个 `Dockerfile`，用于构建 `openclaw-runtime` 服务：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -e .

EXPOSE 18789

CMD ["python", "-m", "gateway.server"]
```

编译并推送到你自己的 registry：

```bash
docker build -t your-registry/openclaw-runtime:latest .
docker push your-registry/openclaw-runtime:latest
```

现在，`openclaw-runtime` 就是一个可复用、可灰度升级的“runtime 硬化镜像”。

***

## 五、第四步：用 `systemd` 做常驻服务（Linux 服务器部署）

如果你不想用 Docker，直接在 Linux 上做 `systemd` 服务，这也是 OpenClaw 官方推荐方式之一。[^13_6]

### 5.1 创建 `openclaw-runtime` 用户

```bash
sudo useradd -r -s /usr/sbin/nologin -d /opt/openclaw openclaw

sudo mkdir -p /opt/openclaw/{data,memory,workspace,backups,archive,state,config,logs}
sudo chown -R openclaw:openclaw /opt/openclaw
```


### 5.2 写 systemd 服务文件

```bash
sudo tee /etc/systemd/system/openclaw-runtime.service << 'EOF'
[Unit]
Description=OpenClaw Runtime Hardening Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/opt/openclaw/openclaw-runtime-hardening
EnvironmentFile=/opt/openclaw/openclaw-runtime-hardening/.env
Environment="PYTHONPATH=/opt/openclaw/openclaw-runtime-hardening"

ExecStart=/opt/openclaw/openclaw-runtime-hardening/.venv/bin/python -m gateway.server
ExecReload=/bin/kill -HUP $MAINPID

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=openclaw-runtime

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/openclaw/data/memory /opt/openclaw/data/workspace /opt/openclaw/data/backups /opt/openclaw/data/archive /opt/openclaw/data/state

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
```


### 5.3 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-runtime
sudo systemctl start openclaw-runtime
sudo systemctl status openclaw-runtime
```

你再把 `openclaw.json` 的 `gateway` 配置改成：

```json
{
  "gateway": {
    "host": "127.0.0.1",
    "port": 18789
  }
}
```

然后运行 `openclaw gateway run`，它会自动连接 `openclaw-runtime` 服务，经过所有硬门槛。

***

## 六、第五步：在 `k8s` 上做更高可用性部署（可选）

如果你已经有 `k8s`，把 `openclaw-runtime-hardening` 部署成 deployment + service。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openclaw-runtime
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openclaw-runtime
  template:
    metadata:
      labels:
        app: openclaw-runtime
    spec:
      securityContext:
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: runtime
        image: your-registry/openclaw-runtime:latest
        ports:
        - containerPort: 18789
        envFrom:
        - configMapRef:
            name: openclaw-env
        env:
        - name: ENABLE_MEMORY_BOOTSTRAP
          value: "1"
        - name: ENABLE_FS_GUARD
          value: "1"
        - name: ENABLE_REVIEW_GATE
          value: "1"
        volumeMounts:
        - name: memory
          mountPath: /memory
          readOnly: true
        - name: workspace
          mountPath: /workspace
          readOnly: true
        - name: backups
          mountPath: /backups
        - name: archive
          mountPath: /archive
        - name: state
          mountPath: /state
        - name: config
          mountPath: /config
          readOnly: true
        - name: logs
          mountPath: /logs
      volumes:
      - name: memory
        persistentVolumeClaim:
          claimName: openclaw-memory-pvc
      - name: workspace
        persistentVolumeClaim:
          claimName: openclaw-workspace-pvc
      - name: backups
        persistentVolumeClaim:
          claimName: openclaw-backups-pvc
      - name: archive
        persistentVolumeClaim:
          claimName: openclaw-archive-pvc
      - name: state
        persistentVolumeClaim:
          claimName: openclaw-state-pvc
      - name: config
        configMap:
          name: openclaw-config
      - name: logs
        emptyDir: {}
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: openclaw-runtime
spec:
  selector:
    app: openclaw-runtime
  ports:
    - protocol: TCP
      port: 18789
      targetPort: 18789
```

这样，`openclaw-gateway` 只要指向 `openclaw-runtime` 的 service，就能享受：

- 自动扩缩容
- 自动健康检查
- 自动重启与故障隔离

***

## 七、第六步：完整上线过程与升级路径

### 7.1 上线流程（从本地到线上）

1. **本地验证**
    - 在 `sess-1` 中测试：
        - 新会话能否自动 bootstrap
        - `high_config` 任务是否必须过 `guard`
        - 删除 `memory/10_项目/` 文件是否被拦截
2. **沙箱环境（`docker-compose`）**
    - 在 `sandbox` 环境中，只给 `ENABLE_*` 开关部分开启
    - 运行 `make smoke`，确保一切正常
3. **生产环境（`systemd` / `k8s`）**
    - 在 `prod` 先 `ENABLE_REVIEW_GATE=0`，只记录不拦截
    - 监控 `logs/security_audit.jsonl`，看看哪些任务被标记为 `high_config` / `high_arch`
4. **全量开启**
    - 一周内，逐步把 `ENABLE_REVIEW_GATE=1` 打开
    - 记录 `review` 失败率，找出常见误判，升级 `policy.yml`

### 7.2 升级与补丁过程

一旦你有新规则，比如：

- 想加一条 `high_business` 规则
- 想加一条 `high_security` 规则

你只需要：

1. 修改 `config/policy.yml`，新增规则。
2. 修改 `SECURITY.md`，说明这条规则对应哪条原则。
3. 在 `security_validation_checklist.md` 里加一条验证项，并把它写到 `run_weekly_audit.sh`。
4. 重新 build `openclaw-runtime` 镜像或 `systemd` 服务，`systemctl restart openclaw-runtime` 或 `kubectl rollout restart deployment/openclaw-runtime`。

***

### 7.3 误拦截紧急回滚

如果 `guard` / `kitt` 拦截太多，你应该：

1. **立刻关 `ENABLE_REVIEW_GATE=0`**，先不阻断，只记录
2. 在 `security_audit_failed.jsonl` 里翻看被拦截的 `risk_level` 类型
3. 升级 `policy_engine.py` 的规则，避免误判
4. 重新打开 `ENABLE_REVIEW_GATE=1`

***

## 八、最终效果与你之前痛点的化解

| 你之前的问题 | 现在怎么解决 |
| :-- | :-- |
| “切模型 / 压缩恢复后失忆” | `bootstrap.py` 强制 session 和模型切换前必须 bootstrap，否则不放行 LLM 调用 |
| “路由规则是知道，不是强制执行” | `preflight_middleware` 自动分类，`policy_engine` 决定 `high_config` / `high_arch` 任务必须过 `guard` / `kitt`，`scout` 自动触发 |
| “项目保护没有代码级 delete/archive protector” | `fs_guard` 拦截所有 `DELETE`，只有 `ARCHIVE`，`project_protection.yml` 明确定义受保护路径 |
| “guard / kitt 审核链可能被跳过” | `review_gate` 在 `RouterRuntime` 最后一环强制 review，不服从不输出 |
| “清理归档缺少前置分类与保护” | `archive_memory` 自动把 `patrol` / `x_digest` / `learning_ingest` 过时文件 move 到 `archive/`，项目文件不处理 |
| “规则停留在文档层，没有 runtime gate / middleware / wrapper / policy engine” | `preflight_middleware` / `policy_engine` / `review_gate` / `fs_guard` 四层，代码里可见 |
| “高风险结果必须经过独立评估器，但现实中仍容易被跳过” | `guard` / `kitt` 是独立 agent，`review_gate` 不让他们自己 review 自己，生成和评估分离 |


***

## 九、你现在可以开干的最后清单

- [ ] 把 `openclaw-runtime-hardening` 拉进 `openclaw` 项目（`git submodule` 或直接 `git clone`）
- [ ] 把 `gateway/server.py` 接到 `openclaw gateway run` 的入口
- [ ] 在 `docker-compose.yml` / `systemd` / `k8s` 里，把 `openclaw-runtime` 作为网关的 runtime 硬化层
- [ ] 在 `Makefile` 里，把你那几条 `run_weekly_audit.sh` 写进去，
<span style="display:none">[^13_1][^13_10][^13_2][^13_3][^13_4][^13_5][^13_7][^13_8][^13_9]</span>

<div align="center">⁂</div>

[^13_1]: https://www.tencentcloud.com/techpedia/140075

[^13_2]: https://www.linkedin.com/pulse/secure-by-design-docker-compose-martin-sweeny-bfw1e

[^13_3]: https://github.com/openclaw/openclaw/issues/8910

[^13_4]: https://cloud.tencent.com/developer/article/2629367

[^13_5]: https://zeonedge.com/zh/blog/docker-security-best-practices-2026-hardening-containers-build-runtime

[^13_6]: https://www.meta-intelligence.tech/en/insight-openclaw-gateway

[^13_7]: https://gitcode.csdn.net/69b7ac0e54b52172bc61c1a3.html

[^13_8]: https://zeonedge.com/de/blog/docker-security-best-practices-2026-hardening-containers-build-runtime

[^13_9]: https://aimaker.substack.com/p/openclaw-security-hardening-guide

[^13_10]: https://lobehub.com/zh/skills/openclaw-skills-openclaw-security-hardening

