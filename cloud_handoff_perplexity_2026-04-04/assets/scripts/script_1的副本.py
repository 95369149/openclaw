
# Final summary: list all 6 pages
import os
pages = [
    ('output/page1_main_circuit.png',   '1/6  主回路图'),
    ('output/page2_control_circuit.png','2/6  控制回路图（梯形图）'),
    ('output/page3_io.png',             '3/6  TC-6832 I/O 接线原理图'),
    ('output/page4_terminal.png',       '4/6  端子接线分配表'),
    ('output/page5_bom.png',            '5/6  物料清单 BOM'),
    ('output/page6_routing.png',        '6/6  走线路径+拖链截面+施工顺序'),
    ('output/panel_layout_corrected.png','附图  配电板布置图（1650×350 Rev.B）'),
]
print(f"{'页次':<30} {'文件大小':>10}")
print('─'*44)
total = 0
for fn,name in pages:
    if os.path.exists(fn):
        sz = os.path.getsize(fn)//1024
        total += sz
        print(f"{name:<30} {sz:>8} KB")
print('─'*44)
print(f"{'合计':<30} {total:>8} KB")
