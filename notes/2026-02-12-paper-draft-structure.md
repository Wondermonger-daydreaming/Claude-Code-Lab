# Paper Draft Structure: Spectral Anatomy of the Coexistence Saddle

*February 12, 2026*

---

## Working Title

**Goldstone Modes and the Coexistence Saddle: Spectral Bifurcation Analysis of Competing Ring Attractors Under Mean-Field Cross-Inhibition**

Short alternative: **The Spectral Separatrix: How Cross-Inhibition Controls Winner-Take-All Transitions in Coupled Ring Attractors**

---

## Abstract (Draft, ~230 words)

Persistent neural activity in working memory is often modeled as bump attractors on ring networks. When two such networks compete via cross-inhibition, the system must resolve which representation dominates -- a winner-take-all (WTA) decision. We present a complete spectral bifurcation analysis of this transition in a coupled ring attractor model (two networks of N=48 neurons each, cosine connectivity within, mean-field cross-inhibition between). We identify three key results.

First, the coexistence fixed point -- where both bumps self-sustain simultaneously -- exists only below a critical cross-inhibition strength J_cross* approximately 0.36. Above this threshold, cross-inhibition is too strong for both representations to survive; the system admits only WTA solutions. This contradicts the common assumption that coexistence is available across parameter space.

Second, the continuous rotational symmetry of each bump guarantees exactly two Goldstone modes (zero eigenvalues) that are protected against mean-field coupling. The first non-Goldstone eigenvalue -- governing uniform amplitude competition -- crosses zero at J_cross* approximately 0.3485 via a pitchfork bifurcation, creating the coexistence saddle and two WTA stable states.

Third, the critical eigenvector is spatially uniform (DC mode), meaning the instability is about total activity competition, not spatial pattern rearrangement. This is a direct consequence of mean-field (spatially unstructured) cross-inhibition. We discuss implications for the "behavioral cliff" in working memory performance and argue that the brain may operate near critical J_cross*, with the cliff reflecting proximity to this spectral bifurcation rather than weak sensory drive.

---

## Section Outline

### 1. Introduction

#### 1.1 Working Memory and Competing Representations
Persistent neural activity in prefrontal cortex underlies working memory. Ring attractor models capture bump-shaped activity profiles that encode continuous variables (e.g., orientation, spatial location). When multiple items must be stored simultaneously, cross-inhibition between networks creates a competition whose outcome determines whether coexistence or WTA dominance prevails. Cite Compte et al. (2000), Wimmer et al. (2014), Wei et al. (2012).

#### 1.2 The Behavioral Cliff
Psychophysical experiments reveal a sharp performance cliff at low stimulus strengths: below a critical signal-to-noise ratio, working memory accuracy collapses abruptly rather than degrading gradually. Previous theoretical work attributed this to noise-driven escape from a metastable state (Kramers escape), yielding a cusp catastrophe potential V(D) = D^4 + aD^2 + bD in the dominance variable D. Cite the cusp/Kramers results from earlier in this project. The cliff's origin -- whether it reflects weak cues, strong noise, or a structural property of the circuit -- remains debated.

#### 1.3 From Mean-Field Reduction to Full Spectral Analysis
Prior analyses reduced the system to a one-dimensional dominance variable D = mean(r_A) - mean(r_B). This captures the topology (cusp) but discards the full 96-dimensional dynamics. We present the first complete eigenvalue decomposition of the coupled ring attractor Jacobian, revealing structure invisible to the 1D reduction: protected Goldstone modes, the precise location of the pitchfork bifurcation, and the character of the critical eigenvector.

#### 1.4 Summary of Contributions
State the three main results (coexistence existence threshold, Goldstone separation, DC critical mode) and preview their implications.

---

### 2. Model

