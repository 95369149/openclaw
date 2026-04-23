# MemPalace 接入 OpenClaw 方案

时间：2026-04-10 12:00 CST

1. 安装验证：`python3.9 -m pip install mempalace`；兼容性测试：`python3.9 -c "import mempalace, chromadb; print('ok')" && python3.9 -m mempalace --help`。若命令不存在，再测 `mempalace --help`。建议单独记录依赖版本到 `/Users/apple/.openclaw/workspace/requirements-mempalace.txt`。

2. 初始化：建议 palace 根目录放 `/Users/apple/.openclaw/workspace/.mempalace`，执行 `mempalace init /Users/apple/.openclaw/workspace/.mempalace`。结构上：`wings` 按域划分（sales/customers/devices/ops）；`halls` 按来源或生命周期（daily-notes/shared-memory/tasks）；`rooms` 按实体建（客户名、设备型号、项目号）。这样既能做横向搜索，也能按业务归档。

3. 批量导入：扫描 `/Users/apple/.openclaw/workspace/memory/shared/*.md`，每篇文档切块后写入 palace。示例 Python：遍历 glob→读取 markdown→按标题/段落分 chunk→为每块附 metadata `{source_path,tags,date}`→调用 `mempalace add --wing shared --hall memory --room <文件名> --text <chunk>`；如走 SDK，则 `client.add(text=chunk, metadata=...)`。导入后抽样执行 `mempalace search "某客户/某项目"` 验证命中率。

4. 集成 OpenClaw：优先做 CLI 包装，成本最低——在检索前由 agent 先调用 `mempalace search`，命中后再回读原文路径；写入时在任务完成、决策确认后追加 `mempalace add`。进阶再接 MCP server，把 search/add/list 暴露成工具，替代现在纯 markdown 手读。建议先 CLI 验证价值，再 MCP 产品化。

5. 风险与回滚：风险主要是 Python 3.9 兼容性、导入脚本切块不佳导致召回差、metadata 设计混乱。回滚方案：保留 `/Users/apple/.openclaw/workspace/memory/shared/` 作为唯一事实源，MemPalace 仅做旁路索引；初始化与数据目录独立放在 `.mempalace/`，出问题直接停用检索并删除该目录，原 markdown 流程不受影响。
