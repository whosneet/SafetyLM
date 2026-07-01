# SafetyLM — System Architecture

## Overview

SafetyLM v1 is a RAG (Retrieval-Augmented Generation) system. Understanding this architecture is the foundation for every technical decision in the project. This document explains how the pieces fit together, why each component exists, and what the data flow looks like from a user query to a generated response.

---

## What RAG actually means

> **Learning note:** RAG is the most important concept to understand before building anything. Get this right and the rest of the architecture follows logically.

A standard LLM (like Llama or Mistral) has knowledge baked in from its training data. That knowledge has a cutoff date, it doesn't include private or specialised documents, and the model can't tell you where a specific answer came from. It just knows things the way a person knows things — absorbed, not cited.

RAG changes this by splitting the problem into two distinct steps:

**Step 1 — Retrieve:** When a user asks a question, the system searches a curated document database to find the most relevant chunks of text. This is not a keyword search — it's a semantic search using vector embeddings (explained below). The result is a handful of highly relevant document excerpts.

**Step 2 — Generate:** Those retrieved excerpts are injected into the context window of the LLM alongside the user's question. The model then generates a response that is grounded in those documents rather than relying purely on what it memorised during training.

The analogy: instead of asking an expert to answer from memory, you hand them the relevant documents and ask them to reason over what's in front of them. The answer is more reliable and you can check their work.

For SafetyLM, this means:
- The WHS corpus (legislation, codes of practice, guidance) lives in a vector database
- A user asks "what are the PCBU duties for psychosocial hazards in NSW?"
- The retrieval system finds the most relevant chunks from the NSW WHS Act, Safe Work Australia's psychosocial guide, and the Code of Practice
- Those chunks go into the prompt alongside the question
- The LLM generates a response grounded in those specific documents
- The response includes citations back to the source documents

---

## Component map

```
┌─────────────────────────────────────────────────────────────┐
│                        USER QUERY                           │
│         "What are PCBU duties for psychosocial              │
│              hazards under NSW legislation?"                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   QUERY PROCESSING                          │
│   • Jurisdiction detection (NSW flagged from query)         │
│   • Query embedding (converts text → vector)                │
│   • Metadata filter construction (jurisdiction = NSW)       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   VECTOR STORE (Qdrant)                     │
│   • Stores embeddings for all corpus documents              │
│   • Filtered semantic search: NSW documents only            │
│   • Returns top-k most relevant chunks (typically 5–8)      │
│   • Each chunk carries metadata: source, jurisdiction,      │
│     document type, date, URL                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROMPT CONSTRUCTION                        │
│   • System prompt (WHS professional identity + rules)       │
│   • Retrieved chunks injected as context                    │
│   • Original user query appended                            │
│   • Citation instruction included                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASE LLM (local)                         │
│   • Runs on M3 Max via Ollama (Metal)                       │
│   • Generates response grounded in retrieved context        │
│   • Cites specific documents from the injected chunks       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    RESPONSE OUTPUT                          │
│   • Answer grounded in retrieved WHS documents              │
│   • Citations: document title, jurisdiction, section, URL   │
│   • Confidence signal if retrieval was weak                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Component breakdown

### 1. Corpus (the knowledge base)

The raw material. Every public WHS document from AU/NZ regulators, legislation, codes of practice, guidance materials, and the AIHS Body of Knowledge. Stored as structured text after processing.

- **Input:** PDFs, HTML pages, DOCX files from regulator websites
- **Output:** Clean text chunks with metadata attached
- **Where it lives:** `corpus/processed/` (gitignored — too large for GitHub, reproduced via scripts)
- **Detailed design:** [`03-corpus-strategy.md`](03-corpus-strategy.md)

---

### 2. Embeddings (the semantic index)

> **Learning note:** Embeddings are how machines understand meaning rather than just matching keywords.

An embedding model converts a piece of text into a list of numbers (a vector) that captures its semantic meaning. Text with similar meaning produces vectors that are mathematically close to each other, even if the words are different. "PCBU duties" and "person conducting a business or undertaking obligations" would produce similar vectors.

When a user asks a question, it gets converted to a vector too. The retrieval system finds corpus chunks whose vectors are closest to the query vector — those are the semantically relevant documents.

- **Embedding model:** `bge-m3` is the current primary candidate (native dense+sparse, hybrid-ready); `nomic-embed-text` is prototyping-only. *Benchmark-decided — refreshed 2026-06-29.*
- **Vector store:** Qdrant (self-hostable, strong metadata filtering)
- **Detailed design + candidates:** [`04-rag-pipeline.md`](04-rag-pipeline.md), [`02-model-selection.md`](02-model-selection.md)

---

### 3. Retrieval pipeline

The logic layer that takes a query, builds the right search filters, hits the vector store, and assembles the prompt. This is where jurisdictional precision lives — the pipeline detects which jurisdiction is relevant to the query and applies it as a metadata filter before searching.

- **Orchestration framework:** LlamaIndex (better RAG primitives than LangChain for this use case)
- **Two-stage retrieval (refreshed 2026-06-29):** hybrid search retrieves a wide candidate set, then a cross-encoder **reranker** narrows to the top-k for precision.
- **Key design decisions:** chunking strategy, top-k value, metadata filter logic, reranker choice, prompt template
- **Detailed design:** [`04-rag-pipeline.md`](04-rag-pipeline.md)

---

### 4. Base LLM

The language model that generates the final response. For SafetyLM v1, this runs locally on the M3 Max. No API dependency, no per-token cost, full data sovereignty.

- **Candidates (refreshed 2026-06-29):** Qwen3-14B, Qwen3-30B-A3B (MoE), Mistral Small 3.2 24B — all Apache/MIT; benchmark-decided, not locked. (Llama & Gemma 3 excluded on licence grounds.)
- **Runtime:** Ollama (simplest local model serving for this hardware)
- **Selection rationale:** [`02-model-selection.md`](02-model-selection.md)

---

### 5. Evaluation layer

> **Learning note:** Most AI projects skip this and regret it. Without a benchmark, you have no way to know if a change you made improved or degraded the system.

A dataset of 500+ WHS-specific questions with verified ground truth answers. Every time a change is made to the corpus, chunking strategy, retrieval logic, or prompt template, the system is evaluated against this benchmark. This is what allows confident iteration.

- **Format:** Question, expected answer, jurisdiction, document type, hazard category
- **Published independently** on Hugging Face as a standalone dataset
- **Detailed design:** [`05-evaluation.md`](05-evaluation.md)

---

## Data flow summary

```
Raw WHS documents (PDF/HTML)
        │
        ▼ [corpus pipeline]
Cleaned text chunks + metadata
        │
        ▼ [embedding pipeline]
Vector embeddings stored in Qdrant
        │
        ▼ [at query time]
User query → embed query → semantic search with jurisdiction filter
        │
        ▼ [retrieval]
Top-k relevant chunks retrieved
        │
        ▼ [prompt construction]
System prompt + chunks + query assembled
        │
        ▼ [LLM inference]
Response generated and cited
        │
        ▼
User receives grounded, cited WHS answer
```

---

## What v2 adds (for reference, out of scope now)

Fine-tuning sits on top of this architecture, not instead of it. In v2:
- The base LLM is replaced with a fine-tuned version trained on WHS-specific instruction pairs
- The fine-tuned model reasons in ICAM structure, bowtie logic, and critical control language natively
- RAG still runs — the fine-tuned model gains behavioural alignment, RAG provides current knowledge
- LoRA adapters are published so organisations can layer their own incident data on top

The v1 RAG system is also the data collection mechanism for v2 — usage logs and human-reviewed outputs become the fine-tuning training set.
