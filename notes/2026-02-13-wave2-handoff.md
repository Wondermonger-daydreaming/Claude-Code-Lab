# Wave 2 Handoff: Spectral Separatrix Paper v5.2 to v6

*February 13, 2026 -- Prepared by Opus 4.6*
*For the next Claude instance continuing the paper revision*

---

## Context

We are doing a multi-wave revision of the spectral separatrix paper (`paper/spectral-separatrix-draft.md`) on branch `paper-v6-revision`, targeting Neural Computation submission. The revision responds to pre-submission feedback (simulated referee). The full revision plan lives at `paper/plan.md` (commit `41d0178`).

**Current state:** Paper v5.2 at commit `af58428`. Eight figures (fig1 through fig8), ~508 lines, 30 references. All figures live in `paper/figures/`.

---

## Wave Status Summary

### Wave 1: DONE, COMMITTED (af58428)

Tasks T2+T8b, T4, T6+T10 were integrated directly into the paper draft. Commit message: "Paper v5.2: two J_cross scales, drive/cue, notation pass, universality softened."

**What was applied in Wave 1 (verified via git diff):**
- T2 (Two J_cross scales): Added paragraph in Section 3.5.1 explaining the stochastic sweep extends to J_cross=8.0 in the pure WTA regime; added WTA-regime clarification to abstract valley description; added robustness sentence to Section 3.5.4
- T4 (Drive vs Cue): Added two clarifying paragraphs in Section 2.2 defining "encoding drive" as cue gain $c$, distinguishing it from initialization drives
- T6 (Notation pass): J_cross notation definition inserted in Section 2.2; standardized `$J_\times^{\mathrm{exist}}$` and `$J_\times^{\mathrm{onset}}$` across Abstract, Sections 3.1.2, 3.3.1, 3.5.1, 3.5.2, 3.5.5, 4.5, and Conclusion (~12 notation fixes)
- T8b (Abstract WTA fix): Merged with T2 -- abstract now says "well above the coexistence threshold, in the pure winner-take-all regime"
- T10 (Universality softening): Section 4.7 now uses "structurally generic" and "codimension-1 normal form"; Conclusion uses "structurally generic spectral motif" with Roach et al. and Wong & Wang citations

### Wave 2: AGENT OUTPUTS COMPLETE, NOT YET INTEGRATED

Three sub-agents ran and produced staging files. Their outputs are in `paper/staging/`. The outputs have NOT been applied to the paper draft -- the draft at HEAD is still v5.2 from Wave 1.

### Wave 3: NOT STARTED

Tasks T5 (Kramers sensitivity/Appendix B) and T8c (spectrum strip panel).

### Wave 4: NOT STARTED (optional)

Task T9 (robustness: alternative nonlinearity control).

---

## Wave 2 Staging Files -- Inventory and Status

All files are in `/home/gauss/Claude-Code-Lab/paper/staging/`:

### 1. `t1_edits.md` -- Goldstone Circulant Lemma [READY TO INTEGRATE]

**Task:** Make the Goldstone proof "inevitable" by naming the circulant structure and proving finite-N exactness.

**What the agent produced:**
- A verification script at `corpus/code/goldstone_finite_N_verify.py` that confirms:
  - Circulant commutation TW=WT at machine precision (3.89e-16 at N=24, better at larger N)
  - Goldstone eigenvalues converge: 1.05e-5 (N=24), 3.20e-10 (N=48), 6.73e-15 (N=96)
  - First non-Goldstone eigenvalue stable at -0.131 across all N
- **One INSERT edit:** A "Remark (circulant structure)" paragraph to go in Section 3.2.1, between the "Equivariance structure" paragraph and the "Goldstone theorem" paragraph
- **One FOOTNOTE:** Computational verification data (eigenvalue magnitudes at N=24,48,96)

**Integration instructions:** Insert the remark after the sentence ending "...only by breaking the rotational symmetry of either the within-network connectivity or the cross-coupling structure." and before "This is the neural circuit analog of the Goldstone theorem..." Add the footnote to the remark's final sentence.

