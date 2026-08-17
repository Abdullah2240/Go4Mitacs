# Archived Cloud Authentication and Shortlist Setup

This document describes deferred infrastructure only. It is not part of the
active local-only Mitacs Matcher product. Do not create users, run cloud E2E
flows, or enable cloud routes for local development.

## Browser variables

Set these in the repository-root `.env` for local development and in the web
deployment environment before building Next.js:

```text
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-or-publishable-key>
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The URL and anon/publishable key are the only Supabase values permitted in
browser code. `SUPABASE_DB_URL`, `DATABASE_URL`, service-role keys, JWT
secrets, provider keys, and other backend credentials remain in the API
environment only. The repository privacy scanner and browser-source tests
check this boundary.

## Deferred two-account verification workflow

Create two non-personal accounts manually in the Supabase Auth dashboard. Do
not create them from scripts and do not store their credentials in Git.

1. Sign in as Account A.
2. `PUT /api/v1/candidate/profile` with a harmless test display name.
3. `POST /api/v1/candidate/import` with a synthetic fact whose source is
   `e2e-test`.
4. Call `GET /api/v1/matches` with Account A's bearer token.
5. Sign out and sign in as Account B.
6. Confirm Account B sees only its own profile and facts. Requests using an
   Account A record ID must return 404 or an RLS-denied safe error.
7. While signed out, call `GET /api/v1/projects`; confirm public projects are
   returned and no candidate fields are present.
8. Delete the synthetic records and test accounts after verification.

The automated suite verifies unauthenticated rejection, token subject
handling, owner-scoped SQL, migration policy shape, and browser secret safety.
Live two-user verification remains manual because this project must not create
accounts or store credentials autonomously.

## Shortlist migration

`20260818000004_candidate_shortlists.sql` was applied after static review. It
creates owner-scoped `candidate_shortlists` and
`candidate_shortlist_items`, links items to `candidate_profiles` and public
`mitacs_projects`, enforces unique projects per shortlist, enables RLS, grants
only authenticated access, and revokes anonymous/public table access.

Rollback is at
`supabase/rollback/20260818000004_candidate_shortlists.sql` and is outside the
forward migration directory. It remains historical/deferred infrastructure;
local-only mode does not use it.
