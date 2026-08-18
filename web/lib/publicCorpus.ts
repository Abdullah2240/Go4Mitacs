import corpus from "../data/mitacs-projects.public.json";

export type PublicProject = {
  id: string; title: string; description_preview: string; research_area: string; skills_background: string | null;
  supervisor: { first_name: string | null; last_name: string | null }; university: string | null; campus: string | null;
  province: string | null; language: string | null; start_date: string | null; flexible_start: string | null;
  start_notes: string | null; source_url: string | null; source_retrieved_at: string | null; corpus_version: string;
};
export type PublicCorpus = { corpus_version: string; count: number; projects: PublicProject[] };
export const publicCorpus = corpus as PublicCorpus;
export const GLOBALINK_PORTAL_URL = "https://globalink.mitacs.ca/";

const tokenPattern = /[a-z0-9][a-z0-9+#./-]{1,}/gi;
export function tokens(value: string) { return new Set((value || "").match(tokenPattern)?.map((token) => token.toLowerCase()) ?? []); }
export function searchable(project: PublicProject) { return `${project.title} ${project.description_preview} ${project.research_area} ${project.skills_background ?? ""} ${project.university ?? ""} ${project.province ?? ""} ${project.language ?? ""}`; }

const GENERIC_MATCH_TERMS = new Set(["ai", "application", "applications", "based", "data", "development", "engineering", "method", "methods", "model", "models", "process", "processes", "project", "research", "system", "systems", "technology", "technologies", "using", "work", "working"]);
const corpusDocumentFrequency = new Map<string, number>();
for (const project of publicCorpus.projects) {
  for (const token of Array.from(tokens(searchable(project)))) corpusDocumentFrequency.set(token, (corpusDocumentFrequency.get(token) || 0) + 1);
}
function tokenWeight(token: string) { return Math.log((publicCorpus.projects.length + 1) / ((corpusDocumentFrequency.get(token) || 0) + 1)) + 1; }

export function filterProjects(projects: PublicProject[], params: URLSearchParams) {
  const query = (params.get("q") || "").trim().toLowerCase();
  const province = (params.get("province") || "").trim().toLowerCase();
  const university = (params.get("university") || "").trim().toLowerCase();
  const language = (params.get("language") || "").trim().toLowerCase();
  return projects.filter((project) => (!query || searchable(project).toLowerCase().includes(query)) && (!province || (project.province || "").toLowerCase() === province) && (!university || (project.university || "").toLowerCase() === university) && (!language || (project.language || "").toLowerCase() === language));
}

export function rankProjects(projects: PublicProject[], evidenceText: string, filters: { province?: string; university?: string; research_area?: string }) {
  const rawEvidence = tokens(evidenceText);
  const meaningfulEvidence = new Set(Array.from(rawEvidence).filter((token) => !GENERIC_MATCH_TERMS.has(token)));
  const evidence = meaningfulEvidence.size >= 2 ? meaningfulEvidence : rawEvidence;
  return projects.filter((project) => (!filters.province || (project.province || "").toLowerCase() === filters.province.toLowerCase()) && (!filters.university || (project.university || "").toLowerCase() === filters.university.toLowerCase()) && (!filters.research_area || searchable(project).toLowerCase().includes(filters.research_area.toLowerCase()))).map((project) => {
    const projectTokens = tokens(searchable(project)); const overlap = Array.from(evidence).filter((token) => projectTokens.has(token)).sort(); const matchedWeight = overlap.reduce((sum, token) => sum + tokenWeight(token), 0); const totalWeight = Array.from(evidence).reduce((sum, token) => sum + tokenWeight(token), 0) || 1; const evidenceCoverage = matchedWeight / totalWeight; const breadth = overlap.length / Math.max(8, Math.min(18, evidence.size)); const titleTokens = tokens(project.title); const titleOverlap = Array.from(evidence).filter((token) => titleTokens.has(token)); const titleCoverage = titleOverlap.reduce((sum, token) => sum + tokenWeight(token), 0) / totalWeight; const score = (evidenceCoverage * .55 + Math.min(1, breadth) * .35 + Math.min(1, titleCoverage) * .1) * 100; const missingEvidence = Array.from(evidence).filter((token) => !projectTokens.has(token)).sort().slice(0, 8);
    return { project_id: project.id, title: project.title, score: Number(score.toFixed(4)), score_breakdown: { evidence_coverage: Number((evidenceCoverage * 55).toFixed(2)), evidence_breadth: Number((Math.min(1, breadth) * 35).toFixed(2)), title_coverage: Number((Math.min(1, titleCoverage) * 10).toFixed(2)) }, group: score >= 70 ? "ambitious" : score >= 35 ? "strong-fit" : "reliable", matched_evidence: overlap.slice(0, 20), missing_evidence: missingEvidence.length ? missingEvidence : ["No meaningful evidence gap detected; verify the full project requirements manually"], risks: ["Lexical evidence signal only; review requirements and eligibility manually"], metadata: { ProjectID: project.id, ProjectTitle: project.title, LanguageUsed: project.language, StartDate: project.start_date, isStartDateFlexible: project.flexible_start, NotesOnStartDate: project.start_notes, Province: project.province, PreferredBackgroundCollection: project.skills_background, "Professor.FirstName": project.supervisor.first_name, "Professor.LastName": project.supervisor.last_name, "Professor.UniversityName": project.university, "Professor.CampusName": project.campus }, source_url: GLOBALINK_PORTAL_URL, text_preview: project.description_preview };
  }).sort((a, b) => b.score - a.score || a.project_id.localeCompare(b.project_id));
}
