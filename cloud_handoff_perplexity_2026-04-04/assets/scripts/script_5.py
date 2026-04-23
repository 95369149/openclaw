
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
import os, json

prop = fm.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
kw = dict(fontproperties=prop)

def _tx(ax,x,y,s,fs=7.5,c='#111',ha='center',va='center',fw='normal',rot=0,z=9):
    ax.text(x,y,s,ha=ha,va=va,fontsize=fs,color=c,fontweight=fw,
            rotation=rot,zorder=z,**kw,
            path_effects=[pe.withStroke(linewidth=1.2,foreground='white')])

def _R(ax,x,y,w,h,fc='white',ec='#333',lw=1.2,z=3,al=1.0):
    ax.add_patch(mpatches.FancyBboxPatch((x,y),w,h,boxstyle='round,pad=1',fc=fc,ec=ec,lw=lw,zorder=z,alpha=al))

PULSE_DATA = [
    ('X轴','SRV1\n前后轴1','#c62828','W-PLS1'),
    ('Y轴','SRV2\n前后轴2','#e65100','W-PLS2'),
    ('UD1','SRV3\n左右轴','#f57c00','W-PLS3'),
    ('Z轴','SRV4\n升降轴','#2e7d32','W-PLS4'),
    ('U轴','SRV5\n旋转轴','#1565c0','W-PLS5'),
]

fig,ax = plt.subplots(figsize=(30,20))
fig.patch.set_facecolor('white'); ax.set_facecolor('white'); ax.axis('off')
W=800; H=680; CX,CY,CW,CH = 340,380,180,340
ax.set_xlim(0,W); ax.set_ylim(0,H+50)

