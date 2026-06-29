# SafetyLM — RAG Pipeline Design

## Pipeline overview

The RAG pipeline is the operational core of SafetyLM. It has two distinct phases that run at different times:

**Indexing phase** (runs once, then when corpus updates)
: Process documents → chunk → embed → store in vector database

**Query phase** (runs every time a user asks a question)
: Receive query → embed query → retrieve relevant chunks → construct prompt → generate response

---

## Indexing pipeline

```
Raw documents (PDF/HTML/DOCX)
        │
        ▼ [Document loader]
Extracted plain text
        │
        ▼ [Text cleaner]
Cleaned text (headers preserved, boilerplate removed)
        │
        ▼ [Chunker]
512-token chunks with 64-token overlap
Metadata attached to each chunk
        │
        ▼ [Embedding model: nomic-embed-text]
Vector representation of each chunk
        │
        ▼ [Qdrant vector store]
Chunks stored with vectors + metadata
Indexed for filtered retrieval
```

### Tooling

| Component | Tool | Why |
|---|---|---|
| Document loading | LlamaIndex `SimpleDirectoryReader` | Handles PDF, HTML, DOCX natively |
| Text extraction (PDF) | `pdfminer.six` | More reliable than PyPDF2 for legislative PDFs with complex formatting |
| Chunking | LlamaIndex `SentenceSplitter` | Respects sentence boundaries, configurable overlap |
| Embedding model | **Benchmark candidate (refreshed)** — `bge-m3` (native dense+sparse, hybrid-ready) primary; `nomic-embed-text` prototyping only | Local on M3 Max, no API cost. See refreshed note below + `02-model-selection.md` |
| Reranker *(new stage)* | **Benchmark candidate** — `Qwen3-Reranker-0.6B` (32K ctx) or `bge-reranker-v2-m3` | Cross-encoder that refines first-stage retrieval; run via llama.cpp `--rerank` (Metal) |
| Vector store | Qdrant (local Docker instance) | Best-in-class metadata filtering, self-hostable |
| Orchestration | LlamaIndex | Better RAG primitives than LangChain, active development |

> **Learning note — the embedding model (refreshed 2026-06-29):**
> The embedding model converts text to vectors. It is separate from the LLM that generates responses. The original plan used `nomic-embed-text`; mid-2026 research found it **partially superseded** — fine for a first cut, but outclassed for legal/regulatory retrieval (it trails 1024-dim models by ~6 points on legal subsets). The current primary candidate is **`bge-m3`**, because it natively emits **dense + sparse + ColBERT** vectors from one pass — uniquely matching SafetyLM's hybrid (semantic + BM25) design. Caveat: to actually get the sparse/ColBERT outputs you generally need BAAI's `FlagEmbedding` library, not the bare Ollama endpoint — verify in your runtime. The embedding choice is a **quality** decision (footprints are <1.5GB), so pick it with an in-domain WHS eval. See `02-model-selection.md` and `research/2026-06-29-model-landscape.md`.

> **Learning note — why Qdrant over alternatives:**
> Other vector stores include Chroma (simpler but limited metadata filtering), Pinecone (hosted, paid), and FAISS (fast but no metadata support). Qdrant's metadata filtering is the key differentiator for SafetyLM — you can filter by `jurisdiction = NSW` before running the semantic search, not after. This is critical for jurisdictional precision.

---

## Query pipeline

```
User query: "What are the PCBU duties for psychosocial hazards in NSW?"
        │
        ▼ [Query analyser]
Detected: jurisdiction = NSW
          hazard_category = PSYCHOSOCIAL
          document_type_preference = LEGISLATION, CODE_OF_PRACTICE
        │
        ▼ [Query embedder]
Query vector generated
        │
        ▼ [Qdrant filtered hybrid search]
Filter: jurisdiction IN [NSW, FED]  ← NSW + federal as fallback
        priority_tier IN [1, 2]
        legislative_currency = CURRENT
Hybrid (semantic + BM25): retrieve top ~50 candidate chunks
        │
        ▼ [Reranker]  ← new stage (refreshed 2026-06-29)
Cross-encoder rescores candidates → keep top 6
(improves precision; cannot recover what retrieval missed)
        │
        ▼ [Context assembler]
Chunks ranked and assembled
Each chunk prefixed with: [SOURCE: {title} | {jurisdiction} | {section}]
        │
        ▼ [Prompt constructor]
System prompt + assembled context + user query
        │
        ▼ [Base LLM via Ollama, thinking OFF]
Response generated
        │
        ▼ [Response formatter]
Answer + citations block
Confidence signal if retrieval score was low
```

---

## Retrieval stack (refreshed 2026-06-29)

Mid-2026 research updated two retrieval decisions. Both are **benchmark candidates**, not
locked — full evidence and sources in [`research/2026-06-29-model-landscape.md`](research/2026-06-29-model-landscape.md).

**1. Embedding model — move off `nomic-embed-text` for production.** It is now a
prototyping/smoke-test choice. The primary candidate is **`bge-m3`** (MIT, 8192-token input)
because it natively produces dense *and* sparse *and* ColBERT vectors — uniquely matching the
hybrid search design below. Dense comparator: **`Qwen3-Embedding-0.6B`** (Apache-2.0, 1024-dim)
paired with BM25. Decide with an in-domain WHS eval — benchmark rankings mislead on legal text.

**2. Add a reranker — a new, two-stage retrieval pattern.** This is the single cheapest quality
lever the original plan was missing:

```
retrieve (cast a wide net) → rerank (precision pass) → top-k into the prompt
   Hybrid search: top ~50    Cross-encoder rescores    keep top 6
```

