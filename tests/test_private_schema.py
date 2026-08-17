from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_private_schema import TABLES, validate


def test_private_migration_has_owner_rls_and_rollback_contract() -> None:
    assert validate() == []
    assert len(TABLES) == 9


def test_private_schema_does_not_create_anonymous_policy() -> None:
    migration = (Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "20260818000003_candidate_private_auth.sql").read_text(encoding="utf-8")
    assert "TO anon" not in migration
    assert "TO authenticated" in migration
    assert "owner_id = auth.uid()" in migration


def test_cross_owner_attachment_constraints_are_present() -> None:
    migration = (Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "20260818000003_candidate_private_auth.sql").read_text(encoding="utf-8")
    assert migration.count("FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id)") == 8
    assert "FOREIGN KEY (document_id, owner_id) REFERENCES candidate_documents(id, owner_id)" in migration


def test_public_project_schema_is_not_modified_by_private_migration() -> None:
    migration = (Path(__file__).resolve().parents[1] / "supabase" / "migrations" / "20260818000003_candidate_private_auth.sql").read_text(encoding="utf-8")
    assert "mitacs_projects" not in migration
    assert "project_chunks" not in migration
    assert "import_runs" not in migration
