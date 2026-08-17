# Mitacs Application Sources

This file records external sources used by the Mitacs application workspace. Treat live web sources as refreshable: capture and date the project records when the matcher corpus is built.

## Official open-project catalogue

- Source: [Mitacs Open Projects - Research, Pakistan](https://webform.mitacs.ca/en/open-projects?field_title_value=&field_project_type_value_i18n=research&field_location_s_where_project_c_country=PK&field_location_s_where_project_c_administrative_area=All&field_location_s_where_project_c_locality=)
- Recorded: 2026-08-17
- Current filters in the supplied link: project type **Research**; country **Pakistan**; province **Any**; city blank.
- Intended use: first-party discovery source for the project corpus and for checking project details before a final shortlist is submitted.

### Matcher ingestion rule

Do not treat this URL as a complete, permanent export. When implementation begins, retrieve and normalize the currently visible records, retain the source URL and retrieval timestamp per project, and re-check shortlisted projects immediately before application submission. Project availability and descriptions can change.

## Globalink student-application catalogue

- Public catalogue: [Globalink student application - projects](https://globalink.mitacs.ca/#/student/application/projects)
- Recorded: 2026-08-17
- Observed catalogue size: **3,359 projects**.
- Access finding: browsing and search results are publicly available; login is required to add a project to an application or apply, not to inspect the catalogue.

### Public reference endpoints

| Endpoint | Verified purpose | Access observed |
| --- | --- | --- |
| [`/api/portals`](https://globalink.mitacs.ca/api/portals) | active portal/cohort configuration and deadline metadata | Public GET |
| [`/api/universities/`](https://globalink.mitacs.ca/api/universities/) | Canadian university lookup (88 records observed) | Public GET |
| [`/api/provinces/`](https://globalink.mitacs.ca/api/provinces/) | province lookup (11 records observed) | Public GET |
| [`/api/countries`](https://globalink.mitacs.ca/api/countries) | country/partner lookup (237 records observed) | Public GET |

### Corpus endpoint for the matcher

The application itself uses `POST /api/sasprojectlistpaging` for public project search/pagination. A minimal unfiltered request with `offset: 0` and `limit: 10` returned a `count` of 3,359 and 10 detailed project records without a login. Each record includes the project title, descriptions, research area, student roles and skills, location, faculty supervisor, university/campus, language, and planned start date.

Use the application's own filtering fields (`HostProvinceName`, `HostUniversityID`, `HostCampusID`, `LanguageUsed`, `keyword`, `FirstName`, `LastName`, `AcademicDiscipline`, and `PreferredBackgroundCollection`) with `offset` and `limit`. The service can issue a `qToken` response header and the site handles throttling; the future importer must page slowly, honor retry/backoff, store a retrieval timestamp, and never use authenticated application endpoints or attempt to apply on the user's behalf.

## Recommendation-letter guidance

- Local source: [`../docs/GRI-Recommendation-letter-guidelines_2025-1.pdf`](../docs/GRI-Recommendation-letter-guidelines_2025-1.pdf)
- Companion checklist: [`../docs/LOR_SUBMISSION_CHECKLIST.md`](../docs/LOR_SUBMISSION_CHECKLIST.md)
- Scope: content and document-format guidance only. It does **not** specify an email address, portal workflow, file name, deadline, or whether the referee/applicant must upload the final letter. Confirm those mechanics in the current application instructions before sending anything.
