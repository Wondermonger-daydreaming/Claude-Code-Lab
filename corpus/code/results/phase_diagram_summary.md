# Phase Diagram: Swap Errors in Coupled Ring Attractors

**Date:** February 12, 2026
**Method:** Autonomous 4-agent parallel parameter sweep
**Figure:** `figures/fig55_phase_diagram_swap_errors.png`

---

## Setup

Four parallel agents swept a 256-point grid across the (J_cross, drive_strength) parameter space of a coupled ring attractor model. Each point ran 500 stochastic trials (128,000 total trials). Two ring attractor networks (N=48 neurons each, sigmoid activation, cosine connectivity) competed via mean-field cross-inhibition. Network A received item 1, Network B received item 2 (separated by π/2 radians). Swap errors were classified as decoded responses within 0.3 rad of the non-target item.

## Key Results

| Metric | Value |
|--------|-------|
| Total grid points | 256 (8×8 per agent × 4 agents) |
| Points with swap rate > 5% | **240 / 256 (93.8%)** |
| Maximum swap rate | **51.8%** (J_cross=8.0, drive=4.1) |
| Numerical failures (NaN/explosion/collapse) | **0** |
| Total simulation time | ~33 min (4 agents × ~33 min, parallel) |

### The Phase Transition

Swap errors emerge at **J_cross ≈ 0.25–0.30**, consistent with the spectral analysis prediction of a pitchfork bifurcation at J_cross* ≈ 0.3485. The transition is gradual in the stochastic model (noise smears the sharp bifurcation), but the critical J_cross band matches the eigenvalue crossing.

- **Below J_cross ≈ 0.25:** Both bumps coexist stably. Correct rate > 90%. Swap rate ≈ 0%.
- **J_cross ≈ 0.3–0.5:** Transitional regime. Swap rate 20–45%. Both outcomes are common.
- **Above J_cross ≈ 1.0:** Pure winner-take-all. Swap rate → 50%. Each network wins with equal probability — the model has become a biased coin flip.

### Drive Strength Is Secondary

Across all four agents, drive strength (input_gain from 1.0 to 8.0) had minimal effect on swap error rates compared to J_cross. The phase diagram shows near-vertical isocontours in Panel A, meaning the swap rate is essentially a function of J_cross alone. This is consistent with the spectral finding that the critical eigenvector is **uniform/DC** — the instability is in total activity competition, not spatial pattern encoding.

### Competition Index

The competition index (swap/(swap+correct)) provides a clean measure of WTA strength:
- At J_cross = 0.2: competition index ≈ 0 (no competition)
- At J_cross = 0.5: competition index ≈ 0.45 (strong but asymmetric)
- At J_cross > 2.0: competition index ≈ 0.50 (symmetric coin flip)

The approach to 0.5 confirms that at high cross-inhibition, the system is a pure noise-driven bistable switch with no memory of which network received which item.

## Interpretation

**The coupled ring attractor model robustly produces swap errors** through a winner-take-all mechanism governed by the cross-inhibition strength J_cross. The spectral separatrix at J_cross* ≈ 0.3485 marks the onset of competition. Above this threshold, noise during the maintenance period determines which network survives, producing stochastic swaps in the decoded response.

This connects the spectral analysis (eigenvalue crossing at the bifurcation) to behavioral phenomenology (swap errors in working memory tasks). The model predicts:

1. **Swap error rate should increase with set size** — more networks competing increases the probability of a non-target win
2. **Swap errors should cluster at specific non-target locations** — not diffuse errors, but discrete jumps to other items' positions
3. **The transition should be sharp in low-noise conditions** — noise smears the bifurcation, but the underlying phase transition is abrupt

These predictions are testable against psychophysical data from Zhang & Luck (2008) and Bays et al. (2009).

## Files

- `coupled_ring_sweep.py` — Simulation harness
- `synthesize_phase_diagram.py` — Phase diagram synthesis
- `alternative_activations.py` — Alternative activation fallback (not needed)
- `results/agent_{1,2,3,4}.json` — Raw results from 4 agents
- `figures/fig55_phase_diagram_swap_errors.png` — Phase diagram figure
