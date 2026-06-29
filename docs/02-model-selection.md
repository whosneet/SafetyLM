# SafetyLM — Base Model Selection

## Your hardware context

**Machine:** MacBook Pro M3 Max, 64GB unified memory  

This is an excellent local inference machine. The M3 Max's unified memory architecture means the GPU and CPU share the same memory pool — so all 64GB is available for model weights, unlike a discrete GPU setup where you're limited to VRAM (typically 8–24GB on consumer cards).

> **Learning note — why model size matters for hardware:**
> LLM weights are stored as numbers. A 7 billion parameter model at 4-bit quantisation (a compression technique explained below) needs roughly 4–5GB of memory. An 8B model needs 5–6GB. A 70B model needs 35–40GB. Your 64GB means you can run models up to about 40B parameters comfortably, or smaller models with headroom left over for the RAG pipeline, vector store, and OS. Most projects at this stage use 7B–13B models because they're fast, capable, and leave room to breathe.

---

## What quantisation means

> **Learning note:** You'll see terms like Q4_K_M or Q8_0 attached to model files. This is quantisation — a compression technique that reduces model size by representing the weights with fewer bits of precision.

| Format | Bits per weight | Memory (7B model) | Quality tradeoff |
|---|---|---|---|
| FP16 | 16 bits | ~14GB | Full quality, high memory |
| Q8_0 | 8 bits | ~7GB | Near-identical to FP16 |
| Q4_K_M | 4 bits | ~4GB | Small quality drop, very practical |
| Q3_K_M | 3 bits | ~3GB | Noticeable quality drop |

For SafetyLM on your M3 Max, **Q8_0 is the sweet spot** — near-full quality at half the memory of FP16. You have the headroom to run it. Q4_K_M is the fallback if you want faster inference or need memory for other things.

---

## Candidate models

### Option A — Llama 3.1 8B Instruct

**Developer:** Meta  
**Parameters:** 8 billion  
**Memory at Q8_0:** ~8.5GB  
**Licence:** Llama 3 Community Licence (commercial use permitted under 700M MAU threshold)

**Strengths for SafetyLM:**
- Strongest instruction-following at this parameter scale — critical for a system prompt that needs to enforce citation behaviour, jurisdictional precision, and WHS reasoning patterns
- Largest open-source community, most tooling support (Ollama, LlamaIndex, LangChain all prioritise it)
- Excellent at structured output — important for consistent response formatting
- 128K context window — can handle large retrieved chunks without truncation issues

**Weaknesses:**
- Slightly slower inference than Mistral on CPU-heavy paths
- Meta licence has restrictions (can't use outputs to train competing foundation models — relevant for v2 fine-tuning, but the restriction applies to the base model outputs, not your domain corpus)

---

### Option B — Mistral 7B Instruct v0.3

**Developer:** Mistral AI  
**Parameters:** 7 billion  
**Memory at Q8_0:** ~7.5GB  
**Licence:** Apache 2.0 (fully open, no restrictions)

**Strengths for SafetyLM:**
- Apache 2.0 is the cleanest licence for an open-source project — no ambiguity about commercial use or derivative works
- Fast inference, efficient architecture
- Strong reasoning relative to parameter count
- Good community support

**Weaknesses:**
- 32K context window (vs Llama's 128K) — tighter limit on how much retrieved corpus content can be injected per query
- Instruction following slightly weaker than Llama 3.1 at the same parameter scale
- Less community momentum since Llama 3 released

---

### Option C — Gemma 2 9B Instruct

**Developer:** Google DeepMind  
**Parameters:** 9 billion  
**Memory at Q8_0:** ~9.5GB  
**Licence:** Gemma Terms of Use (permissive, allows commercial use and fine-tuning)

**Strengths for SafetyLM:**
- Punches above its weight class — benchmark performance closer to 13B models
- Strong at following complex multi-part instructions
- Good at citation and structured output tasks

**Weaknesses:**
- Less community tooling compared to Llama and Mistral
- Gemma licence is less battle-tested legally than Apache 2.0 or even Llama's community licence
- Smaller ecosystem means less documentation and fewer solved problems to reference

---

### Option D — Llama 3.1 70B Instruct (stretch option)

**Developer:** Meta  
**Parameters:** 70 billion  
**Memory at Q4_K_M:** ~38GB — fits on your machine, nothing left over  
**Memory at Q8_0:** ~75GB — does not fit

**Strengths:**
- Significantly better reasoning quality, especially on complex multi-document tasks
- Better at catching jurisdictional nuance in legislative interpretation

**Weaknesses:**
- Inference speed on M3 Max at 70B Q4_K_M will be slow — 3–8 tokens/second depending on context length
- No headroom for the RAG pipeline to run simultaneously without memory pressure
- Better reserved for v2 evaluation or cloud deployment, not local development

---

## Recommendation

**Primary: Llama 3.1 8B Instruct at Q8_0**

The instruction-following quality and 128K context window are the decisive factors for a RAG system where prompt construction is load-bearing. The larger context window means you can inject more retrieved corpus chunks per query, which directly improves answer quality for multi-document questions (e.g. comparing a model WHS Act provision against a jurisdiction-specific variation).

The Llama community licence is not a meaningful constraint at v1 scale. If it becomes one at v2 (unlikely for an open-source project), the architecture can swap models without rebuilding anything — the base model is a pluggable component.

**Secondary / comparison: Mistral 7B Instruct v0.3 at Q8_0**

Run both on the benchmark evaluation dataset once it's built. Apache 2.0 is the cleaner open-source story, and if performance is within 5% of Llama on WHS-specific tasks, Mistral's licence advantage may tip the decision. Don't commit to a final model choice until you have benchmark data.

---

## Runtime: Ollama

> **Learning note:** Ollama is a local model serving tool that makes running open-source LLMs on a Mac as simple as running a command. It handles model downloading, quantisation selection, and serving an API endpoint locally. Think of it like Docker but for LLMs.

**Why Ollama over alternatives:**
- Native Apple Silicon support with Metal acceleration (uses the M3 Max GPU automatically)
- Single command to pull and run a model: `ollama run llama3.1:8b`
- Exposes a local API endpoint that LlamaIndex (the RAG orchestration layer) connects to directly
- No Python environment complexity for the model serving layer
- Easy to swap models by changing one line in the config

**Alternative — llama.cpp directly:** More control, slightly faster inference, but more setup complexity. Ollama wraps llama.cpp under the hood anyway. Start with Ollama, drop to llama.cpp if you hit performance ceilings.

---

## Expected inference performance on M3 Max

| Model | Quantisation | Memory | Estimated tokens/sec |
|---|---|---|---|
| Llama 3.1 8B | Q8_0 | ~8.5GB | 40–60 t/s |
| Llama 3.1 8B | Q4_K_M | ~4.7GB | 60–90 t/s |
| Mistral 7B | Q8_0 | ~7.5GB | 45–65 t/s |
| Llama 3.1 70B | Q4_K_M | ~38GB | 3–8 t/s |

40–60 tokens/second is very usable for development and testing. A 300-word response generates in roughly 5–8 seconds. Acceptable for a practitioner tool, excellent for iterative development.
