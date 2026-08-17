# Implementation Status

## Direction status: local knowledge-base matcher

The next active milestone is a browser-local document workspace with local
profile generation, full-corpus retrieval, optional consented AI reranking,
and visible clear/fallback/privacy states. Cloud infrastructure remains
deferred.

## Deployment status (2026-08-18)

The active application is deployable as one Next.js project with `web` as the
Vercel Root Directory. The public index is generated from the normalized
3,359-project corpus and committed under `web/data/`. Active routes are
same-origin Next.js handlers for `/api/health`, `/api/projects`,
`/api/projects/:projectId`, and `/api/local/matches`. The retained FastAPI
application is not required for the active deployment.

Updated 2026-08-18 after conversion to local-only mode.

## Complete

- Repository-root `.env` loading with `python-dotenv`; shell variables win.
- Secret-safe importer errors, structured redaction helper, staged-file privacy scanner, and tests.
- Normalized project validation, provenance preservation, background-ID parsing, and database-incompatible text sanitization.
- Deterministic bounded chunking and a fixed 1536-dimensional local/mock embedding contract.
- Resumable, idempotent Supabase project upserts in batches; full public corpus imported and verified at 3,359 records.
- Server-side health, project search, and project detail endpoints.
- Archived Supabase Auth, owner-scoped candidate APIs, and cloud shortlist APIs
  are retained but are not registered by the active local-only application.
- Deterministic keyword-baseline matching at `POST /api/v1/local/matches`, with
  matched evidence, missing evidence, risks, and ambitious/strong-fit/reliable
  grouping.
- Minimal Next.js local-only public project search, evidence input, matching,
  and browser-local shortlist UI.
- Documented browser Auth configuration and a manual two-account verification
  workflow using non-personal test accounts.
- Preserved the applied owner-scoped shortlist migration and rollback as
  historical/deferred infrastructure; active shortlist state is browser-local.
- Local-first browser flow with optional provider selection, sessionStorage key
  handling, forget-key behavior, local evidence, local shortlist state, public
  search, and unauthenticated deterministic matching.

## Partial or deferred

- Cloud embedding providers are represented only by guarded provider contracts; no external provider is called.
- Project chunks and pgvector storage are scaffolded in the applied schema, but embedding generation/storage is deferred.
- Shortlist persistence is implemented and migration
  `20260818000004_candidate_shortlists.sql` is applied. The live tables have
  RLS, authenticated owner policies, anonymous SELECT denied, and duplicate
  project protection.
- Candidate document upload, private Storage buckets, cloud embeddings,
  reranking, CV alignment, and the full research workspace UI remain deferred.
- Runtime two-user ownership testing requires an authenticated test session;
  no test users or personal data were created. Static/unit tests cover the
  bearer boundary and owner-scoped SQL.
- External provider calls, cloud authentication, cloud routes, and browser key
  transmission remain disabled.

The candidate/private authentication foundation is applied through
`20260818000003_candidate_private_auth.sql`. It defines nine owner-scoped
tables, RLS, authenticated owner policies, anonymous/public revokes, and
private Storage path metadata. Runtime verification confirms all nine tables
exist, all nine have RLS enabled, authenticated owner policies are present,
anonymous SELECT privileges are denied, and the public Mitacs corpus remains
3,359 rows with 3,359 unique project IDs.

## Verified database state

- Full corpus: 3,359 records and 3,359 distinct project IDs.
- 100-record smoke corpus: 100 records and 100 distinct project IDs.
- Repeated imports reuse the same `import_runs` row for each corpus version.
- RLS is enabled on `source_documents`, `mitacs_projects`, `project_chunks`, and `import_runs`.
- No public policies exist for those tables.

The migrations were applied without resetting the database. No private Storage
bucket, auth user, personal data, private document, or credential was created
or added to Git.

## Active local-only routes

- Public: `GET /health/live`, `GET /health/ready`, `GET /health`,
  `GET /api/v1/projects`, `GET /api/v1/projects/{project_id}`.
- Local: `POST /api/v1/local/matches`.

No active route requires authentication. `SUPABASE_DB_URL`, database URLs,
service credentials, JWT secrets, and Supabase client credentials are not part
of local mode. Local-only behavior is documented in
`matcher-docs/13_LOCAL_FIRST_BYOK_AND_CLOUD_MODE.md`. The next milestone is
local UX hardening; cloud infrastructure remains deferred.
