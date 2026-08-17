"""Local structured candidate-evidence import contracts; no file upload or AI calls."""

from dataclasses import dataclass
import hashlib
from typing import Any

from .chunking import chunk_text


@dataclass(frozen=True)
class EvidenceChunk:
    chunk_id: str
    source_ref: str
    text: str
    content_hash: str
    start_char: int
    end_char: int


def validate_candidate_payload(payload: Any) -> list[dict[str, Any]]:
    records = payload.get("facts") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError("candidate JSON must contain a facts list")
    valid: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict) or not record.get("fact_text") or not record.get("source_type"):
            raise ValueError("each candidate fact requires fact_text and source_type")
        if "confidence" in record and record["confidence"] is not None and not 0 <= float(record["confidence"]) <= 1:
            raise ValueError("candidate confidence must be between 0 and 1")
        valid.append({key: value for key, value in record.items() if key != "owner_id"})
    return valid


def chunk_evidence(source_ref: str, text: str, *, max_chars: int = 1200) -> list[EvidenceChunk]:
    chunks = chunk_text(source_ref, text, category="candidate_evidence", max_chars=max_chars, overlap=120)
    return [EvidenceChunk(chunk.chunk_id, source_ref, chunk.text, chunk.content_hash, chunk.start_char, chunk.end_char) for chunk in chunks]
