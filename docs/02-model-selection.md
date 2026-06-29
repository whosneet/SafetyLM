# SafetyLM — Base Model Selection

> **Status: refreshed 2026-06-29.** This document was originally written in 2024 around
> Llama 3.1 8B. It has been updated to the mid-2026 landscape. **Nothing here is locked** —
> the base model, embedding model, and reranker are *pluggable components* chosen by the
> Phase 4 benchmark, not by this document. The evidence base (with sources and confidence
> flags) is the research snapshot: [`research/2026-06-29-model-landscape.md`](research/2026-06-29-model-landscape.md).
>
> **Why "don't lock":** in a RAG system the model is swappable behind the pipeline. The right
> answer comes from running candidates against SafetyLM's own benchmark on real AU/NZ WHS
> questions — public leaderboards do **not** reliably predict in-domain legal performance.

---

## Your hardware context

**Machine:** MacBook Pro M3 Max, 64GB unified memory.

The M3 Max's unified memory means the GPU and CPU share one memory pool — all 64GB is
available for model weights, unlike a discrete GPU limited to its VRAM. After the OS and
apps (~10GB) you have roughly **50–54GB usable** for the whole AI stack (LLM + vector store +
embedding model + context cache).

> **Learning note — what fits:** a 14B model at Q8 is ~15GB; a 24–32B dense model at Q4 is
> ~13–20GB; a Mixture-of-Experts 30B-A3B is ~17–18GB at Q4. **All of these run comfortably on
> 64GB alongside Qdrant and an embedding model** — so the original 2024 instinct to default to
> an 8B model under-uses this machine. The constraint is speed and quality tradeoffs, not
> memory.

> **Bandwidth governs speed:** the M3 Max has ~400 GB/s memory bandwidth and decode is
> bandwidth-bound — tokens/sec ≈ bandwidth ÷ bytes read per token. This is *why* Mixture-of-
> Experts models are attractive locally (below).

---

## What quantisation means

> **Learning note:** model files carry tags like `Q4_K_M` or `Q8_0`. This is quantisation — a
> compression technique that stores each weight with fewer bits, trading a little quality for a
> lot of memory and speed.

| Format | Bits/weight | Memory (14B model) | Quality tradeoff |
|---|---|---|---|
| FP16 | 16 | ~28GB | Full quality, high memory |
| Q8_0 | 8 | ~15GB | Near-identical to FP16 |
| Q4_K_M | 4 | ~8–9GB | ~95–98% of full precision — very practical |
| MLX 4-bit | 4 | ~8GB | Apple-native; retains ~97% MMLU, ~10% less memory than GGUF |

For interactive RAG on your machine, **Q4_K_M (or Apple MLX 4-bit) is the working default** —
the quality loss is small and the speed/memory gain is large. Reserve Q8 for a final-quality
comparison if the benchmark suggests Q4 is costing accuracy.

---

## What changed since 2024 (and why it matters for SafetyLM)

The original doc compared Llama 3.1 8B, Mistral 7B, and Gemma 2 9B. Two things have shifted the
decision substantially:

1. **Licensing is now the first filter, not a footnote.** SafetyLM is an open, *legal-domain*
   product, so a clean licence (Apache-2.0 / MIT) matters twice over:
   - **Llama** models stay under the Meta Community Licence → excluded from being the flagship
     base model (avoids the licence caveat in the README entirely).
   - **Gemma 3** ships under the Gemma Terms of Use, whose prohibited-use policy includes
     **restrictions touching legal/medical professional-practice content** — a genuine problem
     for a WHS tool. (Gemma 4, Apr 2026, reportedly moved to Apache-2.0 — verify before use.)
   - The **clean-licence field** is strong now: **Qwen3** (Apache-2.0), **Mistral Small**
     (Apache-2.0), **Phi-4** (MIT), **gpt-oss** (Apache-2.0).

2. **Two RAG-specific findings change how we run the model:**
   - **Reasoning/"thinking" mode hallucinates *more* on grounded summarisation.** On Vectara's
     hallucination benchmarks, reasoning models exceed 10% hallucination where instruct models
     sit at 4–6%. **→ Run instruct (non-reasoning) variants with thinking OFF on SafetyLM's
     faithfulness-critical path.**
   - **Bigger is not more faithful.** Qwen3-8B beats Qwen3-32B, and Gemma-3 12B beats 27B, on
     grounded-summarisation hallucination. **→ Don't assume the largest model that fits is the
     most trustworthy; benchmark faithfulness directly.**

---

## Current candidates (mid-2026)

All licence-clean, all fit on 64GB. See the research snapshot for sources, context windows, and
Ollama tags.

### Dense models

