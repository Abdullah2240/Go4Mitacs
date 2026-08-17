"""Static validation for the candidate/private auth migration.

This intentionally does not connect to Supabase or apply migrations.
"""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase" / "migrations" / "20260818000003_candidate_private_auth.sql"
ROLLBACK = ROOT / "api" / "migrations" / "003_candidate_private_auth.down.sql"
TABLES = [
    "candidate_profiles", "candidate_facts", "candidate_documents",
    "candidate_document_chunks", "candidate_skills", "candidate_experience",
    "candidate_projects", "candidate_certificates", "candidate_research",
]


def validate() -> list[str]:
    sql = MIGRATION.read_text(encoding="utf-8")
    rollback = ROLLBACK.read_text(encoding="utf-8")
    errors: list[str] = []
    for table in TABLES:
        if not re.search(rf"CREATE TABLE IF NOT EXISTS {table}\s*\(", sql):
            errors.append(f"missing table: {table}")
        if not re.search(rf"{table}.*?owner_id UUID NOT NULL REFERENCES auth\.users\(id\)", sql, re.S):
            errors.append(f"missing auth.users owner reference: {table}")
        if not re.search(rf"'{table}'.*?ENABLE ROW LEVEL SECURITY", sql, re.S):
            errors.append(f"missing RLS enablement: {table}")
        if not re.search(rf"'{table}'.*?REVOKE ALL ON TABLE public\.%I FROM anon", sql, re.S):
            errors.append(f"missing anonymous revoke: {table}")
    if "CREATE POLICY" not in sql or "TO authenticated" not in sql or "owner_id = auth.uid()" not in sql:
        errors.append("missing authenticated owner policy contract")
    if "REVOKE ALL ON TABLE public.%I FROM PUBLIC" not in sql or "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.%I TO authenticated" not in sql:
        errors.append("missing explicit public revoke/authenticated grant")
    if re.search(r"CREATE POLICY.*TO anon", sql, re.S | re.I):
        errors.append("anonymous policy found")
    for table in TABLES:
        if f"DROP TABLE IF EXISTS {table}" not in rollback:
            errors.append(f"missing rollback: {table}")
    for table in TABLES[1:]:
        if f"FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id)" not in sql and table != "candidate_document_chunks":
            errors.append(f"missing composite profile ownership constraint: {table}")
    if "FOREIGN KEY (document_id, owner_id) REFERENCES candidate_documents(id, owner_id)" not in sql:
        errors.append("missing composite document ownership constraint")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("private schema validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"private schema validation passed: {len(TABLES)} private tables checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
