"""Read-only public project search for local-only mode."""

from typing import Any

from fastapi import HTTPException

from .local_projects import load_local_projects


def search_projects(*, query: str | None, province: str | None, university: str | None, language: str | None, limit: int, offset: int) -> dict[str, Any]:
    records = list(load_local_projects())
    if query:
        needle = query.casefold()
        records = [record for record in records if needle in f"{record['title']} {record['text']}".casefold()]
    if province:
        records = [record for record in records if record["metadata"].get("Province") == province]
    if university:
        records = [record for record in records if record["metadata"].get("Professor.UniversityName") == university]
    if language:
        records = [record for record in records if record["metadata"].get("LanguageUsed") == language]
    records.sort(key=lambda record: str(record["project_id"]))
    items = [{key: record[key] for key in ("project_id", "title", "metadata", "source_url", "source_retrieved_at")} for record in records[offset:offset + limit]]
    return {"items": items, "total": len(records), "limit": limit, "offset": offset}


def get_project(project_id: str) -> dict[str, Any]:
    record = next((item for item in load_local_projects() if item["project_id"] == project_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="project not found")
    return record
