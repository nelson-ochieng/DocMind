from pathlib import Path

from modules.chunker import chunk_document, split_text


def test_chunking_and_overlap():
    chunks = split_text("A " * 1000, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert chunks[0] == chunks[0].strip()


def test_chunk_metadata():
    chunks = chunk_document(
        Path("paper.pdf"),
        "document123",
        [{"page_number": 3, "text": "A finding from the paper.", "section": None}],
    )
    assert chunks[0]["document_id"] == "document123"
    assert chunks[0]["source_filename"] == "paper.pdf"
    assert chunks[0]["page_number"] == 3


def test_chunk_ids_are_deterministic():
    pages = [{"page_number": 1, "text": "Stable text.", "section": None}]
    first = chunk_document(Path("paper.pdf"), "document123", pages)
    second = chunk_document(Path("paper.pdf"), "document123", pages)
    assert first[0]["chunk_id"] == second[0]["chunk_id"]
