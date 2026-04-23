
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import numpy as np
import os, json

prop = fm.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
kw = dict(fontproperties=prop)

def tx(ax,x,y,s,fs=8,c='#111',ha='center',va='center',fw='normal',rot=0,z=9):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=c,fontweight=fw,
            rotation=rot,zorder=z,**kw,
            path_effects=[pe.withStroke(linewidth=1.5,foreground='white')])

def lh(ax,x1,x2,y,c='#333',lw=1.5,ls='-',z=5): ax.plot([x1,x2],[y,y],c,lw=lw,ls=ls,zorder=z)
def lv(ax,x,y1,y2,c='#333',lw=1.5,ls='-',z=5): ax.plot([x,x],[y1,y2],c,lw=lw,ls=ls,zorder=z)

fig = plt.figure(figsize=(30,22))
fig.patch.set_facecolor('white')

gs = fig.add_gridspec(2, 3, hspace=0.18, wspace=0.12,
                      left=0.04, right=0.97, top=0.93, bottom=0.06)

# ══════════════════════════════════════════════════════
# SUB-PLOT 1 (top-left, span 2 cols) — 机身走线俯视图
# ══════════════════════════════════════════════════════
ax1 = fig.add_subplot(gs[0, :2])
ax1.set_facecolor('#f8f9fa')
ax1.set_xlim(0,620); ax1.set_ylim(0,280)
ax1.axis('off')

# Machine body outline
ax1.add_patch(mpatches.FancyBboxPatch((20,30),400,220,
    boxstyle='round,pad=4',fc='#eeeeee',ec='#555',lw=2,zorder=2))
tx(ax1,220,260,'切割床身（俯视）',fs=11,fw='bold',c='#333')

# Gantry (横梁)
ax1.add_patch(mpatches.Rectangle((20,128),400,24,fc='#bdbdbd',ec='#555',lw=1.5,zorder=3))
tx(ax1,220,140,'横梁（Y轴）',fs=9,fw='bold',c='#333')

# 配电板 (right side of machine, embedded)
ax1.add_patch(mpatches.FancyBboxPatch((425,80),60,140,
    boxstyle='round,pad=3',fc='#e3f2fd',ec='#1565c0',lw=2,zorder=4))
tx(ax1,455,150,'配电板\n1650×350\n内嵌',fs=8.5,fw='bold',c='#0d47a1')
tx(ax1,455,115,'TC-6832\n(右侧)',fs=8,c='#4527a0')

# 小变频柜 (left side)
ax1.add_patch(mpatches.FancyBboxPatch((8,110),14,60,
    boxstyle='round,pad=2',fc='#fff9c4',ec='#e65100',lw=2,zorder=4))
tx(ax1,15,140,'变频\n柜',fs=7.5,fw='bold',c='#e65100')

# BR 角孔 (bottom-right of 配电板)
ax1.add_patch(plt.Circle((425,85),8,fc='#c62828',ec='#c62828',zorder=6))
tx(ax1,425,73,'BR角孔\n主出线口',fs=7,c='#c62828',fw='bold')

# BL 角孔 (bottom-left of 配电板)
ax1.add_patch(plt.Circle((425,215),8,fc='#2e7d32',ec='#2e7d32',zorder=6))
tx(ax1,425,227,'BL角孔\n主进线',fs=7,c='#2e7d32',fw='bold')

# TR 角孔 (操作台)
ax1.add_patch(plt.Circle((485,215),8,fc='#4527a0',ec='#4527a0',zorder=6))
tx(ax1,525,215,'TR角孔→操作台',fs=7,c='#4527a0',fw='bold',ha='left')

# Cable path: BR → along right side → to X-axis drag chain anchor
# Segment 1: BR → right wall bottom (vertical inside machine)
path_color_ac = '#c62828'
path_color_sig = '#1565c0'
path_color_enc = '#2e7d32'

# Route along right inner wall
for yy,col,lbl,yoffset in [
    (85,'#c62828','H1动力线 L1/L2/N/PE',-12),
    (90,'#1565c0','H5信号线 I/O/24V',-22),
    (95,'#2e7d32','H4编码/脉冲线',-32),
]:
    ax1.annotate('',xy=(240,yy+0),xytext=(420,yy+0),
        arrowprops=dict(arrowstyle='->',color=col,lw=2.5,
                        connectionstyle='arc3,rad=0.0'))

# X-axis drag chain (horizontal along Y=85~95)
ax1.add_patch(mpatches.FancyBboxPatch((60,72),340,38,
    boxstyle='round,pad=3',fc='none',ec='#888',lw=1.5,ls='--',zorder=3))
tx(ax1,220,59,'X轴拖链槽 (随横梁Y轴移动)\n65mm×38mm 尼龙拖链',fs=8.5,fw='bold',c='#555')

