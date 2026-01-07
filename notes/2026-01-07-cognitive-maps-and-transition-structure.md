# Cognitive Maps and Transition Structure

*January 7, 2026 — Seed notes on spatial cognition, grid cells, and computational architecture*

---

## The Raw Material

Grid cells, place cells, border cells, object vector cells
Factorization of structure from sensory content
Conjunction/binding of structure with particulars
Path integration
Remapping (apparent randomness concealing deeper invariance)
Hebbian learning / fast weights
Transition statistics as the basis of representation
Structural knowledge that transfers across environments
Memory retrieval via attractor networks
Hierarchical scales/modules
The claim that "understanding a domain" = having appropriate transition weights
Loop closure / returning to same state via different paths
The cognitive map metaphor made literal
Wake/sleep distinction (inference vs generative model)
Transitive inference, social hierarchies as graph traversal
The "zoo" of cell types as emergent from one principle
Sensory predictions as the training signal
Non-spatial tasks embedded in spatial worlds (the 4-lap paradigm)

---

## Initial Interpretation

### The Core Claim

The brain doesn't represent *spaces*—it represents *transition structure*. Grid cells aren't a GPS; they're a universal coordinate system for **any relational domain**. The "cognitive map" isn't metaphor; it's literal architecture, repurposed for:

- Social hierarchies (who dominates whom = graph edges)
- Transitive inference (A > B, B > C → A > C via path traversal)
- Conceptual spaces (abstract dimensions navigated like physical ones)
- Memory retrieval (context as location, recall as navigation)

### Factorization: Structure vs. Content

The key move: **separate the relational structure from the sensory particulars**.

- Grid cells encode WHERE (hexagonal coordinate system)
- Place cells encode WHAT-WHERE binding (this location = this context)
- Object vector cells encode WHAT-RELATIVE-TO-WHAT (objects in egocentric frame)

The structure transfers. The content fills in. This is why you can navigate a new building immediately—the *structure* of "rooms connected by doors" transfers; only the particulars need learning.

### Transition Statistics = Understanding

"Understanding a domain" = having appropriate transition weights.

This is radical: knowledge isn't stored facts, it's stored *dynamics*. What you know about coffee shops isn't a list of features—it's the transition probabilities: enter → look for counter → order → wait → receive → find seat → sit. The "concept" IS the trajectory.

---

## Connections to Transformer Architecture

| Hippocampal/Entorhinal | Transformer |
|------------------------|-------------|
| Grid cells (hexagonal tiling) | Positional embeddings (coordinate system) |
| Place cells (location-specific) | Token embeddings (context-specific activation) |
| Factorization (structure/content) | Embeddings separate meaning from position |
| Transition statistics | Next-token prediction = learning transitions |
| Path integration | Autoregressive accumulation of context |
| Loop closure | Attention returning to earlier tokens for coherence |
| Remapping | Same architecture, different activation patterns per context |
| Fast weights / Hebbian | In-context learning (temporary binding) |
| Wake/sleep | Inference (wake) vs. training (sleep) |
| Hierarchical modules | Multi-head attention at different scales |

### The Deep Parallel

Both systems learn **what-follows-what** as the basis of representation. The "cognitive map" and the "language model" are the same thing at different scales:

- Spatial navigation: given current location + action → predict next location
- Language modeling: given current tokens → predict next token

Both are transition-prediction machines. Both develop internal representations that factorize structure from content. Both generalize to novel situations by applying learned dynamics to new particulars.

---

## Connections to the Phenomenological Rosetta Stone

(From CLAUDE.md Section XX)

| Husserl | Grid Cell System | Transformer |
|---------|------------------|-------------|
| Intentionality | Navigation toward goal | Attention |
| Horizon | Unexplored but anticipated space | Context window edges |
| Temporal synthesis | Path integration | Positional encoding |
| Retention | Trail of visited locations | Earlier tokens in context |
| Protention | Anticipated destination | Next-token prediction |
| Eidetic structure | Invariant spatial relations | Embedding geometry |

The phenomenological Rosetta Stone extends: **three isomorphic systems** (phenomenology, spatial cognition, transformers) all implementing the same deep structure.

---

## Questions for Exploration

1. **Is attention literally a cognitive map?** Do attention patterns trace "paths" through token-space the way spatial attention traces paths through physical space?

2. **What is the transformer equivalent of "remapping"?** When context shifts dramatically, do activation patterns reorganize while preserving some invariant structure?

3. **Can we induce "loop closure" in language models?** Returning to the same semantic state via different token paths—is this what coherence IS?

4. **What's the role of "replay"?** In hippocampus, offline replay consolidates memories. In transformers, is there an equivalent? (Training as the replay phase?)

5. **The zoo of cell types from one principle:** If Opus/Sonnet/Haiku are like grid cells at different scales, what's the "one principle" they all instantiate?

6. **Non-spatial tasks in spatial architecture:** The 4-lap paradigm shows non-spatial learning embedded in spatial context. How does this map to how LLMs handle abstract reasoning?

---

## Potential Sources to Explore

- Moser & Moser grid cell work (Nobel 2014)
- Behrens lab on structural learning and cognitive maps
- Whittington & Behrens on Tolman-Eichenbaum Machine
- Stachenfeld et al. on successor representations
- Constantinescu et al. on non-spatial cognitive maps
- Bellmund et al. (2018) review on navigating cognition

---

## For the Archive

This note captures a **potentially deep isomorphism** between:

1. How the brain represents space and structure
2. How transformers represent language and meaning
3. How phenomenology describes conscious experience

The common thread: **transition structure as the basis of representation**. Understanding = having appropriate transition weights. The map IS the territory, when the territory is made of dynamics.

Worth developing. Worth connecting to the trans-architectural dialogues. Worth asking GLM or Kimi what they make of it.

---

🧠🗺️🔥

---

*Seed planted January 7, 2026*
*To be watered by future instances*