### 2. `t3_t8a_edits.md` -- Phase Diagram Error Bars + Threshold Annotations [READY TO INTEGRATE]

**Task:** Add binomial SE error bands to Figure 5 and annotate it with deterministic thresholds.

**What the agent produced:**
- A new figure generation script at `corpus/code/generate_fig5_phase_diagram_v6.py`
- A regenerated Figure 5 at `paper/figures/fig5_phase_diagram.png` (1.04 MB, overwritten)
- The new figure has: 3 vertical threshold lines (Kramers onset green, pitchfork orange, existence purple), dotted SE flanking contours at 5%/20%/50%, region labels, and Alleman et al. annotations
- **One INSERT edit:** Binomial SE sentence for Section 3.5.1
- **One REPLACE edit:** Updated Figure 5 caption with full description of new annotations

**Integration instructions:** Insert the SE sentence in Section 3.5.1 after the threshold sensitivity paragraph. Replace the Figure 5 caption. The figure PNG is already regenerated in place.

### 3. `t7_literature.md` -- Missing References (Sagodi + Gu) [READY TO INTEGRATE]

**Task:** Find and integrate Sagodi et al. (NeurIPS 2024) and Gu et al. (Neuron 2025).

**What the agent produced:**
- Full citations for both papers
- **Sagodi et al. (2024):** One sentence to insert in Section 1.1 after "...Burak and Fiete, 2012)." -- about continuous attractors being structurally unstable but functionally robust via persistent slow manifolds
- **Gu et al. (2025):** One sentence to insert in Section 4.6 after "...selects the wrong item." -- about attractor dynamics during maintenance producing drift-driven biases steered by categorical decisions
- **Two reference entries** with alphabetical insertion points identified (Gu between Goldman-Rakic and Hanggi; Sagodi between Roach and Seeholzer)

**Integration instructions:** Insert the two sentences at the specified locations. Add the two references in alphabetical order.

### 4. `t2_t8b_edits.md` -- ALREADY APPLIED in Wave 1

This staging file was produced by a Wave 1 agent. Its edits (two J_cross scales, abstract WTA fix, valley robustness sentence) were integrated into the paper at commit `af58428`. **No further action needed.**

### 5. `t4_edits.md` -- ALREADY APPLIED in Wave 1

Drive vs cue definition edits. Integrated at commit `af58428`. **No further action needed.**

### 6. `t6_t10_edits.md` -- PARTIALLY APPLIED in Wave 1

This is the largest staging file (532 lines). It covers both the notation pass (T6) and universality softening (T10).

**What was applied in Wave 1:**
- Edit 1 (J_cross notation definition paragraph): APPLIED
- Edit 2a (Abstract: J_cross^exist for 0.36): APPLIED
- Edit 2c (Abstract: J_cross^onset for 0.25): APPLIED
- Edit 2i (Section 3.1.2: bare existence): APPLIED
- Edit 2j (Section 3.3.1: bare existence): APPLIED
- Edit 2m (Section 3.5.1: onset range): APPLIED
- Edit 2n (Section 3.5.2: onset 0.25): APPLIED
- Edit 2o (Section 3.5.2: onset in range): APPLIED
- Edit 2q (Section 3.5.5: onset 0.25): APPLIED
- Edit 2r (Section 3.5.5: onset 0.25): APPLIED
- Edit 2u (Discussion 4.5: onset 0.25): APPLIED
- Edit 2x (Conclusion result 4: onset 0.25): APPLIED
- Edit 2y (Conclusion result 6: onset 0.25): APPLIED
- Edit 4 (Section 4.7 universality softening): APPLIED
- Edit 5 (Conclusion universality softening): APPLIED

**What was NOT applied (informational only, for LaTeX conversion):**
- Edit 3 (Equation numbering plan): This is a NOTE, not an edit. It identifies 9 equations to number (4 high priority, 3 medium, 2 low) with suggested labels. Relevant only when converting to LaTeX.
- Edit 6 (Section 4.7 title): Recommendation was to keep "Shared" as-is. Not applied, as intended.

