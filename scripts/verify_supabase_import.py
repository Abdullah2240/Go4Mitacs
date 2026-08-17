"""Read-only verification for the 100-record Supabase smoke import."""

import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.env import load_repo_dotenv


load_repo_dotenv()

TABLES = ["source_documents", "mitacs_projects", "project_chunks", "import_runs"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify smoke-import counts, RLS, and public policies")
    parser.add_argument("--manifest", type=Path, default=Path("matcher-data/globalink-fetch-manifest.json"))
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        parser.error("SUPABASE_DB_URL is not set")

    import psycopg

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected_count = args.limit if args.limit > 0 else int(manifest["record_count"])
    corpus_version = f"{manifest['retrieved_at']}:smoke-{expected_count}"
    try:
        with psycopg.connect(db_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*), COUNT(DISTINCT project_id) FROM mitacs_projects WHERE corpus_version = %s",
                    (corpus_version,),
                )
                project_count, unique_project_ids = cursor.fetchone()
                cursor.execute(
                    "SELECT COUNT(*) FROM import_runs WHERE corpus_version = %s AND status = 'completed'",
                    (corpus_version,),
                )
                completed_runs = cursor.fetchone()[0]
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
                    "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public' AND tablename = ANY(%s)",
                    (TABLES,),
                )
                public_policy_count = cursor.fetchone()[0]
    except psycopg.Error:
        parser.error("database verification connection failed; credentials omitted")

    result = {
        "corpus_version": corpus_version,
        "project_count": project_count,
        "unique_project_ids": unique_project_ids,
        "completed_import_runs": completed_runs,
        "rls_enabled": rls,
        "public_policy_count": public_policy_count,
    }
    if project_count != expected_count or unique_project_ids != expected_count:
        raise SystemExit(f"verification failed: expected {expected_count} projects with unique IDs")
    if completed_runs < 1:
        raise SystemExit("verification failed: no completed import run")
    if any(not rls.get(table, False) for table in TABLES):
        raise SystemExit("verification failed: RLS is not enabled on every expected table")
    if public_policy_count != 0:
        raise SystemExit("verification failed: unexpected public read policy exists")
    print(json.dumps({"status": "ok", **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
