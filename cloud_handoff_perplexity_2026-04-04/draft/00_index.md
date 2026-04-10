# 振动刀切割机 — 电气设计草案索引

版本：v0.4-draft  
日期：2026-04-10  
状态：**草案，不可直接用于施工**

> v0.4 更新：补全 C-08 主回路/变频器回路线径工程推算，补全 B-03 VFD 频率给定方式推断，整理 B-04 IN1/IN2 急停双通道接线逻辑。
> 保留未确认项：安全等级、门联锁、DS2 是否支持 STO、XT-MP 11~24 中 TC 操作盒逐针定义、ALM CLR 输出点位等。

---

## 文件清单

| 文件 | 内容 |
|------|------|
| [01_power_topology.md](01_power_topology.md) | 供电拓扑 / 主回路 |
| [02_control_circuit.md](02_control_circuit.md) | 控制回路（24V 逻辑 + 继电器梯形图） |
| [03_vfd_circuit.md](03_vfd_circuit.md) | 变频器柜接线 + 气路 + MD310 参数 |
| [04_servo_pinout.md](04_servo_pinout.md) | 伺服驱动器 CN1/CN2 引脚定义 |
| [05_io_table.md](05_io_table.md) | TC-6832 I/O 分配表 |
| [06_terminal_blocks.md](06_terminal_blocks.md) | 端子排分配（XT-IN / XT-OUT / XT-MP / XT-PE） |
| [07_panel_grounding.md](07_panel_grounding.md) | 操作台面板布局 + PE 接地系统 |
| [08_emi_emc.md](08_emi_emc.md) | EMI/EMC 建议 |
| [09_missing_info.md](09_missing_info.md) | 缺失信息清单 / 待确认项 |
| [10_bom.md](10_bom.md) | 电气物料清单 BOM（36类） |

---

## 信息来源说明

- **已确认事实**：来自 source_cleaned.md（Perplexity 导出清洗版）及 images/ 图纸
- **工程推算**：在各文件中以 `[推算]` 标注
- **待确认**：在各文件中以 `[待确认]` 标注，汇总于 09_missing_info.md

---

## 图纸对应关系

| 页次 | 图片文件 | 内容 |
|------|----------|------|
| 1/9 | images/page1_main_circuit.png | 主回路图 |
| 2/9 | images/page2_control_circuit.png | 控制回路梯形图 |
| 3/9 | images/page3_io.png | TC-6832 I/O 图 |
| 4/9 | （无对应图片导出） | 端子接线分配表 |
| 5/9 | （无对应图片导出） | BOM 物料清单 |
| 6/9 | images/page6_routing.png | 走线路径 + 拖链截面 |
| 7/9 | images/page7_vfd_cabinet.png | 变频器柜 + 气路 + 参数 |
| 8/9 | images/page8_servo_pins.png | 伺服 CN1/CN2 引脚图 |
| 9/9 | images/page9_panel_grounding.png | 操作台 + 接地系统 |
