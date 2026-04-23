const pptxgen = require('pptxgenjs');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'OpenClaw';
pptx.company = '红太阳数控';
pptx.subject = '周例会周报';
pptx.title = '周例会周报：工期与团队凝聚力';
pptx.lang = 'zh-CN';
pptx.theme = {
  headFontFace: 'Microsoft YaHei',
  bodyFontFace: 'Microsoft YaHei',
  lang: 'zh-CN'
};

const C = {
  navy: '17324D',
  blue: '2E5B88',
  lightBlue: 'DCEAF7',
  red: 'C93C37',
  orange: 'D87A00',
  green: '2F7D4A',
  bg: 'F7F9FC',
  text: '1F2937',
  mute: '6B7280',
  line: 'D1D9E6',
  white: 'FFFFFF',
  lightRed: 'FBE4E2',
  lightOrange: 'FDEEDB',
  lightGreen: 'E4F3E8'
};

function title(slide, main, sub='') {
  slide.addText(main, { x: 0.5, y: 0.35, w: 8.8, h: 0.5, fontSize: 24, bold: true, color: C.navy });
  if (sub) slide.addText(sub, { x: 0.5, y: 0.9, w: 8.5, h: 0.28, fontSize: 10, color: C.mute });
  slide.addShape(pptx.ShapeType.line, { x: 0.5, y: 1.18, w: 12.3, h: 0, line: { color: C.line, pt: 1.2 } });
}
function footer(slide) {
  slide.addText('红太阳数控｜周例会材料', { x: 0.5, y: 6.95, w: 3.5, h: 0.2, fontSize: 9, color: C.mute });
}
function box(slide, x,y,w,h, fill, line=C.line) {
  slide.addShape(pptx.ShapeType.roundRect, { x,y,w,h, rectRadius: 0.06, fill: { color: fill }, line: { color: line, pt: 1 } });
}
function bulletList(slide, items, x,y,w,h, color=C.text, fs=16, indent=18) {
  let runs=[];
  items.forEach(t=>{
    runs.push({ text: t, options: { bullet: { indent }, breakLine: true } });
  });
  slide.addText(runs, { x,y,w,h, fontSize: fs, color, breakLine: false, paraSpaceAfterPt: 8, valign: 'top', margin: 0.04 });
}

// Slide 1
{
  const s = pptx.addSlide();
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.33, h:7.5, fill:{color:C.bg}, line:{color:C.bg, pt:0} });
  s.addShape(pptx.ShapeType.rect, { x:0, y:0, w:13.33, h:1.35, fill:{color:C.navy}, line:{color:C.navy, pt:0} });
  s.addText('周例会周报', { x:0.65, y:1.75, w:5.2, h:0.6, fontSize: 28, bold: true, color: C.navy });
  s.addText('本周重点：工期问题 + 团队凝聚力', { x:0.65, y:2.45, w:6.4, h:0.4, fontSize: 18, color: C.blue, bold: true });
  s.addText('会议核心：把问题讲透，把责任压实，把动作定清。', { x:0.65, y:3.0, w:6.6, h:0.35, fontSize: 13, color: C.text });
  box(s, 7.7, 1.8, 4.9, 3.3, C.white);
  s.addText('本周两大议题', { x:8.05, y:2.05, w:2.8, h:0.3, fontSize: 18, bold: true, color: C.navy });
  bulletList(s, [
    '工期：临近假期备货集中，代加工来不及，返工品挤占时间',
    '凝聚力：互帮互助、补台不拆台、共担赢未来'
  ], 8.0, 2.55, 4.1, 1.8, C.text, 16, 16);
  s.addText('汇报人：厂办/管理层', { x:0.65, y:6.2, w:3.6, h:0.25, fontSize: 11, color: C.mute });
  s.addText('时间：本周例会', { x:0.65, y:6.48, w:3.6, h:0.25, fontSize: 11, color: C.mute });
  footer(s);
}

