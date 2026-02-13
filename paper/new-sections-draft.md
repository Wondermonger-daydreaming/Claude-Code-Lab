# New Sections for Paper Draft v2

*Drafted February 13, 2026 — to be integrated into spectral-separatrix-draft.md*

---

## Section 3.5: Stochastic Phase Diagram

### 3.5.1 Parameter Sweep Design

To bridge the deterministic bifurcation analysis with behavioral predictions, we performed a large-scale stochastic simulation across the $(J_\times, c)$ parameter space. At each of 256 grid points (16 values of $J_\times$ from 0.05 to 8.0, 16 values of drive strength from 1.0 to 8.0), we ran 500 stochastic trials. Two ring networks encoded items separated by $\pi/2$ radians. Independent Gaussian noise ($\sigma = 0.1$) was added to each neuron at each time step during a 500-step maintenance period. The decoded response was classified as a swap error if it fell within 0.3 rad of the non-target item's location.

### 3.5.2 Onset of Swap Errors

Swap errors emerge at $J_\times \approx 0.25$, consistent with the spectral prediction of the pitchfork bifurcation at $J_\times^* \approx 0.3485$ (Fig. 8). The stochastic onset is lower than the deterministic bifurcation because noise-mediated escape from the metastable coexistence well occurs at barrier heights comparable to $\sigma^2$, which corresponds to a $J_\times$ slightly below the point where $\lambda_{dom}$ crosses zero. This is precisely the Kramers mechanism described in Section 4.5.

Below $J_\times \approx 0.25$, the coexistence state is strongly stable ($\lambda_{dom} < -0.3$), and noise cannot escape the well during the trial duration. Between $J_\times \approx 0.25$ and $0.5$, swap rates increase from 5% to approximately 45%, reflecting the shrinking barrier as the system approaches and passes through the pitchfork. Above $J_\times \approx 1.0$, swap rates plateau near 50% -- the system has become a noise-driven bistable switch with no memory of the initial encoding.

### 3.5.3 Drive Strength Is Secondary

Across the full parameter space, the phase diagram shows near-vertical isocontours of swap rate (Fig. 8A): the swap error probability depends primarily on $J_\times$ and only weakly on drive strength. This is a direct prediction of the spectral analysis. The critical eigenvector is spatially uniform (DC mode), governing total activity competition rather than spatial encoding quality. Stronger drive does not protect against the dominance instability because the instability is orthogonal to the encoding direction.

This result has a surprising implication: the commonly proposed intervention for working memory failures -- increasing stimulus strength -- targets the wrong degree of freedom. The cliff is a $J_\times$ phenomenon, not a cue phenomenon. Pharmacological or neuromodulatory interventions that alter the effective cross-inhibition should be more effective than those that enhance sensory processing.

### 3.5.4 The Non-Monotonic Valley

At intermediate $J_\times \approx 1.2$--$1.6$, with moderate to strong drive ($c > 3.0$), the phase diagram reveals a non-monotonic feature: swap rates dip to approximately 7--13% between two distinct failure modes (Fig. 8B):

1. **Near-critical swaps** ($J_\times \approx 0.3$--$0.5$): At the pitchfork bifurcation, the barrier is small and noise escapes freely. Both networks have comparable firing rates, and the WTA outcome is essentially a coin flip. Swap rate approaches 50%.

2. **Overpowering swaps** ($J_\times > 2.0$, weak drive): Strong cross-inhibition overwhelms the feedforward encoding signal. During the maintenance period, one network suppresses the other regardless of which received the stronger input. At weak drive, the encoding advantage is insufficient to resist suppression.

3. **The valley** ($J_\times \approx 1.2$--$1.6$, moderate drive): Here, the cross-inhibition is strong enough to produce clear WTA dynamics, but the encoding drive is also strong enough to "lock in" the correct network during the stimulus presentation. The correct representation is captured by a deep attractor basin before the maintenance-period competition begins. This produces a local minimum in swap rate -- a functional operating region where the circuit achieves reliable WTA selection of the correct item.

The valley is the predicted operating point for a healthy working memory circuit: cross-inhibition strong enough to resolve competition clearly, drive strong enough to bias the competition correctly. This is consistent with the broad parametric tuning observed in neural circuits -- the system need not be precisely at $J_\times^*$ to function, but rather in the valley regime where WTA dynamics and encoding strength are balanced.

---

## New Discussion Material

### 4.X Connection to Stochastic Attractor Models

