from __future__ import annotations

import requests
from collections.abc import Iterator

import config


class LLMError(RuntimeError):
    pass


def ollama_status() -> tuple[bool, str, list[str]]:
    try:
        response = requests.get(f"{config.OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = [item["name"] for item in response.json().get("models", [])]
        return True, "Connected", models
    except requests.RequestException:
        return False, "Ollama is not running", []


def generate(prompt: str, model: str = config.LLM_MODEL, temperature: float = 0.1, schema: dict | None = None) -> str:
    try:
        response = requests.post(
            f"{config.OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, **({"format": schema} if schema else {}), "keep_alive": 0, "think": False, "options": {"temperature": temperature, "num_ctx": 4096, "num_predict": 650}},
            timeout=600,
        )
        response.raise_for_status()
        text = response.json().get("response", "").strip()
        if not text:
            raise LLMError("The local model returned an empty response.")
        return text
    except requests.Timeout as exc:
        raise LLMError("The local model timed out. Try a shorter question or document selection.") from exc
    except requests.RequestException as exc:
        raise LLMError("Could not connect to Ollama. Start Ollama and ensure the model is installed.") from exc


def generate_stream(prompt: str, model: str = config.LLM_MODEL, temperature: float = 0.1) -> Iterator[str]:
    try:
        with requests.post(
            f"{config.OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True, "options": {"temperature": temperature, "num_ctx": 4096, "num_predict": 650}},
            timeout=(10, 180),
            stream=True,
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                import json
                payload = json.loads(line)
                chunk = payload.get("response", "")
                if chunk:
                    yield chunk
    except requests.Timeout as exc:
        raise LLMError("The local model timed out. Try a shorter question or document selection.") from exc
    except requests.RequestException as exc:
        raise LLMError("Could not connect to Ollama. Start Ollama and ensure the model is installed.") from exc
