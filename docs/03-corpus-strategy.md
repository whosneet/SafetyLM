# SafetyLM — Corpus Strategy

## What the corpus is

The corpus is SafetyLM's knowledge base — every document the system can draw on when answering a question. The quality of the corpus is the single biggest determinant of output quality. A well-designed RAG system on a mediocre corpus produces mediocre answers. A well-curated corpus with a straightforward RAG pipeline produces excellent answers.

> **Learning note:** "Corpus" is the technical term for a structured collection of text documents used to train or ground an AI system. In RAG, the corpus is not baked into the model — it lives in a vector database that the model queries at runtime. This means you can update the corpus without retraining anything.

---

## Corpus design principles

**1. Primary sources only**
Legislation, regulations, and codes of practice from official regulators only. No summaries, no third-party interpretations, no blog posts. When SafetyLM cites a document, it cites something a practitioner or court would recognise as authoritative.

**2. Metadata is first-class**
Every chunk of text carries structured metadata: jurisdiction, document type, regulator, hazard category, date published, legislative currency. This metadata drives retrieval filtering — the system doesn't just find semantically relevant text, it finds the right jurisdiction's relevant text.

**3. Currency flagged, not assumed**
WHS legislation is amended regularly. The corpus records the version date of every document. Responses include a currency caveat. The system never asserts that a provision is currently in force without the user verifying against the regulator's live publication.

**4. Reproducible**
The corpus manifest (the spreadsheet) is the source of truth. Anyone can take the manifest, run the download scripts, and reproduce the corpus. The raw and processed documents are gitignored (too large), but the methodology is fully open.

---

## Source taxonomy

### Tier 1 — Foundation (must have for v1)

These are the documents SafetyLM cannot function without. Any question involving AU/NZ WHS law touches these.

**Federal**
- Model WHS Act 2011 (and all amendments)
- Model WHS Regulations 2011 (and all amendments)
- All Safe Work Australia approved codes of practice (~28–30 documents — verify exact current count)
- Safe Work Australia guidance materials (psychosocial, silica, asbestos, manual tasks, plant, etc.)
- Key Work Health and Safety Statistics — Australia (annual)

**States and territories**
For each jurisdiction: WHS Act, WHS Regulations, all approved/compliance codes of practice

| Jurisdiction | Act | Regulator |
|---|---|---|
| NSW | Work Health and Safety Act 2011 (NSW) | SafeWork NSW |
| VIC | Occupational Health and Safety Act 2004 | WorkSafe VIC |
| QLD | Work Health and Safety Act 2011 (QLD) | Workplace Health and Safety QLD |
| SA | Work Health and Safety Act 2012 (SA) | SafeWork SA |
| WA | Work Health and Safety Act 2020 (WA) — harmonised 31 Mar 2022 | WorkSafe WA |
| TAS | Work Health and Safety Act 2012 (Tas) | WorkSafe Tasmania |
| NT | Work Health and Safety (National Uniform Legislation) Act 2011 | NT WorkSafe |
| ACT | Work Health and Safety Act 2011 (ACT) | WorkSafe ACT |
| Federal (Cth) | Work Health and Safety Act 2011 (Cth) | Comcare |

> **Note on harmonisation (corrected 2026-06-30):** **Victoria is the sole non-harmonised jurisdiction** — it operates under the Occupational Health and Safety Act 2004 (Vic) and OHS Regulations 2017, and uses "compliance codes" rather than "codes of practice". VIC documents are flagged `pre_harmonisation: true`. **Western Australia is now harmonised:** the Work Health and Safety Act 2020 (WA) commenced 31 March 2022 and repealed the OSH Act 1984, so WA documents are `pre_harmonisation: false` — do **not** catalogue the repealed OSH Act 1984 as current WA law. See [`research/2026-06-30-whs-source-map.md`](research/2026-06-30-whs-source-map.md).

**New Zealand**
- Health and Safety at Work Act 2015 (HSWA)
- Health and Safety at Work (General Risk and Workplace Management) Regulations 2016
- Health and Safety at Work (Hazardous Substances) Regulations 2017
- Health and Safety at Work (Asbestos) Regulations 2016
- Health and Safety at Work (Major Hazard Facilities) Regulations 2016
- All WorkSafe NZ approved codes of practice
- WorkSafe NZ good practice guidelines

---

### Tier 2 — Important (include in v1 where available)

**AIHS Body of Knowledge**
All publicly available chapters covering: safety science foundations, risk, human factors, safety management systems, incident investigation, psychosocial hazards, contractor management, leadership, and more. Published at **ohsbok.org.au** (not aihs.org.au). **Licence caveat:** the OHS Body of Knowledge is **proprietary** (non-commercial, no-derivatives, no-charging — *not* an open/Creative Commons licence), so chapters are catalogued but flagged **not ingestable** for model training absent written AIHS permission.

