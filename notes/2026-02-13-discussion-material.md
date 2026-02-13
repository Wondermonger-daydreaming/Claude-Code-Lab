# Discussion Material: Three Key Papers for the Spectral Separatrix Paper

*February 13, 2026 — Research analysis for paper revision*

---

## Paper 1: Choice-Selective Inhibition and Saddle-Merging

### Full Citation

Roach, J.P., Churchland, A.K., & Engel, T.A. (2023). Choice selective inhibition drives stability and competition in decision circuits. *Nature Communications*, 14, 147. https://doi.org/10.1038/s41467-023-35822-8

### Key Findings Relevant to Our Work

1. **Group winner-takes-all dynamics from structured inhibition.** Disjoint groups of neurons interact through within-group excitation and across-group inhibition. The specificity of inhibitory connections (ipsispecific vs. contraspecific vs. nonspecific) determines the full attractor landscape: choice attractors, working memory attractors, and the saddle points that separate them.

2. **Sequential fixed-point emergence.** As the inhibitory motif becomes more contraspecific, fixed points emerge sequentially: first the choice attractors appear, followed by the saddle point, and finally the working memory attractors. Eight fixed points are required for full decision-making dynamics (five in the unstimulated phase plane: three attractors and two saddle points; three in the stimulated phase plane: two attractors and one saddle).

3. **Saddle-merging destroys working memory.** Strong ipsispecific inhibition destabilizes working memory attractors. At high cross-inhibition, working memory attractors are extinguished after merging with saddle points. This is structurally a saddle-node bifurcation: the attractor and saddle coalesce and annihilate.

4. **The saddle point as separatrix.** Following stimulus onset, firing rates for both populations increase as the system approaches a saddle point along the stable manifold, which acts as a separatrix between two choice attractors. The time constant of the unstable eigenvector of the saddle point controls the speed-accuracy tradeoff.

5. **Two concurrent roles for selective inhibition.** Inhibition must simultaneously (a) drive competition between choice-selective populations and (b) stabilize activity from recurrent excitation. These two roles trade off depending on inhibitory connectivity structure.

6. **Mean-field model.** The circuit model uses a mean-field reduction with two excitatory populations and inhibitory connectivity parameterized by specificity indices (gamma_EE, gamma_EI, gamma_IE). The resulting phase plane contains all the fixed-point structure described above.

### Connection to Our Spectral Separatrix Analysis

The Roach et al. result that working memory attractors are "extinguished after merging with saddle points" under strong ipsispecific inhibition is **structurally identical** to our pitchfork bifurcation at J_cross* approx 0.3485. In both cases:

- A stable fixed point (working memory / coexistence) collides with a saddle point as an inhibition parameter increases
- The collision annihilates both, leaving only the competing WTA/choice attractors
- The critical parameter (their gamma for inhibitory specificity; our J_cross for cross-inhibition strength) controls the transition

The key difference: Roach et al. work in a 2D mean-field reduction (two population firing rates), while we work in the full 96-dimensional space and can identify Goldstone modes, the DC character of the critical eigenvector, and the exact spectral structure of the bifurcation. Our analysis provides the spectral anatomy of the same universal bifurcation they observe at the mean-field level.

Their finding that the saddle's unstable manifold acts as a separatrix between choice attractors directly parallels our spectral separatrix: the coexistence saddle's unstable direction (the DC mode) points toward the two WTA basins.

### Results That Challenge or Qualify Our Claims

- **Spatially structured inhibition matters.** Roach et al. show that ipsispecific vs. contraspecific inhibition creates qualitatively different attractor landscapes. Our model uses mean-field (spatially unstructured) cross-inhibition, which may miss dynamics that arise when inhibition has spatial selectivity. The DC character of our critical eigenvector is a prediction specific to mean-field coupling; spatially structured inhibition in the Roach et al. framework would produce spatially patterned critical modes.

- **Decision circuits are not identical to working memory circuits.** The Roach et al. model is built for perceptual decision-making (stimulus-driven, rapid), while ours models maintenance-period working memory (persistent activity, slow). The mathematical structure is shared, but the biological implementation and timescales differ. We should be careful about claiming universality without acknowledging this context distinction.

