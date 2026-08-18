import { PublicProject } from "../publicCorpus";
import { embedLocal, DIMENSIONS } from "./semantic";

export type EmbeddingVector = number[];
export interface EmbeddingProvider { embedCandidateProfile(text: string): Promise<EmbeddingVector>; embedProject(project: PublicProject): Promise<EmbeddingVector>; embedBatch(projects: PublicProject[]): Promise<EmbeddingVector[]>; }
export function validateEmbedding(vector: number[], dimensions = DIMENSIONS) { if (vector.length !== dimensions || vector.some((value) => !Number.isFinite(value))) throw new Error(`Embedding must contain ${dimensions} finite values.`); return vector; }
export const localEmbeddingProvider: EmbeddingProvider = { async embedCandidateProfile(text) { return validateEmbedding(embedLocal(text)); }, async embedProject(project) { return validateEmbedding(embedLocal(`${project.title} ${project.description_preview} ${project.research_area} ${project.skills_background || ""}`)); }, async embedBatch(projects) { return projects.map((project) => validateEmbedding(embedLocal(`${project.title} ${project.description_preview} ${project.research_area} ${project.skills_background || ""}`))); } };
