# Mitacs Project Data Schema and Metadata Contract

This document defines how Globalink project data should be preserved, normalized, embedded, filtered, and refreshed in the Mitacs Matcher. It is intended for future implementation and maintenance.

## Source and artifacts

Current public source:

- Catalogue: <https://globalink.mitacs.ca/#/student/application/projects>
- Paging endpoint: `POST https://globalink.mitacs.ca/api/sasprojectlistpaging`
- Retrieval manifest: [`../matcher-data/globalink-fetch-manifest.json`](../matcher-data/globalink-fetch-manifest.json)
- Raw archive: [`../matcher-data/globalink-projects-raw.jsonl`](../matcher-data/globalink-projects-raw.jsonl)
- Normalized archive: [`../matcher-data/globalink-projects-normalized.jsonl`](../matcher-data/globalink-projects-normalized.jsonl)
- Fetcher: [`../matcher-data/fetch_globalink_projects.py`](../matcher-data/fetch_globalink_projects.py)

The raw archive is the preservation layer. The normalized archive is the interchange layer for embedding pipelines, vector databases, and structured databases.

## Raw JSONL envelope

Each line in `globalink-projects-raw.jsonl` has this shape:

```json
{
  "record": { "ProjectID": "...", "ProjectTitle": "..." },
  "source": {
    "url": "https://globalink.mitacs.ca/api/sasprojectlistpaging",
    "retrieved_at": "2026-08-17T09:44:17.460365+00:00"
  }
}
```

`record` preserves the API field names and values, including nulls, duplicate bilingual fields, nested professor data, and questionnaire fields. Do not overwrite this layer during normalization.

## Normalized JSONL record

Each line in `globalink-projects-normalized.jsonl` has four top-level fields:

```json
{
  "id": "51150",
  "text": "title, research area, description, roles, and skills concatenated for embedding",
  "metadata": { "ProjectID": "51150", "StartDate": "2027-05-03T07:00:00.000Z" },
  "source": {
    "url": "https://globalink.mitacs.ca/api/sasprojectlistpaging",
    "retrieved_at": "2026-08-17T09:44:17.460365+00:00"
  }
}
```

### `id`

Use the stable string form of `ProjectID` as the canonical project identifier. All chunks, embeddings, comparisons, shortlist entries, and audit records should retain this ID.

### `text`

The embedding text is assembled from non-empty narrative fields in this order:

1. `ProjectTitle`, `ProjectTitle2`
2. `ResearchAreaDescription`, `ResearchAreaDescription2`
3. `projectDescription`, `ProjectDescription`, `projectDescription2`, `ProjectDescription2`
4. `StudentRoles`, `StudentRoles2`
5. `StudentSkills`, `StudentSkills2`

Keep the text human-readable. Do not put IDs, questionnaire answers, or source-control fields into the main semantic text unless a later evaluation shows they improve retrieval.

### `metadata`

Metadata is copied from the raw record after removing only long narrative fields. It is used for filtering, reranking, display, and evidence—not as a replacement for the source text.

## Metadata field groups

### Identity and language

| API field | Meaning | Use |
| --- | --- | --- |
| `ProjectID` | Stable catalogue project identifier | Primary key and citation target |
| `ProjectTitle` | Main project title | Display and embedding |
| `ProjectTitle2` | Alternate-language or alternate title, when supplied | Preserve and optionally embed |
| `LanguageUsed` | Main project language | Eligibility/filtering |
| `lang1` | Alternate language indicator | Preserve; do not assume it is populated |

### Narrative research content

| API field | Meaning | Use |
| --- | --- | --- |
| `ResearchAreaDescription` / `ResearchAreaDescription2` | Supervisor/research-area context | Embedding and professor-fit explanation |
| `projectDescription` / `ProjectDescription` | Main project description variants | Embedding and evidence |
| `projectDescription2` / `ProjectDescription2` | Alternate-language or alternate description variants | Preserve and embed when non-empty |
| `StudentRoles` / `StudentRoles2` | Expected activities and learning outcomes | Skills/experience matching |
| `StudentSkills` / `StudentSkills2` | Required or preferred skills | Keyword and semantic matching |

