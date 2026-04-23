
# Page 2 — 控制回路图 (Control/24V Circuit)  梯形图风格
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import os, json

prop = fm.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
fig, ax = plt.subplots(figsize=(28, 22))
fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.axis('off')
kw = dict(fontproperties=prop)

def lh(x1,x2,y,c='#111',lw=1.5,ls='-',z=5): ax.plot([x1,x2],[y,y],c,lw=lw,ls=ls,zorder=z)
def lv(x,y1,y2,c='#111',lw=1.5,ls='-',z=5): ax.plot([x,x],[y1,y2],c,lw=lw,ls=ls,zorder=z)
def jn(x,y,c='#111',r=2.5): ax.add_patch(plt.Circle((x,y),r,fc=c,ec=c,zorder=8))
def tx(x,y,s,fs=7.5,c='#111',ha='center',va='center',fw='normal',rot=0,z=9):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=c,fontweight=fw,rotation=rot,zorder=z,**kw,
            path_effects=[pe.withStroke(linewidth=1.2,foreground='white')])
def wn(x,y,s):
    ax.add_patch(mpatches.FancyBboxPatch((x-12,y-4),24,8,boxstyle='round,pad=1',
        fc='#fffde7',ec='#f9a825',lw=0.6,zorder=7))
    tx(x,y,s,fs=6,c='#5d4037',z=8)
def coil(x,y,lbl,col='#c62828'):
    ax.add_patch(plt.Circle((x,y),9,fc='white',ec=col,lw=1.8,zorder=5))
    tx(x,y,lbl,fs=6.5,fw='bold',c=col)
def coil_rect(x,y,lbl,sub='',col='#1565c0',w=32,h=18):
    ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='square,pad=0',
        fc='white',ec=col,lw=1.8,zorder=5))
    tx(x,y+3,lbl,fs=7,fw='bold',c=col)
    tx(x,y-4,sub,fs=5.5,c=col)
def nc_contact(x,y,lbl='',col='#333'):
    ax.plot([x-8,x+8],[y,y],col,lw=1.8,zorder=5)
    ax.plot([x-8,x+8],[y+5,y+5],col,lw=1.2,zorder=5)
    ax.plot([x,x],[y-10,y],col,lw=1.5,zorder=5)
    ax.plot([x,x],[y+5,y+15],col,lw=1.5,zorder=5)
    ax.plot([x-7,x+7],[y+12,y+12],col,lw=1,ls='--',zorder=5)
    tx(x,y+22,lbl,fs=6.5,c=col)
def no_contact(x,y,lbl='',col='#333'):
    ax.plot([x-8,x+8],[y,y],col,lw=1.8,zorder=5)
    ax.plot([x-8,x+8],[y+8,y+8],col,lw=1.2,zorder=5)
    ax.plot([x,x],[y-10,y],col,lw=1.5,zorder=5)
    ax.plot([x,x],[y+8,y+15],col,lw=1.5,zorder=5)
    tx(x,y+22,lbl,fs=6.5,c=col)

# ══ Power rails ═══════════════════════
LRAIL = 40   # +24V left rail
RRAIL = 560  # 0V right rail
RTOP  = 820
RBOT  = 30

lv(LRAIL,RBOT,RTOP,'#c62828',lw=4,z=3)
lv(RRAIL,RBOT,RTOP,'#1565c0',lw=4,z=3)
tx(LRAIL,RTOP+12,'+24V  DC',fs=10,fw='bold',c='#c62828')
tx(RRAIL,RTOP+12,'0V  GND',fs=10,fw='bold',c='#1565c0')

# CB breakers on +24V rail
for i,(cy,lbl) in enumerate([(790,'CB1 2A\nPLC'),(770,'CB2 3A\n阀/驱'),(750,'CB3 1A\n信号'),(730,'CB4 2A\nSVON')]):
    ax.add_patch(mpatches.FancyBboxPatch((LRAIL-8,cy-8),16,16,
        boxstyle='square,pad=0',fc='#fff9c4',ec='#e65100',lw=1.2,zorder=4))
    tx(LRAIL,cy,lbl,fs=6,fw='bold',c='#e65100')

# ══ RUNG definitions ══════════════════
# Each rung: y, description, contacts left→right, then coil on right
# Format: draw manually for precision