// Slide 2
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '一、本周问题总览', '先看问题，不绕圈子');
  box(s, 0.6, 1.45, 5.95, 4.9, C.white);
  box(s, 6.8, 1.45, 5.95, 4.9, C.white);
  s.addText('问题一：工期', { x:0.9, y:1.75, w:2.2, h:0.3, fontSize: 20, bold: true, color: C.red });
  bulletList(s, [
    '临近假期，备货任务集中卡在同一时间段',
    '代加工厂商来不及，外协承接能力不足',
    '为赶工接收了不合格品，反而拖慢整体节奏',
    '返工、重配、重检，直接挤压交付时间'
  ], 0.9, 2.2, 5.1, 3.3, C.text, 16, 16);
  s.addText('问题二：团队凝聚力', { x:7.1, y:1.75, w:3.2, h:0.3, fontSize: 20, bold: true, color: C.orange });
  bulletList(s, [
    '部门之间补位意识不够强',
    '有时只看自己岗位，不看整体结果',
    '出现问题先分责任，补台动作慢',
    '企业文化里的“团结”还没有完全落到行为上'
  ], 7.1, 2.2, 5.0, 3.3, C.text, 16, 16);
  footer(s);
}

// Slide 3
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '二、工期问题分析', '核心不是忙，而是忙乱、忙偏、忙出返工');
  box(s, 0.7, 1.55, 3.75, 4.9, C.lightRed, C.red);
  box(s, 4.8, 1.55, 3.75, 4.9, C.lightOrange, C.orange);
  box(s, 8.9, 1.55, 3.75, 4.9, C.lightBlue, C.blue);
  s.addText('现象', { x:1.0, y:1.85, w:1.5, h:0.3, fontSize: 20, bold: true, color: C.red });
  bulletList(s, [
    '订单、备货、外协任务同时堆积',
    '代加工交付跟不上节奏',
    '为抢时间接受不合格件'
  ], 0.98, 2.25, 3.0, 2.5, C.text, 15, 14);
  s.addText('后果', { x:5.1, y:1.85, w:1.5, h:0.3, fontSize: 20, bold: true, color: C.orange });
  bulletList(s, [
    '返工增加',
    '质检压力变大',
    '交期被进一步拖延',
    '客户感受变差'
  ], 5.05, 2.25, 3.0, 2.5, C.text, 15, 14);
  s.addText('根因', { x:9.2, y:1.85, w:1.5, h:0.3, fontSize: 20, bold: true, color: C.blue });
  bulletList(s, [
    '假期前任务前置预判不够',
    '代加工产能预留不足',
    '质量底线在赶工时被放松',
    '缺少统一节奏和优先级管理'
  ], 9.15, 2.25, 3.0, 2.8, C.text, 15, 14);
  footer(s);
}

// Slide 4
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '三、工期问题改进动作', '先稳质量，再稳节奏，再保交付');
  box(s, 0.7, 1.55, 12.0, 4.8, C.white);
  const ys = [1.95, 2.75, 3.55, 4.35, 5.15];
  const titles = ['动作1', '动作2', '动作3', '动作4', '动作5'];
  const texts = [
    '假期前两周，提前做备货预警和外协产能锁定，不等任务堆到眼前再抢。',
    '重点订单、急单、常规单分层排产，不能所有单子一个优先级。',
    '代加工来料不合格，一律卡在前道，不允许带病流入内部工序。',
    '返工件、异常件单独建台账，日清日结，不能混进正常进度。',
    '每天盯三件事：缺件、外协、返工，发现卡点当天处理。'
  ];
  for (let i=0;i<5;i++) {
    s.addShape(pptx.ShapeType.roundRect, { x:1.0, y:ys[i], w:1.0, h:0.42, rectRadius:0.04, fill:{color:C.navy}, line:{color:C.navy, pt:0.5} });
    s.addText(titles[i], { x:1.18, y:ys[i]+0.08, w:0.6, h:0.2, fontSize: 14, bold:true, color:C.white, align:'center' });
    s.addText(texts[i], { x:2.3, y:ys[i]+0.03, w:9.7, h:0.32, fontSize: 16, color:C.text });
  }
  footer(s);
}