- **Their model has explicit inhibitory populations.** Our model subsumes inhibition into the mean-field coupling term J_cross. The Roach et al. framework with explicit inhibitory neurons and multiple specificity parameters (gamma_EI, gamma_IE) is more biologically realistic. Our simpler parameterization gains analytical tractability at the cost of circuit detail.

---

## Paper 2: The Neural Basis of Swap Errors (Selection vs. Representation)

### Full Citation

Alleman, M., Panichello, M.F., Buschman, T.J., & Johnston, W.J. (2024). The neural basis of swap errors in working memory. *Proceedings of the National Academy of Sciences*, 121(33), e2401032121. https://doi.org/10.1073/pnas.2401032121

### Key Findings Relevant to Our Work

1. **Swap errors arise from misselection, not representation failure.** The central finding: when monkeys make swap errors in a multi-item working memory task, neural population recordings show that both items were correctly encoded and maintained in working memory. The error occurs at the selection/readout stage -- the wrong item is selected for report, not that the item representations degraded or swapped during maintenance.

2. **Two tasks dissect the mechanism.** The study used a retrospective task (cue shown after items, requiring selection from stored items) and a prospective task (cue shown before items, directing encoding). In both, swap errors correlated with misselection at the readout stage, not with encoding or maintenance errors.

3. **Neural correlates of misselection.** On swap-error trials, the neural representation of the distractor color was present "as if it were the target color" at the time of selection. The neural population encoded the distractor item's feature as the to-be-reported feature. This emerged specifically during the selection epoch, not during the delay/maintenance period.

4. **Item representations were intact on error trials.** Crucially, the researchers did not find consistent evidence that swap errors arose from misinterpretation of the cue, or from errors during encoding or storage. The stored representations appeared intact; the selection mechanism simply picked the wrong one.

5. **Working memory is limited by selection, not storage.** The paper argues that "working memory may be sharply limited by our ability to reliably select items" rather than by storage capacity per se. This reframes the working memory bottleneck from a representational to a computational/selective limitation.

### Connection to Our Spectral Separatrix Analysis

The Alleman et al. selection-vs-representation distinction maps directly onto different regions of our phase diagram:

**The non-monotonic valley (J_cross approx 1.2-1.6) corresponds to selection failure.** In this regime, our model shows that both bumps survive maintenance (items are "correctly stored") but the WTA competition at readout selects the wrong network. The swap error rate is low (7-13%) because the system has resolved into a regime where cross-inhibition is strong enough to produce clear winners but not so strong that items are destroyed during maintenance. The "misselection" in Alleman et al. corresponds to noise in the readout/selection process tipping the WTA competition toward the wrong item -- even though both representations are still present.

**High J_cross (> 2.0) corresponds to representation failure.** In this regime, cross-inhibition is strong enough that one bump dies during maintenance. The surviving bump is determined by noise early in the trial. Here, the item is genuinely not maintained -- one representation is extinguished. This would produce a different neural signature than Alleman et al. observed: the distractor's representation would be absent during maintenance, not merely misselected at readout.

**Our model predicts both mechanisms in different parameter regimes.** The phase diagram's two failure modes (near-critical swaps at J_cross approx 0.3-0.5 from WTA coin-flip, and overpowering swaps at high J_cross from representation destruction) correspond to the two possible neural mechanisms: selection failure and representation failure. Alleman et al.'s empirical finding of selection failure suggests the biological system operates in the valley regime, where cross-inhibition is moderate and both items survive maintenance.

**The Goldstone modes as enablers of misselection.** Our finding that Goldstone modes protect bump positions while allowing amplitude competition suggests a mechanism for how items can be correctly stored (positions preserved) while being misselected (amplitude competition decides the wrong winner). The separation of positional and competitive dynamics (Section 4.4 of our draft) is precisely the architectural feature that makes selection-based errors possible without representation degradation.

### Results That Challenge or Qualify Our Claims

