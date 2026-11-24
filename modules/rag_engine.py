from __future__ import annotations

import config
from modules.embeddings import embed_text
from modules.llm import generate
from modules.vector_store import VectorStore
from modules.citation_engine import verify_citations
import re


class RAGEngine:
    def __init__(self, vector_store: VectorStore | None = None):
        self.store = vector_store or VectorStore()

    def ask(
        self,
        question: str,
        document_ids: list[str] | None = None,
        top_k: int = config.TOP_K,
        threshold: float = config.SIMILARITY_THRESHOLD,
        history: list[dict] | None = None,
        model: str = config.LLM_MODEL,
        temperature: float = 0.1,
    ) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("Question cannot be empty.")

        from modules.research import rank
        from modules.structured import answer as structured_answer, SCHEMA
        deep = bool(re.search(r"method|research|compar|critical|workflow|analy|limitation|summari|flowchart|mind map", question, re.I))
        rows = [r for r in self.store.all_chunks(document_ids) if not re.search(r"^(references|bibliography|declarations?|acknowledg)", r.get("section") or "", re.I)]
        semantic = self.store.search(embed_text(question), top_k=40, document_ids=document_ids) if rows else []
        sources = rank(question, rows, semantic, deep, 24 if deep else top_k)
        if deep and re.search(r'method|workflow|procedure',question,re.I):
            methods = [r for r in rows if re.search(r'method|study area|instrument|validation',r.get('section') or '',re.I)]
            if methods:
                methods.sort(key=lambda r:(r['document_id'],r.get('page_number') or 0,r.get('chunk_index',0)))
                seen={r['chunk_id'] for r in methods}
                sources=methods+[r for r in sources if r['chunk_id'] not in seen][:8]
        if history and re.search(r'^(and |what about|explain that|expand|why|how so)',question,re.I):
            previous=next((m['content'] for m in reversed(history) if m['role']=='user'),'')
            question=previous[:500]+' — Follow-up: '+question
        if not sources:
            return {"answer": "No relevant evidence found in the selected documents.", "sources": []}
        answer = structured_answer(question, sources, lambda p: generate(p, model=model, temperature=temperature, schema=SCHEMA), deep)
        for i, source in enumerate(sources,1): source["citation_id"] = i
        return {"answer": answer, "sources": sources}
