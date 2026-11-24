from pathlib import Path

from docx import Document
from pypdf import PdfWriter

from modules.document_processor import extract_document


def test_txt_extraction(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("Private local notes.", encoding="utf-8")
    pages = extract_document(path)
    assert pages[0]["text"] == "Private local notes."
    assert pages[0]["page_number"] is None


def test_docx_extraction(tmp_path: Path):
    path = tmp_path / "report.docx"
    document = Document()
    document.add_paragraph("Research findings.")
    document.save(path)
    pages = extract_document(path)
    assert pages[0]["text"] == "Research findings."
    assert pages[0]["section"] == "Paragraph 1"


def test_empty_pdf_preserves_page_numbers(tmp_path: Path):
    path = tmp_path / "empty.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(path)
    pages = extract_document(path)
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