RUNGS = [
    # (y_rung, rung_number, description)
    (700, 'R01', '主接触器KM1 控制回路'),
    (660, 'R02', '风机接触器KM2 控制回路'),
    (620, 'R03', '急停安全回路 SF1'),
    (570, 'R04', 'SF1 复位指示'),
    (530, 'R05', '伺服使能 SVON'),
    (490, 'R06', '前梁对射 IN2'),
    (450, 'R07', '后梁对射 IN3'),
    (400, 'R08', '变频器正转 OUT3'),
    (360, 'R09', 'YV1 台面阀1'),
    (320, 'R10', 'YV2 台面阀2'),
    (280, 'R11', 'YV3~YV5 台面阀3~5'),
    (240, 'R12', 'YV6 反吹阀'),
    (190, 'R13', '报警灯/蜂鸣器'),
    (150, 'R14', '24V电源指示'),
]

for ry,rnum,rdesc in RUNGS:
    lh(LRAIL,RRAIL,ry,'#eee',lw=0.4,ls='-',z=2)
    tx(LRAIL-28,ry,rnum,fs=7,c='#aaa',ha='right')
    tx((LRAIL+RRAIL)/2,ry+14,rdesc,fs=7.5,c='#444',fw='bold')

# ══ RUNG R01 — KM1 主接触器 ════════════
RY = 700
lh(LRAIL,100,RY,'#c62828',lw=1.8)
no_contact(100,RY-12,'TC\nOUT1','#c62828')  # TC OUT1
lh(108,175,RY,'#c62828',lw=1.8)
no_contact(175,RY-12,'SF1\n13-14(NO)','#880e4f')  # SF1 NO
lh(183,250,RY,'#c62828',lw=1.8)
nc_contact(250,RY-12,'KM2\nNC(互锁)','#e65100')  # KM2 NC interlock
lh(258,RRAIL-40,RY,'#c62828',lw=1.8)
coil_rect(RRAIL-20,RY,'KM1\n线圈','NC1-25\nDC24V','#c62828')
lh(RRAIL-4,RRAIL,RY,'#1565c0',lw=1.8)
wn(175,RY-36,'W-O1-KM1')
# Self-holding contact
lh(155,185,RY-30,'#c62828',lw=1.2,ls='--')
no_contact(170,RY-42,'KM1\n自保(NO)','#c62828')
tx(170,RY-70,'自保持回路',fs=6.5,c='#888')

# ══ RUNG R02 — KM2 风机接触器 ════════
RY = 660
lh(LRAIL,100,RY,'#c62828',lw=1.8)
no_contact(100,RY-12,'TC\nOUT2','#e65100')
lh(108,175,RY,'#c62828',lw=1.8)
nc_contact(175,RY-12,'KM1\nNC(互锁)','#c62828')
lh(183,RRAIL-40,RY,'#c62828',lw=1.8)
coil_rect(RRAIL-20,RY,'KM2\n线圈','NC1-12\nDC24V','#e65100')
lh(RRAIL-4,RRAIL,RY,'#1565c0',lw=1.8)
wn(140,RY-36,'W-O2-KM2')

# ══ RUNG R03 — SF1 急停安全回路 ════════
RY = 620
lh(LRAIL,80,RY,'#880e4f',lw=1.8)
nc_contact(80,RY-12,'SB-ES\nA通道 NC','#880e4f')
lh(88,150,RY,'#880e4f',lw=1.8)
nc_contact(150,RY-12,'SB-ES\nB通道 NC','#880e4f')
lh(158,230,RY,'#880e4f',lw=1.8)
# SF1 box
ax.add_patch(mpatches.FancyBboxPatch((230,RY-18),80,36,boxstyle='round,pad=2',
    fc='#fce4ec',ec='#880e4f',lw=2,zorder=5))
tx(270,RY+6,'SF1 A1/A2',fs=7.5,fw='bold',c='#880e4f')
tx(270,RY-6,'Pilz PNOZ X2P',fs=7,c='#880e4f')
lh(310,RRAIL,RY,'#1565c0',lw=1.8)
wn(190,RY-36,'W-ES-A / W-ES-B')
# EDM feedback
lh(LRAIL,80,RY-40,'#880e4f',lw=1.2,ls='--')
nc_contact(80,RY-52,'KM1 EDM\n(NC反馈)','#c62828')
lh(88,230,RY-40,'#880e4f',lw=1.2,ls='--')
lv(230,RY-40,RY-18,'#880e4f',lw=1.2,ls='--')
tx(155,RY-70,'EDM监测回路(虚线)',fs=6.5,c='#888')

