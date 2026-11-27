from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root = Path(__file__).parent
source = (root / 'two-week-build-schedule.md').read_text(encoding='utf-8')
doc = Document()
section = doc.sections[0]
section.top_margin = section.bottom_margin = Inches(0.65)
section.left_margin = section.right_margin = Inches(0.75)
section.page_width, section.page_height = Inches(8.5), Inches(11)
for name in ['Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3']:
    style = doc.styles[name]
    style.font.name = 'Arial'
    style.font.color.rgb = RGBColor(0, 0, 0)
normal = doc.styles['Normal']
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(3)
normal.paragraph_format.line_spacing = 1.05
for name, size in [('Title', 24), ('Heading 1', 15), ('Heading 2', 11)]:
    doc.styles[name].font.size = Pt(size)
    doc.styles[name].paragraph_format.space_before = Pt(10)
    doc.styles[name].paragraph_format.space_after = Pt(5)
doc.styles['Title'].paragraph_format.space_before = Pt(0)

def clean(text):
    return text.replace('**', '').replace('`', '')

def para(text, checkbox=False):
    p = doc.add_paragraph()
    if checkbox:
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.first_line_indent = Inches(-0.2)
        r = p.add_run('\u2610  ')
        r.font.name = 'Segoe UI Symbol'
    for i, part in enumerate(re.split(r'\*\*(.*?)\*\*', text)):
        r = p.add_run(part.replace('`', ''))
        r.bold = bool(i % 2)
    return p

lines = source.splitlines()
i = 0
while i < len(lines):
    line = lines[i].strip()
    i += 1
    if not line:
        continue
    if line.startswith('|'):
        rows = [line]
        while i < len(lines) and lines[i].strip().startswith('|'):
            rows.append(lines[i].strip()); i += 1
        data = [[clean(c.strip()) for c in row.strip('|').split('|')] for row in rows if not re.match(r'^\|\s*---', row)]
        t = doc.add_table(rows=0, cols=len(data[0]))
        t.style = 'Table Grid'
        for ri, values in enumerate(data):
            cells = t.add_row().cells
            for cell, value in zip(cells, values):
                cell.text = value
                if ri == 0:
                    sh = OxmlElement('w:shd'); sh.set(qn('w:fill'), 'EAEAEA'); cell._tc.get_or_add_tcPr().append(sh)
                    for r in cell.paragraphs[0].runs: r.bold = True
        continue
    if line.startswith('# '):
        doc.add_paragraph('Gesture Controlled Remote', 'Title')
        doc.add_paragraph('Two Week Build Checklist', 'Subtitle')
        doc.styles['Subtitle'].font.color.rgb = RGBColor(0, 0, 0)
    elif line.startswith('## '):
        text = line[3:]
        m = re.match(r'Day (\d+)', text)
        if m and int(m.group(1)) % 2 == 1:
            doc.add_page_break()
        elif text == 'Scope rules':
            doc.add_page_break()
        doc.add_paragraph(text.replace('—', ' ').replace(':', ' '), 'Heading 1')
    elif line.startswith('### '):
        doc.add_paragraph(line[4:], 'Heading 2')
    elif line.startswith('- [ ] '):
        para(line[6:], checkbox=True)
    elif line.startswith('- '):
        para('\u2022  ' + line[2:])
    else:
        para(line)

doc.core_properties.title = 'Gesture Controlled Remote Two Week Build Checklist'
doc.core_properties.subject = 'C on ESP32s and Python server with optional temperature features'
doc.save(root / 'two-week-build-schedule-google-docs.docx')
print('Created document')
