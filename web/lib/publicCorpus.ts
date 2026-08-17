import corpus from "../data/mitacs-projects.public.json";

export type PublicProject = {
  id: string; title: string; description_preview: string; research_area: string; skills_background: string | null;
  supervisor: { first_name: string | null; last_name: string | null }; university: string | null; campus: string | null;
  province: string | null; language: string | null; start_date: string | null; flexible_start: string | null;
  start_notes: string | null; source_url: string | null; source_retrieved_at: string | null; corpus_version: string;
};
export type PublicCorpus = { corpus_version: string; count: number; projects: PublicProject[] };
export const publicCorpus = corpus as PublicCorpus;

const tokenPattern = /[a-z0-9][a-z0-9+#./-]{1,}/gi;
export function tokens(value: string) { return new Set((value || "").match(tokenPattern)?.map((token) => token.toLowerCase()) ?? []); }
export function searchable(project: PublicProject) { return `${project.title} ${project.description_preview} ${project.research_area} ${project.skills_background ?? ""} ${project.university ?? ""} ${project.province ?? ""} ${project.language ?? ""}`; }

export function filterProjects(projects: PublicProject[], params: URLSearchParams) {
  const query = (params.get("q") || "").trim().toLowerCase();
  const province = (params.get("province") || "").trim().toLowerCase();
  const university = (params.get("university") || "").trim().toLowerCase();
  const language = (params.get("language") || "").trim().toLowerCase();
  return projects.filter((project) => (!query || searchable(project).toLowerCase().includes(query)) && (!province || (project.province || "").toLowerCase() === province) && (!university || (project.university || "").toLowerCase() === university) && (!language || (project.language || "").toLowerCase() === language));
}

export function rankProjects(projects: PublicProject[], evidenceText: string, filters: { province?: string; university?: string; research_area?: string }) {
  const evidence = tokens(evidenceText);
  return projects.filter((project) => (!filters.province || (project.province || "").toLowerCase() === filters.province.toLowerCase()) && (!filters.university || (project.university || "").toLowerCase() === filters.university.toLowerCase()) && (!filters.research_area || searchable(project).toLowerCase().includes(filters.research_area.toLowerCase()))).map((project) => {
    const projectTokens = tokens(searchable(project)); const overlap = Array.from(evidence).filter((token) => projectTokens.has(token)).sort(); const titleOverlap = Array.from(tokens(project.title)).filter((token) => evidence.has(token)).length; const keywordScore = Math.min(1, overlap.length / Math.max(1, Math.min(18, evidence.size))); const titleBonus = Math.min(.15, titleOverlap * .03); const score = Math.min(100, (keywordScore + titleBonus) * 100);
    return { project_id: project.id, title: project.title, score: Number(score.toFixed(4)), score_breakdown: { keyword_overlap: Number((keywordScore * 100).toFixed(2)), title_bonus: Number((titleBonus * 100).toFixed(2)) }, group: score >= 70 ? "ambitious" : score >= 35 ? "strong-fit" : "reliable", matched_evidence: overlap.slice(0, 20), missing_evidence: overlap.length ? [] : ["No exact evidence terms matched"], risks: score < 70 ? ["Deterministic lexical retrieval; semantic fit needs human review"] : [], metadata: { ProjectID: project.id, ProjectTitle: project.title, LanguageUsed: project.language, StartDate: project.start_date, isStartDateFlexible: project.flexible_start, NotesOnStartDate: project.start_notes, Province: project.province, PreferredBackgroundCollection: project.skills_background, "Professor.FirstName": project.supervisor.first_name, "Professor.LastName": project.supervisor.last_name, "Professor.UniversityName": project.university, "Professor.CampusName": project.campus }, source_url: project.source_url, text_preview: project.description_preview };
  }).sort((a, b) => b.score - a.score || a.project_id.localeCompare(b.project_id));
}
