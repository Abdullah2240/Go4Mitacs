from pathlib import Path
from types import SimpleNamespace
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

import app.local_projects as local_projects
from app.main import app


def test_public_projects_and_local_matching_require_no_auth_or_database(monkeypatch) -> None:
    root = Path(__file__).resolve().parents[1]
    settings = SimpleNamespace(normalized_projects_path=root / "matcher-data" / "globalink-projects-normalized.jsonl")
    monkeypatch.setattr(local_projects, "settings", settings)
    local_projects.load_local_projects.cache_clear()
    client = TestClient(app)
    projects_response = client.get("/api/v1/projects", params={"limit": 1})
    assert projects_response.status_code == 200
    assert projects_response.json()["total"] > 0
    match_response = client.post("/api/v1/local/matches", json={"evidence_text": "Python data analysis"})
    assert match_response.status_code == 200
    assert match_response.json()["method"] == "deterministic-full-corpus-keyword-retrieval"
    assert match_response.json()["considered"] == 3359


def test_cloud_matching_is_not_an_active_route() -> None:
    response = TestClient(app).get("/api/v1/matches")
    assert response.status_code == 404