// Slide 5
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '四、团队凝聚力问题展开', '文化不是墙上的字，要变成现场动作');
  box(s, 0.7, 1.55, 4.0, 4.9, C.lightBlue, C.blue);
  box(s, 4.95, 1.55, 3.9, 4.9, C.lightOrange, C.orange);
  box(s, 9.05, 1.55, 3.6, 4.9, C.lightGreen, C.green);
  s.addText('当前短板', { x:1.0, y:1.85, w:1.8, h:0.3, fontSize: 20, bold: true, color: C.blue });
  bulletList(s, [
    '遇事先看自己，不先看整体',
    '跨岗位补位不够主动',
    '出现问题时容易有“这不是我的事”'
  ], 1.0, 2.25, 3.2, 2.5, C.text, 15, 14);
  s.addText('文化要求', { x:5.25, y:1.85, w:1.8, h:0.3, fontSize: 20, bold: true, color: C.orange });
  bulletList(s, [
    '互帮互助',
    '补台不拆台',
    '共担赢未来'
  ], 5.25, 2.25, 2.6, 2.2, C.text, 16, 14);
  s.addText('落地标准', { x:9.35, y:1.85, w:1.8, h:0.3, fontSize: 20, bold: true, color: C.green });
  bulletList(s, [
    '看到问题先补位',
    '发现风险先提醒',
    '出结果时一起扛',
    '不当旁观者'
  ], 9.35, 2.25, 2.5, 2.5, C.text, 15, 14);
  footer(s);
}

// Slide 6
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '五、团队凝聚力建设动作', '把“团结”从口号变成机制和行为');
  box(s, 0.8, 1.55, 12.0, 4.95, C.white);
  const data = [
    ['1', '班组之间遇到赶工、缺人、卡点时，先补位，再讨论责任。'],
    ['2', '管理层在会议上多讲“怎么补台”，少讲“谁先撇清”。'],
    ['3', '对主动协同、主动补位、帮助同事解决问题的行为，公开表扬。'],
    ['4', '对拆台、推责、看笑话式旁观，明确批评。'],
    ['5', '让每个人知道：个人赢不算赢，团队赢才是真赢。']
  ];
  let y = 1.95;
  data.forEach(([n,t])=>{
    s.addShape(pptx.ShapeType.ellipse, { x:1.0, y:y, w:0.42, h:0.42, fill:{color:C.orange}, line:{color:C.orange, pt:0.5} });
    s.addText(n, { x:1.12, y:y+0.08, w:0.18, h:0.16, fontSize: 14, bold:true, color:C.white, align:'center' });
    s.addText(t, { x:1.7, y:y+0.02, w:10.4, h:0.28, fontSize: 16, color:C.text });
    y += 0.87;
  });
  footer(s);
}

// Slide 7
{
  const s = pptx.addSlide(); s.background = { color: C.bg }; title(s, '六、会议要求与本周落地', '会后不是散会，是开干');
  box(s, 0.75, 1.55, 5.8, 4.9, C.white);
  box(s, 6.8, 1.55, 5.8, 4.9, C.white);
  s.addText('会议要求', { x:1.0, y:1.85, w:1.8, h:0.3, fontSize: 20, bold: true, color: C.navy });
  bulletList(s, [
    '讲结果，不讲空话',
    '讲问题，不绕责任',
    '讲动作，不停留在态度表态'
  ], 1.0, 2.25, 4.7, 2.2, C.text, 16, 14);
  s.addText('本周落地', { x:7.05, y:1.85, w:1.8, h:0.3, fontSize: 20, bold: true, color: C.navy });
  bulletList(s, [
    '生产、采购、外协：梳理假期前订单优先级',
    '质检：严控不合格件流入',
    '各部门负责人：带头补位、带头协同',
    '会后形成责任清单，逐项盯到人、盯到时间'
  ], 7.05, 2.25, 4.8, 2.8, C.text, 16, 14);
  s.addShape(pptx.ShapeType.roundRect, { x:3.65, y:6.2, w:6.0, h:0.58, rectRadius:0.05, fill:{color:C.navy}, line:{color:C.navy, pt:0.5} });
  s.addText('补台不拆台，共担赢未来。质量守住，工期才守得住。', { x:3.82, y:6.37, w:5.65, h:0.2, fontSize: 15, bold:true, color:C.white, align:'center' });
  footer(s);
}

pptx.writeFile({ fileName: '/Users/apple/.openclaw/workspace/projects/weekly-meeting-ppt-2026-04-21/周例会周报_工期与团队凝聚力_2026-04-21.pptx' });