# Machine head (cutting head)
ax1.add_patch(mpatches.FancyBboxPatch((85,118),60,44,
    boxstyle='round,pad=4',fc='#fff3e0',ec='#e65100',lw=2,zorder=5))
tx(ax1,115,140,'机头\n(SRV4 升降\nSRV5 旋转)',fs=8,fw='bold',c='#e65100')

# Y-axis drag chain (vertical inside gantry)
ax1.add_patch(mpatches.FancyBboxPatch((148,118),30,44,
    boxstyle='round,pad=2',fc='none',ec='#aaa',lw=1.2,ls=':',zorder=3))
tx(ax1,163,108,'Y轴拖链\n(机头→横梁)',fs=7.5,c='#777')

# Arrows: from gantry fixed end to machine head
ax1.annotate('',xy=(148,140),xytext=(85+60,140),
    arrowprops=dict(arrowstyle='<->',color='#888',lw=1.5))

# Section callout arrows pointing to cross-section
for xa,ya,lbl in [(290,85,'截面A-A\n(见右上)'),(220,140,'截面B-B\n(见右下)')]:
    ax1.add_patch(plt.Circle((xa,ya),5,fc='#ffd54f',ec='#f57f17',zorder=7))
    tx(ax1,xa+2,ya-16,lbl,fs=7.5,c='#f57f17',fw='bold')

tx(ax1,310,260,'走线总原则:  ①动力线靠上层  ②信号线中层  ③编码/脉冲封闭下层  ④拖链槽内三层物理分隔',
   fs=8.5,c='#333',ha='center')
ax1.set_title('机身走线俯视路径图  (Top View Cable Routing)',
    fontsize=13,fontweight='bold',color='#1a237e',pad=10,**kw)

# ══════════════════════════════════════════════════════
# SUB-PLOT 2 (top-right) — X轴拖链截面 A-A
# ══════════════════════════════════════════════════════
ax2 = fig.add_subplot(gs[0, 2])
ax2.set_facecolor('white')
ax2.set_xlim(0,200); ax2.set_ylim(0,200)
ax2.axis('off')
ax2.set_title('截面 A-A   X轴拖链 65×38mm\n(Scale 2:1)',fontsize=11,fontweight='bold',color='#333',pad=8,**kw)

# Outer chain body
ax2.add_patch(mpatches.FancyBboxPatch((30,40),140,100,
    boxstyle='square,pad=0',fc='#e0e0e0',ec='#555',lw=2.5,zorder=2))
