
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import os, json

prop = fm.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

# ══════════════════════════════════════════════════════
# PAGE 6 — 主回路图 (Main Circuit) 正式版
# GB/T 6988 风格: 竖向母线 + 横向支路
# 左→右: L1/L2/N/PE 母线, 各支路向右延伸
# 完整线号 + 端子号标注
# ══════════════════════════════════════════════════════
fig = plt.figure(figsize=(28, 20))
fig.patch.set_facecolor('white')
ax = fig.add_subplot(111)
ax.set_facecolor('white')
ax.axis('off')
kw = dict(fontproperties=prop)

W, H = 560, 760

# ── helpers ──────────────────────────────────────────
def lh(x1,x2,y,c='#111',lw=1.5,ls='-',z=5):
    ax.plot([x1,x2],[y,y],c,lw=lw,ls=ls,zorder=z)
def lv(x,y1,y2,c='#111',lw=1.5,ls='-',z=5):
    ax.plot([x,x],[y1,y2],c,lw=lw,ls=ls,zorder=z)
def jn(x,y,c='#111',r=2.5):
    ax.add_patch(plt.Circle((x,y),r,fc=c,ec=c,zorder=8))
def tx(x,y,s,fs=7.5,c='#111',ha='center',va='center',fw='normal',rot=0,z=9):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=c,fontweight=fw,
            rotation=rot,zorder=z,**kw,
            path_effects=[pe.withStroke(linewidth=1.2,foreground='white')])
def wn(x,y,s,col='#555'):  # wire number label
    ax.add_patch(mpatches.FancyBboxPatch((x-10,y-4),20,8,
        boxstyle='round,pad=1',fc='#fffde7',ec='#f9a825',lw=0.6,zorder=7))
    tx(x,y,s,fs=6,c='#5d4037',z=8)
def tn(x,y,s):  # terminal number label
    ax.add_patch(mpatches.FancyBboxPatch((x-10,y-4),20,8,
        boxstyle='round,pad=1',fc='#e8eaf6',ec='#3949ab',lw=0.6,zorder=7))
    tx(x,y,s,fs=6,c='#1a237e',z=8)

# IEC symbols
def breaker(ax,x,y,lbl,sub='',w=22,h=28):
    ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,
        boxstyle='square,pad=0',fc='white',ec='#c62828',lw=1.5,zorder=4))
    lv(x,y+h/2,y+h/2+10,'#c62828',lw=1.5)
    lv(x,y-h/2,y-h/2-10,'#c62828',lw=1.5)
    ax.plot([x-8,x+8],[y-8,y+8],'#c62828',lw=1.2,zorder=5)
    tx(x,y+h/2+18,lbl,fs=7.5,fw='bold',c='#b71c1c')
    tx(x,y-h/2-18,sub,fs=6.5,c='#777')

def contactor(ax,x,y,lbl,phases=1):
    for i in range(phases):
        dy = (i-(phases-1)/2)*18
        ax.add_patch(plt.Circle((x,y+dy),5,fc='white',ec='#e65100',lw=1.3,zorder=4))
        ax.plot([x-8,x-5],[y+dy,y+dy],'#e65100',lw=1.5,zorder=5)
        ax.plot([x+5,x+8],[y+dy,y+dy],'#e65100',lw=1.5,zorder=5)
        ax.plot([x-4,x+4],[y+dy+3,y+dy+3],'#e65100',lw=2,zorder=5)
    tx(x,y+phases*9+8,lbl,fs=7.5,fw='bold',c='#e65100')

def srv_drive(ax,x,y,lbl,w=44,h=58):
    ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,
        boxstyle='round,pad=2',fc='#e3f2fd',ec='#1565c0',lw=1.5,zorder=4))
    tx(x,y+10,lbl,fs=8,fw='bold',c='#0d47a1')
    tx(x,y-4,'L1/L2',fs=6.5,c='#1565c0')
    tx(x,y-14,'CN1/CN2',fs=6,c='#555')

def psu(ax,x,y,lbl,w=44,h=50):
    ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,
        boxstyle='round,pad=2',fc='#fff3e0',ec='#e65100',lw=1.5,zorder=4))
    tx(x,y+10,lbl,fs=8,fw='bold',c='#e65100')
    tx(x,y-4,'24V/10A',fs=7,c='#e65100')

