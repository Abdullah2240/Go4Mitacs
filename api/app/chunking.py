"""Deterministic, bounded text chunks for future retrieval and embeddings."""

from dataclasses import dataclass
import hashlib
import re


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    category: str
    text: str
    content_hash: str
    start_char: int
    end_char: int


def chunk_text(project_id: str, text: str, *, category: str = "overview", max_chars: int = 1800, overlap: int = 200) -> list[TextChunk]:
    if max_chars <= 0 or overlap < 0 or overlap >= max_chars:
        raise ValueError("max_chars must be positive and overlap must be smaller than max_chars")
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(clean):
        end = min(len(clean), start + max_chars)
        if end < len(clean):
            boundary = clean.rfind(" ", start, end)
            if boundary > start + max_chars // 2:
                end = boundary
        chunk = clean[start:end].strip()
        digest = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
        chunk_id = hashlib.sha256(f"{project_id}:{category}:{index}:{digest}".encode("utf-8")).hexdigest()[:32]
        chunks.append(TextChunk(chunk_id, category, chunk, digest, start, end))
        if end >= len(clean):
            break
        start = max(end - overlap, start + 1)
        index += 1
    return chunks

