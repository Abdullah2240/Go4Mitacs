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

const stopWords = new Set("a an and are as at be been by for from in into is it its of on or our that the their this to was were with you your".split(" "));
const tokenPattern = /[a-z0-9]+(?:[+#][a-z0-9]+)?/gi;
function normalizeTerm(value: string) {
  const term = value.toLowerCase();
  if (stopWords.has(term) || term.length < 2) return "";
  if (term.endsWith("ies") && term.length > 4) return term.slice(0, -3) + "y";
  if (term.endsWith("ing") && term.length > 6) return term.slice(0, -3);
  if (term.endsWith("ed") && term.length > 5) return term.slice(0, -2);
  if (term.endsWith("s") && !term.endsWith("ss") && !term.endsWith("is") && !term.endsWith("us") && term.length > 4) return term.slice(0, -1);
  return term;
}
export function terms(value: string) { return (value || "").match(tokenPattern)?.map(normalizeTerm).filter(Boolean) ?? []; }
export function tokens(value: string) { return new Set(terms(value)); }
export function searchable(project: PublicProject) { return `${project.title} ${project.description_preview} ${project.research_area} ${project.skills_background ?? ""} ${project.university ?? ""} ${project.province ?? ""} ${project.language ?? ""}`; }

type FieldName = "title" | "research" | "skills" | "description";
type IndexedProject = { project: PublicProject; fields: Record<FieldName, string[]>; all: Set<string>; allWeight: number; titleWeight: number };
const fieldWeights: Record<FieldName, number> = { title: 3.2, research: 2.2, skills: 1.8, description: 1 };
const fieldText = (project: PublicProject): Record<FieldName, string> => ({ title: project.title, research: project.research_area, skills: project.skills_background ?? "", description: `${project.description_preview} ${project.university ?? ""} ${project.province ?? ""} ${project.language ?? ""}` });
function weightOf(terms: Set<string>) { let sum = 0; terms.forEach((term) => { sum += idf(term); }); return sum || 1; }
function indexFields(project: PublicProject): { fields: Record<FieldName, string[]>; all: Set<string> } { const fields = Object.fromEntries((Object.entries(fieldText(project)) as Array<[FieldName, string]>).map(([name, value]) => [name, terms(value)])) as Record<FieldName, string[]>; return { fields, all: new Set(Object.values(fields).flat()) }; }
const fieldIndex = publicCorpus.projects.map(indexFields);
const documentFrequency = new Map<string, number>();
for (const indexed of fieldIndex) for (const term of Array.from(indexed.all)) documentFrequency.set(term, (documentFrequency.get(term) || 0) + 1);
const averageLength: Record<FieldName, number> = { title: 1, research: 1, skills: 1, description: 1 };
for (const field of Object.keys(averageLength) as FieldName[]) averageLength[field] = fieldIndex.reduce((sum, item) => sum + item.fields[field].length, 0) / Math.max(1, fieldIndex.length);
function idf(term: string) { const df = documentFrequency.get(term) || 0; return Math.log(1 + (fieldIndex.length - df + 0.5) / (df + 0.5)); }
const corpusIndex: IndexedProject[] = publicCorpus.projects.map((project, i) => { const { fields, all } = fieldIndex[i]; return { project, fields, all, allWeight: weightOf(all), titleWeight: weightOf(new Set(fields.title)) }; });
function count(values: string[], term: string) { return values.reduce((total, value) => total + (value === term ? 1 : 0), 0); }
function phraseHits(query: string[], field: string[]) { if (query.length < 2 || field.length < 2) return 0; let hits = 0; for (let i = 0; i < query.length - 1; i++) for (let j = 0; j < field.length - 1; j++) if (query[i] === field[j] && query[i + 1] === field[j + 1]) hits++; return hits; }

export function filterProjects(projects: PublicProject[], params: URLSearchParams) {
  const query = (params.get("q") || "").trim().toLowerCase(); const province = (params.get("province") || "").trim().toLowerCase(); const university = (params.get("university") || "").trim().toLowerCase(); const language = (params.get("language") || "").trim().toLowerCase();
  return projects.filter((project) => (!query || searchable(project).toLowerCase().includes(query)) && (!province || (project.province || "").toLowerCase() === province) && (!university || (project.university || "").toLowerCase() === university) && (!language || (project.language || "").toLowerCase() === language));
}

const corpusIndexById = new Map(corpusIndex.map((indexed) => [indexed.project.id, indexed]));

export function rankProjects(projects: PublicProject[], evidenceText: string, filters: { province?: string; university?: string; research_area?: string }) {
  const query = Array.from(new Set(terms(evidenceText))); const queryWeight = query.reduce((sum, term) => sum + idf(term), 0) || 1; const queryPhrases = query.length > 1 ? query : [];
  return projects.filter((project) => (!filters.province || (project.province || "").toLowerCase() === filters.province.toLowerCase()) && (!filters.university || (project.university || "").toLowerCase() === filters.university.toLowerCase()) && (!filters.research_area || searchable(project).toLowerCase().includes(filters.research_area.toLowerCase()))).map((project) => {
    const indexed = corpusIndexById.get(project.id) ?? (() => { const { fields, all } = indexFields(project); return { project, fields, all, allWeight: weightOf(all), titleWeight: weightOf(new Set(fields.title)) }; })(); const matched = query.filter((term) => indexed.all.has(term)); const matchedWeight = matched.reduce((sum, term) => sum + idf(term), 0);
    // How much of what THIS project is asking for shows up in the evidence, not how much of the
    // evidence's full vocabulary (soft skills, dates, filler from a long CV) appears in one project
    // description. The old denominator (full evidence weight) meant longer, more complete evidence
    // could only ever lower this signal, since no single project mentions most of a real CV. Same
    // rationale applies to titleCoverage below, normalized against the title's own (usually much
    // smaller) vocabulary weight instead of the full query weight.
    const evidenceCoverage = Math.min(1, matchedWeight / Math.min(queryWeight, indexed.allWeight));
    const titleMatched = query.filter((term) => indexed.fields.title.includes(term));
    const titleCoverage = Math.min(1, titleMatched.reduce((sum, term) => sum + idf(term), 0) / Math.min(queryWeight, indexed.titleWeight));
    let bm25 = 0;
    for (const term of query) { const termIdf = idf(term); for (const field of Object.keys(fieldWeights) as FieldName[]) { const tf = count(indexed.fields[field], term); if (!tf) continue; const length = indexed.fields[field].length; const normalization = 0.75 + 0.25 * (length / Math.max(1, averageLength[field])); bm25 += fieldWeights[field] * termIdf * ((tf * 2.2) / (tf + 1.2 * normalization)); } }
    const bm25Signal = bm25 / (bm25 + 12); const phraseSignal = queryPhrases.length > 1 ? Math.min(1, (Object.keys(fieldWeights) as FieldName[]).reduce((sum, field) => sum + phraseHits(queryPhrases, indexed.fields[field]), 0) / Math.max(1, queryPhrases.length - 1)) : 0; const score = Number(((bm25Signal * 0.55 + evidenceCoverage * 0.25 + phraseSignal * 0.1 + titleCoverage * 0.1) * 100).toFixed(1)); const missingEvidence = query.filter((term) => !indexed.all.has(term)).slice(0, 8);
    return { project_id: project.id, title: project.title, score, score_breakdown: { bm25_relevance: Number((bm25Signal * 55).toFixed(2)), evidence_coverage: Number((evidenceCoverage * 25).toFixed(2)), phrase_match: Number((phraseSignal * 10).toFixed(2)), title_relevance: Number((titleCoverage * 10).toFixed(2)) }, group: score >= 65 ? "ambitious" : score >= 35 ? "strong-fit" : "reliable", matched_evidence: matched.slice(0, 20), missing_evidence: missingEvidence.length ? missingEvidence : ["No major vocabulary gap detected; verify the full project requirements manually"], risks: ["Lexical BM25 evidence signal only; review requirements and eligibility manually"], metadata: { ProjectID: project.id, ProjectTitle: project.title, LanguageUsed: project.language, StartDate: project.start_date, isStartDateFlexible: project.flexible_start, NotesOnStartDate: project.start_notes, Province: project.province, PreferredBackgroundCollection: project.skills_background, "Professor.FirstName": project.supervisor.first_name, "Professor.LastName": project.supervisor.last_name, "Professor.UniversityName": project.university, "Professor.CampusName": project.campus }, source_url: GLOBALINK_PORTAL_URL, text_preview: project.description_preview };
  }).sort((a, b) => b.score - a.score || a.project_id.localeCompare(b.project_id));
}