# ══ RUNG R05 — SVON 伺服使能 ══════════
RY = 530
lh(LRAIL,100,RY,'#c62828',lw=1.8)
no_contact(100,RY-12,'TC\nOUT11','#2e7d32')
lh(108,175,RY,'#c62828',lw=1.8)
no_contact(175,RY-12,'SF1 23-24\nNO辅助','#880e4f')
lh(183,250,RY,'#c62828',lw=1.8)
no_contact(250,RY-12,'KM1 NO\n辅助触点','#c62828')
lh(258,RRAIL-40,RY,'#c62828',lw=1.8)
coil_rect(RRAIL-20,RY,'SVON\n线圈','KA G2R\nDC24V','#2e7d32')
lh(RRAIL-4,RRAIL,RY,'#1565c0',lw=1.8)
tx(RRAIL-20,RY-28,'触点→SRV1~5 SON/STO',fs=6.5,c='#555')
wn(175,RY-36,'W-O11-SVON')

# ══ RUNG R06/R07 — 对射输入 ══════════
for RY,lbl,wlbl in [(490,'RX1前梁对射\nIN2','W-IN2-RX1'),(450,'RX2后梁对射\nIN3','W-IN2-RX2')]:
    lh(LRAIL,100,RY,'#1565c0',lw=1.8)
    ax.add_patch(mpatches.FancyBboxPatch((100,RY-14),80,28,boxstyle='round,pad=2',
        fc='#e3f2fd',ec='#1565c0',lw=1.3,zorder=4))
    tx(140,RY,lbl,fs=7.5,c='#0d47a1',fw='bold')
    lh(180,230,RY,'#1565c0',lw=1.8)
    ax.add_patch(mpatches.FancyBboxPatch((230,RY-10),60,20,boxstyle='round,pad=2',
        fc='#e3f2fd',ec='#1565c0',lw=1.2,zorder=4))
    tx(260,RY,'TC-6832\nIN2/IN3',fs=7,c='#0d47a1')
    lh(290,RRAIL,RY,'#1565c0',lw=1.8)
    wn(215,RY-18,wlbl)

# ══ RUNG R08 — VFD正转 ══════════════
RY = 400
lh(LRAIL,100,RY,'#c62828',lw=1.8)
no_contact(100,RY-12,'TC\nOUT3','#e65100')
lh(108,200,RY,'#c62828',lw=1.8)
ax.add_patch(mpatches.FancyBboxPatch((200,RY-16),90,32,boxstyle='round,pad=2',
    fc='#e8f5e9',ec='#2e7d32',lw=1.5,zorder=4))
tx(245,RY,'VFD DI1\n汇川MD310\n正转指令',fs=7.5,c='#1b5e20',fw='bold')
lh(290,RRAIL,RY,'#1565c0',lw=1.8)
wn(155,RY-20,'W-O3-VFD-FWD')

# ══ RUNGS R09~R12 — 电磁阀 YV1~YV6 ══
for i,(RY,yn,out) in enumerate([(360,'YV1 台面1','OUT5'),
                                 (320,'YV2 台面2','OUT6'),
                                 (280,'YV3~5 台面3~5','OUT7~9'),
                                 (240,'YV6 反吹','OUT10')]):
    lh(LRAIL,100,RY,'#c62828',lw=1.8)
    no_contact(100,RY-12,f'TC\n{out}','#2e7d32')
    lh(108,220,RY,'#c62828',lw=1.8)
    ax.add_patch(mpatches.FancyBboxPatch((220,RY-14),90,28,boxstyle='round,pad=2',
        fc='#e8f5e9',ec='#2e7d32',lw=1.5,zorder=4))
    tx(265,RY,f'{yn}\n电磁阀 DC24V',fs=7.5,c='#1b5e20',fw='bold')
    lh(310,RRAIL-40,RY,'#c62828',lw=1.8)
    # diode symbol
    ax.add_patch(mpatches.Polygon([[RRAIL-40,RY-5],[RRAIL-40,RY+5],[RRAIL-28,RY]],
        fc='#ffeb3b',ec='#f57f17',lw=1.2,zorder=5))
    lh(RRAIL-28,RRAIL,RY,'#1565c0',lw=1.8)
    tx(RRAIL-34,RY-12,'D续流\n1N4007',fs=6,c='#f57f17')
    wn(165,RY-20,f'W-O{i+5}-{yn[:3]}')

