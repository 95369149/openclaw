import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import os, json

for candidate in [
    '/System/Library/Fonts/PingFang.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/Library/Fonts/Arial Unicode MS.ttf',
]:
    if os.path.exists(candidate):
        prop = fm.FontProperties(fname=candidate)
        break
else:
    prop = fm.FontProperties()
kw = dict(fontproperties=prop)

def tx(ax,x,y,s,fs=7.5,c='#111',ha='center',va='center',fw='normal',rot=0,z=9):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=c,fontweight=fw,
            rotation=rot,zorder=z,**kw,
            path_effects=[pe.withStroke(linewidth=1.5,foreground='white')])

def rect(ax,x,y,w,h,fc='white',ec='#333',lw=1.5,z=4,alpha=1.0):
    ax.add_patch(mpatches.FancyBboxPatch((x,y),w,h,
        boxstyle='round,pad=1.5',fc=fc,ec=ec,lw=lw,zorder=z,alpha=alpha))

def trough(ax,x1,x2,y,h,lbl,fc,ec,fs=6):
    ax.add_patch(mpatches.Rectangle((x1,y),x2-x1,h,fc=fc,ec=ec,lw=1.5,zorder=3))
    tx(ax,(x1+x2)/2,y+h/2,lbl,fs=fs,c='white',fw='bold',z=5)

def rail(ax,x1,x2,y):
    ax.add_patch(mpatches.Rectangle((x1,y-2),x2-x1,5,fc='#bdbdbd',ec='#555',lw=1,zorder=6))

def dev(ax,x,y,w,h,lbl,sub='',fc='white',ec='#333',fs=7,sfs=5.5):
    rect(ax,x,y,w,h,fc=fc,ec=ec,lw=1.5,z=5)
    if sub:
        tx(ax,x+w/2,y+h*0.65,lbl,fs=fs,fw='bold',c=ec,z=7)
        tx(ax,x+w/2,y+h*0.28,sub,fs=sfs,c='#333',z=7)
    else:
        tx(ax,x+w/2,y+h/2,lbl,fs=fs,fw='bold',c=ec,z=7)

def zone_bg(ax,x1,x2,y1,y2,fc,ec):
    ax.add_patch(mpatches.Rectangle((x1,y1),x2-x1,y2-y1,
        fc=fc,ec=ec,lw=2,zorder=1,alpha=0.15))

def lv(ax,x,y1,y2,c='#aaa',lw=1,ls='--',z=2):
    ax.plot([x,x],[y1,y2],color=c,lw=lw,ls=ls,zorder=z)

# ══════════════════════════════════════════════════════
# 画布设置
# W=1650mm（配电板宽），H=600（图纸高，含线槽+器件+端子排）
# Y轴从下到上：
#   y=0   底边
#   y=20  H3信号线槽（30×30）
#   y=55  H2控制线槽（50×50）
#   y=110 端子排导轨RL-4
#   y=115 端子排（高55mm）→ y=170
#   y=185 PE铜排
#   y=210 器件下层导轨RL-2（伺服驱动器，高150mm）→ y=360
#   y=370 H4编码器线槽（40×25）
#   y=400 器件上层导轨RL-1（断路器/接触器，高65mm）→ y=465
#   y=475 H5伺服动力线槽（50×50）
#   y=530 H1动力线槽（50×50）
#   y=585 顶边
# ══════════════════════════════════════════════════════
fig = plt.figure(figsize=(36,20))
fig.patch.set_facecolor('white')
gs = gridspec.GridSpec(2,1,figure=fig,height_ratios=[2.5,1],
                       hspace=0.08,left=0.02,right=0.98,top=0.96,bottom=0.03)

ax = fig.add_subplot(gs[0])
ax.set_facecolor('white'); ax.axis('off')
W,H = 1650,590
ax.set_xlim(-40,W+60); ax.set_ylim(-10,H+60); ax.set_aspect('equal')

# 标题
tx(ax,W/2,H+45,'振动刀切割设备  配电板布局图  1650×350×300mm  Rev.C  2026-04-06',
   fs=13,fw='bold',c='#1a237e',z=10)
tx(ax,W/2,H+30,'A区:主回路  B区:伺服驱动  C区:24V控制  D区:TC-6832+端子排  |  强弱分离',
   fs=8,c='#555',z=10)

# 配电板外框
ax.add_patch(mpatches.Rectangle((0,0),W,H,fc='none',ec='#333',lw=2.5,zorder=0))

