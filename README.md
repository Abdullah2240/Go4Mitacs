# Mitacs Matcher

Mitacs Matcher is a local-first knowledge-base matcher for Mitacs Globalink
projects. It screens the complete public catalogue of 3,359 projects with a
deterministic, evidence-led ranking, while keeping candidate documents,
profiles, results, private reference notes, and shortlists in the browser.

## Why it is different

The searchable universe is the full corpus, not a fixed top-240 pool. Optional
AI reranking is a separate, bounded review of selected candidates and is not
implemented in the Vercel deployment milestone. The deterministic matcher
works without an account, provider key, database, or cloud sync.

## Features

- Browser-local document workspace with drag/drop, picker, paste, duplicate
  hashing, size limits, and parsing for text formats, PDF, DOCX, and XLSX.
- Deterministic local profile builder with editable skills, tools, domains,
  methods, evidence snippets, and missing-information warnings.
- Same-origin Next.js routes for public project search, detail, health, and
  full-corpus local matching.
- Local shortlist classifications, comparison view, Markdown export, and clear
  workspace/key/shortlist actions.
- Optional private professor-reference documents parsed locally only. Historical
  context annotations are visibly labelled and never affect ranking, eligibility,
  nationality inference, or recommendations.

## Architecture

```text
web/app/page.tsx                 browser workspace and local storage UI
web/lib/documentParser.ts        browser-side TXT/MD/CSV/JSON/HTML/PDF/DOCX/XLSX parsing
web/lib/profile.ts               deterministic candidate profile extraction
web/data/mitacs-projects.public.json  committed minimized public index
web/app/api/                       same-origin Vercel Route Handlers
scripts/generate_public_index.py  reproducible public-index generator
matcher-data/                     normalized public source corpus
```

The active deployable application is `web/`. The Python API and Supabase
migrations remain historical/deferred code and are not required or initialized
by the active product. No candidate document is accepted by a route handler.

## Local development

From the repository root:

```powershell
cd web
npm install
npm run dev
```

Open `http://localhost:3000`. This runs the frontend and public matching API
together. No `.env` file or environment variable is required.

## Public corpus refresh

When the official normalized corpus is refreshed, regenerate the committed
deployment index from the repository root:

```powershell
python scripts\generate_public_index.py
```

The generator reads `matcher-data/globalink-projects-normalized.jsonl`, selects
only public search/detail fields, sorts by project ID, and writes
`web/data/mitacs-projects.public.json`. Do not manually edit the generated file.

## Vercel deployment

Import the GitHub repository in Vercel and set:

- Root Directory: `web`
- Framework Preset: Next.js
- Environment variables: none

Do not add Supabase, database, backend URL, analytics, or provider-key
variables. Then deploy from the Vercel UI. The repository does not deploy
automatically from this workspace.

“Local-first” means no account or server-side candidate persistence. The hosted
site and its public corpus routes still need a network connection; it is not an
offline application. Optional future AI actions must obtain explicit consent
before selected content leaves the browser.

## Privacy and limitations

Provider keys, when used by a future consented adapter, belong only in
`sessionStorage`. They must never be committed, placed in URLs, logged, stored
in localStorage, or configured in Vercel. Browser localStorage is not encrypted
and has storage limits. Clear the workspace and private reference context on a
shared machine. The public index contains only public Mitacs project data.

## Verification

```powershell
cd web
npm run lint
npm run test
npm run build
cd ..
pytest -q
python -m compileall api scripts
python scripts\check_public_repo.py
```

## Current status and roadmap

Current status: frontend-only Vercel deployment, local knowledge base,
deterministic full-corpus retrieval, local shortlist, private historical
annotations, and production build verification are implemented.

Roadmap: consented provider adapters and bounded AI reranking, richer local
document claim review, stronger semantic retrieval, and expanded comparison
tools. These are optional additions and do not change the full-corpus promise.

## Deferred infrastructure

Historical Supabase migrations, authentication, private candidate APIs, and
cloud shortlist code are retained for research history only. Do not apply
migrations, create users or buckets, enable cloud sync, or add database
credentials for the active product.
