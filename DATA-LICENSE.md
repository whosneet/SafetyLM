# Data & Documentation Licence

SafetyLM uses a **split licence**. This file covers the non-code assets.

| Asset | Licence |
|---|---|
| Source code (pipeline, scripts, evaluation code, UI) | Apache 2.0 — see [`LICENSE`](LICENSE) |
| **Benchmark dataset** (`eval/`) | **CC BY 4.0** (this file) |
| **Documentation** (`docs/`, `README.md`) | **CC BY 4.0** (this file) |
| Base model weights (benchmark-selected; Apache/MIT shortlist: Qwen3-14B / Qwen3-30B-A3B / Mistral Small 3.2 24B) | Provider's permissive licence (Apache 2.0 / MIT) — obtained by users from the provider via Ollama; not redistributed here. Llama & Gemma 3 excluded on licence grounds. |
| Corpus source documents (`corpus/raw/`, not committed) | Crown copyright / open access — see per-document `license_notes` in the corpus manifest |

---

## CC BY 4.0 — Creative Commons Attribution 4.0 International

The SafetyLM benchmark dataset and documentation are licensed under the
**Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

**You are free to:**

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

**Under the following terms:**

- **Attribution** — You must give appropriate credit, provide a link to the licence, and
  indicate if changes were made. You may do so in any reasonable manner, but not in any way
  that suggests the licensor endorses you or your use.

Full legal code: <https://creativecommons.org/licenses/by/4.0/legalcode>

**Suggested attribution:**

> "SafetyLM" by Avneet Singh and contributors, licensed under CC BY 4.0.

---

## Attribution of corpus source documents

Corpus documents are primary government and standards-body publications and are **not**
relicensed by SafetyLM. They remain under their original terms. Responses that quote them
attribute as follows:

```
© Commonwealth of Australia / [State] / New Zealand Crown, [year].
Reproduced under Crown copyright for non-commercial research purposes.
```

For AIHS Body of Knowledge chapters:

```
AIHS Body of Knowledge, Chapter [X].
Licensed under Creative Commons Attribution-NonCommercial-ShareAlike.
```

See `docs/08-governance.md` for the full attribution and liability framework.