# 区域背景
zone_bg(ax,   0, 395,  0, H, '#e3f2fd','#1565c0')
zone_bg(ax, 400, 920,  0, H, '#fff3e0','#e65100')
zone_bg(ax, 925,1340,  0, H, '#e8f5e9','#2e7d32')
zone_bg(ax,1345,1650,  0, H, '#ede7f6','#4527a0')

# 区域标题
for x1,x2,lbl,c in [
    (0,395,'A区  主回路 / 滤波\n380V · 220V AC','#1565c0'),
    (400,920,'B区  伺服驱动\n400W×3 + 100W×2','#e65100'),
    (925,1340,'C区  24V控制\n电源 / 安全 / 继电器','#2e7d32'),
    (1345,1650,'D区  TC-6832\n控制器 + 端子排','#4527a0'),
]:
    tx(ax,(x1+x2)/2,H+14,lbl,fs=8,fw='bold',c=c,z=8)

# 区域分隔线
for xd,c in [(397,'#1565c0'),(922,'#e65100'),(1342,'#2e7d32')]:
    lv(ax,xd,0,H,c=c,lw=2,ls='--',z=2)

# ══ 线槽（从上到下）══
# H1 顶部动力线槽（红，y=530~580）
trough(ax,0,920,530,50,'H1  AC动力线槽  50×50mm  红色  L1/L2/N → QF0 → KM1/KM2 → QF3~QF8  4mm²',
       '#c62828','#8b0000',fs=6.5)
# H5 伺服动力（橙，y=475~525）
trough(ax,400,920,475,50,'H5  伺服动力线槽  50×50mm  橙色  220VAC → SRV1~5  1.5mm²',
       '#e65100','#bf360c',fs=6.5)
# H4 铝合金封闭（黑，y=370~395）
trough(ax,0,1340,370,25,'H4  铝合金封闭线槽  40×25mm  编码器/脉冲专用  全程屏蔽  ASTP',
       '#424242','#212121',fs=6)
# H2 控制线槽（灰，y=55~105）
trough(ax,0,1650,55,50,'H2  DC24V控制线槽  50×50mm  灰色  L≈1200mm  ← 与H1间距≥200mm',
       '#607d8b','#37474f',fs=6.5)
# H3 信号线槽（浅灰，y=10~45）
trough(ax,0,1650,10,40,'H3  信号线槽  30×30mm  灰色  I/O·信号·辅助  0.75mm²',
       '#78909c','#455a64',fs=6.5)

# ══ 导轨 ══
# RL-1 上层（y=400，断路器/接触器）
for x1,x2 in [(5,390),(405,915),(930,1335)]:
    rail(ax,x1,x2,400)
    tx(ax,(x1+x2)/2,390,'── C45 DIN导轨 ──',fs=5,c='#888',z=4)

# RL-2 中层（y=210，伺服驱动器）
for x1,x2 in [(405,760)]:
    rail(ax,x1,x2,210)
    tx(ax,(x1+x2)/2,200,'── C45 DIN导轨 ──',fs=5,c='#888',z=4)

# RL-3 D区（y=400，TC-6832）
rail(ax,1350,1640,400)

# RL-4 端子排导轨（y=115）
rail(ax,5,1640,115)
tx(ax,825,105,'── 端子排导轨 C45 ──',fs=5,c='#888',z=4)

# ══ A区器件（上层导轨，y=400，高65mm → y=400~465）══
# RCD:72  QF0:105  KM1:57  KM2:45  QF2:18  EMI1:50
A_devs = [
    (8,   72, 65, 'RCD\n漏保',     '4P 125A\n30mA',            '#e3f2fd','#1565c0'),
    (85, 105, 65, 'QF0\n主断路器', 'NSX100F\n3P+N 63A',        '#ffebee','#c62828'),
    (195, 57, 65, 'KM1\n主接触器', 'CJX2-1810\nAC220V\nSB-KEY','#fff3e0','#e65100'),
    (257, 45, 65, 'KM2\n风机',     'NC1-12\nDC24V\n←OUT2',     '#fff3e0','#e65100'),
    (307, 18, 65, 'QF2',           'iC65N\n1P 20A',             '#ffebee','#c62828'),
    (330, 50, 65, 'EMI1\n滤波器',  'DOREXS\nDEA4-20A\n20A',    '#e8f5e9','#2e7d32'),
]
for x,w,h,lbl,sub,fc,ec in A_devs:
    dev(ax,x,400,w,h,lbl,sub,fc=fc,ec=ec)

