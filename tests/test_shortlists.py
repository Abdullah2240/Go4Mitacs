from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.main import app


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase" / "migrations" / "20260818000004_candidate_shortlists.sql"
ROLLBACK = ROOT / "supabase" / "rollback" / "20260818000004_candidate_shortlists.sql"


def test_shortlist_migration_is_additive_and_private() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")
    assert "CREATE TABLE IF NOT EXISTS candidate_shortlists" in sql
    assert "CREATE TABLE IF NOT EXISTS candidate_shortlist_items" in sql
    assert "REFERENCES candidate_profiles(id, owner_id)" in sql
    assert "REFERENCES mitacs_projects(project_id)" in sql
    assert "UNIQUE (shortlist_id, project_id)" in sql
    assert sql.count("ENABLE ROW LEVEL SECURITY") == 2
    assert sql.count("TO authenticated") >= 4
    assert "REVOKE ALL ON TABLE candidate_shortlists FROM anon" in sql
    assert "REVOKE ALL ON TABLE candidate_shortlist_items FROM anon" in sql
    assert "ALTER TABLE mitacs_projects" not in sql
    assert "DROP TABLE IF EXISTS candidate_shortlist_items" in ROLLBACK.read_text(encoding="utf-8")
    assert "DROP TABLE IF EXISTS candidate_shortlists" in ROLLBACK.read_text(encoding="utf-8")


def test_shortlist_routes_require_authentication() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/candidate/shortlists").status_code == 404
    assert client.post("/api/v1/candidate/shortlists", json={"name": "Test"}).status_code == 404
    assert client.get("/api/v1/candidate/shortlists/not-a-user/comparison").status_code == 404


def test_shortlist_sql_is_owner_scoped() -> None:
    source = (ROOT / "api" / "app" / "shortlist_api.py").read_text(encoding="utf-8")
    assert "owner_id = %s" in source
    assert "candidate_shortlist_items WHERE id = %s AND shortlist_id = %s AND owner_id = %s" in source
    assert "SUPABASE_DB_URL" not in source
