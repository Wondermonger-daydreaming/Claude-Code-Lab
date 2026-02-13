# T5: Kramers Onset Sensitivity to Noise Level σ

**Problem:** The paper derives the swap-error onset at $J_\times^{\mathrm{onset}} \approx 0.25$ for $\sigma = 0.1$, but does not show how this prediction shifts with noise level. A reviewer may ask whether the onset is robust or an artifact of a single $\sigma$ choice.

**Computation:** `corpus/code/kramers_sensitivity.py` (run Feb 13, 2026)

The script computes $\lambda_{\mathrm{dom}}(J_\times)$ at 60 points across $J_\times \in [0, 0.36]$, then finds the crossing of $\Delta V = |\lambda_{\mathrm{dom}}|^2 / (4\gamma)$ with the Kramers threshold band $\Delta V = \sigma^2 \ln(k_0 T)$, $\ln(k_0 T) \in [3.9, 6.2]$.

---

## Computed Results

| $\sigma$ | $\Delta V$ threshold range | Predicted $J_\times^{\mathrm{onset}}$ range |
|:--------:|:-------------------------:|:-------------------------------------------:|
| 0.05     | [0.0098, 0.0155]          | [0.298, 0.310]                              |
| 0.10     | [0.039, 0.062]            | [0.230, 0.260]                              |
| 0.15     | [0.088, 0.140]            | [0.141, 0.199]                              |

Key observations:
- At $\sigma = 0.10$, the band brackets $J_\times \approx 0.25$, consistent with stochastic simulations.
- Halving $\sigma$ shifts onset upward by $\sim$0.05 (less noise, barrier matters later).
- Increasing $\sigma$ by 50% shifts onset downward by $\sim$0.06 (more noise, barrier breached earlier).
- The onset shifts smoothly and monotonically with $\sigma$, but the barrier collapse itself ($\Delta V \propto |\lambda_{\mathrm{dom}}|^2$) is structural — determined by the pitchfork geometry of the bifurcation, not by noise parameters.

---

## Edit: INSERT into §3.5.5

**Location:** Immediately after the sentence ending "squarely in the $\ln(k_0 T)$ band (Fig. 7C)." (line 347 of `spectral-separatrix-draft.md`), and before the paragraph beginning "This provides a quantitative explanation..."

**Surrounding text for anchoring:**

```
...taking $\gamma = 0.3$ gives $\Delta V(0.25) \approx 0.046$ and $\Delta V / \sigma^2 \approx 4.6$, squarely in the $\ln(k_0 T)$ band (Fig. 7C).
                                                                                                                                                    <-- INSERT HERE
This provides a quantitative explanation for why the behavioral "cliff" occurs substantially below the deterministic pitchfork.
```

**Insert:**

```
The onset prediction shifts smoothly with noise amplitude. Because $\Delta V \propto |\lambda_{\mathrm{dom}}|^2$ while the threshold scales as $\sigma^2 \ln(k_0 T)$, the predicted $J_\times^{\mathrm{onset}}$ depends on $\sigma$ only through the threshold level, not through the barrier shape:

| $\sigma$ | $\Delta V$ threshold | $J_\times^{\mathrm{onset}}$ range |
|:--------:|:-------------------:|:---------------------------------:|
| 0.05 | [0.010, 0.016] | [0.30, 0.31] |
| 0.10 | [0.039, 0.062] | [0.23, 0.26] |
| 0.15 | [0.088, 0.140] | [0.14, 0.20] |

Halving the noise from $\sigma = 0.10$ to $0.05$ shifts the onset upward by only $\Delta J_\times \approx 0.05$; increasing it to $0.15$ shifts it downward by $\sim$0.06. The quadratic barrier collapse is structural — set by the spectral approach to the pitchfork — so the sensitivity enters only through the logarithmic noise floor $\sigma^2 \ln(k_0 T)$.
```

---

## Notes

- The table values are rounded to 2 decimal places for the $\Delta V$ thresholds and 2 for the onset ranges. Full precision is in the script output.
- The inserted paragraph comes logically between the self-consistency check (which validates $\gamma$ at the baseline $\sigma = 0.10$) and the summary paragraph explaining WHY the cliff occurs below the pitchfork.
- The table can be formatted as a LaTeX tabular if the journal requires it; the Markdown inline table works for the current draft format.
- The key rhetorical move: the barrier *shape* is structural (quadratic collapse from spectral geometry), only the *threshold level* depends on noise. This preempts the objection that the onset prediction is parameter-dependent.
