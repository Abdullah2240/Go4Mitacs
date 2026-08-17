from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.candidate_ingestion import chunk_evidence, validate_candidate_payload
from app.matching import rank_projects


def test_candidate_json_validation_and_chunking_are_local_and_deterministic() -> None:
    records = validate_candidate_payload({"facts": [{"fact_text": "Python and PostgreSQL", "source_type": "cv", "source_ref": "cv:p1"}]})
    assert records[0]["source_type"] == "cv"
    assert chunk_evidence("cv:p1", records[0]["fact_text"]) == chunk_evidence("cv:p1", records[0]["fact_text"])


def test_candidate_json_rejects_missing_provenance_fields() -> None:
    with pytest.raises(ValueError):
        validate_candidate_payload({"facts": [{"fact_text": "unsupported"}]})


def test_matching_baseline_is_deterministic_and_explains_gaps() -> None:
    projects = [{"project_id": "2", "title": "Python research", "text": "Python data analysis", "metadata": {}}, {"project_id": "1", "title": "Other", "text": "biology", "metadata": {}}]
    result = rank_projects(projects, "Python", limit=2)
    assert result[0]["project_id"] == "2"
    assert "risks" in result[0]
    assert result[1]["missing_evidence"]

