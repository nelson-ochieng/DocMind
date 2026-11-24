import config
from modules.embeddings import embed_text
from modules.llm import generate
from modules.rag_engine import RAGEngine


def compare_documents(
    rag: RAGEngine,
    document_ids: list[str],
    model: str = config.LLM_MODEL,
    temperature: float = 0.1,
) -> dict:
    if len(document_ids) < 2:
        return {"answer": "Select at least two documents to compare.", "sources": []}
    topics = [
        "research objectives and problem statements",
        "methodology and data sources",
        "results and findings",
        "recommendations and conclusions",
    ]
    evidence = []
    sources_seen = set()
    for topic in topics:
        embedding = embed_text(topic)
        matches = rag.store.search(embedding, top_k=8, document_ids=document_ids)
        for item in matches:
            if item["similarity"] >= 0.25 and item["chunk_id"] not in sources_seen:
                evidence.append(item)
                sources_seen.add(item["chunk_id"])
    if not evidence:
        return {"answer": "I could not find enough comparable evidence in the selected documents.", "sources": []}
    context = "\n\n".join(
        f"[{i}] {item['source_filename']} - {('Page ' + str(item['page_number'])) if item.get('page_number', -1) != -1 else (item.get('section') or 'Unnumbered')}\n{item['chunk_text']}"
        for i, item in enumerate(evidence, 1)
    )
    prompt = (
        "Compare only the selected documents using the evidence below. "
        "Describe objectives, methodology, data sources, findings, recommendations, similarities, and differences. "
        "Do not add general knowledge. Cite every comparison with source numbers.\n\nEVIDENCE:\n" + context
    )
    return {"answer": generate(prompt, model=model, temperature=temperature), "sources": evidence}
