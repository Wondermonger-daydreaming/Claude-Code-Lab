# Revision Plan: Spectral Separatrix Paper v5.1 → v6

*February 13, 2026 — Prepared by Opus 4.6 (Session 15)*
*For future Claude instances inheriting this paper*

---

## Context

The paper received detailed pre-submission feedback (likely from an LLM reviewer simulating a Neural Computation referee). Verdict: **Major Revision — promising, can land in Neural Computation.** All CRITICAL and HIGH items from the *previous* review round (Session 14) are already addressed. This plan targets the *new* feedback.

**Current state:** Paper v5.1 at commit `30e6dc4`. Eight figures (1–8), ~490 lines, 23 references. PDF at `paper/spectral-separatrix-draft.pdf` (2.1 MB).

**Key files:**
- `paper/spectral-separatrix-draft.md` — main manuscript
- `paper/figures/` — all 8 figure PNGs
- `notebooks/kramers_barrier_analysis.ipynb` — Colab notebook (fixed)
- `corpus/code/threshold_robustness.py` — threshold robustness script
- `corpus/code/results/threshold_robustness.json` — robustness data
- `notes/2026-02-13-session-handoff-v5.md` — Session 14 handoff
- `paper/reviews/reviewer-feedback-2026-02-13.md` — previous review

---

## Reviewer Feedback Summary

### Strengths (no action needed — these are working)
- Spectral framing is the right tool and actually used properly
- Clear, falsifiable structural predictions (DC critical mode)
- Theory-to-behavior bridge is unusually concrete (128k trials)
- Heterogeneity result is persuasive
- Valley regime narrative is intellectually honest

### Weaknesses Requiring Action

| ID | Issue | Priority | Effort | Section |
|----|-------|----------|--------|---------|
| A | Goldstone proof: formal but not "inevitable" | **HIGH** | Medium | §3.2.1 |
| B | Two J_× scales confusion | **HIGH** | Low | §2.2, §3.5.1, Abstract |
| C | Kramers sensitivity to γ and σ | **MEDIUM** | Medium | §3.5.5 |
| D | Claims must match model simplicity | **LOW** | Low | Throughout |
| E | Phase diagram needs error bars | **HIGH** | Medium | §3.5.1, Fig 5 |
| F | Notation/definitional hygiene | **MEDIUM** | Low | §2.2, Throughout |

### Missing Literature
| Paper | Status | Action |
|-------|--------|--------|
| Alleman et al. PNAS 2024 | ✅ Already cited | None |
| Penny 2024 | ✅ Already cited | None |
| Ságodi et al. NeurIPS 2024 | ❌ Not cited | Find and integrate |
| Gu et al. Neuron 2025 | ❌ Not cited | Find and integrate |

### Presentation Changes
| Item | Priority | Section |
|------|----------|---------|
| "Spectrum strip" panel (eigenvalues vs J_×) | **MEDIUM** | New Fig or modify Fig 3 |
| Annotate phase diagram with J_×*, J_×^exist | **HIGH** | Fig 5 |
| Abstract: clarify valley is pure WTA regime | **HIGH** | Abstract |
| Define "drive" vs "cue" early | **MEDIUM** | §2.2 |

---

## Detailed Action Items

### TASK 1: Goldstone Lemma — Make It Inevitable [HIGH, §3.2.1]

**Current state:** §3.2.1 (lines 164–186) has a formal 2-step proof + equivariance paragraph. It proves:
1. Rotational derivative is null vector of uncoupled block
2. Mean-field coupling annihilates rotational mode (because ∑∂r_j/∂φ = 0)
3. SO(2)×SO(2) equivariance protects two Goldstones

**What's missing (per reviewer):**
- The word "circulant" never appears — but W_ij IS exactly circulant by construction
- No explicit statement about finite-N exactness
- The algebraic commutation is implicit, not shown

**Action:**
1. **Add a remark after the equivariance paragraph** (after line 186) that explicitly states:
   > "The within-network connectivity $W_{ij} = \frac{1}{N}(-J_0 + J_1 \cos(\theta_i - \theta_j))$ is exactly circulant: $W_{ij} = w(i-j \mod N)$ for all $N$. The circulant structure ensures that the discrete rotation operator $T: r_i \mapsto r_{i+1 \mod N}$ commutes with $\mathbf{W}$, i.e., $T\mathbf{W} = \mathbf{W}T$. Because the fixed-point equation $-\mathbf{r}^* + \sigma(\mathbf{W}\mathbf{r}^*) = 0$ is solved by any rotation $T^k \mathbf{r}^*$, the nullspace of the Jacobian contains the rotational tangent vector $\partial \mathbf{r}^*/\partial \varphi$ at *every* $N$, not merely in the continuous limit. The protection is exact at finite $N$, not an asymptotic approximation."