# ══ RUNG R13 — 报警灯/蜂鸣器 ══════════
RY = 190
lh(LRAIL,100,RY,'#c62828',lw=1.8)
no_contact(100,RY-12,'TC\nOUT12','#c62828')
lh(108,180,RY,'#c62828',lw=1.8)
ax.add_patch(mpatches.FancyBboxPatch((180,RY-12),60,24,boxstyle='round,pad=1',
    fc='#ffcdd2',ec='#c62828',lw=1.3,zorder=4))
tx(210,RY,'HL-R 报警灯\nDC24V',fs=7,c='#b71c1c')
lh(240,RRAIL,RY,'#1565c0',lw=1.8)

# ══ RUNG R14 — 电源指示灯 ════════════
RY = 150
lh(LRAIL,120,RY,'#c62828',lw=1.8)
ax.add_patch(mpatches.FancyBboxPatch((120,RY-12),80,24,boxstyle='round,pad=1',
    fc='#e8f5e9',ec='#2e7d32',lw=1.3,zorder=4))
tx(160,RY,'HL-PWR 电源指示\n上电常亮 DC24V',fs=7.5,c='#1b5e20',fw='bold')
lh(200,RRAIL,RY,'#1565c0',lw=1.8)

# ══ NOTES block ══════════════════════
ax.add_patch(mpatches.FancyBboxPatch((LRAIL,90),RRAIL-LRAIL,52,
    boxstyle='round,pad=2',fc='#fffde7',ec='#f9a825',lw=1,zorder=4))
notes = [
    '控制电路说明:  ① 全部控制线圈电压 DC24V，由PS1 S-250-24 经CB1~CB4分路供电',
    '② KM1与KM2 互锁：KM1线圈串KM2 NC辅助触点，KM2线圈串KM1 NC辅助触点，防止同时得电',
    '③ 所有感性负载（KM1/KM2线圈、KA线圈、YV1~YV6阀）并联续流二极管1N4007（阳极→0V，阴极→+24V）',
    '④ SF1 安全继电器硬接线急停，优先级高于TC-6832软件控制，断电时KM1/SVON同时断开',
]
for i,n in enumerate(notes):
    tx(LRAIL+4,136-i*13,n,fs=7.2,c='#5d4037',ha='left')

# ══ TITLE BLOCK ══════════════════════
ax.add_patch(mpatches.Rectangle((0,0),600,36,fc='#f5f5f5',ec='#333',lw=1.2,zorder=10))
ax.plot([0,600],[24,24],'#333',lw=0.8,zorder=11)
for xd,lbl in [(0,'振动刀切割设备'),(160,'控制回路图  Control Circuit'),(360,'Rev.B'),(460,'2026-04'),(530,'2 / 6')]:
    tx(xd+4,30,lbl,fs=7.5,fw='bold' if xd<160 else 'normal',c='#111',ha='left')
for xd in [160,360,460,530,600]:
    ax.plot([xd,xd],[0,36],'#333',lw=0.8,zorder=11)
ax.add_patch(mpatches.Rectangle((0,0),600,12,fc='#e8eaf6',ec='#3949ab',lw=0.8,zorder=10))
tx(300,6,'梯形图读法: 左母线=+24V  右母线=0V  触点=开关  线圈=执行元件  NO=常开  NC=常闭',fs=6.5,c='#1a237e')

ax.set_xlim(-20,620); ax.set_ylim(-5,855); ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('output/page2_control_circuit.png',dpi=180,bbox_inches='tight',
            facecolor='white',edgecolor='none')
with open('output/page2_control_circuit.png.meta.json','w') as f:
    json.dump({"caption":"第2页  控制回路图（24V梯形图，含KM互锁/SF1安全/SVON/YV阀/续流二极管）",
               "description":"标准梯形图风格，+24V左母线/0V右母线，R01~R14共14个控制梯级，包含KM1/KM2互锁、SF1急停、伺服使能、电磁阀、VFD控制"}, f)
plt.close()
print("page2 done")
