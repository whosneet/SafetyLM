# embeddings/

The embedding pipeline — converts the processed corpus into vectors and loads them into the
Qdrant vector store. This is the **indexing** half of the RAG system (runs once, then on
corpus updates).

**Planned (Phase 2):**

- `embed_corpus.py` — embed each processed chunk with `nomic-embed-text` (via Ollama) and
  upsert into Qdrant with its metadata, indexed for filtered retrieval

**Stack:** `nomic-embed-text` (768-dim, local via Ollama) → Qdrant (local Docker).
Why these choices: `docs/04-rag-pipeline.md`. What embeddings physically are:
`docs/learning/concepts.md` (Phase 2 concepts).
