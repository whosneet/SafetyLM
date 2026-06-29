# Research Snapshot — Local Model Landscape for SafetyLM (2026-06-29)

> **What this is.** A point-in-time research briefing on the open-weight LLM, embedding,
> and reranker landscape for SafetyLM's local RAG stack, captured **2026-06-29**. It is the
> evidence base behind the refreshed [`02-model-selection.md`](../02-model-selection.md).
>
> **How it was produced.** Five parallel web-research agents (dense LLMs, MoE + RAG
> benchmarks, embeddings, rerankers, M3 Max performance) followed by a synthesis pass.
> Sources are cited inline with dates.
>
> **Trust level — read before relying on this.** This was a single research pass; it did
> **not** go through adversarial cross-verification. Model *existence, licences, context
> windows, and Ollama availability* are primary-sourced and trustworthy. Specific *benchmark
> numbers* — especially for models released after January 2026 (Gemma 4, Qwen3.5/3.6,
> Mistral Small 4, Ministral 3, DeepSeek-V4) — are largely secondary-blog sourced and should
> be treated as **indicative, not settled**. The §7 "Confidence & gaps" section is the
> honest accounting. **Nothing here is a locked decision — it is input to a Phase 4 benchmark.**

---

## 0. The two changes since January 2026 that matter most

