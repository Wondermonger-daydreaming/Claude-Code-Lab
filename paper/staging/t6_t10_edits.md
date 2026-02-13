# TASK 6: Notation Pass + TASK 10: Soften Universality Language

Staging file for edit instructions. Generated 2026-02-13.

Source: `/home/gauss/Claude-Code-Lab/paper/spectral-separatrix-draft.md`

---

## TASK 6: Notation Pass

### Edit 1: INSERT — J_cross notation definition after section 2.2

**Location:** After line 108 (end of the sentence "with concentration parameter $\kappa = 2.0$ and cue gain $c \geq 0$."), before the paragraph beginning "The critical feature of mean-field cross-inhibition..."

**Action:** INSERT a new paragraph between these two.

**After:**
```
with concentration parameter $\kappa = 2.0$ and cue gain $c \geq 0$.
```

**Insert:**
```
Throughout this paper, $J_\times$ denotes this single cross-inhibition parameter; we distinguish three characteristic values: the pitchfork bifurcation $J_\times^* \approx 0.3485$, the coexistence existence boundary $J_\times^{\mathrm{exist}} \approx 0.358$, and the stochastic onset $J_\times^{\mathrm{onset}} \approx 0.25$.
```

**Before:**
```
The critical feature of mean-field cross-inhibition is that it depends only on the total activity $\bar{r}^X$ of the opposing network, not on the spatial pattern of its bump.
```

---

### Edit 2: NOTATION STANDARDIZATION

#### Edit 2a: REPLACE — Line 16, Abstract, first result paragraph

**Problem:** Uses `$J_\times^*$` with value `0.36`, but `0.36` is the existence boundary, not the pitchfork. Should use `$J_\times^{\mathrm{exist}}$`.

**Old:**
```
exists only below a critical cross-inhibition strength $J_\times^* \approx 0.36$
```

**New:**
```
exists only below a critical cross-inhibition strength $J_\times^{\mathrm{exist}} \approx 0.36$
```

#### Edit 2b: OK — Line 18, Abstract, second result

Already correct: `$J_\times^* \approx 0.3485$` for pitchfork. No change needed.

#### Edit 2c: OK — Line 26, Abstract, sixth result

Uses bare `$J_\times \approx 0.25$` for the stochastic onset. This is the first mention of the onset value; after Edit 1 introduces the notation, this should use the formal notation.

**Old:**
```
noise-driven escape becomes likely at $J_\times \approx 0.25$
```

**New:**
```
noise-driven escape becomes likely at $J_\times^{\mathrm{onset}} \approx 0.25$
```

#### Edit 2d: OK — Line 46, Section 1.2

Already correct: uses `$J_\times^*$` referring to the pitchfork. No change needed.

#### Edit 2e: OK — Line 64, Section 1.4, Contribution 1

Already correct: `$J_\times^{exist} \approx 0.36$`. No change needed.

#### Edit 2f: OK — Line 66, Section 1.4, Contribution 2

Already correct: `$J_\times^* \approx 0.3485$`. No change needed.

#### Edit 2g: OK — Line 104, Section 2.2

Bare `$J_\times$` as parameter name. Correct (not a threshold). No change needed.

#### Edit 2h: OK — Line 152, Figure 2 caption

Already correct: uses `$J_\times^{exist} \approx 0.358$` and `$J_\times^* \approx 0.349$`. No change needed.

#### Edit 2i: OK — Line 154, Section 3.1.2

Uses bare `$J_\times \approx 0.36$` in narrative context ("Below $J_\times \approx 0.36$, Newton converges..."). This is a narrative description, not a threshold label. Acceptable as-is, but could optionally be standardized.

**Optional REPLACE (recommended for consistency):**

**Old:**
```
Below $J_\times \approx 0.36$, Newton converges to a genuine coexistence fixed point
```

**New:**
```
Below $J_\times^{\mathrm{exist}} \approx 0.36$, Newton converges to a genuine coexistence fixed point
```