**Industrial manslaughter legislation (updated 2026-06-30)**
As of 2026, an industrial/workplace manslaughter offence is in force in **all nine Australian jurisdictions**:
- QLD: Work Health and Safety Act 2011 (Qld) — industrial manslaughter (2017)
- NT: WHS (National Uniform Legislation) Act 2011 (NT) — from 1 Feb 2020
- VIC: Workplace manslaughter, Occupational Health and Safety Act 2004 (Vic) — from 1 Jul 2020
- WA: Work Health and Safety Act 2020 (WA) — from 31 Mar 2022
- SA: Work Health and Safety Act 2012 (SA) — from 1 Jul 2024
- Cth: Work Health and Safety Act 2011 (Cth) — from 1 Jul 2024 (Commonwealth public sector + scheme licensees)
- NSW: Work Health and Safety Act 2011 (NSW) — enacted 2024 (confirm operative commencement)
- TAS: WHS Amendment (Industrial Manslaughter) Act 2024 (Tas) — from 2 Oct 2024
- ACT: industrial manslaughter under the Work Health and Safety Act 2011 (ACT)
- NZ: no dedicated industrial-manslaughter offence; HSWA s.47 (reckless conduct) is the most serious offence

**Thematic guidance across all jurisdictions**
- Psychosocial hazards and psychological health
- Occupational violence and aggression (OVA)
- Sexual harassment and Respect@Work positive duty
- Engineered stone / crystalline silica / RCS
- Asbestos identification and management
- Working at heights / fall prevention
- Hazardous manual tasks / musculoskeletal disorders
- Plant and equipment / machinery guarding
- Electrical safety
- Confined spaces
- Contractor management and PCBU duty chain
- Fatigue management

---

### Tier 3 — Supplementary (v1 stretch, v2 priority)

- Selected Federal Court and state tribunal decisions on WHS prosecutions (establishes how duties are interpreted in practice)
- Coroners court findings with WHS relevance
- Safe Work Australia research reports
- International Labour Organization (ILO) conventions ratified by Australia
- ISO 45001:2018 — licensing makes direct inclusion complex, but the AIHS BoK covers it substantially

---

## Corpus metadata schema

Every document in the corpus manifest carries these fields. Every chunk derived from that document inherits them.

```
source_id           Unique ID: [JURISDICTION]-[CATEGORY]-[SEQUENCE]
                    e.g. FED-COP-001, NSW-LEG-001, NZ-REG-003

jurisdiction        FED / NSW / VIC / QLD / SA / WA / TAS / NT / ACT / NZ

regulator           Issuing body full name
                    e.g. Safe Work Australia, SafeWork NSW, WorkSafe NZ

document_type       LEGISLATION / REGULATION / CODE_OF_PRACTICE /
                    GUIDANCE / STATISTICAL_REPORT / COURT_DECISION /
                    POLICY / BOK_CHAPTER

document_title      Full official title

url                 Direct URL to document or landing page

file_format         PDF / HTML / DOCX / XLSX

date_published      YYYY-MM-DD or YYYY if only year known

date_last_reviewed  YYYY-MM-DD or NULL

legislative_currency CURRENT / SUPERSEDED / UNDER_REVIEW

hazard_category     PRIMARY hazard domain — one value only:
                    PSYCHOSOCIAL / OVA / FALLS / PLANT_EQUIPMENT /
                    CHEMICAL / MANUAL_HANDLING / ELECTRICAL /
                    CONFINED_SPACES / CONTRACTOR / GENERAL

industry_relevance  Comma-separated: CONSTRUCTION / HEALTH /
                    TRANSPORT / MANUFACTURING / MINING / ALL

priority_tier       1 / 2 / 3

pre_harmonisation   true / false (true = non-harmonised jurisdiction; VIC only.
                    WA is harmonised since 2022, so WA = false)

license_notes       Crown copyright / Creative Commons / Open Access

notes               Version notes, relationships to other documents,
                    known gaps
```

---

## Chunking strategy

> **Learning note:** Chunking is how you break large documents into smaller pieces for the vector store. The LLM can only process a limited amount of text at once (its "context window"). Chunking ensures each piece is small enough to be efficiently retrieved and injected, while large enough to contain meaningful information.

**The tradeoff:** Small chunks = more precise retrieval but lose surrounding context. Large chunks = more context but noisier retrieval and higher token cost.

**SafetyLM approach:**
- Chunk size: 512 tokens with 64-token overlap
- Overlap ensures a sentence split at a chunk boundary doesn't lose its context
- Chunks respect document structure where possible: section headings, clause numbers, and definition boundaries are preserved as natural split points
- Each chunk stores the section heading it belongs to as metadata (e.g. "Division 2 — Primary duty of care")

This is a starting point. The evaluation benchmark will expose whether chunk size needs tuning — if the system consistently retrieves relevant documents but misses the specific clause, chunks are too large. If it retrieves clauses with no surrounding context, chunks are too small.

---

## Corpus build output

The corpus build phase produces three things:

1. **`corpus/manifest/corpus_manifest.csv`** — the master catalogue, one row per source document
2. **`corpus/manifest/corpus_manifest.xlsx`** — human-readable version of the manifest
3. **`corpus/processed/`** — chunked text files with metadata, ready for embedding (gitignored)

The manifest is the only thing committed to GitHub. Raw and processed documents are reproduced locally via the download and processing scripts.
