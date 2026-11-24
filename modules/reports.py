from pathlib import Path
from xml.sax.saxutils import escape

def save_report(path,messages):
    path=Path(path); lines=[]
    for m in messages:
        lines.extend([m['role'].title(),m['content']])
        for i,s in enumerate(m.get('sources',[]),1): lines.append(f"[{s.get('citation_id',i)}] {s['source_filename']} | page {s.get('page_number')} | {s.get('section')}: {s['chunk_text']}")
    if path.suffix.lower()=='.docx':
        from docx import Document
        doc=Document(); doc.add_heading('DocMind research report',0)
        for line in lines: doc.add_paragraph(line)
        doc.save(path)
    elif path.suffix.lower()=='.pdf':
        from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        style=getSampleStyleSheet(); story=[Paragraph('DocMind research report',style['Title'])]
        for line in lines:
            for part in line.splitlines(): story.extend([Paragraph(escape(part),style['BodyText']),Spacer(1,5)])
        SimpleDocTemplate(str(path)).build(story)
    else: path.write_text('\n\n'.join(lines),encoding='utf-8')