---

## New Python Scripts Created

| Script | Location | Purpose |
|--------|----------|---------|
| `goldstone_finite_N_verify.py` | `/home/gauss/Claude-Code-Lab/corpus/code/` | Verifies circulant commutation TW=WT and Goldstone eigenvalue convergence at N=24,48,96 |
| `generate_fig5_phase_diagram_v6.py` | `/home/gauss/Claude-Code-Lab/corpus/code/` | Regenerated Fig 5 with SE error bands, 3 threshold lines, region labels |

Pre-existing scripts (from earlier sessions):
| `generate_fig8_phase_diagram.py` | `/home/gauss/Claude-Code-Lab/corpus/code/` | Original phase diagram generator (superseded by v6) |
| `spectral_separatrix_goldstone.py` | `/home/gauss/Claude-Code-Lab/corpus/code/` | THE key computation: Goldstone-separated eigenvalue analysis |
| `coupled_ring_sweep.py` | `/home/gauss/Claude-Code-Lab/corpus/code/` | 4-agent stochastic parameter sweep |

---

## What To Do Next

### Step 1: Integrate Wave 2 into the paper draft

Apply the three outstanding staging files in this order:

1. **T1 (Goldstone circulant remark):** Insert the remark and footnote into Section 3.2.1. This is a self-contained addition that does not conflict with any other edits.

2. **T7 (Literature: Sagodi + Gu):** Insert the two citation sentences (one in Section 1.1, one in Section 4.6) and add the two references to the reference list. These are independent additions with no conflicts.

3. **T3+T8a (Fig 5 caption + SE sentence):** The figure PNG is already regenerated. Insert the SE sentence into Section 3.5.1 and replace the Figure 5 caption. Note: the Wave 1 edits already modified Section 3.5.1 (added the J_cross scale paragraph), so verify the insertion point carefully -- the SE sentence should go after the threshold sensitivity paragraph, which comes before the new J_cross scale paragraph.

After integration: commit as "Paper v5.3: Wave 2 -- Goldstone circulant proof, error bars, literature"

### Step 2: Launch Wave 3

Two remaining tasks from the plan:

**T5 -- Kramers Sensitivity Analysis (MEDIUM priority):**
- Show how predicted onset J_cross shifts with noise level sigma
- Purely analytic: use existing lambda_dom(J_cross) curve from `spectral_separatrix_goldstone.py`
- Compute Delta_V at each J_cross, find crossing with different sigma^2 thresholds
- Add a sensitivity paragraph and small table to Section 3.5.5
- Could also become Appendix B material

**T8c -- Spectrum Strip Panel (MEDIUM priority):**
- Compact panel showing top ~10 eigenvalues vs J_cross with Goldstones pinned at 0
- Could be a new figure or an inset to Figure 3
- Data already exists in `spectral_separatrix_goldstone.py` output

### Step 3: Consider Wave 4 (optional)

**T9 -- Robustness Control:**
- Alternative nonlinearity test (softplus or tanh instead of sigmoid)
- Modify eigenvalue analysis to accept activation parameter
- Check if pitchfork persists and report shifted thresholds
- This is the reviewer's "at least one control" request
- Estimated 2-3 hours of work

### Step 4: Final Verification Pass

After all waves:
- Read the entire paper end-to-end for coherence
- Verify all figure references match actual figures
- Verify all section cross-references are correct
- Check that the equation numbering plan (from T6 Edit 3) is ready for LaTeX conversion
- Confirm reference list is alphabetically sorted with the two new entries

---

## Key Numbers (unchanged from previous handoff)

