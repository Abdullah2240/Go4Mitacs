"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { buildLocalProfile } from "../lib/profile";
import { parseDocument, pasteDocument } from "../lib/documentParser";
import { clearKnowledgeBase, clearShortlist, DocumentRecord, forgetProviderKey, hasProviderKey, loadDocuments, loadLocalShortlist, loadProfile, loadReferenceAnnotations, LocalShortlistItem, Profile, ReferenceAnnotation, saveDocuments, saveLocalShortlist, saveProfile, saveReferenceAnnotations, Provider } from "../lib/localMode";
import { AppHeader } from "./components/AppHeader";
import { EvidenceWorkspace } from "./components/EvidenceWorkspace";
import { ProfileReview } from "./components/ProfileReview";
import { WorkspaceTabs } from "./components/WorkspaceTabs";
import { Project, StepId } from "./components/types";
import { MatchResults } from "./components/MatchResults";
import { ProjectInspector } from "./components/ProjectInspector";
import { ShortlistWorkspace } from "./components/ShortlistWorkspace";
import { SettingsDialog } from "./components/SettingsDialog";

const providerDefaults: Record<Provider, string> = { openrouter: "openai/gpt-4o-mini", gemini: "gemini-2.0-flash", huggingface: "Qwen/Qwen2.5-7B-Instruct" };
const steps = [["knowledge", "Evidence"], ["profile", "Profile"], ["results", "Matches"], ["shortlist", "Shortlist"]] as const;

