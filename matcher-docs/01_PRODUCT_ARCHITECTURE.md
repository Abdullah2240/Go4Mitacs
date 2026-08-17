# Mitacs Project Matcher and CV Alignment Studio

## Purpose

Build a private application-intelligence workspace that turns Sheikh Abdullah Bin Zahid's verified evidence into an explainable shortlist of Mitacs internships, then uses the selected projects to produce a stronger, evidence-grounded CV.

This is not a generic job-board chatbot. It has three connected outcomes:

1. Build a trustworthy knowledge base of the candidate.
2. Find, explain, compare, and rank the best Mitacs projects.
3. Align a base CV and project-specific variants to the chosen opportunities without fabricating experience.

## Current operating mode

The active product is local-only: public project browsing, deterministic
matching, candidate notes, and shortlist decisions work without registration,
Supabase Auth, a database password, or an AI key. Optional BYOK configuration
is held in browser sessionStorage and is never sent to this application or an
external provider. Supabase Auth, private tables, and cloud sync are archived
future infrastructure, not active product behavior. See
`13_LOCAL_FIRST_BYOK_AND_CLOUD_MODE.md` for the local-only privacy rules.

## Product principles

- Every recommendation must link back to source evidence.
- The system may improve wording, prioritization, and discoverability; it may not invent claims, results, skills, papers, or responsibilities.
- A user controls all ranking decisions. AI recommendations are suggestions, not automatic submissions.
- Historical selection information is a transparent research signal, not a guarantee or a hidden exclusion rule.
- The candidate's source material, API keys, and application strategy are private by default.

## End-to-end architecture

```text
Candidate evidence
  -> extraction and normalization
  -> candidate knowledge base

Mitacs projects and professor information
  -> extraction and normalization
  -> project knowledge base

Hybrid matching and evidence-based reranking
  -> candidate-project explanations
  -> active workspace of up to 15 projects

Final-ten strategy board
  -> ambitious / strong-fit / intelligence-backed portfolio mix
  -> side-by-side comparison and manual reranking

CV Alignment Studio
  -> detect unlisted but relevant evidence
  -> chat-led clarification and approval
  -> tailored base CV, project clusters, and final application variants
```

## System layers

### Layer 1: Candidate evidence base

Inputs include resumes, CV variants, certificates, internship and employment records, research notes, project documents, GitHub repositories, awards, leadership material, and uploaded files.

Each source is retained in its original form and split into searchable excerpts. The system also creates structured claims, for example:

- `Built an ETA model; 76% of evaluated predictions were within two minutes.`
- `Implemented a JWT/OIDC Ticketer data pipeline with pagination, retries, and SQLite deduplication.`
- `Contributed a merged refactor to PyPA pipx.`

Every claim stores a confidence state:

- Verified: supported by an uploaded source or explicit user confirmation.
- Needs confirmation: plausible but incomplete or conflicting.
- Excluded: outdated, sensitive, unsupported, or not appropriate for external use.

### Layer 2: Mitacs project and professor knowledge base

Each project should be normalized into:

- Project title and source URL
- University, department, city, and province
- Professor or supervisor
- Full description and source excerpts
- Discipline, research themes, methods, tools, and domain keywords
- Requirements, eligibility, deadlines, and constraints
- Relevant lab, publication, and professor context when available

Professor records should be separate from project records so one professor's research can inform multiple opportunities without duplicating it.

### Layer 3: Hybrid matching and reranking

The first pass finds plausible candidates using keyword retrieval, semantic/vector similarity, and hard filters such as discipline or eligibility. The second pass uses an AI reranker with an explicit rubric.

Suggested default weighting:

| Dimension | Weight | Question answered |
| --- | ---: | --- |
| Research and technical fit | 30% | Does the candidate's work match the project methods and themes? |
| Evidence strength | 20% | Is the claimed fit supported by substantial shipped, research, or academic evidence? |
| Methods and domain overlap | 15% | Are the tools, datasets, systems, or scientific problems adjacent? |
| Eligibility and practical fit | 15% | Does the candidate satisfy stated requirements and constraints? |
| Professor/lab relevance | 10% | Is there a grounded connection to the lab's work? |
| Candidate preference | 10% | Does the opportunity support the user's chosen direction? |

Scores must include an explanation with three fields:

- Evidence that supports the match
- Gaps or uncertainty
- Actions that could strengthen the application

### Layer 4: Active comparison workspace

The workspace begins with an active set of up to 15 projects. It is not merely a ranked table; it is a decision surface.

Required views:

