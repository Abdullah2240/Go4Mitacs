"""Read-only public project corpus fallback for local-first mode."""

import json
from functools import lru_cache
from typing import Any

from .config import settings


@lru_cache(maxsize=1)
def load_local_projects() -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    with settings.normalized_projects_path.open("r", encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            records.append({
                "project_id": record.get("id"),
                "title": (record.get("metadata") or {}).get("ProjectTitle", record.get("id")),
                "text": record.get("text", ""),
                "metadata": record.get("metadata") or {},
                "source_url": (record.get("source") or {}).get("url"),
                "source_retrieved_at": (record.get("source") or {}).get("retrieved_at"),
            })
    return tuple(records)
