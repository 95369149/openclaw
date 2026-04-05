# agency-agents 定向吸收清单（2026-03-23）

## 结论
不整仓安装 `msitarzewski/agency-agents`，只定向吸收当前最需要的 6 个角色，作为 Kitt 系统升级素材。

仓库：`https://github.com/msitarzewski/agency-agents`
星标：`60246`
定位：角色型 agent 提示词库，不是记忆引擎，不是 orchestrator。

## 第一批吸收对象（已审计）

### 1. `engineering/engineering-code-reviewer.md`
- 用途：补 `Reality Checker / verifier`
- 吸收点：
  - `🔴 blocker / 🟡 suggestion / 💭 nit` 三层审查
  - 一次性给完整反馈，避免滴灌式评论
  - 以正确性、安全性、可维护性、性能、测试为主轴
- 在我们系统中的落点：
  - 复杂代码 / 架构 / 规则文档交付后，必须经审查者复核

### 2. `project-management/project-management-project-shepherd.md`
- 用途：补任务闭环和跨 agent 协调
- 吸收点：
  - 明确里程碑、阻塞项、依赖关系、升级路径
  - 状态汇报模板清晰，适合改造成三态回复骨架
- 在我们系统中的落点：
  - 主调度者负责进度、阻塞、验收，而不是只派发不收口

### 3. `engineering/engineering-frontend-developer.md`
- 用途：补前端执行角色
- 吸收点：
  - 强调性能、可访问性、组件化与测试
  - 对前端实现交付边界比较清楚
- 在我们系统中的落点：
  - 后续抖音工作流前端 / 拓客系统前端恢复或重建时可直接吸收

### 4. `marketing/marketing-douyin-strategist.md`
- 用途：补抖音内容策略角色
- 吸收点：
  - `前3秒钩子`、`完播率优先`、`内容矩阵`、`直播节奏`
  - 非常适合红太阳短视频矩阵
- 在我们系统中的落点：
  - `T-119` / `T-121` / `T-130` / `T-143`

### 5. `sales/sales-outbound-strategist.md`
- 用途：补拓客系统销售策略角色
- 吸收点：
  - 信号驱动外呼，不靠群发
  - ICP 分层、触发式外联、多触点节奏
- 在我们系统中的落点：
  - `T-116` 外贸线索实时响应系统

### 6. `engineering/engineering-software-architect.md`
- 用途：补架构审查角色
- 吸收点：
  - ADR 思维
  - 明说 trade-off，不搞架构空话
  - 先域模型，后技术
- 在我们系统中的落点：
  - 任何系统级改造（记忆、多 agent、守护层、上下文层）先做 trade-off 审查

## 不建议直接整仓安装的原因
1. 角色过多，容易把现有路由搞乱
2. 它解决的是“分工层”，不是“底层能力层”
3. 当前最急的是把：
   - 记忆自动归纳
   - verifier
   - fallback 自动切换
   - 三态回复
   - 项目目录白名单保护
   工程化，而不是导入上百个角色文件

## 下一步（执行顺序）
1. 把 `Code Reviewer` + `Software Architect` 合并成我们自己的 `Reality Checker` 规则
2. 把 `Project Shepherd` 吸收到主调度回复模板
3. 把 `Douyin Strategist` / `Outbound Strategist` 作为业务角色模板接入任务路由
4. 后续再视情况吸收更多角色，不做整仓迁移
