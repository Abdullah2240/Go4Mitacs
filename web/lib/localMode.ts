export type Provider = "openrouter" | "gemini" | "huggingface" | "openai";
export type DocumentRecord = { id: string; name: string; type: string; chars: number; text: string; hash: string; status: "ready" | "error"; error?: string; size: number; createdAt: string; kind?: "candidate" | "reference" };
export type LocalShortlistItem = { project_id: string; title: string; classification: string; rank: number };
export type Profile = { skills: string[]; tools: string[]; domains: string[]; methods: string[]; evidence: string[]; gaps: string[] };
export type ReferenceAnnotation = { project_id: string; note: string; source_document_id: string; context: "historical" };
export type KeyStatus = "untested" | "valid" | "rate-limited" | "invalid";
export type PooledKey = { id: string; label: string; value: string; status: KeyStatus };

const KEY_PREFIX = "mitacs:provider-key:";
const POOL_PREFIX = "mitacs:provider-keypool:";
const DOCS_KEY = "mitacs:knowledge-base";
const PROFILE_KEY = "mitacs:profile";
const PROFILE_VERSION_KEY = "mitacs:profile-version";
const RESULTS_KEY = "mitacs:results";
const RESULTS_VERSION_KEY = "mitacs:results-version";
const SHORTLIST_KEY = "mitacs:local-shortlist";
const CACHE_KEY = "mitacs:ai-cache";
const REFERENCE_NOTES_KEY = "mitacs:reference-annotations";

export const providerKeyName = (provider: Provider) => `${KEY_PREFIX}${provider}`;
export const hasProviderKey = (provider: Provider) => getKeyPool(provider).some((key) => key.status !== "invalid");
export const getProviderKey = (provider: Provider) => getKeyPool(provider).find((key) => key.status === "valid" || key.status === "untested")?.value ?? "";
export const saveProviderKey = (provider: Provider, value: string) => { addPoolKey(provider, "Key 1", value); };
export const forgetProviderKey = (provider: Provider) => { savePoolKeys(provider, []); };

const poolKeyName = (provider: Provider) => `${POOL_PREFIX}${provider}`;
export const getKeyPool = (provider: Provider): PooledKey[] => { if (typeof window === "undefined") return []; try { return JSON.parse(window.sessionStorage.getItem(poolKeyName(provider)) ?? "[]"); } catch { return []; } };
export const savePoolKeys = (provider: Provider, keys: PooledKey[]) => { if (typeof window !== "undefined") window.sessionStorage.setItem(poolKeyName(provider), JSON.stringify(keys)); };
export const addPoolKey = (provider: Provider, label: string, value: string) => { const pool = getKeyPool(provider); const next = [...pool, { id: `${Date.now()}-${pool.length}`, label: label || `Key ${pool.length + 1}`, value, status: "untested" as KeyStatus }]; savePoolKeys(provider, next); return next; };
export const removePoolKey = (provider: Provider, id: string) => { savePoolKeys(provider, getKeyPool(provider).filter((key) => key.id !== id)); };
export const setPoolKeyStatus = (provider: Provider, id: string, status: KeyStatus) => { savePoolKeys(provider, getKeyPool(provider).map((key) => key.id === id ? { ...key, status } : key)); };
export const nextUsableKey = (provider: Provider, triedIds: string[]): PooledKey | null => getKeyPool(provider).find((key) => key.status !== "invalid" && !triedIds.includes(key.id)) ?? null;

export const hashText = (text: string) => { let hash = 0; for (let i = 0; i < text.length; i++) { hash = (Math.imul(31, hash) + text.charCodeAt(i)) | 0; } return hash.toString(36); };
export const getProfileVersion = (): string => typeof window === "undefined" ? "" : window.sessionStorage.getItem(PROFILE_VERSION_KEY) ?? "";
export const setProfileVersion = (version: string) => { if (typeof window !== "undefined") window.sessionStorage.setItem(PROFILE_VERSION_KEY, version); };
export const getResultsVersion = (): string => typeof window === "undefined" ? "" : window.sessionStorage.getItem(RESULTS_VERSION_KEY) ?? "";
export const setResultsVersion = (version: string) => { if (typeof window !== "undefined") window.sessionStorage.setItem(RESULTS_VERSION_KEY, version); };

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