# ══ B区断路器（上层导轨，y=400，高65mm）══
# QF3~QF8 各18mm宽
for i,(lbl,sub) in enumerate([('QF3\n6A','SRV1'),('QF4\n6A','SRV2'),('QF5\n6A','SRV3'),
                                ('QF6\n4A','SRV4'),('QF7\n4A','SRV5'),('QF8\n6A','PS1')]):
    dev(ax,410+i*22,400,18,65,lbl,sub,fc='#fff8e1',ec='#c62828',fs=6,sfs=5)

# ══ B区伺服驱动器（中层导轨，y=210）══
# DS2-20P4: 70×150mm  DS2-10P4: 55×130mm
srv_devs = [
    (410, 70,150,'SRV1\nDS2-20P4','400W  X轴\n前后轴1','#dce8fb','#1565c0'),
    (485, 70,150,'SRV2\nDS2-20P4','400W  Y轴\n前后轴2','#dce8fb','#1565c0'),
    (560, 70,150,'SRV3\nDS2-20P4','400W  UD1\n左右轴', '#dce8fb','#1565c0'),
    (640, 55,130,'SRV4\nDS2-10P4','100W  Z轴\n升降轴', '#d5f0db','#2e7d32'),
    (700, 55,130,'SRV5\nDS2-10P4','100W  U轴\n旋转轴', '#d5f0db','#2e7d32'),
]
for x,w,h,lbl,sub,fc,ec in srv_devs:
    dev(ax,x,210,w,h,lbl,sub,fc=fc,ec=ec,fs=7,sfs=5.5)
    # 虚线连接断路器
    lv(ax,x+w/2,400,210+h,'#bbb',lw=0.8,ls=':',z=3)
    # CN标注
    tx(ax,x+w/2,207,'CN1↓',fs=4.5,c='#555',z=5)

# ══ C区器件（上层导轨，y=400）══
# PS1: 99×65mm
dev(ax,930,400,99,65,'PS1\nS-250-24','24V/10A 250W\n明纬',fc='#fff3e0',ec='#e65100',fs=7,sfs=5.5)

# CB1~CB4: 各18mm
for i,(lbl,amp,func) in enumerate([('CB1','2A','TC'),('CB2','3A','阀'),
                                     ('CB3','1A','信号'),('CB4','2A','SVON')]):
    dev(ax,1035+i*22,400,18,65,lbl+'\n'+amp,func,fc='#e8f5e9',ec='#2e7d32',fs=6,sfs=5)

# SF1: 45×94mm（中层，y=210）
dev(ax,930,210,45,150,'SF1\n安全继电器','Pilz PNOZ X2P\nDC24V 2NO\n双通道急停\nEDM监测',
    fc='#fce4ec',ec='#880e4f',fs=6.5,sfs=5.5)

# KA继电器组: 各27×90mm（中层，y=210）
for i,(lbl,func) in enumerate([('KA-SVON','伺服使能'),('KA-A1','报警1'),('KA-A2','报警2'),
                                 ('KA-A3','报警3'),('KA-A4','报警4'),('KA-A5','报警5')]):
    dev(ax,985+i*30,210,27,130,lbl,func+'\n工易联\nDC24V',fc='#e8f5e9',ec='#388e3c',fs=5.5,sfs=4.5)

# ══ D区：TC-6832（252×170mm，安装在上层导轨，y=400）══
TC_X,TC_Y,TC_W,TC_H = 1355,215,252,250
rect(ax,TC_X,TC_Y,TC_W,TC_H,fc='#ede7f6',ec='#4527a0',lw=2.5,z=5)
tx(ax,TC_X+TC_W/2,TC_Y+TC_H*0.80,'TC-6832',fs=13,fw='bold',c='#4527a0',z=7)
tx(ax,TC_X+TC_W/2,TC_Y+TC_H*0.65,'乾诚 TROCEN',fs=8,c='#7e57c2',z=7)
tx(ax,TC_X+TC_W/2,TC_Y+TC_H*0.50,'5轴 / IN8 / OUT32',fs=7.5,c='#4527a0',z=7)
tx(ax,TC_X+TC_W/2,TC_Y+TC_H*0.36,'USB  /  以太网',fs=7,c='#555',z=7)
tx(ax,TC_X+TC_W/2,TC_Y+TC_H*0.20,'252 × 170 mm',fs=6.5,c='#999',z=7)

# 顶部IN端子条
ax.add_patch(mpatches.Rectangle((TC_X+5,TC_Y+TC_H),TC_W-10,16,
    fc='#bbdefb',ec='#1565c0',lw=1.2,zorder=6))
