from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.importer import read_normalized_records, validate_import_batch


def test_import_batch_contract_is_exactly_100_records() -> None:
    records = list(read_normalized_records(Path("matcher-data/globalink-projects-normalized.jsonl"), 100))
    validate_import_batch(records, expected_count=100)
    assert len({record["id"] for record in records}) == 100

