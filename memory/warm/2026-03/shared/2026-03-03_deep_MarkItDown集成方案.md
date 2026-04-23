# MarkItDown 集成到红太阳工作流方案

- 生成时间：2026-03-03 00:49:46 +0800
- 文件：/Users/apple/.openclaw/workspace/memory/shared/2026-03-03_deep_MarkItDown集成方案.md

## 1) 安装与测试方案

安装（建议独立虚拟环境）：
```bash
python3 -m venv /Users/apple/.openclaw/workspace/.venv-markitdown
source /Users/apple/.openclaw/workspace/.venv-markitdown/bin/activate
pip install -U pip
pip install 'markitdown[all]'
```

测试目录：`/Users/apple/.openclaw/workspace/memory/test-files/`
首批样例：
- `客户A_报价单.pdf`（多页报价）
- `客户B_订单.xlsx`（SKU/数量/金额）
- `HTYCNC_产品手册.docx`
- `售前方案.pptx`
- `设备铭牌.jpg`
- `客户语音需求.m4a`

验收标准：
- 成功率≥95%；
- 关键字段（型号、数量、价格、日期）可稳定抽取；
- 输出文件可追溯源文件。

## 2) 三个应用场景

a) 客户文档自动处理  
输入：`/Users/apple/.openclaw/workspace/Documents/客户文档/` 的 PDF/Excel。  
输出：
- Markdown：`/Users/apple/.openclaw/workspace/memory/knowledge-base/customers/`
- JSON：`/Users/apple/.openclaw/workspace/memory/knowledge-base/structured/orders/`
价值：减少录入，形成统一订单数据。

b) 产品知识库（RAG）  
输入：手册、技术文档、FAQ。  
输出：`/Users/apple/.openclaw/workspace/memory/knowledge-base/products/`  
价值：支持客服问答、售前检索、培训复用。

c) 销售资料智能分析  
输入：客户PPT、竞品资料。  
输出：`/Users/apple/.openclaw/workspace/memory/knowledge-base/sales-insights/`（需求摘要/竞品对比/行动建议）。

## 3) 技术实现路径（Python）

脚本：`/Users/apple/.openclaw/workspace/memory/scripts/markitdown_ingest.py`

流程：
1. 监控 ` /Users/apple/.openclaw/workspace/Documents/客户文档/ `；
2. 扫描新增文件（mtime+hash 去重）；
3. MarkItDown 转 Markdown；
4. 写入 ` /Users/apple/.openclaw/workspace/memory/knowledge-base/raw/ `；
5. 生成元数据（source_path、doc_type、processed_at）。

可选定时：接入 OpenClaw cron，每15分钟执行：
```bash
python /Users/apple/.openclaw/workspace/memory/scripts/markitdown_ingest.py
```

## 4) 与现有系统集成

- 与 X 监控协同：线索附件统一落地到  
`/Users/apple/.openclaw/workspace/Documents/客户文档/leads/`
- 与学习摄取协同：行业资料统一落地到  
`/Users/apple/.openclaw/workspace/Documents/客户文档/market/`
- 命名规范：`来源_主题_类型_YYYYMMDD.ext`  
  例：`RFQ_客户A_报价单_20260303.pdf`
- Markdown 规范：`YYYYMMDD_来源_主题_类型.md`
- 目录建议：
  - 输入：`/Users/apple/.openclaw/workspace/Documents/客户文档/{leads,orders,products,market}`
  - 输出：`/Users/apple/.openclaw/workspace/memory/knowledge-base/{raw,customers,products,sales-insights,structured/orders}`

结论：先以“目录扫描+自动转换+结构化抽取”两周落地，再叠加RAG与分析模板，形成红太阳可持续增长的文档智能中枢。
