"""Generate the committed, minimized public corpus used by the Vercel app.

Run from the repository root after refreshing matcher-data. The input is public
source data; this script deliberately selects only fields needed by search and
detail routes.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "matcher-data" / "globalink-projects-normalized.jsonl"
DEFAULT_OUTPUT = ROOT / "web" / "data" / "mitacs-projects.public.json"
CORPUS_VERSION = "globalink-normalized-2026-08-17"


def preview(text: str, limit: int = 320) -> str:
    compact = re.sub(r"\s+", " ", text or "").strip()
    return compact if len(compact) <= limit else compact[: limit - 1].rstrip() + "…"


def build_record(record: dict) -> dict:
    metadata = record.get("metadata") or {}
    professor = metadata.get("Professor") or {}
    text = record.get("text", "")
    return {
        "id": str(record.get("id") or metadata.get("ProjectID")),
        "title": metadata.get("ProjectTitle") or record.get("id"),
        "description_preview": preview(text),
        "research_area": preview(text, 180),
        "skills_background": metadata.get("PreferredBackgroundCollection"),
        "supervisor": {
            "first_name": metadata.get("Professor.FirstName") or professor.get("FirstName"),
            "last_name": metadata.get("Professor.LastName") or professor.get("LastName"),
        },
        "university": metadata.get("Professor.UniversityName") or professor.get("UniversityName"),
        "campus": metadata.get("Professor.CampusName") or professor.get("CampusName"),
        "province": metadata.get("Province") or metadata.get("Professor.FacultyProvince"),
        "language": metadata.get("LanguageUsed"),
        "start_date": metadata.get("StartDate"),
        "flexible_start": metadata.get("isStartDateFlexible"),
        "start_notes": metadata.get("NotesOnStartDate"),
        "source_url": (record.get("source") or {}).get("url"),
        "source_retrieved_at": (record.get("source") or {}).get("retrieved_at"),
        "corpus_version": CORPUS_VERSION,
    }


def generate(source: Path = DEFAULT_INPUT, target: Path = DEFAULT_OUTPUT) -> int:
    rows = []
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(build_record(json.loads(line)))
    rows.sort(key=lambda row: row["id"])
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"corpus_version": CORPUS_VERSION, "count": len(rows), "projects": rows}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"generated {generate(args.input, args.output)} public projects at {args.output}")