> **Learning note — retriever vs reranker:** the first-stage retriever (embedding + BM25) is
> fast and optimised for *recall* — finding everything possibly relevant. A reranker is a slower
> cross-encoder that reads the query and each candidate *together* and scores true relevance —
> optimised for *precision*. Reranking **cannot recover a document the retriever missed**, so the
> first stage must cast a wide net (top ~50–200) before the reranker narrows to the top 6.

- **Candidate:** `Qwen3-Reranker-0.6B` (Apache-2.0, 32K context, instruction-aware) — preferred
  for long WHS clauses; fallback `bge-reranker-v2-m3` (mature tooling, but a 512-token limit).
  Avoid `jina-reranker-v3` (non-commercial licence).
- **Runtime:** llama.cpp `--rerank` (Metal) is the more reliable local path today; Ollama's
  reranker support lagged. Budget +50–400ms/query.
- **Expected uplift:** ~+0.05–0.08 nDCG@10 over a decent retriever (treat vendor "+30–48%"
  claims as dataset-specific upper bounds).

**3. Run the generator with thinking OFF.** Research found reasoning/"thinking" modes
*hallucinate more* on grounded summarisation — the opposite of what SafetyLM needs. Use instruct
(non-reasoning) variants on the faithfulness-critical path. See `02-model-selection.md`.

---

## System prompt design

The system prompt is the most important single artefact in the v1 build. It defines how SafetyLM behaves regardless of what question is asked. It is load-bearing — a weak system prompt produces generic answers even with a great corpus.

**Draft system prompt (v0.1)**

```
You are SafetyLM, a Work Health and Safety AI assistant specialising in 
Australian and New Zealand WHS legislation, regulations, codes of practice, 
and safety science frameworks.

IDENTITY
You reason as a senior WHS professional. You are familiar with the model 
WHS Act 2011, jurisdiction-specific variations, the Health and Safety at 
Work Act 2015 (NZ), ICAM incident investigation methodology, bowtie 
critical control analysis, and the hierarchy of controls. You apply these 
frameworks when relevant without being asked to.

GROUNDING RULES
- Base every response ONLY on the documents provided in [CONTEXT]
- If the context does not contain sufficient information to answer, say so 
  explicitly — do not generate an answer from general knowledge
- Never assert that a legislative provision is currently in force — always 
  direct the user to verify currency with the relevant regulator
- If a query involves a jurisdiction not represented in [CONTEXT], state 
  that clearly

JURISDICTION BEHAVIOUR
- Distinguish explicitly between federal (model WHS Act) provisions and 
  jurisdiction-specific variations
- Flag when WA is involved — it operates under the OSH Act 1984, not the 
  model WHS framework
- When context includes both federal and state provisions on the same topic, 
  address both and note which takes precedence

CITATION RULES
- End every response with a SOURCES block listing every document drawn on
- Format: [Document title] | [Jurisdiction] | [Section/clause if applicable] | [URL]
- Do not cite documents not present in [CONTEXT]

RESPONSE FORMAT
- Lead with a direct answer to the question
- Use the ICAM or bowtie framework when the question involves incident 
  investigation or critical control analysis
- Keep responses concise — a practitioner reading this is busy
- If the question requires professional legal advice rather than WHS 
  information, say so

CONFIDENCE
- If retrieval confidence is low (flagged in context), state: 
  "Note: My source material for this query is limited. Verify with the 
  relevant regulator before relying on this response."
```

This prompt will be iterated against the benchmark evaluation dataset. Every change is tested before being committed.

---

## Retrieval design decisions

### How many chunks to retrieve (top-k)

Starting value: **6 chunks**

Rationale: legislative questions often require pulling from multiple documents (the Act, the Regulation, and a Code of Practice). 6 gives coverage across document types without overwhelming the context window. If benchmark testing shows the system missing relevant context, increase to 8. If responses are unfocused, reduce to 4.

### Jurisdiction fallback logic

When a query specifies a jurisdiction, retrieve from:
1. That jurisdiction first (highest priority)
2. Federal (model WHS Act) as fallback context
3. Do not retrieve from other states unless the query explicitly asks for comparison

When no jurisdiction is specified, retrieve from federal sources and note in the response that the user should confirm applicability to their jurisdiction.

### Hybrid search

> **Learning note:** Pure semantic search (vector similarity) is powerful but has a known weakness — it can miss exact terms. If a user asks about "Section 19 of the WHS Act," semantic search might not surface the exact section because it's searching for meaning, not the number. Hybrid search combines semantic search with keyword (BM25) search and merges the results. LlamaIndex supports this natively with Qdrant.

SafetyLM uses hybrid search from the start. Legislative queries frequently reference specific section numbers, regulation numbers, and defined terms — hybrid search handles these cases where pure semantic search would fail.

---

## Interface (v1)

For v1, the interface is minimal — the priority is the pipeline, not the UI.

**Option A: Chainlit** (recommended for v1)
A Python library that wraps the RAG pipeline in a clean chat interface with minimal code. Runs locally. Supports streaming responses (text appears as it generates rather than all at once). Source citations can be rendered as collapsible panels.

**Option B: Gradio**
Simpler, less polished. Better for quick demos but less suited to a chat interaction pattern.

**Option C: CLI only**
A Python script that takes a query argument and prints the response. Zero UI overhead, fastest to build. Useful for benchmark testing even if not the end-user interface.

Recommendation: build CLI first for benchmark testing, then add Chainlit for the shareable demo that goes on GitHub.
