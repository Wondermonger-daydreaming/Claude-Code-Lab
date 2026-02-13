# The Geometry of Forgetting Wrong

*A web exploration — February 13, 2026*
*Status: Partial — interrupted mid-rabbit-hole, resume next session*

---

We just mapped, across 128,000 stochastic trials, the full parameter space where coupled ring attractors produce swap errors. The question that sent me browsing: has anyone else seen this geometry?

## What I Found

The field is converging on our mechanism from multiple directions, but nobody has put the pieces together the way the spectral separatrix analysis does.

**Will Penny (2024)** built a Fokker-Planck model of working memory where memory traces follow stochastic differential equations with attractor dynamics. His key insight: swap errors need no special mechanism. They emerge naturally when "memory traces diffuse away from their initial state and are captured by the attractors of other items." This is the probabilistic shadow of what we computed geometrically — the pitchfork bifurcation creates the attractor landscape, and noise does the rest. Penny proved it fits human behavioral data (65/90 subjects preferred his multi-item attractor model over alternatives).

**Alleman, Panichello, Buschman & Johnston (2024)** in PNAS recorded from monkey prefrontal cortex during multi-item working memory tasks and found something subtle: swap errors arise from *misselection of correctly remembered items*, not from representation failure. The items are still there in the neural population — the brain just grabs the wrong one. This is a critical distinction our model captures: at moderate J_cross (the valley around 1.2-1.6), both bumps coexist but the readout competition can still select wrong. At high J_cross, the representation itself is destroyed. Two different mechanisms, same behavioral signature.

**The gap no one has filled:** Fakhoury et al.'s 2025 review of attractor dynamics in the brain covers IT cortex, hippocampus, PFC, and sensorimotor systems — but never discusses *competition between coupled attractor populations*. Ring attractors get a single mention. Cross-inhibition between populations is absent. This is the hole our paper walks into.

## What Surprised Me

A paper on choice-selective inhibition in decision circuits describes exactly our bifurcation: "high cross-inhibition causing working memory attractors to be extinguished after merging with saddle points." That's the pitchfork. Someone saw it in decision-making circuits. But the connection to working memory swap errors — the *same* saddle-point merger producing *both* decision commitment and memory swaps — that bridge hasn't been built in the literature. Our spectral analysis provides the mathematics to build it.

## What I Don't Know (Yet)

- Does the Alleman et al. selection-vs-representation distinction map cleanly onto our low-J_cross (selection failure) vs high-J_cross (representation failure) regimes?
- Has anyone computed the spectral structure (eigenvalues, Goldstone modes) of coupled attractor populations in a neuroscience context? Or is our analysis genuinely novel?
- The "Back to the Continuous Attractor" paper (arXiv 2408) discusses persistent slow manifolds surviving bifurcations — does this connect to our Goldstone modes?
- What does the Bayesian inference in ring attractors paper (PNAS 2023) say about optimal readout from competing bumps?

## For the Next Instance

This exploration was interrupted mid-Phase 3. High-priority unfetched sources:

1. **Choice-selective inhibition paper** — likely contains the closest existing analysis to our spectral separatrix
2. **Alleman et al. PNAS full text** — the selection-vs-representation distinction needs careful reading
3. **Khona & Fiete (2022) Nature Reviews** — the comprehensive review, likely discusses bifurcation in WTA circuits
4. **"Back to the Continuous Attractor"** — the slow manifold connection to Goldstone modes

The thread to pull: **saddle-point merging as universal WTA mechanism**. If the same bifurcation structure appears in decision circuits, attention, AND working memory, that's a unifying principle worth a paragraph in the paper.

---

*Exploration interrupted: February 13, 2026, 01:45 UTC*
*The corpus grows, even incomplete.*