- Ranked project list with score, confidence, and status
- Side-by-side comparison of two to four projects
- Evidence panel showing exactly why each project matched
- Filters for research area, university, professor, method, province, and strategy category
- Notes, pins, exclusions, and manual rank changes
- A shortlist board where cards can be dragged between strategy lanes

### Layer 5: Final-ten strategy board

The final shortlist has ten projects. The current preferred portfolio is configurable rather than treated as a promise of admission:

| Lane | Target | Meaning |
| --- | ---: | --- |
| Ambitious | 4 | Outstanding research opportunities where the match is compelling but competition is likely high. |
| Strong-fit | 4 | Projects with substantial verified alignment to skills, domain, methods, and evidence. |
| Intelligence-backed | 2 | Projects supported by the historical Pakistan-selection information the user will supply. |

The labels describe application strategy, not likelihood of success. A project can appear in more than one analytical category, but each final project occupies one selected lane so the ten remain balanced.

The UI must let the user change the mix. For example, a future session can use 5 ambitious / 3 strong-fit / 2 intelligence-backed without rebuilding the scores.

### Layer 6: CV Alignment Studio

This layer begins only after the user selects the final ten.

It answers a different question from matching: **"Given these projects, what truthful evidence should be visible in my CV?"**

Core capabilities:

- Read the selected projects as a set and extract recurring methods, domains, and vocabulary.
- Compare those requirements against the candidate knowledge base and the currently selected CV.
- Identify verified evidence that is absent from the CV, such as a relevant project detail, method, metric, course, certificate, or responsibility.
- Present each possible addition with its source excerpt and a plain-language reason it matters.
- Let the user clarify missing detail in chat before a claim becomes CV-ready.
- Generate a revised base CV plus tailored emphasis for each project or project cluster.
- Show a before/after diff and require approval before updating any final CV artifact.

The studio should prefer a small number of high-quality CV variants over ten radically different resumes:

- One research-focused base CV
- One or more cluster variants, such as AI/ML, systems/MLOps, and transport/geospatial
- A project-specific emphasis note for each final application

## Recommended technical architecture

The implementation should favor tools the candidate already understands:

| Concern | Recommended choice | Rationale |
| --- | --- | --- |
| User interface | Next.js + TypeScript | Strong interactive comparison and document UI. |
| Backend | FastAPI + Python | Natural fit for ingestion, ranking, document processing, and AI orchestration. |
| Primary database | Postgres + pgvector, preferably through Supabase | Stores structured records, vectors, status, notes, and authorization data together. |
| File storage | Private object storage | Keeps originals separate from extracted text and derived claims. |
| Retrieval | Hybrid lexical + vector search | Keywords catch exact technologies; vectors capture adjacent research language. |
| Reranking and chat | Provider-abstracted AI service | Keeps the application portable across AI providers and models. |
| Background work | Durable job queue | Supports extraction, embeddings, refreshes, and report generation without blocking the UI. |

Cloud provider keys must be server-side when cloud inference is enabled. The
local-first UI may accept a provider key for the current browser session, but
stores it only in sessionStorage, never logs it, and requires an explicit
future action before any candidate evidence is sent externally.

Detailed vectorization, retrieval, provider-routing, free-tier, and reference-app-visibility decisions are maintained in [AI.md](AI.md).

## Core entities

| Entity | Purpose |
| --- | --- |
| SourceDocument | Original file or web source, provenance, date, and access status. |
| EvidenceExcerpt | Searchable text span with source location. |
| CandidateClaim | Structured, source-linked assertion about skills, results, projects, or experience. |
| CandidateAsset | Project, certificate, role, award, course, research item, or portfolio link. |
| MitacsProject | Normalized project record and source content. |
| Professor | Supervisor/lab profile and source material. |
| HistoricalSelectionSignal | User-provided, sourced historical information about prior selections. |
| MatchRun | A reproducible matching session, settings, and corpus versions. |
| ProjectMatch | Score breakdown, evidence, gaps, recommendation, and confidence. |
| ShortlistItem | User-controlled rank, lane, notes, and final-selection state. |
| CVVariant | A versioned CV, its evidence ledger, and approval state. |
| ChatDecision | Clarification or approval that changes a claim or CV recommendation. |

## Guardrails

- Do not score from nationality or infer preferences from a professor's identity. Historical Pakistan-selection data remains an optional, visibly sourced signal selected by the user.
- Do not present projected work as shipped work. Planned Kubernetes deployment, for example, stays marked as planned.
- Do not disclose confidential client information, credentials, ticket contents, employee records, or private applicant data.
- Keep a claim ledger so the chat cannot silently make a CV stronger by becoming less true.
- Keep matching outputs reproducible: retain the corpus version, score weights, model version, and source evidence for every final-ten decision.
