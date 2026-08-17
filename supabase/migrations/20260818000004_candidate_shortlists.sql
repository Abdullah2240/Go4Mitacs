BEGIN;

-- Private shortlist state. Both tables are owner-scoped and are intentionally
-- separate from the public Mitacs project corpus. No anonymous policies exist.
CREATE TABLE IF NOT EXISTS candidate_shortlists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (owner_id, name),
    UNIQUE (id, owner_id),
    FOREIGN KEY (profile_id, owner_id)
        REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidate_shortlist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shortlist_id UUID NOT NULL,
    profile_id UUID NOT NULL,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id TEXT NOT NULL REFERENCES mitacs_projects(project_id) ON DELETE CASCADE,
    display_order INTEGER NOT NULL DEFAULT 0 CHECK (display_order >= 0),
    classification TEXT NOT NULL DEFAULT 'strong-fit'
        CHECK (classification IN ('ambitious', 'strong-fit', 'reliable', 'confirmed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (shortlist_id, project_id),
    UNIQUE (shortlist_id, display_order),
    FOREIGN KEY (shortlist_id, owner_id)
        REFERENCES candidate_shortlists(id, owner_id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id, owner_id)
        REFERENCES candidate_profiles(id, owner_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_candidate_shortlists_owner
    ON candidate_shortlists(owner_id);
CREATE INDEX IF NOT EXISTS idx_candidate_shortlist_items_owner_shortlist
    ON candidate_shortlist_items(owner_id, shortlist_id);
CREATE INDEX IF NOT EXISTS idx_candidate_shortlist_items_project
    ON candidate_shortlist_items(project_id);

ALTER TABLE candidate_shortlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidate_shortlist_items ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE candidate_shortlists FROM anon;
REVOKE ALL ON TABLE candidate_shortlist_items FROM anon;
REVOKE ALL ON TABLE candidate_shortlists FROM PUBLIC;
REVOKE ALL ON TABLE candidate_shortlist_items FROM PUBLIC;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE candidate_shortlists TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE candidate_shortlist_items TO authenticated;

DROP POLICY IF EXISTS candidate_shortlists_owner_access ON candidate_shortlists;
CREATE POLICY candidate_shortlists_owner_access ON candidate_shortlists
    FOR ALL TO authenticated
    USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

DROP POLICY IF EXISTS candidate_shortlist_items_owner_access ON candidate_shortlist_items;
CREATE POLICY candidate_shortlist_items_owner_access ON candidate_shortlist_items
    FOR ALL TO authenticated
    USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

COMMENT ON TABLE candidate_shortlists IS
    'Private owner-scoped shortlist metadata; service credentials remain server-only.';
COMMENT ON TABLE candidate_shortlist_items IS
    'Private owner-scoped links to public Mitacs projects; no anonymous policy exists.';

COMMIT;
