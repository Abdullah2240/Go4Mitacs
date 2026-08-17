# Mitacs Matcher - UI Design Specification

## Active flow update

The primary flow is `Add evidence -> Review knowledge base -> Build profile ->
Review profile -> Run full-corpus match`. Documents expose name, type,
character count, parse status, duplicate state, and errors. Provider actions
are separate and always show a consent modal naming provider/model and the exact
data categories leaving the browser.

## Status

The previous architecture defined the required UI surfaces, but visual UI work was not complete. This document turns those surfaces into an implementable visual system and interaction contract.

## Default entry flow

The first screen is a local-first welcome state, not a login wall. It offers
public project search, local candidate-evidence input, deterministic matching,
and a browser-session BYOK setup for OpenRouter, Gemini, or Hugging Face. A
visible warning explains that browser-held keys are inspectable by the browser
owner, and a `Forget key` action clears the selected session key.

There is no cloud-sync, login, or registration control in the active UI.
Supabase Auth and owner-scoped private-data controls are archived future
infrastructure and are not initialized by the frontend.

## Design read

Private research-decision workspace for a technical applicant, with a trust-first, evidence-led language and a calm analytical product system.

Design dials:

- `DESIGN_VARIANCE: 3` - consistent alignment and predictable navigation
- `MOTION_INTENSITY: 2` - restrained transitions used for feedback and state change
- `VISUAL_DENSITY: 6` - information-rich comparison without cockpit clutter

This is a product workspace, not a marketing landing page. Use the product-system rules below rather than decorative landing-page patterns.

## Design system decision

Use one accessible component foundation: **Radix Themes** with owned application components around it. Use TanStack Table for large tabular views if needed, but do not mix Fluent, Material, Carbon, or multiple visual component systems.

The visual system is intentionally quiet:

- Base: cool white and soft blue-grey surfaces.
- Primary text: deep navy ink.
- Single brand accent: Mitacs-like cobalt blue, provisional until a supplied brand token is confirmed.
- Semantic colors: reserved for match status, warnings, errors, and verified evidence only.
- No AI-purple gradients, decorative glass, excessive rounded cards, or ornamental dashboards.

Provisional tokens:

```text
ink             #10243E
muted           #5C6B7A
surface         #F6F8FB
surfaceRaised   #FFFFFF
line            #DCE4EC
accent          #1769AA
accentSoft      #E8F2FA
success         #18805C
warning         #B26A00
danger          #B42318
radiusPanel     12px
radiusControl   8px
radiusPill      999px (status only)
```

Typography should use a readable sans-serif with a strong text hierarchy. Use a display size only for the workspace title; project titles and evidence content should remain compact and scannable.

## Global shell

Desktop layout:

```text
┌──────────────────────────────────────────────────────────────┐
│ workspace switcher   search / command bar       profile      │
├───────────────┬──────────────────────────────────────────────┤
│ Overview      │ page title + corpus/version context           │
│ Candidate     │                                                │
│ Projects      │ main workspace                                │
│ Match runs    │                                                │
│ Compare       │                                                │
│ Strategy      │                                                │
│ CV Studio     │                                                │
│ Sources       │                                                │
└───────────────┴──────────────────────────────────────────────┘
```

Rules:

- Left navigation stays stable; active item uses a clear accent rail and text contrast, not a floating decorative pill.
- Every project-facing page displays corpus version and retrieval date somewhere discoverable.
- The command/search bar searches projects, candidate evidence, and saved decisions but never submits an application.
- Destructive actions require confirmation; archive/delete actions are visually distinct from ranking actions.

Mobile layout:

- Collapse navigation into a labelled menu.
- Convert compare columns into a swipeable or stacked sequence with a persistent project selector.
- Keep primary actions reachable at the bottom of the viewport without covering evidence.
- Never rely on hover to reveal source or score explanations.

## Screen contracts

### 1. Overview

Purpose: orient the user after opening the app.

Show:

- Candidate evidence completeness, with a source count rather than an unexplained percentage.
- Current corpus count, corpus retrieval date, and last successful import.
- Latest match run and its model/embedding version.
- Active shortlist summary: top 15 and final-ten lane counts.
- Open review tasks: claims needing approval, missing evidence, and stale project records.

Empty state: explain how to upload the first CV or import the public project corpus.

### 2. Candidate evidence

Purpose: build and verify the personal knowledge base.

Show:

- Source documents grouped by CV, certificates, work, research, and portfolio evidence.
- Extracted claims with source locations and verification state.
- A side panel for the selected excerpt.