tx(ax2,100,155,'65 mm',fs=9,fw='bold',c='#333')
ax2.annotate('',xy=(170,148),xytext=(30,148),arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
ax2.annotate('',xy=(20,40),xytext=(20,140),arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax2,12,90,'38mm',fs=9,fw='bold',c='#333',rot=90)

# Divider plates (2 separators = 3 layers)
ax2.add_patch(mpatches.Rectangle((30,72),140,3,fc='#ffd54f',ec='#f57f17',lw=1,zorder=4))
ax2.add_patch(mpatches.Rectangle((30,105),140,3,fc='#ffd54f',ec='#f57f17',lw=1,zorder=4))
tx(ax2,178,74,'分隔条\n(黄色PVC)',fs=7.5,c='#f57f17',ha='left')

# Layer 1 (top) — 气管
for xi in [50,75,100,125,150]:
    ax2.add_patch(plt.Circle((xi,121),9,fc='#b3e5fc',ec='#0288d1',lw=1.5,zorder=5))
    tx(ax2,xi,121,'气\n管',fs=6,c='#0288d1')
tx(ax2,100,143,'层1: 气管  Ø12mm  ×4条',fs=8,fw='bold',c='#0288d1')

# Layer 2 (mid) — AC power + 24V
for xi,col,lbl in [(55,'#c62828','L'),(75,'#f57c00','L'),(95,'#1565c0','N'),
                   (115,'#2e7d32','PE'),(138,'#c62828','U'),(158,'#f57c00','V')]:
    ax2.add_patch(plt.Circle((xi,88),6,fc=col,ec='#333',lw=0.8,zorder=5))
    tx(ax2,xi,88,lbl,fs=5.5,c='white',fw='bold')
tx(ax2,100,76,'层2: 动力+24V  RVVP 1.5mm²  ×6+4',fs=8,fw='bold',c='#c62828')

# Layer 3 (bottom) — encoder + pulse (closed metal channel inside)
ax2.add_patch(mpatches.Rectangle((35,43),130,26,fc='#e8f5e9',ec='#2e7d32',lw=2,zorder=4))
for xi,col,lbl in [(50,'#c62828','PLS1'),(72,'#e65100','PLS2'),(94,'#2e7d32','PLS3'),
                   (116,'#1565c0','PLS4'),(138,'#880e4f','ENC')]:
    ax2.add_patch(plt.Circle((xi,56),7,fc=col,ec='#eee',lw=0.8,zorder=6))
    tx(ax2,xi,56,lbl,fs=5,c='white',fw='bold')
tx(ax2,100,45,'层3: 编码/脉冲(封闭金属槽内)',fs=7.5,fw='bold',c='#2e7d32')

# Wall thickness callout
tx(ax2,100,28,'拖链壁厚≥3mm  弯曲半径R≥75mm',fs=7.5,c='#555')
tx(ax2,100,18,'内净空: 65×38mm  (3层+2黄色PVC分隔条)',fs=7.5,c='#555')

# ══════════════════════════════════════════════════════
# SUB-PLOT 3 (bottom-left, span 2 cols) — 配电板到机身侧走线示意 (侧视)
# ══════════════════════════════════════════════════════
ax3 = fig.add_subplot(gs[1, :2])
ax3.set_facecolor('#fafafa')
ax3.set_xlim(0,620); ax3.set_ylim(0,200)
ax3.axis('off')
ax3.set_title('配电板出线 → 拖链槽 侧视走线图  (Side View)',
    fontsize=12,fontweight='bold',color='#1a237e',pad=8,**kw)

# Panel outline
ax3.add_patch(mpatches.FancyBboxPatch((8,30),80,140,
    boxstyle='round,pad=3',fc='#e3f2fd',ec='#1565c0',lw=2,zorder=3))
tx(ax3,48,130,'配电板\n1650×350',fs=9,fw='bold',c='#0d47a1')
tx(ax3,48,110,'A区      D区',fs=8,c='#555')
tx(ax3,48,95,'(强)      (弱)',fs=8,c='#555')

# Slots on panel
for sy,sc,sl in [(165,'#c62828','H1 动力顶层'),(145,'#e65100','H2 24V中层'),
                 (125,'#1565c0','H5 信号干线'),(105,'#2e7d32','H4 编码底层(封)')]:
    ax3.add_patch(mpatches.Rectangle((8,sy),80,12,fc=sc,ec=sc,lw=0,zorder=4,alpha=0.85))
    tx(ax3,130,sy+6,sl,fs=8,fw='bold',c=sc,ha='left')

# BR corner hole
ax3.add_patch(plt.Circle((88,50),12,fc='white',ec='#c62828',lw=2.5,zorder=5))
tx(ax3,88,50,'BR\n角孔',fs=7.5,fw='bold',c='#c62828')

# Cable conduit down to cable tray
for cy,col,lw_,desc in [
    (165,'#c62828',3,'动力 L1/L2/N/PE'),
    (145,'#e65100',2,'24V/信号'),
    (125,'#1565c0',2,'I/O信号'),
    (105,'#2e7d32',2,'编码/脉冲(封闭)'),
]:
    ax3.annotate('',xy=(180,50),xytext=(88,cy),
        arrowprops=dict(arrowstyle='->',color=col,lw=lw_,
                        connectionstyle='arc3,rad=0.25'))

# Cable tray horizontal
ax3.add_patch(mpatches.FancyBboxPatch((180,35),260,30,
    boxstyle='round,pad=2',fc='#fff9c4',ec='#f9a825',lw=2,zorder=3))
tx(ax3,310,50,'机身右侧  线缆桥架  (PVC槽 50×50)\n统一走向横梁左端',fs=9,c='#5d4037',fw='bold')

# Arrow to drag chain entry
ax3.annotate('',xy=(475,50),xytext=(440,50),
    arrowprops=dict(arrowstyle='->',color='#888',lw=2))

# Drag chain
ax3.add_patch(mpatches.FancyBboxPatch((475,30),80,40,
    boxstyle='round,pad=3',fc='#e8f5e9',ec='#2e7d32',lw=2,zorder=3))
tx(ax3,515,50,'X轴\n拖链槽\n65×38',fs=9,fw='bold',c='#1b5e20')

# Arrow to head
ax3.annotate('',xy=(590,50),xytext=(555,50),
    arrowprops=dict(arrowstyle='->',color='#e65100',lw=2))
ax3.add_patch(mpatches.FancyBboxPatch((590,30),28,40,
    boxstyle='round,pad=2',fc='#fff3e0',ec='#e65100',lw=2,zorder=3))
tx(ax3,604,50,'机\n头',fs=9,fw='bold',c='#e65100')

# Dimension annotations
ax3.annotate('',xy=(180,20),xytext=(88,20),arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax3,134,14,'竖管段约200mm\n(PVC波纹管保护)',fs=7.5,c='#555')
ax3.annotate('',xy=(440,18),xytext=(180,18),arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax3,310,12,'桥架段≈1200mm  固定扎带间距≤300mm',fs=8,c='#555')
ax3.annotate('',xy=(555,18),xytext=(475,18),arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax3,515,10,'拖链≈900mm',fs=7.5,c='#555')

# Notes row
for i,note in enumerate([
    '① BR角孔出线用 Ø25mm PVC波纹管保护，竖向下落约200mm后进桥架',
    '② 机身右侧桥架(50×50mm)水平固定在机架型材上，每300mm一个扎带+管夹',
    '③ 进拖链前套热缩管标色标号，动力线留弯曲余量≥1.5倍链宽',
    '④ 编码器/脉冲线在拖链内独立塑料扎带束，不得与动力线接触',
]):
    ax3.add_patch(mpatches.Rectangle((0,i*13+63),618,12,
        fc='#e8f5e9' if i%2==0 else 'white',ec='#c8e6c9',lw=0.5,zorder=2))
    tx(ax3,3,i*13+69,note,fs=8,c='#1b5e20',ha='left')

# ══════════════════════════════════════════════════════
# SUB-PLOT 4 (bottom-right) — 接线工序流程
# ══════════════════════════════════════════════════════
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor('white')
ax4.set_xlim(0,200); ax4.set_ylim(0,200)
ax4.axis('off')
ax4.set_title('接线施工顺序\n(Wiring Sequence)',fontsize=11,fontweight='bold',color='#1a237e',pad=8,**kw)

steps = [
    ('Step 1','安装导轨 R1/R2/R3\n固定PE铜排','#c62828'),
    ('Step 2','安装线槽 H1~H5\nV1~V6竖向槽','#e65100'),
    ('Step 3','安装元件到导轨\nQF0→KM→CB→KA','#f57c00'),
    ('Step 4','TC-6832\n背板固定','#2e7d32'),
    ('Step 5','敷设 H1 主动力线\n(红棕4mm²)','#c62828'),
    ('Step 6','敷设 H4 编码/脉冲线\n(封闭铝槽最先放)','#2e7d32'),
    ('Step 7','敷设 H2/H5 控制线\n(24V/信号)','#1565c0'),
    ('Step 8','端子排 XT-IN/OUT\n逐点接线打号管','#4527a0'),
    ('Step 9','操作台 XT-MP\n航插接线','#4527a0'),
    ('Step 10','PE 所有接地线\n汇入铜排','#2e7d32'),
    ('Step 11','上电前绝缘测试\n≥1MΩ/500V','#880e4f'),
    ('Step 12','上电调试 SF1→\nSVON→轴回原点','#1565c0'),
]

for i,(_sn,_desc,_col) in enumerate(steps):
    sy = 190 - i*15
    ax4.add_patch(mpatches.FancyBboxPatch((5,sy-6),190,13,
        boxstyle='round,pad=1',fc=_col,ec=_col,lw=0,zorder=3,alpha=0.15))
    ax4.add_patch(mpatches.FancyBboxPatch((5,sy-6),30,13,
        boxstyle='round,pad=1',fc=_col,ec=_col,lw=0,zorder=4))
    tx(ax4,20,sy+0.5,_sn,fs=7.5,fw='bold',c='white',z=5)
    tx(ax4,110,sy+0.5,_desc,fs=7,c='#111',z=5,ha='center')
    if i < len(steps)-1:
        ax4.annotate('',xy=(20,sy-7),xytext=(20,sy-5),
            arrowprops=dict(arrowstyle='->',color=_col,lw=1))

# ══════════════════════════════════════════════════════
# MAIN TITLE + TITLE BLOCK
# ══════════════════════════════════════════════════════
fig.text(0.5,0.965,'振动刀切割设备  |  第6页  走线路径图 + 拖链截面图 + 施工顺序',
    ha='center',va='center',fontsize=15,fontweight='bold',color='#1a237e',**kw)
fig.text(0.5,0.948,'Cable Routing & Cable Chain Cross-Section  |  Rev.B  2026-04  |  6 / 6',
    ha='center',va='center',fontsize=9,color='#555',**kw)

plt.savefig('output/page6_routing.png',dpi=165,bbox_inches='tight',
            facecolor='white',edgecolor='none')
with open('output/page6_routing.png.meta.json','w') as f:
    json.dump({"caption":"第6页  走线路径图 + X轴拖链截面A-A + 侧视走线路径 + 接线施工顺序",
               "description":"包含机身俯视走线总览、65×38mm拖链截面三层分隔、配电板BR角孔→桥架→拖链侧视路径图、12步接线施工顺序"}, f)
plt.close()
print(f"page6 OK: {os.path.getsize('output/page6_routing.png')//1024} KB")
