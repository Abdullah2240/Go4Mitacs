# Private Candidate Data and Authentication Design

The candidate foundation is additive and separate from the public Mitacs
catalogue. Migration `20260818000003_candidate_private_auth.sql` creates nine
private tables, each owned by a Supabase Auth user through `owner_id UUID
REFERENCES auth.users(id)`.

Every private table has:

- RLS enabled;
- an authenticated `FOR ALL` policy requiring `owner_id = auth.uid()`;
- no anonymous policy, plus an explicit revoke from `anon`;
- owner/profile indexes and foreign-key indexes;
- privacy classification and provenance fields where the record represents
  extracted or source-backed candidate evidence.

Candidate documents store only private Storage metadata (`storage_bucket` and
`storage_path`) plus provenance. Raw PDFs, certificates, recommendation
letters, and extracted private files do not belong in Git.

Composite `(profile_id, owner_id)` and `(document_id, owner_id)` foreign keys
prevent a user from attaching a child record to another user's profile or
document while satisfying a row-level owner check.

The candidate and shortlist migrations are preserved as applied historical
records. They are not accessed by the active local-only product, which does not
require authentication or a database connection.

Authentication UI, session middleware, candidate API endpoints, and cloud
shortlist APIs remain archived/deferred code. Private Storage bucket
provisioning, embeddings, and CV workflows remain deferred.
