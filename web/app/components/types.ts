import { DocumentRecord, LocalShortlistItem, Profile, Provider, ReferenceAnnotation } from "../../lib/localMode";

export type Project = { project_id: string; title: string; score?: number; group?: string; metadata?: Record<string, any>; matched_evidence?: string[]; missing_evidence?: string[]; risks?: string[]; text_preview?: string; source_url?: string };
export type StepId = "knowledge" | "profile" | "results" | "shortlist";
export type WorkspaceStep = readonly [StepId, string];

export type CommonWorkspaceProps = { documents: DocumentRecord[]; profile: Profile | null; shortlist: LocalShortlistItem[]; annotations: ReferenceAnnotation[]; provider: Provider; model: string; keyReady: boolean; status: string; busy: boolean };