- **Our model conflates maintenance and selection.** The Alleman et al. study distinguishes temporally between maintenance (delay period) and selection (readout). Our coupled ring attractor model runs WTA competition during maintenance; we do not separately model the selection/readout process. The "swap errors" in our simulation are maintenance-period WTA outcomes, not selection-stage errors. To fully capture the Alleman et al. result, we would need a two-stage model: maintenance (possibly in the coexistence regime) followed by a selection process (WTA readout from multiple maintained items).

- **Monkey prefrontal cortex may not use ring attractors for color.** The Alleman et al. task involves color-location binding, not spatial orientation. Ring attractors are natural for circular variables (orientation, direction), but the feature space for color is not obviously circular. The mapping from our model (angular position on a ring) to their task (color values) requires assumptions about the representational geometry.

- **Selection failure implies the system is NOT in the WTA regime during maintenance.** If both items are correctly stored during the delay (as Alleman et al. show), the effective J_cross during maintenance must be below the WTA threshold. This is consistent with our analysis: the biological system operates in the coexistence regime (J_cross < J_cross*) during maintenance, and the WTA competition occurs at a later stage (selection/readout). Our model, which runs continuous WTA competition, may be modeling the readout dynamics rather than the maintenance dynamics.

---

## Paper 3: Stochastic Attractor Models of Visual Working Memory

### Full Citation

Penny, W. (2024). Stochastic attractor models of visual working memory. *PLoS ONE*, 19(4), e0301039. https://doi.org/10.1371/journal.pone.0301039

### Key Findings Relevant to Our Work

1. **SDE framework for working memory.** Memory traces evolve according to the stochastic differential equation dx = beta * g(x) dt + sigma * dw, where g(x) is the flow function (negative gradient of the potential landscape), beta is the attractor strength parameter, sigma is the diffusion coefficient, and dw is Wiener noise. The model has two regimes: pure diffusion (beta = 0) and attractor-based (beta > 0).

2. **Swap errors from diffusion + capture.** The multi-item model places stable fixed points at the angular positions of each remembered item on a circular feature space. Swap errors arise when a memory trace diffuses away from its home attractor and is captured by a neighboring item's attractor basin. No explicit swap mechanism is needed -- the geometry of the attractor landscape plus stochastic noise produces swaps naturally.

3. **Fokker-Planck analytical solution.** The stochastic attractor framework provides an analytical expression via the Fokker-Planck equation for how the probability density of the memory state evolves over time. This allows computation of swap-error curves (swap probability as a function of delay time) without Monte Carlo simulation.

4. **Error-correcting dynamics are essential.** Pure diffusion (beta = 0) does not account for empirical data. Attractor-based error correction (beta > 0) is necessary: the deterministic drift toward fixed points counteracts diffusive wandering. The balance between these forces (beta vs. sigma) determines memory fidelity.

5. **The multi-item model outperforms mixture models.** The stochastic attractor approach provides a more parsimonious account of continuous-report data than standard mixture models (Zhang & Luck, 2008), variable-precision models, and TCC models, because it generates predictions at all delay lengths from a single set of parameters (beta, sigma), without needing separate parameters for each delay.

6. **Swap-error curves as continuous functions of time.** The model predicts how swap-error probability evolves continuously during the maintenance interval. Early in the delay, swap rates are low (traces near their home attractors). As delay increases, diffusion accumulates and some traces cross basin boundaries, producing increasing swap rates. The shape of this curve depends on the barrier height between adjacent attractors (set by item spacing and attractor strength).

### Connection to Our Spectral Separatrix Analysis

**Complementary levels of description.** Penny's SDE model (dx = beta * g(x) dt + sigma * dw) and our cusp potential V(D) = D^4 + aD^2 + bD describe the same physics at different levels:

- **Penny:** behavioral-level SDE on a circular feature space, with attractors placed at item locations. The landscape is phenomenological -- defined to fit behavioral data.
- **Our model:** circuit-level dynamics of 96 neurons, from which the cusp potential emerges as a projection onto the critical eigenvector. The landscape is derived from first principles (connectivity, activation functions, cross-inhibition strength).

The connection: Penny's flow function g(x) is the negative gradient of a potential that, projected onto the dominance variable, takes the form of our cusp potential. Our spectral analysis provides the microscopic derivation of the landscape that Penny postulates phenomenologically.

