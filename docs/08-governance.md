# SafetyLM — Governance, Licensing, and Liability

## Licence structure

SafetyLM uses a split licence approach because code and data have different intellectual property considerations.

| Component | Licence | Why |
|---|---|---|
| Code (pipeline, scripts, evaluation, UI) | Apache 2.0 | Permissive, patent protection, compatible with commercial use, standard for open-source AI tooling |
| Benchmark dataset | Creative Commons CC-BY-4.0 | Allows reuse with attribution, standard for open datasets |
| Documentation | Creative Commons CC-BY-4.0 | Same reasoning as dataset |
| Base model (benchmark-chosen; Apache/MIT-only shortlist: Qwen3-14B / Qwen3-30B-A3B / Mistral Small 3.2 24B) | Provider's permissive licence (Apache 2.0 / MIT) | Obtained by users from the provider via Ollama; Llama & Gemma 3 excluded on licence grounds |

> **Learning note — why not MIT:**  
> Apache 2.0 and MIT are both permissive. The key difference is that Apache 2.0 includes an explicit patent grant — if a contributor has patents relevant to their contribution, they grant users rights to those patents. For a project in a safety-critical domain, Apache 2.0 is the more defensible choice.

> **Learning note — why the base model licence matters:**  
> You are not distributing model weights — users pull them from the provider directly via Ollama. Your Apache 2.0 licence covers SafetyLM's code. The v1 model shortlist is Apache/MIT-licensed (Qwen3-14B, Qwen3-30B-A3B, Mistral Small 3.2 24B), so users inherit a permissive licence on the weights too — record the exact model and its licence once the Phase 4 benchmark picks it. Document this in the README and `LIMITATIONS.md`.

---

## Liability and disclaimer

WHS advice carries real-world consequences. SafetyLM's disclaimer is not boilerplate — it is a design principle surfaced prominently and repeatedly.

### Required disclaimer language

Include verbatim in README, model card, and as a persistent UI element in the Chainlit interface:

```
SafetyLM is an AI research tool for information purposes only.

It is not a substitute for professional WHS advice, legal advice, or the 
judgement of a qualified work health and safety practitioner.

SafetyLM's responses are grounded in publicly available documents as of 
the corpus version date. Legislative instruments are amended regularly — 
always verify currency with the relevant regulator before relying on any 
legislative provision cited here.

Avneet Singh and SafetyLM contributors accept no liability 
for decisions made in reliance on SafetyLM outputs.
```

### What SafetyLM should decline to do

Hard boundaries enforced in the system prompt:

- Not assert that a legislative provision is currently in force
- Not provide advice on a specific incident investigation in a way that could prejudice a regulatory investigation
- Not generate content that could be used to obscure or minimise serious safety failures
- Not make jurisdictional assertions without surfacing the source document

---

## Attribution requirements

SafetyLM draws on Crown copyright documents. Australian and New Zealand Crown copyright generally permits reproduction for non-commercial purposes with attribution. The corpus manifest records the licence status of every source document.

Attribution format for corpus sources in responses:
```
© Commonwealth of Australia / [State] / New Zealand Crown, [year]. 
Reproduced under Crown copyright for non-commercial research purposes.
```

For documents under Creative Commons (AIHS Body of Knowledge chapters):
```
AIHS Body of Knowledge, Chapter [X]. 
Licensed under Creative Commons Attribution-NonCommercial-ShareAlike.
```

---

## Governance principles for v1

As a solo project at v1, governance is simple. Document it now so the framework scales if contributors join.

**Decision authority:** Project creator (Neet Singh) retains final authority on:
- Changes to corpus scope and source inclusion criteria
- Modifications to the system prompt
- Benchmark design and scoring methodology
- Licence and liability framework

**Accepted contributions** without prior approval:
- Corpus manifest additions with complete metadata and verified URLs
- Benchmark question additions in the correct format
- Bug fixes that don't modify system behaviour
- Documentation improvements

**Changes requiring discussion before merge:**
- New document categories or jurisdictions
- Changes to chunking strategy or retrieval architecture
- System prompt modifications
- New model integrations

**What will never be accepted:**
- Proprietary or confidential documents without clear licence
- Documents that could compromise an ongoing regulatory investigation or legal proceeding
- Contributions that dilute the AU/NZ WHS focus in v1

---

## Versioning

SafetyLM uses semantic versioning: `vMAJOR.MINOR.PATCH`

- **MAJOR:** Breaking change to pipeline architecture, model change, or corpus scope restructure
- **MINOR:** Corpus additions, system prompt changes, new evaluation questions
- **PATCH:** Bug fixes, documentation updates, script improvements

Corpus versions are tracked separately from code versions. A corpus update without pipeline changes is a MINOR bump with a corpus changelog entry.

Every version published to Hugging Face has a corresponding git tag and release notes in GitHub.

---

## Code of conduct

Contributors to SafetyLM are expected to:

- Engage in good faith with the safety science that underpins the project
- Not use the project to minimise or obscure workplace safety failures
- Attribute sources accurately and not introduce fabricated legislative citations
- Treat WHS practitioners as the primary audience — contributions should serve them

This is not an exhaustive code of conduct. A full contributor covenant will be added when the project has active contributors beyond the founder.
