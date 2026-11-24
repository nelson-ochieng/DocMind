import config
from modules.rag_engine import RAGEngine
from modules.llm import generate
from modules.embeddings import embed_text


SUMMARY_TYPES = {
    "Executive summary": "Provide a concise executive summary.",
    "Key findings": "Extract the key findings.",
    "Methodology": "Summarize the methodology.",
    "Recommendations": "Extract recommendations.",
}


def summarize_document(
    rag: RAGEngine,
    document_ids: list[str],
    summary_type: str,
    model: str = config.LLM_MODEL,
    temperature: float = 0.1,
) -> dict:
    instruction = SUMMARY_TYPES.get(summary_type, "Summarize the document.")
    query_embedding = embed_text(instruction)
    sources = rag.store.search(query_embedding, top_k=12, document_ids=document_ids)
    sources = [item for item in sources if item["similarity"] >= 0.20]
    if not sources:
        return {"answer": "There was not enough document evidence to create this summary.", "sources": []}
    context = "\n\n".join(
        f"[{i}] {item['source_filename']} - {('Page ' + str(item['page_number'])) if item.get('page_number', -1) != -1 else (item.get('section') or 'Unnumbered')}\n{item['chunk_text']}"
        for i, item in enumerate(sources, 1)
    )
    prompt = (
        f"{instruction} Use only the evidence below. Cite claims with source numbers. "
        "Do not invent information.\n\nEVIDENCE:\n" + context
    )
    return {"answer": generate(prompt, model=model, temperature=temperature), "sources": sources}