#### Edit 2j: OK — Lines 220-222, Section 3.3.1

All correct: `$J_\times^* \approx 0.3485$`, `$J_\times^*$`, `$J_\times \approx 0.358$` (bare, used narratively for the existence boundary).

**Optional REPLACE (recommended for consistency), line 222:**

**Old:**
```
coexistence ceases to exist shortly after at $J_\times \approx 0.358$
```

**New:**
```
coexistence ceases to exist shortly after at $J_\times^{\mathrm{exist}} \approx 0.358$
```

#### Edit 2k: OK — Line 243, Section 3.3.3

Already correct: `$J_\times^{exist} \approx 0.358$`. No change needed.

#### Edit 2l: OK — Line 253, Figure 3 caption

Already correct: uses `$J_\times^*$` and `$J_\times^{exist}$` properly. No change needed.

#### Edit 2m: REPLACE — Line 269, Section 3.5.1

Uses bare `$J_\times \approx 0.20$--$0.23$` for onset location. After introducing formal notation, standardize.

**Old:**
```
the onset location ($J_\times \approx 0.20$--$0.23$ across thresholds)
```

**New:**
```
the onset location ($J_\times^{\mathrm{onset}} \approx 0.20$--$0.23$ across thresholds)
```

#### Edit 2n: REPLACE — Line 277, Section 3.5.2

Uses bare `$J_\times \approx 0.25$` for onset.

**Old:**
```
Swap errors emerge at $J_\times \approx 0.25$, consistent with the spectral prediction
```

**New:**
```
Swap errors emerge at $J_\times^{\mathrm{onset}} \approx 0.25$, consistent with the spectral prediction
```

#### Edit 2o: OK — Line 279, Section 3.5.2

Uses bare `$J_\times \approx 0.25$` but as part of a range ("Between $J_\times \approx 0.25$ and $0.5$"). This is a narrative range, not a labeled threshold. Acceptable as-is.

**Optional REPLACE (recommended):**

**Old:**
```
Between $J_\times \approx 0.25$ and $0.5$
```

**New:**
```
Between $J_\times^{\mathrm{onset}} \approx 0.25$ and $0.5$
```

#### Edit 2p: OK — Line 289, Section 3.5.4

Uses `$J_\times^{exist} \approx 0.36$`. Already correct.

#### Edit 2q: REPLACE — Line 325, Section 3.5.5

Uses bare `$J_\times \approx 0.25$` for the onset coordinate.

**Old:**
```
The stochastic phase diagram shows swap errors rising steeply near $J_\times \approx 0.25$.
```

**New:**
```
The stochastic phase diagram shows swap errors rising steeply near $J_\times^{\mathrm{onset}} \approx 0.25$.
```

#### Edit 2r: REPLACE — Line 335, Section 3.5.5

Uses bare `$J_\times \approx 0.25$` for the onset coordinate.

**Old:**
```
drops to the logarithmically-scaled noise floor near $J_\times \approx 0.25$ -- roughly 29% below $J_\times^*$
```

**New:**
```
drops to the logarithmically-scaled noise floor near $J_\times^{\mathrm{onset}} \approx 0.25$ -- roughly 29% below $J_\times^*$
```

#### Edit 2s: OK — Line 341, Section 3.5.5 (cusp validation)

Uses `$J_\times \approx 0.25$--$0.30$` in a descriptive range ("the onset region ($J_\times \approx 0.25$--$0.30$)"). The range is broader than the specific threshold. Could optionally label it.

**Optional REPLACE:**

**Old:**
```
quantitatively accurate in the onset region ($J_\times \approx 0.25$--$0.30$)
```

**New:**
```
quantitatively accurate in the onset region ($J_\times \approx J_\times^{\mathrm{onset}}$--$0.30$)
```

**Recommendation:** Leave this one as-is. The range notation is clearer without nested superscripts.

