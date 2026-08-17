# Mitacs Matcher - Implementation Plan and Handoff

This is the execution plan for turning the current planning and data workspace into a working private application. The plan assumes the application is for one candidate first, but keeps the data model extensible.

## Current baseline

Already prepared:

- Product architecture, UI surfaces, matching lanes, and CV Alignment Studio: [`01_PRODUCT_ARCHITECTURE.md`](01_PRODUCT_ARCHITECTURE.md)
- User flow, output contracts, and implementation phases: [`02_PRODUCT_FLOW_AND_BUILD_BLUEPRINT.md`](02_PRODUCT_FLOW_AND_BUILD_BLUEPRINT.md)
- Source registry and public endpoint findings: [`03_MITACS_APPLICATION_SOURCES.md`](03_MITACS_APPLICATION_SOURCES.md)
- Raw/normalized schema and vector-ingestion rules: [`04_DATA_SCHEMA_AND_METADATA.md`](04_DATA_SCHEMA_AND_METADATA.md)
- Retrieval, embeddings, provider routing, safety, and evaluation: [`AI.md`](AI.md)
- UI visual direction and screen contracts: [`06_UI_DESIGN_SPEC.md`](06_UI_DESIGN_SPEC.md)
- Decision log and CLI/Supabase checklist: [`07_DECISION_LOG_AND_CLI_CHECKLIST.md`](07_DECISION_LOG_AND_CLI_CHECKLIST.md)
- Complete public corpus: [`../matcher-data/globalink-projects-raw.jsonl`](../matcher-data/globalink-projects-raw.jsonl) and [`../matcher-data/globalink-projects-normalized.jsonl`](../matcher-data/globalink-projects-normalized.jsonl)
- Candidate CV and LOR guidance in the sibling `docs` directory.

The data fetch is complete and validated at 3,359 unique project records. The vector database is not populated yet; the normalized JSONL is the input for that phase.

## Product outcome

The first usable release should let the user:

1. Ingest a private evidence base: CV, certificates, project notes, research, work evidence, and later professor/history sources.
2. Browse and filter the complete Mitacs corpus.
3. Run a transparent hybrid match and receive a ranked top 15.
4. Compare projects side by side with evidence, strengths, gaps, and confidence.
5. Maintain a manually adjustable ten-project strategy board.
6. Generate an evidence-constrained CV alignment draft for selected projects.

The application must never apply to projects, contact professors, or send documents automatically.

## Recommended stack

These are the working defaults, not irreversible commitments:

| Layer | Default | Responsibility |
| --- | --- | --- |
| Web UI | Next.js + TypeScript | Dashboard, explorer, match details, compare view, strategy board, CV studio |
| API | FastAPI + Python | Ingestion, normalization, retrieval, scoring, AI orchestration |
| Structured data | PostgreSQL + pgvector, preferably Supabase | Projects, candidate claims, matches, versions, filters, vectors |
| Private files | S3-compatible/Supabase private storage | Original CVs, certificates, research files, generated drafts |
| Background jobs | Redis-backed queue or managed durable jobs | Parsing, chunking, embeddings, refreshes, report generation |
| Embeddings | Local/self-hosted first where practical | Stable, inexpensive vectorization of sensitive evidence |
| Generation/reranking | Provider abstraction | Gemini/OpenRouter/Hugging Face adapters with explicit fallback policy |

Keep the provider key server-side. The browser must never receive or persist provider secrets.

## Build sequence

### Local-first reorder (2026-08-18)

The active delivery order is local browser/API shell, public corpus browsing,
deterministic local matching, local candidate evidence, and local shortlist.
BYOK keys are session-only configuration but external calls are not active.
Supabase Auth/RLS, private storage, embeddings, reranking, and CV Studio are
deferred or archived infrastructure rather than prerequisites for first use.

### Phase 0 - Repository and environment foundation

Deliverables:

- Application repository with `web`, `api`, and shared schema boundaries.
- Environment template containing placeholder variables only.
- Database migrations and a health-check endpoint.
- Private storage policy and a local development profile.
- Import manifest that records corpus version, source URL, retrieval time, and schema version.

Acceptance checks:

- A fresh developer setup can start the API and web app.
- Secrets are absent from source control and browser bundles.
- A migration can create the empty schema and roll back safely.

### Phase 1 - Project corpus ingestion

Deliverables:

- Import the normalized JSONL into `mitacs_projects`.
- Preserve raw API payloads or raw-file references for provenance.
- Parse `PreferredBackgroundCollection` into an integer array while retaining the original string.
- Flatten professor/university/campus metadata for filtering.
- Create project chunks for overview, research area, roles, and skills.
- Add idempotent refresh logic keyed by `ProjectID` and source snapshot.

Acceptance checks:

- Database count matches the manifest count.
- Every project has a source timestamp and stable ID.
- Exact filters work for province, language, university, campus, professor, and flexible start date.
- Re-running the import creates no duplicates.

### Phase 2 - Candidate evidence base

Deliverables:

- Upload private documents and record their provenance.
- Extract text and create evidence excerpts with page/section references.
- Create candidate assets and claims only from source-backed excerpts.
- Add claim status: `proposed`, `verified`, `rejected`, or `needs_review`.
- Build the candidate profile from approved claims rather than ungrounded chat memory.

Acceptance checks:

- Every displayed skill or achievement links to a source excerpt.
- The user can correct or reject an extracted claim.
- Private source documents are not returned in public project responses.

### Phase 3 - Matching MVP

Deliverables:

