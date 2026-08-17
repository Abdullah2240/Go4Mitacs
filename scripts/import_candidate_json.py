"""Validate a local structured candidate JSON file without storing its contents."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.candidate_ingestion import chunk_evidence, validate_candidate_payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local candidate evidence JSON")
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    records = validate_candidate_payload(payload)
    chunk_count = sum(len(chunk_evidence(str(record.get("source_ref", "local")), record["fact_text"])) for record in records)
    print(json.dumps({"status": "ok", "facts": len(records), "chunks": chunk_count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

