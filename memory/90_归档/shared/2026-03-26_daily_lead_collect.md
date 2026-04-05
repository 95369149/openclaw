# 每日线索采集报告 — 2026-03-26

**采集时间**: 2026-03-26 08:30 CST  
**执行状态**: ✅ 成功（ImportYeti 数据落盘，Apollo 鉴权失败已记录）  
**总线索数**: 20 条（ImportYeti）+ 0 条（Apollo，401 失败）

---

## 系统状态

| 组件 | 状态 | 说明 |
|------|------|------|
| 后端 API | ❌ 未就绪 | `ModuleNotFoundError: No module named 'sqlalchemy'`，venv 依赖未安装 |
| ImportYeti | ✅ 正常 | 直连网站 API，无需 Key |
| Apollo | ⚠️ 401 | API Key 鉴权失败，需更新 Key |
| Apify | 未用 | ImportYeti 直连成功，未触发 Apify 兜底 |

> 后端未就绪：已尝试 `bash start.sh` 拉起，进程存在但端口未响应，根因为 sqlalchemy 未安装。按规则已记录，未告警。

---

## ImportYeti 采集结果

### 关键词：oscillating knife cutter（10 条）

| 公司名 | 国家 | 进口批次 | 最近发货 | ImportYeti 链接 |
|--------|------|---------|---------|----------------|
| Oscillating Systems Technology | BR 🇧🇷 | 90 | 2025-03-12 | [链接](https://www.importyeti.com/supplier/oscillating-systems-technology) |
| Yuan Lih Knife | TW 🇹🇼 | 90 | 2026-02-24 | [链接](https://www.importyeti.com/supplier/yuan-lih-knife) |
| We Knife | CN 🇨🇳 | 67 | 2022-11-10 | [链接](https://www.importyeti.com/supplier/we-knife) |
| China Knife | CN 🇨🇳 | 62 | 2021-01-29 | [链接](https://www.importyeti.com/supplier/china-knife) |
| Key Knife | DE 🇩🇪 | 38 | 2025-09-11 | [链接](https://www.importyeti.com/supplier/key-knife) |
| Moki Knife | JP 🇯🇵 | 23 | 2022-10-07 | [链接](https://www.importyeti.com/supplier/moki-knife) |
| Hello Knife | CN 🇨🇳 | 21 | 2025-07-09 | [链接](https://www.importyeti.com/supplier/hello-knife) |
| Ningbo Huaxing Cutter | CN 🇨🇳 | 15 | 2024-02-29 | [链接](https://www.importyeti.com/supplier/ningbo-huaxing-cutter) |
| Control Cutter | NO 🇳🇴 | 6 | 2025-08-09 | [链接](https://www.importyeti.com/supplier/control-cutter) |
| Cutter | IT 🇮🇹 | 4 | 2022-05-25 | [链接](https://www.importyeti.com/supplier/cutter) |

**⭐ 重点关注**：
- **Yuan Lih Knife（台湾）**：90 批次，最近发货 2026-02-24，高频活跃进口商，上游供应商含 TKM，有切割工具采购需求
- **Oscillating Systems Technology（巴西）**：90 批次，南非约翰内斯堡地址，跨区域业务

---

### 关键词：vibrating blade cutting machine（10 条）

| 公司名 | 国家 | 进口批次 | 最近发货 | ImportYeti 链接 |
|--------|------|---------|---------|----------------|
| Tdc Cutting Tools | CN 🇨🇳 | 993 | 2022-12-09 | [链接](https://www.importyeti.com/supplier/tdc-cutting-tools) |
| Wuxi Turbine Blade | CN 🇨🇳 | 697 | 2026-03-07 | [链接](https://www.importyeti.com/supplier/wuxi-turbine-blade) |
| Jewel Blade | GB 🇬🇧 | 168 | 2026-02-15 | [链接](https://www.importyeti.com/supplier/jewel-blade) |
| Carrier Vibrating Equipment | CN 🇨🇳 | 41 | 2026-01-08 | [链接](https://www.importyeti.com/supplier/carrier-vibrating-equipment) |
| C Blade | IT 🇮🇹 | 58 | 2026-03-04 | [链接](https://www.importyeti.com/supplier/c-blade) |
| Honggang Cutting Machine | CN 🇨🇳 | 3 | 2017-04-10 | [链接](https://www.importyeti.com/supplier/honggang-cutting-machine) |
| Hanggang Cutting Machine | CN 🇨🇳 | 1 | 2017-01-15 | [链接](https://www.importyeti.com/supplier/hanggang-cutting-machine) |
| Italian Cutting Machine | IT 🇮🇹 | 1 | 2023-06-03 | [链接](https://www.importyeti.com/supplier/italian-cutting-machine) |
| Maanshan Zhengli Machine Blade | CN 🇨🇳 | 2 | 2023-08-15 | [链接](https://www.importyeti.com/supplier/maanshan-zhengli-machine-blade) |
| Vegetable Cutting Machine | CN 🇨🇳 | 1 | 2017-11-14 | [链接](https://www.importyeti.com/supplier/vegetable-cutting-machine) |

**⭐ 重点关注**：
- **Jewel Blade（英国）**：168 批次，2026-02-15 最近发货，Sheffield 刀片制造商，上游含 Accutec Blades、US Blade Manufacturing，切割刀片专业买家
- **C Blade（意大利）**：58 批次，2026-03-04 最近，供应 Siemens Energy / GE，工业级精密切割

---

## Apollo 采集结果

| 关键词 | 状态 | 说明 |
|--------|------|------|
| CNC cutting machine | ⚠️ 401 Unauthorized | API Key 已失效，需在 apollo.io 后台更新 |
| composite material cutting | ⚠️ 401 Unauthorized | 同上 |

> 按规则：Apollo 鉴权失败已记录，**不影响本次 Job 成功判定**。

---

## 待办 / 已知问题

1. **后端 venv 修复**（高优先级）：
   ```bash
   cd /Users/apple/.openclaw/workspace/projects/b2b-growth-system/backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r ../requirements.txt
   ```
2. **Apollo API Key 更新**：登录 [apollo.io](https://apollo.io) → Settings → API Keys → 重新生成并更新 `backend/.env` 中的 `APOLLO_API_KEY`
3. **ImportYeti 关键词优化**：当前结果含部分刀具/turbine blade 等无关条目，建议后续调整为更精确关键词（如 "fabric cutting machine" / "leather cutting machine"）

---

*自动生成 by Kitt · 2026-03-26 08:30 CST*
