import { DocumentRecord, Profile, Provider } from "../localMode";
import { PublicProject } from "../publicCorpus";

export type AIAction = "profile" | "rerank" | "cv-align";
export type EvidenceExcerpt = { sourceId: string; sourceName: string; text: string; isPrivate: boolean };
export type SanitizedEvidence = { excerpts: EvidenceExcerpt[]; includedSourceIds: string[]; excludedSourceIds: string[]; characters: number; estimatedTokens: number };
export type AIRequestReceipt = { provider: Provider; model: string; action: AIAction; timestamp: string; includedSourceIds: string[]; excludedSourceIds: string[]; outcome: "ai" | "deterministic-fallback" };
export type ProviderRequest = { provider: Provider; model: string; key: string; system: string; user: string; signal?: AbortSignal };
export type ProviderResponse = { text: string; provider: Provider; model: string };
export type ProfileClaim = { text: string; confidence: number; sourceIds: string[]; status?: "proposed" | "approved" | "rejected" | "unsupported" };
export type AIProfileProposal = { headline: ProfileClaim | null; technicalSkills: Record<string, ProfileClaim[]>; researchInterests: ProfileClaim[]; experienceBullets: ProfileClaim[]; projectSummaries: ProfileClaim[]; measurableOutcomes: ProfileClaim[]; strengths: ProfileClaim[]; missingInformation: string[]; questions: string[] };
export type RerankItem = { projectId: string; rank: number; finalFitScore: number; matchedEvidence: string[]; missingEvidence: string[]; whyItFits: string; emphasize: string[]; uncertainty: string[] };
export type CombinedScore = { projectId: string; semanticSimilarity: number; keywordOverlap: number; disciplineFit: number; evidenceCoverage: number; missingRequirements: string[]; finalScore: number; explanation: string; confidence: number };
export type CVAlignmentDraft = { summary: ProfileClaim | null; reorderedSkills: ProfileClaim[]; projectBullets: ProfileClaim[]; researchInterests: ProfileClaim[]; suggestedKeywords: string[]; gapAnalysis: string[]; questions: string[] };
export function profileToText(profile: Profile | null) { return profile ? [...profile.skills, ...profile.tools, ...profile.domains, ...profile.methods, ...profile.evidence].join(" ") : ""; }
export function projectToText(project: PublicProject) { return [project.title, project.description_preview, project.research_area, project.skills_background, project.university, project.province].filter(Boolean).join(" "); }
export function selectedDocuments(documents: DocumentRecord[], ids: string[]) { return documents.filter((document) => ids.includes(document.id)); }
