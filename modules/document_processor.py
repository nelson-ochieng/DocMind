from __future__ import annotations

import hashlib
import re
import logging
from pathlib import Path

from docx import Document
from pypdf import PdfReader

logger = logging.getLogger("docmind")


class DocumentProcessingError(RuntimeError):
    pass


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name[:180] or "document"


def document_id(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.name.encode("utf-8"))
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()[:16]


def extract_pdf(path: Path) -> list[dict]:
    try:
        reader = PdfReader(str(path))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            cleaned = text.strip()
            if cleaned:
                pages.append({"page_number": index, "text": cleaned, "section": None})
                continue
            try:
                import fitz
                import pytesseract
                from PIL import Image
                from io import BytesIO

                pdf = fitz.open(str(path))
                pix = pdf[index - 1].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(BytesIO(pix.tobytes("png")))
                cleaned = pytesseract.image_to_string(image).strip()
                pdf.close()
            except ImportError:
                cleaned = ""
            except Exception as exc:
                cleaned = ""
                logger.warning("OCR failed for %s page %s: %s", path.name, index, exc)
            pages.append({"page_number": index, "text": cleaned, "section": "OCR text" if cleaned else "No extractable text"})
        return pages
    except Exception as exc:
        raise DocumentProcessingError(f"Could not read PDF '{path.name}'.") from exc


def extract_docx(path: Path) -> list[dict]:
    try:
        doc = Document(str(path))
        sections = []
        for index, block in enumerate(doc.element.body, start=1):
            if block.tag.endswith("p"):
                paragraph = next((item for item in doc.paragraphs if item._p is block), None)
                if paragraph is None:
                    continue
                text = paragraph.text.strip()
                if text:
                    heading = f"Heading: {text}" if paragraph.style.name.startswith("Heading") else f"Paragraph {index}"
                    sections.append({"page_number": None, "text": text, "section": heading})
            elif block.tag.endswith("tbl"):
                for row_index, row in enumerate(next(
                    (table.rows for table in doc.tables if table._tbl is block),
                    (),
                ), start=1):
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        sections.append({
                            "page_number": None,
                            "text": row_text,
                            "section": f"Table row {row_index}",
                        })
        return sections
    except Exception as exc:
        raise DocumentProcessingError(f"Could not read DOCX '{path.name}'.") from exc


def extract_txt(path: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as exc:
        raise DocumentProcessingError(f"Could not read text file '{path.name}'.") from exc
    return [{"page_number": None, "text": text.strip(), "section": None}]


def extract_document(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(path)
    if suffix == ".docx":
        return extract_docx(path)
    if suffix == ".txt":
        return extract_txt(path)
    raise DocumentProcessingError(f"Unsupported document format: {suffix}")
