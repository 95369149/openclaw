# Agent 路由与调用规则 v1.0（2026-02-24 补充完善）

## 1. 渠道路由（硬规则）
- **Telegram** → jimmy（主入口）
- **Discord** (#kitt-team) → kitt（团队协作）
- **WhatsApp** → main（gemini CLI）
- **其他未配置渠道** → jimmy（默认）

## 2. Agent 职责与调用场景

### 2.1 jimmy（mynewapi/claude-sonnet-4-6）
**职责**: 总调度，前台接待，记忆管理，配置变更
**调用触发**:
1. 任何渠道的首次输入
2. 简单任务（查memory/单文件操作/单轮对话）
3. 配置变更请求
4. 需要多agent协调的任务（先接收再派发）

### 2.2 kitt（xjrouter/claude-opus-4-6-max 或 fallback）
**职责**: 复杂架构设计，多轮规划，外部模型协调
**调用触发**:
1. 复杂任务（步骤≥5，涉及子系统交互）
2. 架构设计/方案输出（文档/PPT/流程图）
3. 多agent协调失败需要仲裁
4. 厂长明确要求"深度思考/架构分析"

### 2.3 main（gemini-3-pro-preview → claude-opus-4-6 降级）
**职责**: 视频脚本，营销文案，创意生成
**调用触发**:
1. TikTok/YouTube 视频脚本
2. 营销文案/朋友圈内容
3. 创意生成（图片构思/文案风格）
4. WhatsApp 专属需求

### 2.4 logic（v1api/deepseek-r1）
**职责**: 深度推理，代码分析，多步计算
**调用触发**:
1. 复杂代码问题
2. 数学计算/逻辑推理
3. 系统故障分析
4. 多变量决策树

### 2.5 deep（siliconflow/deepseek-v3.2）
**职责**: 代码生成，技术实现，系统搭建
**调用触发**:
1. 需要完整代码输出
2. 技术栈研究（新框架/库）
3. 系统搭建方案
4. API对接实现

## 3. 路由判断流程

### 3.1 输入 → jimmy（必须）
1. jimmy接收所有输入
2. **第一层判断**（jimmy执行）:
   - 查询memory/search/知识库（已有答案）→ 直接回答
   - 简单操作（单文件/单命令）→ 直接执行
   - 查配置/状态 → 直接回复
   - 日常对话 → 直接回复

3. **第二层判断**（是否需要派发）:
   - Yes → jimmy继续处理
   - No → jimmy处理完成后派发最合适agent

### 3.2 派发规则（优先级）
1. **渠道限定**: WhatsApp→main | Discord→kitt
2. **任务匹配**（按顺序）:
   a. 视频/营销 → main  
   b. 代码/技术 → deep  
   c. 推理/计算 → logic  
   d. 架构/规划 → kitt
3. **降级策略**:
   - deep(v3.2)超时→logic(r1)
   - logic失败→kitt(opus)
   - kitt失败→main(gemini)
   - 全部失败→jimmy降级回答并标记

## 4. 调用语法

### 4.1 jimmy使用：
```bash
# 派发深度推理
sessions_spawn({
  \"agentId\": \"logic\",
  \"task\": \"分析这个代码的复杂度...\",
  \"model\": \"deepseek-r1\"
})

# 派发架构设计
sessions_spawn({
  \"agentId\": \"kitt\",  
  \"task\": \"设计这个系统架构...\",
  \"model\": \"max\"
})

# 派发代码生成
sessions_spawn({
  \"agentId\": \"deep\",
  \"task\": \"生成Node.js API代码...\",
  \"model\": \"siliconflow/deepseek-v3.2\"
})
```

### 4.2 回传机制：
被派发agent完成后：
1. 结果写回session（jsonl）
2. jimmy汇总→格式化→回复厂长
3. 异常标记（超时/错误）
4. 自动降级重试

## 5. 应急处理

### 5.1 降级预案：
- deepseek-v3.2失败→deepseek-r1→kitt→main→jimmy
- 任一环节失败自动向上一级

### 5.2 超时控制：
- 简单任务：30秒
- 复杂任务：90秒
- 超时自动中断并提示

---

**实施文件**：
- `memory/01_强制规则/agent_routing.md`（本文件）
- `memory/01_强制规则/排兵布阵.md`（引用此规则）
- `memory/scripts/agent_dispatcher_v4.py`（待实现）