# TC box
_R(ax,CX-CW//2,CY-CH//2,CW,CH,'#ede7f6','#4527a0',lw=2.5,z=4)
_tx(ax,CX,CY+140,'乾诚 TC-6832',fs=14,fw='bold',c='#311b92')
_tx(ax,CX,CY+122,'运动控制系统',fs=10,c='#4527a0')
_tx(ax,CX,CY+104,'5轴 / IN8 / OUT32',fs=9,c='#6a1b9a')

# LEFT: IN
IN_DATA = [
    ('IN1','急停反馈 ← SF1 Y1','#880e4f','SB-ES-EDM'),
    ('IN2','前梁对射 ← RX1','#1565c0','XT-IN:5'),
    ('IN3','后梁对射 ← RX2','#1565c0','XT-IN:7'),
    ('IN4','四角暂停 ← SB-P','#e65100','XT-IN:9'),
    ('IN5','X原点/限位','#2e7d32','XT-IN:11'),
    ('IN6','Y原点/限位','#2e7d32','XT-IN:13'),
    ('IN7','Z原点/限位','#2e7d32','XT-IN:15'),
    ('IN8','U原点/限位','#2e7d32','XT-IN:17'),
]
for i,(pin,desc,col,src) in enumerate(IN_DATA):
    py = CY+115-i*37
    _R(ax,22,py-11,100,22,fc='#f5f5f5',ec=col,lw=1.2,z=4)
    _tx(ax,72,py+2,src,fs=7.5,fw='bold',c=col)
    _tx(ax,72,py-5,desc,fs=6.5,c='#555')
    ax.plot([122,CX-CW//2],[py,py],col,lw=1.5,ls='--',zorder=5)
    ax.plot([CX-CW//2-4,CX-CW//2+4],[py,py],'#4527a0',lw=3,zorder=6)
    _tx(ax,CX-CW//2-16,py,pin,fs=7.5,fw='bold',c='#4527a0')
    ax.add_patch(mpatches.FancyBboxPatch((168,py-5),38,10,boxstyle='round,pad=1',fc='#fffde7',ec='#f9a825',lw=0.7,zorder=7))
    _tx(ax,187,py,f'W-{pin}',fs=6,c='#5d4037',z=8)

# RIGHT: OUT
OUT_DATA = [
    ('OUT1','KM1 主接触器','#c62828','XT-OUT:1'),
    ('OUT2','KM2 风机','#e65100','XT-OUT:3'),
    ('OUT3','VFD DI1 正转','#f57c00','XT-OUT:5'),
    ('OUT4','VFD DI2 复位','#f57c00','XT-OUT:7'),
    ('OUT5','YV1 台面阀1','#2e7d32','XT-OUT:9'),
    ('OUT6','YV2 台面阀2','#2e7d32','XT-OUT:11'),
    ('OUT7~9','YV3~5 台面阀3~5','#2e7d32','XT-OUT:13'),
    ('OUT10','YV6 反吹阀','#2e7d32','XT-OUT:19'),
    ('OUT11','KA-SVON 使能','#880e4f','XT-OUT:21'),
    ('OUT12','HL-R 报警灯','#c62828','XT-OUT:23'),
    ('OUT13','HL-G 运行灯','#2e7d32','XT-OUT:25'),
    ('OUT14','BZ 蜂鸣器','#f57c00','XT-OUT:27'),
]
for i,(pin,desc,col,tgt) in enumerate(OUT_DATA):
    py = CY+115-i*33
    _R(ax,CX+CW//2+60,py-11,110,22,fc='#f5f5f5',ec=col,lw=1.2,z=4)
    _tx(ax,CX+CW//2+115,py+2,tgt,fs=7.5,fw='bold',c=col)
    _tx(ax,CX+CW//2+115,py-5,desc,fs=6.5,c='#555')
    ax.plot([CX+CW//2,CX+CW//2+60],[py,py],col,lw=1.5,zorder=5)
    ax.plot([CX+CW//2-4,CX+CW//2+4],[py,py],'#4527a0',lw=3,zorder=6)
    _tx(ax,CX+CW//2+18,py,pin,fs=7,fw='bold',c='#4527a0',ha='left')
    ax.add_patch(mpatches.FancyBboxPatch((CX+CW//2+18,py-5),38,10,boxstyle='round,pad=1',fc='#fffde7',ec='#f9a825',lw=0.7,zorder=7))
    _tx(ax,CX+CW//2+37,py,f'W-O{i+1}',fs=6,c='#5d4037',z=8)

# BOTTOM: pulse axes
for i,(axn,srv,col,wlbl) in enumerate(PULSE_DATA):
    px = CX-90+i*45
    ax.plot([px,px],[CY-CH//2,CY-CH//2-18],col,lw=2,zorder=5)
    _R(ax,px-24,CY-CH//2-58,48,38,fc='#e3f2fd',ec=col,lw=1.5,z=4)
    _tx(ax,px,CY-CH//2-34,f'{axn} {wlbl}',fs=7,fw='bold',c=col)
    _tx(ax,px,CY-CH//2-47,srv,fs=6.5,c='#555')
    ax.plot([px,px],[CY-CH//2-58,CY-CH//2-78],col,lw=1.5,ls='--',zorder=5)
    _R(ax,px-26,CY-CH//2-108,52,26,fc='#e8f5e9',ec=col,lw=1.2,z=4)
    _tx(ax,px,CY-CH//2-95,'CN1  ASTP 4C',fs=6.5,c=col)

# TOP: encoder
for i,(axn,srv,col,wlbl) in enumerate(PULSE_DATA):
    px = CX-90+i*45
    ax.plot([px,px],[CY+CH//2,CY+CH//2+18],col,lw=1.8,ls='--',zorder=5)
    _R(ax,px-26,CY+CH//2+18,52,24,fc='#e8f5e9',ec=col,lw=1.2,z=4)
    _tx(ax,px,CY+CH//2+30,'CN2 编码器',fs=6.5,c=col)
    _tx(ax,px,CY+CH//2+48,f'ASTP 6C\nW-ENC{i+1}',fs=6,c='#888')

# 24V power
ax.plot([0,CX-CW//2],[CY-60,CY-60],'#c62828',lw=2,zorder=5)
ax.plot([0,CX-CW//2],[CY-75,CY-75],'#1565c0',lw=2,zorder=5)
_tx(ax,4,CY-60,'+24V CB1',fs=8,fw='bold',c='#c62828',ha='left')
_tx(ax,4,CY-75,'0V GND',fs=8,fw='bold',c='#1565c0',ha='left')

# Title
ax.add_patch(mpatches.Rectangle((0,0),W,28,fc='#f5f5f5',ec='#333',lw=1.2,zorder=10))
ax.plot([0,W],[18,18],'#333',lw=0.8,zorder=11)
for xd,lbl in [(2,'振动刀切割设备'),(200,'TC-6832 I/O 接线原理图'),(420,'Rev.B'),(510,'2026-04'),(580,'3 / 6')]:
    ax.text(xd+2,23,lbl,ha='left',va='center',fontsize=8,fontweight='bold' if xd<200 else 'normal',color='#111',zorder=11,**kw)
for xd in [200,420,510,580,W]:
    ax.plot([xd,xd],[9,28],'#333',lw=0.8,zorder=11)
ax.add_patch(mpatches.Rectangle((0,0),W,9,fc='#e8eaf6',ec='#3949ab',lw=0.8,zorder=10))
ax.text(W/2,5,'左侧=数字输入(蓝色导线0.75mm²) | 右侧=数字输出(绿/橙导线0.75mm²) | 下方=脉冲轴ASTP屏蔽 | 上方=编码器ASTP',
        ha='center',va='center',fontsize=7,color='#1a237e',zorder=11,**kw)
ax.text(W/2,H+38,'第3页  TC-6832 I/O 接线原理图',ha='center',va='center',fontsize=13,fontweight='bold',color='#1a237e',**kw)

plt.tight_layout()
plt.savefig('output/page3_io.png',dpi=160,bbox_inches='tight',facecolor='white',edgecolor='none')
with open('output/page3_io.png.meta.json','w') as f:
    json.dump({"caption":"第3页 TC-6832 I/O接线原理图（完整IN/OUT/5轴脉冲/编码器）",
               "description":"TC-6832控制器居中，左侧IN1~IN8，右侧OUT1~OUT14，下方5轴脉冲，上方编码器，全部含线号"}, f)
plt.close()
print(f"page3 OK: {os.path.getsize('output/page3_io.png')//1024} KB")

# Now rebuild panel layout + terminal + BOM in one summary
for fn in ['output/page1_main_circuit.png','output/page2_control_circuit.png','output/page3_io.png']:
    print(f"{fn}: {os.path.getsize(fn)//1024} KB")