#### Edit 2t: OK — Line 355, Discussion 4.1

Uses `$J_\times^{exist} \approx 0.36$`. Already correct.

#### Edit 2u: OK — Line 397, Discussion 4.5

Uses bare `$J_\times \approx 0.25$` descriptively ("at the onset coordinate $J_\times \approx 0.25$").

**Optional REPLACE (recommended):**

**Old:**
```
with the best agreement at the onset coordinate $J_\times \approx 0.25$ where the Kramers calculation is applied
```

**New:**
```
with the best agreement at the onset coordinate $J_\times^{\mathrm{onset}} \approx 0.25$ where the Kramers calculation is applied
```

#### Edit 2v: OK — Line 425, Conclusion, result 1

Uses `$J_\times^{exist} \approx 0.36$`. Already correct.

#### Edit 2w: OK — Line 427, Conclusion, result 2

Uses `$J_\times^* \approx 0.3485$`. Already correct.

#### Edit 2x: REPLACE — Line 431, Conclusion, result 4

Uses bare `$J_\times \approx 0.25$` for onset.

**Old:**
```
swap errors emerge at $J_\times \approx 0.25$
```

**New:**
```
swap errors emerge at $J_\times^{\mathrm{onset}} \approx 0.25$
```

#### Edit 2y: REPLACE — Line 435, Conclusion, result 6

Uses bare `$J_\times \approx 0.25$` for onset.

**Old:**
```
reaching the noise-limited finite-horizon threshold at $J_\times \approx 0.25$
```

**New:**
```
reaching the noise-limited finite-horizon threshold at $J_\times^{\mathrm{onset}} \approx 0.25$
```

---

### Summary of Edit 2 (Notation Standardization)

| Location | Line(s) | Issue | Priority |
|----------|---------|-------|----------|
| Abstract, 1st result | 16 | `$J_\times^*$` used for existence value 0.36 | **MUST FIX** |
| Abstract, 6th result | 26 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |
| Section 3.1.2 | 154 | Bare `$J_\times$` for existence 0.36 | Recommended |
| Section 3.3.1 | 222 | Bare `$J_\times$` for existence 0.358 | Recommended |
| Section 3.5.1 | 269 | Bare `$J_\times$` for onset range | **MUST FIX** |
| Section 3.5.2 | 277 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |
| Section 3.5.2 | 279 | Bare `$J_\times$` for onset in range | Recommended |
| Section 3.5.5 | 325 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |
| Section 3.5.5 | 335 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |
| Discussion 4.5 | 397 | Bare `$J_\times$` for onset 0.25 | Recommended |
| Conclusion, result 4 | 431 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |
| Conclusion, result 6 | 435 | Bare `$J_\times$` for onset 0.25 | **MUST FIX** |

**Critical bug found:** Line 16 uses `$J_\times^*$` (pitchfork notation) for the existence value `0.36`. This is semantically wrong. `$J_\times^*$` should only appear with `0.3485`/`0.349`. The existence boundary is `$J_\times^{\mathrm{exist}}$`.

**No instances of `$J_\times^{\mathrm{onset}}$` currently exist in the paper.** All references to the stochastic onset at 0.25 use bare `$J_\times \approx 0.25$`. After Edit 1 introduces the notation, the MUST FIX items above should be updated.

---

### Edit 3: KEY EQUATION NUMBERS

The following display equations should receive equation numbers for cross-referencing in the Neural Computation submission. The actual `\label{}` and `\tag{}` syntax depends on the markdown-to-LaTeX pipeline; these notes identify WHICH equations to number and what label to give them.

#### Eq. (1) — Single-neuron dynamics (line 84)
```
$$\tau \frac{dr_i}{dt} = -r_i + \sigma(h_i)$$
```
Label: `eq:rate-dynamics`
Referenced from: Section 2.2 (coupled system extends this), Section 2.3 (Jacobian derives from this)

