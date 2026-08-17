export type Provider = "openrouter" | "gemini" | "huggingface";
export type DocumentRecord = { id: string; name: string; type: string; chars: number; text: string; hash: string; status: "ready" | "error"; error?: string; size: number; createdAt: string; kind?: "candidate" | "reference" };
export type LocalShortlistItem = { project_id: string; title: string; classification: string; rank: number };
export type Profile = { skills: string[]; tools: string[]; domains: string[]; methods: string[]; evidence: string[]; gaps: string[] };
export type ReferenceAnnotation = { project_id: string; note: string; source_document_id: string; context: "historical" };

const KEY_PREFIX = "mitacs:provider-key:";
const DOCS_KEY = "mitacs:knowledge-base";
const PROFILE_KEY = "mitacs:profile";
const RESULTS_KEY = "mitacs:results";
const SHORTLIST_KEY = "mitacs:local-shortlist";
const CACHE_KEY = "mitacs:ai-cache";
const REFERENCE_NOTES_KEY = "mitacs:reference-annotations";

export const providerKeyName = (provider: Provider) => `${KEY_PREFIX}${provider}`;
export const hasProviderKey = (provider: Provider) => typeof window !== "undefined" && Boolean(window.sessionStorage.getItem(providerKeyName(provider)));
export const getProviderKey = (provider: Provider) => typeof window === "undefined" ? "" : window.sessionStorage.getItem(providerKeyName(provider)) ?? "";
export const saveProviderKey = (provider: Provider, value: string) => { if (typeof window !== "undefined") window.sessionStorage.setItem(providerKeyName(provider), value); };
export const forgetProviderKey = (provider: Provider) => { if (typeof window !== "undefined") window.sessionStorage.removeItem(providerKeyName(provider)); };

export const loadDocuments = (): DocumentRecord[] => { if (typeof window === "undefined") return []; try { return JSON.parse(localStorage.getItem(DOCS_KEY) ?? "[]"); } catch { return []; } };
export const saveDocuments = (items: DocumentRecord[]) => { if (typeof window !== "undefined") localStorage.setItem(DOCS_KEY, JSON.stringify(items)); };
export const clearKnowledgeBase = () => { if (typeof window !== "undefined") { localStorage.removeItem(DOCS_KEY); localStorage.removeItem(PROFILE_KEY); localStorage.removeItem(RESULTS_KEY); localStorage.removeItem(REFERENCE_NOTES_KEY); } };
export const loadProfile = (): Profile | null => { if (typeof window === "undefined") return null; try { const raw = localStorage.getItem(PROFILE_KEY); return raw ? JSON.parse(raw) : null; } catch { return null; } };
export const saveProfile = (profile: Profile) => { if (typeof window !== "undefined") localStorage.setItem(PROFILE_KEY, JSON.stringify(profile)); };
export const loadResults = (): unknown[] => { if (typeof window === "undefined") return []; try { return JSON.parse(localStorage.getItem(RESULTS_KEY) ?? "[]"); } catch { return []; } };
export const saveResults = (results: unknown[]) => { if (typeof window !== "undefined") localStorage.setItem(RESULTS_KEY, JSON.stringify(results)); };
export const loadLocalShortlist = (): LocalShortlistItem[] => { if (typeof window === "undefined") return []; try { return JSON.parse(localStorage.getItem(SHORTLIST_KEY) ?? "[]"); } catch { return []; } };
export const saveLocalShortlist = (items: LocalShortlistItem[]) => { if (typeof window !== "undefined") localStorage.setItem(SHORTLIST_KEY, JSON.stringify(items)); };
export const clearShortlist = () => { if (typeof window !== "undefined") localStorage.removeItem(SHORTLIST_KEY); };
export const loadReferenceAnnotations = (): ReferenceAnnotation[] => { if (typeof window === "undefined") return []; try { return JSON.parse(localStorage.getItem(REFERENCE_NOTES_KEY) ?? "[]"); } catch { return []; } };
export const saveReferenceAnnotations = (items: ReferenceAnnotation[]) => { if (typeof window !== "undefined") localStorage.setItem(REFERENCE_NOTES_KEY, JSON.stringify(items)); };
export const clearReferenceContext = () => { if (typeof window !== "undefined") { localStorage.removeItem(REFERENCE_NOTES_KEY); const next = loadDocuments().filter((doc) => doc.kind !== "reference"); saveDocuments(next); } };
export const cacheKey = (key: string) => `${CACHE_KEY}:${key}`;