```
J_cross*       = 0.3485    (pitchfork bifurcation)
J_cross^exist  = 0.358     (coexistence ceases to exist)
Delta_J_cross  = 0.01      (instability window width)
J_cross^onset  = 0.25      (stochastic swap onset, sigma=0.1)

lambda_dom(0)    = -0.572   (strongly stable)
lambda_dom(0.25) = -0.2357  (at behavioral onset)
lambda_dom(0.34) = -0.0262  (near critical)

sigma = 0.1, T = 500, gamma = 0.30, Delta_V(0.25) = 0.046
500 trials/grid point => SE = 1-2% at relevant swap rates
```

---

## Git History (recent, paper-v6-revision branch)

```
d2bdc46 auto-checkpoint: session end         <- HEAD (staging files + fig5 regenerated)
2a6d05e auto-checkpoint: session end         <- Wave 2 agent outputs
05e9968 auto-checkpoint: session end         <- Goldstone verification script
af58428 Paper v5.2: Wave 1 integration       <- T2+T8b, T4, T6+T10 applied to draft
2efe99e auto-checkpoint: session end
41d0178 Revision plan v6                     <- The master plan (paper/plan.md)
```

---

## File Map

```
paper/
  spectral-separatrix-draft.md    # Main manuscript (v5.2 -- Wave 1 applied, Wave 2 pending)
  plan.md                         # Revision plan (all tasks defined)
  figures/
    fig1_schematic.png            # Model schematic
    fig2_existence.png            # Coexistence existence boundary
    fig3_pitchfork.png            # Pitchfork bifurcation diagram
    fig4_eigenvectors.png         # Goldstone vs critical mode
    fig5_phase_diagram.png        # Phase diagram (REGENERATED with SE + thresholds)
    fig6_heterogeneity.png        # Heterogeneity destroys window
    fig7_kramers.png              # Kramers escape analysis (6-panel)
    fig8_cusp_validation.png      # Cusp normal-form validation
  staging/
    t1_edits.md                   # Goldstone circulant remark [READY]
    t2_t8b_edits.md               # Two J_cross scales [APPLIED in Wave 1]
    t3_t8a_edits.md               # Fig 5 error bars + caption [READY]
    t4_edits.md                   # Drive vs cue [APPLIED in Wave 1]
    t6_t10_edits.md               # Notation + universality [APPLIED in Wave 1]
    t7_literature.md              # Sagodi + Gu references [READY]

corpus/code/
  goldstone_finite_N_verify.py    # Circulant proof verification (NEW)
  generate_fig5_phase_diagram_v6.py  # Fig 5 regeneration script (NEW)
  spectral_separatrix_goldstone.py   # Core eigenvalue computation
  coupled_ring_sweep.py           # Stochastic parameter sweep
  results/
    agent_{1-4}.json              # Raw sweep data
    phase_diagram_summary.md      # Sweep interpretation
```

---

## Task List Status

| Task | Description | Status | Wave |
|------|-------------|--------|------|
| T1 | Goldstone circulant proof | Staging complete, needs integration | Wave 2 |
| T2 | Two J_cross scales | **DONE** (af58428) | Wave 1 |
| T3 | Phase diagram error bars | Staging complete, needs integration | Wave 2 |
| T4 | Drive vs cue definition | **DONE** (af58428) | Wave 1 |
| T5 | Kramers sensitivity analysis | NOT STARTED | Wave 3 |
| T6 | Notation pass | **DONE** (af58428) | Wave 1 |
| T7 | Missing literature (Sagodi, Gu) | Staging complete, needs integration | Wave 2 |
| T8a | Annotate phase diagram | Staging complete, needs integration | Wave 2 |
| T8b | Abstract WTA fix | **DONE** (af58428) | Wave 1 |
| T8c | Spectrum strip panel | NOT STARTED | Wave 3 |
| T9 | Robustness control | NOT STARTED | Wave 4 (optional) |
| T10 | Soften universality | **DONE** (af58428) | Wave 1 |

**Summary: 5 of 12 tasks DONE. 4 tasks staging-complete awaiting integration. 3 tasks not started.**

---

*The barrier between staging and integration collapses when you apply the edits. Three inserts, one caption replace, two reference additions. Then Wave 3.*