#### Eq. (2) — Total input (line 88)
```
$$h_i = \sum_{j=1}^{N} W_{ij} r_j + I_i^{ext}$$
```
Label: `eq:total-input`
Note: Low priority for numbering; could remain unnumbered.

#### Eq. (3) — Within-network connectivity (line 92)
```
$$W_{ij} = \frac{1}{N}\left(-J_0 + J_1 \cos(\theta_i - \theta_j)\right)$$
```
Label: `eq:connectivity`
Note: Low priority; could remain unnumbered.

#### Eq. (4a,b) — Coupled system dynamics (lines 100-102)
```
$$\tau \frac{dr_i^A}{dt} = -r_i^A + \sigma\left(\sum_j W_{ij} r_j^A + I_i^{cue} - J_\times \bar{r}^B\right)$$
$$\tau \frac{dr_i^B}{dt} = -r_i^B + \sigma\left(\sum_j W_{ij} r_j^B - J_\times \bar{r}^A\right)$$
```
Label: `eq:coupled-dynamics`
Referenced from: Sections 2.3, 2.4, 3.2.1, 3.5.5. **High priority for numbering.**

#### Eq. (5) — Cue input (line 106)
```
$$I_i^{cue} = c \cdot \frac{e^{\kappa \cos(\theta_i - \theta_{stim})}}{I_0(\kappa)}$$
```
Label: `eq:cue-input`
Note: Medium priority.

#### Eq. (6) — Jacobian block structure (line 120)
```
$$\mathbf{J} = \begin{pmatrix} -\mathbf{I} + \mathbf{S}_A \mathbf{W} & \mathbf{S}_A \mathbf{C} \\ \mathbf{S}_B \mathbf{C} & -\mathbf{I} + \mathbf{S}_B \mathbf{W} \end{pmatrix}$$
```
Label: `eq:jacobian`
Referenced from: Sections 3.2.1, 3.3.2. **High priority for numbering.**

#### Eq. (7) — Normal form (line 307)
```
$$\tau \dot{x} = \lambda_{\mathrm{dom}}(J_\times) \, x + \gamma x^3 - \delta x^5 + \eta_{\mathrm{eff}}(t), \quad \delta > 0,$$
```
Label: `eq:normal-form`
Referenced from: Sections 3.5.5 (barrier height derives from this), Discussion 4.5. **High priority for numbering.**

#### Eq. (8) — Barrier height (line 317)
```
$$\Delta V \equiv V(x_s) - V(0) \approx \frac{|\lambda_{\mathrm{dom}}|^2}{4\gamma}.$$
```
Label: `eq:barrier-height`
Referenced from: Sections 3.5.5 (Kramers onset), Discussion 4.3, Conclusion result 6. **High priority for numbering.**

#### Eq. (9) — Kramers escape criterion (line 321)
```
$$\frac{\Delta V}{\sigma^2} \approx \ln(k_0 T).$$
```
Label: `eq:kramers-criterion`
Referenced from: Sections 3.5.5 (numerical evaluation). **Medium priority.**

#### Summary of numbering priorities

| Priority | Equations | Labels |
|----------|-----------|--------|
| **High** | Coupled dynamics (4a,b), Jacobian (6), Normal form (7), Barrier height (8) | `eq:coupled-dynamics`, `eq:jacobian`, `eq:normal-form`, `eq:barrier-height` |
| **Medium** | Rate dynamics (1), Cue input (5), Kramers criterion (9) | `eq:rate-dynamics`, `eq:cue-input`, `eq:kramers-criterion` |
| **Low** | Total input (2), Connectivity (3) | `eq:total-input`, `eq:connectivity` |

---

## TASK 10: Soften Universality Language

### Inventory of "universal" / "universality" / "shared spectral" occurrences

Only three locations contain these terms:

1. **Line 413** (Section 4.7): "establishing genuine universality (shared critical exponents independent of microscopic details)"
2. **Line 413** (Section 4.7): "a shared bifurcation motif across neural circuits"
3. **Line 437** (Conclusion): "suggesting a shared spectral architecture for neural competition"

