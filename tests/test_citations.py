from modules.citation_engine import citation_reference, verify_citations


def test_citation_with_page():
    source = {"source_filename": "paper.pdf", "page_number": 14, "section": None}
    assert citation_reference(1, source) == "[1] paper.pdf - Page 14"


def test_citation_without_page():
    source = {"source_filename": "notes.docx", "page_number": None, "section": "Paragraph 2"}
    assert citation_reference(2, source) == "[2] notes.docx - Paragraph 2"


def test_verify_citations_filters_unreferenced_sources():
    sources = [
        {"source_filename": "a.pdf", "page_number": 1, "section": None},
        {"source_filename": "b.pdf", "page_number": 2, "section": None},
    ]
    answer, verified = verify_citations("Supported only by [2].", sources)
    assert answer == "Supported only by [2]."
    assert verified == [sources[1]]
