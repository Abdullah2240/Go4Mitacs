import { embedLocal, cosineSimilarity } from "./semantic";

export type EvaluationLabel = "strong" | "partial" | "weak" | "keyword-trap" | "missing-evidence";
export type EvaluationFixture = { id: string; label: EvaluationLabel; query: string; project: string; expectedRelevant: boolean };
export const evaluationFixtures: EvaluationFixture[] = [
  { id: "strong", label: "strong", query: "python machine learning image classification", project: "Python machine learning image classification research", expectedRelevant: true },
  { id: "partial", label: "partial", query: "python data analysis", project: "Environmental data analysis with statistical modelling", expectedRelevant: true },
  { id: "weak", label: "weak", query: "robotics control systems", project: "Forest ecology and biodiversity monitoring", expectedRelevant: false },
  { id: "keyword-trap", label: "keyword-trap", query: "python", project: "Python-shaped protein structures in molecular biology", expectedRelevant: false },
  { id: "missing-evidence", label: "missing-evidence", query: "quantum chemistry laboratory", project: "Chemistry education literature review", expectedRelevant: false },
];
export function evaluateLocalBaseline(fixtures = evaluationFixtures) { const results = fixtures.map((fixture) => ({ ...fixture, similarity: cosineSimilarity(embedLocal(fixture.query), embedLocal(fixture.project)) })); const top10 = results.slice().sort((a, b) => b.similarity - a.similarity).slice(0, 10); const relevant = top10.filter((result) => result.expectedRelevant).length; return { precisionAt10: relevant / Math.max(1, top10.length), falsePositiveRate: top10.filter((result) => !result.expectedRelevant).length / Math.max(1, top10.length), fixtureCount: fixtures.length, results }; }
