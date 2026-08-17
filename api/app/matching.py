"""Deterministic, evidence-first matching baseline; no LLM or embeddings."""

import re
from typing import Any


TOKEN = re.compile(r"[a-z0-9][a-z0-9+#./-]{1,}", re.I)


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in TOKEN.findall(value or "")}


def rank_projects(projects: list[dict[str, Any]], evidence_text: str, *, limit: int = 15) -> list[dict[str, Any]]:
    evidence = _tokens(evidence_text)
    ranked = []
    for project in projects:
        metadata = project.get("metadata") or {}
        text = " ".join([project.get("title", ""), project.get("text", ""), json_metadata(metadata)])
        project_tokens = _tokens(text)
        overlap = sorted(evidence & project_tokens)
        keyword_score = min(1.0, len(overlap) / max(1, min(12, len(evidence))))
        score = round(keyword_score * 100, 4)
        ranked.append({
            "project_id": project.get("project_id") or project.get("id"),
            "title": project.get("title") or metadata.get("ProjectTitle"),
            "score": score,
            "group": "ambitious" if score >= 70 else "strong-fit" if score >= 35 else "reliable",
            "matched_evidence": overlap[:20],
            "missing_evidence": [] if overlap else ["No exact evidence terms matched"],
            "risks": ["Deterministic keyword baseline; semantic fit is not yet evaluated"] if score < 70 else [],
        })
    return sorted(ranked, key=lambda item: (-item["score"], str(item["project_id"])))[:limit]


def json_metadata(metadata: dict[str, Any]) -> str:
    return " ".join(str(value) for value in metadata.values() if isinstance(value, (str, int, float)))