2. **Verify claim computationally**: Run eigenvalue analysis at N=24, 48, 96 and show Goldstone eigenvalues remain at machine precision. This could be a one-line table or footnote.

**Key insight for implementer:** The circulant structure is already present in the model definition (§2.1, line 92). The proof already uses it implicitly. This is about making the implicit explicit — name the property, show the commutation, state the finite-N consequence.

---

### TASK 2: Resolve the Two J_× Scales [HIGH, §2.2 + §3.5.1 + Abstract]

**The problem:** The deterministic analysis covers J_× ∈ [0, 0.36]. The stochastic sweep covers J_× ∈ [0.05, 8.0]. The valley sits at J_× ≈ 1.2–1.6. The reviewer asks: are these the same J_×? Is there a hidden rescaling?

**The answer:** Yes, they are the same J_×. The stochastic sweep uses the identical model equations (§2.2) at J_× values far above the coexistence threshold. Above J_×^exist ≈ 0.36, coexistence doesn't exist — only WTA solutions exist. The sweep explores how WTA behavior changes with coupling strength. The valley at J_× ≈ 1.2–1.6 is a WTA-regime phenomenon where two different failure modes compete.

**Action:**
1. **Add a paragraph to §3.5.1** (after the sweep description, around line 271) explicitly stating:
   > "The stochastic sweep extends to $J_\times = 8.0$, well beyond the coexistence existence threshold $J_\times^{exist} \approx 0.36$. For $J_\times > J_\times^{exist}$, the system admits only WTA solutions; the stochastic trials begin from a coexistence-like initial condition (both bumps established by strong drives) and the dynamics reveal which network captures the WTA state. This extended range is necessary to characterize the full behavioral landscape, including the non-monotonic valley at $J_\times \approx 1.2$–$1.6$ (Section 3.5.4), which operates in the pure WTA regime. The cross-inhibition parameter $J_\times$ has the same definition throughout: the coefficient in the mean-field coupling term $J_\times \bar{r}^X$ (Eq. 2). No rescaling is applied between the deterministic and stochastic analyses."

2. **Update the abstract** (line 22) to clarify:
   > Change "a non-monotonic valley at intermediate $J_\times$ identifies a functional operating regime for working memory" to "a non-monotonic valley at intermediate $J_\times \approx 1.2$–$1.6$ — well above the coexistence threshold, in the pure winner-take-all regime — identifies a functional operating regime for working memory"

3. **Add a sentence to §3.5.4** (valley discussion, around line 289) noting that the valley's location in parameter space is model-dependent (specific to the sigmoid parameters), but the qualitative two-failure-mode structure is the robust finding.

**Key insight for implementer:** This is primarily a *writing* task, not a computation. The physics is already correct — the paper just doesn't make the reader's bridge explicit enough.

---

### TASK 3: Phase Diagram Error Bars [HIGH, §3.5.1 + Fig 5]

**Current state:** 500 trials per grid point, swap rates reported as point estimates. No error bars anywhere.

**The math:** For swap probability p estimated from n=500 trials:
- SE = √(p(1-p)/n)
- At p=0.10: SE ≈ 0.013 (±1.3%)
- At p=0.05: SE ≈ 0.010 (±1.0%)
- At p=0.50: SE ≈ 0.022 (±2.2%)

**Action:**
1. **Add a sentence to §3.5.1** stating:
   > "Binomial standard errors for the estimated swap rates are $\mathrm{SE} = \sqrt{p(1-p)/500}$, ranging from $\pm 1.0\%$ at the onset threshold ($p \approx 0.05$) to $\pm 2.2\%$ at chance ($p = 0.50$). These uncertainties are small relative to the qualitative features of the phase diagram (onset band, valley depth, plateau height)."

