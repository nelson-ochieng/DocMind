from __future__ import annotations

from datetime import datetime
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import config


def _sources_text(sources: list[dict]) -> list[str]:
    return [
        f"[{index}] {source['source_filename']} - "
        f"{('Page ' + str(source['page_number'])) if source.get('page_number') not in (None, -1) else (source.get('section') or 'Unnumbered')}"
        for index, source in enumerate(sources, 1)
    ]


def export_txt(title: str, content: str, sources: list[dict], filename: str) -> Path:
    path = config.EXPORTS_DIR / filename
    text = f"{title}\nGenerated: {datetime.now().isoformat(timespec='minutes')}\n\n{content}\n\nSources:\n"
    text += "\n".join(_sources_text(sources))
    path.write_text(text, encoding="utf-8")
    return path


def export_docx(title: str, content: str, sources: list[dict], filename: str) -> Path:
    path = config.EXPORTS_DIR / filename
    document = Document()
    document.add_heading(title, 0)
    document.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    document.add_heading("Content", level=1)
    document.add_paragraph(content)
    document.add_heading("Source references", level=1)
    for reference in _sources_text(sources):
        document.add_paragraph(reference)
    document.save(path)
    return path


def export_pdf(title: str, content: str, sources: list[dict], filename: str) -> Path:
    path = config.EXPORTS_DIR / filename
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, title[:90])
    y -= 30
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, y, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 24

    def write_line(text: str, bold: bool = False):
        nonlocal y
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)
        pdf.setFont("Helvetica-Bold" if bold else "Helvetica", 9)
        pdf.drawString(50, y, text[:110])
        y -= 14

    for block in content.split("\n"):
        write_line(block)
    y -= 12
    write_line("Source references", bold=True)
    for reference in _sources_text(sources):
        write_line(reference)
    pdf.save()
    return path
