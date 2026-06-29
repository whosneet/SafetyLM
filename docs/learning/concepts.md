# SafetyLM — Learning Companion

Concepts explained as they become relevant to the build. Each section is tagged to the phase where you'll encounter it. Read ahead if curious, or come back when the phase arrives.

---

## Phase 0 concepts

### Large Language Models — what they actually are

An LLM is a statistical model trained to predict the next token (roughly: word fragment) given a sequence of previous tokens. That's the entire mechanism. The emergent capability — coherent reasoning, language understanding, instruction following — comes from training on enormous volumes of text at sufficient scale.

When you send a message to Claude or ChatGPT, you're not querying a database or running a rules engine. You're running a mathematical function that takes text as input and produces a probability distribution over possible next tokens. It generates responses one token at a time, each token's probability conditioned on everything that came before.

**Parameters** are the numbers the model learned during training. "7 billion parameters" means 7 billion numbers, each storing a tiny fraction of the statistical patterns the model absorbed. More parameters generally means more capacity to represent complex patterns — but also more memory and compute required to run.

**Why this matters for SafetyLM:** The base model has no specific knowledge of AU/NZ WHS legislation. What it has is strong general language capability and some general knowledge about health and safety topics from its training data. RAG adds the specific knowledge at query time.

---

### Tokens

A token is the unit a language model operates on. In English, tokens are roughly word fragments — "safety" might be one token, "reasonably" might be two ("reason" + "ably"). The GPT tokeniser averages about 0.75 words per token, so 100 tokens ≈ 75 words.

**Why this matters for SafetyLM:**
- Context window limits are in tokens, not words
- Llama 3.1 8B has a 128,000 token context window — that's roughly 96,000 words, or about 200 pages of text
- When you retrieve 6 chunks of 512 tokens each, that's 3,072 tokens of context injected into the prompt
- Embedding models also have token limits — `nomic-embed-text` handles 8,192 tokens, which is enough for most legislative sections

---

### Context window

The context window is the maximum amount of text (in tokens) the model can consider at once. Everything outside the context window is invisible to the model — it has no memory of it.

For RAG, this means:
- Your system prompt takes some tokens
- Retrieved chunks take some tokens  
- The user's question takes some tokens
- The generated response takes some tokens
- Everything must fit within the limit

Llama 3.1 8B's 128K context window is generous. In practice, RAG systems rarely need more than 8K–16K tokens of context per query. The 128K limit is a ceiling you won't hit during normal SafetyLM operation.

---

## Phase 1 concepts

### Why text extraction from PDFs is harder than it sounds

Regulators publish legislation and codes of practice as PDFs. PDFs were designed for printing, not for text extraction. The internal structure of a PDF describes how to paint pixels on a page — not how to parse the text semantically.

Problems you'll encounter:
- **Column layout:** A two-column legislative PDF extracts text column-by-column, producing garbled output where left and right columns are interleaved
- **Headers and footers:** "Safe Work Australia | Code of Practice | Page 12" appears in the extracted text of every page
- **Tables:** Extract as a single row of jumbled text rather than structured data
- **Footnotes:** Mixed into the body text at unpredictable points
- **Hyphenated words:** "reason-\nably" across a line break becomes two tokens

The extraction script (`scripts/extract_text.py`) handles these with heuristics. Not perfectly — you'll do a QA pass over the processed chunks and manually fix the worst cases.

**Practical implication:** Budget more time for corpus processing than it initially looks like. The manifest build is straightforward. The extraction and QA is where the effort lives.

---

### Why chunking strategy matters

Imagine a legislative clause that says: "A PCBU must ensure, so far as is reasonably practicable, the physical and psychological health, safety and welfare of workers."

If your chunk boundary falls between "physical and psychological" and "health, safety and welfare", you get two chunks that are independently useless. Neither contains the complete duty statement.

Good chunking:
- Respects sentence and clause boundaries
- Keeps section headings with their content (the heading tells you what the clause is about)
- Uses overlap (the last 64 tokens of chunk N are also the first 64 tokens of chunk N+1) to ensure continuity across boundaries

The LlamaIndex `SentenceSplitter` handles this — it doesn't cut in the middle of sentences. Section heading preservation requires a custom preprocessing step that identifies heading patterns in the extracted text and tags them before chunking.

---

## Phase 2 concepts

### Vector embeddings — what they physically are

An embedding is a list of floating-point numbers — typically 768 or 1,536 numbers. Each number represents a coordinate in a high-dimensional space. Text with similar meaning produces lists of numbers that are close together in that space. Text with different meaning produces numbers far apart.

The `nomic-embed-text` model converts a piece of text into a 768-dimensional vector. When you embed the query "PCBU duties for psychosocial hazards", you get a list of 768 numbers. Qdrant then finds the corpus chunks whose 768-number vectors are mathematically closest to your query vector.

**Why this is powerful:** "Person conducting a business or undertaking obligations for psychological safety" produces a vector close to "PCBU duties for psychosocial hazards" even though the words are completely different. Keyword search would find zero overlap. Semantic search finds the meaning.

