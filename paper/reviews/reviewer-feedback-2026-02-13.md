# Pre-Submission Reviewer Feedback

*Collected February 13, 2026 — Two LLM reviewers (GPT-based)*
*Paper: "Goldstone Modes and the Coexistence Saddle" v3*
*Target: Neural Computation*

---

## Reviewer 1 Verdict: Minor Revision

### Key Strengths Identified
- Novelty of full 96D eigenvalue decomposition (upgrade over 1D cusp folklore)
- Rank-1 coupling → DC-only destabilization is elegant
- Heterogeneity result is "mathematically rigorous and biologically crucial"
- Valley interpretation is "conceptually rich and well-supported"

### Key Concerns
1. **Goldstone proof sketched, not proven**: Need explicit J·(∂r*/∂φ) = 0 derivation
2. **Kramers gap**: Have eigenvalues but don't compute barrier height ΔV
3. **Phase diagram**: 500 trials/point → SE ≈ 2% (noisy for 7-13% valley). Need 2000-5000 trials
4. **Swap threshold**: 0.3 rad hard threshold — test 0.2, 0.4, 0.5 rad robustness
5. **D notation collision**: D_X (sigmoid derivatives) vs D (dominance variable)
6. **J_× vs J_\times** notation fluctuation
7. **Biological claims too strong**: J_× ≈ 1.2-1.6 depends on arbitrary parameterization
8. **"Universality" overclaimed**: Use "structural isomorphism" or "generic topological feature"
9. **Heterogeneity missing from abstract**
10. **Section 4.5 redundant** with intro — condense to one paragraph

### Top 3 Changes Requested
1. Compute/approximate Kramers barrier ΔV using dominant eigenvalue
2. Fix D notation collision, add Goldstone proof line
3. Add heterogeneity to abstract, soften valley biological claims

---

## Reviewer 2 Verdict: Major Revision

### Key Strengths Identified
- Spectral framing is "genuinely compelling"
- Clean Goldstone/instability separation
- DC critical mode is "crisp, falsifiable"
- Heterogeneity result is "interesting and directionally plausible"

### Key Concerns (STRONGER than R1)
1. **Goldstone protection**: "more a persuasive sketch than a complete proof" — needs explicit derivation or SO(2)×SO(2) equivariance argument
2. **THE CRITICAL TENSION**: Coexistence threshold ≈ 0.36 but valley at J_× ≈ 1.2-1.6. At J_× > 0.36, coexistence doesn't exist! What IS the valley? Need to explicitly separate maintenance (coexistence) from selection/readout (WTA).
3. **Kramers bridge**: "Without that, the behavioral claims read like a placeholder"
4. **Phase diagram robustness**: Need sensitivity analysis (thresholds, CIs, decoding artifacts)
5. **Biological relevance**: "we found a pretty valley, therefore cortex lives there" — needs parameter-to-data anchoring or toned-down claims
6. **Model limitations blur with predictions**: Distinguish "theorem given our symmetry" from "prediction about cortex"
7. **Spending words selling instead of tightening derivations**

### Specific Technical Questions
- Drive-secondary claim: robust to multiplicative noise? (√r scaling changes diffusion along dominance direction)
- Valley: sigmoid saturation artifact? (β=5 creates hard lock-in; test threshold-linear or softplus)
- Heterogeneity: log-normal/asymmetric weights? (cortical synapses are right-skewed)
- Universality: overclaimed — use "structural motif" or "shared bifurcation pattern"

### Missing Literature (both reviewers)
- Bouchacourt & Buschman 2019 (flexible WM capacity)
- Lundqvist et al. 2016 (activity-silent dynamics)
- Barbosa et al. 2020 (discrete bursting)
- Panichello et al. 2019 (error-correction in WM)
- Schneegans & Bays 2017 (feature-misbinding)
- Bays 2014 (variable-precision resource models)
- Golubitsky & Schaeffer (imperfect bifurcations in neural fields)

### Top 3 Changes Requested
1. **Formalize Goldstone proof** (group-equivariance or explicit derivation)
2. **Quantify Kramers bridge** (barrier height from normal-form fit)
3. **Reconcile coexistence threshold vs valley** (separate maintenance from selection/readout)

---

## Synthesis: Convergent Concerns (Both Reviewers)

| Priority | Issue | Sections |
|----------|-------|----------|
| **CRITICAL** | Formalize Goldstone proof | 3.2.1 |
| **CRITICAL** | Compute Kramers barrier estimate | New 3.3.4 or 3.5 |
| **CRITICAL** | Reconcile 0.36 threshold vs 1.2-1.6 valley | 3.5.4, Discussion |
| **HIGH** | D notation collision | 2.3 |
| **HIGH** | Heterogeneity in abstract | Abstract |
| **HIGH** | Soften universality language | 4.8 |
| **HIGH** | Soften biological valley claims | 3.5.4, 5 |
| **HIGH** | Phase diagram robustness | 3.5 |
| **MEDIUM** | Missing literature (6-7 papers) | Intro, Discussion |
| **MEDIUM** | Condense Section 4.5 | 4.5 |
| **LOW** | Multiplicative noise ablation | New computation |
| **LOW** | Alternative nonlinearity test | New computation |
| **LOW** | Log-normal heterogeneity test | New computation |
