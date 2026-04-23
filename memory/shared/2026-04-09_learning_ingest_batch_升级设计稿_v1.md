# learning_ingest_batch 升级设计稿 v1

时间：2026-04-09 07:12 CST
负责人：Kitt
目标：把当前 `learning_ingest_batch` 从“扫描 inbox / 收藏并写摘要”升级成更贴合 OpenClaw 2026.4.8 的 **wiki 编译流**，让它成为 `memory-wiki + active memory + shared digest` 的桥接层，而不是单纯日报生成器。

---

## 一、升级背景

当前 `learning_ingest_batch` 的主要问题：

1. **偏“扫一遍写摘要”**
   - 原料扫描后直接出日报/摘要
   - 缺少 claim / evidence / contradiction 的结构化中间层

2. **shared/ 承担过多知识沉淀**
   - 长期知识、阶段结论、任务交付、临时摘要混在一起
   - 不利于后续 recall / compile / dashboard

3. **没有真正接上 `memory-wiki` 的主链**
   - 现有 ingest 更像 active memory 周边脚本
   - 还没升级成“原料 → 编译知识 → 交付摘要”的结构

4. **Dream / digest / ingest 边界不清**
   - dreaming 被当日报输出器
   - ingest 也在做摘要
   - shared/ 还在承接部分知识归档

因此，这次升级目标不是“继续优化摘要质量”，而是：

> **把 ingest 升级成知识编译前置层，让 memory-wiki 成为长期知识底座，让 shared/ 回归成果层。**

---

## 二、升级后目标结构

`learning_ingest_batch` 以后只负责五步：

1. **Raw Collect**
2. **Extract / Normalize**
3. **Claim / Evidence Build**
4. **Wiki Compile Trigger**
5. **Shared Digest Output**

也就是：

```text
raw source
  ↓
extract / summarize / normalize
  ↓
claim + evidence + tags + contradictions
  ↓
memory-wiki import / compile / lint
  ↓
shared digest（只保留完成摘要与交付）
```

---

## 三、目标分层（四层收口）

### 1. 原料层 Raw

存放未整理输入，不作为长期知识成品。

建议目录：

- `memory/inbox/`
- `memory/80_收藏/`
- 外部抓取缓存 / 原始 markdown / URL 清单

**规则**：

- 原料保留来源、时间、URL、抓取方式
- 不直接视为“知识已沉淀”

---

### 2. 编译知识层 Compiled Wiki

由 `memory-wiki` 负责。

建议落点：

- 官方 vault：`memory/wiki-vault/`（或实际生成落点）
- 产物包括：
  - claims
  - evidence
  - dashboards
  - digest
  - compiled pages

**规则**：

- 长期知识尽量不再直接堆进 `shared/`
- 以 topic / entity / project / workflow 为组织维度

---

### 3. 成果层 Durable Results

只保留可复用输出和阶段性交付。

建议目录：

- `memory/shared/`

**保留内容**：

- 正式清单
- 最终方案
- 模板
- SOP
- 对外可复用报告
- 执行摘要

**不再鼓励放入**：

- 纯原料摘抄
- 零散学习片段
- 临时中间态摘要

---

### 4. 系统记忆层 System Memory

继续由现有 active memory 承担。

包括：

- `memory/.abstract`
- `MEMORY.md`
- 日志 `memory/2026-04-09.md`
- dreaming / daily notes / task-board

**作用**：

- 保留行为规则、长期教训、运行状态、任务上下文
- 不替代 wiki compiled knowledge

---

## 四、新版 ingest 流程设计

### Step 1：扫描原料

扫描范围：

- `memory/inbox/`
- `memory/80_收藏/`
- 指定 source feed / 链接清单
- 需要时接外部 search/extract

输出：

- 本轮新增源列表
- 去重后的候选条目清单

**要求**：

- 空目录 / 无新增时默认静默
- 正常完成不通知厂长

---

### Step 2：提取与标准化

对每条源做最小必要处理：

- 标题
- 时间
- 来源 URL / 文件路径
- 主题标签
- 核心摘要
- 关键事实点
- 适用场景
- 是否与现有主题重复/冲突

输出：

- normalized item 列表

**这里建议吸收 `ai-rag-pipeline` 的结构**：

- retrieval
- extraction
- context cleanup
- source attribution

---

### Step 3：构建 claim / evidence / contradiction

每条内容不再只做“摘要”，而要转为知识对象：

