# Parallel Codex CLI Prompt - Privacy and Phase 1 Hardening

Copy the prompt below into Codex CLI while the Supabase project is being created. It is intentionally bounded and does not require a live Supabase database.

```text
Work in C:\Users\Hp\Resume\Resumes\Mitacs.

Read these documents first:
- matcher-docs/01_PRODUCT_ARCHITECTURE.md
- matcher-docs/04_DATA_SCHEMA_AND_METADATA.md
- matcher-docs/05_IMPLEMENTATION_PLAN_AND_HANDOFF.md
- matcher-docs/06_UI_DESIGN_SPEC.md
- matcher-docs/07_DECISION_LOG_AND_CLI_CHECKLIST.md
- matcher-docs/08_PARALLEL_CLI_PROMPT.md

Implement only Phase 1 privacy and repository hardening. Do not build matching, embeddings, CV rewriting, or the full UI.

Goals:

1. Lock the initial vector contract at 1536 dimensions.
   - Keep the pgvector migration at vector(1536).
   - Add a clear server-side validation helper or test that rejects an embedding with any other length.
   - Do not call an embedding provider yet.

2. Harden the repository for future public release.
   - Update .gitignore to exclude .env files, Supabase secrets, local storage, caches, logs, generated embeddings, private PDFs, certificates, LORs, application records, and the private “2026 Mitacs GRI docs (good seniors)” directory.
   - Do not ignore the public project JSONL files or public architecture documentation.
   - Add a staged-file privacy scanner that fails on likely secrets and private document paths. It must be safe to run before the repository has any commits.
   - Add tests for the privacy scanner.
   - Do not delete or move existing user files.

3. Add database privacy scaffolding.
   - Keep public Mitacs project tables readable only through the server-side API unless an explicit public policy is later approved.
   - Enable RLS on source_documents and all future candidate/private tables.
   - Do not create anonymous read policies for private tables.
   - Add comments explaining that the service-role key is server-only.
   - Keep the migration idempotent and add a rollback migration outside Supabase’s forward migration directory.
   - Do not apply or push migrations because the user has not finished creating the Supabase project.

4. Improve the import contract without requiring a database.
   - Keep project_id upserts and import_runs verification.
   - Add a dry-run/schema test for the 100-record import.
   - Ensure the importer never logs DATABASE_URL, SUPABASE_DB_URL, service-role keys, or provider keys.

Verification required:
- pytest -q
- python scripts\import_smoke.py --limit 100
- python scripts\check_public_repo.py (or the chosen scanner name)
- Python compilation/import checks
- Show the final git status, but do not commit or push.

Report changed files, tests, assumptions, and anything that still requires the live Supabase project.
```

## Why 1536 for now

1536 is a valid initial contract if we choose an embedding model that emits exactly 1536 values. The important rule is consistency: the model, migration, index, and query vectors must all share the same dimension. We can change later, but it would require a deliberate migration and full re-embedding run, so do not make the dimension configurable silently.
