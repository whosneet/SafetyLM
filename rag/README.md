# rag/

The query-time RAG pipeline — the operational core of SafetyLM. Takes a natural-language
query and returns a grounded, cited WHS answer.

**Planned (Phases 3 & 5):**

- `pipeline.py` — LlamaIndex orchestration: jurisdiction detection → embed query → hybrid
  search (semantic + BM25) over Qdrant with jurisdiction metadata filter → assemble context
  → call Llama 3.1 8B via Ollama → format answer + SOURCES block
- `prompts/` — system prompt template(s); the system prompt is the most-iterated artefact
  (draft v0.1 lives in `docs/04-rag-pipeline.md`)
- `query.py` — CLI entry point (query in, response out) — built first, used for benchmarking
- `app.py` — Chainlit chat UI for the public demo (Phase 5)

Design & retrieval decisions: `docs/04-rag-pipeline.md`. How LlamaIndex orchestrates the
steps and why prompt construction is engineering: `docs/learning/concepts.md` (Phase 3).