tx(ax,TC_X+TC_W/2,TC_Y+TC_H+8,'24V  GND  IN1 ~ IN8',fs=6,c='#0d47a1',z=7)

# 底部OUT端子条
ax.add_patch(mpatches.Rectangle((TC_X+5,TC_Y-16),TC_W-10,16,
    fc='#fff3e0',ec='#e65100',lw=1.2,zorder=6))
tx(ax,TC_X+TC_W/2,TC_Y-8,'OUT1 ~ OUT32  GND',fs=6,c='#bf360c',z=7)

# 左侧CN1/CN2
for cy,lbl in [(TC_Y+TC_H*0.72,'CN2\n编码器'),(TC_Y+TC_H*0.42,'CN1\n脉冲')]:
    ax.add_patch(mpatches.FancyBboxPatch((TC_X-32,cy-16),30,32,
        boxstyle='round,pad=1',fc='#424242',ec='#212121',lw=1.2,zorder=6))
    tx(ax,TC_X-17,cy,lbl,fs=5.5,c='white',fw='bold',z=7)

# 右侧5轴接口
for i,lbl in enumerate(['X轴','Y轴','UD1','Z轴','U轴']):
    ay = TC_Y+TC_H*0.88-i*46
    ax.add_patch(mpatches.FancyBboxPatch((TC_X+TC_W+2,ay-14),32,28,
        boxstyle='round,pad=1',fc='#e8f5e9',ec='#2e7d32',lw=0.8,zorder=6))
    tx(ax,TC_X+TC_W+18,ay,lbl+'\nPUL/DIR',fs=5,c='#1b5e20',z=7)

# ══ 端子排（底部导轨，y=115，高55mm → y=115~170）══
# XT-IN: 20节×6mm=120mm
# XT-OUT: 20节×6mm=120mm
# XT-PE: 8节×8mm=64mm
# XT-MP: 50mm
# PE铜排: 60mm
term_devs = [
    (5,   120,55,'XT-IN\n蓝色', 'UK-2.5×20节\n数字输入',  '#e3f2fd','#1565c0'),
    (130, 120,55,'XT-OUT\n橙色','UK-2.5×20节\n数字输出',  '#fff3e0','#e65100'),
    (255,  64,55,'XT-PE\n黄绿', 'UK-6/PE×8节\n接地',      '#e8f5e9','#2e7d32'),
    (325,  55,55,'XT-MP\n航插', '24芯\n操作台',            '#ede7f6','#4527a0'),
    (390,  65,55,'PE铜排\n25×4','铝合金\n星形接地',        '#fffde7','#f57f17'),
]
for x,w,h,lbl,sub,fc,ec in term_devs:
    dev(ax,x,115,w,h,lbl,sub,fc=fc,ec=ec,fs=6.5,sfs=5.5)

# ══ 尺寸标注 ══
ax.annotate('',xy=(W,-8),xytext=(0,-8),
    arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax,W/2,-14,'1650 mm',fs=8,fw='bold',c='#333')
ax.annotate('',xy=(-28,H),xytext=(-28,0),
    arrowprops=dict(arrowstyle='<->',color='#333',lw=1.2))
tx(ax,-22,H/2,'350 mm',fs=7,fw='bold',c='#333',rot=90)

# ══ 强弱分离说明框 ══
ax.add_patch(mpatches.FancyBboxPatch((0,H+2),W,18,
    boxstyle='round,pad=2',fc='#e8f5e9',ec='#2e7d32',lw=1.2,zorder=6))
tx(ax,W/2,H+11,
   '【强弱分离】A区(380V/220V) ←隔断→ B区(220V伺服) ←隔断→ C区(DC24V)  |  '
   'H4铝合金封闭线槽全程屏蔽  |  H1动力与H2控制间距≥200mm  |  KM1线圈AC220V由SB-KEY硬接线',
   fs=6.5,fw='bold',c='#1b5e20',z=7)

# ══════════════════════════════════════════════════════
# 下半：I/O对照表
# ══════════════════════════════════════════════════════
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('white'); ax2.axis('off')
ax2.set_xlim(0,1000); ax2.set_ylim(0,230)

tx(ax2,500,220,'乾诚 TC-6832  |  I/O接线对照表',fs=11,fw='bold',c='#1a237e',z=10)

