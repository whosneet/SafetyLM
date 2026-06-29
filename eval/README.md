# eval/

The credibility layer — the benchmark dataset and evaluation scripts that prove SafetyLM
works and let anyone test any WHS AI system. Licensed CC BY 4.0 (see `DATA-LICENSE.md`) and
published independently on Hugging Face.

**Planned (Phase 4):**

- `benchmark/` — 500 question–answer pairs across 7 categories (legislative interpretation,
  jurisdictional comparison, incident investigation, critical control reasoning, document
  retrieval, procedural WHS, definitions). Entry format: `docs/05-evaluation.md`.
- `run_eval.py` — run the benchmark against SafetyLM and the baselines (vanilla Llama,
  prompted Llama, full RAG)
- RAGAS scoring for factual categories; rubric-based human review for reasoning categories

**Targets (v1):** jurisdictional accuracy > 85%; SafetyLM beats vanilla Llama on legislative
interpretation by > 30 points. Scoring methodology & RAGAS explainer: `docs/05-evaluation.md`
and `docs/learning/concepts.md` (Phase 4).
