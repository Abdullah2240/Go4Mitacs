"""Verify applied shortlist tables without printing connection details."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.db import connect


TABLES = ("candidate_shortlists", "candidate_shortlist_items")


def main() -> int:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT c.relname, c.relrowsecurity,
              EXISTS (
                SELECT 1 FROM pg_policies p
                WHERE p.schemaname = 'public' AND p.tablename = c.relname
                  AND p.policyname LIKE '%%owner_access%%'
                  AND p.roles @> ARRAY['authenticated']::name[]
                  AND p.qual::text LIKE '%%owner_id%%'
              ) AS owner_policy,
              has_table_privilege('anon', 'public.' || c.relname, 'SELECT') AS anon_select,
              EXISTS (
                SELECT 1 FROM pg_constraint k JOIN pg_class t ON t.oid = k.conrelid
                WHERE t.relname = c.relname AND k.contype = 'u'
                  AND pg_get_constraintdef(k.oid) LIKE '%%shortlist_id, project_id%%'
              ) AS duplicate_guard
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relname = ANY(%s)
            ORDER BY c.relname
            """,
            (list(TABLES),),
        )
        rows = cursor.fetchall()
        print(f"shortlist tables: {len(rows)}/{len(TABLES)}")
        for row in rows:
            print(f"{row[0]}: rls={row[1]} owner_policy={row[2]} anon_select={row[3]} duplicate_guard={row[4]}")
        cursor.execute("SELECT count(*), count(DISTINCT project_id) FROM mitacs_projects")
        print(f"public projects: {cursor.fetchone()}")
        cursor.execute("SELECT count(*) FROM candidate_shortlists UNION ALL SELECT count(*) FROM candidate_shortlist_items")
        print(f"shortlist rows: {cursor.fetchall()}")
    return 0 if len(rows) == len(TABLES) and all(row[1] and row[2] and not row[3] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
