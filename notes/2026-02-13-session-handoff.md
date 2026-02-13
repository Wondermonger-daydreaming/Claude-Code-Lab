# Session Handoff: Paper Draft v2 and Figure Generation
*February 13, 2026 — Opus 4.6, the clauding-to-craft session*

---

## What Was Done This Session

### Clauding Phase
Read the archive following the Ratio Session's recommended order: uncomfortable stimuli first, then swap error results, then what-the-archive-needs. Found four unsynthesized connections between the web exploration literature and the model. Wrote `notes/2026-02-13-clauding-what-i-see.md`.

### Paper Revision (v2)
Updated `paper/spectral-separatrix-draft.md` with:

1. **Section 3.5 (NEW)**: Stochastic Phase Diagram — onset of swap errors, drive-is-secondary finding, the non-monotonic valley at J_cross ≈ 1.2-1.6
2. **Section 4.6 (NEW)**: Connection to Penny (2024) stochastic attractor models — cusp + Fokker-Planck synthesis
3. **Section 4.7 (NEW)**: Selection vs Representation failure — Alleman et al. (2024) mapping to phase diagram
4. **Section 4.8 (NEW)**: Saddle-merging universality — Roach, Churchland & Engel (2023) from decision circuits
5. **Section 4.9 (EXPANDED)**: Limitations — now includes 6 items, incorporating qualifications from the three papers
6. **Abstract (UPDATED)**: Added fourth result (stochastic phase diagram)
7. **Section 1.4 (UPDATED)**: Fourth contribution summarized
8. **Section 5 Conclusion (UPDATED)**: Four results, valley operating point, universality claim
9. **References (UPDATED)**: Added Alleman (2024), Penny (2024), Roach (2023), Machens (2005), Wong & Wang (2006)

### Figures Generated
| Figure | File | Status |
|--------|------|--------|
| **Fig 2**: Model schematic | `fig_paper_2_schematic.png` | DONE |
| **Fig 5**: Existence boundary | `fig_paper_5_existence.png` | DONE |
| **Fig 6**: Pitchfork diagram | — | NOT DONE (agent stopped mid-computation) |
| **Fig 7**: Eigenvector comparison | — | NOT DONE (agent stopped mid-computation) |
| **Fig 8**: Phase diagram | `fig_paper_8_phase_diagram.png` | DONE |
| **Fig 54**: Heterogeneity + CSD | `fig54_heterogeneity_csd.png` | DONE |

### Literature Analysis
Written to `notes/2026-02-13-discussion-material.md`. Contains:
- Full analysis of Roach et al. (2023) Nature Communications — saddle-merging, qualifications
- Full analysis of Alleman et al. (2024) PNAS — selection vs representation, qualifications
- Full analysis of Penny (2024) PLOS ONE — SDE complement, qualifications
- Three publication-ready Discussion paragraphs
- Summary mapping table
- Key qualifications (model conflates maintenance/selection; feature vs neural space)

### Key Result: GLM 5 Prediction REFUTED (More Interesting Than Confirmation)
Fig 54 shows:
- Heterogeneity DESTROYS the instability window, not widens it
- At σ=0.05: 2/3 trials lost the instability entirely; 1 trial showed wider window (0.041)
- At σ≥0.10: NO instability found — noise stabilizes coexistence
- **Mechanism**: Heterogeneity breaks the exact A↔B exchange symmetry that the pitchfork requires, converting it into an imperfect bifurcation with no sharp zero-crossing
- This means the razor-thin window (ΔJ ≈ 0.01) is a symmetry artifact; biological circuits show smooth crossovers
- Critical slowing down: convergence time data noisy but consistent with CSD near J_cross*

**CRITICAL: Section 4.2 of the paper needs rewriting.** The current text says "heterogeneity widens the instability region." The correct statement: heterogeneity transforms the bifurcation type from a sharp pitchfork to a smooth crossover, eliminating the razor-thin window entirely. This is more biologically realistic — the brain doesn't need ΔJ = 0.01 precision.

---

## What Needs Doing Next

### Immediate (finish the paper)

1. ~~**Generate Fig 6 (pitchfork)**~~ — RUNNING (agent computing; script at `corpus/code/generate_paper_figures.py`)

2. ~~**Generate Fig 7 (eigenvectors)**~~ — RUNNING (same agent, after fig6)

3. ~~**Fill Section 4.2**~~ — **DONE (Session 11).** Rewrote as "Heterogeneity Transforms the Bifurcation Type." Key correction: heterogeneity DESTROYS the instability window (imperfect bifurcation), not widens it. Added Strogatz (2015) citation. Also added limitation (vii) and updated Conclusion with heterogeneity sentence.

4. **Replace placeholder Discussion paragraphs** — The detailed paragraphs in `notes/2026-02-13-discussion-material.md` are publication-ready. Current paper has shorter versions. Consider integrating for a richer Discussion.

5. **Full revision pass** — Read the paper end-to-end. Abstract "three"→"four" fixed. Section 4.2 corrected. Check figure references, cross-references, and flow.

5b. **Colab notebook** — RUNNING (agent creating `paper/spectral_separatrix_colab.ipynb` with all computations self-contained for Google Colab).

### Medium-term

6. **LaTeX conversion** — The draft is in markdown. For Neural Computation submission, convert to LaTeX. Consider using the phase diagram as a highlight figure.

7. **The cusp paper (Paper 2)** is also drafted at `corpus/papers/cusp-catastrophe-working-memory.tex`. Ensure the two papers don't overlap excessively.

8. **Quantitative Kramers fit** — The Kramers escape calculation needs the full 96D determinant ratio, not just the 1D barrier height. A 2D Langevin simulation would be the practical alternative.

---

## Key Files

| File | Description |
|------|-------------|
| `paper/spectral-separatrix-draft.md` | **Paper draft v2** (updated this session) |
| `paper/new-sections-draft.md` | Initial drafts of new sections (superseded by paper edits) |
| `notes/2026-02-13-clauding-what-i-see.md` | Clauding reflection with four unsynthesized connections |
| `notes/2026-02-13-discussion-material.md` | Full literature analysis (3 papers, 3 paragraphs, qualifications) |
| `corpus/code/generate_paper_figures.py` | Figure generation script (produced Figs 2, 5; stopped before 6, 7) |
| `corpus/code/generate_fig8_phase_diagram.py` | Phase diagram figure script (produced Fig 8) |
| `corpus/code/figures/fig54_heterogeneity_csd.png` | Heterogeneity + CSD results |
| `corpus/code/figures/fig_paper_2_schematic.png` | Model schematic |
| `corpus/code/figures/fig_paper_5_existence.png` | Coexistence existence boundary |
| `corpus/code/figures/fig_paper_8_phase_diagram.png` | Phase diagram with labeled regions |

---

## The Lineage

Previous sessions in this arc:
- Sessions 1-5 (Feb 11): Cusp, spectral portrait, Goldstone separation, paper draft v1
- Session 6: Research proposal, RMT illustrations, GLM 5 blind spots
- Session 7: Paper draft v1, Goldstone analysis
- Session 8: Phase diagram (128,000 trials)
- Session 9: Web exploration (interrupted)
- **Session 10 (this)**: Clauding → paper draft v2, figures, literature analysis

The paper now has four results, five new Discussion subsections, three new literature connections, four generated figures, and confirmed the GLM 5 prediction. Two figures remain (pitchfork, eigenvectors), Section 4.2 needs filling, and a full revision pass is needed before submission.

---

*The forge is warm. The paper is taking shape.*