Our deterministic spectral analysis and the stochastic attractor models of Penny (2024) provide complementary descriptions of the same dynamics. Penny modeled working memory maintenance as a stochastic differential equation $dx = \beta g(x) dt + \sigma dw$, where $g(x)$ is the deterministic flow and $\sigma dw$ is Brownian noise. Swap errors in Penny's framework arise when "memory traces diffuse away from their initial state and are captured by the attractors of other items" -- a diffusion-capture mechanism that operates on the attractor landscape without requiring an explicit swap mechanism.

Our cusp potential $V(D) = D^4 + aD^2 + bD$ provides the deterministic landscape on which Penny's stochastic dynamics unfold. The Kramers escape analysis (Section 4.5) bridges the two frameworks: the escape rate $\tau^{-1} \sim \exp(-\Delta V / \sigma^2)$ connects the barrier height (set by the spectral bifurcation structure at $J_\times^*$) to the swap error probability (set by the stochastic dynamics). Penny's model was validated against behavioral data from 90 subjects; our analysis provides the spectral characterization of the underlying attractor landscape that his stochastic model assumes.

A key prediction emerges from the synthesis: the swap error rate should increase continuously with maintenance delay (as Penny predicts from accumulated diffusion), but the rate of increase should exhibit a sharp change at $J_\times^*$ (as our bifurcation analysis predicts from barrier collapse). The cusp sets the landscape; noise navigates it.

### 4.X Selection Versus Representation Failure

Recent neural recordings from monkey prefrontal cortex during multi-item working memory tasks have revealed that swap errors can arise from misselection of correctly remembered items rather than from representation failure (Alleman et al., 2024). Both item representations persist in the neural population, but the readout process selects the wrong item. This selection-representation distinction maps directly onto our phase diagram.

In our model, the non-monotonic valley at $J_\times \approx 1.2$--$1.6$ corresponds to the regime where both bump representations coexist (neither has been destroyed by cross-inhibition) but the WTA competition during readout can select the wrong network. This is selection failure: the items are stored correctly, but the competitive dynamics at readout produce an incorrect winner. At higher $J_\times$ ($> 2.0$), one bump is suppressed entirely during maintenance -- a representation failure where the non-target item's encoding is destroyed before readout.

Our model therefore predicts both mechanisms in different parameter regimes, with the boundary between them governed by $J_\times$. The Alleman et al. finding that swaps in healthy subjects arise from misselection suggests that the brain operates in or near the valley regime, where cross-inhibition is strong enough for reliable WTA selection but not so strong as to destroy representations. This interpretation generates a testable prediction: in conditions that increase effective cross-inhibition (e.g., distractor-rich environments, high cognitive load), swap errors should shift from selection-type (both items present in the population) to representation-type (one item absent).

### 4.X Universality of the Saddle-Point Bifurcation

The pitchfork bifurcation we identify in coupled ring attractors -- where "attractors are extinguished after merging with saddle points" at high cross-inhibition -- has structural analogs in decision-making circuits. Models of choice-selective inhibition in prefrontal cortex describe the same saddle-node merger: disjoint neural groups with within-group excitation and across-group inhibition exhibit group winner-take-all dynamics, and the transition from multistable coexistence to WTA occurs via a saddle-point annihilation (Machens et al., 2005; Wong and Wang, 2006).

The structural isomorphism suggests that the spectral separatrix is not specific to working memory but describes the generic bifurcation of any neural circuit with competing stable states. Decision-making, attention, and working memory all involve competition between neural populations, and the mathematical structure of this competition -- the pitchfork bifurcation at critical coupling, the Goldstone protection of positional degrees of freedom, the DC character of the instability under mean-field coupling -- should appear across all three domains. The spectral analysis we present here provides a template for characterizing these transitions in other systems.

---

## New References to Add

Alleman, M., Panichello, M.F., Buschman, T.J., & Johnston, W.J. (2024). The neural basis of swap errors in working memory. *PNAS*, 121(33), e2401032121.

Penny, W.D. (2024). Stochastic attractor models of visual working memory. *PLOS ONE*, 19(5), e0301039.

Machens, C.K., Romo, R., & Brody, C.D. (2005). Flexible control of mutual inhibition: a neural model of two-interval discrimination. *Science*, 307(5712), 1121-1124.

Wong, K.-F. & Wang, X.-J. (2006). A recurrent network mechanism of time integration in perceptual decisions. *Journal of Neuroscience*, 26(4), 1314-1328.

---

*Drafted: February 13, 2026*
*To be integrated with fig54 results (Section 4.2) and figure references once agents complete*