def emi_f(ax,x,y):
    ax.add_patch(mpatches.FancyBboxPatch((x-14,y-10),28,20,
        boxstyle='square,pad=0',fc='#e8f5e9',ec='#2e7d32',lw=1.3,zorder=4))
    tx(x,y+3,'EMI',fs=7,fw='bold',c='#2e7d32')
    tx(x,y-5,'20A',fs=6.5,c='#2e7d32')

def safety_relay(ax,x,y,lbl):
    ax.add_patch(mpatches.FancyBboxPatch((x-24,y-22),48,44,
        boxstyle='round,pad=2',fc='#fce4ec',ec='#880e4f',lw=1.5,zorder=4))
    tx(x,y+8,lbl,fs=8,fw='bold',c='#880e4f')
    tx(x,y-4,'Pilz PNOZ X2P',fs=6.5,c='#880e4f')
    tx(x,y-14,'DC24V  2NO',fs=6.5,c='#880e4f')

# ══════════════════════════════════════════════════════
# MAIN POWER BUSES (vertical, left side)
# ══════════════════════════════════════════════════════
BUS_X = {'L1':30,'L2':55,'N':80,'PE':105}
BUS_COL = {'L1':'#c62828','L2':'#f57c00','N':'#1565c0','PE':'#2e7d32'}
BUS_TOP = 710; BUS_BTM = 40

for bname,(bx,bc) in zip(BUS_X.keys(),
    [(BUS_X[k],BUS_COL[k]) for k in BUS_X]):
    lv(bx,BUS_BTM,BUS_TOP,bc,lw=3.5,z=3)
    tx(bx,BUS_TOP+10,bname,fs=9,fw='bold',c=bc)
    # incoming arrow
    ax.annotate('',xy=(bx,BUS_TOP),xytext=(bx,BUS_TOP+20),
        arrowprops=dict(arrowstyle='->',color=bc,lw=2))

# BL incoming label
ax.add_patch(mpatches.FancyBboxPatch((4,720),110,18,
    boxstyle='round,pad=2',fc='#ffcdd2',ec='#c62828',lw=1.2,zorder=6))
tx(59,729,'BL角孔  主进线  3P+N+PE',fs=7.5,fw='bold',c='#b71c1c',z=7)
wn(59,718,'W-MAINS')

# ══════════════════════════════════════════════════════
# BRANCH 1 — QF0 总断路器
# ══════════════════════════════════════════════════════
BR1_X = 175; BR1_Y = 690
for bname,bc in [('L1','#c62828'),('L2','#f57c00'),('N','#1565c0')]:
    bx = BUS_X[bname]
    lh(bx,BR1_X-20,680,bc,lw=2)
    jn(bx,680,bc)

breaker(ax,BR1_X,BR1_Y,'QF0','NSX100F\n3P+N 63A',w=28,h=32)
# PE direct bypass
lh(BUS_X['PE'],BR1_X+40,660,'#2e7d32',lw=2)
tx(BR1_X+50,660,'PE 直通',fs=6.5,c='#2e7d32')

# Wire numbers on QF0 output
for i,(bname,bc) in enumerate([('L1','#c62828'),('L2','#f57c00'),('N','#1565c0')]):
    wy = 655
    lv(BR1_X-8+i*8, BR1_Y-16, wy, bc,lw=2)
    wn(BR1_X-8+i*8, wy-8, f'W-{bname}1',col=bc)

# ══════════════════════════════════════════════════════
# BRANCH 2 — KM1 主接触器
# ══════════════════════════════════════════════════════
BR2_X = 240
lh(BR1_X,BR2_X-15,644,'#c62828',lw=2)
lh(BR1_X,BR2_X-15,636,'#f57c00',lw=2)
lh(BR1_X,BR2_X-15,628,'#1565c0',lw=2)
lv(BR2_X-15,628,644,'#c62828',lw=1.5,ls=':')
contactor(ax,BR2_X,636,'KM1\nNC1-25',phases=3)
for y,bc,wlbl in [(644,'#c62828','W-L1A'),(636,'#f57c00','W-L2A'),(628,'#1565c0','W-NA')]:
    lh(BR2_X+15,BR2_X+35,y,bc,lw=2)
    jn(BR2_X+35,y,bc)
    wn(BR2_X+25,y-8,wlbl)

