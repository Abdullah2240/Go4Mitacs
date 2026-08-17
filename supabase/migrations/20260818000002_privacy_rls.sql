BEGIN;

-- No anonymous or authenticated PostgREST policies are created here.
-- The FastAPI server uses the Supabase service-role key server-side only;
-- that key must never be sent to Next.js, logged, or committed.
ALTER TABLE source_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE mitacs_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_runs ENABLE ROW LEVEL SECURITY;

COMMENT ON TABLE source_documents IS
    'Private source metadata. Access only through the server-side API; never expose the service-role key to clients.';
COMMENT ON TABLE mitacs_projects IS
    'Public-source catalogue data, still server-mediated by default until an explicit public policy is approved.';
COMMENT ON TABLE project_chunks IS
    'Server-mediated project retrieval data; no anonymous read policy is defined.';
COMMENT ON TABLE import_runs IS
    'Server-side ingestion audit data; no anonymous read policy is defined.';

-- Candidate/private tables are created in later phases. Keep this migration
-- safe to re-run and apply RLS automatically if those tables already exist.
DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'evidence_excerpts', 'candidate_claims', 'candidate_assets',
        'professors', 'match_runs', 'project_matches', 'shortlist_items',
        'cv_variants', 'chat_decisions'
    ] LOOP
        IF to_regclass('public.' || table_name) IS NOT NULL THEN
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
        END IF;
    END LOOP;
END $$;

COMMIT;

