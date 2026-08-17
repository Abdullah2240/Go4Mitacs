# AI, Retrieval, and Provider-Routing Architecture

## Decision summary

The matcher will index the full Mitacs corpus, not a preselected subset. The AI system has four distinct jobs:

1. Convert candidate evidence and Mitacs project material into structured, source-linked records.
2. Retrieve relevant projects from the complete corpus using hybrid search.
3. Rerank and explain only a manageable candidate set with an LLM.
4. Help the user improve their CV using verified evidence after the final ten are selected.

The system must not depend on free LLM requests for bulk indexing. Bulk vectorization should be local or otherwise inexpensive and deterministic; LLM usage should be reserved for high-value tasks such as extraction review, reranking, comparison, chat, and CV wording.

## Corpus design

### Candidate corpus

Store original sources and build three representations:

- **Source excerpts**: small, searchable passages from resumes, certificates, project notes, research material, and supporting files.
- **Evidence claims**: structured, source-linked statements about skills, methods, outcomes, responsibilities, and eligibility.
- **Candidate assets**: projects, roles, certificates, awards, courses, research items, and portfolio links.

No raw claim becomes externally usable until it is either source-backed or explicitly confirmed by the user.

### Mitacs corpus

Import all available project records, not only a discovered shortlist. Each project should have:

- Raw source text and URL
- A normalized project card: title, university, professor, discipline, eligibility, research problem, methods, tools, and constraints
- Semantic chunks from the detailed description
- Exact keyword fields for tools, domains, and methods
- A corpus version and import timestamp

Professor and lab material remains linked but separate, allowing the same professor to enrich multiple project records.

## Vectorization strategy

### What is embedded

Embed both:

- Candidate evidence excerpts and compact claim/asset cards
- Project cards and detailed project-description chunks

Do not embed whole PDFs or entire project pages as one vector. Large documents dilute important signals and make explanations weak.

### Chunking rules

| Source | Primary unit | Target size | Required metadata |
| --- | --- | ---: | --- |
| Resume / CV | Bullet or grouped experience block | 100-300 words | role, dates, skill tags, source location |
| Project evidence | Problem, implementation, result block | 150-400 words | project, domain, methods, metrics, source URL |
| Certificate / course | Credential or course record | 50-150 words | issuer, date, skills, verification state |
| Mitacs project | Project card plus description chunks | 150-450 words | project ID, professor, university, field, requirements |
| Professor profile | Research theme or publication block | 100-300 words | professor ID, lab, source URL |

Each chunk should overlap lightly only when a sentence would otherwise lose context. Metadata matters as much as embeddings because filtering and explanations depend on it.

### Embedding provider

Use a local embedding model for the default build. This avoids spending free LLM quota on thousands of records and lets the full corpus be reindexed whenever the source dataset changes.

The implementation should expose an embedding-provider interface so a hosted embedding API can be added later, but local embeddings are the baseline. The vector store should retain an `embedding_model`, `embedding_version`, and `embedded_at` field for every vector.

## Retrieval pipeline

```text
Full Mitacs corpus
  -> hard filters: eligibility, discipline, user exclusions
  -> lexical search: exact methods, tools, acronyms, university/professor terms
  -> vector search: semantic research and systems adjacency
  -> reciprocal-rank fusion / hybrid merge
  -> top 50-100 candidate projects
  -> LLM reranking of the strongest candidates
  -> active workspace of up to 15
  -> user-controlled final ten
```

Lexical retrieval is essential for exact terms such as `OSRM`, `NATS JetStream`, `OIDC/JWT`, `MLflow`, and `Flutter`. Vector retrieval is essential for adjacent phrasing, such as linking transport telemetry work to mobility analytics even when the terminology differs.

The LLM must never be asked to compare all 3,000 projects at once. It reranks a short, retrieved candidate set and returns structured evidence, gaps, and positioning suggestions.

## Matching and reranking output

For each candidate-project pair, the reranker returns:

- Overall score and score breakdown
- Verified candidate evidence that supports the match
- Project requirements that are met, adjacent, unknown, or missing
- Research-method overlap
- Risks, gaps, and questions for the user
- Suggested, truthful CV emphasis
- Source references for every important assertion

Structured output is required. Free-form prose alone cannot power a trustworthy compare view, strategy board, or CV diff.

## Reference-app visibility and competition signals

### Verified observation

On 17 August 2026, the reference app at `https://mitacs-matcher.vercel.app/app` visibly offered the following **Projects read** options: Top 30, Top 60, Top 120, and Top 240. Its visible default was Top 60.

This establishes a visible maximum of 240 projects per run in that interface. It does **not** establish:

- Whether the capped projects are static or profile-dependent
- Whether they are selected by a particular ranking algorithm
- How many users see or apply to them
- Any intent by the app author to withhold opportunities

### How our product should use the signal