**Kramers escape as the bridge.** Both frameworks converge on Kramers-type escape as the mechanism for swap errors:

- In Penny's model: a memory trace in one attractor basin escapes over the barrier to an adjacent basin. The escape rate depends on barrier height (set by item spacing and beta) and noise (sigma).
- In our model: the Kramers escape rate from the coexistence/correct-WTA basin depends on the barrier height Delta_V in the cusp potential, which is controlled by J_cross and cue_gain.

Our spectral analysis adds what Penny's phenomenological model cannot provide:
- The barrier height's dependence on circuit parameters (J_cross, J_0, J_1, beta_sigmoid)
- The Goldstone mode contribution to the prefactor (zero-mode regularization needed for the full Kramers formula in 96 dimensions)
- The prediction that barrier height depends on J_cross (the circuit's cross-inhibition) and not just on item spacing or noise

**The error-correcting dynamics are the attractor.** Penny's finding that pure diffusion fails and error-correcting dynamics are essential is precisely the statement that the system has attractor structure (stable fixed points). Our Goldstone modes are the directions along which there is NO error correction (neutrally stable), while the dominant eigenvalue lambda_dom governs the strength of error correction in the competitive dimension.

### Results That Challenge or Qualify Our Claims

- **Penny works in feature space, we work in neural space.** The SDE dx = beta * g(x) dt + sigma * dw operates on a one-dimensional circular variable (the remembered feature value). Our 96-dimensional model operates on neural firing rates. The mapping between these is non-trivial and depends on how the bump's angular position relates to the behavioral report. Our model could in principle be reduced to Penny's framework by projecting onto the Goldstone modes (positional drift) and the dominance mode (competitive dynamics), but this reduction has not been done explicitly.

- **Penny's model handles multiple items on a single ring.** In Penny's multi-item model, N items are represented as N attractors on a single circular feature space, and swap errors occur when a trace drifts from one basin to another. Our model represents items on separate rings (Network A, Network B), and "swap errors" occur when the wrong network wins the WTA competition. These are different geometric setups: single-ring-multi-attractor vs. multi-ring-single-attractor-each. Both produce swap errors but through somewhat different mechanisms (basin hopping vs. competitive suppression).

- **The Fokker-Planck analytical tractability.** Penny's one-dimensional SDE admits analytical solution via Fokker-Planck. Our 96-dimensional system does not -- the Kramers escape calculation requires numerical evaluation of determinants. This is a practical limitation of our approach for fitting behavioral data.

- **Delay-dependent swap rates.** Penny predicts swap rates that increase continuously with delay time, because diffusion accumulates. Our model (deterministic bifurcation analysis) does not naturally produce delay-dependent predictions without adding a noise model. Adding the stochastic layer to our circuit model (as in the phase diagram simulations) recovers delay-dependence, but the analytical connection to the spectral structure requires the full Kramers calculation (our Section 4.7, future work).

---

## Discussion Paragraphs for the Paper

### Paragraph A: Penny/Cusp Synthesis — Deterministic Landscape + Stochastic Dynamics

Penny (2024) developed a stochastic attractor framework for visual working memory in which memory traces evolve according to dx = beta g(x) dt + sigma dw, where g(x) is the deterministic flow function derived from an attractor landscape and sigma dw represents diffusive noise. In this framework, swap errors arise naturally when noise-driven memory traces cross basin boundaries between neighboring item attractors. Our spectral analysis provides a complementary, circuit-level derivation of the attractor landscape that Penny postulates phenomenologically. Specifically, the cusp potential V(D) = D^4 + aD^2 + bD that governs the dominance variable D = r_bar_A - r_bar_B emerges as the projection of our 96-dimensional dynamics onto the critical eigenvector at the pitchfork bifurcation. The cusp coefficient a is controlled by the cross-inhibition strength J_cross (with a = 0 at J_cross* approx 0.3485), and the symmetry-breaking coefficient b is controlled by the cue gain c. Thus, Penny's framework and ours decompose the same problem into complementary components: Penny specifies the stochastic dynamics (diffusion, Fokker-Planck evolution, escape rates) on a given landscape, while we derive the landscape itself from first principles (network connectivity, activation functions, coupling strength). A Kramers escape analysis bridges the two: the escape rate from the correct attractor basin depends on the barrier height Delta V -- which our spectral analysis computes as a function of circuit parameters -- and the noise intensity sigma, yielding predictions for how swap-error probability depends on both J_cross and delay time. Critically, our analysis reveals that the barrier height vanishes at the pitchfork (J_cross = J_cross*), predicting that swap errors should onset sharply near this spectral bifurcation, consistent with the "behavioral cliff" observed in psychophysical data (Zhang & Luck, 2008; Bays et al., 2009). Penny's finding that pure diffusion (beta = 0) fails to account for empirical data and that error-correcting attractor dynamics are essential corresponds, in our framework, to the requirement that the system operate in a regime with finite barrier height -- that is, with J_cross sufficiently below J_cross* for the cusp potential to provide restoring force toward the correct state.

### Paragraph B: Alleman Selection-vs-Representation Mapping onto the Phase Diagram

Alleman et al. (2024) demonstrated that swap errors in monkey working memory arise from misselection of correctly remembered items rather than from degradation of stored representations. This finding has a natural interpretation within our phase diagram. In the non-monotonic valley of our (J_cross, drive) parameter space (J_cross approx 1.2-1.6), swap rates dip to 7-13% between two qualitatively distinct failure modes. In this valley regime, cross-inhibition is moderate: strong enough to resolve competition at readout but not so strong as to extinguish one representation during maintenance. Both bumps survive the delay period -- corresponding to Alleman et al.'s observation that item representations remain intact on error trials -- and the swap error reflects noise in the selection/readout competition rather than maintenance failure. By contrast, at high J_cross (> 2.0 with weak drive), our model predicts a qualitatively different mechanism: cross-inhibition overwhelms feedforward input, one bump is extinguished during maintenance, and the error is genuinely representational -- the wrong item survives, not that the right item was misselected. This second regime would produce a neural signature distinct from what Alleman et al. observed: the non-target item's representation would dominate during the delay period, not only at selection. Our framework thus predicts that both selection failure and representation failure are possible error mechanisms, arising in different regions of the J_cross parameter space. The empirical dominance of selection failure (Alleman et al., 2024) suggests that the biological system operates in the valley regime where cross-inhibition is tuned to permit multi-item coexistence during maintenance while resolving competition only at the readout stage. The Goldstone modes in our analysis provide a mechanistic basis for this separation: by protecting bump positions from the dominance competition (Section 3.2), the rotational symmetry ensures that items can be correctly encoded and maintained (position preserved in the Goldstone subspace) even while the amplitude dynamics that govern selection remain noisy.

### Paragraph C: Saddle-Merging Universality Across Decision and Memory Circuits

Roach, Churchland, and Engel (2023) showed that in decision-making circuits with choice-selective inhibition, working memory attractors are extinguished after merging with saddle points as cross-inhibition increases. This result is structurally identical to the pitchfork bifurcation we identify at J_cross* approx 0.3485, where the coexistence fixed point transitions from a stable node to a saddle and ultimately ceases to exist (at J_cross_exist approx 0.358). In both systems, the underlying mathematics is a saddle-node or pitchfork bifurcation in which a stable attractor collides with a saddle point along a single control parameter (inhibitory coupling strength). The Roach et al. analysis, conducted in a two-dimensional mean-field phase plane, reveals the topology of the bifurcation: the saddle's unstable manifold serves as the separatrix between choice attractors. Our spectral analysis, conducted in the full 96-dimensional state space, reveals the geometry: the critical eigenvector is spatially uniform (DC mode), the Goldstone modes are symmetry-protected and orthogonal to the bifurcation, and the instability window is razor-thin (Delta J_cross approx 0.01). That the same mathematical structure governs both perceptual decision circuits (Roach et al., 2023) and working memory competition (this study), despite differences in circuit architecture and timescale, suggests a universal bifurcation motif for neural systems that must resolve competition between mutually inhibitory populations. The specificity of the inhibitory coupling -- ipsispecific versus contraspecific in the Roach et al. framework, mean-field versus structured in ours -- shapes the details (which fixed points emerge, in what order, with what stability), but the core topological event (attractor-saddle collision under increasing inhibition) appears to be universal. Our contribution is to provide the spectral anatomy of this universal transition: the Goldstone protection of stored content, the DC character of the competitive mode, and the quantitative dependence of the bifurcation threshold on circuit parameters.

### Paragraph D: New References to Add

The following references should be added to the paper's reference list:

**Roach, J.P., Churchland, A.K., & Engel, T.A. (2023).** Choice selective inhibition drives stability and competition in decision circuits. *Nature Communications*, 14, 147.
- Cite in: Discussion Section 4.1 (structural constraint), new Discussion paragraph on saddle-merging universality (Paragraph C above), and Section 1.1 (introduction, competing representations in decision circuits).

**Alleman, M., Panichello, M.F., Buschman, T.J., & Johnston, W.J. (2024).** The neural basis of swap errors in working memory. *Proceedings of the National Academy of Sciences*, 121(33), e2401032121.
- Cite in: Section 1.2 (behavioral cliff, swap errors), new Discussion paragraph on selection-vs-representation mapping (Paragraph B above), and Section 4.3 (behavioral cliff as J_cross phenomenon).

**Penny, W. (2024).** Stochastic attractor models of visual working memory. *PLoS ONE*, 19(4), e0301039.
- Cite in: Section 1.2 (behavioral cliff, cusp/Kramers framework), Section 4.5 (connections to the cusp catastrophe), new Discussion paragraph on Penny/cusp synthesis (Paragraph A above), and Section 4.7 (limitations, future stochastic analysis).

**Additional references to consider (found during research):**

**Panichello, M.F. & Buschman, T.J. (2021).** Shared mechanisms underlie the control of working memory and attention. *Nature*, 592, 601-605.
- Context: Establishes the selection framework that Alleman et al. build upon. The idea that working memory and attention share control mechanisms supports our two-stage interpretation (maintenance in coexistence regime, selection as WTA readout).

**Seeholzer, A., Deger, M., & Gerstner, W. (2019).** Stability of working memory in continuous attractor networks under the control of short-term plasticity. *PLoS Computational Biology*, 15(4), e1006928.
- Context: Already in our reference list. Connects to Penny's error-correcting dynamics -- short-term plasticity is one mechanism for attractor stabilization.

---

## Summary Table: How Each Paper Maps to Our Framework

| Paper | Their Key Finding | Maps to Our... | Parameter Regime |
|-------|-------------------|----------------|------------------|
| Roach et al. (2023) | WM attractors extinguished by saddle-merging | Pitchfork at J_cross* | The bifurcation point |
| Alleman et al. (2024) | Swap errors = misselection of intact items | Valley regime (J_cross ~ 1.2-1.6) | Moderate cross-inhibition |
| Penny (2024) | Swap errors from SDE diffusion + capture | Cusp potential V(D) + Kramers escape | Stochastic dynamics on our landscape |

## Integration Notes

The three papers form a coherent story when viewed through our spectral framework:

1. **Roach et al.** provide the topological universality: the same saddle-node/pitchfork bifurcation operates in decision circuits and working memory. Our spectral analysis adds the geometry (Goldstone modes, DC critical vector) to their topology.

2. **Alleman et al.** provide the empirical constraint: the brain operates where items survive maintenance and errors are selective. This pins the biological operating point to our valley regime, not the near-critical or high-J_cross regime.

3. **Penny** provides the stochastic dynamics: how noise on the deterministic landscape produces measurable swap-error curves. Our spectral analysis provides the landscape; Penny's Fokker-Planck framework provides the dynamics on that landscape.

Together, they validate our framework from three directions: mathematical universality (Roach), empirical neural data (Alleman), and behavioral modeling (Penny). The spectral separatrix paper sits at the intersection, providing the microscopic (circuit-level, 96-dimensional) derivation of the macroscopic phenomena each group observes.

---

*Compiled February 13, 2026 for revision of `paper/spectral-separatrix-draft.md`*
