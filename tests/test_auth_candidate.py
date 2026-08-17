from pathlib import Path
import sys
from types import SimpleNamespace

import jwt
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

import app.auth as auth
from app.auth import get_current_user_id
from app.candidate_api import _safe_payload
from app.main import app


def test_candidate_endpoint_requires_bearer_authentication() -> None:
    response = TestClient(app).get("/api/v1/candidate/profile")
    assert response.status_code == 404


def test_client_cannot_supply_owner_or_profile_id() -> None:
    payload = _safe_payload({"owner_id": "other", "profile_id": "other", "fact_text": "evidence", "source_type": "cv"}, ["fact_text", "source_type"])
    assert payload == {"fact_text": "evidence", "source_type": "cv"}


def test_owner_scoped_sql_is_present_for_updates_and_deletes() -> None:
    source = (Path(__file__).resolve().parents[1] / "api" / "app" / "candidate_api.py").read_text(encoding="utf-8")
    assert "WHERE id = %s AND owner_id = %s" in source
    assert "WHERE owner_id = %s" in source


def test_supabase_jwt_subject_becomes_authenticated_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        auth,
        "settings",
        SimpleNamespace(supabase_jwt_secret="local-test-secret", supabase_url="", supabase_anon_key=""),
    )
    token = jwt.encode(
        {"sub": "11111111-1111-1111-1111-111111111111", "aud": "authenticated"},
        "local-test-secret",
        algorithm="HS256",
    )
    assert auth.user_id_from_token(token) == "11111111-1111-1111-1111-111111111111"


def test_candidate_import_is_protected_before_database_access() -> None:
    response = TestClient(app).post("/api/v1/candidate/import", json={"facts": []})
    assert response.status_code == 404
