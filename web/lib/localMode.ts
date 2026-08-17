export type Provider = "openrouter" | "gemini" | "huggingface";

const KEY_PREFIX = "mitacs:provider-key:";
const CANDIDATE_KEY = "mitacs:local-candidate-evidence";
const SHORTLIST_KEY = "mitacs:local-shortlist";

export function providerKeyName(provider: Provider): string {
  return `${KEY_PREFIX}${provider}`;
}

export function hasProviderKey(provider: Provider): boolean {
  return typeof window !== "undefined" && Boolean(window.sessionStorage.getItem(providerKeyName(provider)));
}

export function saveProviderKey(provider: Provider, value: string): void {
  if (typeof window !== "undefined") window.sessionStorage.setItem(providerKeyName(provider), value);
}

export function forgetProviderKey(provider: Provider): void {
  if (typeof window !== "undefined") window.sessionStorage.removeItem(providerKeyName(provider));
}

export function loadCandidateEvidence(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(CANDIDATE_KEY) ?? "";
}

export function saveCandidateEvidence(value: string): void {
  if (typeof window !== "undefined") window.localStorage.setItem(CANDIDATE_KEY, value);
}

export type LocalShortlistItem = { project_id: string; title: string; classification: string };

export function loadLocalShortlist(): LocalShortlistItem[] {
  if (typeof window === "undefined") return [];
  try { return JSON.parse(window.localStorage.getItem(SHORTLIST_KEY) ?? "[]"); } catch { return []; }
}

export function saveLocalShortlist(items: LocalShortlistItem[]): void {
  if (typeof window !== "undefined") window.localStorage.setItem(SHORTLIST_KEY, JSON.stringify(items));
}
