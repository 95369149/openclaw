# Claude Working Draft

## 状态：v0.2-draft 已输出

日期：2026-04-04

## 输出文件（draft/）

| 文件 | 版本 | 状态 |
|------|------|------|
| 00_index.md | v0.2 | 完成 |
| 01_power_topology.md | v0.2 | 完成 |
| 02_control_circuit.md | v0.2 | 完成 |
| 03_vfd_circuit.md | v0.1 | 待更新（MD310 参数值仍需 page7 图纸） |
| 04_servo_pinout.md | v0.1 | 待更新（需驱动器手册） |
| 05_io_table.md | v0.2 | 完成 |
| 06_terminal_blocks.md | v0.2 | 完成 |
| 07_panel_grounding.md | v0.2 | 完成（含 page6 走线数据） |
| 08_emi_emc.md | v0.1 | 基本完整 |
| 09_missing_info.md | v0.2 | 完成（已标注已解决项） |

## 信息来源

- source_cleaned.md（pages 7-9 详细）
- images/（7 张图片）
- exported-assets.zip → script.py（page1）、script_1.py（page2）、script_4.py/script_5.py（page3）、page6_routing.png 图片
- script_5~11.py 为抖音视频生成器无关代码，已忽略

## v0.2 新增确认数据

- QF0 = 施耐德 NSX100F 3P+N 63A
- KM1 = NC1-25 DC24V；KM2 = NC1-12 DC24V
- PS1 = S-250-24（24V/10A）；QF8 6A 供电
- SF1 = Pilz PNOZ X2P DC24V 2NO；双通道急停
- SVON 中间继电器 = 欧姆龙 G2R DC24V
- CB1~CB4 四路 24V 分支断路器（2A/3A/1A/2A）
- QF3~5 = 6A（SRV1~3 400W）；QF6~7 = 4A（SRV4~5 100W）
- R01~R14 完整梯形图功能
- IN1~IN8 / OUT1~OUT14 完整 I/O 分配及线号
- XT-IN/XT-OUT 端子号（奇数序列）
- 5轴：X=SRV1前后轴1，Y=SRV2前后轴2，UD1=SRV3左右轴，Z=SRV4升降轴，U=SRV5旋转轴
- 拖链截面 65×38mm，5层分组，12步施工顺序
- 风机 9kW 380V，KM2 控制

## 下一步精修建议

1. 获取 page4（端子接线分配表）→ 填充 XT-MP 逐针定义
2. 获取 page5（BOM）→ 填充器件型号
3. 获取 SRV1~5 驱动器手册 → 完善 04_servo_pinout.md
4. 确认安全等级（PLc/PLd）→ 完善 02_control_circuit.md 安全部分

