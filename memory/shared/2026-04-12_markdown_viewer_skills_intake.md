# markdown-viewer skills 接入记录

来源仓库：`https://github.com/markdown-viewer/skills`
拉取时间：2026-04-12
本地镜像：`/Users/apple/.openclaw/workspace/markdown-viewer-skills`

## 处理策略

采用“吸收适合当前机器的能力，不整包覆盖现有技能”的策略。

### 已吸收进 workspace

路径：`/Users/apple/.openclaw/workspace/skills/markdown-viewer/`

已纳入：

- architecture
- infographic
- infocard
- mermaid
- vega
- graphviz
- security
- network
- cloud
- uml
- data-analytics
- bpmn
- archimate
- iot

### 暂未吸收

- canvas

原因：workspace 已存在 `skills/canvas` 相关能力，先避免重名冲突。

## 适配建议

最值得先用的 5 个：

1. `architecture`：系统架构图、分层图
2. `infographic`：老板汇报图、流程图、KPI 图卡
3. `infocard`：单页知识卡、人物卡、方案卡
4. `mermaid`：流程与时序图
5. `vega`：数据图表

## 下一步

后续需要时，可把这些 skill 再封装成适合 OpenClaw 当前工作流的本地 skill 索引与调用规范。
