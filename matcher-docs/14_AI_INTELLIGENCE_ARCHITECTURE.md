# AI intelligence architecture

Go4Mitacs keeps deterministic full-corpus matching as the source of truth. The browser may optionally send explicitly selected evidence and a bounded candidate pool to a provider selected by the user.

The adapter in `web/lib/ai/providers.ts` supports OpenRouter, Gemini, and Hugging Face. It normalizes responses, applies timeouts, classifies failures, and never logs request content or keys. Runtime validators reject malformed JSON and project IDs outside the reviewed candidate pool.

The local semantic baseline uses fixed 256-dimensional hashed-token vectors and cosine similarity. It is explainable, deterministic, and available offline. Public project text is bundled; candidate evidence remains browser-local. AI reranking never sends all 3,359 projects to a chat model. A vector database is deferred until local quality or load measurements justify one.

`web/lib/ai/embeddings.ts` defines the provider-independent `EmbeddingProvider` contract for candidate, project, and batch embeddings. The active implementation is local only; provider-backed embeddings are deliberately not enabled until a benchmark demonstrates a meaningful retrieval gain.
