# SafetyLM — Distribution and Launch Strategy

## v1 distribution approach

**Phase 5 target:** GitHub repository with README, full documentation, and installation guide. Hugging Face included if benchmark results justify the claim.

This is intentionally minimal. The goal is to ship something real rather than over-invest in distribution infrastructure before the product exists.

---

## GitHub repository

### Repository name
`SafetyLM` under your personal GitHub account to start. If community contribution grows, migrate to a GitHub organisation (`safetylm-org` or similar) to give the project independent identity from any one contributor.

### Repository structure at launch
```
SafetyLM/
├── README.md                  # Project overview, quick start, what it does/doesn't do
├── CONTRIBUTING.md            # How to contribute corpus additions, eval questions, code
├── LIMITATIONS.md             # Honest accounting of failure modes and scope boundaries
├── LICENSE                    # Apache 2.0 for code; CC-BY-4.0 for dataset
├── docs/                      # All planning and architecture docs (these files)
├── corpus/
│   └── manifest/              # corpus_manifest.csv and .xlsx (source catalogue only)
├── embeddings/                # Embedding pipeline scripts
├── rag/                       # RAG pipeline, prompt templates, CLI, Chainlit app
├── eval/                      # Benchmark dataset and evaluation scripts
└── scripts/                   # Download, extraction, chunking utilities
```

### Repository settings
- **Topics:** `whs`, `ohs`, `work-health-safety`, `llm`, `rag`, `open-source`, `australia`, `new-zealand`, `safety`, `ai`
- **Description:** "Open-source RAG-powered AI for Australian and New Zealand WHS practitioners"
- **Website:** safetylm.com (once domain is live)
- **Social preview image:** worth creating — GitHub cards with visuals get significantly more click-through

### README structure
```
# SafetyLM

[One-line description]
[Badges: licence, Hugging Face, GitHub stars]

## What SafetyLM does
## What SafetyLM does NOT do (important — sets expectations)
## Quick start (5 commands to get running)
## Requirements (hardware, Python version, Ollama)
## Architecture overview (link to docs/01-architecture.md)
## Benchmark results
## Limitations
## Contributing
## Licence
```

---

## Hugging Face

### When to publish

Publish to Hugging Face when:
- Benchmark results show SafetyLM meaningfully outperforms the no-RAG baseline floor (vanilla Llama 3.1 8B) on the WHS benchmark
- The system prompt and RAG pipeline are stable enough that the published version is representative
- The dataset card is written and accurate

Do not publish early for visibility. A model card that can't be backed by benchmark evidence damages credibility faster than no presence at all.

### What to publish

**SafetyLM model card** — not fine-tuned weights (v1 has none), but a model card that documents:
- Base model: selected by the Phase 4 benchmark from the Apache/MIT-licensed shortlist (Qwen3-14B, Qwen3-30B-A3B, or Mistral Small 3.2 24B) — Llama excluded on licence grounds (vanilla Llama 3.1 8B is kept only as the no-RAG baseline floor)
- System prompt template (publishable, not secret)
- Corpus methodology and sources
- Benchmark results
- How to reproduce the system

**SafetyLM-Eval dataset** — the 500-question benchmark dataset, published independently so it has standalone utility. This is the more immediately valuable Hugging Face contribution at v1.

### Profile page
Hugging Face organisation: `safetylm` — request the namespace early, before launch.

---

## Domain

`safetylm.com` — register now, build later.

**v1:** Point to the GitHub repository. A simple redirect is fine.  
**v2:** A dedicated project site with docs, demo, and community links. Can extend neetsingh.com as a subdomain (`safetylm.neetsingh.com`) for v1 if the domain isn't ready, then migrate.

---

## Community announcement

### Sequencing

1. **Soft launch** — GitHub repo goes public with a pinned post on your personal LinkedIn. No formal announcement. Gather early feedback from your immediate network.

2. **AIHS announcement** — post to the AIHS LinkedIn page and any relevant community groups once you have benchmark results. The WHS Rising Star credibility and your COHSProf accreditation are the trust signals that make this land differently than a random AI project.

3. **Tech communities** — post to r/LocalLLaMA (Hugging Face and local model community), the LlamaIndex Discord, and relevant WHS LinkedIn groups.

### Messaging

The announcement is not "I built an AI." It is:

> "There is no open-source AI grounded in Australian and New Zealand WHS legislation and frameworks. I built one. Here's what it can do, here's what it can't, and here's how you can run it yourself or contribute to making it better."

The limitations and honest framing are part of the credibility, not a weakness of the pitch. WHS practitioners are trained to be sceptical. Meeting that scepticism directly is the right approach.

---

## Contribution model

At launch, contributions are welcome in three areas:

**1. Corpus contributions**
Adding documents to the manifest that are missing from the initial scope. Contributors submit a pull request adding rows to `corpus_manifest.csv` with all metadata populated.

**2. Evaluation contributions**
Adding questions to the benchmark dataset. A contributing WHS practitioner can add their own jurisdiction-specific or domain-specific questions using the format in `docs/05-evaluation.md`.

**3. Code contributions**
Pipeline improvements, new retrieval strategies, UI enhancements, bug fixes. Standard GitHub fork-and-PR workflow.

What is explicitly not accepted for v1: adding non-AU/NZ jurisdictions, adding commercial or proprietary safety documents, changes to the base model without benchmark evidence.
