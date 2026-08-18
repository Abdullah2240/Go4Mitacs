# Go4Mitacs

Go4Mitacs is an independent project-matching workspace for the public Mitacs
catalogue. It screens all 3,359 bundled projects with deterministic,
evidence-led matching while keeping documents, profiles, results, private
reference notes, settings, and shortlists in the browser.

## Features

- Browser-local evidence workspace with drag/drop, paste, duplicate detection,
  and TXT, MD, CSV, JSON, HTML, PDF, DOCX, and XLSX parsing.
- Deterministic profile builder with editable skills, tools, domains, methods,
  evidence summaries, and missing-information prompts.
- Same-origin Next.js route handlers for public project search, detail, health,
  and full-corpus matching.
- Local shortlist classifications, comparison of up to four projects,
  Markdown export, and clear-workspace actions.
- Optional private professor-reference documents whose historical annotations
  never affect ranking, eligibility, nationality inference, or predictions.

## Architecture

```text
web/app/                         Next.js application and route handlers
web/app/page.tsx                 browser workspace UI
web/lib/documentParser.ts        browser-side document parsing
web/lib/profile.ts               deterministic profile extraction
web/data/mitacs-projects.public.json  bundled public project index
scripts/generate_public_index.py reproducible public-index generator
matcher-data/                    normalized public source corpus
```

The application is deployed from `web/` to Vercel. It uses the bundled public
index and same-origin route handlers; candidate documents are never accepted
by a route handler.

## Local development

```powershell
cd web
npm install
npm run dev
```

Open `http://localhost:3000`. No environment variable is required.

## Public corpus refresh

```powershell
python scripts\generate_public_index.py
```

The generator reads the normalized public corpus, selects public search/detail
fields, sorts by project ID, and writes the committed deployment index.

## Vercel deployment

Set the Vercel root directory to `web`, choose the Next.js framework preset,
and deploy with no environment variables.

## Privacy

Your documents, profile, settings, and shortlist stay in this browser.
Clearing browser storage removes them from this device. Provider keys, when
entered, remain in `sessionStorage` for the current browser session only.
Optional AI review supports OpenRouter, Gemini, and Hugging Face through explicit browser consent. Evidence sources are reviewed before sending, protected documents are excluded unless selected, and deterministic full-corpus results remain available as the fallback. The local semantic baseline uses fixed hashed-token vectors; no vector database is currently required.
Profile enrichment and project-specific CV alignment are review-first drafts: every accepted statement retains source provenance, and original profile content is not silently overwritten.

## Verification

```powershell
cd web
npm run lint
npm run test
npm run build
cd ..
pytest -q
python scripts\check_public_repo.py
python -m compileall api scripts
git diff --check
```