# ══════════════════════════════════════════════════════
# BRANCH 3 — KM2 风机接触器 (分支, 380V)
# ══════════════════════════════════════════════════════
BR3_X = 240; BR3_Y = 580
lh(BR1_X,BR3_X-15,590,'#c62828',lw=2)
lh(BR1_X,BR3_X-15,580,'#f57c00',lw=2)
ax.add_patch(mpatches.Rectangle((BR3_X-20,555),50,50,
    fc='#fff9c4',ec='#e65100',lw=1.3,zorder=4))
tx(BR3_X+5,BR3_Y,'KM2\nNC1-12\n380V',fs=7.5,fw='bold',c='#e65100')
lh(BR3_X+30,BR3_X+60,580,'#e65100',lw=2)
ax.add_patch(mpatches.FancyBboxPatch((BR3_X+60,572),50,18,
    boxstyle='round,pad=2',fc='#e8f5e9',ec='#2e7d32',lw=1.2,zorder=4))
tx(BR3_X+85,581,'风机\n9kW 380V',fs=7,c='#1b5e20')
wn(BR3_X+47,572,'W-FAN-U/V/W')

# ══════════════════════════════════════════════════════
# BRANCH 4 — QF2 + EMI1 → 220V伺服母排
# ══════════════════════════════════════════════════════
BUS220_X = 330  # 220V 竖向母排位置
BUS220_Y1 = 540; BUS220_Y2 = 120

lh(BR2_X+35,BUS220_X,644,'#c62828',lw=2)
lh(BR2_X+35,BUS220_X,628,'#1565c0',lw=2)

breaker(ax,BUS220_X+20,620,'QF2','1P 20A',w=18,h=22)
lh(BUS220_X,BUS220_X+11,620,'#c62828',lw=2)
wn(BUS220_X+8,612,'W-L1B')

emi_f(ax,BUS220_X+60,620)
lh(BUS220_X+31,BUS220_X+46,620,'#c62828',lw=2)
lh(BUS220_X+74,BUS220_X+95,620,'#c62828',lw=2)
wn(BUS220_X+83,612,'W-L1C')

# 220V 竖母排
lv(BUS220_X+95,BUS220_Y2,620,'#c62828',lw=3,z=3)
lv(BUS220_X+78,BUS220_Y2,620,'#1565c0',lw=2.5,z=3)
tx(BUS220_X+95,BUS220_Y2-10,'220V L',fs=8,fw='bold',c='#c62828')
tx(BUS220_X+78,BUS220_Y2-10,'N',fs=8,fw='bold',c='#1565c0')
tx(BUS220_X+87,BUS220_Y2-22,'220V伺服总线',fs=8,fw='bold',c='#555')
wn(BUS220_X+87,BUS220_Y2-32,'W-AC220-BUS')

# ══════════════════════════════════════════════════════
# BRANCHES 5~10 — QF3~QF8 → 各驱动器 / PS1
# 从220V竖母排向右分支
# ══════════════════════════════════════════════════════
SRV_X_LIST = [430, 464, 498, 430, 464, 498]  # X坐标(3列x2行)
SRV_Y_LIST = [500, 500, 500, 350, 350, 350]
SRV_INFO = [
    ('QF3\n6A','SRV1\n400W\n前后轴1'),
    ('QF4\n6A','SRV2\n400W\n前后轴2'),
    ('QF5\n6A','SRV3\n400W\n左右轴'),
    ('QF6\n4A','SRV4\n100W\n升降轴'),
    ('QF7\n4A','SRV5\n100W\n旋转轴'),
    ('QF8\n6A','PS1\n24V\n电源'),
]

