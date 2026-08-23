"""Provider-neutral, server-side embedding contracts with a deterministic mock."""

from collections.abc import Sequence
import hashlib
import math
import os
from typing import Protocol

from .vectors import EMBEDDING_DIMENSION, validate_embedding


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class OpenAIEmbeddingProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.embeddings.create(model=self.model, input=list(texts))
        return [validate_embedding(item.embedding) for item in response.data]


class MockEmbeddingProvider:
    name = "mock"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = text.encode("utf-8")
            values: list[float] = []
            counter = 0
            while len(values) < EMBEDDING_DIMENSION:
                digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
                values.extend((byte / 127.5) - 1.0 for byte in digest)
                counter += 1
            vector = validate_embedding(values[:EMBEDDING_DIMENSION])
            norm = math.sqrt(sum(value * value for value in vector)) or 1.0
            vectors.append([value / norm for value in vector])
        return vectors


class FallbackEmbeddingProvider:
    def __init__(self, primary: EmbeddingProvider, fallback: EmbeddingProvider):
        self.primary = primary
        self.fallback = fallback
        self.name = f"{primary.name}->{fallback.name}"

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        try:
            return self.primary.embed(texts)
        except Exception:
            return self.fallback.embed(texts)


def provider_from_name(name: str) -> EmbeddingProvider:
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockEmbeddingProvider()
    if normalized == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("openai provider requires OPENAI_API_KEY to be set")
        return OpenAIEmbeddingProvider(api_key=api_key)
    if normalized in {"openrouter", "gemini", "huggingface"}:
        raise RuntimeError(f"{normalized} provider is not enabled without an explicit server-side credential")
    raise ValueError(f"unknown embedding provider: {name}")


def default_provider() -> EmbeddingProvider:
    if os.getenv("OPENAI_API_KEY"):
        return FallbackEmbeddingProvider(provider_from_name("openai"), MockEmbeddingProvider())
    return MockEmbeddingProvider()