#### Claim

- 这条内容声称了什么
- 是否是动作建议、事实判断、趋势判断、策略判断

#### Evidence

- 证据来源是什么
- 原始出处 / 引文 / 文件路径 / URL
- 是否一手/二手来源

#### Contradiction

- 是否与已有结论冲突
- 冲突点是什么
- 是否需要人工审核

#### Metadata

- topic
- tags
- importance
- confidence
- freshness
- owner（若属于具体项目）

输出：

- 准备进入 wiki 的结构化条目

---

### Step 4：触发 wiki 编译

目标动作：

- bridge import
- compile
- lint
- digest/dashboard update

理想链路：

```text
normalized items
  → memory-wiki bridge import
  → wiki compile
  → wiki lint
  → dashboards / digests refresh
```

**注意**：

- 当前环境 `openclaw wiki` CLI 仍存在 `SIGKILL` 风险
- 因此短期必须采用：
  - 单步命令
  - 文件系统验收
  - 不以一条长命令定成败

**验收物优先级**：

1. `wiki-vault` 是否生成
2. `claims/evidence` 相关产物是否生成
3. `reports/` / dashboards / digest 是否更新
4. 文件内容是否符合预期，而不是只看命令退出码

---

### Step 5：写 shared digest

shared 只写：

- 本轮 ingest 处理了什么
- 沉淀到哪些 wiki topic / claim / dashboard
- 哪些内容值得厂长看
- 哪些内容需要人工判断

**shared digest 模板建议**：

1. 本轮新增来源数
2. 进入 wiki 的主题数
3. 关键 claim 3-5 条
4. 新发现矛盾/冲突点
5. 可执行建议 1-3 条
6. 若无重要新增，则静默或只落盘不通知

---

## 五、Dream / ingest / shared 的重新分工

### ingest

负责：

- 原料摄取
- 结构化整理
- 推入 wiki
- 产出简洁 digest

### dreaming

负责：

- 后台巩固
- 聚类
- 低频整合
- 长周期模式发现

**不再负责**：

- 给厂长发“Dream完成”
- 充当日报广播器

### shared

负责：

- 成果与交付
- SOP / 模板 / 正式总结

**不再负责**：

- 充当长期知识大杂烩

---

## 六、升级原则（必须遵守）

1. **正常完成默认静默**
   - 无新增、无异常、Dream 正常完成，都不要推送给厂长

2. **只有异常才通知**
   - gateway 不可达
   - CLI 连续失败
   - wiki compile/lint 异常
   - claims 结构损坏
   - 连续多轮 ingest 未处理成功

3. **shared 只放成果，不放原料垃圾**

4. **长期知识优先进入 wiki，不再堆 shared**

5. **命令执行结果必须以文件验收为准**
   - 当前环境对 `openclaw wiki` 存在 `SIGKILL`，不能只看命令返回

---

## 七、建议的第一版落地任务拆解

### P0-A：先把新版流程定稿

输出：

- 本文档（已完成）

### P0-B：梳理当前 `learning_ingest_batch` 实际脚本/配置入口

目标：

- 找到当前 cron / script / prompt / session 入口点
- 搞清楚现在到底谁在扫描、谁在写摘要、谁在通知

### P0-C：补一份字段规范

至少定义：

- source
- title
- summary
- claim
- evidence
- contradiction
- tags
- topic
- importance
- confidence
- status

### P0-D：把 shared digest 模板收窄

只保留成果摘要，不再兼任知识仓库

### P1：等 wiki CLI 稳定后，把 bridge/import/compile/lint 串起来

---

## 八、理想的最终形态

```text
外部/本地原料
  ↓
learning_ingest_batch（采集 + 标准化 + claim/evidence）
  ↓
memory-wiki（bridge/import/compile/lint/dashboard）
  ↓
shared digest（对厂长可读的交付摘要）
  ↓
active memory / dreaming（规则、状态、长期反思、运行闭环）
```

最终效果：

- raw 不等于知识
- shared 不等于知识库
- dreaming 不等于日报器
- wiki 才是 compiled knowledge 的底座
- ingest 是把原料送进底座的装配线

---

## 九、下一步

下一轮直接做：

1. 找出当前 `learning_ingest_batch` 的真实脚本/配置入口
2. 查 Dream 正常完成通知到底从哪发出来
3. 设计 claim/evidence 字段规范 v1
