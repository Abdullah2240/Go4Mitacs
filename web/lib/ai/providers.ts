import { getKeyPool, nextUsableKey, Provider, setPoolKeyStatus } from "../localMode";
import { ProviderRequest, ProviderResponse } from "./contracts";
export class ProviderError extends Error { constructor(public code: "invalid-key" | "rate-limit" | "network" | "timeout" | "malformed" | "loading" | "provider", message: string) { super(message); } }
export type PoolAttemptLog = { keyLabel: string; outcome: "sending" | "succeeded" | "rate-limited" | "failed" };
export async function requestProviderWithPool(request: Omit<ProviderRequest, "key">, onAttempt?: (entry: PoolAttemptLog) => void): Promise<ProviderResponse> {
  const pool = getKeyPool(request.provider);
  if (!pool.length) throw new ProviderError("invalid-key", "Add a provider key in Settings first.");
  const tried: string[] = [];
  let candidate = nextUsableKey(request.provider, tried);
  while (candidate) {
    tried.push(candidate.id);
    onAttempt?.({ keyLabel: candidate.label, outcome: "sending" });
    try {
      const response = await requestProvider({ ...request, key: candidate.value });
      setPoolKeyStatus(request.provider, candidate.id, "valid");
      onAttempt?.({ keyLabel: candidate.label, outcome: "succeeded" });
      return response;
    } catch (error) {
      if (error instanceof ProviderError && error.code === "rate-limit") {
        setPoolKeyStatus(request.provider, candidate.id, "rate-limited");
        onAttempt?.({ keyLabel: candidate.label, outcome: "rate-limited" });
        candidate = nextUsableKey(request.provider, tried);
        continue;
      }
      if (error instanceof ProviderError && error.code === "invalid-key") setPoolKeyStatus(request.provider, candidate.id, "invalid");
      onAttempt?.({ keyLabel: candidate.label, outcome: "failed" });
      throw error;
    }
  }
  throw new ProviderError("rate-limit", `All ${pool.length} ${request.provider} key${pool.length === 1 ? "" : "s"} are rate-limited or invalid. Add another key in Settings to continue.`);
}
export function classifyProviderStatus(status: number): ProviderError["code"] { if (status === 401 || status === 403) return "invalid-key"; if (status === 429) return "rate-limit"; if (status === 503) return "loading"; return "provider"; }
function timeoutSignal(signal?: AbortSignal) { const controller = new AbortController(); const timeout = window.setTimeout(() => controller.abort(), 30000); signal?.addEventListener("abort", () => controller.abort(), { once: true }); return { signal: controller.signal, clear: () => window.clearTimeout(timeout) }; }
export async function requestProvider(request: ProviderRequest): Promise<ProviderResponse> { if (!request.key.trim()) throw new ProviderError("invalid-key", "Add a provider key in Settings first."); const timed = timeoutSignal(request.signal); try { let response: Response; if (request.provider === "openrouter") response = await fetch("https://openrouter.ai/api/v1/chat/completions", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${request.key}` }, body: JSON.stringify({ model: request.model, messages: [{ role: "system", content: request.system }, { role: "user", content: request.user }], temperature: 0 }), signal: timed.signal }); else if (request.provider === "gemini") response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(request.model)}:generateContent`, { method: "POST", headers: { "Content-Type": "application/json", "x-goog-api-key": request.key }, body: JSON.stringify({ systemInstruction: { parts: [{ text: request.system }] }, contents: [{ role: "user", parts: [{ text: request.user }] }], generationConfig: { temperature: 0, responseMimeType: "application/json" } }), signal: timed.signal }); else if (request.provider === "openai") response = await fetch("https://api.openai.com/v1/chat/completions", { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${request.key}` }, body: JSON.stringify({ model: request.model, messages: [{ role: "system", content: request.system }, { role: "user", content: request.user }], temperature: 0 }), signal: timed.signal }); else response = await fetch(`https://api-inference.huggingface.co/models/${request.model}`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${request.key}` }, body: JSON.stringify({ inputs: `${request.system}\n\n${request.user}`, parameters: { return_full_text: false, temperature: 0 } }), signal: timed.signal }); if (!response.ok) throw new ProviderError(classifyProviderStatus(response.status), response.status === 503 ? "The selected model is still loading. Try again shortly." : "The selected provider could not complete this request."); let body: any; try { body = await response.json(); } catch { throw new ProviderError("malformed", "The provider returned invalid JSON."); } if (body?.error && request.provider === "huggingface") throw new ProviderError("loading", "The selected model is still loading. Try again shortly."); const text = request.provider === "openrouter" || request.provider === "openai" ? body?.choices?.[0]?.message?.content : request.provider === "gemini" ? body?.candidates?.[0]?.content?.parts?.[0]?.text : Array.isArray(body) ? body?.[0]?.generated_text : body?.generated_text; if (typeof text !== "string" || !text.trim()) throw new ProviderError("malformed", "The provider returned an unreadable response."); return { text, provider: request.provider, model: request.model }; } catch (error) { if (error instanceof ProviderError) throw error; if (error instanceof DOMException && error.name === "AbortError") throw new ProviderError("timeout", "The provider request timed out or was cancelled."); throw new ProviderError("network", "The provider could not be reached. Your deterministic results are unchanged."); } finally { timed.clear(); } }
