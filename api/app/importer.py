"""Small, dependency-free Phase 0 importer validation helpers."""

import json
from pathlib import Path
from typing import Iterable

from .project_contract import normalize_project_record


def read_normalized_records(path: Path, limit: int | None = None) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            if not line.strip():
                continue
            yield json.loads(line)


def validate_import_batch(records: list[dict], expected_count: int = 100) -> None:
    if len(records) != expected_count:
        raise AssertionError(f"expected {expected_count} records, got {len(records)}")
    normalized = []
    for record in records:
        try:
            normalized.append(normalize_project_record(record))
        except ValueError as error:
            raise AssertionError(str(error)) from error
    ids = [record["id"] for record in normalized]
    if len(set(ids)) != len(ids):
        raise AssertionError("duplicate project ids in import batch")
