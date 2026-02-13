# Paper Review Prompt

Copy the text below and paste it along with the attached paper (PDF or HTML) when requesting feedback from an LLM.

---

## The Prompt

You are reviewing a manuscript for submission to **Neural Computation**. The paper presents a spectral bifurcation analysis of competing ring attractor networks used to model multi-item working memory.

Please provide a thorough, constructive review organized as follows:

### 1. Summary (2-3 sentences)
What is this paper about? What are the main claims?

### 2. Strengths
What does the paper do well? Consider:
- Novelty of the analysis (has this eigenvalue decomposition been done before for coupled ring attractors?)
- Clarity of the mathematical exposition
- Connection between theory and behavioral predictions
- The heterogeneity result (Section 4.2) — is the argument about imperfect bifurcations convincing?
- The valley interpretation (Section 3.5.4) — is the functional operating point argument well-supported?

### 3. Weaknesses and Major Concerns
Be direct. Consider:
- **Mathematical rigor**: Are the proofs/arguments for Goldstone mode protection complete? Is the Jacobian derivation sufficiently detailed?
- **Model limitations**: N=48 neurons, rate model, additive noise, mean-field coupling — do these simplifications undermine the claims?
- **Missing analysis**: The Kramers escape rate is invoked but not computed quantitatively (acknowledged in limitations). How much does this weaken the behavioral predictions?
- **Phase diagram methodology**: 500 trials per grid point with a swap error threshold of 0.3 rad — are these sufficient? Is the swap classification robust?
- **Biological relevance**: The paper claims the brain operates in the "valley regime" (J_× ≈ 1.2-1.6). Is this testable? Is the mapping from model parameters to biology credible?
- **Notation consistency**: Any undefined symbols or notation shifts?

### 4. Specific Technical Questions
- Is the claim that "drive strength is secondary to cross-inhibition" (Section 3.5.3) robust to different noise models (multiplicative, state-dependent)?
- The non-monotonic valley — could this be an artifact of the specific activation function (sigmoid with β=5.0, h₀=0.5)?
- The heterogeneity test uses symmetric Gaussian noise on weights. Would asymmetric heterogeneity (e.g., log-normal, as in cortical data) produce different results?
- The paper claims "universality" of the saddle-point bifurcation (Section 4.8). Is this overclaimed for a single model with specific parameters?

### 5. Missing Literature
Are there relevant papers the authors should cite or engage with? Consider:
- Recent attractor network models of working memory (2022-2025)
- Experimental evidence for/against bump attractor dynamics in prefrontal cortex
- Alternative models of swap errors (non-attractor-based)
- Mathematical treatments of imperfect bifurcations in neural circuits

### 6. Presentation
- Is the paper too long, too short, or about right for Neural Computation?
- Are the figures clear and informative? (6 figures: schematic, existence boundary, pitchfork diagram, eigenvector comparison, phase diagram, heterogeneity test)
- Suggestion for the abstract — does it accurately represent all four results?
- Any sections that could be cut or condensed?

### 7. Verdict
- **Accept / Minor Revision / Major Revision / Reject** with justification
- What are the 2-3 changes that would most improve the paper?
- Is the central contribution (spectral bifurcation analysis of coupled ring attractors) sufficient for Neural Computation?

---

## Context for the Reviewer

- Target journal: **Neural Computation** (MIT Press)
- Paper length: ~6,500 words, 28 references, 6 figures
- The paper includes a Colab notebook for reproducibility (not attached)
- Key novel result: the coexistence saddle exists in a razor-thin window (ΔJ ≈ 0.01) that is destroyed by heterogeneity — converting the pitchfork into an imperfect bifurcation
- The stochastic phase diagram (128,000 trials) is the bridge between spectral theory and behavior
