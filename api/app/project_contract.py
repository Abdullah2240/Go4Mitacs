"""Validation and normalization for the public normalized-project contract."""

import json
import re
from typing import Any


TOP_LEVEL_FIELDS = {"id", "text", "metadata", "source"}


def parse_background_ids(value: Any) -> list[int]:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        integer_values = [item for item in value if isinstance(item, int) and not isinstance(item, bool)]
        string_values = [item for item in value if isinstance(item, str)]
        if len(integer_values) + len(string_values) != len(value):
            raise ValueError("PreferredBackgroundCollection contains an unsupported value")
        if string_values and not all(item.isdigit() for item in string_values):
            # A small number of source rows contain a JSON-escaped character
            # list such as ['[', '2', '7', ',', '6', '8', ']']. Recover only
            # explicit digit runs and retain the original raw field.
            values = [*map(int, re.findall(r"\d+", "".join(string_values))), *integer_values]
        else:
            values = [*string_values, *integer_values]
    elif isinstance(value, str):
        try:
            return parse_background_ids(json.loads(value))
        except json.JSONDecodeError:
            values = [part for part in re.split(r"[,\s]+", value.strip("[] ")) if part]
    else:
        raise ValueError("PreferredBackgroundCollection must be a list or string-encoded list")
    if not isinstance(values, list) or any(isinstance(item, bool) or not str(item).isdigit() for item in values):
        raise ValueError("PreferredBackgroundCollection contains a non-integer value")
    return list(dict.fromkeys(int(item) for item in values))


def normalize_project_record(record: dict[str, Any]) -> dict[str, Any]:
    if set(record) != TOP_LEVEL_FIELDS:
        raise ValueError(f"normalized record fields must be {sorted(TOP_LEVEL_FIELDS)}")
    project_id = record.get("id")
    if not isinstance(project_id, str) or not project_id.strip() or project_id == "None":
        raise ValueError("project id must be a non-empty string")
    if not isinstance(record.get("text"), str) or not record["text"].strip():
        raise ValueError(f"project {project_id} has empty text")
    metadata = record.get("metadata")
    source = record.get("source")
    if not isinstance(metadata, dict) or str(metadata.get("ProjectID")) != project_id:
        raise ValueError(f"project {project_id} has mismatched metadata ProjectID")
    if not isinstance(source, dict) or not source.get("url") or not source.get("retrieved_at"):
        raise ValueError(f"project {project_id} is missing provenance")
    normalized_metadata = dict(metadata)
    clean_text = record["text"].replace("\x00", "")
    if clean_text != record["text"]:
        normalized_metadata["NormalizationWarnings"] = ["removed_nul_character_from_text"]
    if "PreferredBackgroundCollection" in normalized_metadata:
        normalized_metadata["PreferredBackgroundIds"] = parse_background_ids(
            normalized_metadata["PreferredBackgroundCollection"]
        )
    return {"id": project_id, "text": clean_text, "metadata": normalized_metadata, "source": source}
