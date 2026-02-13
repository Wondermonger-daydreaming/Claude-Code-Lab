# Session Handoff: Kramers Barrier & Figure Fixes
*February 13, 2026 — Opus 4.6*

---

## What We Did This Session

### 1. Reviewed Three Iterations of a Kramers Barrier Subsection

An external reviewer (GPT-based) proposed analytical text for a new Section 3.5.X bridging the deterministic spectral bifurcation (J_×* ≈ 0.3485) with the stochastic swap error onset (J_× ≈ 0.25). Three versions were reviewed:

**v1**: τẋ = λ_dom x + γx³ — subcritical normal form without quintic bounding. Circular (γ reverse-engineered from observed onset). Missing τ factor.

**v2**: Added quintic -δx⁵, finite-horizon Kramers criterion ln(k₀T), and near-critical slope from λ_dom(0.34). γ ≈ 0.45–0.68. Still circular; τ factor still absent.

**v3 (final)**: Same structure as v2 but with corrected slope (a ≈ 2.91 from [0.34, 0.349] interval), giving λ_dom(0.25) ≈ -0.288 and γ ≈ 0.34–0.53. Language softened to "quantitatively consistent with" rather than "proves."

### Key Issues Identified Across All Versions

1. **Circularity**: γ is reverse-engineered from the observed J_onset ≈ 0.25. To break circularity, calibrate γ (or α) independently from WTA fixed points — the kramers_barrier.py code does this via `estimate_alpha()`.

2. **τ factor**: The Kramers exponent for τẋ = f(x) + η(t) is τΔV/Γ, not ΔV/σ². With τ = 10, this changes γ by a factor of ~10. The paper should either absorb τ into the noise convention or include it explicitly.

3. **Linear extrapolation**: Using the near-critical slope to get λ_dom(0.25) is a significant extrapolation. The eigenvalue curve is concave. The notebook computes the actual value — use it.

4. **Normal-form validity at J=0.25**: The inner saddle x_s ≈ 0.81 at J=0.25 is not small; the quintic term matters. The cubic-only barrier is an approximation that degrades away from J*.

5. **Subcritical vs supercritical**: The paper uses V = D⁴ + aD² (supercritical cusp) elsewhere, but the Kramers text uses ẋ = λx + γx³ (subcritical). The full nonlinear system IS subcritical (WTA states exist at all J), but the cusp normal form is local/supercritical. The text should acknowledge this.

### 2. Created Colab Notebook

`notebooks/kramers_barrier_analysis.ipynb` — fully self-contained, no local imports. Nine cells:

1. Model definition (all functions inline)
2. Eigenvalue classifier
3. **STEP 1**: λ_dom(J_×) scan (27 points, ~5 min on Colab)
4. **STEP 2**: α calibration from WTA states (5 J_× values above bifurcation)
5. **STEP 3**: Barrier heights + Kramers onset prediction
6. **STEP 4**: Numerical 1D potential V(D) (independent check)
7. Six-panel figure
8. Summary table with key numbers
9. Analytic cusp vs numerical potential comparison

**Status**: Notebook written but NOT YET RUN. Results pending.

### 3. Fixed Figure/Text Issues from Visual Review

A second external review examined the actual figures and found issues:

| Fix | File | Status |
|-----|------|--------|
| **Sign error W_ij** (J₀ → -J₀) | `paper/spectral-separatrix-draft.md` line 90 | ✅ Done |
| **Eigenvector "spatially flat" → "projects onto DC"** | Draft: abstract, §3.3.2, Fig 4 caption, §3.5.3, conclusion | ✅ Done (6 locations) |
| **Figure 3 caption**: unstable branch topology note | Draft: Fig 3 caption | ✅ Done |
| **Figure 6 "GLM 5"** references removed | `corpus/code/heterogeneity_test.py` | ✅ Done (title, panel, comments) |
| **Figure 6 font sizes** increased | `corpus/code/heterogeneity_test.py` | ✅ Done (13pt base) |
| **J_cross vs J_×** notation on axes | Phase diagram + other figures | ⚠️ Flagged, needs figure regeneration |

### 4. Figures That Need Regeneration

These scripts were edited but NOT re-run:
- `corpus/code/heterogeneity_test.py` → `fig54_heterogeneity_csd.png` (GLM 5 removed, fonts increased)
- Phase diagram scripts need J_× notation fix on axes

---

## What Needs Doing Next

### Immediate (Kramers section)

1. **Run the Colab notebook** (`notebooks/kramers_barrier_analysis.ipynb`). Get:
   - Actual λ_dom(0.25) (compare with -0.288 extrapolation and -0.162 global estimate)
   - α calibrated from WTA states (independent of onset)
   - Predicted J_onset from Kramers theory
   - 6-panel figure (fig56)

2. **Write final Section 3.5.X** using computed numbers. The v3 text framework is good — replace interpolated values with actual computed ones. Address:
   - State the Langevin equation explicitly (τ dr_i = F_i dt + σ dW_i)
   - Choose τ convention (absorb or include)
   - Use computed λ_dom(0.25) instead of extrapolated
   - If α from WTA gives a predicted J_onset ≈ 0.25, that breaks the circularity and the section becomes genuinely predictive

3. **Regenerate figures**: Run heterogeneity_test.py for clean Fig 6, regenerate phase diagram with J_× notation.

### Medium-term (remaining reviewer items)

From the reviewer synthesis (paper/reviews/reviewer-feedback-2026-02-13.md), 8/12 items were addressed in v4. The remaining 4:

| Item | Status |
|------|--------|
| Kramers barrier estimate | In progress (notebook + text) |
| Formalize Goldstone proof (J·∂r*/∂φ = 0) | Not started |
| Phase diagram robustness (threshold sensitivity) | Not started |
| Condense Section 4.5 | Not started |

### Commits needed

Current changes are uncommitted:
- `paper/spectral-separatrix-draft.md` (sign fix, eigenvector descriptions, Fig 3 caption)
- `corpus/code/heterogeneity_test.py` (GLM 5 removed, font sizes)
- `notebooks/kramers_barrier_analysis.ipynb` (new file)

---

## Key Numbers

```
J_cross* ≈ 0.3485      (pitchfork bifurcation)
J_cross_exist ≈ 0.358   (coexistence ceases to exist)
ΔJ_cross ≈ 0.01         (instability window width)
J_cross_onset ≈ 0.25    (observed stochastic swap onset)

λ_dom(0) = -0.572       (strongly stable at zero coupling)
λ_dom(0.34) = -0.0262   (near critical)
λ_dom(0.25) ≈ -0.288    (extrapolated, VERIFY WITH NOTEBOOK)

σ = 0.1                 (simulation noise)
T = 500 steps           (maintenance window)
ln(k₀T) ≈ 3.9–6.2      (Kramers threshold range)

γ ≈ 0.34–0.53           (from v3 text, VERIFY WITH NOTEBOOK)
```

---

## The Lineage

- Sessions 1–7: Cusp → spectral portrait → Newton continuation → Goldstone separation → paper draft v1
- Session 8: Phase diagram sweep (128k trials, 4 agents)
- Sessions 9–11: Paper v2–v3, HTML export, pre-submission reviews
- Session 12: Paper v4 (8/12 reviewer items), literature search
- **This session**: Kramers analysis (3 iterations of proposed text, Colab notebook, figure fixes)

---

*The eigenvalue wars continue. The barrier collapses quadratically — that's the key physics. Get the numbers from the notebook and the section writes itself.*