2. **Regenerate Figure 5** with shaded error bands or contour uncertainty. This requires modifying the phase diagram plotting script.
   - Find the script: likely in `corpus/code/` — search for phase diagram generation code
   - Add ±1 SE shading to the key contour lines (5%, 20%, 50% swap rate)
   - If the original data (per-trial results) is still available, compute exact binomial CIs (Wilson interval preferred over Wald for small p)

3. **Alternative (lighter touch):** If regenerating the figure is too costly, add a supplementary table of swap rates ± SE at key J_× values along a representative drive level.

**Key insight for implementer:** The reviewer isn't asking for fancy Bayesian inference. They want to see that 500 trials actually resolves the features you're claiming. A simple binomial SE annotation is sufficient.

---

### TASK 4: Define "Drive" vs "Cue" Explicitly [MEDIUM, §2.2]

**Current state:** "Cue" is well-defined (von Mises input with gain c, line 104–108). "Drive" is used informally throughout to mean "encoding strength" but is never formally defined. The fixed-point finding uses "strong external drives ($I_{ext} = 5.0$)" (line 142) which is different from the cue.

**Action:**
1. **Add a clarifying sentence after line 108:**
   > "We refer to the cue gain $c$ as the *encoding drive* (or simply *drive*) when discussing its role in the stochastic simulations, where it controls the strength of the stimulus that biases initial encoding toward network A."

2. **Add a sentence in §3.5.1** (around line 269) noting that "drive strength" on the phase diagram axis corresponds to the cue gain $c$ applied during a brief encoding period, not to the initialization drives used in the fixed-point solver.

**Key insight for implementer:** Two-sentence fix. The confusion arises because §3.1.1 uses "drives" ($I_{ext} = 5.0$) for initialization, while the stochastic sweep varies "drive strength" ($c$). These are different quantities with the same informal name.

---

### TASK 5: Kramers Sensitivity Analysis [MEDIUM, §3.5.5]

**Current state:** §3.5.5 derives γ ∈ [0.22, 0.36] from matching the Kramers threshold at J_× ≈ 0.25 with σ = 0.1. Self-consistency check at γ = 0.3. But no systematic sensitivity to σ or γ.

**Action:**
1. **Add a sensitivity paragraph** after the self-consistency check (after current line 333):
   > Show how the predicted onset J_× shifts with σ:
   > - σ = 0.05 → onset shifts to higher J_× (smaller noise needs thinner barrier)
   > - σ = 0.15 → onset shifts to lower J_× (larger noise punches through earlier)
   > Compute: for σ ∈ {0.05, 0.10, 0.15}, what J_× satisfies ΔV(J_×) = σ² · ln(k₀T)?
   > This is a purely analytic calculation using the existing λ_dom(J_×) curve.

2. **Add a small table or inline results:**
   ```
   σ = 0.05: ΔV threshold ≈ 0.010–0.016 → onset J_× ≈ 0.30–0.32
   σ = 0.10: ΔV threshold ≈ 0.039–0.062 → onset J_× ≈ 0.25 (current result)
   σ = 0.15: ΔV threshold ≈ 0.088–0.139 → onset J_× ≈ 0.18–0.22
   ```
   (Exact values need computation from the λ_dom(J_×) curve data.)

3. **Key point to make:** The onset J_× shifts smoothly with σ, but the *quadratic collapse* of the barrier is a structural feature independent of noise level. The Kramers bridge explains the *mechanism* (barrier thinning), not just the specific onset coordinate.

**Key insight for implementer:** This is mostly analytic — use the existing eigenvalue data from `spectral_separatrix_goldstone.py` to compute ΔV at each J_×, then find the crossing with different σ² thresholds. No new simulations needed.

---

### TASK 6: Notation Pass [MEDIUM, Throughout]

