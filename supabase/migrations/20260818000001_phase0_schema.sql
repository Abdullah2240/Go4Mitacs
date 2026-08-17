BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS source_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    content_hash TEXT,
    retrieved_at TIMESTAMPTZ,
    access_status TEXT NOT NULL DEFAULT 'available',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mitacs_projects (
    project_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    narrative_text TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    source_url TEXT NOT NULL,
    source_retrieved_at TIMESTAMPTZ NOT NULL,
    corpus_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS project_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL REFERENCES mitacs_projects(project_id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(1536)
);

CREATE TABLE IF NOT EXISTS import_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    corpus_version TEXT NOT NULL,
    source_uri TEXT NOT NULL,
    record_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    UNIQUE (corpus_version, source_uri)
);

CREATE INDEX IF NOT EXISTS idx_mitacs_projects_metadata
    ON mitacs_projects USING GIN (metadata);

COMMIT;

