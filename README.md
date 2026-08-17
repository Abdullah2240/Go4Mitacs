# Mitacs Matcher

## Current local knowledge-base workflow

Add or paste documents, review the browser-local knowledge base, build/edit an
evidence-backed profile, then match against all 3,359 public Mitacs projects.
Candidate files and extracted text are not uploaded to Supabase or persisted by
the backend. Provider keys remain in sessionStorage only. AI consent is required
before any external request. See `matcher-docs/14_LOCAL_KNOWLEDGE_BASE_AND_AI_CONSENT.md`.

Local-only Mitacs project browsing and evidence-based deterministic matching.
The active product does not require registration, Supabase login, a database
URL, a service-role key, or an AI provider key.

## Architecture

- `web/`: Next.js and TypeScript frontend.
- `api/`: FastAPI and Python backend.
- `matcher-data/`: public normalized Mitacs project corpus used by local mode.
- `matcher-docs/`: architecture, product, privacy, and implementation notes.

The backend serves the public corpus and runs deterministic keyword matching.
Candidate evidence and shortlist state remain in the browser. Supabase Auth,
private candidate tables, cloud shortlists, Storage, and cross-device sync are
deferred infrastructure preserved for a future product mode.

## Prerequisites

- Python 3.11 or newer
- Node.js and npm

## Installation

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r api\requirements.txt
Copy-Item .env.example .env
```

Ensure the local setting is present in `.env`:

```text
CLOUD_SYNC_ENABLED=false
```

No Supabase or database variables are needed for local mode.

Install frontend dependencies:

```powershell
Set-Location web
npm install
```

## Run locally

Start the FastAPI backend from the repository root:

```powershell
uvicorn app.main:app --app-dir api --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`.

Health endpoints:

- `GET http://127.0.0.1:8000/health/live`
- `GET http://127.0.0.1:8000/health/ready`
- `GET http://127.0.0.1:8000/health`

In another terminal, start the Next.js frontend:

```powershell
Set-Location web
npm run dev
```

The frontend is available at `http://localhost:3000`. Set
`NEXT_PUBLIC_API_URL` in `.env` when the API is deployed somewhere other than
`http://127.0.0.1:8000`.

## Local privacy behavior

Provider keys are optional. If entered, a key is stored only in browser
`sessionStorage` for the current session and can be removed with **Forget key**.
The keys are not sent to the backend, Supabase, URLs, logs, analytics, or
external providers. External AI calls are not implemented or enabled.

Candidate evidence and local shortlists are stored in browser `localStorage`.
This is not an encrypted vault; do not use it for highly sensitive material.
The data is not synced across devices and is lost if the browser storage is
cleared.

Public project search and deterministic local matching work without an AI key,
Supabase credentials, or a database password. Candidate evidence is sent only
to the local API process when matching is run; it is not sent to an external
AI provider.

## Production deployment

A deployed frontend requires a reachable deployed API configured through
`NEXT_PUBLIC_API_URL`, or an equivalent deployment that bundles and serves the
public project corpus through the API. Do not expose database URLs,
service-role keys, JWT secrets, provider secrets, or other backend credentials
as `NEXT_PUBLIC_*` variables.

## Verification commands

From the repository root:

```powershell
pytest -q
python -m compileall api scripts
python scripts\check_public_repo.py
python scripts\import_smoke.py --limit 100
```

Build the frontend:

```powershell
Set-Location web
npm run build
npx tsc --noEmit
```

The repository currently has no dedicated frontend `lint` or JavaScript test
script; frontend security behavior is covered by the Python test suite and
the production build/typecheck.

## Deferred Supabase infrastructure

Existing Supabase migrations and private-data code are retained as historical
and deferred infrastructure. Local-only operation does not apply or push
migrations, create users, create Storage buckets, or require Supabase Auth.
Do not run `supabase db push` for normal local development.
