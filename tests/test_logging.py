from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.logging import safe_fields


def test_structured_fields_redact_credentials() -> None:
    values = safe_fields({"database_url": "secret", "api_key": "secret", "record_count": 100})
    assert values == {"database_url": "[REDACTED]", "api_key": "[REDACTED]", "record_count": 100}