**Current state:** J_× is used consistently (confirmed by previous session's notation check). But "drive" is ambiguous (Task 4), and J_× plays multiple conceptual roles.

**Action:**
1. **After defining J_× in §2.2 (line 104)**, add:
   > "Throughout this paper, $J_\times$ denotes this single parameter; we distinguish three characteristic values: the pitchfork bifurcation $J_\times^* \approx 0.3485$, the coexistence existence boundary $J_\times^{exist} \approx 0.358$, and the stochastic onset $J_\times^{onset} \approx 0.25$."

2. **Ensure consistent subscript notation** throughout: J_×^* (pitchfork), J_×^{exist} (existence), J_×^{onset} (stochastic). Grep for ad-hoc variants and standardize.

3. **Check that the equation numbering is consistent** — the paper currently uses `$$...$$` display math without equation numbers. For Neural Computation submission, key equations (steady state, Jacobian, normal form, barrier height) should be numbered for cross-reference.

**Key insight for implementer:** This is a proofreading pass, not a rewrite. Focus on the three J_× thresholds having consistent superscript notation, and "drive" being pinned to cue gain c.

---

### TASK 7: Missing Literature [MEDIUM, §1 + §4]

**Papers to find and integrate:**

1. **Ságodi et al., NeurIPS 2024, "Back to the Continuous Attractor"**
   - Relevance: Contemporary theoretical anchor for continuous attractor structure and fragilities
   - Where to cite: §1.1 (working memory and ring attractors), alongside Burak & Fiete 2012
   - Action: Read the paper (use arXiv MCP), find the key claim about attractor fragility, add one sentence + citation

2. **Gu et al., Neuron 2025, "Attractor dynamics of working memory…"**
   - Relevance: Drift/bias dynamics, helps situate the "valley regime / operating point" narrative
   - Where to cite: §4.6 (selection vs representation failure) or §4.3 (behavioral cliff)
   - Action: Read the paper, find the key claim about estimation biases and operating points, add one sentence + citation

**How to find them:**
```bash
# Search arXiv for Ságodi
mcp__arxiv__search_papers("Ságodi continuous attractor", categories=["cs.LG", "q-bio.NC"])

# Search web for Gu et al. Neuron 2025
WebSearch("Gu et al Neuron 2025 attractor dynamics working memory estimation biases")
```

**Key insight for implementer:** These are strategic citations — they show the paper engages with the latest literature. One sentence each is sufficient. Don't restructure sections around them.

---

### TASK 8: Presentation Improvements [MEDIUM-HIGH]

#### 8a. Annotate Phase Diagram (Fig 5) with Deterministic Thresholds [HIGH]

**The problem:** The phase diagram shows swap rate in (J_×, c) space, but the deterministic thresholds (J_×* ≈ 0.349, J_×^exist ≈ 0.358) are not visually marked. The reader has to cross-reference text to understand where deterministic theory meets stochastic behavior.

**Action:** Regenerate Fig 5 with:
- Vertical dashed line at J_×* ≈ 0.349 (labeled "pitchfork")
- Vertical dashed line at J_×^exist ≈ 0.358 (labeled "existence boundary")
- Optionally: vertical dashed line at J_× ≈ 0.25 (labeled "Kramers onset")

**Implementation:** Find the phase diagram plotting script in `corpus/code/`. Add `axvline` calls. Re-export.

#### 8b. Abstract Clarification [HIGH]

Already covered in Task 2 — add "pure WTA regime" to the valley description in the abstract.

#### 8c. Spectrum Strip Panel [MEDIUM]

**The request:** A compact panel showing all dominant eigenvalues vs J_× with Goldstones visually pinned at 0.

**Current state:** Figure 3 is the pitchfork bifurcation diagram (D vs J_×). Figure 7A shows λ_dom vs J_×. But no single panel shows the full eigenvalue spectrum.

**Action:** Create a new panel (could be Fig 3 inset or a new figure):
- X-axis: J_×
- Y-axis: eigenvalue (real part)
- Plot: top ~10 eigenvalues as colored curves
- Goldstones: pinned at λ ≈ 0 (highlight in distinct color)
- λ_dom: emphasized, crossing zero at J_×*
- Other stable eigenvalues: fading into background

**Implementation:** Use eigenvalue data from `spectral_separatrix_goldstone.py`. The script already computes all 96 eigenvalues at each J_×. Extract the top 10 (least negative) and plot.

---

### TASK 9: Robustness — At Least One Control [MEDIUM]

**The reviewer explicitly asks for at least one of:**
- Multiplicative noise (test √r scaling)
- Alternative nonlinearity (softplus or tanh instead of sigmoid)
- Log-normal heterogeneity

**Recommendation:** Do the **alternative nonlinearity** test. Rationale:
- It's the most surgical: change one line (sigmoid → softplus or tanh), re-run eigenvalue analysis
- It directly addresses whether the valley is sigmoid-specific
- Multiplicative noise requires changing the simulation loop (more work)
- Log-normal heterogeneity is interesting but less critical (the symmetric Gaussian result already makes the structural point)

**Action:**
1. Modify the eigenvalue analysis script to accept an `activation` parameter
2. Run with softplus: `σ(h) = log(1 + exp(β(h - h₀)))` (appropriately scaled)
3. Compute J_×* and J_×^exist for the alternative nonlinearity
4. If the pitchfork persists (it should — it's a symmetry-breaking phenomenon, not activation-specific), report the shifted thresholds
5. Optionally: run a small stochastic sweep (fewer trials, coarser grid) to check if the valley qualitative structure persists
6. Add 1–2 sentences to §4.8 (Limitations) reporting the result

**Key insight for implementer:** The pitchfork bifurcation is structurally determined by exchange symmetry, not by the specific nonlinearity. What may change: the exact J_×* value, the width of the coexistence window, the barrier shape. The valley's existence as a qualitative two-failure-mode feature should survive. If it doesn't, that's an important negative result worth reporting.

---

### TASK 10: Soften "Universality" Language [LOW]

**Current state:** Already partially done in v4 (per Session 12 handoff). But the reviewer flags it again.

**Action:** Grep for "universal" in the paper and replace any remaining claims of quantitative universality with qualitative/structural language:
- "universal" → "structurally generic" or "codimension-1"
- "appears across domains" → "the same normal form (pitchfork → imperfect unfolding) governs any exchange-symmetric competition"
- Remove or qualify "shared spectral architecture" unless explicitly framed as conjecture

**Key insight for implementer:** The reviewer is fine with the structural claim. They just want you to distinguish "same normal form" (generic, good) from "same numbers" (model-specific, don't claim).

---

## Priority Ordering

**Phase 1 — Must-do for resubmission (address in order):**

| Order | Task | ID | Est. Work |
|-------|------|----|-----------|
| 1 | Two J_× scales clarification | T2 | 30 min (writing) |
| 2 | Define drive vs cue | T4 | 15 min (writing) |
| 3 | Notation pass | T6 | 30 min (proofreading) |
| 4 | Goldstone lemma: circulant + finite-N | T1 | 45 min (writing + verify) |
| 5 | Phase diagram error bars | T3 | 1–2 hrs (code + figure) |
| 6 | Annotate phase diagram | T8a | 30 min (code + figure) |
| 7 | Abstract fix | T8b | 10 min (writing) |

**Phase 2 — Strongly recommended:**

| Order | Task | ID | Est. Work |
|-------|------|----|-----------|
| 8 | Kramers sensitivity | T5 | 1 hr (analytic + writing) |
| 9 | Missing literature | T7 | 1 hr (search + integrate) |
| 10 | Spectrum strip panel | T8c | 1 hr (code + figure) |

**Phase 3 — Nice to have:**

| Order | Task | ID | Est. Work |
|-------|------|----|-----------|
| 11 | One robustness control | T9 | 2–3 hrs (code + analysis) |
| 12 | Soften universality | T10 | 15 min (proofreading) |

---

## Key Numbers to Remember

```
J_×*       ≈ 0.3485    (pitchfork bifurcation)
J_×^exist  ≈ 0.358     (coexistence ceases to exist)
ΔJ_×       ≈ 0.01      (instability window width)
J_×^onset  ≈ 0.25      (stochastic swap onset, σ=0.1)

λ_dom(0)    = -0.572    (strongly stable)
λ_dom(0.25) = -0.2357   (at behavioral onset)
λ_dom(0.34) = -0.0262   (near critical)

σ = 0.1, T = 500, γ = 0.30, ΔV(0.25) ≈ 0.046
500 trials/grid point → SE ≈ 1-2% at relevant swap rates
```

---

## For the Implementer

**Read first:**
1. This plan
2. `notes/2026-02-13-session-handoff-v5.md` (Session 14 handoff)
3. `paper/spectral-separatrix-draft.md` (the paper itself — ~500 lines)

**The reviewer's top-3 (their words):**
1. Make Goldstone protection **explicit and short-but-formal**
2. Resolve the **two J_× scales** issue
3. Upgrade phase diagram from picture to **inference** (error bars + one robustness test)

**What NOT to do:**
- Don't restructure the paper — the organization is working
- Don't add new sections — integrate into existing ones
- Don't run massive new simulations unless the robustness test demands it
- Don't over-cite — 2 new references (Ságodi, Gu) is sufficient

**Target:** Paper v6, ready for Neural Computation submission.

---

*The barrier between draft and submission collapses quadratically.*
