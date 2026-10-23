const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, ImageRun, Header, Table, TableRow, TableCell,
  WidthType, AlignmentType, VerticalAlign, BorderStyle } = require('docx');

const FONT = 'Times New Roman', GREY = '4D4D4D';
const none = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none };
const line = (text, size, after = 0) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 0, after, line: 260 },
  children: [new TextRun({ text, bold: true, font: FONT, size, color: GREY })],
});

const LOGO_W = 1800, TEXT_W = 8398, TABLE_W = LOGO_W + TEXT_W; // A4 width minus 0.75" margins = 10198 DXA
const header = new Header({ children: [
  new Table({
    width: { size: TABLE_W, type: WidthType.DXA }, columnWidths: [LOGO_W, TEXT_W], borders: noBorders,
    rows: [new TableRow({ children: [
      new TableCell({ width: { size: LOGO_W, type: WidthType.DXA }, borders: noBorders, verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new ImageRun({
          type: 'png', data: fs.readFileSync('bbs_logo.png'), transformation: { width: 72, height: 114 },
          altText: { title: 'BBS logo', description: 'Borneo Brave Stone logo', name: 'logo' } })] })] }),
      new TableCell({ width: { size: TEXT_W, type: WidthType.DXA }, borders: noBorders, verticalAlign: VerticalAlign.CENTER,
        children: [
          line('Borneo Brave Stone Sdn. Bhd.', 48, 60),
          line('202001016006(1372326-K)', 24, 20),
          line('L412 (SL 14) Taman Koppes, Jalan Bako,', 21),
          line('93050 Kuching Sarawak.', 21),
          line('No Tel : 019 889 8840 Email : borneobravestone@gmail.com', 21),
        ] }),
    ] })],
  }),
  new Paragraph({ spacing: { before: 120, after: 0 }, children: [] }),
] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 2700, bottom: 1080, left: 1080, right: 1080, header: 500 } } },
    headers: { default: header },
    children: [new Paragraph({ children: [] })],
  }],
});
Packer.toBuffer(doc).then(b => fs.writeFileSync('Borneo_Brave_Stone_Letterhead.docx', b));
