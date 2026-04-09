# 2026-04-09 cron 降噪与 ingest 升级落地记录

时间：2026-04-09 07:52 CST
负责人：Kitt
状态：已完成第一阶段落地

---

## 一、本轮已实际修改

### 1. 修改文件
- `/Users/apple/.openclaw/cron/jobs.json`

### 2. 自动备份
- `/Users/apple/.openclaw/cron/jobs.json.bak.20260409_074602`

---

## 二、已完成的两项核心改动

### A. Dream 通知降噪
目标：彻底去掉正常执行后的“Dream完成”噪音。

原来：
- `dream_memory_consolidation`
- prompt 中硬编码：`完成后回复'Dream完成'`

现在改为：
- 正常完成时 **不要输出任何内容**
- **不要回复“Dream完成”**
- 仅当脚本执行失败、出现异常、或发现需要人工关注的问题时，才输出简短异常摘要

### 结论
`Dream完成` 的源头级配置已被替换，后续是否彻底静默，只需看下一次对应 run 的 delivery 结果即可。

---

### B. `learning_ingest_batch` 升级为 memory-wiki bridge 方向
目标：把它从“手写 wiki 文件 + shared 摘要”改成“结构化编译输入 + shared digest”的新架构。

已改内容：
- prompt 标题改为：`每日知识编译任务（memory-wiki bridge 版）`
- 明确要求先做：
  - 标题
  - 核心观点
  - 对红太阳的启示
  - topic
  - tags
  - importance
  - confidence
  - contradiction note
- 明确要求生成结构化编译输入：
  - `claim`
  - `evidence`
  - `source`
  - `tags`
  - `topic`
  - `contradiction`
- 明确 shared 只保留成果摘要，不再把长期知识直接堆进 shared
- 明确 CLI / wiki compile 不稳定时，可先落中间编译稿，后续再 compile
- 明确正常完成不发用户消息，仅异常时输出

### 结论
`learning_ingest_batch` 已从“日报型 ingest”切到“编译型 ingest”的正确方向，虽然还不是代码级自动 compile，但 cron prompt 层已经扳正。

---

## 三、现场验收结果

已再次读取 `/Users/apple/.openclaw/cron/jobs.json`，确认两条 job 的 payload 已写入成功：

### `dream_memory_consolidation`
当前关键信息：
- 正常完成静默
- 不再回复 `Dream完成`
- 异常才输出摘要

### `learning_ingest_batch`
当前关键信息：
- 已显示为 `memory-wiki bridge 版`
- 已要求 claim/evidence/source/topic/tags/contradiction 结构
- 已要求 shared 仅保留 digest
- 已要求正常完成不输出消息

---

## 四、下一步验收动作（留给后续轮次）

### P1：看下一次 Dream run
重点确认：
- `561747e0-e8d2-453f-b7ac-d9dd6fbf59d9` 对应 run 是否 `status=ok`
- 是否 `lastDeliveryStatus=not-delivered` 或等效静默结果
- 不再出现“Dream完成”文案

### P1：看下一次 `learning_ingest_batch` run
重点确认：
- 输出是否从“wiki 直接堆文”转向“结构化 digest”
- 是否出现 compile 降级说明
- 是否仍有 delivery 噪音

---

## 五、一句话总结

本轮不是只写方案，已经把两处关键 cron 真配置改了：
- Dream：从源头静默
- learning_ingest_batch：从摘要型 prompt 扳到 memory-wiki bridge 型 prompt
