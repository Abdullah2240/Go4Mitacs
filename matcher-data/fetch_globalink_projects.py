"""Fetch the public Globalink project catalogue into JSONL files.

The script preserves raw API rows and writes a normalized, vector-ready view.
It uses only the public catalogue endpoint; it never logs in or submits an application.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_URL = "https://globalink.mitacs.ca/api/sasprojectlistpaging"
PAGE_SIZE = 100
OUT_DIR = Path(__file__).resolve().parent
RAW_PATH = OUT_DIR / "globalink-projects-raw.jsonl"
NORMALIZED_PATH = OUT_DIR / "globalink-projects-normalized.jsonl"
MANIFEST_PATH = OUT_DIR / "globalink-fetch-manifest.json"

BASE_FILTER = {
    "HostProvinceName": None,
    "HostUniversityID": None,
    "HostCampusID": None,
    "LanguageUsed": None,
    "keyword": None,
    "FirstName": None,
    "LastName": None,
    "AcademicDiscipline": None,
    "PreferredBackgroundCollection": None,
}

LONG_FIELDS = {
    "projectDescription",
    "projectDescription2",
    "ProjectDescription",
    "ProjectDescription2",
    "ResearchAreaDescription",
    "ResearchAreaDescription2",
    "StudentRoles",
    "StudentRoles2",
    "StudentSkills",
    "StudentSkills2",
}


def request_page(offset: int, qtoken: str | None) -> tuple[dict, str | None]:
    body = dict(BASE_FILTER, offset=offset, limit=PAGE_SIZE)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://globalink.mitacs.ca",
        "Referer": "https://globalink.mitacs.ca/",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Authorization": "JWT ",
    }
    if qtoken:
        headers["qToken"] = qtoken
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    for attempt in range(1, 11):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload, response.headers.get("qtoken") or qtoken
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 10:
                raise
            qtoken = error.headers.get("qtoken") or qtoken
            headers["qToken"] = qtoken or ""
            request = urllib.request.Request(
                API_URL,
                data=json.dumps(body).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            time.sleep(min(30, attempt * 3))
    raise RuntimeError("unreachable")


def normalized_record(row: dict, retrieved_at: str) -> dict:
    text_parts = []
    for field in (
        "ProjectTitle",
        "ProjectTitle2",
        "ResearchAreaDescription",
        "ResearchAreaDescription2",
        "projectDescription",
        "ProjectDescription",
        "projectDescription2",
        "ProjectDescription2",
        "StudentRoles",
        "StudentRoles2",
        "StudentSkills",
        "StudentSkills2",
    ):
        value = row.get(field)
        if value and value not in text_parts:
            text_parts.append(value)

    metadata = {key: value for key, value in row.items() if key not in LONG_FIELDS}
    return {
        "id": str(row.get("ProjectID")),
        "text": "\n\n".join(text_parts),
        "metadata": metadata,
        "source": {"url": API_URL, "retrieved_at": retrieved_at},
    }


def main() -> None:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []
    qtoken = None
    offset = 0
    expected_count = None

    while expected_count is None or offset < expected_count:
        payload, qtoken = request_page(offset, qtoken)
        page_rows = payload.get("rows", [])
        if expected_count is None:
            expected_count = int(payload.get("count", 0))
        if not page_rows:
            break
        rows.extend(page_rows)
        offset += len(page_rows)
        print(f"Fetched {offset}/{expected_count}")
        if offset < expected_count:
            time.sleep(0.4)

    ids = [str(row.get("ProjectID")) for row in rows]
    if len(rows) != expected_count:
        raise RuntimeError(f"Expected {expected_count} records but fetched {len(rows)}")
    if len(set(ids)) != len(ids):
        raise RuntimeError("Duplicate project IDs detected")

    raw_tmp = RAW_PATH.with_suffix(".tmp")
    normalized_tmp = NORMALIZED_PATH.with_suffix(".tmp")
    with raw_tmp.open("w", encoding="utf-8", newline="\n") as raw_file, normalized_tmp.open(
        "w", encoding="utf-8", newline="\n"
    ) as normalized_file:
        for row in rows:
            raw_file.write(json.dumps({"record": row, "source": {"url": API_URL, "retrieved_at": retrieved_at}}, ensure_ascii=False) + "\n")
            normalized_file.write(json.dumps(normalized_record(row, retrieved_at), ensure_ascii=False) + "\n")
    os.replace(raw_tmp, RAW_PATH)
    os.replace(normalized_tmp, NORMALIZED_PATH)

    manifest = {
        "source": API_URL,
        "retrieved_at": retrieved_at,
        "record_count": len(rows),
        "page_size": PAGE_SIZE,
        "raw_jsonl": RAW_PATH.name,
        "normalized_jsonl": NORMALIZED_PATH.name,
        "notes": "Public catalogue records only; no authentication or application submission was used.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
