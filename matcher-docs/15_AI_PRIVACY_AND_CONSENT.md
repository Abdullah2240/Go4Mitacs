# AI privacy and consent

AI is disabled until the user starts a request, reviews the exact sources, and confirms sending. The review lists included and excluded sources, character and token estimates, provider, and model.

Protected documents are excluded by default and require a separate checkbox. Keys are saved only in `sessionStorage`, never placed in URLs or localStorage, and removed by Forget Key. Saving a key makes no provider call.

Evidence is truncated deterministically, labelled with source IDs, and placed inside untrusted evidence delimiters. Provider output is treated as data only after runtime validation. Deterministic matching remains the fallback for missing keys, consent denial, offline use, provider failures, timeouts, and malformed responses.
