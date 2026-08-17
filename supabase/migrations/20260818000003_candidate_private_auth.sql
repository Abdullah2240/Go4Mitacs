BEGIN;

-- Candidate data is private application data. The service-role key, if used
-- by a server-side API, must remain server-only and must never be sent to the
-- browser, logged, or committed. No anonymous policies are created below.

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    summary TEXT,
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_id),
    UNIQUE (id, owner_id)
);

CREATE TABLE IF NOT EXISTS candidate_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    fact_type TEXT NOT NULL,
    fact_text TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    storage_bucket TEXT NOT NULL DEFAULT 'candidate-private',
    storage_path TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    content_hash TEXT,
    original_filename TEXT,
    mime_type TEXT,
    size_bytes BIGINT CHECK (size_bytes IS NULL OR size_bytes >= 0),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_id, storage_bucket, storage_path),
    UNIQUE (id, owner_id),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL,
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    chunk_text TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    source_location TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (document_id, chunk_index),
    FOREIGN KEY (document_id, owner_id) REFERENCES candidate_documents(id, owner_id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    proficiency TEXT,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_experience (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    organization TEXT NOT NULL,
    role_title TEXT NOT NULL,
    description TEXT,
    started_on DATE,
    ended_on DATE,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    role TEXT,
    started_on DATE,
    ended_on DATE,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_certificates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    issuer TEXT,
    issued_on DATE,
    expires_on DATE,
    credential_ref TEXT,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    venue TEXT,
    abstract TEXT,
    role TEXT,
    published_on DATE,
    source_type TEXT NOT NULL,
    source_ref TEXT,
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    privacy_classification TEXT NOT NULL DEFAULT 'private'
        CHECK (privacy_classification IN ('private', 'restricted')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (profile_id, owner_id) REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_candidate_profiles_owner ON candidate_profiles(owner_id);
CREATE INDEX IF NOT EXISTS idx_candidate_facts_owner_profile ON candidate_facts(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_documents_owner_profile ON candidate_documents(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_document_chunks_owner_document ON candidate_document_chunks(owner_id, document_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_owner_profile ON candidate_skills(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_experience_owner_profile ON candidate_experience(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_projects_owner_profile ON candidate_projects(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_certificates_owner_profile ON candidate_certificates(owner_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_candidate_research_owner_profile ON candidate_research(owner_id, profile_id);

DO $$
DECLARE
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'candidate_profiles', 'candidate_facts', 'candidate_documents',
        'candidate_document_chunks', 'candidate_skills', 'candidate_experience',
        'candidate_projects', 'candidate_certificates', 'candidate_research'
    ] LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM anon', table_name);
        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM PUBLIC', table_name);
        EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.%I TO authenticated', table_name);
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', table_name || '_owner_access', table_name);
        EXECUTE format(
            'CREATE POLICY %I ON public.%I FOR ALL TO authenticated USING (owner_id = auth.uid()) WITH CHECK (owner_id = auth.uid())',
            table_name || '_owner_access', table_name
        );
        EXECUTE format(
            'COMMENT ON TABLE public.%I IS %L',
            table_name,
            'Private candidate data. Authenticated users may access only rows where owner_id = auth.uid(); no anonymous policy exists. Server credentials remain server-only.'
        );
    END LOOP;
END $$;

COMMIT;
