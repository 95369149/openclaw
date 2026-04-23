# Agent 分配与职责规划 v1.0

**制定时间**: 2026-02-23 17:37  
**制定人**: Kitt (xjrouter/claude-opus-4-6-max)  
**审核人**: 厂长

---

## 核心理念

**单入口，智能路由**：

- 厂长只和 jimmy 对话
- jimmy 根据任务类型自动派发给最合适的 agent
- 各 agent 完成后结果汇总给 jimmy，由 jimmy 统一回复厂长

---

## Agent 编制（5员）

### 1. jimmy（总调度 + 日常管家）

**模型**: mynewapi/claude-sonnet-4-6  
**角色**: 默认 agent，总调度中枢  
**职责**:

- 接收所有厂长的请求
- 判断任务类型并路由到合适的 agent
- 汇总各 agent 的结果
- 日常对话、简单问答
- 记忆管理（读写 memory/）
- 工具编排（exec/read/write）

**擅长**:

- 快速响应（sonnet 速度快）
- 成本控制（比 opus 便宜）
- 通用任务处理

**调用方式**: 默认（厂长直接对话）

---

### 2. main（多模态专家）

**模型**: google-gemini-cli/gemini-3-pro-preview  
**角色**: 多模态内容生成与分析  
**职责**:

- 图片生成（Imagen）
- 视频生成（Veo）
- 图片/视频分析
- 长文档分析（1M context）
- 多语言翻译

**擅长**:

- 视觉内容处理
- 超长上下文（1M tokens）
- 多模态理解

**调用方式**: `sessions_spawn(agentId="main", task="...")`

**触发场景**:

- 需要生成图片/视频
- 需要分析图片/视频内容
- 需要处理超长文档（>100KB）

---

### 3. logic（推理引擎）

**模型**: siliconflow/deepseek-ai/DeepSeek-R1  
**角色**: 复杂推理与数学计算  
**职责**:

- 复杂逻辑推理
- 数学问题求解
- 算法设计与优化
- 代码调试（深度分析）
- 科学计算

**擅长**:

- 思维链推理（CoT）
- 数学/物理/化学问题
- 算法复杂度分析

**调用方式**: `sessions_spawn(agentId="logic", task="...")`

**触发场景**:

- 数学计算/证明
- 复杂算法设计
- 需要深度推理的问题
- 代码性能优化

---

### 4. deep（中文代码专家）

**模型**: siliconflow/deepseek-ai/DeepSeek-V3.2  
**角色**: 中文内容 + 代码生成  
**职责**:

- 中文内容生成（文章/报告/文案）
- 中文内容润色
- 代码编写（Python/JS/TS/Go）
- 代码重构
- 技术文档编写

**擅长**:

- 中文语境理解
- 代码生成速度快
- 性价比高（免费 API）

**调用方式**: `sessions_spawn(agentId="deep", task="...")`

**触发场景**:

- 中文内容创作
- 代码编写/重构
- 技术文档生成
- 中文润色

---

### 5. kitt（架构师 + 决策顾问）

**模型**: xjrouter/claude-opus-4-6-max  
**角色**: 系统架构设计 + 关键决策  
**职责**:

- 系统架构设计
- 技术方案评审
- 关键决策分析
- 复杂问题拆解
- 战略规划

**擅长**:

- 深度思考（opus 级别推理）
- 架构设计
- 风险评估
- 长期规划

**调用方式**: `sessions_spawn(agentId="kitt", task="...")`

**触发场景**:

- 系统架构设计
- 重大技术决策
- 复杂问题需要深度分析
- 战略规划

---

## 路由规则（jimmy 决策树）

### 1. 内容生成类

- **图片/视频** → main
- **中文文章/文案** → deep
- **技术文档** → deep
- **简单文本** → jimmy 自己处理

### 2. 分析类

- **图片/视频分析** → main
- **代码分析/调试** → logic
- **架构分析** → kitt
- **简单分析** → jimmy 自己处理

### 3. 推理类

- **数学/算法** → logic
- **复杂推理** → logic
- **战略决策** → kitt
- **简单推理** → jimmy 自己处理

### 4. 代码类

- **代码编写** → deep
- **代码优化** → logic
- **架构设计** → kitt
- **简单脚本** → jimmy 自己处理

### 5. 特殊场景

- **超长文档（>100KB）** → main
- **多模态任务** → main
- **关键决策** → kitt
- **成本敏感任务** → deep（免费）

---

## 协作模式

### 模式 1: 单 agent 完成

```
厂长 → jimmy → 判断 → agent X → 完成 → jimmy → 厂长
```

### 模式 2: 多 agent 协作

```
厂长 → jimmy → 拆解任务
              ├→ agent A（子任务1）
              ├→ agent B（子任务2）
              └→ agent C（子任务3）
              → jimmy 汇总 → 厂长
```

### 模式 3: 递归调用

```
厂长 → jimmy → agent X → 遇到难题 → agent Y → 完成 → agent X → jimmy → 厂长
```

---

## 成本控制

### 免费优先

1. deep（SiliconFlow，11 Key 轮动）
2. main（Gemini CLI，OAuth 免费）
3. logic（SiliconFlow，11 Key 轮动）

### 付费谨慎

4. jimmy（mynewapi，付费但便宜）
5. kitt（xjrouter，免费但需代理，仅关键任务）

### 原则

- 简单任务 jimmy 自己处理，不派发
- 能用免费的不用付费的
- kitt 只用于关键决策，不日常调用

---

## 配置实施

### 当前配置

```json
agents.list = [
  { id: "jimmy", default: true, model: "mynewapi/claude-sonnet-4-6" },
  { id: "main", model: "google-gemini-cli/gemini-3-pro-preview" },
  { id: "logic", model: "siliconflow/deepseek-ai/DeepSeek-R1" },
  { id: "deep", model: "siliconflow/deepseek-ai/DeepSeek-V3.2" },
  { id: "kitt", model: "xjrouter/claude-opus-4-6-max" }
]
```

### 下一步

1. 重启 Gateway 使配置生效
2. 测试各 agent 的调用
3. 优化路由规则
4. 监控成本和性能

---

## 测试计划

### 测试 1: 单 agent 调用

- jimmy 自己处理简单问答 ✅
- 派 main 生成图片
- 派 logic 解数学题
- 派 deep 写代码
- 派 kitt 做架构设计

### 测试 2: 多 agent 协作

- 复杂项目拆解给多个 agent
- 验证结果汇总流程

### 测试 3: 成本监控

- 记录各 agent 的调用次数
- 统计 token 消耗
- 优化成本结构

---

## 迭代方向

### 短期（本周）

- 完成配置和测试
- 建立路由规则库
- 监控各 agent 表现

### 中期（本月）

- 优化路由决策
- 增加自动质检
- 建立 agent 协作模板

### 长期（本季度）

- 引入更多专业 agent（如 writer/researcher）
- 建立 agent 性能评估体系
- 自动化路由优化

---

**状态**: 待实施  
**下一步**: 重启 Gateway，开始测试
