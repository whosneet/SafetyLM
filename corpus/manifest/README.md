# corpus/manifest/

The master catalogue of every source document in the SafetyLM corpus — the **source of truth**
for corpus scope. This is the only corpus artefact committed to git.

**Planned files (Phase 1):**

- `corpus_manifest.csv` — machine-readable catalogue, one row per source document
- `corpus_manifest.xlsx` — human-readable version of the same data

**Each row carries the full metadata schema** (`source_id`, `jurisdiction`, `regulator`,
`document_type`, `document_title`, `url`, `file_format`, `date_published`,
`date_last_reviewed`, `legislative_currency`, `hazard_category`, `industry_relevance`,
`priority_tier`, `pre_harmonisation`, `license_notes`, `notes`). Full field definitions:
`docs/03-corpus-strategy.md`.

**`source_id` format:** `[JURISDICTION]-[CATEGORY]-[SEQUENCE]` — e.g. `FED-COP-001`.

**Rule:** never fabricate a URL or document title. Unverified entries are marked `VERIFY`
and resolved manually before the document is downloaded.
