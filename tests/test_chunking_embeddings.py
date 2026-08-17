from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.chunking import chunk_text
from app.embeddings import FallbackEmbeddingProvider, MockEmbeddingProvider, provider_from_name


def test_chunking_is_deterministic_and_bounded() -> None:
    text = "alpha " * 1000
    first = chunk_text("p1", text, max_chars=100, overlap=10)
    second = chunk_text("p1", text, max_chars=100, overlap=10)
    assert first == second
    assert all(len(chunk.text) <= 100 for chunk in first)
    assert len({chunk.chunk_id for chunk in first}) == len(first)


def test_mock_embeddings_are_deterministic_and_1536_dimensional() -> None:
    provider = MockEmbeddingProvider()
    assert provider.embed(["same"])[0] == provider.embed(["same"])[0]
    assert len(provider.embed(["same"])[0]) == 1536


def test_provider_fallback_and_cloud_configuration_guard() -> None:
    class Broken:
        name = "broken"

        def embed(self, texts):
            raise RuntimeError("provider failed")

    assert len(FallbackEmbeddingProvider(Broken(), MockEmbeddingProvider()).embed(["x"])[0]) == 1536
    with pytest.raises(RuntimeError):
        provider_from_name("gemini")

