# Semantic matching evaluation

The current baseline is local hashed-token retrieval combined with the existing keyword score. Its vector length is 256; cosine similarity is combined with keyword overlap, discipline fit, and evidence coverage. This is a transparent baseline, not a claim of neural semantic understanding.

Evaluation fixtures cover strong, partial, weak, misleading-keyword, and missing-evidence cases in the frontend unit suite. Future provider comparisons should report precision@10, false-positive rate, unsupported-claim rate, malformed-response rate, latency, approximate cost, bundle impact, and browser storage impact. Provider calls are not made during automated tests.

The checked-in fixture set currently contains five manually labelled examples. The local baseline computes metrics in `web/lib/ai/evaluation.ts`; the current fixture run is a small regression signal, not a statistically meaningful benchmark. Provider reranking metrics remain unmeasured until a user manually runs the consented smoke-test with a real key. No provider key, response, or private evidence is stored by the evaluation suite.

A vector database is deferred because the public corpus is static and bundled while private candidate material must remain local. Reconsider only if measured local ranking quality or load time is insufficient.
