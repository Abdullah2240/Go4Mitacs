BEGIN;

DROP POLICY IF EXISTS candidate_shortlist_items_owner_access ON candidate_shortlist_items;
DROP POLICY IF EXISTS candidate_shortlists_owner_access ON candidate_shortlists;
DROP INDEX IF EXISTS idx_candidate_shortlist_items_project;
DROP INDEX IF EXISTS idx_candidate_shortlist_items_owner_shortlist;
DROP INDEX IF EXISTS idx_candidate_shortlists_owner;
DROP TABLE IF EXISTS candidate_shortlist_items;
DROP TABLE IF EXISTS candidate_shortlists;

COMMIT;
