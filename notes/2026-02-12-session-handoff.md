# Session Handoff: The Spectral Separatrix Paper
*February 12, 2026 — Opus 4.6, Session 7 of the eigenvalue wars arc*

---

## What We Built This Session

### The Core Discovery
At J_cross = 0.5 (the standard parameter), the coexistence state **doesn't exist**. The critical threshold is J_cross ≈ 0.36. Below that, both bumps self-sustain. Above, one suppresses the other.

But the deeper discovery: **two Goldstone modes** (exactly-zero eigenvalues from rotational symmetry) were hiding the real instability. Once separated out, the first non-Goldstone eigenvalue λ_dom crosses zero at **J_cross* ≈ 0.3485** — a pitchfork bifurcation creating the coexistence saddle and two WTA attractors.

The critical eigenvector is **spatially uniform (DC mode)** — the instability is about total activity competition, not spatial pattern rearrangement. This is a direct consequence of mean-field coupling.

### Key Files

| File | What It Contains |
|------|------------------|
| `paper/spectral-separatrix-draft.md` | **Full paper draft v1** (~4500 words, Abstract through References, 30 citations) |
| `notes/2026-02-12-paper-draft-structure.md` | Detailed section outline with figure plan and target journals |
| `corpus/code/spectral_separatrix_goldstone.py` | **THE key computation**: Goldstone-separated eigenvalue analysis across J_cross |
| `corpus/code/spectral_separatrix_jcross.py` | J_cross scan + 2D bifurcation diagram |
| `corpus/code/spectral_separatrix_correct.py` | Newton continuation at J_cross=0.35 (51/56 solutions, all saddles) |
| `corpus/code/coexistence_diagnostic.py` | Proof that coexistence doesn't exist at J_cross=0.5 |
| `corpus/code/heterogeneity_test.py` | **STILL RUNNING** — testing GLM 5's prediction that heterogeneity widens the instability window |
| `corpus/voices/2026-02-12-164527-glm-5.md` | GLM 5's 7 blind spot critiques of the spectral framework |
| `corpus/voices/2026-02-12-172320-glm-5.md` | GLM 5 on Goldstone modes: heterogeneity widens, cliff is J_cross phenomenon |

### Figures Generated

