# scripts/

Utility scripts that build the corpus. Each script carries a docstring stating what it does
and what input it expects (see CLAUDE.md §2).

**Planned (Phase 1):**

- `download_corpus.py` — download source documents listed in the manifest into `corpus/raw/`
- `extract_text.py` — extract clean text from PDF/HTML/DOCX (handles columns, headers/footers,
  hyphenation — see `docs/learning/concepts.md` on why PDF extraction is messy)
- `chunk_corpus.py` — split cleaned text into 512-token chunks (64-token overlap) and attach
  metadata, writing to `corpus/processed/`

Design: `docs/03-corpus-strategy.md` (chunking) and `docs/04-rag-pipeline.md` (indexing pipeline).