**Why this is not magic:** Embeddings capture statistical co-occurrence patterns from training data. They can miss highly specific legislative terminology that doesn't appear in training data, or conflate similar-sounding but legally distinct concepts. This is why hybrid search (semantic + keyword) is used.

---

### Cosine similarity

The mathematical operation Qdrant uses to compare vectors. It measures the angle between two vectors in high-dimensional space. An angle of 0° (cosine similarity = 1.0) means the vectors are identical — perfectly similar text. An angle of 90° (cosine similarity = 0.0) means completely unrelated.

In practice, relevant matches typically score 0.7–0.9. Retrieval typically surfaces chunks above a similarity threshold (e.g. 0.65) rather than just the top-k, to avoid returning irrelevant chunks when no good match exists.

---

### Why Qdrant over a simple Python dictionary

You could store embeddings in a Python dictionary and compare every query vector against every stored vector. For 1,000 chunks, this is fine. For 50,000 chunks, it becomes slow. For 500,000 chunks across a large corpus, it's unusable.

Qdrant uses HNSW (Hierarchical Navigable Small World graphs) — an indexing algorithm that finds approximate nearest neighbours without comparing against every stored vector. Query time stays fast regardless of corpus size. It also supports filtered search natively — filter first, then search only the filtered subset.

---

## Phase 3 concepts

### What LlamaIndex actually does

LlamaIndex is an orchestration framework. It doesn't do any AI work itself — it connects the components that do. Specifically for SafetyLM, it:

1. Takes the query string
2. Calls `nomic-embed-text` to embed it
3. Calls Qdrant with the embedded vector and metadata filters
4. Takes the returned chunks
5. Assembles them with the system prompt into a complete prompt string
6. Calls Llama 3.1 8B via Ollama
7. Returns the generated text

Without LlamaIndex, you'd write this orchestration manually in Python. LlamaIndex saves that work and provides tested retrieval primitives (hybrid search, re-ranking, query decomposition) that you'd otherwise build from scratch.

**Analogy from your background:** LlamaIndex is the integration layer — like a middleware bus that connects the component services (embedding model, vector store, LLM) without those components needing to know about each other.

---

### Prompt construction — why it's engineering, not writing

A RAG prompt has four parts assembled programmatically, not written by hand:

```
[SYSTEM PROMPT]
You are SafetyLM...

[CONTEXT]
SOURCE: Work Health and Safety Act 2011 (NSW) | Section 19 | ...
"A person conducting a business or undertaking must ensure..."

SOURCE: Safe Work Australia Psychosocial Hazards Code | Section 3.2 | ...
"Psychosocial hazards include job demands that exceed a worker's capacity..."

[QUERY]
User: What are the PCBU duties for psychosocial hazards in NSW?

[INSTRUCTION]
Answer based only on the CONTEXT above. Cite your sources.
```

Every time a query runs, this prompt is assembled fresh with different retrieved chunks. The system prompt stays constant. The context block changes with every query. This is why prompt engineering for RAG systems is primarily about:
- How to format retrieved chunks so the LLM understands what they are
- How to instruct the LLM to stay grounded in context and not hallucinate
- How to get consistent citation behaviour across diverse question types

---

## Phase 4 concepts

### RAGAS — how automated evaluation works

RAGAS (Retrieval-Augmented Generation Assessment) is a library that uses a separate LLM (typically GPT-4 or Claude) as a judge to score your RAG system's outputs.

You give RAGAS:
- The user question
- The ground truth answer (from your benchmark dataset)
- The generated answer (from SafetyLM)
- The retrieved context chunks

RAGAS scores four dimensions:
- **Answer correctness:** Does the generated answer match the ground truth? (0–1)
- **Faithfulness:** Is everything in the generated answer supported by the retrieved context? (0–1 — 0 means hallucination)
- **Context precision:** Of the chunks retrieved, what proportion were actually relevant? (0–1)
- **Context recall:** Of the chunks needed to answer, what proportion were actually retrieved? (0–1)

Running RAGAS on 500 questions produces a rigorous, repeatable score. It costs a small amount in API fees (the LLM judge calls) — typically $5–15 AUD for a full benchmark run.

---

### The difference between precision and recall

These are fundamental information retrieval concepts you'll see constantly in this project.

**Precision:** Of what was retrieved, how much was correct?
- High precision = the chunks you retrieved were relevant
- Low precision = you retrieved lots of chunks but many were irrelevant noise

**Recall:** Of what should have been retrieved, how much did you get?
- High recall = you found all the relevant chunks
- Low recall = you missed important documents

For SafetyLM, both matter — but jurisdiction precision is especially critical. Retrieving the wrong jurisdiction's documents with high confidence is worse than retrieving nothing, because the LLM will generate a confident but wrong answer.

**The tradeoff:** Increasing top-k (retrieving more chunks) improves recall but decreases precision. The evaluation benchmark tells you where your current top-k sits on that tradeoff and whether it's calibrated correctly.