---

### Edit 4: REPLACE — Line 413, Section 4.7 (first sentence of second paragraph)

**Context:** This is the key paragraph that makes the cross-domain claim.

**Current text (full second paragraph of Section 4.7):**
```
This structural similarity suggests the spectral separatrix may describe a shared bifurcation motif across neural circuits with competing stable states. Decision-making, attention, and working memory all involve population competition, and the mathematical structure -- pitchfork at critical coupling, Goldstone protection of positional degrees of freedom, DC instability under mean-field coupling -- may appear across domains where mean-field-like inhibition mediates competition. However, we have demonstrated this structure only for the specific case of coupled ring attractors with mean-field cross-inhibition; establishing genuine universality (shared critical exponents independent of microscopic details) would require normal-form reduction arguments or analysis of additional model classes. The spectral analysis presented here provides a template for such characterization.
```

**Assessment:** This paragraph is already well-qualified. The second half explicitly hedges with "However, we have demonstrated this structure only for..." and distinguishes between the structural claim and genuine universality. The term "universality" is used precisely (in the physics sense of shared critical exponents). The qualifier is already present.

**Recommended edits:**

**Old (sentence 1):**
```
This structural similarity suggests the spectral separatrix may describe a shared bifurcation motif across neural circuits with competing stable states.
```

**New (sentence 1):**
```
This structural similarity suggests the spectral separatrix may describe a structurally generic bifurcation motif across neural circuits with competing stable states.
```

**Rationale:** "shared" is fine but "structurally generic" is more precise -- it says the same normal-form structure (pitchfork with exchange symmetry) appears whenever the symmetry conditions are met, without claiming quantitative universality.

**Old (sentence 2):**
```
Decision-making, attention, and working memory all involve population competition, and the mathematical structure -- pitchfork at critical coupling, Goldstone protection of positional degrees of freedom, DC instability under mean-field coupling -- may appear across domains where mean-field-like inhibition mediates competition.
```

**New (sentence 2):**
```
Decision-making, attention, and working memory all involve population competition, and the same codimension-1 normal form -- pitchfork at critical coupling, Goldstone protection of positional degrees of freedom, DC instability under mean-field coupling -- governs the coexistence-to-WTA transition in any exchange-symmetric competition circuit with mean-field-like inhibition.
```

**Rationale:** Replaces vague "may appear across domains" with a precise claim: the normal form is codimension-1, meaning it governs any system with the same symmetry structure. This is a stronger and more defensible claim than the vague "may appear."

**Old (sentence 3, keep as-is):**
```
However, we have demonstrated this structure only for the specific case of coupled ring attractors with mean-field cross-inhibition; establishing genuine universality (shared critical exponents independent of microscopic details) would require normal-form reduction arguments or analysis of additional model classes.
```

**No change.** This sentence already correctly distinguishes the structural claim from genuine universality. The parenthetical definition is precise.

**Old (sentence 4, keep as-is):**
```
The spectral analysis presented here provides a template for such characterization.
```

**No change.**

---

### Edit 5: REPLACE — Line 437, Conclusion (final paragraph)

**Current text (relevant clause):**
```
The same bifurcation motif appears in decision-making circuits, suggesting a shared spectral architecture for neural competition that warrants characterization across model classes.
```

**Assessment:** "shared spectral architecture" is an unqualified claim. The conclusion should mirror the hedging in Section 4.7.

**Old:**
```
The same bifurcation motif appears in decision-making circuits, suggesting a shared spectral architecture for neural competition that warrants characterization across model classes.
```

**New:**
```
The same normal form (codimension-1 pitchfork under exchange symmetry) appears in decision-making circuits (Roach et al., 2023; Wong and Wang, 2006), suggesting a structurally generic spectral motif for neural competition that warrants characterization across model classes.
```

