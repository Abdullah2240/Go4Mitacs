"""Read-only post-apply verification for candidate/private Supabase tables."""

import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.env import load_repo_dotenv


load_repo_dotenv()


TABLES = [
    "candidate_profiles", "candidate_facts", "candidate_documents",
    "candidate_document_chunks", "candidate_skills", "candidate_experience",
    "candidate_projects", "candidate_certificates", "candidate_research",
]
PUBLIC_TABLES = ["mitacs_projects", "project_chunks", "import_runs"]


def main() -> int:
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise SystemExit("SUPABASE_DB_URL is not set")
    import psycopg

    with psycopg.connect(db_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = ANY(%s)
                ORDER BY table_name
                """,
                (TABLES,),
            )
            existing = [row[0] for row in cursor.fetchall()]
            cursor.execute(
                """
                SELECT c.relname, c.relrowsecurity
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relname = ANY(%s)
                ORDER BY c.relname
                """,
                (TABLES,),
            )
            rls = {name: enabled for name, enabled in cursor.fetchall()}
            cursor.execute(
                """
                SELECT tablename, policyname, roles::text, qual::text, with_check::text
                FROM pg_policies
                WHERE schemaname = 'public' AND tablename = ANY(%s)
                ORDER BY tablename
                """,
                (TABLES,),
            )
            policies = [dict(zip(("table", "name", "roles", "qual", "with_check"), row)) for row in cursor.fetchall()]
            anon_select = {}
            auth_select = {}
            for table in TABLES:
                cursor.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", ("anon", f"public.{table}"))
                anon_select[table] = cursor.fetchone()[0]
                cursor.execute("SELECT has_table_privilege(%s, %s, 'SELECT')", ("authenticated", f"public.{table}"))
                auth_select[table] = cursor.fetchone()[0]
            cursor.execute(
                "SELECT COUNT(*), COUNT(DISTINCT project_id) FROM mitacs_projects"
            )
            public_project_count, public_project_ids = cursor.fetchone()
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = ANY(%s)",
                (PUBLIC_TABLES,),
            )
            public_tables = sorted(row[0] for row in cursor.fetchall())

    owner_policies = {
        policy["table"]: policy
        for policy in policies
        if "authenticated" in policy["roles"]
        and "owner_id = auth.uid()" in (policy["qual"] or "")
        and "owner_id = auth.uid()" in (policy["with_check"] or "")
    }
    result = {
        "private_tables": existing,
        "rls_enabled": rls,
        "authenticated_owner_policies": sorted(owner_policies),
        "anon_select_privileges": anon_select,
        "authenticated_select_privileges": auth_select,
        "public_tables": public_tables,
        "public_project_count": public_project_count,
        "public_project_ids": public_project_ids,
    }
    if sorted(existing) != sorted(TABLES):
        raise SystemExit("verification failed: private table set is incomplete")
    if any(not rls.get(table, False) for table in TABLES):
        raise SystemExit("verification failed: RLS is not enabled on every private table")
    if sorted(owner_policies) != sorted(TABLES):
        raise SystemExit("verification failed: authenticated owner policies are incomplete")
    if any(anon_select.values()):
        raise SystemExit("verification failed: anon has SELECT privilege on a private table")
    print(json.dumps({"status": "ok", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
