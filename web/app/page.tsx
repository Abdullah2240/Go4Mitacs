"use client";

import { FormEvent, useEffect, useState } from "react";
import { forgetProviderKey, hasProviderKey, loadCandidateEvidence, loadLocalShortlist, LocalShortlistItem, Provider, saveCandidateEvidence, saveLocalShortlist, saveProviderKey } from "../lib/localMode";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";
type Project = { project_id: string; title: string; score?: number; group?: string; metadata?: Record<string, unknown> };

export default function Home() {
  const [provider, setProvider] = useState<Provider>("openrouter");
  const [keyInput, setKeyInput] = useState("");
  const [keyReady, setKeyReady] = useState(false);
  const [evidence, setEvidence] = useState("");
  const [projects, setProjects] = useState<Project[]>([]);
  const [shortlist, setShortlist] = useState<LocalShortlistItem[]>([]);
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState("Local-only mode is ready; no login or AI key is required.");

  useEffect(() => {
    setEvidence(loadCandidateEvidence());
    setShortlist(loadLocalShortlist());
    setKeyReady(hasProviderKey(provider));
  }, [provider]);

  function saveKey(event: FormEvent) {
    event.preventDefault();
    if (!keyInput.trim()) { setMessage("Enter a key or continue without one."); return; }
    saveProviderKey(provider, keyInput.trim());
    setKeyInput("");
    setKeyReady(true);
    setMessage("Key held for this browser session only. No external AI call was made.");
  }

  function forgetKey() {
    forgetProviderKey(provider);
    setKeyInput("");
    setKeyReady(false);
    setMessage("Provider key forgotten from this browser session.");
  }

  async function search(event?: FormEvent) {
    event?.preventDefault();
    setMessage("Searching public projects...");
    try {
      const response = await fetch(`${API_URL}/api/v1/projects?q=${encodeURIComponent(query)}&limit=30`);
      const body = await response.json();
      if (!response.ok) throw new Error("Public project search is unavailable");
      setProjects(body.items ?? []);
      setMessage(`${body.total ?? 0} public projects found`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Search failed"); }
  }

  async function runLocalMatch() {
    if (!evidence.trim()) { setMessage("Add candidate evidence before matching."); return; }
    saveCandidateEvidence(evidence);
    setMessage("Running deterministic local matching...");
    try {
      const response = await fetch(`${API_URL}/api/v1/local/matches?limit=15`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ evidence_text: evidence }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Local matching failed");
      setProjects(body.items ?? []);
      setMessage("Local matches ready. Evidence was sent only to this local API.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Local matching failed"); }
  }

  function addToShortlist(project: Project) {
    if (shortlist.some((item) => item.project_id === project.project_id)) { setMessage("Project is already in the local shortlist."); return; }
    const next = [...shortlist, { project_id: project.project_id, title: project.title, classification: project.group ?? "strong-fit" }];
    setShortlist(next); saveLocalShortlist(next); setMessage("Added to local shortlist.");
  }

  function removeFromShortlist(projectId: string) {
    const next = shortlist.filter((item) => item.project_id !== projectId);
    setShortlist(next); saveLocalShortlist(next); setMessage("Removed from local shortlist.");
  }

  function classify(projectId: string, classification: string) {
    const next = shortlist.map((item) => item.project_id === projectId ? { ...item, classification } : item);
    setShortlist(next); saveLocalShortlist(next);
  }

  return <main style={{ maxWidth: 1080, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
    <header><h1>Mitacs Matcher</h1><p>Local-only, evidence-led project matching. No registration, login, or cloud sync.</p></header>
    <section style={{ border: "1px solid #dce4ec", padding: 16, borderRadius: 12 }}>
      <h2>Optional provider key</h2>
      <p>Keys are held in sessionStorage for this tab only. They are not sent to the backend, Supabase, or external providers. Browser-held keys are inspectable by the browser owner.</p>
      <form onSubmit={saveKey} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <select aria-label="AI provider" value={provider} onChange={(event) => setProvider(event.target.value as Provider)}><option value="openrouter">OpenRouter</option><option value="gemini">Gemini</option><option value="huggingface">Hugging Face</option></select>
        <input aria-label="Provider API key" type="password" value={keyInput} onChange={(event) => setKeyInput(event.target.value)} placeholder="Optional provider key" autoComplete="off" />
        <button type="submit">Hold key for session</button>{keyReady && <button type="button" onClick={forgetKey}>Forget key</button>}
      </form>
      <small>{keyReady ? `${provider} key is held for this session.` : "No provider key held. Local matching still works."} External AI calls are not implemented.</small>
    </section>
    <section style={{ marginTop: 24 }}><h2>Candidate evidence</h2><p>Stored locally in this browser. Local storage is not an encrypted vault and is not synced across devices.</p><textarea aria-label="Candidate evidence" rows={5} value={evidence} onChange={(event) => setEvidence(event.target.value)} placeholder="Paste non-sensitive evidence, skills, methods, or project notes" style={{ width: "100%" }} /><button onClick={runLocalMatch} style={{ marginTop: 8 }}>Run local match</button></section>
    <section style={{ marginTop: 24 }}><h2>Public projects</h2><form onSubmit={search}><input aria-label="Project search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search the public corpus" /><button type="submit">Search</button></form><p role="status">{message}</p><ul>{projects.map((project) => <li key={project.project_id}><strong>{project.title}</strong> ({project.project_id}) {project.score !== undefined && ` - ${project.score} / ${project.group}`} <button onClick={() => addToShortlist(project)}>Add</button></li>)}</ul></section>
    <section style={{ marginTop: 24 }}><h2>Local shortlist</h2>{shortlist.length === 0 ? <p>Your local shortlist is empty.</p> : <ol>{shortlist.map((item) => <li key={item.project_id}>{item.title} <select aria-label={`Classification for ${item.title}`} value={item.classification} onChange={(event) => classify(item.project_id, event.target.value)}><option>ambitious</option><option>strong-fit</option><option>reliable</option><option>confirmed</option></select> <button onClick={() => removeFromShortlist(item.project_id)}>Remove</button></li>)}</ol>}</section>
  </main>;
}