The lower-case and upper-case description fields may duplicate one another. Preserve both in raw storage; deduplicate identical text when constructing normalized embedding text.

### Timing and availability

| API field | Meaning | Use |
| --- | --- | --- |
| `StartDate` | Preferred start timestamp, normally ISO-8601 | Date filtering and compatibility scoring |
| `isStartDateFlexible` | Whether the supervisor marked the start date flexible | Positive flexibility filter |
| `NotesOnStartDate` | Free-text timing constraints or flexibility notes | Human review and evidence-backed scoring |

The current response does **not** provide a separate explicit end date, internship duration, term length, or professor tenure field. Do not infer those values from the start date or questionnaire answers. Treat timing notes as free text unless manually normalized with a documented rule.

### Geography and institution

| API field | Meaning | Use |
| --- | --- | --- |
| `City` | Project location city | Location display/filter |
| `Province` | Project location province | Location display/filter |
| `Professor.FacultyProvince` / `Professor.FacultyProvince` | Faculty/university province | Institution filter |
| `Professor.UniversityName` | Host university | University matching |
| `Professor.UniversityID` | Stable university lookup ID | Join to university reference data |
| `Professor.CampusName` | Host campus | Campus filter/display |
| `Professor.FirstName` / `Professor.LastName` | Faculty supervisor name | Professor matching and display |
| `Professor` | Nested duplicate of professor/institution fields | Preserve raw; flatten for normalized querying |

### Academic background

| API field | Meaning | Use |
| --- | --- | --- |
| `PreferredBackgroundCollection` | String-encoded list of catalogue background IDs | Parse into an integer array in the normalized database; preserve original string in raw metadata |

These IDs require a reference dictionary before they can be shown as human-readable disciplines. Do not guess their labels from the numeric values.

### Internship questionnaire

The API returns `InternshipQ1` through `InternshipQ16`. Values include `Always`, `Very often`, `Often`, `Occasionally`, `Infrequently`, `Almost never`, `Never`, `Yes`, `No`, or null. The field semantics should be confirmed against the current application UI before assigning labels.

Store every answer unchanged. For a later normalized schema, use a child table or object such as:

```json
{
  "questionnaire": {
    "Q1": "Often",
    "Q2": "Infrequently",
    "Q15": "No",
    "Q16": null
  }
}
```

Do not treat these values as universal scores until their question text and directionality are captured from the application interface.

## Vector-database preparation

The recommended ingestion path is:

```text
raw JSONL
  -> normalized JSONL
  -> narrative chunking
  -> embeddings
  -> vector database
```

For long projects, split `text` into bounded chunks while repeating `project_id`, title, university, professor, and source timestamp in chunk metadata. Recommended chunk categories are `overview`, `research_area`, `roles`, and `skills`. Retrieval results must be merged by `project_id` before ranking so one project does not occupy the shortlist multiple times.

Keep these metadata fields filterable in the vector store or relational sidecar:

- `project_id`
- `language`
- `province`
- `city`
- `university_id`
- `university_name`
- `campus_name`
- `professor_name`
- `start_date`
- `start_date_flexible`
- `preferred_background_ids`
- `retrieved_at`

Use a relational database for exact filters and date logic; use vector search for semantic similarity. A vector database should not be the sole source of truth.

## Provenance and refresh rules

- Retain `source.url` and `source.retrieved_at` for every record and chunk.
- Refresh the corpus before final project selection because titles, availability, dates, and descriptions can change.
- Keep prior snapshots when practical so ranking decisions can be reproduced.
- Never store login tokens, application records, or private recommendation letters in the public-project JSONL files.
- Never submit applications, add projects, or contact supervisors as part of ingestion.

## Validation checklist

Before accepting a new fetch:

- `record_count` matches the API-reported count.
- Every line is valid UTF-8 JSON.
- Every `ProjectID` is unique within the snapshot.
- Every normalized record has non-empty `id`, `text`, and `source`.
- Timing, institution, professor, location, language, and questionnaire fields are retained.
- Raw and normalized record counts match.
- The retrieval timestamp and source endpoint are recorded in the manifest.
