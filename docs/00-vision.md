# SafetyLM — Vision, Goals, and Guiding Principles

## The problem

WHS practitioners in Australia and New Zealand operate in a complex, multi-jurisdictional regulatory environment. When they turn to general AI tools for help — drafting SWMS, investigating incidents, interpreting legislation, identifying critical controls — the tools fail in domain-specific ways that a non-practitioner would never detect.

A chatbot confidently citing a repealed regulation, conflating the model WHS Act with jurisdiction-specific variations, or applying a generic "hierarchy of controls" template where a bowtie analysis was needed is not a minor inconvenience. In a safety-critical context, it erodes trust and potentially contributes to poor decisions.

No existing open-source model is trained or grounded specifically for AU/NZ WHS practice. SafetyLM exists to fill that gap.

---

## Vision statement

> SafetyLM is the open-source AI reasoning system that WHS practitioners across Australia and New Zealand can actually trust — grounded in primary legislation, aligned to domain frameworks, and transparent about its sources.

---

## Build goals

### v1 (current scope)
- A working RAG system that retrieves relevant WHS content from a curated AU/NZ corpus and generates practitioner-grade responses
- Public GitHub repository with full documentation and methodology
- A benchmark evaluation dataset of 500+ WHS-specific questions that anyone can use to test any model
- Hugging Face presence when system quality justifies it

### v2 (future scope — out of scope for now)
- Fine-tuned model weights that internalise WHS reasoning patterns (ICAM structure, bowtie logic, critical control thinking)
- Synthetic training dataset generated from v1 RAG outputs and human review
- LoRA adapters published to Hugging Face so organisations can extend on their own data

---

## Who this is for

**Primary users**
- WHS consultants doing legislative research across jurisdictions
- Early-career WHS professionals who need a reliable starting point for documents and frameworks
- Small business operators without a dedicated safety team
- WHS students and people studying for CERT IV, Diploma, or postgraduate WHS qualifications

**Secondary users**
- WHS software vendors embedding domain AI into their products
- Researchers and academics studying AI applications in occupational health and safety
- Large organisations wanting to self-host a WHS AI on their own infrastructure

---

## What SafetyLM is not

- Not a replacement for professional WHS advice or a qualified practitioner
- Not a legal interpretation service
- Not a general-purpose chatbot
- Not a compliance checker that guarantees legislative currency (the corpus has a published date, users must verify current versions)

These constraints are not disclaimers buried in fine print. They are design decisions that shape how the system responds and what it declines to assert with confidence.

---

## Guiding principles

**1. Source transparency**
Every response surfaces which document it drew from, which jurisdiction, and when that document was last reviewed. If the retrieval system cannot find a grounded source, the model says so rather than generating a plausible-sounding answer.

**2. Jurisdiction precision**
The corpus is structured by jurisdiction. A query about working at heights in Western Australia retrieves WA instruments first, not NSW codes that happen to rank higher semantically. Jurisdictional metadata is a first-class retrieval filter, not an afterthought.

**3. Framework alignment**
The system prompt and prompt templates are designed around the frameworks WHS professionals actually use: ICAM for incident investigation, bowtie for critical control analysis, the hierarchy of controls for risk treatment, the WHS Act duty hierarchy for legal framing. The model doesn't just know what these are — it reasons through them.

**4. Conservative confidence**
The model is calibrated to express uncertainty rather than confabulate. A response that says "I couldn't find a specific code of practice for this scenario in the SA jurisdiction — here is what the model WHS Act says at a federal level" is more valuable than a confident but fabricated answer.

**5. Open methodology**
The corpus curation criteria, chunking strategy, embedding model choice, retrieval architecture, and evaluation benchmark are all documented and published. Other practitioners, researchers, and developers can reproduce, critique, and improve the system.

---

## Success criteria for v1

SafetyLM v1 is successful when:

- [ ] A WHS practitioner can ask a jurisdiction-specific legislative question and receive a response citing the correct instrument with a source link
- [ ] The system correctly distinguishes between model WHS Act provisions and jurisdiction-specific variations at least 80% of the time on the benchmark dataset
- [ ] Responses to incident investigation prompts demonstrate ICAM-structured reasoning without the user having to ask for it
- [ ] The GitHub repository has clear enough documentation that another WHS practitioner with basic technical literacy could run the system locally
- [ ] The benchmark evaluation dataset is published and usable independently of SafetyLM itself
