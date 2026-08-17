# Local Knowledge Base and AI Consent

## Browser-owned workspace

The browser stores documents, extracted text, hashes, metadata, profile drafts,
match results, and shortlist decisions in localStorage. Provider keys are held
only in sessionStorage. These stores are not encrypted, are not cross-device
sync, and may be cleared by browser privacy settings. The UI exposes clear
workspace, clear shortlist, and Forget key actions.

## Parsing boundaries

TXT, Markdown, CSV, JSON, HTML, and source-code/text files use browser APIs.
PDF, DOCX, and XLSX use browser-safe parser libraries. Each document has a
stable ID, SHA-256 content hash, size/character limits, parse status, and
user-visible errors. Duplicates are rejected by hash; an oversized or
unsupported file does not remove other documents. Original files are never
uploaded or stored on the backend.

## Profile and matching

The local builder extracts skills, tools, domains, methods, education/work
terms, evidence snippets, and missing-information warnings from local text. It
does not invent qualifications or metrics. Full-corpus retrieval evaluates all
3,359 projects and reports the considered count. AI reranking is optional and
bounded to 30, 60, 120, 240, 480, or a custom capped width. This is AI review
width, not corpus size.

## Consent and provider lifecycle

Before any provider call, a modal states provider/model, exact content
categories being sent, that the key/content are used only for this action, that
this app does not retain the request, and how to cancel. Only explicit
confirmation proceeds. The app never silently switches providers. Keys are
never logged, cached, returned, written to files, databases, analytics, or URLs.
Any proxy must be stateless, size-limited, allowlisted, and redacting.

## Failure, cost, and clearing

Deterministic matching is free apart from the local API request. AI cost depends
on provider/model and prompt size; the UI estimates one bounded review request
plus retries and warns about free-tier rate limits. Transient failures retry
with backoff. Failure, decline, absent key, or rate limiting preserves the
deterministic ranking. Any AI cache is browser-local and version-keyed.

## Deployment model

The no-cloud deployment is a local/static frontend plus the read-only public
project API or bundled public corpus. It needs no registration, cloud sync,
Supabase Auth, private bucket, candidate database, or provider `.env` secret.
