# CLAUDE.md — SafetyLM Project Memory

This file is auto-loaded at the start of every Claude Code session in this repo. It is the
**single source of truth** for project context and replaces the former `SESSION-PRIMER.md`.
Keep it current: update **§6 Current status** at the end of each working session. For deep
detail on any decision, follow the pointers in [§8 Reference docs](#8-reference-docs).

---

## 1. Identity

- **Name:** SafetyLM
- **What:** Open-source, RAG-powered AI reasoning system for Work Health & Safety (WHS)
  practitioners across **Australia and New Zealand**. Grounded in primary AU/NZ WHS
  legislation, regulations, codes of practice, and safety science — *not* a general
  chatbot with a safety prompt.
- **Owner:** Avneet (Neet) Singh — WHS practitioner (COHSProf). Domain expert; building
  AI/Python engineering skills through this project.
- **Approach:** RAG for v1. Fine-tuning is explicitly **v2** (out of scope now).
- **Status:** Phase 0 (planning) complete → moving into Phase 1 (corpus build).
- **GitHub:** TBD (not yet pushed) · **Hugging Face:** TBD · **Domain:** safetylm.com (planned)

---

## 2. How to work on this project (working agreement)

**Teach as we build.** The owner is a senior WHS domain expert but newer to AI/Python
engineering. When working:

- Explain *why* a technical decision is made and its tradeoffs — briefly, in plain language —
  not just *what*. The `docs/learning/concepts.md` companion is part of the project's DNA;
  keep that spirit in code comments and explanations.
- Surface choices rather than silently picking. Name the recommended option and the reason.
- Prefer simple, readable, well-commented code. Every script carries a docstring stating
  what it does and what input it expects.

**Domain-accuracy rules — non-negotiable (this is a safety-critical domain):**

- **Never fabricate** a legislative citation, section/regulation number, document title, or
  URL. If something is unverified, mark it `VERIFY` and flag it — do not guess.
- **Jurisdiction precision is first-class.** AU = federal (model WHS) + NSW, VIC, QLD, SA,
  WA, TAS, NT, ACT; plus NZ. Never conflate jurisdictions. **WA is not harmonised**
  (OSH Act 1984, not the model WHS framework) — always flag it.
- **Never assert legislative currency as fact.** Always direct the user to verify against the
  regulator's live publication.
- Every grounded answer traces to a source document. If retrieval finds nothing, say so —
  do not confabulate a plausible-sounding answer.

**Process guardrails:**

- Do **not** add Python dependencies not in `requirements.txt` without flagging first.
- Do **not** create files/directories outside the structure in §5 without flagging.
- Do **not** download or process corpus documents unless this is a corpus-build session.
- Treat every file as self-documenting — assume a contributor reads it cold.

---

## 3. Locked architecture decisions (v1)

| Decision | Choice |
|---|---|
| Approach | RAG only (no fine-tuning in v1) |
| Base model | Llama 3.1 8B Instruct @ Q8_0 (primary); Mistral 7B Instruct v0.3 (comparison) |
| Model runtime | Ollama (Metal acceleration on Apple Silicon) |
| Embedding model | `nomic-embed-text` via Ollama (768-dim) |
| Vector store | Qdrant (local Docker instance) |
| RAG orchestration | LlamaIndex |
| Chunking | 512 tokens, 64-token overlap, structure-aware |
| Retrieval | Hybrid (semantic + BM25), top-6, jurisdiction metadata filter |
| Interface | CLI first, then Chainlit for the demo |
| Hardware | MacBook Pro M3 Max, 64GB unified memory |

> ⚠️ **Currency note:** these picks were made in 2024. The base model is a *pluggable*
> component and the final choice is deferred to benchmark data (Phase 4). Revisit the
> local-model landscape at Phase 2/3 — newer open models may outperform Llama 3.1 8B.
> Do not treat the 2024 pick as fixed.

---

## 4. Locked corpus decisions

- **Jurisdictions:** AU (federal + all states/territories) + NZ.
- **Tier 1 (must-have for v1):** Model WHS Act + Regulations, all AU codes of practice, all
  NZ approved codes, AIHS BoK chapters, and each jurisdiction's Act / Regs / codes.
- **WA flag:** every WA document tagged `pre_harmonisation: true`.
- **`source_id` format:** `[JURISDICTION]-[CATEGORY]-[SEQUENCE]` — e.g. `FED-COP-001`,
  `NSW-LEG-001`, `NZ-REG-003`.
- **Metadata schema:** full field list in `docs/03-corpus-strategy.md`.
- The manifest (`corpus/manifest/`) is the only corpus artefact committed to git. `raw/` and
  `processed/` are gitignored and reproduced locally via scripts.

---

## 5. Repository structure

```
SafetyLM/
├── README.md              # Public project front page
├── CLAUDE.md              # ← this file (project memory, auto-loaded)
├── LICENSE                # Apache 2.0 (code)
├── DATA-LICENSE.md        # CC BY 4.0 (benchmark dataset + docs)
├── requirements.txt       # Python deps (stub — finalised in Phase 1)
├── docs/                  # Architecture & planning docs (00–08)
│   └── learning/          # concepts.md — learning companion
├── corpus/
│   ├── manifest/          # corpus_manifest.csv + .xlsx (committed)
│   ├── raw/               # downloaded sources (gitignored)
│   └── processed/         # chunked text + metadata (gitignored)
├── embeddings/            # embedding pipeline
├── rag/                   # RAG pipeline, prompt templates, CLI, Chainlit app
├── eval/                  # benchmark dataset + evaluation scripts
└── scripts/               # download, extraction, chunking utilities
```

---

## 6. Roadmap & current status

**Phases are sequential.** Advance only when the acceptance criteria in
`docs/06-phased-roadmap.md` are met.

0. Planning & documentation — ✅ done
1. **Corpus build** — manifest (≥150 docs) → download → extract → chunk ← **NEXT**
2. Embedding & vector store — Qdrant index + retrieval validation
3. RAG pipeline & system prompt — end-to-end query → cited answer
4. Benchmark evaluation — 500-Q dataset, RAGAS scoring, baselines
5. Interface & public launch — Chainlit, install docs, GitHub public
6. v2 planning — fine-tuning, LoRA (future)

<!-- Update the three lines below at the end of each working session. -->
- **Current phase:** Phase 0 → Phase 1 transition
- **Last completed:** Phase 0 admin setup — repo scaffolded, `git init`, this CLAUDE.md authored
- **Next session goal:** Begin Phase 1 — build the corpus manifest

---

## 7. Conventions

- **Python tooling:** *undecided — to be chosen in Phase 1* (candidates: uv / pip+venv /
  conda). Do not assume one until it is recorded here.
- **Licensing:** Apache 2.0 for code; CC BY 4.0 for the benchmark dataset and docs; the
  Llama 3 Community Licence passes through to users (they pull weights from Meta via Ollama).
- **Versioning:** semantic `vMAJOR.MINOR.PATCH`. The corpus is versioned separately from
  code — a corpus-only update is a MINOR bump with a changelog entry.
- **Scripts:** docstring + explicit input/output contract; no fabricated URLs/titles
  (mark `VERIFY`).
- **git / commits:** make commits only when the owner asks. If on `main`, branch first.

---

## 8. Reference docs

| Topic | File |
|---|---|
| Vision, users, success criteria | `docs/00-vision.md` |
| System architecture & data flow | `docs/01-architecture.md` |
| Base model selection rationale | `docs/02-model-selection.md` |
| Corpus scope & metadata schema | `docs/03-corpus-strategy.md` |
| RAG pipeline & system prompt | `docs/04-rag-pipeline.md` |
| Evaluation & benchmark design | `docs/05-evaluation.md` |
| Phased roadmap & acceptance criteria | `docs/06-phased-roadmap.md` |
| Distribution & launch | `docs/07-distribution.md` |
| Governance, licensing, liability | `docs/08-governance.md` |
| Concept explainers (learning) | `docs/learning/concepts.md` |

---

## 9. Out of scope for v1 (v2 parking lot)

Fine-tuning / LoRA adapters · synthetic training data from v1 outputs · multi-turn
conversation · public API endpoint · non-AU/NZ jurisdictions · Tier 3 corpus (court
decisions, coroner findings) beyond stretch goals. Record emerging v2 ideas in
`docs/06-phased-roadmap.md` (Phase 6).
