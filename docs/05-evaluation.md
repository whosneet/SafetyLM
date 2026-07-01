# SafetyLM — Evaluation and Benchmark Design

## Why evaluation matters more than the model

Most AI projects optimise for the model and underinvest in evaluation. The result is a system that feels good in informal testing but has no rigorous evidence of improvement — or degradation — when components change.

For SafetyLM, the evaluation benchmark serves three purposes:

1. **Quality gate:** Before any component change ships (corpus update, chunking tweak, prompt revision), it runs against the benchmark. If the score drops, the change is rejected or revised.
2. **Public credibility:** A published benchmark dataset lets the WHS community and other developers independently verify SafetyLM's claims. It also lets them test competing systems — making the dataset itself a contribution to the field.
3. **Improvement signal:** The benchmark tells you precisely where the system fails, not just that it's failing. "Fails on WA-specific queries" is an actionable finding. "Doesn't feel right" is not.

> **Learning note:** In ML, evaluation datasets are how you make subjective quality ("is this answer good?") into something measurable and repeatable. The benchmark is a set of questions where you already know the correct answer. You run the system, compare its output to the known answer, and score it. Do this consistently and you have a reliable signal for whether changes help or hurt.

---

## Benchmark dataset design

### Target size

**500 question-answer pairs for v1 launch**

Rationale: enough to cover the main query categories with statistical reliability, small enough to build and validate manually without unreasonable effort. The dataset grows with the project.

### Question categories

| Category | Description | Target count | % of dataset |
|---|---|---|---|
| Legislative interpretation | Jurisdiction-specific duty questions | 120 | 24% |
| Jurisdictional comparison | How does X differ between NSW and VIC? | 60 | 12% |
| Incident investigation | ICAM application, contributing factor identification | 80 | 16% |
| Critical control reasoning | Bowtie application, control effectiveness | 60 | 12% |
| Document retrieval | Find the relevant code of practice / section | 80 | 16% |
| Procedural WHS | SWMS content, consultation requirements, notification | 60 | 12% |
| Definitions and terms | What does [defined term] mean under [Act]? | 40 | 8% |

### Question format

Each benchmark entry contains:

```yaml
question_id:        WHS-LEG-NSW-001
category:           LEGISLATIVE_INTERPRETATION
jurisdiction:       NSW
hazard_category:    PSYCHOSOCIAL
priority_tier:      1
difficulty:         MEDIUM   # EASY / MEDIUM / HARD
question:           "What is the primary duty of a PCBU under the Work Health 
                    and Safety Act 2011 (NSW) regarding psychosocial hazards?"
ground_truth:       "Under section 19 of the Work Health and Safety Act 2011 
                    (NSW), a PCBU must ensure, so far as is reasonably 
                    practicable, the health (including psychological health), 
                    safety and welfare of workers and others at the workplace..."
key_facts:          
  - "Section 19 is the primary duty provision"
  - "Health includes psychological health explicitly"
  - "Standard is reasonably practicable"
  - "Duty extends to psychological safety"
source_document:    "Work Health and Safety Act 2011 (NSW)"
source_section:     "Section 19"
source_url:         "https://legislation.nsw.gov.au/view/html/inforce/current/act-2011-010"
validated_by:       "Neet Singh, WHS practitioner"
date_validated:     "2026"
notes:              ""
```

### Difficulty classification

**EASY:** Single document, explicit answer, no interpretation required
Example: "What does 'reasonably practicable' mean under the model WHS Act?"

**MEDIUM:** Requires understanding of jurisdiction-specific variation or cross-referencing Act and Regulation
Example: "What are the notification requirements for a serious injury in QLD and how do they differ from the model WHS Regulations?"

**HARD:** Requires reasoning across multiple documents, applying a framework (ICAM/bowtie), or navigating jurisdictional complexity
Example: "Apply an ICAM analysis to this scenario: [scenario]. What were the organisational factors and what critical controls were absent?"

---

## Scoring methodology

### For factual questions (legislative, definitions, procedural)

**RAGAS framework** — a standard evaluation approach for RAG systems with four dimensions:

| Metric | What it measures | How scored |
|---|---|---|
| Answer correctness | Does the answer match the ground truth? | 0–1, LLM-as-judge against key_facts |
| Faithfulness | Is the answer grounded in retrieved context? | 0–1, checks for hallucination |
| Context precision | Were the retrieved chunks actually relevant? | 0–1, relevant chunks / total chunks retrieved |
| Context recall | Did retrieval find the chunks needed to answer? | 0–1, needed chunks found / total needed |

> **Learning note:** RAGAS (Retrieval-Augmented Generation Assessment) uses a separate LLM to score the outputs of your RAG system. You don't manually read 500 answers — you define the scoring criteria and an LLM evaluates them at scale. You then manually review a sample to validate that the LLM scorer is calibrated correctly.

### For reasoning questions (ICAM, bowtie, critical control)

Automated scoring is less reliable for open-ended reasoning. These use a **rubric-based human review** on a sample:

| Criterion | Weight |
|---|---|
| Correct framework applied (ICAM vs generic) | 25% |
| Causation hierarchy correctly identified | 25% |
| Controls identified are appropriate to the hazard | 25% |
| Response is actionable for a practitioner | 25% |

### Jurisdictional accuracy (cross-cutting)

A separate metric tracked across all categories:
- Did the response correctly identify the applicable jurisdiction?
- Did it correctly distinguish federal vs state provisions?
- Did it correctly flag VIC pre-harmonisation where applicable (Victoria being the sole non-harmonised jurisdiction)?

Target for v1: **>85% jurisdictional accuracy** across the full benchmark.

---

## Baseline comparison

Before evaluating SafetyLM, run the benchmark against:

1. **Vanilla Llama 3.1 8B** with no system prompt and no RAG — establishes the floor
2. **The chosen base model (Phase 4 benchmark pick — e.g. Qwen3-14B) with WHS system prompt but no RAG** — isolates the value of the system prompt
3. **SafetyLM (full RAG + system prompt)** — the actual system

If SafetyLM doesn't meaningfully outperform a well-prompted vanilla model, the RAG pipeline isn't adding value. That's important information, not a failure — it means the corpus or retrieval design needs revisiting.

---

## Publishing the benchmark

The benchmark dataset is published independently of SafetyLM on Hugging Face Datasets under a Creative Commons CC-BY-4.0 licence.

**Dataset card will include:**
- How questions were created and validated
- What WHS expertise was applied in validation
- Known gaps (questions not yet covered, jurisdictions underrepresented)
- How to run evaluation against any model using the dataset
- Version history as the dataset grows

This is a genuine contribution to the WHS AI space regardless of how SafetyLM performs. Any future WHS AI system — open source or commercial — can benchmark against it. That gives SafetyLM community relevance beyond its own performance.

---

## Evaluation tooling

| Tool | Purpose |
|---|---|
| RAGAS library | Automated RAG evaluation (Answer correctness, Faithfulness, Context precision/recall) |
| Pandas | Dataset management and scoring aggregation |
| Weights & Biases (optional) | Experiment tracking — log every benchmark run with config metadata |
| Jupyter notebooks | Interactive evaluation review and analysis |

All evaluation scripts live in `eval/` and are published to GitHub alongside the dataset.
