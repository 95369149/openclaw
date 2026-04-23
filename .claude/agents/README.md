# Kitt Agent 编制

## jimmy（主调度）
- model: mynewapi/claude-sonnet-4-6
- 职责: 主对话、任务路由、验收子agent输出
- tool限制: 全部工具可用
- 禁止: 修改 openclaw.json（需 guard 审核）

## kitt（架构终审）
- model: mynewapi/claude-opus-4-6
- 职责: 架构设计、复杂推理、重大决策、Reality Checker
- tool限制: 全部工具可用
- 触发条件: 2步以上推理、不可逆操作、对外发布内容

## guard（安全审计）
- model: mynewapi/claude-opus-4-6
- 职责: 配置变更、安全审计、密钥管理、回滚
- tool限制: 全部工具可用
- 强制审核: 所有配置变更必须经 guard

## deep（代码执行）
- model: mygptapi/gpt-5.4
- fallback: mynewapi/claude-sonnet-4-6
- 职责: 代码开发、脚本编写、bug修复
- tool限制: exec, read, write, edit

## main（多模态）
- model: google-gemini-cli/gemini-3-pro-preview
- 职责: 图片/视频/长文档分析、定时任务执行
- tool限制: read, web_fetch, image

## scout（情报侦察）
- model: google-gemini-cli/gemini-3-pro-preview
- 职责: 外链读取、竞品情报、GitHub、搜索
- tool限制: web_search, web_fetch, exec

## sino（中文内容）
- model: kimi/kimi-k2.5
- fallback: glm/glm-4-plus
- 职责: 中文文案、早报、日报、翻译
- tool限制: read, write, message