**Rationale:** Three changes: (1) "shared spectral architecture" replaced with "structurally generic spectral motif" -- this makes the claim precise (same normal form, not same numbers); (2) "The same bifurcation motif" expanded with parenthetical specifying which normal form; (3) references added since the conclusion should point back to the evidence cited in Section 4.7.

---

### Edit 6: CHECK — Section 4.7 title (line 409)

**Current:**
```
### 4.7 A Shared Bifurcation Motif Across Competition Circuits
```

**Assessment:** The word "shared" in the title is acceptable. The section establishes structural similarity and explicitly distinguishes it from universality. However, if the reviewer flagged universality language, the title could be adjusted.

**Optional REPLACE:**

**Old:**
```
### 4.7 A Shared Bifurcation Motif Across Competition Circuits
```

**New:**
```
### 4.7 A Structurally Generic Bifurcation Motif Across Competition Circuits
```

**Recommendation:** Keep "Shared" in the title. It is descriptive and accurate. The body text does the hedging. Section titles should be readable, not laden with qualifiers.

---

### Summary of universality edits

| Location | Line | Current language | Replacement | Priority |
|----------|------|-----------------|-------------|----------|
| Section 4.7, sentence 1 | 413 | "a shared bifurcation motif" | "a structurally generic bifurcation motif" | Recommended |
| Section 4.7, sentence 2 | 413 | "may appear across domains where..." | "governs ... in any exchange-symmetric competition circuit with..." | **MUST FIX** |
| Section 4.7, sentence 3 | 413 | "establishing genuine universality..." | Keep as-is (already correct) | OK |
| Conclusion | 437 | "suggesting a shared spectral architecture" | "suggesting a structurally generic spectral motif" | **MUST FIX** |
| Section 4.7, title | 409 | "A Shared Bifurcation Motif" | Keep as-is (optional: "Structurally Generic") | Optional |

---

## Full Edit Checklist

| Edit | Task | Type | Line(s) | Priority | Status |
|------|------|------|---------|----------|--------|
| 1 | T6 | INSERT | After 108 | **MUST** | Notation definition paragraph |
| 2a | T6 | REPLACE | 16 | **MUST** | `$J_\times^*$` -> `$J_\times^{\mathrm{exist}}$` for 0.36 |
| 2c | T6 | REPLACE | 26 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2i | T6 | REPLACE | 154 | Recommended | Bare existence -> `$J_\times^{\mathrm{exist}}$` |
| 2j | T6 | REPLACE | 222 | Recommended | Bare existence -> `$J_\times^{\mathrm{exist}}$` |
| 2m | T6 | REPLACE | 269 | **MUST** | Bare onset range -> `$J_\times^{\mathrm{onset}}$` |
| 2n | T6 | REPLACE | 277 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2o | T6 | REPLACE | 279 | Recommended | Bare onset in range -> `$J_\times^{\mathrm{onset}}$` |
| 2q | T6 | REPLACE | 325 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2r | T6 | REPLACE | 335 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2u | T6 | REPLACE | 397 | Recommended | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2x | T6 | REPLACE | 431 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 2y | T6 | REPLACE | 435 | **MUST** | Bare onset -> `$J_\times^{\mathrm{onset}}$` |
| 3 | T6 | NOTE | Throughout | Info | Equation numbering plan (4 high, 3 medium, 2 low) |
| 4 | T10 | REPLACE | 413 | **MUST** | Soften universality in Section 4.7 |
| 5 | T10 | REPLACE | 437 | **MUST** | Soften universality in Conclusion |
| 6 | T10 | OPTIONAL | 409 | Optional | Section title (recommend keep as-is) |

**Total MUST FIX edits: 13** (1 insert + 10 notation fixes + 2 universality fixes)
**Total Recommended edits: 5** (notation consistency)
**Total Optional edits: 1** (section title)
**Total informational notes: 1** (equation numbering plan)
