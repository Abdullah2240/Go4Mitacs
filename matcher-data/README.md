# Matcher Data

This directory contains small, versioned public-source snapshots used to validate the Mitacs Matcher data model before a full-corpus importer is built.

- [`globalink-projects-raw.jsonl`](globalink-projects-raw.jsonl) is the complete 3,359-record source archive, one API record per line.
- [`globalink-projects-normalized.jsonl`](globalink-projects-normalized.jsonl) is the complete vector-ready view, with searchable `text`, filterable `metadata`, and source timestamps.
- [`globalink-fetch-manifest.json`](globalink-fetch-manifest.json) records the retrieval count, page size, and source endpoint.
- [`fetch_globalink_projects.py`](fetch_globalink_projects.py) is the reproducible public-endpoint fetcher with pagination, duplicate detection, and throttling backoff.
- [`globalink-public-sample-10.md`](globalink-public-sample-10.md) is a human-readable sample of the first public page (10 projects).
- [`globalink-public-sample-10-metadata.md`](globalink-public-sample-10-metadata.md) preserves the timing, flexibility, institution, supervisor, background, and questionnaire metadata for those same records.
- Source endpoint: `POST https://globalink.mitacs.ca/api/sasprojectlistpaging`
- Retrieval date: 2026-08-17
- Observed unfiltered corpus count: 3,359 projects.

These records are public catalogue data, not application data. Do not add credentials, application responses, recommendation letters, or other private documents to this directory.