1. **The Gemma licence flipped.** Gemma 3 ships under the restrictive **Gemma Terms of Use**,
   whose Prohibited Use Policy includes restrictions touching **legal/medical
   professional-practice content**, plus a flow-down obligation and Google's unilateral
   remote-restriction right — a genuine problem for a legal product. **Gemma 4 (2 Apr 2026)
   moved to clean Apache-2.0.** The single most consequential licensing change for SafetyLM.
   (Sources: [Gemma Terms](https://ai.google.dev/gemma/terms);
   [WCR.legal analysis](https://wcr.legal/google-gemma-license-risks/);
   [TechCrunch, Mar 2025](https://techcrunch.com/2025/03/14/open-ai-model-licenses-often-carry-concerning-restrictions/);
   [Google Gemma 4 blog, Apr 2026](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/))
2. **Ollama is switching its Apple-Silicon engine from llama.cpp to MLX (announced
   30 Mar 2026).** MLX is meaningfully faster for decode on Apple Silicon, but the initial
   MLX runner supported only ~6 architectures and sources disagree on version/auto-activation
   specifics — **verify on your own machine.**
   ([yage.ai, 2026-03-31](https://yage.ai/share/mlx-apple-silicon-en-20260331.html))

> **Dense-vs-MoE trap (post-Jan-2026):** "27B"-labelled models are no longer reliably dense.
> Qwen3.5-27B is hybrid-MoE; Qwen3.6-27B is fully dense; Gemma 4's 26B is MoE while its 31B
> is dense; Mistral Small 4 and all Llama 4 are MoE. **Verify architecture per model** before
> sizing.

---

## 1. Current open-weight LLMs 7–32B (dense + MoE)

Memory rule of thumb (64GB Mac → ~50–54GB usable for all AI processes after OS/headroom):
Q4_K_M ≈ 0.55–0.6GB per 1B **total** params; Q8 ≈ ~1.1GB/1B. For MoE, **total** params drive
memory, **active** params drive speed.

### Dense models (the licence-clean core for SafetyLM)

| Model | Params | Licence | Native ctx | Ollama | Notes (RAG lens) |
|---|---|---|---|---|---|
| **Qwen3-32B** | 32B | **Apache-2.0** | 128K | `qwen3:32b` | Mature; thinking toggle, tool calling, structured output |
| **Qwen3-14B** | 14B | **Apache-2.0** | 128K | `qwen3:14b` | Solid mid-size; same toolchain as 32B |
| **Mistral Small 3.2** | 24B | **Apache-2.0** | 128K | `mistral-small3.2` (~15GB) | Explicitly tuned for instruction-following + function-calling |
| **Qwen3.6-27B** ⚠ post-cutoff | 27B dense | **Apache-2.0** | 262K | community GGUF; official lib catching up | Newest strong dense ~27B |
| **Gemma 4 31B** ⚠ post-cutoff | 31B | **Apache-2.0** (now clean) | 256K | `gemma4:31b` (~20GB) | Google quality + permissive licence at last |
| **Ministral 3 (14B/8B)** ⚠ post-cutoff | 14B/8B | **Apache-2.0** | 128K | 3B official; 14B/8B community GGUF | Verify tag |
| **Phi-4-reasoning** | 14B | **MIT** | **32K only** | `phi4-reasoning:14b` | Short context is the catch for citation-heavy RAG |
| **Phi-4** | 14B | **MIT** | **16K only** | `phi4` | Shortest context here |
| **Mistral NeMo** | 12B | **Apache-2.0** | 128K | `mistral-nemo:12b` | Older (mid-2024) clean fallback |
| DeepSeek-R1-Distill-Qwen 32B/14B | 32B/14B | **MIT** (Qwen2.5 base) | ~128K | `deepseek-r1:32b`/`:14b` | Verbose `<think>`; weaker structured-output discipline |

> Avoid **Llama-based** DeepSeek distills (8B/70B) — they inherit the Llama licence.

### MoE models (fit-on-64GB analysis)

| Model | Total / Active | Licence | Ollama | 64GB feasibility |
|---|---|---|---|---|
| **Qwen3-30B-A3B** (Instruct-2507) | 30B / 3B | **Apache-2.0** | `qwen3:30b` | **Excellent** — ~18–20GB Q4, full ctx. Reference local-RAG MoE |
| **Qwen3.6-35B-A3B** ⚠ post-cutoff | 35B / 3B | **Apache-2.0** | `qwen3.6:35b-a3b` | **Excellent** — ~20GB Q4 |
| **gpt-oss-20b** | 21B / 3.6B | **Apache-2.0** | `gpt-oss:20b` (~14GB) | **Excellent** — runs in 16GB; reasoning model |
| **Gemma 4 26B-A4B** ⚠ post-cutoff | 25.2B / ~3.8B | Apache-2.0 (Gemma 4 terms) | listed | **Excellent** — ~15–17GB Q4; specs secondary-sourced |
| **GLM-4.5-Air** | 106B / 12B | **MIT** | yes | **Borderline** — ~58–62GB Q4 |
| **gpt-oss-120b** | 117B / 5.1B | **Apache-2.0** | yes | **Borderline** — ~63–65GB |
| **Llama 4 Scout** | 109B / 17B | Llama 4 Community | yes (~55GB) | Borderline + **licence-excluded** |
| Mixtral 8x7B (legacy) | 47B / 13B | Apache-2.0 | `mixtral:8x7b` | Good fit (~26GB) but outclassed by Qwen3-30B-A3B |

**Excluded on licence grounds:** all **Llama** models (Community Licence) and **Gemma 3**
(Gemma Terms, legal/medical-practice restriction).

---

## 2. RAG-quality standings (cited benchmarks)

**2.1 Instruction-following — IFEval / IFBench.** IFEval is saturating >0.90 so it no longer
discriminates well; the harder IFBench is topped by closed models. **Takeaway: Qwen3.x is the
safest instruction-following default; Mistral Small 3.2 is purpose-tuned for it.**
([IFEval leaderboard](https://llm-stats.com/benchmarks/ifeval), updated 2026-06-29;
[IFBench / Artificial Analysis](https://artificialanalysis.ai/evaluations/ifbench))

**2.2 Faithfulness / low hallucination — Vectara HHEM** (updated 2026-05-11,
[GitHub](https://github.com/vectara/hallucination-leaderboard)). Lower hallucination = better.
Open 7–32B: Gemma-3 12B **4.4%**, Qwen3-8B **4.8%**, Mistral Small 2501 5.1%, Qwen3-14B 5.4%,
Qwen3-32B 5.9%, Gemma-3 27B 7.4%. **Two decision-shaping findings:**
1. **Bigger is not more faithful** in grounded summarisation (8B beats 32B; 12B beats 27B).
2. **Reasoning mode hallucinates MORE** — on Vectara's harder next-gen benchmark
   ([19 Nov 2025](https://www.vectara.com/blog/introducing-the-next-generation-of-vectaras-hallucination-leaderboard))
   reasoning models all exceed 10%. **Run instruct/non-reasoning variants with "thinking" OFF
   on the faithfulness-critical path.** Strongest cross-cutting signal in the briefing.

**2.3 Long-context — RULER / LongBench (weakest-evidenced section).** Advertised windows
overstate usable context badly (models reliably use ~50–65% of claimed length).
**Qwen3.x** is the most practical long-context choice in this tier. No clean cross-model RULER
table for 7–32B open models at 128K exists — **verify effective context for your model+quant
on your own NIAH/RULER run.** Quantization degrades long-context fidelity further.

**2.4 Structured output / tool use.** Qwen3.x (native structured-output + tool-calling),
Mistral Small 3.2 (hardened function-calling), gpt-oss (native tool-use) are strongest.
**Avoid DeepSeek R1 distills** for strict JSON/citation formatting without extra scaffolding.

**2.5 End-to-end RAG-faithfulness.** **No authoritative current leaderboard ranks 7–32B
generators head-to-head on end-to-end RAG faithfulness.** Vectara HHEM is the best-maintained
proxy. RAGTruth is for training detectors, not ranking generators.

> **Evidence flag:** Qwen3.5/3.6 and Gemma 4 per-benchmark figures come substantially from
> secondary blogs / HF card titles. Existence/specs corroborated by primary cards; treat
> specific benchmark numbers as indicative/unverified.

---

## 3. Local embedding models for hybrid retrieval

*MTEB v1 (legacy), MTEB v2, and MMTEB (multilingual) are **not** directly comparable — do not
rank across benchmarks by raw score.*

| Model | Standing | Dims | Max tokens | Native sparse? | Licence | Ollama |
|---|---|---|---|---|---|---|
| **BGE-M3** | "practical default" for legal | 1024 | **8192** | **YES — dense + sparse + ColBERT** | **MIT** | `bge-m3` (dense-only via API ⚠) |
| **Qwen3-Embedding-8B** | #1 MMTEB at release (Jun 2025) | ≤4096 | 32K | No | Apache-2.0 | `:8b` |
| **Qwen3-Embedding-4B/0.6B** | 69.45 / 64.33 MMTEB | ≤2560 / ≤1024 | 32K | No | Apache-2.0 | `:4b` / `:0.6b` |
| **Snowflake Arctic-embed-l-v2.0** | ~55.6 NDCG@10 BEIR | 1024 | **8192** | No | Apache-2.0 | `snowflake-arctic-embed2` |
| **mxbai-embed-large-v1** | 64.68 MTEB (legacy) | 1024 | **512 only** ⚠ | No | Apache-2.0 | `mxbai-embed-large` |
| **nomic-embed-text-v1.5** | 62.28 MTEB (legacy) | 768 | 8192 | No | Apache-2.0 | `nomic-embed-text` |
| **nomic-embed-text-v2-moe** | beats v1.5 BEIR/MIRACL | 768 | 512–2048 | No | Apache-2.0 | `nomic-embed-text-v2-moe` |
| **EmbeddingGemma-300M** | #1 open <500M | 768 | 2048 | No | **Gemma Terms (not OSI)** ⚠ | `embeddinggemma:300m` |

**⚠ mxbai's 512-token cap is disqualifying for legal** — clauses routinely exceed 512 tokens.
**⚠ EmbeddingGemma's Gemma licence** is a compliance flag for a legal product.

**Verdict — is nomic-embed-text still reasonable in mid-2026?** **Partially superseded —
usable but clearly outclassed for serious legal retrieval; do not pick it as primary.** A 2026
source reports v1.5 trailing 1024-dim models by **~6 points on legal subsets specifically**.
Fine for a first cut / smoke test, not the production retrieval pick.
([legal-RAG guidance](https://www.promptquorum.com/power-local-llm/best-embedding-models-local-rag-2026))

**Hybrid caveat:** **BGE-M3 is essentially the only mainstream local model that natively emits
dense + sparse + ColBERT.** BUT Ollama's `bge-m3` endpoint and Qdrant FastEmbed have
historically returned **dense vectors only** — to get sparse + ColBERT you generally need
BAAI's **`FlagEmbedding`** library, not the bare Ollama endpoint. **Verify in your runtime.**

**Benchmark ≠ legal reality:** on a real contract eval, MTEB top-3 models ranked 5th/7th/2nd
in-domain while a lower-ranked model won ([arXiv 2510.06999](https://arxiv.org/pdf/2510.06999)).
**Run an in-domain eval on your own labelled WHS queries before committing.**

---

## 4. Local rerankers

| Model | Size | Licence | Context | Quality | Notes |
|---|---|---|---|---|---|
| **bge-reranker-v2-m3** | ~568M | **Apache-2.0** | **512** | MTEB-R 57.03 | Safe multilingual default; MLX port; 512-tok limit |
| **Qwen3-Reranker-0.6B** | 596M | **Apache-2.0** | **32K** | **MTEB-R 65.80** | Best permissive small; instruction-aware; Ollama support immature |
| **Qwen3-Reranker 4B/8B** | 4B/8B | **Apache-2.0** | 32K | higher | Slow: 4B >1s/query |
| **mxbai-rerank-large-v2** | 1.5B | **Apache-2.0** | 8K | BEIR 57.49 | Fast; beats Cohere 3.5 / Voyage-2 |
| **jina-reranker-v3** | 597M | **CC-BY-NC-4.0** ⚠ | 131K | BEIR 61.94 (best small) | **Non-commercial — likely a blocker** |
| **Ettin Reranker (150M–1B)** ⚠ post-cutoff | 17M–1B | **Apache-2.0** | 8192 | NanoBEIR ≤0.724 | **EN only**; best param-efficiency (May 2026) |

**How much does reranking help / cost?** Typical uplift **~+0.05–0.08 nDCG@10** over a decent
retriever (vendor claims of +28–48% are dataset-specific upper bounds). **Reranking improves
precision, not recall** — it cannot recover documents the retriever missed; set first-stage
top-k high (50–200), rerank down to top-5/10. Latency **+50–400ms/query**. On Apple Silicon,
**llama.cpp `--rerank` (Metal) is the more reliable local path** today (Ollama reranker support
lagged). Sources: [Qwen3-Reranker](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B);
[bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3);
[mxbai-rerank-v2](https://www.mixedbread.com/blog/mxbai-rerank-v2).

---

## 5. M3 Max 64GB practical performance

**Governing fact:** M3 Max ≈ **400 GB/s** memory bandwidth; decode is bandwidth-bound.
**⚠ Most fresh 2026 benchmarks are M4/M5 — treat M3 Max as ~equal to, or 5–15% below, M4 Max
for decode.** Usable AI memory: **~50–54GB** after OS reserve.

**Memory (weights only; add KV cache + 2–4GB context headroom):**

| Size | Q4_K_M | Q8_0 | MLX 4-bit |
|---|---|---|---|
| 7–8B | ~5GB | ~8–8.5GB | ~4.5–5GB |
| 13–14B | ~8–9GB | ~14–15GB | ~8GB |
| 24B | ~13.4GB | ~25GB | ~13GB |
| 32B | ~18–20GB | ~34GB | ~18GB |
| MoE 30B-A3B | ~17–18GB | ~32GB | ~17GB |

**Tokens/sec (decode, single-stream, Q4):** 7–8B **45–55**; 13–14B **~30**; 24–32B **~25–35**;
**MoE 30B-A3B ~90–130 (extrapolated from M4 — no direct M3 Max figure)**; 70B ~7.5 (needs
128GB, not usable). Q4_K_M ≈ 95–98% of full precision.

**Runtime — MLX vs llama.cpp:** MLX is ~2× llama.cpp on 8B/14B decode but **weaker at prefill /
long context — directly relevant to RAG** (which stuffs large retrieved chunks into the prompt).
At 30K+ context MLX decode ran ~50% slower than llama.cpp+FlashAttention.
**Recommendation: prefer MLX for decode, but benchmark your own prefill at realistic RAG prompt
lengths — if you routinely exceed ~5–8K context, llama.cpp + FlashAttention may win end-to-end.**

**Concurrent stack on 64GB:** OS+apps ~10GB; embedding model 0.2–0.7GB; Qdrant ~0.5–4GB;
KV cache 2–4GB → **~33–50GB remaining for the LLM**. Plenty of headroom for a 32B dense Q4 or
30B-A3B MoE Q4 alongside the full retrieval stack.

---

## 6. Recommended benchmark shortlist — *benchmark these, do not lock*

All licence-clean (Apache-2.0 / MIT), all fit comfortably on M3 Max 64GB alongside Qdrant +
embeddings. Run them with **thinking/reasoning OFF** for the faithfulness-critical path (§2.2).

### LLMs (benchmark head-to-head)

| Role | Model | Why | Licence / ctx | Footprint (Q4) | M3 Max tok/s |
|---|---|---|---|---|---|
| **~14B dense** | **Qwen3-14B** (`qwen3:14b`) | Best-evidenced clean-licence 14B; native structured output; strong faithfulness in the Qwen3 instruct line | Apache-2.0 / 128K | ~8–9GB | ~30 |
| **~24–32B / MoE** | **Qwen3-30B-A3B** (`qwen3:30b`) — MoE pick; also try **Mistral Small 3.2 24B** (`mistral-small3.2`) as a dense comparator | 64GB sweet spot: ~30B quality at ~3B speed, 256K ctx; Mistral Small purpose-tuned for instruction-following | Apache-2.0 / 256K | ~17–18GB | ~90–130 (verify) |
| **Small baseline** | **gpt-oss-20b** (`gpt-oss:20b`) or **Qwen3-8B** (top Vectara faithfulness 4.8%) | Clean floor to measure RAG uplift against | Apache-2.0 / 128K | ~14GB | ~45–60 |

Also keep **vanilla Llama 3.1 8B** as the **no-RAG floor baseline** for the eval (per
`05-evaluation.md`) — to measure how much the corpus + retrieval add, not as a deployment pick.

**Optional newer dense ~27–31B (verify at build):** Qwen3.6-27B (fully dense, Apache) or
Gemma 4 31B (`gemma4:31b`, now Apache) — post-Jan-2026, benchmark-numbers-unverified; upside
experiments, not the baseline.

> **Why not the obvious options:** Gemma-3 12B posts the best Vectara faithfulness but is
> **licence-excluded** (legal-practice restriction) — use Gemma 4 or a small Qwen3 instruct.
> Phi-4 (MIT) is tempting on licence but **16–32K context** constrains citation-heavy RAG.
> DeepSeek R1 distills (MIT) hurt structured-output discipline.

### Retrieval

- **Embedding — primary: BGE-M3** (MIT, 8192 ctx, native dense + sparse + ColBERT — uniquely
  satisfies the hybrid requirement). **Run via `FlagEmbedding`, not the bare Ollama endpoint,
  to get sparse + ColBERT.** Dense comparator: **Qwen3-Embedding-0.6B** (Apache, 1024-dim, 32K)
  + BM25. **Do not** default to nomic for production. Embedding footprints are tiny (<1.5GB) —
  it's a quality decision, so **pick it with an in-domain WHS eval**.
- **Reranker — primary: Qwen3-Reranker-0.6B** (Apache, 32K ctx, MTEB-R 65.80) via
  llama.cpp `--rerank` (Metal). Fallback: **bge-reranker-v2-m3** (mature, but 512-tok limit).
  **Avoid jina-reranker-v3** (non-commercial). First-stage top-k 50–200 → rerank to top-5/10.

---

## 7. Confidence & gaps

**High confidence (primary-sourced):** model existence, param counts, licences, context
windows, Ollama availability; **Gemma 3 = restricted / Gemma 4 = Apache-2.0**; Llama Community
Licence exclusion; Vectara HHEM ordering + the reasoning-hallucinates-more finding; MLX decode
advantage + prefill/long-context weakness; mxbai 512-tok cap; BGE-M3 native sparse; nomic
768-dim limitation.

**Medium / thin / fast-moving — verify before locking:** Qwen3.5/3.6 and Gemma 4 per-benchmark
numbers (secondary); long-context rankings (§2.3, weakest); no authoritative end-to-end RAG
generator leaderboard; M3 Max MoE decode (extrapolated from M4); Qdrant-on-Mac / KV-cache GB
estimates; exact Ollama tags for the newest community-GGUF-led releases; reranker uplift
figures (secondary); Ollama→MLX engine switch specifics.

**Post-January-2026 releases referenced (all flagged ⚠; verify independently):** Ministral 3
(Dec 2025); Qwen3.5 (Feb 2026); Mistral Small 4 (Mar 2026); Ollama→MLX switch (Mar 2026);
Gemma 4 incl. 26B-A4B (Apr 2026); Qwen3.6-27B + 35B-A3B (Apr 2026); DeepSeek-V4 (Apr 2026);
Ettin Reranker (May 2026).

**The one recommendation with no caveat:** whatever you pick, **validate it on a labelled set
of real AU/NZ WHS queries.** Public benchmarks will not reliably predict in-domain WHS
performance. **Benchmark the shortlist; do not lock from this document.**
