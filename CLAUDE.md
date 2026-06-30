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
  WA, TAS, NT, ACT; plus NZ. Never conflate jurisdictions. **Victoria is the sole
  non-harmonised jurisdiction** (OHS Act 2004) — always flag it. (WA harmonised under the
  WHS Act 2020 from 31 Mar 2022; the OSH Act 1984 is repealed.)
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

## 3. Architecture decisions (v1)

**Locked** = settled for v1. **⏳ Benchmark** = a pluggable component chosen by the Phase 4
eval, not assumed (refreshed 2026-06-29 — see [`docs/02-model-selection.md`](docs/02-model-selection.md)
and [`docs/research/2026-06-29-model-landscape.md`](docs/research/2026-06-29-model-landscape.md)).

| Decision | Choice |
|---|---|
| Approach | **Locked:** RAG only (no fine-tuning in v1) |
| Base model ⏳ Benchmark | Shortlist: **Qwen3-14B**, **Qwen3-30B-A3B** (MoE), **Mistral Small 3.2 24B**; small baseline Qwen3-8B / gpt-oss-20b; vanilla Llama 3.1 8B kept only as the no-RAG floor. All Apache/MIT — **Llama & Gemma 3 excluded on licence**. Run instruct (thinking OFF). |
| Model runtime | **Locked:** Ollama (Metal). ⚠️ Verify the Ollama→MLX engine switch: MLX is faster at decode but weaker at prefill/long-context (RAG-relevant) |
| Embedding model ⏳ Benchmark | Primary candidate **`bge-m3`** (native dense+sparse, hybrid-ready); `nomic-embed-text` prototyping only |
| Reranker ⏳ Benchmark *(new)* | **`Qwen3-Reranker-0.6B`** or `bge-reranker-v2-m3` — cross-encoder precision pass after retrieval |
| Vector store | **Locked:** Qdrant (local Docker instance) |
| RAG orchestration | **Locked:** LlamaIndex |
| Chunking | **Locked:** 512 tokens, 64-token overlap, structure-aware |
| Retrieval | **Locked:** two-stage — hybrid (semantic + BM25) retrieve top ~50 → rerank → top-6; jurisdiction metadata filter |
| Interface | **Locked:** CLI first, then Chainlit for the demo |
| Hardware | MacBook Pro M3 Max, 64GB unified memory |

> ⚠️ **Currency note (refreshed 2026-06-29):** the model / embedding / reranker rows are
> *pluggable* and chosen by the Phase 4 benchmark, not assumed. The original 2024 picks
> (Llama 3.1 8B, `nomic-embed-text`) are superseded as defaults. Two findings to honour:
> run **instruct variants with thinking OFF** (reasoning modes hallucinate *more* on grounded
> text), and **validate any pick on real AU/NZ WHS queries** — public benchmarks don't predict
> in-domain legal performance. Re-verify post-Jan-2026 model specs/availability at build time.

---

## 4. Locked corpus decisions

- **Jurisdictions:** AU (federal + all states/territories) + NZ.
- **Tier 1 (must-have for v1):** Model WHS Act + Regulations, all AU codes of practice, all
  NZ approved codes, AIHS BoK chapters, and each jurisdiction's Act / Regs / codes.
- **Harmonisation flag:** VIC is the sole non-harmonised jurisdiction (OHS Act 2004) → tag VIC docs `pre_harmonisation: true`; WA is harmonised (WHS Act 2020, 31 Mar 2022) → `false`. See `docs/research/2026-06-30-whs-source-map.md`.
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

- **Python tooling:** **uv** (decided Phase 1, 2026-06-30). `pyproject.toml` + `uv.lock` are
  the source of truth; `requirements.txt` is a generated locked mirror for non-uv users.
  Run scripts with `uv run <script>`; add deps with `uv add <pkg>`.
- **Dependency licensing:** every runtime dependency must be permissively licensed
  (MIT / BSD / Apache-2.0) to stay compatible with the project's Apache-2.0 code licence.
  **PyMuPDF (AGPL-3.0) is deliberately avoided** for PDF extraction in favour of
  `pdfplumber` / `pdfminer.six` (MIT). Flag any AGPL/GPL/SSPL dependency before adding it.
- **Network/sandbox:** corpus downloads hit public AU/NZ government sites; run
  `download_corpus.py` with network egress enabled. Government WAFs require a browser-like
  User-Agent (a bot UA hangs/403s) — the script sets one and self-throttles.
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