Interaction rule: a claim can be edited, approved, rejected, or marked uncertain. The UI must show what source supports it.

### 3. Project explorer

Purpose: search the complete catalogue before matching.

Show:

- Search and exact filters: keyword, language, province, university, campus, professor, start date, flexible start date, and academic background.
- Result count and corpus snapshot.
- Compact rows with ID, title, professor, institution, location, language, start date, and a short relevance preview.

Use a table/list hybrid for scanability. Avoid a wall of equal cards.

### 4. Match run

Purpose: generate a reproducible ranked set.

Show:

- Candidate profile version and corpus snapshot.
- Retrieval settings and optional hard filters.
- Progress states for lexical retrieval, vector retrieval, and reranking.
- Ranked results with score components, confidence, evidence count, and gaps.

The user must be able to inspect the run configuration after completion.

### 5. Match detail

Purpose: explain one recommendation.

Structure:

```text
project identity + save/compare actions
fit summary       evidence for fit       gaps / risks
project facts     candidate evidence    source citations
```

Every important recommendation must have an expandable “Why this was scored” section. Keep evidence and project requirements visibly distinct.

### 6. Compare view

Purpose: compare two to five projects side by side.

Rows:

- Research domain and methods
- Required skills and candidate evidence
- Supervisor/institution
- Start timing and flexibility
- Location and language
- Fit strengths
- Evidence gaps
- Ambition/feasibility lane
- User notes and rank

On small screens, use a project picker and stacked sections. Do not shrink five columns until text becomes unreadable.

### 7. Strategy board

Purpose: make the final choice deliberate.

Use three explicit lanes:

- Strong fit
- Ambitious fit
- Intelligence-backed / experimental

The default board may suggest 4 / 4 / 2, but the user owns the counts. Dragging or rank changes must create an auditable decision event. Model suggestions never silently reorder the board.

### 8. CV Alignment Studio

Purpose: align the approved CV with the chosen project set without exaggeration.

Use a three-pane layout:

```text
selected projects | evidence and gaps | proposed CV diff
```

Every proposed bullet displays:

- source claim(s)
- projects it supports
- whether it is existing wording, a rewrite, or a newly requested fact
- approval state

The export action is disabled while unapproved claims remain in the draft.

## State design

Every major screen must implement:

- Loading: layout-shaped skeletons, not a generic spinner.
- Empty: explain what action populates the screen.
- Error: preserve the user’s inputs and show retry plus diagnostic context.
- Stale: show when corpus or evidence versions have changed.
- Permission: explain why a private source is unavailable without revealing its contents.
- Success: confirm the saved artifact or run ID.

## Evidence and provenance presentation

- Use a compact source badge with document name and page/section when available.
- Source links open an evidence drawer, not a new uncontrolled navigation path.
- Confidence is always accompanied by an explanation; never show a bare percentage as truth.
- Distinguish `verified`, `proposed`, `uncertain`, and `rejected` claims with text labels and accessible color support.
- Display `planned`, `prototype`, `tested`, and `production` work states explicitly in CV alignment.

## Motion and accessibility

- Motion is limited to page transitions, drawer expansion, drag feedback, and saved-state confirmation.
- Respect `prefers-reduced-motion` and provide an equally understandable static state.
- Keyboard navigation must cover filters, project rows, compare selection, evidence drawers, and board movement.
- Focus rings must be visible on the chosen surface and pass contrast checks.
- Do not encode fit or risk using color alone.
- Target WCAG AA contrast and readable table density at 200% zoom.

## Component inventory for implementation

Build these reusable primitives before composing pages:

- `AppShell`
- `PageHeader`
- `CorpusStatus`
- `EvidenceStatusBadge`
- `SourceCitation`
- `FilterBar`
- `ProjectRow`
- `ProjectMetadataStrip`
- `ScoreBreakdown`
- `EvidenceDrawer`
- `CompareGrid`
- `StrategyLane`
- `ClaimDiff`
- `AsyncState`
- `ConfirmActionDialog`

Each component should have loading, empty, error, keyboard, and mobile behavior documented alongside its implementation.

## Visual completion status

The visual direction and screen contracts are now consolidated. The visual UI is **not yet coded or visually verified**. Implementation still needs:

1. A low-fidelity shell and typography/token pass.
2. A clickable explorer/detail/compare prototype using the ten-record sample.
3. Review and approval of the visual direction.
4. Migration from sample data to the full database-backed corpus.

This is the correct point to begin implementation, not to claim that the interface is finished.
