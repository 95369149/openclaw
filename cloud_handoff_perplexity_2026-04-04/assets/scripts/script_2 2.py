
# Verify all pages and share
import os
pages = [
    ('output/page1_main_circuit.png', '第1页 主回路图'),
    ('output/page2_control_circuit.png', '第2页 控制回路图（梯形图）'),
    ('output/schematic_v2.png', '第3页 TC-6832 I/O原理图'),
    ('output/page4_terminal.png', '第4页 端子接线分配表'),
    ('output/page5_bom.png', '第5页 物料清单BOM'),
    ('output/panel_layout_corrected.png', '附图 配电板布置图（1650×350）'),
]
for p,n in pages:
    sz = os.path.getsize(p)/1024
    print(f"✓ {n}: {sz:.0f} KB")
