# 接手说明（中文）

## 这个包是什么
这是一个给 Cloud / Claude 接手用的振动刀设备电气设计 handoff 包。
目标不是直接出最终施工图，而是基于现有 markdown、图片、脚本资产，继续整理成可精修的工程草案。

## 当前已有资产
- `source.md`：原始导出 markdown
- `source_cleaned.md`：已做一轮清洗的 markdown
- `images/`：主回路、控制回路、IO、布线、变频器柜、伺服针脚、接地等图片
- `assets/scripts/`：导出残留/辅助脚本，先保留，不假定一定有用
- `spec.md`：目标输出要求
- `claude_working.md`：Claude 后续工作底稿

## 处理边界
1. 不要把现有内容当成最终可施工图。
2. 要区分“已确认事实”和“工程假设”。
3. 不要擅自编造具体器件型号、端子号、线号、PLC 点位。
4. 可以整理、重组、补结构，但不能把缺失数据伪装成已确定。

## Cloud / Claude 下一步重点
1. 先读 `source_cleaned.md`
2. 逐张核对 `images/`
3. 重组为更清晰的工程文档
4. 输出时重点覆盖：
   - power topology
   - main circuit
   - control circuit
   - 24V circuit
   - VFD circuit
   - safety circuit
   - terminal blocks
   - EMI / EMC recommendations
   - missing information

## 当前最可能缺的内容
- 端子号
- 线号
- PLC / 控制卡 IO 对应表
- 伺服/驱动器最终品牌与接口定义
- 变频器联锁细节
- 安全回路细节

## 目标
把当前资产包整理成“可继续精修的电气设计草案”，而不是聊天总结。
