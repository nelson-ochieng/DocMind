from __future__ import annotations

import requests

import config


class EmbeddingError(RuntimeError):
    pass


def embed_text(text: str, model: str = config.EMBEDDING_MODEL) -> list[float]:
    if not text.strip():
        raise EmbeddingError("Cannot embed empty text.")
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/embed",
            json={"model": model, "input": text, "keep_alive": 0},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise EmbeddingError("Could not connect to Ollama. Start Ollama and try again.") from exc

    vectors = payload.get("embeddings")
    if not vectors or not isinstance(vectors[0], list):
        raise EmbeddingError("Ollama did not return a valid embedding.")
    return vectors[0]


def embed_batch(texts: list[str], model: str = config.EMBEDDING_MODEL) -> list[list[float]]:
    if not texts:
        return []
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/embed",
            json={"model": model, "input": texts},
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise EmbeddingError("Could not connect to Ollama. Start Ollama and try again.") from exc

    vectors = payload.get("embeddings")
    if not vectors or len(vectors) != len(texts):
        raise EmbeddingError("Ollama did not return embeddings for every text.")
    return vectors