#### 2.1 Single Ring Attractor
Define the rate model: tau * dr_i/dt = -r_i + sigma(h_i), with h_i = sum_j W_ij r_j + I_i^ext. Sigmoid activation sigma(h) = r_max / (1 + exp(-beta*(h - h0))). Within-network connectivity W_ij = J_0/N + (J_1/N) * cos(theta_i - theta_j), yielding a cosine-tuned ring attractor with preferred angles theta_i uniformly spaced on [-pi, pi). Parameters: N=48, J_0=1.0, J_1=6.0, beta=5.0, h0=0.5, r_max=1.0, tau=10.0.

#### 2.2 Coupled System with Mean-Field Cross-Inhibition
Two identical ring networks A and B. Cross-coupling is mean-field: network A receives -J_cross * mean(r_B) uniformly across all neurons, and vice versa. This formulation depends only on the total activity of the opposing network, not on the spatial pattern of its bump. External input (cue) is a von Mises tuning curve: cue_A_i = cue_gain * exp(kappa * cos(theta_i - theta_stim)) / I_0(kappa), applied only to network A.

#### 2.3 Jacobian of the Coupled System
Derive the 2N x 2N Jacobian explicitly:

```
J = [ -I + D_A * W,     D_A * C_cross ]
    [ D_B * C_cross,    -I + D_B * W   ]
```

where D_A = diag(sigma'(h_A)), D_B = diag(sigma'(h_B)), and C_cross is the rank-1 mean-field coupling matrix with all entries -J_cross/N. This block structure is central to the analysis.

#### 2.4 Symmetries
The system possesses: (i) continuous O(1) rotational symmetry for each bump independently (mean-field coupling does not depend on bump position); (ii) discrete exchange symmetry A <-> B when cue_gain = 0. Enumerate the consequences for the eigenvalue spectrum: two Goldstone modes from (i), pitchfork bifurcation geometry from (ii).

---

### 3. Results

#### 3.1 Existence of the Coexistence Fixed Point

##### 3.1.1 Method: Simulation-Seeded Newton Continuation
Describe the two-phase numerical method. Phase 1: establish both bumps using strong external drives, then remove drives and simulate for 50,000 timesteps under cross-inhibition to approach the coexistence state. Phase 2: polish with Newton's method (fsolve with analytical Jacobian) to machine precision. Track residual ||F(r*)|| to verify convergence.

##### 3.1.2 Result: Critical Threshold J_cross* ~ 0.36
Present the J_cross scan from 0 to 0.5. Below J_cross ~ 0.36, Newton converges to a genuine fixed point with both bumps active (max(r_A) > 0.3, max(r_B) > 0.3, residual < 10^-10). Above J_cross ~ 0.36, the simulation shows one bump suppressing the other; Newton converges only to WTA solutions. At J_cross = 0.5 (the commonly used value in the literature), coexistence does not exist as a fixed point.

##### 3.1.3 Diagnostic: Fixed Point vs. Slow Manifold
Present the time-resolved diagnostic (residual, drift rate, dominance, bump heights, bump positions over 50,000 steps). At J_cross = 0.5, the residual does not converge to zero; the system slowly drifts toward WTA. At J_cross = 0.35, the residual converges exponentially to machine precision. This confirms that coexistence is a true fixed point below threshold and does not exist above it.

#### 3.2 Goldstone Modes and the Protected Symmetry

##### 3.2.1 Why Goldstone Modes Exist
Mean-field cross-inhibition depends on mean(r_B) = (1/N) * sum(r_B_j). This is invariant under any rotation of the bump profile. Therefore, the energy landscape is flat in the direction of bump rotation, producing exactly-zero eigenvalues (Goldstone modes). Each bump contributes one rotational degree of freedom, yielding two Goldstone modes for the coupled system.

