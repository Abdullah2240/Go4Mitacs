from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.importer import read_normalized_records, validate_import_batch


def test_first_100_normalized_records_are_importable() -> None:
    path = Path("matcher-data/globalink-projects-normalized.jsonl")
    records = list(read_normalized_records(path, 100))
    validate_import_batch(records, expected_count=100)

