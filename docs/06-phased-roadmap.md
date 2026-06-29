# SafetyLM — Phased Roadmap

Phases are sequential. Each phase has clear acceptance criteria — move to the next phase only when those criteria are met. Time estimates are omitted deliberately; this project runs at your pace alongside full-time work.

---

## Phase 0 — Planning and documentation ← current

**Goal:** Produce a complete project plan that serves as a persistent brief for every Claude Code session. No code written, no corpus collected.

**Why this phase exists:**  
Without documented decisions, every technical session starts with re-explaining context. These docs are the memory layer for the project — feed them into Claude Code at the start of each session and it has full context without re-prompting.

**Deliverables:**
- [x] README.md — project overview and repo structure
- [x] docs/00-vision.md — goals, users, success criteria
- [x] docs/01-architecture.md — system design and component map
- [x] docs/02-model-selection.md — hardware-matched model comparison
- [x] docs/03-corpus-strategy.md — source taxonomy and metadata schema
- [x] docs/04-rag-pipeline.md — pipeline design and tooling decisions
- [x] docs/05-evaluation.md — benchmark design and scoring methodology
- [x] docs/06-phased-roadmap.md — this document
- [ ] docs/07-distribution.md — launch strategy
- [ ] docs/08-governance.md — licensing and contribution framework

**Acceptance criteria:**
- [ ] All docs complete and internally consistent
- [ ] A new Claude Code session can be started with these docs as context and immediately produce useful output without further explanation
- [ ] You can explain the architecture and each phase to a non-technical colleague

---

## Phase 1 — Corpus build

**Goal:** Produce a complete, structured manifest of every AU/NZ WHS document in scope, then download and process the Tier 1 corpus.

**What you are building:**
A spreadsheet (CSV + XLSX) cataloguing every source document, followed by a pipeline that downloads and processes those documents into clean text chunks ready for embedding.

**Why before the pipeline:**  
You cannot build a RAG system without knowing what's going in it. The manifest also forces explicit decisions about scope, licensing, and metadata structure before they become expensive to change.

**Tasks:**
- [ ] Build corpus manifest (Claude Code session using the corpus manifest prompt)
- [ ] Validate and resolve all VERIFY-flagged URLs manually
- [ ] Write document download script (`scripts/download_corpus.py`)
- [ ] Write PDF/HTML text extraction script (`scripts/extract_text.py`)
- [ ] Write chunking script with metadata attachment (`scripts/chunk_corpus.py`)
- [ ] Process all Tier 1 documents through the pipeline
- [ ] Manual QA: spot-check 20 processed chunks for quality

**Acceptance criteria:**
- [ ] Manifest contains minimum 150 documents across all Tier 1 jurisdictions
- [ ] All Tier 1 documents downloaded and stored in `corpus/raw/`
- [ ] All Tier 1 documents processed into chunks in `corpus/processed/`
- [ ] Each chunk carries complete metadata (all fields from schema populated or explicitly NULL)
- [ ] WA documents are flagged `pre_harmonisation: true`

**What you will learn this phase:**
- How to write and run Python scripts in a terminal
- How PDF text extraction works and why it's messier than it sounds
- Why metadata design decisions made in Phase 0 either pay off or cause pain here

---

## Phase 2 — Embedding and vector store

**Goal:** Convert the processed corpus into vector embeddings and load them into a Qdrant vector database. Verify that semantic search is returning sensible results.

**What you are building:**
The retrieval layer. By the end of this phase, you can type a query and get back the top 6 most relevant corpus chunks with their metadata.

**Why this phase is separate from Phase 3:**  
Indexing is a one-time (or periodic) operation. Querying is real-time. Separating them means you can rebuild the index without touching the query pipeline, and vice versa.

**Tasks:**
- [ ] Install and configure Qdrant locally (Docker — one command)
- [ ] Install Ollama and pull `nomic-embed-text` embedding model
- [ ] Write embedding pipeline (`embeddings/embed_corpus.py`)
- [ ] Run embedding pipeline on Tier 1 processed corpus
- [ ] Write a simple retrieval test script — hardcode 10 test queries, print top-3 results
- [ ] Validate retrieval: do the returned chunks make sense for each query?
- [ ] Test jurisdiction filtering: NSW query should not surface VIC-specific documents

**Acceptance criteria:**
- [ ] Qdrant running locally with all Tier 1 chunks indexed
- [ ] Test retrieval script returns sensible top-3 for 9 of 10 test queries
- [ ] Jurisdiction filter works correctly on 10/10 jurisdiction-specific test queries
- [ ] Retrieval latency under 500ms per query on M3 Max