export default function Home() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [shortlist, setShortlist] = useState<LocalShortlistItem[]>([]);
  const [annotations, setAnnotations] = useState<ReferenceAnnotation[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [provider, setProvider] = useState<Provider>("openrouter");
  const [model, setModel] = useState(providerDefaults.openrouter);
  const [keyReady, setKeyReady] = useState(false);
  const [tab, setTab] = useState("knowledge");
  const [paste, setPaste] = useState("");
  const [status, setStatus] = useState("Add evidence to begin. The hosted site needs a network connection for public corpus routes.");
  const [busy, setBusy] = useState(false);
  const [filters, setFilters] = useState({ province: "", university: "", research: "" });
  const [width, setWidth] = useState("60");
  const [detail, setDetail] = useState<Project | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [consent, setConsent] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  useEffect(() => { setDocuments(loadDocuments()); setProfile(loadProfile()); setShortlist(loadLocalShortlist()); setAnnotations(loadReferenceAnnotations()); setKeyReady(hasProviderKey(provider)); }, [provider]);
  useEffect(() => { if (!detail && !settingsOpen && !consent) return; const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") { setDetail(null); setSettingsOpen(false); setConsent(false); } }; document.addEventListener("keydown", closeOnEscape); return () => document.removeEventListener("keydown", closeOnEscape); }, [detail, settingsOpen, consent]);

  const combinedText = useMemo(() => documents.filter((d) => d.status === "ready" && d.kind !== "reference").map((d) => d.text).join("\n\n"), [documents]);
  const candidateDocuments = documents.filter((doc) => doc.kind !== "reference");
  const referenceDocuments = documents.filter((doc) => doc.kind === "reference");
  const corpusLabel = projects.length ? `${projects.length} shown from all 3,359 screened` : "3,359 public projects";

  function addDocs(files: FileList | File[], kind: "candidate" | "reference" = "candidate") { setBusy(true); Promise.all(Array.from(files).map((file) => parseDocument(file, kind))).then((parsed) => { const existing = new Set(documents.map((d) => d.hash)); const fresh = parsed.filter((d) => !d.hash || !existing.has(d.hash)); const next = [...documents, ...fresh]; setDocuments(next); saveDocuments(next); setStatus(`${fresh.length} ${kind === "reference" ? "private context " : ""}document${fresh.length === 1 ? "" : "s"} added locally. Duplicate content was skipped.`); }).finally(() => setBusy(false)); }
  function removeDoc(id: string) { const next = documents.filter((d) => d.id !== id); setDocuments(next); saveDocuments(next); const notes = annotations.filter((item) => item.source_document_id !== id); setAnnotations(notes); saveReferenceAnnotations(notes); setStatus("Document and any derived annotations were removed from this browser workspace."); }
  async function addPaste(event: FormEvent) { event.preventDefault(); if (!paste.trim()) return; const doc = await pasteDocument(paste); if (documents.some((d) => d.hash === doc.hash)) { setStatus("That pasted content is already in the workspace."); return; } const next = [...documents, doc]; setDocuments(next); saveDocuments(next); setPaste(""); setStatus("Pasted evidence added locally."); }
  function buildProfile() { if (!combinedText) { setStatus("Add at least one parsed evidence document first."); return; } const next = buildLocalProfile(documents); setProfile(next); saveProfile(next); setTab("profile"); setStatus("Local profile built from your evidence. Review it before matching."); }
  async function runMatch(event?: FormEvent) { event?.preventDefault(); if (!profile && !combinedText) { setStatus("Build a profile or add evidence first."); return; } setBusy(true); setTab("results"); setStatus("Screening the complete Mitacs corpus..."); try { const response = await fetch("/api/local/matches?limit=50", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ evidence_text: profile ? [...profile.skills, ...profile.tools, ...profile.domains, ...profile.methods, ...profile.evidence].join(" ") : combinedText, filters: { Province: filters.province, "Professor.UniversityName": filters.university, research_area: filters.research } }) }); const body = await response.json(); if (!response.ok) throw new Error(body.detail ?? "Matching failed"); setProjects(body.items ?? []); setStatus(`Full-corpus retrieval complete. ${body.considered ?? 3359} projects were screened.`); } catch (error) { setStatus(error instanceof Error ? error.message : "Matching failed. Your local evidence is preserved."); } finally { setBusy(false); } }
  function addShortlist(project: Project) { if (shortlist.some((x) => x.project_id === project.project_id)) return; const next = [...shortlist, { project_id: project.project_id, title: project.title, classification: project.group ?? "strong-fit", rank: shortlist.length + 1 }]; setShortlist(next); saveLocalShortlist(next); setStatus("Saved to the local shortlist."); }
  function classify(id: string, classification: string) { const next = shortlist.map((x) => x.project_id === id ? { ...x, classification } : x); setShortlist(next); saveLocalShortlist(next); }
  function toggleCompare(id: string) { setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : current.length >= 4 ? current : [...current, id]); }
  function exportMarkdown() { const body = shortlist.map((x, i) => `${i + 1}. **${x.title}** (${x.project_id}) - ${x.classification}`).join("\n"); const blob = new Blob([`# Mitacs shortlist\n\n${body || "No projects saved."}\n\n_Local browser export._`], { type: "text/markdown" }); const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "mitacs-shortlist.md"; a.click(); URL.revokeObjectURL(a.href); }
  function saveKey(event: FormEvent) { event.preventDefault(); const input = event.currentTarget.querySelector("input") as HTMLInputElement; if (input.value.trim()) { sessionStorage.setItem(`mitacs:provider-key:${provider}`, input.value.trim()); input.value = ""; setKeyReady(true); setStatus("Key held in sessionStorage only. No provider call was made."); } }
  function clearAll() { if (!window.confirm("Clear all local documents, profile, results, shortlist, and private context?")) return; clearKnowledgeBase(); clearShortlist(); setDocuments([]); setProfile(null); setProjects([]); setShortlist([]); setAnnotations([]); setStatus("Local workspace cleared."); }
  function saveAnnotation(project: Project, note: string) { const source = documents.find((doc) => doc.kind === "reference" && doc.status === "ready"); if (!source || !note.trim()) return; const next = [...annotations.filter((item) => item.project_id !== project.project_id), { project_id: project.project_id, note: note.trim(), source_document_id: source.id, context: "historical" as const }]; setAnnotations(next); saveReferenceAnnotations(next); setStatus("Historical context annotation saved locally. It does not affect ranking."); }
  const updateProfile = (field: keyof Profile, value: string) => { if (!profile) return; const next = { ...profile, [field]: value.split(",").map((x) => x.trim()).filter(Boolean) }; setProfile(next); saveProfile(next); };

  return <main className="shell">
    <AppHeader onSettings={() => setSettingsOpen(true)} onClear={clearAll} />
    <div className="workspace-shell">
      <WorkspaceTabs active={tab as StepId} steps={steps} onChange={(step) => setTab(step)} />
      <div className="statusbar" role="status"><span className={busy ? "pulse" : "status-mark"} />{status}</div>
      <section className="content">
        {tab === "knowledge" && <EvidenceWorkspace documents={documents} annotations={annotations} onAddDocuments={addDocs} onPaste={addPaste} paste={paste} setPaste={setPaste} onRemove={removeDoc} onBuild={buildProfile} canBuild={Boolean(combinedText)} />}
        {tab === "profile" && <ProfileReview profile={profile} onChange={updateProfile} onContinue={() => runMatch()} onBack={() => setTab("knowledge")} />}
        {tab === "results" && <MatchResults projects={projects} corpusLabel={corpusLabel} filters={filters} onFiltersChange={setFilters} onRunMatch={() => runMatch()} canRun={Boolean(profile || combinedText)} selected={selected} onToggleCompare={toggleCompare} onOpen={setDetail} onSave={addShortlist} reviewWidth={width} onReviewWidth={setWidth} />}
        {tab === "shortlist" && <ShortlistWorkspace shortlist={shortlist} projects={projects} selected={selected} onClassify={classify} onRemoveCompare={toggleCompare} onExport={exportMarkdown} onBack={() => setTab("results")} />}
      </section>
    </div>
      <ProjectInspector project={detail} annotations={annotations} referenceDocuments={referenceDocuments} onClose={() => setDetail(null)} onSaveAnnotation={saveAnnotation} />
      {settingsOpen && <SettingsDialog provider={provider} model={model} keyReady={keyReady} onProvider={(value) => { setProvider(value); setModel(providerDefaults[value]); }} onModel={setModel} onSaveKey={saveKey} onForgetKey={() => { forgetProviderKey(provider); setKeyReady(false); }} onClose={() => setSettingsOpen(false)} onConsent={() => { setSettingsOpen(false); setConsent(true); }} />}
    {consent && <div className="modal-backdrop"><div className="modal consent"><button className="modal-close" onClick={() => setConsent(false)}>Close</button><p className="eyebrow">Consent policy</p><h2>Before any provider request</h2><p>This app would name the selected provider and model, list the exact categories of content being sent, explain that the key and content are used only for that action, and let you cancel.</p><p>Live AI reranking is not available in this deployment. No provider request has been made.</p><button className="button primary" onClick={() => setConsent(false)}>Done</button></div></div>}
    <footer className="footer-note">Go4Mitacs is an independent project-matching tool and is not affiliated with or endorsed by Mitacs.</footer>
  </main>;
}
