# corpus/

SafetyLM's knowledge base — the AU/NZ WHS source documents the RAG system retrieves from.

| Subdir | Contents | In git? |
|---|---|---|
| `manifest/` | `corpus_manifest.csv` + `.xlsx` — the master catalogue, one row per source document with full metadata. **The source of truth.** | ✅ committed |
| `raw/` | Downloaded source documents (PDF/HTML/DOCX) | ❌ gitignored — too large; reproduced via `scripts/download_corpus.py` |
| `processed/` | Cleaned, chunked text with metadata, ready for embedding | ❌ gitignored — reproduced via the extraction + chunking scripts |

**Reproducibility:** the manifest is all that's committed. Anyone can run the download and
processing scripts against it to rebuild `raw/` and `processed/` locally.

Scope, the metadata schema, source tiers, and the chunking strategy are defined in
`docs/03-corpus-strategy.md`. Built in **Phase 1** (`docs/06-phased-roadmap.md`).
