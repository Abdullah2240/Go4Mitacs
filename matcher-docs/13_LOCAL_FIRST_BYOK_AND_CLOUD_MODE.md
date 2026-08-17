# Local-Only Mode and Deferred Cloud Infrastructure

## Active product

Mitacs Matcher currently runs local-only. No registration, login, Supabase
credentials, database URL, service-role key, or AI provider key is required.
Public project browsing uses the local public corpus. Deterministic matching,
candidate evidence, and shortlist decisions are available immediately.

Candidate evidence and shortlist state are stored in browser localStorage.
This is not an encrypted vault, is not appropriate for highly sensitive
material, and is not synchronized across devices.

## BYOK lifecycle

The UI supports optional OpenRouter, Gemini, and Hugging Face key entry. A key
is stored only in browser sessionStorage for the current browser session and
can be removed with `Forget key`. It is never sent to the backend, Supabase,
external providers, URLs, analytics, logs, errors, or generated files.

The key is not currently used: external AI calls are disabled. Browser-held
keys are visible to the browser owner and browser extensions, so this pattern
is suitable only for personal/local use.

## Local data boundary

Candidate evidence is sent to the local API process only when deterministic
matching is run. It is not sent to a hosted API, Supabase, or an external AI
provider. Public project data may be served by a deployed read-only API or a
future bundled-corpus deployment.

## Deferred infrastructure

Supabase Auth, candidate/private tables, shortlist tables, Storage buckets,
database connections, cross-device sync, cloud provider calls, embeddings,
and CV workflows are retained as historical or deferred infrastructure. Their
migrations and private-schema code must not be deleted or modified as part of
local-only product work, but they are not registered in the active API or
initialized by the frontend.
