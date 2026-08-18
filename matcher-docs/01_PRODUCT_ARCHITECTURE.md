# Go4Mitacs product architecture

Go4Mitacs is one Next.js application deployed to Vercel. The browser hosts the
workspace UI and same-origin route handlers. A bundled public project index
supports project search, detail views, filters, and deterministic matching.

Documents, profile, results, settings, protected document context, shortlist
items, and comparisons stay in browser storage. No candidate document is sent
to a route handler. Provider keys are session-only and external reranking is
not currently implemented.

The Python folder contains corpus maintenance and validation utilities. It is
not part of the deployed user workflow.
