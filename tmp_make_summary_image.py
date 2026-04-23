from PIL import Image, ImageDraw, ImageFont
W,H = 1400, 1800
bg = (248,250,252)
img = Image.new('RGB',(W,H),bg)
d = ImageDraw.Draw(img)
font_paths = [
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/Library/Fonts/Arial Unicode.ttf'
]
for p in font_paths:
    try:
        title = ImageFont.truetype(p, 64)
        h1 = ImageFont.truetype(p, 42)
        h2 = ImageFont.truetype(p, 34)
        body = ImageFont.truetype(p, 28)
        small = ImageFont.truetype(p, 24)
        break
    except:
        continue
else:
    title=h1=h2=body=small=ImageFont.load_default()

def box(x,y,w,h,fill=(255,255,255),outline=(220,226,232),r=24):
    d.rounded_rectangle((x,y,x+w,y+h),r,fill=fill,outline=outline,width=2)

def txt(x,y,s,f,fill=(17,24,39),spacing=8):
    d.multiline_text((x,y),s,font=f,fill=fill,spacing=spacing)

box(40,30,1320,170,fill=(15,23,42),outline=(15,23,42),r=28)
txt(80,65,'3.28—4.2 售后电话总结',title,fill=(255,255,255))
txt(82,135,'共 78 通｜全部已解决｜整体满意度高',h2,fill=(203,213,225))

cards=[('总电话量','78'),('服务天数','6天'),('已解决','78'),('主要方式','远程指导/重启/调参数')]
xs=[40,365,690,1015]
for i,(k,v) in enumerate(cards):
    box(xs[i],235,305,150,fill=(255,255,255))
    txt(xs[i]+28,265,k,h2,fill=(71,85,105))
    txt(xs[i]+28,315,v,h1,fill=(15,23,42))

box(40,420,640,420)
txt(70,455,'技术接电排名',h1)
rank=[('许德金',17),('何强聪',15),('贾泽琪',12),('胡振国',10),('秦振洋',10),('耿浩飞',9),('户振磊',5)]
y=525
for i,(name,n) in enumerate(rank,1):
    d.rounded_rectangle((70,y,620,y+36),12,fill=(241,245,249))
    d.rounded_rectangle((70,y,70+int(520*n/17),y+36),12,fill=(59,130,246))
    txt(82,y-2,f'{i}. {name}',body,fill=(255,255,255) if n>12 else (15,23,42))
    txt(575,y-2,str(n),body,fill=(15,23,42))
    y+=50

box(720,420,640,420)
txt(750,455,'高频问题 Top 8',h1)
issues=[('限位类',8),('驱动器报警',7),('振动刀',4),('风机/吸附',4),('气压相关',4),('相机/标定',3),('刀深',3),('其他',42)]
y=525
for name,n in issues:
    txt(760,y,f'• {name}',body)
    txt(1240,y,str(n),body,fill=(37,99,235))
    y+=42

box(40,870,1320,430)
txt(70,905,'核心结论',h1)
analysis='''1. 本周售后电话 78 通，整体处理效率较高，表内记录均为“已解决/满意”。\n2. 问题主要集中在：限位、驱动器报警、振动刀、风机吸附、气压、相机标定。\n3. 大量问题属于“可远程快速解决型”：重启、参数调整、接线检查、限位/气压/刀深校正。\n4. 说明当前售后压力更多来自安装调试细节、操作培训和基础维护，而不是大面积硬件失效。\n5. 建议把高频问题做成标准化短视频/图文 SOP，前置给客户和售后群，能明显减少重复电话。'''
txt(70,980,analysis,body,spacing=16)

box(40,1335,1320,390)
txt(70,1370,'下周建议动作',h1)
reco='''① 做 6 个高频问题 SOP：限位、驱动器报警、振动刀、风机吸附、气压、相机标定\n② 新机交付时增加“刀深/刀角度/限位/急停/吸附”五项首检清单\n③ 每位技术把重复出现的问题录成 1 分钟短视频，沉淀成售后知识库\n④ 对电话量最高的技术（许德金、何强聪、贾泽琪）复盘典型案例，提炼统一话术\n⑤ 统计下周是否因 SOP 上线后，电话量和重复问题占比下降'''
txt(70,1445,reco,body,spacing=16)

out='/tmp/售后电话总结_3.28-4.2.png'
img.save(out)
print(out)
