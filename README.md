# SafetyLM

> An open-source, RAG-powered AI system built for Work Health and Safety practitioners across Australia and New Zealand.

SafetyLM is a domain-specialised AI reasoning system grounded in AU/NZ WHS legislation, codes of practice, incident investigation frameworks, and safety science. It is not a general-purpose chatbot with a safety prompt — it is a purpose-built tool that reasons in the language WHS professionals actually use.

**Built by:** Avneet (Neet) Singh  
**Status:** Pre-development — planning phase  
**Architecture:** RAG v1, fine-tuning planned for v2  
**Base model:** TBD (see [`docs/02-model-selection.md`](docs/02-model-selection.md))  
**Jurisdictions:** Australia (federal + all states and territories) + New Zealand  

---

## Why SafetyLM exists

General-purpose LLMs fail WHS practitioners in predictable ways:

- Hallucinate legislative citations and regulation numbers
- Conflate jurisdictions (citing NSW regs in a WA context)
- Give generic risk management advice with no grounding in AU/NZ law
- Don't reason in domain frameworks like ICAM, bowtie, or critical control logic
- Can't distinguish between model WHS Act provisions and jurisdiction-specific variations

SafetyLM is built to fix that. The corpus is grounded in primary sources. The retrieval pipeline surfaces the right jurisdiction. The system prompt shapes reasoning toward WHS professional standards.

---

## Documentation index

| Document | Purpose |
|---|---|
| [`docs/00-vision.md`](docs/00-vision.md) | Project vision, goals, and guiding principles |
| [`docs/01-architecture.md`](docs/01-architecture.md) | System architecture — how the pieces fit together |
| [`docs/02-model-selection.md`](docs/02-model-selection.md) | Base model comparison and recommendation for M3 Max hardware |
| [`docs/03-corpus-strategy.md`](docs/03-corpus-strategy.md) | Corpus scope, source taxonomy, and curation approach |
| [`docs/04-rag-pipeline.md`](docs/04-rag-pipeline.md) | RAG pipeline design — chunking, embedding, retrieval, prompting |
| [`docs/05-evaluation.md`](docs/05-evaluation.md) | Benchmark design and how to measure if SafetyLM is working |
| [`docs/06-phased-roadmap.md`](docs/06-phased-roadmap.md) | Phase-by-phase build plan with acceptance criteria |
| [`docs/07-distribution.md`](docs/07-distribution.md) | GitHub, Hugging Face, and community launch strategy |
| [`docs/08-governance.md`](docs/08-governance.md) | Licensing, liability, attribution, and contribution guidelines |
| [`docs/learning/`](docs/learning/) | Concept explainers annotated to each build phase |

---

## Project principles

1. **Domain depth over breadth** — one jurisdiction done well beats ten done poorly
2. **Transparency over black-box** — every answer should be traceable to a source document
3. **Practitioners first** — the benchmark is whether a WHS professional trusts the output, not whether it scores well on generic LLM leaderboards
4. **Open by default** — corpus methodology, evaluation datasets, and model weights published openly
5. **Conservative on liability** — clear disclaimers, source citations always surfaced, no substitution for professional judgement

---

## Repository structure (planned)

```
safetylm/
├── README.md
├── docs/                  # All planning and architecture documentation
│   └── learning/          # Concept explainers (annotated to build phases)
├── corpus/                # Corpus manifest, download scripts, processing pipeline
│   ├── manifest/          # Spreadsheet of all source documents
│   ├── raw/               # Downloaded source documents (gitignored)
│   └── processed/         # Chunked and cleaned text (gitignored)
├── embeddings/            # Embedding pipeline and vector store configuration
├── rag/                   # Retrieval pipeline and prompt templates
├── eval/                  # Benchmark dataset and evaluation scripts
└── scripts/               # Utility scripts (download, process, index)
```

---

## Current phase

**Phase 0 — Planning and documentation** ← you are here

Next: Phase 1 — Corpus build