**What you will learn this phase:**
- What vector embeddings physically are (you'll see the actual numbers)
- How metadata filtering works in a vector store
- Why retrieval quality is its own engineering problem separate from generation quality

---

## Phase 3 — RAG pipeline and system prompt

**Goal:** Connect retrieval to the LLM and produce a working end-to-end SafetyLM response from a natural language query.

**What you are building:**
The full pipeline — query in, grounded WHS answer with citations out. First working version of SafetyLM.

**Tasks:**
- [ ] Install Ollama and pull `llama3.1:8b` model
- [ ] Write LlamaIndex RAG orchestration (`rag/pipeline.py`)
- [ ] Implement hybrid search (semantic + BM25 keyword)
- [ ] Implement jurisdiction detection from query
- [ ] Write system prompt v0.1 (template in `04-rag-pipeline.md`)
- [ ] Write CLI interface (`rag/query.py` — takes query as argument, prints response)
- [ ] Manual test: 20 informal queries covering all question categories
- [ ] Iterate system prompt based on failure patterns observed

**Acceptance criteria:**
- [ ] End-to-end query → response working for all question categories
- [ ] Every response includes a SOURCES block with at least one citation
- [ ] System correctly identifies and flags when retrieval confidence is low
- [ ] No responses assert legislative currency as fact
- [ ] Jurisdiction detection correct for 18 of 20 manual test queries

**What you will learn this phase:**
- How LlamaIndex orchestrates the retrieval and generation steps
- Why the system prompt is the most iterated artefact in RAG development
- How hybrid search differs from pure semantic search in practice

---

## Phase 4 — Benchmark evaluation

**Goal:** Build the 500-question benchmark dataset, run it against SafetyLM and the baselines, and produce a published evaluation report.

**What you are building:**
The credibility layer. This phase produces the evidence that SafetyLM actually works, and the dataset that others can use independently.

**Tasks:**
- [ ] Build benchmark dataset — 500 questions across all categories
- [ ] Validate all ground truth answers against primary sources
- [ ] Run benchmark against: vanilla Llama 3.1 8B (no RAG), prompted Llama 3.1 8B (no RAG), SafetyLM
- [ ] Score using RAGAS for factual categories
- [ ] Manual rubric scoring for reasoning categories (sample of 50)
- [ ] Produce evaluation report summarising results
- [ ] Identify top failure patterns and feed back into Phase 3 iteration
- [ ] Publish dataset to Hugging Face with dataset card

**Acceptance criteria:**
- [ ] 500 questions built and validated
- [ ] SafetyLM outperforms vanilla Llama on legislative interpretation by >30 percentage points
- [ ] Jurisdictional accuracy >85% across the benchmark
- [ ] Dataset published on Hugging Face
- [ ] Evaluation scripts published in `eval/`

**What you will learn this phase:**
- How RAGAS evaluation works in practice
- How to interpret retrieval metrics (precision vs recall tradeoffs)
- What "hallucination" looks like in a scored context

---

## Phase 5 — Interface and public launch

**Goal:** Wrap SafetyLM in a usable chat interface, finalise documentation, and publish to GitHub.

**What you are building:**
The public-facing artefact. After this phase, SafetyLM exists as a real open-source project that someone else can clone and run.

**Tasks:**
- [ ] Build Chainlit chat interface (`rag/app.py`)
- [ ] Implement streaming response (text appears token by token, not all at once)
- [ ] Implement citation panel (source documents shown alongside response)
- [ ] Write `CONTRIBUTING.md` — how others can contribute corpus additions, evaluation questions, bug fixes
- [ ] Write `LIMITATIONS.md` — what SafetyLM gets wrong, known failure modes, what it should not be used for
- [ ] Write installation guide (`docs/INSTALL.md`) — step by step for someone with basic technical literacy
- [ ] Finalise all plan docs (this document and remaining docs in `docs/`)
- [ ] GitHub repo polish: topics, description, social preview
- [ ] Hugging Face model card (if benchmark results justify it)
- [ ] LinkedIn / AIHS community announcement

**Acceptance criteria:**
- [ ] Chainlit interface runs locally with `python rag/app.py`
- [ ] A WHS practitioner with no AI background can follow the install guide and get SafetyLM running
- [ ] GitHub repo is public with all documentation complete
- [ ] README accurately describes what SafetyLM does and does not do

---

## Phase 6 — v2 planning (future, out of scope now)

Record decisions here as they emerge during v1 build. Don't build v2 until v1 is validated.

Anticipated v2 scope:
- Fine-tuning pipeline on WHS-specific instruction pairs
- LoRA adapter training and publishing
- Synthetic training data generation from v1 RAG outputs
- Expanded Tier 2 and Tier 3 corpus coverage
- Multi-turn conversation support
- Possible API endpoint for third-party integration
