from __future__ import annotations

from pathlib import Path
import hashlib


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between zero and chunk_size")

    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary >= start + chunk_size // 2:
                end = boundary + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def chunk_document(path: Path, document_id: str, pages: list[dict], chunk_size: int = 1000, overlap: int = 150) -> list[dict]:
    chunks = []
    chunk_index = 0
    from modules.research import sections
    for page in sections(pages):
        page_chunks = split_text(page["text"], chunk_size, overlap)
        for chunk_text in page_chunks:
            chunks.append({
                "chunk_id": hashlib.sha256(
                    f"{document_id}\0{chunk_index}\0{chunk_text}".encode("utf-8")
                ).hexdigest()[:32],
                "document_id": document_id,
                "source_filename": path.name,
                "page_number": page["page_number"],
                "section": page["section"],
                "chunk_text": chunk_text,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
    return chunks