- Lexical retrieval for exact technologies, methods, domains, and institutions.
- Vector retrieval over project chunks and candidate evidence chunks.
- Deterministic hard filters for language, dates, location, and explicit eligibility.
- Transparent score breakdown: semantic fit, keyword fit, evidence strength, feasibility, and gaps.
- AI reranking limited to a retrieved candidate set, with citations to project and candidate evidence.
- Reproducible `MatchRun` storing corpus version, weights, embedding model, and generation model.

Acceptance checks:

- A match result explains both why the project fits and what is missing.
- The model cannot claim an experience absent from the evidence base.
- The same inputs and versions reproduce the same deterministic retrieval set.
- A manually reviewed evaluation set measures precision, unsupported-claim rate, and ranking usefulness.

### Phase 4 - Decision workspace

Deliverables:

- Top-15 results screen.
- Project detail view with source evidence and metadata.
- Side-by-side compare view.
- User notes, manual rank, saved state, and lane assignment.
- Final-ten strategy board with configurable lanes; default preset is 4 strong-fit, 4 ambitious, and 2 intelligence-backed/experimental.

Acceptance checks:

- User ranking is never silently overwritten by a new match run.
- Every shortlist item retains its match-run provenance.
- The UI clearly separates model suggestions from user decisions.

### Phase 5 - CV Alignment Studio

Deliverables:

- Compare selected project requirements against approved candidate claims.
- Identify existing evidence, missing evidence, and wording opportunities.
- Propose CV changes as a diff, never as an invisible rewrite.
- Require user approval before a claim enters a CV variant.
- Export a base CV and project-cluster variants.

Acceptance checks:

- No new factual claim can enter a CV without a linked source or explicit user confirmation.
- Planned work remains labelled as planned; production work remains distinguished from prototypes.
- The final CV export is traceable to a versioned claim set.

### Phase 6 - Intelligence and hardening

Deliverables:

- Optional professor profiles and user-supplied historical-selection signals.
- Reference-app visibility signal only where a project-list source is captured; no speculation about “overused” projects.
- Provider fallback, rate-limit handling, caching, and cost telemetry.
- Prompt-injection tests for imported project text and uploaded documents.
- Backup/restore, deletion workflow, audit log, and evaluation dashboard.

Acceptance checks:

- Historical or country-related signals are visibly sourced, optional, and never used as an unsupported proxy for identity.
- Provider failures do not silently change the meaning of a recommendation.
- A user can delete private evidence and its derived embeddings.

## Initial database entities

Implement these first:

- `source_documents`: original file/web source, hash, provenance, retrieval time, access status.
- `evidence_excerpts`: extracted text, source location, embedding reference.
- `candidate_claims`: approved/proposed claims linked to excerpts.
- `candidate_assets`: projects, certificates, roles, awards, research, and portfolio items.
- `mitacs_projects`: normalized project metadata and narrative fields.
- `project_chunks`: chunk text, category, embedding, and project ID.
- `professors`: normalized supervisor/institution metadata.
- `match_runs`: corpus/model/weight versions and query profile.
- `project_matches`: score components, gaps, evidence references, confidence.
- `shortlist_items`: user rank, lane, notes, and decision state.
- `cv_variants`: versioned output plus claim references.
- `chat_decisions`: user approvals/corrections affecting claims or CV suggestions.

## Non-negotiable safeguards

- Do not use or expose credentials from Ticketer, Fleetview, Mitacs, or any other private system.
- Do not upload the private CV/LOR evidence base to a third-party model without explicit provider and privacy approval.
- Do not infer professor preference from names, nationality, or identity. Use only sourced historical signals the user explicitly provides.
- Do not turn project descriptions into claims about the candidate.
- Do not invent missing project end dates, term lengths, professor tenure, or eligibility.
- Do not perform application submissions or supervisor contact automatically.
- Preserve the distinction between shipped, tested, planned, and proposed work.

## Decisions required before coding

The following can use defaults for the first local prototype, but must be confirmed before deployment:

1. Local/private-only prototype or hosted private application.
2. Supabase/Postgres + pgvector or a separate vector service.
3. First generation provider and embedding model.
4. Whether the first release supports one candidate only or multiple accounts.
5. Which private evidence files are in scope for the initial ingestion test.
6. Whether historical professor/selection data is available and source-documented.

If no decision is supplied, use the local single-user prototype defaults and keep adapters/configuration replaceable.

## Handoff strategy

No separate handoff is required to continue in this workspace: the planning documents and corpus are already in the shared `Mitacs` directory. The cleanest workflow is to keep this thread for decisions and use an implementation task in the same workspace for coding.

If work is moved to another Codex task or agent, hand off these items together:

- The absolute workspace path: `C:\Users\Hp\Resume\Resumes\Mitacs`
- This plan: `matcher-docs/05_IMPLEMENTATION_PLAN_AND_HANDOFF.md`
- The architecture set: `matcher-docs/01_PRODUCT_ARCHITECTURE.md`, `02_PRODUCT_FLOW_AND_BUILD_BLUEPRINT.md`, `AI.md`, and `04_DATA_SCHEMA_AND_METADATA.md`
- The data README and manifest: `matcher-data/README.md` and `globalink-fetch-manifest.json`
- The exact first milestone, not the entire product: **Phase 0 plus a 100-record import smoke test**

The receiving task should report changed files, tests run, open decisions, and any data/model assumptions before moving to the next phase. This keeps implementation incremental and prevents a broad rewrite from outrunning the evidence and schema decisions.

## Definition of ready to start coding

Coding can begin when the repository has a chosen app root and the user confirms the local/private prototype defaults. The first coding task should implement the Phase 0 skeleton and a 100-record import smoke test; it should not begin with the full UI, CV rewriting, professor intelligence, or automatic application actions.
