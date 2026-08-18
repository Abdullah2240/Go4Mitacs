from fastapi import FastAPI, Query

from .health import readiness
from .projects import get_project, search_projects
from .matching import rank_projects
from .local_projects import load_local_projects


app = FastAPI(title="Mitacs Matcher API", version="0.1.0")


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def ready() -> dict:
    return readiness()


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"live": {"status": "ok"}, "ready": readiness()}


@app.get("/api/v1/projects", tags=["projects"])
def projects(
    q: str | None = None,
    province: str | None = None,
    university: str | None = None,
    language: str | None = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict:
    return search_projects(query=q, province=province, university=university, language=language, limit=limit, offset=offset)


@app.get("/api/v1/projects/{project_id}", tags=["projects"])
def project(project_id: str) -> dict:
    return get_project(project_id)


@app.post("/api/v1/local/matches", tags=["matching"])
def local_matches(payload: dict, limit: int = Query(15, ge=1, le=50)) -> dict:
    """Run deterministic matching without external provider calls."""
    evidence_text = payload.get("evidence_text", "")
    if not isinstance(evidence_text, str):
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="evidence_text must be text")
    filters = payload.get("filters") if isinstance(payload.get("filters"), dict) else {}
    allowed = {key: filters.get(key) for key in ("Province", "Professor.UniversityName", "research_area")}
    items = rank_projects(list(load_local_projects()), evidence_text, limit=limit, filters=allowed)
    return {"items": items, "method": "deterministic-full-corpus-keyword-retrieval", "considered": len(load_local_projects()), "filtered": bool(filters), "corpus_version": "globalink-normalized-2026-08-17"}
