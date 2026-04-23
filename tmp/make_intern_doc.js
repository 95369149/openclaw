const fs = require('fs');
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  AlignmentType,
  WidthType,
  BorderStyle,
  Table,
  TableRow,
  TableCell,
  HeightRule,
  VerticalAlign,
} = require('docx');

const borderThin = { style: BorderStyle.SINGLE, size: 1, color: '000000' };
const noBorder = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const allBorders = { top: borderThin, bottom: borderThin, left: borderThin, right: borderThin };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

const bodyText = [
  '彭术罡同学于2026年2月1日至2026年4月3日在我单位技术岗位进行实习。',
  '',
  '实习期间，该生实习态度端正，责任心强，能够自觉遵守单位各项规章制度及操作规程，按时到岗，服从安排。工作中踏实认真，执行力较强，能够按照岗位要求完成相关工作任务。',
  '',
  '在实习过程中，该生表现出较好的学习意识和适应能力，遇到问题能够主动思考、及时请教，具备一定的分析问题和解决问题能力。与同事相处融洽，工作配合较好，整体表现良好。',
  '',
  '经考核，我单位认为该生已完成实习期间各项实践任务，达到实习要求。'
];

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: 'SimSun', size: 24 },
        paragraph: { spacing: { line: 360 } },
      },
    },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1260, bottom: 1440, left: 1260 },
      },
    },
    children: [
      new Table({
        width: { size: 9386, type: WidthType.DXA },
        columnWidths: [9386],
        rows: [
          new TableRow({
            height: { value: 720, rule: HeightRule.ATLEAST },
            children: [
              new TableCell({
                borders: allBorders,
                width: { size: 9386, type: WidthType.DXA },
                verticalAlign: VerticalAlign.CENTER,
                children: [
                  new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [new TextRun({ text: '实习单位鉴定意见', bold: true, size: 32 })],
                  }),
                ],
              }),
            ],
          }),
          new TableRow({
            height: { value: 5400, rule: HeightRule.ATLEAST },
            children: [
              new TableCell({
                borders: allBorders,
                width: { size: 9386, type: WidthType.DXA },
                margins: { top: 240, bottom: 240, left: 240, right: 240 },
                children: bodyText.map((line) => new Paragraph({
                  firstLine: 420,
                  children: [new TextRun(line)],
                })),
              }),
            ],
          }),
          new TableRow({
            height: { value: 900, rule: HeightRule.ATLEAST },
            children: [
              new TableCell({
                borders: allBorders,
                width: { size: 9386, type: WidthType.DXA },
                children: [
                  new Table({
                    width: { size: 8900, type: WidthType.DXA },
                    columnWidths: [5340, 3560],
                    rows: [
                      new TableRow({
                        children: [
                          new TableCell({
                            borders: noBorders,
                            width: { size: 5340, type: WidthType.DXA },
                            children: [new Paragraph({ children: [new TextRun('实习单位指导教师签名：________________')] })],
                          }),
                          new TableCell({
                            borders: noBorders,
                            width: { size: 3560, type: WidthType.DXA },
                            children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun('年    月    日')] })],
                          }),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
            ],
          }),
          new TableRow({
            height: { value: 900, rule: HeightRule.ATLEAST },
            children: [
              new TableCell({
                borders: allBorders,
                width: { size: 9386, type: WidthType.DXA },
                children: [
                  new Table({
                    width: { size: 8900, type: WidthType.DXA },
                    columnWidths: [5340, 3560],
                    rows: [
                      new TableRow({
                        children: [
                          new TableCell({
                            borders: noBorders,
                            width: { size: 5340, type: WidthType.DXA },
                            children: [new Paragraph({ children: [new TextRun('单位（盖章）：________________')] })],
                          }),
                          new TableCell({
                            borders: noBorders,
                            width: { size: 3560, type: WidthType.DXA },
                            children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun('年    月    日')] })],
                          }),
                        ],
                      }),
                    ],
                  }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync('/Users/apple/.openclaw/workspace/tmp/实习单位鉴定意见_彭术罡.docx', buffer);
  console.log('ok');
});
