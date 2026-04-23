# 语义记忆：Kitt 进化路线图

## 愿景

成为厂长的“真分身”：全记忆、全能力、全自动。

## 阶段目标

### Phase 1: 基础设施巩固 (Current)

- [x] **多模态模型**：Gemini 3.0 Pro (CLI) + Claude Opus (API) 双引擎。
- [x] **记忆架构**：文件系统范式 (Memory/ 目录树)。
- [ ] **稳定性**：实现 OpenClaw 故障自愈 (Auto-fix)，不依赖人工介入终端。

### Phase 2: 能力扩展 (Next)

- [ ] **PPT 生成**：移植 Reveal.js Skill，实现“一句话生成演示文稿”。
- [ ] **云端并发**：探索将耗时任务 (爬虫/渲染) 卸载到云端 (Kilo/Worker)，解决本地单线程瓶颈。
- [ ] **手机指挥中心**：优化 Telegram/WhatsApp 交互，实现手机端 Code Review 和复杂任务编排。

### Phase 3: 真分身形态 (Future)

- [ ] **全记忆同步**：像 OpenViking 那样，建立三级索引，毫秒级召回厂长所有历史决策。
- [ ] **主动决策**：从“执行指令”进化到“预判需求并提案”。
- [ ] **数字人格**：完美复刻厂长写作与沟通风格，对外无感替身。

### Phase 4: 具身智能 (Computer Use)

- [ ] **全知之眼**：集成屏幕视觉 (OmniParser/RF-DETR)，实时理解 GUI 界面元素。
- [ ] **神之手**：通过 PyAutoGUI/AppleScript 实现鼠标键盘级操控，操作非 API 软件（如剪映、Photoshop）。
- [ ] **闭环验证**：操作 -> 截图确认 -> 修正操作，实现无人值守的复杂 GUI 任务流。

## 对标竞品

- **Codexbot** (@biggor888)：云端并发、自运维能力。
- **OpenViking** (ByteDance)：三级记忆索引、会话自迭代。
- **Claude Computer Use** (Anthropic)：原生 GUI 操控能力。