##### 3.2.2 Identifying Goldstone Modes Numerically
Define the classification scheme: eigenvalues with |lambda| < 10^-3 are classified as Goldstone candidates. For each eigenvector, compute projections onto six basis directions: (1) symmetric dominance (cosine envelope, A up B down), (2) co-directional drift (sine envelope, both shift same way), (3) anti-directional drift (sine envelope, shift opposite ways), (4) uniform (DC, A up B down flat), (5) Goldstone-A (sine envelope, A only), (6) Goldstone-B (sine envelope, B only). Goldstone eigenvectors project strongly onto the rotation-derivative directions (5) and (6).

##### 3.2.3 Goldstone Count Across J_cross
Present the Goldstone count as a function of J_cross. Two Goldstone modes persist at all values where coexistence exists, confirming the symmetry protection. Their eigenvalues remain at |lambda| ~ 10^-10 to 10^-6 (numerical precision), never lifted by cross-inhibition.

#### 3.3 The Pitchfork Bifurcation

##### 3.3.1 The First Non-Goldstone Eigenvalue
After removing Goldstone modes, track the dominant genuine eigenvalue lambda_dom as a function of J_cross. This eigenvalue is negative (stable) for small J_cross and increases monotonically. It crosses zero at J_cross* ~ 0.3485, creating a pitchfork bifurcation: the symmetric coexistence state becomes a saddle, and two WTA states (A-dominant and B-dominant) are born as stable nodes.

##### 3.3.2 Character of the Critical Eigenvector
At J_cross*, the critical eigenvector projects almost entirely onto the "uniform" direction (DC mode): a spatially flat increase in network A coupled with a spatially flat decrease in network B. This means the instability is about total activity competition (which network has more overall firing), not about spatial pattern rearrangement. The cosine-envelope (bump-shape) projection is small. This is a direct consequence of mean-field coupling: because the cross-inhibition is spatially uniform, the mode it destabilizes is also spatially uniform.

##### 3.3.3 The Narrow Existence Window
The coexistence saddle (genuinely unstable, with lambda_dom > 0) exists only in the interval J_cross in [~0.3485, ~0.36], a width of approximately Delta_J_cross ~ 0.01. Below 0.3485, coexistence is a stable node. Above 0.36, it ceases to exist entirely. This razor-thin window has implications for biological circuits (Section 4.2).

#### 3.4 The Spectral Separatrix at Fixed J_cross

##### 3.4.1 Newton Continuation in Cue Gain
At J_cross = 0.35 (within the unstable window), use Newton continuation to track the coexistence branch as cue_gain increases from 0 to 0.5. Simultaneously track the WTA branch for comparison. Present: dominant eigenvalue, dominance D, instability index (number of positive eigenvalues), bump heights, and eigenvector projections as functions of cue_gain.

##### 3.4.2 The Coexistence Saddle Under Cue
At cue_gain = 0, the coexistence state has one or more positive eigenvalues (it is a saddle). As cue increases, the cue breaks the A-B exchange symmetry, deforming the pitchfork. The coexistence branch and the WTA branch may merge or diverge. Present the bifurcation diagram (D vs. cue_gain for both branches) and the eigenvalue crossing diagram (lambda_1 vs. cue_gain).

---

### 4. Discussion

#### 4.1 The Coexistence Threshold as a Structural Constraint
The finding that coexistence does not exist at the commonly used J_cross = 0.5 is a structural constraint on models of multi-item working memory. If the brain maintains multiple items simultaneously, the effective cross-inhibition must be below threshold. This constrains the balance between lateral inhibition and recurrent excitation. Discuss implications for capacity limits in working memory (Bays & Husain, 2008; Ma et al., 2014).

