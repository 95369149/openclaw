# learning_ingest_batch 与 Dream 通知入口排查记录

时间：2026-04-09 07:31 CST
负责人：Kitt
目标：定位 `learning_ingest_batch` 的真实执行入口，以及 `Dream完成` / `早间推送` 的真实来源，作为后续结构改造和降噪的依据。

---

## 一、已确认的真实入口

### 1. `learning_ingest_batch` 的真实入口
来源文件：`/Users/apple/.openclaw/cron/jobs.json`

关键信息：
- **job name**: `learning_ingest_batch`
- **job id**: `c241361b-1216-472b-a6d6-57c451936e14`
- **enabled**: `true`
- **schedule**: `0 11 * * *`（Asia/Shanghai）
- **sessionTarget**: `isolated`
- **model**: `kimi/kimi-k2.5`
- **delivery**:
  - `mode`: `announce`
  - `channel`: `discord`
  - `to`: `channel:1484338422847115264`

当前 prompt 的真实逻辑仍是旧版“摘要 + wiki 文件追加”路线：
- 扫 `memory/inbox/`
- 扫 `memory/80_收藏/` 过去 48 小时新增
- 直接写 `memory/wiki/*.md`
- 更新 `memory/wiki/INDEX.md`
- 写 `memory/shared/YYYY-MM-DD_learning_ingest.md`
- delivery 自动推送 Discord

### 结论
当前 `learning_ingest_batch` **还没有真正接上官方 `memory-wiki` 编译流**，本质仍是：
> raw 扫描 → 人工主题归档 → shared 摘要

也就是我们前面判断的对：**现在只是“compile wiki 版 prompt”，还不是 memory-wiki 底座版。**

---

### 2. 早间推送的真实入口
来源文件：`/Users/apple/.openclaw/cron/jobs.json`

关键信息：
- **job name**: `morning_wisdom`
- **job id**: `9f979dd5-027b-40ea-bc8d-26119f1d4a98`
- **enabled**: `true`
- **schedule**: `0 7 * * *`（Asia/Shanghai）
- **model**: `google-gemini/gemini-2.5-flash`
- **delivery**:
  - `mode`: `announce`
  - `channel`: `discord`
  - `to`: `channel:1484338422847115264`

当前 prompt 明确要求生成：
- 国学金句（按星期轮换）
- 英语每日 2 句
- 并写入 `memory/20_领域/每日推送记录.md`

### 结论
今天看到的“早间推送 / 国学金句 / 英语每日2句”，真实来源就是这条 cron，不是别的系统自动拼接。

---

### 3. `Dream完成` 的真实入口
来源文件：`/Users/apple/.openclaw/cron/jobs.json`

关键信息：
- **job name**: `dream_memory_consolidation`
- **job id**: `561747e0-e8d2-453f-b7ac-d9dd6fbf59d9`
- **enabled**: `true`
- **schedule**: `every 7200000ms`（每 2 小时）
- **delivery**:
  - `mode`: `announce`
- **payload text**:
  - `运行记忆整合：python3 /Users/apple/.openclaw/workspace/bin/dream.py，完成后回复'Dream完成'`

### 结论
`Dream完成` 不是系统底层固定文案，而是 **cron job prompt 自己硬编码要求输出** 的结果。

也就是说：
> 只要这条 cron 还在 `完成后回复 'Dream完成'`，系统就会继续推送这句。

这是当前 Dream 噪音的**直接根因**，不是模型失控，也不是别的插件偷偷发。

---

## 二、Dream 脚本本身的现状
来源文件：`/Users/apple/.openclaw/workspace/bin/dream.py`

脚本真实行为：
- 扫描 `memory/shared/*.md`
- 依据 `.dream_cursor` 找新增文件
- 提取标题/摘要
- 直接追加写入 `MEMORY.md`
- 追加 `memory/history.jsonl`
- 更新 `.dream_cursor`
- 试图 git add/commit `MEMORY.md` 与 `memory/history.jsonl`
- 最后在 stdout 打印：
  - `✅ Dream 完成，写入 X 条洞察到 MEMORY.md`

### 结论
Dream 当前还是**老式 shared → MEMORY.md 整合器**，不是新版 `memory-wiki` 体系下的后台知识编译器。

它有三个明显问题：
1. 继续直写 `MEMORY.md`
2. 继续把 `shared/` 当主要输入源
3. cron prompt 还会额外要求回复 `Dream完成`

所以今天用户抱怨的 Dream 噪音，根因已经定位清楚：
- **调度层**：cron 配置要求回复 `Dream完成`
- **脚本层**：dream.py 仍是旧架构，围绕 `shared → MEMORY.md`

---

## 三、当前结构判断（已进一步坐实）

### learning_ingest_batch
当前仍是：
- 扫 raw
- 直接写 `memory/wiki/*.md`
- 再写 shared digest

不是：
- claim/evidence
- memory-wiki bridge/import/compile/lint
- dashboard/digest 自动更新

### dreaming
当前仍是：
- 扫 shared
- 更新 MEMORY.md
- cron 广播“Dream完成”

不是：
- 后台静默整合层
- wiki compiled knowledge 的低频巩固器

---

## 四、后续改造优先级（更新版）

### P0-1：改 `learning_ingest_batch` prompt
目标：
- 从 `memory/wiki/*.md` 手写归档模式
- 升成 claim/evidence + wiki compile 触发模式

### P0-2：改 `dream_memory_consolidation` cron
目标：
- 去掉 `完成后回复'Dream完成'`
- 改为“仅异常才输出”
- 正常完成完全静默

### P0-3：评估 `bin/dream.py` 是否降级或重构
目标：
- 不再把 `MEMORY.md` 当主知识整合落点
- 让 dreaming 回归后台巩固，不再充当日报器/知识主仓

---

## 五、一句话结论

今天这轮排查已经把三个关键入口钉死了：
- `learning_ingest_batch`：确实在 cron 里，且还是旧 prompt 结构
- `morning_wisdom`：就是早间推送来源
- `dream_memory_consolidation`：`Dream完成` 的直接根因，来自 cron prompt 硬编码