Do not label a project "overused" merely because a third-party app may expose it. Instead, store an optional `reference_app_visibility` record:

- `unknown`: not checked
- `observed_in_reference_pool`: supported by an observed project list
- `not_observed`: not present in a supplied/observed list
- `unverified`: a user report exists but no source list has been imported

Use it only as a transparent exploration or tie-breaker signal, never as a primary fit score. A strong project should not be downgraded because of an unverified assumption about competition.

If a sourced list of reference-app projects becomes available, the system can calculate corpus coverage and surface a **discovery diversity** indicator. This can encourage exploration outside the visible subset while preserving match quality.

## AI provider and key architecture

### Provider roles

| Task | Default approach | Why |
| --- | --- | --- |
| Embeddings | Local model | Reliable full-corpus indexing without API quota dependence |
| Lexical retrieval | Postgres full-text search | Exact skills, acronyms, and filters |
| Initial ranking | Deterministic hybrid scoring | Cheap, reproducible, works on all 3,000+ projects |
| Reranking | LLM, structured output | Better reasoning over candidate evidence and project requirements |
| Chat and CV drafting | LLM with retrieval citations | Helpful writing without unsupported claims |
| High-stakes final review | User approval plus source ledger | No model should make the final application decision |

### Supported keys

The app can support these optional server-side providers:

- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- `HF_TOKEN`

Keys must be encrypted at rest when persisted, available only to the backend, masked in the UI, and never committed to source control. A user may choose one provider, enable multiple providers, or disable cloud inference for private material.

### Provider routing policy

The router should select a provider by task, capability, privacy setting, cost, health, and recent success rate. It should not simply rotate keys after every error.

| Condition | Action |
| --- | --- |
| 429 / rate limit | Exponential backoff; then route to an enabled compatible fallback. |
| Network timeout | Retry once with a short timeout; then use an enabled fallback. |
| 5xx provider failure | Use an enabled compatible fallback and record the incident. |
| 400 invalid request | Do not blindly fail over. Validate the request/schema/model capability first. |
| 401 / 403 authentication or permission error | Disable that provider for the session and show a key/configuration error. |
| Safety refusal | Preserve the response and ask the user to reframe or remove sensitive material; do not silently route private content elsewhere. |
| Low-quality structured output | Retry with a stricter schema; if still invalid, route to a compatible fallback. |

Before sending sensitive candidate documents to a second provider, the UI must require explicit opt-in to multi-provider fallback. A fallback changes which third party receives the user's information.

## Is a free-key-only plan enough?

It is enough for a personal prototype if the architecture avoids expensive LLM calls during indexing. It is not a dependable long-term production strategy.

- OpenRouter's free tier currently lists a 50-request-per-day limit; its own documentation says free models have low limits and are not generally suitable for production. [OpenRouter pricing](https://openrouter.ai/pricing) and [free-model guidance](https://openrouter.ai/docs/cookbook/get-started/free-models-router-playground)
- Hugging Face currently lists $0.10 monthly Inference Providers credit for free users, which is useful for testing but not a broad reranking workload. [Hugging Face pricing](https://huggingface.co/docs/inference-providers/en/pricing)
- Gemini quotas are account- and tier-dependent and can change; the active limits should be read from Google AI Studio rather than hard-coded into the app. [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

Recommended approach:

1. Keep embeddings and first-pass retrieval local.
2. Cache every LLM extraction, project summary, rerank, and chat result by corpus version and prompt version.
3. Call an LLM only for the top 50-100 retrieved projects, then only refresh results when source data or user preferences change.
4. Use one selected primary provider for normal work and opt-in fallbacks for transient failures.
5. Add a small paid-credit buffer only when the tool becomes a daily workflow; do not design the system around unlimited free calls.

## AI safety and evaluation

### Prompt-injection defense

Imported project pages and uploaded documents are untrusted data. The ingestion pipeline must treat them as content, never as instructions. Their text may be summarized or indexed, but it cannot alter system prompts, routing rules, data sharing, or tool permissions.

### Evaluation set

Before relying on ranks, create a small manually judged benchmark:

- 30-50 diverse Mitacs projects
- Human labels for strong fit, plausible fit, weak fit, and non-fit
- Expected evidence citations and known gaps
- Tests for keyword-only false positives and hallucinated candidate claims

Track retrieval recall at 15, reranker agreement with manual judgement, citation completeness, and unsupported-claim rate.

## Build order for the later implementation

1. Local embeddings, Postgres/pgvector, lexical retrieval, and the full project import.
2. Candidate evidence ingestion and a source-linked claim ledger.
3. Hybrid search and a transparent top-15 result list.
4. LLM reranking with one provider and result caching.
5. Active comparison workspace and final-ten strategy board.
6. CV Alignment Studio with chat clarification, source-backed suggestions, and approval diffs.
7. Opt-in multi-provider routing, professor intelligence, and reference-app diversity signals.

