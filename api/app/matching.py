"""Deterministic, evidence-first full-corpus retrieval; no LLM or embeddings."""

import math
import re
from typing import Any

from .embeddings import EmbeddingProvider


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


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    norm_left = math.sqrt(sum(a * a for a in left)) or 1.0
    norm_right = math.sqrt(sum(b * b for b in right)) or 1.0
    return dot / (norm_left * norm_right)


def rank_projects_semantic(
    projects: list[dict[str, Any]],
    evidence_text: str,
    provider: EmbeddingProvider,
    *,
    limit: int = 15,
    filters: dict[str, str | None] | None = None,
    keyword_weight: float = 0.5,
) -> list[dict[str, Any]]:
    """Blend real embedding similarity with the deterministic keyword baseline.

    Keyword overlap alone misses conceptually-matching projects that use different
    vocabulary (e.g. "PyTorch" vs "deep learning frameworks"); embeddings alone can
    over-reward vague topical similarity with no real evidence. Blending keeps both
    signals honest.
    """
    keyword_ranked = {item["project_id"]: item for item in rank_projects(projects, evidence_text, limit=len(projects) or 1, filters=filters)}
    if not keyword_ranked:
        return []

    surviving = [project for project in projects if (project.get("project_id") or project.get("id")) in keyword_ranked]
    project_texts = [
        " ".join([project.get("title", ""), project.get("text", ""), json_metadata(project.get("metadata") or {})])
        for project in surviving
    ]
    evidence_vector, *project_vectors = provider.embed([evidence_text, *project_texts])

    semantic_weight = 1.0 - keyword_weight
    ranked = []
    for project, project_vector in zip(surviving, project_vectors):
        project_id = project.get("project_id") or project.get("id")
        baseline = keyword_ranked[project_id]
        semantic_score = round(max(0.0, _cosine_similarity(evidence_vector, project_vector)) * 100, 4)
        blended = round(baseline["score"] * keyword_weight + semantic_score * semantic_weight, 4)
        ranked.append({
            **baseline,
            "score": blended,
            "score_breakdown": {**baseline["score_breakdown"], "semantic_similarity": semantic_score},
            "group": "ambitious" if blended >= 70 else "strong-fit" if blended >= 35 else "reliable",
        })
    return sorted(ranked, key=lambda item: (-item["score"], str(item["project_id"])))[:limit]
