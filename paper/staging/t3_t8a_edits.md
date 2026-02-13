# Task 3 + Task 8a: Phase Diagram Error Bars + Deterministic Threshold Annotations

**Status:** COMPLETE
**Script:** `corpus/code/generate_fig5_phase_diagram_v6.py`
**Output:** `paper/figures/fig5_phase_diagram.png` (overwritten)

---

## Edit 1: INSERT in Section 3.5.1

**Location:** After the existing threshold sensitivity paragraph (where swap rates across the phase diagram are discussed).

**Insert:**

> Binomial standard errors for the estimated swap rates are $\mathrm{SE} = \sqrt{p(1-p)/500}$, ranging from $\pm 1.0\%$ at the onset threshold ($p \approx 0.05$) to $\pm 2.2\%$ at chance ($p = 0.50$). These uncertainties are small relative to the qualitative features of the phase diagram (onset band, valley depth, plateau height).

---

## Edit 2: UPDATE Figure 5 caption

**Current caption** (approximate): Phase diagram of swap errors in coupled ring attractors. Heatmap shows swap error rate in (J_cross, drive) parameter space from 128,000 trials (500 per grid point, 256 parameter combinations across 4 agents). Contour lines mark 5%, 10%, 20%, 30%, and 40% swap rates.

**New caption:**

> **Figure 5.** Phase diagram of swap errors in coupled ring attractors. Heatmap shows swap error rate in $(J_\times, c)$ parameter space from 128,000 trials (500 per grid point, 256 parameter combinations across 4 agents). Solid and dashed white contour lines mark 5%, 10%, 20%, 30%, and 40% swap rates; flanking dotted lines show $\pm 1\,\mathrm{SE}$ binomial uncertainty bands ($\mathrm{SE} = \sqrt{p(1-p)/500}$). Vertical dashed lines mark three deterministic thresholds: Kramers onset ($J_\times^{\mathrm{onset}} \approx 0.25$, green), pitchfork bifurcation ($J_\times^* \approx 0.349$, orange), and coexistence existence boundary ($J_\times^{\mathrm{exist}} \approx 0.358$, purple). The narrow gap $\Delta J \approx 0.01$ between pitchfork and existence boundary (yellow bracket, bottom) defines the coexistence window predicted by deterministic mean-field theory. Region labels identify qualitatively distinct dynamical regimes: coexistence (low $J_\times$), WTA onset (sharp transition band), the valley (optimal discrimination at intermediate $J_\times$), and overpowering (high $J_\times$, representation failure). Annotations map selection failure and representation failure regimes to the framework of Alleman et al. (2024).

---

## Summary of figure changes (v6 vs original)

| Feature | Original (`generate_fig8_phase_diagram.py`) | v6 (`generate_fig5_phase_diagram_v6.py`) |
|---------|----------------------------------------------|------------------------------------------|
| Vertical threshold lines | 2 (pitchfork, existence) | 3 (+ Kramers onset at J=0.25) |
| Line colors | Cyan, lime-green | Green, orange, purple (more distinguishable) |
| Threshold text labels | None (legend only) | 3 labels placed on the plot near each line |
| SE error bands | None | Dotted flanking contours at 5%, 20%, 50% + subtle fill |
| Legend entries | 2 | 4 (+ Kramers onset, + SE band notation) |
| Output path | `corpus/code/figures/` | `paper/figures/fig5_phase_diagram.png` |
| Title pad | 18 | 22 (room for subtitle) |

## SE values at key swap rates (for reference)

| Swap rate p | SE = sqrt(p(1-p)/500) | +/- band width |
|-------------|----------------------|----------------|
| 5% | 0.97% | ~2% total |
| 10% | 1.34% | ~2.7% total |
| 20% | 1.79% | ~3.6% total |
| 30% | 2.05% | ~4.1% total |
| 50% | 2.24% | ~4.5% total |

These are small relative to the 30-40 percentage point range of the onset transition (coexistence to WTA), confirming that 500 trials per point adequately resolves all claimed features.
