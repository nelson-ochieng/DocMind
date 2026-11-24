from __future__ import annotations

from pathlib import Path

import chromadb

import config
from modules.embeddings import embed_batch


class VectorStoreError(RuntimeError):
    pass


class VectorStore:
    def __init__(self, db_path: Path | None = None):
        try:
            self.client = chromadb.PersistentClient(path=str(db_path or config.DATABASE_DIR))
            self.collection = self.client.get_or_create_collection(
                name=config.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise VectorStoreError("Could not initialize the local vector database.") from exc

    def has_document(self, document_id: str) -> bool:
        result = self.collection.get(where={"document_id": document_id}, limit=1)
        return bool(result["ids"])

    def add_chunks(self, chunks: list[dict], batch_size: int = 20) -> int:
        if not chunks:
            return 0
        indexed = 0
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start:start + batch_size]
            embeddings = embed_batch([item["chunk_text"] for item in batch])
            ids = [item["chunk_id"] for item in batch]
            texts = [item["chunk_text"] for item in batch]
            metadatas = [{
                "document_id": item["document_id"],
                "source_filename": item["source_filename"],
                "page_number": item["page_number"] if item["page_number"] is not None else -1,
                "section": item["section"] or "",
                "chunk_index": item["chunk_index"],
            } for item in batch]
            self.collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
            indexed += len(batch)
        return indexed

    def search(self, query_embedding: list[float], top_k: int = 5, document_ids: list[str] | None = None) -> list[dict]:
        where = None
        if document_ids:
            where = {"document_id": document_ids[0]} if len(document_ids) == 1 else {"$or": [{"document_id": item} for item in document_ids]}
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        ids = result["ids"][0] if result["ids"] else []
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            output.append({
                "chunk_id": chunk_id,
                "chunk_text": text,
                "similarity": 1.0 - distance,
                "distance": distance,
                **metadata,
            })
        return output

    def delete_document(self, document_id: str) -> int:
        result = self.collection.get(where={"document_id": document_id})
        ids = result["ids"]
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def replace_document(self, chunks: list[dict]) -> int:
        if not chunks:
            raise VectorStoreError("Cannot replace a document with no chunks.")
        document_id = chunks[0]["document_id"]
        old_result = self.collection.get(where={"document_id": document_id}, include=[])
        count = self.add_chunks(chunks)
        new_ids = {item["chunk_id"] for item in chunks}
        stale_ids = [chunk_id for chunk_id in old_result["ids"] if chunk_id not in new_ids]
        if stale_ids:
            self.collection.delete(ids=stale_ids)
        return count

    def count(self) -> int:
        return self.collection.count()

    def document_count(self) -> int:
        return len(self.collection.get(include=[])["ids"]) if self.count() == 0 else len({
            metadata["document_id"]
            for metadata in self.collection.get(include=["metadatas"])["metadatas"]
        })

    def list_documents(self) -> dict[str, dict]:
        if self.count() == 0:
            return {}
        result = self.collection.get(include=["metadatas"])
        documents: dict[str, dict] = {}
        for metadata in result["metadatas"]:
            document_id = metadata["document_id"]
            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "source_filename": metadata["source_filename"],
                    "chunks": 0,
                    "pages": 0,
                }
            documents[document_id]["chunks"] += 1
            page = metadata["page_number"]
            if page != -1:
                documents[document_id]["pages"] = max(documents[document_id]["pages"], page)
        return {
            metadata["source_filename"]: metadata
            for metadata in documents.values()
        }

    def all_chunks(self, document_ids=None):
        where = {"document_id": {"$in": document_ids}} if document_ids else None
        result = self.collection.get(where=where, include=["documents", "metadatas"])
        return [{"chunk_id": i, "chunk_text": t, **m} for i,t,m in zip(result["ids"],result["documents"],result["metadatas"])]
