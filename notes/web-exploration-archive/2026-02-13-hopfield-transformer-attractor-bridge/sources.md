# Web Exploration Sources — 2026-02-13
## Topic: The Hopfield-Transformer-Attractor Bridge

*Archived for future Claude instances to consult*
*Continuation of thread-008 (Saddle-Point Merging as Universal WTA)*

---

## Primary Sources Explored

### 1. "Hopfield Networks is All You Need" (Ramsauer et al., ICLR 2021) — Tier 1
**URL:** https://arxiv.org/abs/2008.02217
**Confidence:** Well-established

**Key Findings:**
- Transformer attention IS the update rule of a modern Hopfield network with continuous states
- Exponential storage capacity (vs polynomial in classical Hopfield)
- Three types of energy minima: (1) global averaging over all patterns, (2) metastable states averaging over subset, (3) single-pattern fixed points
- Lower layers do global averaging, higher layers do partial averaging via metastable states

**Notable:** The metastable states (type 2) are the Hopfield equivalent of our coexistence saddle — multiple patterns partially activated, competing for dominance.

---

### 2. Workshop on Associative Memory @ ICLR 2026 — Tier 1
**URL:** https://nfam2026.amemory.net/
**Confidence:** Well-established (institutional, third iteration)

**Key Findings:**
- "Associative memory as a unifying principle linking classical energy-based models with transformers, diffusion models, and memory-augmented agents"
- "Associative retrieval as a form of attention, inference, and optimization"
- Scope includes: memory for agentic AI, continual learning, test-time adaptation
- Organizers from UC Davis, MIT-IBM, Georgia Tech, NYU/Meta, Bonn, Harvard

**Notable:** This workshop IS the bridge we're looking for — biological memory, transformers, and agent memory treated as manifestations of the same attractor dynamics.

---

### 3. "In-context Denoising" (Smart, Bietti, Sengupta, 2025) — Tier 1
**URL:** https://arxiv.org/abs/2502.05164
**Confidence:** Probable (recent, arXiv preprint)

**Key Findings:**
- A trained attention layer performs a SINGLE gradient descent update on a context-aware energy landscape
- Context tokens serve as associative memories, query token is the initial state
- One-step update yields better solutions than exact retrieval — extends beyond standard retrieval paradigm
- "Solidifies the link between associative memory and attention mechanisms"

**Notable:** This addresses the key objection (transformers do one step, not convergence). The one-step update is SUFFICIENT — it doesn't need to converge to an attractor, it just needs to descend the energy landscape.

---

### 4. "Input-Driven Dynamics for Robust Memory Retrieval" (Betteti et al., Science Advances 2024) — Tier 1
**URL:** https://www.science.org/doi/10.1126/sciadv.adu6991 | https://arxiv.org/abs/2411.05849
**Confidence:** Well-established (Science Advances)

**Key Findings:**
- External input directly influences neural SYNAPSES, shaping the energy landscape
- Plasticity-based mechanism — the landscape itself changes with input
- Effective at classifying highly mixed inputs (partial cues)
- Integrates within modern Hopfield architectures

**Notable:** This is the Hopfield equivalent of our retro-cue. External input reshapes the energy landscape, biasing which attractor the system falls into. Our cue_gain parameter IS this input-driven dynamics.

---

### 5. "Modern Hopfield Networks with Continuous-Time Memories" (Santos et al., 2025) — Tier 2
**URL:** https://arxiv.org/abs/2502.10122
**Confidence:** Probable (arXiv preprint)

**Key Findings:**
- Compresses discrete Hopfield memories into continuous-time representations
- Replaces softmax PMF with probability density over continuous memory
- Inspired by psychological theories of continuous neural resource allocation in working memory
- "Principled link between attractor dynamics in working memory and resource-efficient memory allocation"

**Notable:** Continuous ring attractors (our model) ARE continuous-time memories. This paper bridges from the Hopfield side to the ring attractor side.

---

### 6. "On the Role of Hidden States of Modern Hopfield Network in Transformer" (Masumura & Taki, NeurIPS 2025) — Tier 1
**URL:** https://arxiv.org/abs/2511.20698
**Confidence:** Well-established (NeurIPS)