col_specs = [
    (0,   240,'#c62828','#ffcdd2','轴脉冲输出（PUL±/DIR±）'),
    (250, 490,'#1565c0','#bbdefb','数字输入 IN1~IN8'),
    (500, 750,'#2e7d32','#c8e6c9','数字输出 OUT'),
    (760,1000,'#6a1b9a','#e1bee7','电源/其他'),
]
pulse_rows = [
    'X → SRV1 前后轴1（400W）',
    'Y → SRV2 前后轴2（400W）',
    'UD1 → SRV3 左右轴（400W）',
    'Z → SRV4 升降轴（100W）',
    'U → SRV5 旋转轴（100W）',
]
in_rows = [
    'IN1 → 急停反馈 SF1辅助Y1',
    'IN2 → 前梁对射 RX1 NPN',
    'IN3 → 后梁对射 RX2 NPN',
    'IN4 → 四角暂停 SB-P1~P4',
    'IN5 → X轴原点/限位',
    'IN6 → Y轴原点/限位',
    'IN7 → Z轴原点/限位',
    'IN8 → U轴原点/限位',
]
out_rows = [
    'OUT1 → 已释放（SB-KEY硬接线）',
    'OUT2 → KM2 风机接触器',
    'OUT3 → VFD-FWD 变频器正转',
    'OUT4 → VFD-RST 变频器复位',
    'OUT5~9 → YV1~5 台面电磁阀',
    'OUT10 → YV6 反吹阀',
    'OUT11 → KA-SVON 伺服使能',
    'OUT12/13/14 → HL-R/Y/G 三色灯',
    'OUT15 → YV7 压料阀',
    'OUT16 → YV8 画笔阀（选配）',
]
other_rows = [
    '220VAC → EMI1→QF3~8→SRV1~5',
    '24V → CB1~4→TC/KA/阀/SVON',
    '急停SB-KEY→KM1(AC220V硬接线)',
    '急停SB-ES→SF1→SVON(DC24V)',
    '红光定位→CB3 24V直接供电',
    '操作台→XT-MP 24芯航插',
]
all_cols = [pulse_rows,in_rows,out_rows,other_rows]

for ci,(x1,x2,hc,fc,title) in enumerate(col_specs):
    cw = x2-x1
    ax2.add_patch(mpatches.FancyBboxPatch((x1+2,205),cw-4,14,
        boxstyle='round,pad=1',fc=hc,ec=hc,lw=0,zorder=4))
    tx(ax2,x1+cw/2,212,title,fs=7.5,fw='bold',c='white',z=5)
    for ri,row in enumerate(all_cols[ci]):
        ry = 198-ri*22
        bg = fc if ri%2==0 else 'white'
        ax2.add_patch(mpatches.FancyBboxPatch((x1+2,ry-9),cw-4,18,
            boxstyle='round,pad=1',fc=bg,ec=hc,lw=0.5,zorder=3))
        tx(ax2,x1+cw/2,ry,row,fs=6,c='#222',z=5)

# 标题栏
fig.add_axes([0,0,1,0.025]).axis('off')
ax3 = fig.axes[-1]
ax3.set_xlim(0,1); ax3.set_ylim(0,1)
ax3.add_patch(mpatches.Rectangle((0,0),1,1,fc='#f5f5f5',ec='#333',lw=0,zorder=10))
for xd,lbl in [(0,'振动刀切割设备'),(0.18,'配电板布局图  Panel Layout'),
               (0.55,'Rev.C'),(0.7,'2026-04-06'),(0.85,'7 / 7')]:
    ax3.text(xd+0.005,0.6,lbl,ha='left',va='center',fontsize=8,
             fontweight='bold' if xd<0.18 else 'normal',color='#111',**kw)
ax3.add_patch(mpatches.Rectangle((0,0),1,0.3,fc='#e8eaf6',ec='#3949ab',lw=0,zorder=10))
ax3.text(0.5,0.15,
    'KM1线圈AC220V由SB-KEY带锁急停硬接线  |  KA继电器6只工易联DC24V  |  '
    'H4铝合金封闭线槽编码器专用  |  端子排集中底部导轨便于现场接线',
    ha='center',va='center',fontsize=7,color='#1a237e',**kw)

os.makedirs('output',exist_ok=True)
plt.savefig('output/page7_panel_layout.png',dpi=165,bbox_inches='tight',
            facecolor='white',edgecolor='none')
with open('output/page7_panel_layout.png.meta.json','w') as f:
    json.dump({"caption":"第7页 配电板布局图+I/O对照表 Rev.C"},f)
plt.close()
print("page7_panel_layout done")
