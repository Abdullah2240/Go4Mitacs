# Decisions and CLI Start Checklist

## Decision: browser-owned knowledge base and bounded AI review (2026-08-18)

Candidate documents, extracted text, profiles, results, and shortlist state
stay in browser storage. Keys stay in sessionStorage and are removed by Forget
key. No provider request occurs before explicit consent. Full-corpus retrieval
always evaluates all 3,359 projects; AI reads only a labelled bounded pool.
Do not add migrations, create users/buckets, enable cloud mode, commit, or push.

## Decision: local-first BYOK default (2026-08-18)

The default product mode is local-first. Public browsing and deterministic
matching require no account, database password, or AI key. Provider keys are
optional browser-session inputs and are not transmitted by the local baseline.
Supabase Auth, RLS-protected candidate data, and cloud shortlist persistence
remain deferred archival infrastructure and are not part of the active product.

## Architecture readiness

The architecture is complete enough to begin an MVP implementation. The major product boundaries, data contract, retrieval strategy, safeguards, UI surfaces, and delivery phases are documented.

The visual system is complete at the specification level in [`06_UI_DESIGN_SPEC.md`](06_UI_DESIGN_SPEC.md), but it is not yet implemented or visually verified.

## Decisions to make before the first real deployment

These do not block a local Phase 0 build if the defaults are used.

| Decision | Recommended default | Why it matters |
| --- | --- | --- |
| Initial mode | Single-user private prototype | Avoids premature multi-account authorization complexity |
| Frontend | Next.js + TypeScript | UI, routing, comparison workspace, future hosted deployment |
| API | FastAPI + Python | Ingestion, retrieval, document processing, AI orchestration |
| Database | Supabase Postgres with pgvector enabled | Structured metadata and vectors in one system |
| File storage | Supabase private Storage bucket | CVs/certificates stay separate from searchable text |
| Embeddings | Local model first | Avoids sending private evidence to an external provider by default |
| Vector dimension | 1536 for the initial contract | Keeps the current migration stable; the model must emit exactly 1536 values |
| Generation/reranking | One configured provider first, adapter interface from day one | Easier debugging and reproducible evaluations |
| Background jobs | Synchronous CLI jobs for Phase 0; queue later | Keeps the first build small and observable |
| Hosting | Local during MVP; decide frontend/API hosting after local validation | Supabase alone does not host a Next.js + FastAPI application in the same way a full app host does |
| Authentication | No auth for a local single-user build; Supabase Auth before any shared deployment | Prevents accidental exposure of private evidence |

## Supabase setup decisions

Before Phase 1, confirm:

- A Supabase project exists for this application, separate from unrelated production systems.
- The `vector` extension is enabled.
- Database migrations are applied through a versioned migration directory.
- A private storage bucket exists for source documents.
- The service-role key is used only by the FastAPI server and never in Next.js client code.
- The anon key is used only for explicitly permitted browser operations.
- Row-level security is enabled before any multi-user or hosted deployment.
- Backups and database region are acceptable for the private CV/certificate evidence.

The initial vector contract is `vector(1536)`. Before inserting embeddings, the implementation must validate the selected embedding model's output length and fail clearly if it is not exactly 1536. Changing dimensions later requires a deliberate migration and re-embedding run.

## Public-repository privacy contract

The repository may be private during development, but it must be safe to publish later:

- Personal PDFs, LORs, certificates, application records, and private evidence are never committed.
- `.env*`, Supabase keys, service-role keys, provider keys, local storage, generated embeddings, caches, and logs are ignored.
- Public Mitacs project data may remain in the repository because it is sourced from the public catalogue, but private candidate material must live outside the public project tree or in private Supabase Storage.
- Add a staged-file privacy check before the first commit and run it in CI when the repository becomes public.
- Enable RLS on all tables before private candidate data is inserted. Do not create anonymous read policies for private tables.

## Local CLI checklist

When moving to Codex CLI, give it this exact first task:

> Read `matcher-docs/01_PRODUCT_ARCHITECTURE.md`, `02_PRODUCT_FLOW_AND_BUILD_BLUEPRINT.md`, `AI.md`, `04_DATA_SCHEMA_AND_METADATA.md`, `05_IMPLEMENTATION_PLAN_AND_HANDOFF.md`, `06_UI_DESIGN_SPEC.md`, and this checklist. Implement Phase 0 only: create the app skeleton, environment templates, database migration scaffold, health checks, and a 100-record import smoke test. Do not build the full UI or CV rewriting yet.

The CLI task should:

1. Work from `C:\Users\Hp\Resume\Resumes\Mitacs`.
2. Preserve the existing data and documents.
3. Create a clear application subdirectory rather than mixing source code into `matcher-data` or `matcher-docs`.
4. Add `.gitignore` entries for `.env*`, private uploads, local vector indexes, and generated secrets.
5. Report every changed file and command run.
6. Stop after the Phase 0 acceptance checks and wait for review.

## What is already consolidated

- Product architecture and user journey
- Full public project corpus and fetch manifest
- Raw and normalized JSONL formats
- Metadata and vector-ingestion contract
- AI provider and retrieval strategy
- LOR guidance and private application checklist
- UI visual direction and screen contracts
- Implementation phases, safeguards, and handoff procedure

## What remains after the first coding milestone

- Decide and configure the first embedding model.
- Build the first database migrations.
- Import and verify the 100-record smoke-test subset.
- Review the first shell/explorer/detail UI visually.
- Confirm Supabase data retention and private-storage settings.
- Add evaluation labels for manually reviewed project matches.