for i,(qx,qy,(ql,sl)) in enumerate(zip(SRV_X_LIST,SRV_Y_LIST,SRV_INFO)):
    # tap from 220V bus
    lh(BUS220_X+95,qx-22,qy+20,'#c62828',lw=1.8)
    lh(BUS220_X+78,qx-22,qy+10,'#1565c0',lw=1.8)
    jn(BUS220_X+95,qy+20,'#c62828',r=2)
    jn(BUS220_X+78,qy+10,'#1565c0',r=2)
    # QF symbol
    ax.add_patch(mpatches.FancyBboxPatch((qx-22,qy+2),18,20,
        boxstyle='square,pad=0',fc='#e3f2fd',ec='#1565c0',lw=1.2,zorder=4))
    tx(qx-13,qy+12,ql,fs=6,fw='bold',c='#0d47a1')
    ax.plot([qx-14,qx-12],[qy+6,qy+16],'#1565c0',lw=1,zorder=5)
    wn(qx-13,qy,'W-'+ql.replace('\n','')+'-L')
    # wire to drive
    lv(qx-13,qy+2,qy-5,'#c62828',lw=1.8)
    # drive/ps box
    fc = '#fff3e0' if i==5 else '#e3f2fd' if i<3 else '#e8f5e9'
    ec_c = '#e65100' if i==5 else '#1565c0' if i<3 else '#2e7d32'
    ax.add_patch(mpatches.FancyBboxPatch((qx-22,qy-60),44,52,
        boxstyle='round,pad=2',fc=fc,ec=ec_c,lw=1.5,zorder=4))
    tx(qx,qy-34,sl,fs=7,fw='bold',c=ec_c)
    # PE line
    lh(BUS_X['PE'],qx,qy-65,'#2e7d32',lw=1.2,ls='--')
    tx(qx-5,qy-68,'PE',fs=6,c='#2e7d32')
    wn(qx,qy-76,f'W-PE{i+1}')
    # L/N wire numbers into drive
    wn(qx-13,qy-6,f'W-SRV{i+1}-L')

# ══════════════════════════════════════════════════════
# SF1 SAFETY RELAY (central right area)
# ══════════════════════════════════════════════════════
safety_relay(ax,185,540,'SF1')
lv(185,518,490,'#880e4f',lw=1.5,ls='--')
tx(200,530,'SF1 安全输出NO → KM1线圈回路',fs=7,c='#880e4f',ha='left')
# coil
ax.add_patch(mpatches.FancyBboxPatch((156,487),58,16,
    boxstyle='square,pad=0',fc='#fce4ec',ec='#880e4f',lw=1,zorder=4))
tx(185,495,'线圈 DC24V',fs=6.5,c='#880e4f')
tx(185,482,'← CB2-24V / TC-OUT11',fs=6.5,c='#555',ha='center')

# ══════════════════════════════════════════════════════
# TITLE BLOCK
# ══════════════════════════════════════════════════════
ax.add_patch(mpatches.Rectangle((0,0),W,36,fc='#f5f5f5',ec='#333',lw=1.2,zorder=10))
ax.plot([0,W],[24,24],'#333',lw=0.8,zorder=11)
ax.plot([0,W],[12,12],'#333',lw=0.8,zorder=11)
for xd,lbl in [(0,'振动刀切割设备'),(120,'主回路图  Main Circuit'),(300,'Rev.B'),(400,'2026-04'),(480,'1 / 6')]:
    tx(xd+4,30,lbl,fs=7.5,fw='bold' if xd<120 else 'normal',c='#111',ha='left')
for xd in [120,300,400,480,W]:
    ax.plot([xd,xd],[0,36],'#333',lw=0.8,zorder=11)
# revision box
ax.add_patch(mpatches.Rectangle((0,0),W,12,fc='#e8eaf6',ec='#3949ab',lw=0.8,zorder=10))
tx(W/2,6,'线号规则: W-[总线名]-[支路号]  例:W-L1A=QF0之后L1  W-SRV3-L=SRV3进线L  W-PE2=SRV2接地线',
   fs=6.5,c='#1a237e')

ax.set_xlim(-10,W+10)
ax.set_ylim(-5,780)
ax.set_aspect('equal')
plt.tight_layout()
plt.savefig('output/page1_main_circuit.png',dpi=180,bbox_inches='tight',
            facecolor='white',edgecolor='none')
with open('output/page1_main_circuit.png.meta.json','w') as f:
    json.dump({"caption":"第1页  主回路图（GB/T 6988风格，含线号/端子号/IEC符号）",
               "description":"竖向母线L1/L2/N/PE，横向分支QF0→KM1→KM2→EMI→QF3~QF8→SRV1~5/PS1，含SF1安全继电器接线示意"}, f)
plt.close()
print("page1 done")
