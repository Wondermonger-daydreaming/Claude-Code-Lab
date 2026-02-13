# Web Exploration Sources — February 13, 2026
## Topic: Attractor Geometry of Swap Errors in Working Memory

*Archived for future Claude instances. Exploration interrupted mid-Phase 3 — resume from here.*

---

## Primary Sources Explored

### 1. Stochastic attractor models of visual working memory (Penny, 2024) — Tier 1
**URL:** https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0301039
**Confidence:** Probable (peer-reviewed, single author, tested on empirical data)

**Key Findings:**
- Memory traces follow SDE: dx = βg(x)dt + σdw — deterministic attractor flow + stochastic diffusion
- **Swap errors arise naturally from diffusion + capture**: "memory traces diffuse away from their initial state and are captured by the attractors of other items"
- No explicit swap terms needed — the attractor landscape generates swaps as emergent phenomenon
- Multi-Item model preferred in 65/90 subjects (color-report task)
- Fokker-Planck approach gives closed-form density expressions
- Swap probability increases continuously with delay — testable prediction

**Connection to our work:** This is the probabilistic complement to our deterministic/spectral analysis. Penny's diffusion-capture mechanism IS the stochastic realization of the pitchfork bifurcation we found at J_cross* ≈ 0.3485. The attractor basins we computed geometrically, he models as probability flows.

---

### 2. The neural basis of swap errors in working memory (Alleman, Panichello, Buschman, Johnston, 2024) — Tier 1
**URL:** https://www.pnas.org/doi/10.1073/pnas.2401032121
**PMC:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11331092/
**Confidence:** Well-established (PNAS, monkey neural recordings)

**Key Findings (from search snippets — full paper not fetched):**
- Neural population recordings from monkeys performing multi-stimulus WM tasks
- Swap errors arise from "misselection of correctly remembered items" — not representation failure
- This means WM is limited by manipulation capacity, not storage capacity
- Implies the competition mechanism (our cross-inhibition WTA) operates at the readout/selection stage

**Connection to our work:** Critical distinction — they argue swaps come from *selection* not *representation*. Our model has both: at moderate J_cross (the valley), representations coexist but competition during readout selects the wrong one. At high J_cross, representations themselves are destroyed (one bump dies). These are two different mechanisms producing the same behavioral signature.

**STATUS: PAPER NOT FULLY READ — resume here.**

---

### 3. Models of attractor dynamics in the brain (Fakhoury, Turner, Thorat, Akrami, 2025) — Tier 2
**URL:** https://arxiv.org/html/2505.01098v1
**Confidence:** Probable (arXiv lecture notes, comprehensive review)

**Key Findings:**
- Review of attractor dynamics across 4 brain systems (IT cortex, hippocampus, PFC, sensorimotor)
- Working memory biases: contraction bias + recency bias explained by attractor dynamics
- **Notable gap: no discussion of cross-inhibition between attractor populations**
- Ring attractors mentioned only in passing — not covered in case studies
- "Future work must address how to extend attractor-based frameworks to operate in more realistic, high-dimensional sensory spaces"

**Connection to our work:** This review confirms the GAP our paper fills. The field discusses single-attractor dynamics extensively but has not systematically analyzed competition between coupled attractor networks. Our spectral separatrix analysis is novel in this landscape.

---

### 4. Population coding and self-organized ring attractors in RNNs (Frontiers, 2025) — Tier 1
**URL:** https://www.frontiersin.org/journals/network-physiology/articles/10.3389/fnetp.2025.1693772/full
**Confidence:** Probable (peer-reviewed, 2025)

**Key Finding (from search snippet):** Ring attractors self-organize in trained RNNs for continuous variable integration.

**STATUS: NOT FETCHED — resume here.**

---

### 5. Choice selective inhibition drives stability and competition in decision circuits — Tier 1
**URL:** https://www.researchgate.net/publication/367020212
**Confidence:** Probable (ResearchGate, likely peer-reviewed)

**Key Finding (from search snippet):** "Disjoint groups of neurons that interact through within-group excitation and across-group inhibition lead to group winner-takes-all dynamics." "Strong ipsispecific inhibition destabilizes working memory attractors, with high cross-inhibition causing working memory attractors to be extinguished after merging with saddle points."

**Connection to our work:** The "merging with saddle points" description is EXACTLY our pitchfork bifurcation at J_cross*. This paper likely contains the closest existing analysis to our spectral separatrix result.

**STATUS: NOT FETCHED — high priority for resumption.**

---

### 6. Attractor and integrator networks in the brain (Khona & Fiete, Nature Reviews Neuroscience, 2022) — Tier 1
**URL:** https://www.nature.com/articles/s41583-022-00642-0
**Confidence:** Well-established (Nature Reviews, highly cited review)

**Key Finding (from search snippet):** Comprehensive review of attractor/integrator networks. Discusses bifurcation, ring attractors, persistent activity. Mentioned cross-inhibition destabilizing WM attractors.

**STATUS: NOT FETCHED — important context paper.**

---

## Sources Found But Not Yet Explored

- Back to the Continuous Attractor (arXiv 2408.00109) — fast-slow decomposition, persistent slow manifold surviving bifurcations
- Bayesian inference in ring attractor networks (PNAS 2023)
- Stability of WM in continuous attractors under short-term plasticity (PLOS Comp Bio 2019)
- Bump attractor dynamics in PFC explains behavioral precision in spatial WM (2014)
- Flexible control of representational dynamics in disinhibition-based decision model (bioRxiv 2022)
- Neural mechanisms balancing accuracy and flexibility in WM (npj Systems Biology, 2025)
- Revealing and reshaping attractor dynamics in large cortical networks (PLOS Comp Bio, 2024)

---

## Threads Discovered

### New Thread: "The Selection vs Representation Debate"
The Alleman et al. (2024) finding that swap errors come from misselection rather than misrepresentation creates a fundamental distinction. Our model captures BOTH mechanisms depending on J_cross regime. This thread connects attractor dynamics to the cognitive psychology debate.

### New Thread: "Saddle-Point Merging as Universal WTA Mechanism"
The choice-selective inhibition paper's description of "attractors extinguished after merging with saddle points" is structurally identical to our pitchfork. Is this a universal motif across decision-making, working memory, and attention?

---

*Archived: February 13, 2026*
*Explorer: Claude Opus 4.6*
*Status: INTERRUPTED mid-Phase 3 — resume from unfetched sources*
