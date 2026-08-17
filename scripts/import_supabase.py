"""Import a bounded normalized corpus batch into Supabase Postgres."""

import argparse
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.env import load_repo_dotenv
from app.importer import read_normalized_records, validate_import_batch
from app.project_contract import normalize_project_record


load_repo_dotenv()


UPSERT_PROJECT = """
INSERT INTO mitacs_projects (
    project_id, title, narrative_text, metadata, source_url,
    source_retrieved_at, corpus_version, updated_at
) VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, now())
ON CONFLICT (project_id) DO UPDATE SET
    title = EXCLUDED.title,
    narrative_text = EXCLUDED.narrative_text,
    metadata = EXCLUDED.metadata,
    source_url = EXCLUDED.source_url,
    source_retrieved_at = EXCLUDED.source_retrieved_at,
    corpus_version = EXCLUDED.corpus_version,
    updated_at = now()
"""


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(path: Path, read_limit: int | None, expected_count: int) -> list[dict]:
    records = [normalize_project_record(record) for record in read_normalized_records(path, read_limit)]
    validate_import_batch(records, expected_count=expected_count)
    return records


def import_batch(db_url: str, records: list[dict], corpus_version: str, source_uri: str) -> dict[str, Any]:
    return import_batches(db_url, records, corpus_version, source_uri, batch_size=len(records))


def import_batches(db_url: str, records: list[dict], corpus_version: str, source_uri: str, *, batch_size: int = 100) -> dict[str, Any]:
    import psycopg

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    try:
        connection = None
        for attempt in range(3):
            try:
                connection = psycopg.connect(db_url)
                break
            except psycopg.OperationalError:
                if attempt == 2:
                    raise
                time.sleep(2**attempt)
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO import_runs (corpus_version, source_uri, record_count, status, started_at, completed_at)
                    VALUES (%s, %s, 0, 'running', now(), NULL)
                    ON CONFLICT (corpus_version, source_uri) DO UPDATE SET
                        record_count = 0, status = 'running', started_at = now(), completed_at = NULL
                    RETURNING id
                    """,
                    (corpus_version, source_uri),
                )
                run_id = cursor.fetchone()[0]
            connection.commit()
            for start in range(0, len(records), batch_size):
                batch = records[start : start + batch_size]
                project_rows = []
                for record in batch:
                    metadata = record["metadata"]
                    source = record["source"]
                    project_rows.append(
                        (
                            record["id"],
                            metadata.get("ProjectTitle") or record["id"],
                            record["text"],
                            json.dumps(metadata),
                            source["url"],
                            source["retrieved_at"],
                            corpus_version,
                        )
                    )
                with connection.cursor() as cursor:
                    cursor.executemany(UPSERT_PROJECT, project_rows)
                    cursor.execute(
                        "UPDATE import_runs SET record_count = %s, status = 'running' WHERE id = %s",
                        (start + len(batch), run_id),
                    )
                connection.commit()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*), COUNT(DISTINCT project_id) FROM mitacs_projects WHERE corpus_version = %s",
                    (corpus_version,),
                )
                total, unique_ids = cursor.fetchone()
                if total != len(records) or unique_ids != len(records):
                    raise RuntimeError(f"verification failed: total={total}, unique_ids={unique_ids}, expected={len(records)}")
                cursor.execute(
                    """
                    UPDATE import_runs
                    SET record_count = %s, status = 'completed', completed_at = now()
                    WHERE id = %s
                    """,
                    (len(records), run_id),
                )
            connection.commit()
    except psycopg.Error as error:
        raise RuntimeError(f"database operation failed ({type(error).__name__}); credentials omitted") from None
    return {"run_id": str(run_id), "total": total, "unique_ids": unique_ids}


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a bounded batch into Supabase Postgres")
    parser.add_argument("--input", type=Path, default=Path("matcher-data/globalink-projects-normalized.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("matcher-data/globalink-fetch-manifest.json"))
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true", help="validate the batch without connecting to Postgres")
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    expected_count = args.limit if args.limit > 0 else int(manifest["record_count"])
    read_limit = args.limit if args.limit > 0 else None
    if args.dry_run:
        records = load_records(args.input, read_limit, expected_count)
        print(json.dumps({"status": "dry-run-ok", "records": len(records), "source": manifest["source"]}))
        return 0
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        parser.error("SUPABASE_DB_URL is not set")
    records = load_records(args.input, read_limit, expected_count)
    corpus_version = f"{manifest['retrieved_at']}:smoke-{expected_count}"
    try:
        result = import_batches(db_url, records, corpus_version, manifest["source"], batch_size=args.batch_size)
    except RuntimeError as exc:
        parser.error(str(exc))
    print(json.dumps({"status": "ok", "corpus_version": corpus_version, **result}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
