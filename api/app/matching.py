"""Deterministic, evidence-first full-corpus retrieval; no LLM or embeddings."""

import re
from typing import Any


TOKEN = re.compile(r"[a-z0-9][a-z0-9+#./-]{1,}", re.I)


def _tokens(value: str) -> set[str]:
    return {token.lower() for token in TOKEN.findall(value or "")}


def rank_projects(projects: list[dict[str, Any]], evidence_text: str, *, limit: int = 15, filters: dict[str, str | None] | None = None) -> list[dict[str, Any]]:
    evidence = _tokens(evidence_text)
    filters = filters or {}
    ranked = []
    for project in projects:
        metadata = project.get("metadata") or {}
        research_area = filters.get("research_area")
        if research_area and research_area.casefold() not in project.get("text", "").casefold():
            continue
        if any(value and key != "research_area" and str(metadata.get(key, "")).casefold() != value.casefold() for key, value in filters.items()):
            continue
        text = " ".join([project.get("title", ""), project.get("text", ""), json_metadata(metadata)])
        project_tokens = _tokens(text)
        overlap = sorted(evidence & project_tokens)
        title_overlap = len(evidence & _tokens(project.get("title", "")))
        keyword_score = min(1.0, len(overlap) / max(1, min(18, len(evidence))))
        title_bonus = min(0.15, title_overlap * 0.03)
        score = round(min(100, (keyword_score + title_bonus) * 100), 4)
        ranked.append({
            "project_id": project.get("project_id") or project.get("id"),
            "title": project.get("title") or metadata.get("ProjectTitle"),
            "score": score,
            "score_breakdown": {"keyword_overlap": round(keyword_score * 100, 2), "title_bonus": round(title_bonus * 100, 2)},
            "group": "ambitious" if score >= 70 else "strong-fit" if score >= 35 else "reliable",
            "matched_evidence": overlap[:20],
            "missing_evidence": [] if overlap else ["No exact evidence terms matched"],
            "risks": ["Deterministic lexical retrieval; semantic fit needs human review"] if score < 70 else [],
            "metadata": metadata,
            "source_url": project.get("source_url"),
            "text_preview": project.get("text", "")[:420].replace("\n", " "),
        })
    return sorted(ranked, key=lambda item: (-item["score"], str(item["project_id"])))[:limit]


def json_metadata(metadata: dict[str, Any]) -> str:
    return " ".join(str(value) for value in metadata.values() if isinstance(value, (str, int, float)))