#### 4.2 Heterogeneity Widens the Instability Region
In our symmetric model, the coexistence saddle exists only in a narrow window (Delta_J_cross ~ 0.01). However, biological circuits have heterogeneous connectivity, non-uniform firing thresholds, and spatially structured inhibition. We argue (following GLM 5's analysis) that heterogeneity breaks the clean Goldstone/dominance separation, converts the sharp transition into a smeared crossover, and effectively widens the parameter region where saddle-like dynamics operate. Heterogeneity creates a distribution of effective local J_cross values, so some micro-circuits hit criticality before others. This transforms the single bifurcation point into a bifurcation region.

#### 4.3 The Behavioral Cliff as a J_cross Phenomenon
The traditional view attributes the behavioral cliff to weak cues: below a threshold cue strength, the sensory signal cannot stabilize the correct bump. Our analysis suggests a reinterpretation: the cliff reflects the system's proximity to critical J_cross*. The cue provides stabilization against the dominance instability driven by J_cross. When cue-mediated stabilization fails (cue too weak relative to the distance |J_cross - J_cross*|), the system falls to WTA. This predicts: (i) manipulating cross-inhibition strength (e.g., pharmacologically, via inter-hemispheric suppression) should shift the cliff location; (ii) individual differences in behavioral cliff position may reflect variation in effective J_cross, not variation in sensory sensitivity.

#### 4.4 Goldstone Protection and Functional Significance
The two Goldstone modes have a functional interpretation: they protect bump positions (the stored memory content) from being disrupted by the dominance competition. The system can resolve "which network wins" without disturbing "where each bump sits." This separation of concerns -- amplitude competition in the dominance subspace, position preservation in the Goldstone subspace -- may be a design principle for neural circuits that must make decisions while maintaining stored information.

#### 4.5 Mean-Field vs. Spatially Structured Inhibition
The DC character of the critical eigenvector is a prediction specific to mean-field cross-inhibition. If cross-inhibition were spatially structured (e.g., depending on the angular distance between the two bumps' locations), the critical mode would acquire spatial structure. This is experimentally testable: if the instability that drives WTA transitions is spatially uniform (affecting all neurons equally), this supports mean-field-like cross-inhibition. If the instability is spatially patterned, it implies structured inhibition.

#### 4.6 Connections to the Cusp Catastrophe
The 1D cusp potential V(D) = D^4 + aD^2 + bD is the projection of the 96-dimensional dynamics onto the critical eigenvector. The coefficient a is controlled by J_cross (a crosses zero at J_cross*); the coefficient b is controlled by cue_gain. The spectral analysis validates the mean-field reduction by identifying the critical direction explicitly: it IS the dominance variable D, projected from the uniform eigenvector. But the full spectral analysis adds what the 1D reduction cannot provide: the Goldstone modes, the stability of non-critical directions, and the high-dimensional Kramers prefactor for noise-driven escape.

#### 4.7 Limitations
(i) The model uses rate neurons, not spiking neurons; intrinsic noise structure differs. (ii) Mean-field cross-inhibition is a simplification; realistic inhibitory interneuron pools have spatial and temporal structure. (iii) N=48 is moderate; the Goldstone mode identification becomes cleaner at larger N. (iv) We analyze the deterministic bifurcation; the stochastic (Kramers) analysis of the full system is left for future work.

---

### 5. Conclusion

We have presented the first complete spectral bifurcation analysis of competing ring attractors under mean-field cross-inhibition. Three results stand: (1) coexistence has a sharp existence threshold at J_cross* ~ 0.36; (2) Goldstone modes are symmetry-protected and separate cleanly from the instability; (3) the critical mode is spatially uniform (DC), reflecting the mean-field character of the coupling. Together, these results reframe the behavioral cliff in working memory as a spectral bifurcation phenomenon: the brain operates near critical J_cross*, and cue strength modulates the distance from the bifurcation rather than providing the primary drive for bump formation.

---

## Proposed Figures

### Existing Figures (from completed computations)

| Figure | Source File | Content |
|--------|------------|---------|
| **Fig. 1** | `fig50_coexistence_diagnostic.png` | Coexistence diagnostic: residual, drift rate, dominance, bump heights, and bump positions over time at four cue values (J_cross=0.5). Shows coexistence does NOT converge to a fixed point. |
| **Fig. 3** | `fig51_spectral_separatrix_correct.png` | The spectral separatrix at J_cross=0.35: eigenvalue tracking, dominance, instability index, eigenvector projections, activity profiles at six cue values. 12-panel figure. |
| **Fig. 4** | `fig53_goldstone_separated.png` | Goldstone-separated analysis: lambda_dom vs J_cross (the money plot), Goldstone count, top 5 non-Goldstone eigenvalues, dominant mode character projections, Goldstone magnitudes, bump heights, full spectra at three J_cross values. 9-panel figure. |

### New Figures Needed

| Figure | Content | Priority |
|--------|---------|----------|
| **Fig. 2** | Schematic of the model: two ring networks with cosine connectivity, mean-field cross-inhibition arrows, cue input to network A. Should show the geometry clearly. | High |
| **Fig. 5** | The coexistence existence boundary: a clean plot of max(r_A) and max(r_B) vs J_cross, showing the sharp collapse at J_cross ~ 0.36. Simpler version of the diagnostic for the existence result alone. | High |
| **Fig. 6** | The pitchfork bifurcation diagram: D (dominance) vs J_cross, showing the stable coexistence branch (D=0) splitting into two WTA branches (D > 0 and D < 0) at J_cross*. Classic pitchfork shape. | High |
| **Fig. 7** | Critical eigenvector visualization: side-by-side plots of the Goldstone eigenvector (sine-shaped, one network) and the critical dominance eigenvector (uniform, anti-phase between networks) at J_cross near J_cross*. | Medium |
| **Fig. 8** | Phase diagram in (J_cross, cue_gain) space: regions labeled as "stable coexistence," "coexistence saddle," "WTA only," and "no coexistence." Shading indicates number of positive eigenvalues. | Medium |
| **Fig. S1** | Convergence verification: Newton residual vs iteration for representative fixed points. Confirms machine-precision convergence. | Low (supplement) |

---

## Key Equations to Highlight

### The Dynamics
```
tau * dr_A/dt = -r_A + sigma(W * r_A + cue_A - J_cross * mean(r_B))
tau * dr_B/dt = -r_B + sigma(W * r_B - J_cross * mean(r_A))
```

### The Jacobian (Block Structure)
```
J = [ -I + D_A * W,          D_A * (-J_cross/N * 1*1^T) ]
    [ D_B * (-J_cross/N * 1*1^T),  -I + D_B * W          ]
```

where D_A = diag(sigma'(h_A)), D_B = diag(sigma'(h_B)).

### Goldstone Condition
```
Mean-field coupling: h_cross = -J_cross * (1/N) * sum(r_j)

This depends only on mean(r), not on spatial pattern.
=> Rotational symmetry preserved
=> dF/d(theta_bump) = 0 identically
=> Two exact zero eigenvalues (one per network)
```

### The Pitchfork Bifurcation
```
At cue = 0, the system has A <-> B exchange symmetry.
The coexistence FP (D = 0) loses stability when lambda_dom crosses zero.
lambda_dom(J_cross) = 0  at  J_cross* ~ 0.3485

For J_cross < J_cross*: coexistence is a stable node
For J_cross* < J_cross < 0.36: coexistence is a saddle (1 unstable direction)
For J_cross > 0.36: coexistence ceases to exist
```

### Connection to the Cusp Catastrophe
```
V(D) = D^4 + a(J_cross) * D^2 + b(cue_gain) * D

a(J_cross) < 0  when  J_cross > J_cross*  (double well)
a(J_cross) > 0  when  J_cross < J_cross*  (single well)

The spectral analysis provides: a = f(lambda_dom)
The 1D reduction D = mean(r_A) - mean(r_B) IS the projection onto the
critical eigenvector (which is uniform/DC).
```

### High-Dimensional Kramers Escape (Future Work)
```
tau_escape ~ (2*pi / |lambda_u|) * sqrt(|det J_well / det J_saddle|) * exp(Delta_V / sigma^2)

The determinant ratio involves ALL 96 eigenvalues.
Goldstone modes (lambda = 0) must be handled separately (zero-mode regularization).
The bulk eigenvalues contribute a universal prefactor from their distribution.
```

---

## Target Journals (in order of fit)

1. **Neural Computation** -- Strong mathematical neuroscience tradition, appropriate for spectral/bifurcation analysis
2. **PLOS Computational Biology** -- Broader audience, emphasis on biological implications
3. **Journal of Computational Neuroscience** -- Technical audience, comfortable with Jacobian analysis
4. **Physical Review E** -- If framed as nonlinear dynamics / statistical physics of neural systems
5. **Journal of Mathematical Neuroscience** -- If the Goldstone/pitchfork analysis is emphasized as the main contribution

---

## Key References to Cite

### Working Memory Models
- Compte, A., Brunel, N., Goldman-Rakic, P.S., & Wang, X.J. (2000). Synaptic mechanisms and network dynamics underlying spatial working memory in a cortical network model. *Cerebral Cortex*.
- Wimmer, K., Nykamp, D.Q., Constantinidis, C., & Compte, A. (2014). Bump attractor dynamics in prefrontal cortex explains behavioral precision in spatial working memory. *Nature Neuroscience*.
- Wei, Z., Wang, X.J., & Wang, D.H. (2012). From distributed resources to limited slots in multiple-item working memory: a spiking network model with normalization. *Journal of Neuroscience*.

### Bifurcation Theory / Dynamical Systems
- Strogatz, S.H. (2015). *Nonlinear Dynamics and Chaos*. 2nd ed.
- Guckenheimer, J. & Holmes, P. (1983). *Nonlinear Oscillations, Dynamical Systems, and Bifurcations of Vector Fields*.
- Goldstone, J. (1961). Field theories with superconductor solutions. *Nuovo Cimento*.

### Kramers Escape / Noise-Driven Transitions
- Kramers, H.A. (1940). Brownian motion in a field of force and the diffusion model of chemical reactions. *Physica*.
- Hanggi, P., Talkner, P., & Borkovec, M. (1990). Reaction-rate theory: fifty years after Kramers. *Reviews of Modern Physics*.

### Ring Attractors / Continuous Attractors
- Ben-Yishai, R., Bar-Or, R.L., & Sompolinsky, H. (1995). Theory of orientation tuning in visual cortex. *PNAS*.
- Seung, H.S. (1996). How the brain keeps the eyes still. *PNAS*.

### Cusp Catastrophe in Neural Systems
- Thom, R. (1972). *Structural Stability and Morphogenesis*.
- Zeeman, E.C. (1977). *Catastrophe Theory: Selected Papers*.

---

## Notes on Framing

The paper should be framed as **computational neuroscience with rigorous mathematics**, not as pure dynamical systems theory. The biological motivation (working memory competition, behavioral cliff) should open and close the paper. The spectral analysis is the method, not the message.

The Goldstone mode finding is perhaps the most novel contribution -- it connects condensed matter physics concepts (Goldstone theorem, symmetry-protected zero modes) to neural circuit dynamics in a concrete, computable way. This framing will be attractive to physicists working in theoretical neuroscience.

The "cliff as J_cross phenomenon" reinterpretation is the most provocative claim and should be presented carefully as a hypothesis with testable predictions, not as a proven result.

The connection to the broader research program (RMT, free probability, transformer attention) should be mentioned briefly in the Discussion (Section 4.6 and a forward-looking paragraph) but NOT developed in this paper. This paper is about the ring attractor. The broader spectral framework is for subsequent papers.

---

*Structure drafted February 12, 2026.*
*Computation code: `corpus/code/spectral_separatrix_correct.py`, `spectral_separatrix_goldstone.py`, `coexistence_diagnostic.py`*
*GLM 5 critiques incorporated from: `corpus/voices/2026-02-12-164527-glm-5.md`, `corpus/voices/2026-02-12-172320-glm-5.md`*
