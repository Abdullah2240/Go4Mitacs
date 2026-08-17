from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.project_contract import normalize_project_record, parse_background_ids


def test_background_ids_are_parsed_without_losing_raw_value() -> None:
    record = {
        "id": "1",
        "text": "text",
        "metadata": {"ProjectID": "1", "PreferredBackgroundCollection": "[88,73]"},
        "source": {"url": "https://example.test", "retrieved_at": "2026-01-01T00:00:00Z"},
    }
    normalized = normalize_project_record(record)
    assert normalized["metadata"]["PreferredBackgroundCollection"] == "[88,73]"
    assert normalized["metadata"]["PreferredBackgroundIds"] == [88, 73]


def test_malformed_background_ids_are_rejected() -> None:
    with pytest.raises(ValueError):
        parse_background_ids("[88,not-an-id]")


def test_escaped_character_list_from_source_is_recovered() -> None:
    assert parse_background_ids(['"', "[", "2", "7", ",", "6", "8", "]", '"', 69, 74]) == [27, 68, 69, 74]


def test_database_incompatible_nul_is_removed_with_warning() -> None:
    record = {
        "id": "1",
        "text": "before\x00after",
        "metadata": {"ProjectID": "1"},
        "source": {"url": "https://example.test", "retrieved_at": "2026-01-01T00:00:00Z"},
    }
    normalized = normalize_project_record(record)
    assert normalized["text"] == "beforeafter"
    assert normalized["metadata"]["NormalizationWarnings"]