| Model | Params | Licence | Context | RAG lens |
|---|---|---|---|---|
| **Qwen3-14B** | 14B | Apache-2.0 | 128K | Strong instruction-following + native structured output; well-evidenced |
| **Mistral Small 3.2** | 24B | Apache-2.0 | 128K | Explicitly tuned for instruction-following + function-calling — on-target for citation blocks |
| **Qwen3-32B** | 32B | Apache-2.0 | 128K | Larger sibling; same toolchain |
| **Phi-4** | 14B | MIT | **16–32K only** | Strong reasoning for size, but short context constrains multi-chunk RAG |
| **Gemma 4 31B** ⚠ verify | 31B | Apache-2.0 (verify) | 256K | Post-cutoff; promising but specs need confirming at build |

### Mixture-of-Experts (the M3 Max sweet spot)

> **Learning note — why MoE fits this hardware:** an MoE model has many "expert" sub-networks
> but only activates a few per token. **Total** parameters drive *memory*; **active**
> parameters drive *speed*. So a 30B-total / 3B-active model has the memory footprint of a 30B
> (~17GB at Q4) but decodes at roughly the speed of a 3B model — big-model quality at
> small-model latency.

| Model | Total / Active | Licence | Context | Notes |
|---|---|---|---|---|
| **Qwen3-30B-A3B** | 30B / 3B | Apache-2.0 | 256K | Reference local-RAG MoE; the standout fit for this machine |
| **gpt-oss-20b** | 21B / 3.6B | Apache-2.0 | 128K | ~14GB, fast; clean baseline |

---

## Recommendation — a benchmark shortlist, not a pick

Run these against the Phase 4 benchmark (`05-evaluation.md`). Run all with **thinking OFF** on
the grounded path.

| Role | Model | Why |
|---|---|---|
| **~14B dense** | **Qwen3-14B** | Best-evidenced clean-licence 14B; native structured output; strong faithfulness in the Qwen3 instruct line |
| **~24–32B / MoE** | **Qwen3-30B-A3B** (MoE) + **Mistral Small 3.2 24B** (dense comparator) | The 64GB sweet spot vs a purpose-tuned instruction-following dense model |
| **Small baseline** | **gpt-oss-20b** or **Qwen3-8B** | A clean floor to measure RAG uplift against |
| **No-RAG floor** | **vanilla Llama 3.1 8B** | Kept *only* as the baseline in the eval (per `05-evaluation.md`) to measure what corpus + retrieval add — not a deployment candidate |

If you want to test a newer dense ~27–31B, treat **Qwen3.6-27B** or **Gemma 4 31B** as
**verify-at-build upside experiments** (post-cutoff, specs unconfirmed), not the baseline.

---

## Runtime: Ollama (with an MLX caveat)

> **Learning note:** Ollama is a local model server that makes running open LLMs on a Mac a
> one-line command (`ollama run qwen3:14b`). It handles downloading, quantisation, and serving
> a local API that LlamaIndex connects to. Think Docker, but for LLMs.

**Why Ollama:** native Apple Silicon + Metal acceleration, trivial model swapping (one line),
local API endpoint, no Python complexity for serving.

> **Runtime caveat to verify (mid-2026):** Ollama is reportedly migrating its Apple-Silicon
> engine from llama.cpp to **Apple MLX**. MLX is faster at *decode* but, on current evidence,
> **weaker at *prefill* / long context — which is exactly what RAG stresses** (large retrieved
> chunks go into the prompt). If SafetyLM routinely exceeds ~5–8K tokens of context,
> **llama.cpp + FlashAttention may win end-to-end.** Benchmark your own prefill at realistic
> RAG prompt lengths before committing a runtime. (`llama.cpp` is also the more reliable local
> path for running a reranker via `--rerank` — see `04-rag-pipeline.md`.)

---

## Expected inference performance on M3 Max (Q4, decode)

| Model class | Approx tokens/sec | Notes |
|---|---|---|
| 7–8B dense | 45–55 | Fast |
| 13–14B dense | ~30 | Very usable |
| 24–32B dense | ~25–35 | Acceptable for a research tool |
| **MoE 30B-A3B** | **~90–130** ⚠ extrapolated | Big-model quality at small-model speed; no direct M3 Max figure yet |
| 70B dense | ~7.5 | Needs 128GB — not usable on 64GB |

⚠ Most published 2026 numbers are M4/M5; treat M3 Max as ~equal to or 5–15% below M4 Max for
decode. The MoE figure is extrapolated — verify on your machine.

40–130 tok/s is comfortably interactive: a 300-word answer in a few seconds.

---

## How to actually decide (Phase 4)

1. Build the benchmark first (`05-evaluation.md`) — you cannot choose a model without it.
2. Run the shortlist with thinking OFF; score faithfulness, jurisdictional accuracy, and
   structured-citation reliability, not just "feel".
3. Weight **faithfulness and instruction-following** above raw size.
4. Prefer the cleanest licence among models within ~5% on the WHS benchmark.
5. **Validate the winner on a labelled set of real AU/NZ WHS queries** before locking — the one
   recommendation from the research with no caveat.

Record the final pick (and the benchmark evidence for it) back into this document and
`CLAUDE.md §3` when Phase 4 completes.
