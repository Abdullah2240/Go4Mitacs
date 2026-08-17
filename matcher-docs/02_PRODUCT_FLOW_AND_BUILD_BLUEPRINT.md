# Product Flow and Build Blueprint

## User journey

### 1. Build the personal evidence base

The user uploads or connects material, reviews extracted claims, and resolves any conflict. A profile view shows what the system knows, what is verified, and what is missing.

Output: an approved candidate knowledge base rather than a single static resume.

### 2. Load and inspect Mitacs opportunities

The system imports the project database from the sources the user provides. It validates URLs, normalizes fields, preserves raw descriptions, and flags incomplete records.

Output: a searchable project and professor corpus.

### 3. Run a match session

The user chooses a focus, such as AI/ML, systems, transport analytics, MLOps, HCI, or a broad exploration. The system returns a ranked set with evidence, gaps, and suggested next actions.

Output: an active set of up to 15 projects.

### 4. Compare and shape the shortlist

The user compares projects side by side, adjusts priorities, adds notes, and moves cards into strategy lanes. The final ten should be intentionally mixed across ambitious, strong-fit, and intelligence-backed opportunities.

Output: a user-approved ranked top ten and an evidence record for every decision.

### 5. Align the CV and portfolio evidence

The CV Alignment Studio reads the selected ten together, identifies recurring language and gaps, and recommends truthful additions or edits. The user can ask the chatbot questions such as:

- "Which verified experience of mine is most relevant to this project but absent from my CV?"
- "Show me all projects where Ticketer or transport analytics strengthens the match."
- "Rewrite this bullet for distributed systems research without overstating my role."
- "Which five skills recur most across my selected ten?"

Output: an approved base CV, tailored variants or emphasis notes, and an audit trail of every changed claim.

### 6. Prepare final application work

For each selected project, produce a concise research brief containing:

- Match explanation and supporting evidence
- Professor/lab context with sources
- Required follow-up research
- CV emphasis recommendations
- Portfolio links to include
- Questions or uncertainties to resolve before submission

## Required UI surfaces

### Dashboard

Shows corpus health, number of verified claims, imported projects, active shortlist count, and unresolved evidence gaps.

### Candidate Profile

Contains all evidence sources, claims, projects, skills, experience, certificates, research, and a verification queue.

### Project Explorer

Supports natural-language search, keyword filters, semantic discovery, and project cards that expose the matching rationale.

### Match Detail

Displays a score breakdown, evidence citations, missing requirements, professor context, related projects, and tailored suggestions.

### Compare View

Presents two to four projects side by side with consistent comparison rows: research problem, methods, required skills, evidence from the candidate, gaps, professor/lab, strategy lane, and rank.

### Final-Ten Strategy Board

Provides the visual shortlist UI requested for the final selection. It should include draggable project cards, lane counts, ranking controls, confidence indicators, notes, and a clear finalization action.

### CV Alignment Studio

Shows the current CV next to recommended additions and deletions. Each suggestion must display:

- The candidate evidence that supports it
- The selected projects that make it relevant
- The proposed wording
- The change in keyword or method coverage
- An accept, edit, reject, or ask-chat action

## Matching output contract

Each project match should return a structured result, not only prose:

| Field | Description |
| --- | --- |
| Overall score | Weighted score used for ordering, always shown with its rubric. |
| Confidence | High, medium, or low based on source completeness and evidence quality. |
| Evidence matches | Candidate excerpts that connect directly to the opportunity. |
| Keyword and method overlap | Exact and semantic overlap, kept separate for clarity. |
| Gaps | Missing or weakly evidenced requirements. |
| Suggested positioning | Truthful phrasing and portfolio emphasis. |
| Strategic category | Ambitious, strong-fit, intelligence-backed, or user-defined. |
| User decision | Active, pinned, excluded, final-ten, or submitted. |

## CV alignment rules

1. Reuse verified evidence before asking the user for new information.
2. If a relevant experience is known but under-documented, ask focused chat questions and save the answer as a new claim only after confirmation.
3. Do not add a tool or method because a Mitacs project asks for it unless the candidate actually used it.
4. Prefer outcome, method, and evidence over keyword stuffing.
5. Maintain a core CV and create tailored variants only when the project cluster materially changes emphasis.
6. Keep a source-linked diff for every revision, including what changed and why.

## Implementation phases for the later build

### Phase A: Foundation

- Set up the database, file storage, source provenance, and user authentication.
- Create candidate-document ingestion and claim verification.
- Import a small representative sample of Mitacs projects before importing the full corpus.

### Phase B: Matching MVP

- Build project normalization, hybrid retrieval, filters, score rubric, and evidence-backed match detail.
- Validate outputs against a manually reviewed set of projects.

### Phase C: Decision workspace

- Build the active-15 list, compare view, notes, manual reranking, and final-ten board.
- Add the configurable 4 / 4 / 2 strategy preset.

### Phase D: CV Alignment Studio

- Build selected-ten keyword/method analysis, evidence-gap discovery, chat clarification, and CV diff/approval.
- Produce a base CV and cluster-specific variants from approved claims.

### Phase E: Professor and historical-signal intelligence

- Import user-provided professor and historic-selection sources.
- Display provenance, confidence, and limitations beside every signal.
- Make the signal optional and visible in ranking settings.

### Phase F: Quality and safety

- Add source citation checks, hallucination tests, prompt-injection handling for imported web content, private-data controls, and evaluation datasets.
- Run human review on all final-ten recommendations before relying on them.

## Inputs needed before implementation

- Project-database links, exports, or scraping permissions.
- The historic Pakistan-selection list and its source/provenance.
- A representative set of personal certificates, research materials, and project evidence not already in the resume workspace.
- The target AI provider and how its key will be supplied through environment configuration.
- The desired deployment model: local/private prototype, private cloud workspace, or a polished hosted tool.
- Any Mitacs application constraints, deadlines, and eligibility rules to encode as hard filters.

## Success criteria

The tool is ready for real use when it can:

1. Trace every important candidate claim and project fact to a source.
2. Return a reasoned, adjustable shortlist from the imported Mitacs corpus.
3. Let the user compare, rank, and finalize ten projects visually.
4. Explain why each selected project belongs in the portfolio and what remains uncertain.
5. Produce CV recommendations that are both more relevant and fully defensible.
6. Preserve a complete decision and revision history for later review.

