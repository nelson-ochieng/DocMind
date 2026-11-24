from __future__ import annotations


def citation_reference(index: int, source: dict) -> str:
    location = f"Page {source['page_number']}" if source.get("page_number") not in (None, -1) else (
        source.get("section") or "Section not numbered"
    )
    return f"[{index}] {source['source_filename']} - {location}"


def verify_citations(answer: str, sources: list[dict]) -> tuple[str, list[dict]]:
    verified = []
    for index, source in enumerate(sources, start=1):
        marker = f"[{index}]"
        if marker in answer:
            verified.append(source)
    if not verified:
        return answer, []
    return answer, verified
