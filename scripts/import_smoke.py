import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.env import load_repo_dotenv
from app.importer import read_normalized_records, validate_import_batch


load_repo_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a 100-record normalized corpus import batch")
    parser.add_argument("--input", type=Path, default=Path("matcher-data/globalink-projects-normalized.jsonl"))
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    records = list(read_normalized_records(args.input, args.limit))
    validate_import_batch(records, expected_count=args.limit)
    print(f"import smoke test passed: {len(records)} records, {len({r['id'] for r in records})} unique ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
