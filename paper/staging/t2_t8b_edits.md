# Staging: TASK 2 (Resolve the Two J_cross Scales) + TASK 8b (Abstract WTA Fix)

**Target file:** `paper/spectral-separatrix-draft.md`

**Purpose:** Make explicit that the deterministic analysis (J_cross in [0, 0.36]) and the stochastic sweep (J_cross in [0.05, 8.0]) use the identical parameter with no rescaling. Clarify in the abstract that the valley operates in the pure WTA regime. Add a robustness note to the valley discussion.

---

## Edit 1: INSERT paragraph in Section 3.5.1 (Parameter Sweep)

**Location:** After the paragraph ending with "...preserve the ordering across $J_\times$ values and the location of qualitative transitions." (end of Section 3.5.1, line 269)

**Marker text (preceding paragraph ends with):**
```
Wider classification windows increase absolute swap rates (e.g., 10% vs. 26% at $J_\times = 0.25$ for 0.2 vs. 0.5 rad) but preserve the ordering across $J_\times$ values and the location of qualitative transitions.
```

**Insert the following new paragraph immediately after:**

> The stochastic sweep extends to $J_\times = 8.0$, well beyond the coexistence existence threshold $J_\times^{exist} \approx 0.36$. For $J_\times > J_\times^{exist}$, the system admits only WTA solutions; the stochastic trials begin from a coexistence-like initial condition (both bumps established by strong drives) and the dynamics reveal which network captures the WTA state. This extended range is necessary to characterize the full behavioral landscape, including the non-monotonic valley at $J_\times \approx 1.2$--$1.6$ (Section 3.5.4), which operates in the pure WTA regime. The cross-inhibition parameter $J_\times$ has the same definition throughout: the coefficient in the mean-field coupling term $J_\times \bar{r}^X$ (Eq. 2). No rescaling is applied between the deterministic and stochastic analyses.

---

## Edit 2: REPLACE in Abstract (Task 2 + Task 8b)

**Location:** Fourth paragraph of the Abstract (line 22), the sentence beginning "Fourth, large-scale stochastic simulations..."

**Find this text:**
```
and a non-monotonic valley at intermediate $J_\times$ identifies a functional operating regime for working memory.
```

**Replace with:**
```
and a non-monotonic valley at intermediate $J_\times \approx 1.2$--$1.6$ -- well above the coexistence threshold, in the pure winner-take-all regime -- identifies a functional operating regime for working memory.
```

---

## Edit 3: INSERT sentence in Section 3.5.4 (Valley Discussion)

**Location:** At the end of the valley discussion, after the paragraph ending with "...but the qualitative feature -- a non-monotonic minimum between two failure modes -- is the robust finding." (line 299)

**Marker text (preceding paragraph ends with):**
```
The specific parameter range ($J_\times \approx 1.2$--$1.6$) depends on our model parameterization and should not be interpreted as a direct physiological prediction; the qualitative feature -- a non-monotonic minimum between two failure modes -- is the robust finding. The circuit need not be tuned precisely to $J_\times^*$ but rather to a regime where WTA dynamics and encoding strength are balanced.
```

**Insert the following new paragraph immediately after:**

> The valley's location in parameter space ($J_\times \approx 1.2$--$1.6$) is specific to the sigmoid nonlinearity and gain parameters used here (Section 2.1). The qualitative structure -- two competing failure modes generating a non-monotonic minimum -- is the robust finding, as it depends on the generic competition between cross-inhibition strength and noise-driven escape.

---

## Verification Checklist

- [ ] Edit 1 bridges the deterministic/stochastic J_cross scales explicitly for the reader
- [ ] Edit 2 adds WTA-regime context to the abstract's valley description (covers both T2 and T8b)
- [ ] Edit 3 reinforces parameter-dependence vs. structural robustness of the valley
- [ ] No equations, figure references, or section numbers are changed
- [ ] The parameter name $J_\times$ is confirmed as identical across all analyses (no rescaling)