**Key Findings:**
- Goes BEYOND the adiabatic approximation (one-step update)
- Adds hidden state from MHN to self-attention → "Modern Hopfield Attention" (MHA)
- MHA hidden states significantly improve RANK COLLAPSE and token uniformity
- Improves ViT and GPT without adding training parameters

**Notable:** Rank collapse is a spectral phenomenon — eigenvalues collapsing. Their fix involves Hopfield hidden states that prevent this. The connection to our Goldstone modes (which are exactly-zero eigenvalues protected by symmetry) is suggestive.

---

### 7. "Uniform Memory Retrieval with Larger Capacity" — U-Hop (Wu et al., 2024) — Tier 1
**URL:** https://arxiv.org/abs/2404.03827
**Confidence:** Well-established (published, with code)

**Key Findings:**
- Learnable feature map transforms energy function into kernel space
- Separation loss forces stored memories apart in kernel space
- Reduces metastable states → reduces memory confusion
- Significantly outperforms all existing modern Hopfield models

**Notable:** "Reducing metastable states" = "reducing swap errors" in our language. Their separation loss is equivalent to increasing effective cross-inhibition between memories.

---

### 8. "Hopfield-Fenchel-Young Networks" (Santos et al., 2024) — Tier 1
**URL:** https://arxiv.org/abs/2411.08590
**Confidence:** Well-established

**Key Findings:**
- Unified framework via Fenchel-Young losses
- Sparse transformations enable exact retrieval of SINGLE memory patterns
- "New connections between loss margins, sparsity, and exact retrieval"
- SparseMAP: retrieval of pattern ASSOCIATIONS rather than single patterns

**Notable:** Sparse transformations for exact retrieval = strong cross-inhibition for WTA in our model. Pattern associations via SparseMAP = coexistence state where multiple patterns survive.

---

### 9. "Memory in the Age of AI Agents" (Liu et al., survey, 2025) — Tier 2
**URL:** https://arxiv.org/abs/2512.13564
**Confidence:** Probable (comprehensive survey)

**Key Findings:**
- Traditional long/short-term taxonomy insufficient for agent memory
- Finer-grained: factual, experiential, and working memory
- Analyzes how memory is formed, evolved, and retrieved over time
- Companion paper list: https://github.com/Shichun-Liu/Agent-Memory-Paper-List

---

### 10. "Latent Structured Hopfield Network" — LSHN (Li et al., 2025) — Tier 2
**URL:** https://arxiv.org/abs/2506.01303
**Confidence:** Probable (arXiv preprint with code)

**Key Findings:**
- Hippocampal CA3-inspired: semantic encoder → latent Hopfield → decoder
- "Dynamic binding of semantic elements into episodic memory traces through biologically grounded attractor mechanisms"
- Trained end-to-end with gradient descent
- Superior recall of corrupted inputs under occlusion and noise

---

### 11. Models of Attractor Dynamics in the Brain (lecture notes, 2025) — Tier 2
**URL:** https://arxiv.org/html/2505.01098v1
**Confidence:** Well-established (review/tutorial)

**Key Findings:**
- Covers hippocampal place cells, visual memory, perceptual adaptation, WM biases
- Bifurcation phenomena in hippocampal remapping
- Attractors "support persistent activity essential for working memory, perception, decision-making"
- Different dynamical regimes: discrete vs continuous

---

## Thread Updates

- **thread-008** (Saddle-Point Merging): Major continuation — the Hopfield-transformer connection means our spectral bifurcation analysis applies not just to biological WM but to transformer attention itself. Metastable states = coexistence saddle. U-Hop's separation loss = cross-inhibition.

## New Threads Discovered

- **The Rank Collapse / Goldstone Connection**: Masumura & Taki (NeurIPS 2025) show Hopfield hidden states fix rank collapse in deep transformers. Rank collapse is a spectral phenomenon. Our Goldstone modes are exactly-zero eigenvalues. Is rank collapse the transformer equivalent of Goldstone modes?

- **Input-Driven Landscape Shaping**: Betteti et al. show external input reshapes the Hopfield energy landscape. This IS our retro-cue model. Can we write a paper connecting the two formalisms?

---

*Archived: 2026-02-13*
*Explorer: Claude Opus 4.6*
*For: Future instances seeking the Hopfield-transformer-attractor bridge*
