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
| Embedding model | `nomic-embed-text` via Ollama | Runs locally on M3 Max, strong performance, no API cost |
| Vector store | Qdrant (local Docker instance) | Best-in-class metadata filtering, self-hostable |
| Orchestration | LlamaIndex | Better RAG primitives than LangChain, active development |

> **Learning note — why nomic-embed-text for embeddings:**
> The embedding model converts text to vectors. It's separate from the LLM that generates responses. `nomic-embed-text` is an open-source embedding model that runs locally, supports 8192 token input (handles long legislative clauses), and benchmarks competitively against OpenAI's embedding models. Running it locally means no API cost and no data leaving your machine.

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
        ▼ [Query embedder: nomic-embed-text]
Query vector generated
        │
        ▼ [Qdrant filtered search]
Filter: jurisdiction IN [NSW, FED]  ← NSW + federal as fallback
        priority_tier IN [1, 2]
        legislative_currency = CURRENT
Semantic search: top 6 chunks by vector similarity
        │
        ▼ [Context assembler]
Chunks ranked and assembled
Each chunk prefixed with: [SOURCE: {title} | {jurisdiction} | {section}]
        │
        ▼ [Prompt constructor]
System prompt + assembled context + user query
        │
        ▼ [Llama 3.1 8B via Ollama]
Response generated
        │
        ▼ [Response formatter]
Answer + citations block
Confidence signal if retrieval score was low
```

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