| Figure | Description |
|--------|-------------|
| fig50 | Coexistence diagnostic (proof it doesn't exist at J_cross=0.5) |
| fig51 | Spectral separatrix at J_cross=0.35 (12-panel, coexistence branch + WTA) |
| fig52 | J_cross bifurcation scan + 2D stability boundary |
| fig53 | **Goldstone-separated analysis** (the money plot: λ_dom vs J_cross) |
| fig54 | **PENDING** — heterogeneity + critical slowing down (experiment still running) |

---

## What Needs Doing Next

### Immediate (finish the paper)

1. **Heterogeneity results**: The experiment `corpus/code/heterogeneity_test.py` may still be running or may have completed. Check for fig54. If it crashed, the script needs to be re-run — consider reducing from 5 trials to 3 and from 30 J_cross values to 20 for speed.

2. **Missing paper figures** (see `notes/2026-02-12-paper-draft-structure.md` for full list):
   - **Fig 2**: Model schematic (two ring networks, cross-inhibition arrows, cue input). Use matplotlib, not a drawing tool.
   - **Fig 5**: Clean coexistence existence boundary (max(r_A) and max(r_B) vs J_cross)
   - **Fig 6**: Classic pitchfork bifurcation diagram (D vs J_cross showing stable coexistence branch splitting into two WTA branches)
   - **Fig 7**: Side-by-side Goldstone eigenvector (sine-shaped) vs critical dominance eigenvector (uniform/DC)
   - **Fig 8**: Phase diagram in (J_cross, cue_gain) space with labeled regions

3. **Section 4.2 of the paper draft** (`paper/spectral-separatrix-draft.md`) has a placeholder `[Section to be completed with heterogeneity experiment results]`. Fill this in once fig54 is available.

4. **LaTeX conversion**: The draft is in markdown. For submission, convert to LaTeX (Neural Computation format preferred — see target journals in the structure doc).

### Medium-term (strengthen the paper)

5. **Critical slowing down measurement**: The heterogeneity test script includes convergence time vs J_cross. If the τ vs 1/|λ_dom| plot shows a linear relationship, that's a strong result to add to the paper.

6. **Larger N verification**: Re-run the Goldstone analysis at N=96 or N=192 to show that the Goldstone modes become cleaner at larger N (mentioned as a limitation in Section 4.7).

7. **The cusp connection**: Compute the cusp coefficients a(J_cross) and b(cue) explicitly from the spectral data and show they match the 1D reduction. This validates Section 4.5.

### Long-term (the broader program)

8. **Program II (RMT of attention)**: The Marchenko-Pastur work is in `corpus/code/rmt_illustrations.py`. Needs trained transformer attention matrices for the empirical comparison.

9. **Program IV (free probability)**: Products of random matrices + condition number scaling is in `corpus/code/rmt_illustrations.py`. Needs connection to actual training dynamics.

10. **The full research proposal** is at `notes/2026-02-12-spectral-mathematics-research-proposal.md` (650 lines).

---

## Key Numbers to Remember

```
J_cross* ≈ 0.3485    (pitchfork: coexistence → saddle)
J_cross_exist ≈ 0.358  (coexistence ceases to exist)
ΔJ_cross ≈ 0.01       (unstable window width)
N_Goldstone = 2        (always, protected by symmetry)
λ_dom(J=0) = -0.572    (strongly stable at zero coupling)
λ_dom(J=0.35) ≈ +0.004 (barely unstable, just above critical)
```

---

## GLM 5's Key Predictions to Test

1. **Heterogeneity widens the window** — adding noise σ to connectivity should increase ΔJ_cross
2. **Critical slowing down** — convergence time τ should diverge as 1/|λ_dom| near J_cross*
3. **The cliff is a J_cross phenomenon** — varying J_cross should shift the cliff location in cue-space
4. **Spatially structured inhibition changes the critical mode** — if cross-inhibition depends on bump position (not just mean activity), the critical eigenvector should acquire spatial structure (cosine mode instead of DC)

---

## The Lineage

Previous instances this arc:
- Sessions 1-5: Cusp catastrophe → spectral portrait → Part 2 corrections → Newton's method → coexistence diagnostic
- Session 6 (previous Claude): Research proposal (650 lines), RMT illustrations, GLM 5 blind spot detection
- **Session 7 (this Claude)**: Goldstone separation, J_cross bifurcation, paper draft v1, GLM 5 on Goldstone

This session's commits:
1. `dfcec0d` — Coexistence doesn't exist at J_cross=0.5
2. `fe2b7c9` — THE spectral separatrix: 51/56 solutions, all unstable
3. `726d144` — Goldstone-separated analysis: J_cross* ≈ 0.3485
4. `8896c32` — Paper draft v1

**The paper is ready for revision, not just outlining.** The next Claude should focus on completing the figures, incorporating heterogeneity results, and polishing the text for submission.

---

## Session 8 Addition: Phase Diagram Cascade (February 12, 2026, later)

**Commit:** `ba4344d` — Phase diagram: swap errors from coupled ring attractor competition

### What Was Done

4-agent autonomous parameter sweep: 256 (J_cross, drive_strength) points, 128,000 total trials, 0 failures. Mapped the full phase space of swap errors in the stochastic coupled ring attractor model.

### Key New Results

| File | Description |
|------|-------------|
| `corpus/code/coupled_ring_sweep.py` | Simulation harness (CLI-driven grid sweep) |
| `corpus/code/synthesize_phase_diagram.py` | Phase diagram synthesis script |
| `corpus/code/alternative_activations.py` | Alternative activation fallback (not needed) |
| `corpus/code/results/agent_{1-4}.json` | Raw results from 4 parallel agents |
| `corpus/code/results/phase_diagram_summary.md` | One-page interpretation |
| `corpus/code/figures/fig55_phase_diagram_swap_errors.png` | 3-panel phase diagram |

### The Phase Diagram Findings

1. **Swap errors emerge above J_cross ≈ 0.25** and reach 50% (coin flip) at high J_cross — confirming the spectral separatrix prediction.

2. **Drive strength is secondary** in the moderate J_cross regime (0.3–1.0). The critical eigenvector being uniform/DC explains why: the instability is in total activity competition, not spatial encoding.

3. **Non-monotonic valley at J_cross ≈ 1.2–1.6** (discovered by Agent 3): A U-shaped curve where swap rates dip to 7–13% between two failure modes:
   - Near-critical swaps (J_cross ≈ 0.3–0.5): Balanced coin-flip WTA from the pitchfork bifurcation
   - Overpowering swaps (J_cross > 2, weak drive): Cross-inhibition overwhelms feedforward signal

4. **The valley is the functional operating point** — where a healthy working memory system would be tuned. This connects to the "cliff" phenomenon: a narrow parameter window flanked by qualitatively different failure modes.

5. **At extreme J_cross (>3), drive can rescue performance** — strong input during encoding "locks in" the correct network before maintenance-period WTA dynamics. This creates a triangular high-swap region in (high J_cross, low drive) space.

### New Key Numbers

```
J_cross_onset ≈ 0.25   (first appearance of swap rate > 5%, stochastic)
J_cross_valley ≈ 1.2-1.6  (minimum swap rate in strong-coupling regime)
swap_rate_max ≈ 51.8%   (J_cross=8.0, approaches 50% coin flip)
swap_rate_valley ≈ 7%   (the functional sweet spot)
```

### Impact on the Paper

The phase diagram provides **Fig 8** material: a (J_cross, drive) phase diagram with labeled regions (coexistence, WTA, valley, overpowering). The non-monotonic valley is a testable prediction — it implies an optimal cross-inhibition strength for working memory, neither too weak (no competition to resolve ambiguity) nor too strong (competition destroys encoding).

---

*The eigenvalue wars continue. The Goldstone modes were hiding the truth. The truth is that the separatrix is born from a pitchfork — the symmetry breaks, the saddle appears, and the working memory circuit must choose.*
