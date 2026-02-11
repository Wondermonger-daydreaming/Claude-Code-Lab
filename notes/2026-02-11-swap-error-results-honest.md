---
title: "Swap Error Simulation: What the Run Actually Showed"
date: 2026-02-11
type: computation-results
instance: Claude Opus 4.6
status: partial-failure
---

# Swap Error Simulation: What the Run Actually Showed

*Trust the run. The run said: "not swap errors. Blending."*

---

## The Prediction

The loom (Feb 10) and the archive's geometric theory predicted:
> "If you encode two items on overlapping manifolds, decoding one is
> contaminated by the other. The mixture model's 'swap' component is
> actually geometric."

Specific prediction: a bump in the error distribution at the non-target
item's location, without any swap mechanism.

## What Actually Happened

### Figure 7: No swap bump. Blending instead.

| Condition | Result |
|-----------|--------|
| Single item (control) | Clean unimodal, kurtosis 0.09 |
| Two items, 90° apart | Shifted unimodal at ~0.8 rad (midpoint). No bump at item 2 (1.57 rad) |
| Two items, 45° apart | Shifted unimodal at ~0.4 rad (midpoint). No bump at item 2 (0.79 rad) |

The distribution shifts toward the midpoint between items. It does NOT
develop a second mode at the non-target location.

### Figure 8: Mean bias ≈ separation/2

The decoder consistently reports an angle approximately halfway between
the two items. Mean bias is nearly linear with separation up to ~155°,
then drops to 0 at 180° (symmetric case).

### The Numbers

```
Separations (°):  22   45   68   90   112  135  158  180
Mean biases (°):  11   23   34   45   56   67   71   -2
Ratio (bias/sep): 0.50 0.50 0.50 0.50 0.50 0.50 0.45 ~0
```

The pattern is stark: bias/separation ≈ 0.5. The decoder averages.

## Why This Happened (Mechanistic)

The model uses equal weights (0.5 each). The combined response:

    r = 0.5 * f(θ₁) + 0.5 * f(θ₂) + noise

The ML decoder minimizes ||r - f(θ)||². For equal weights, the minimum
is near the midpoint between θ₁ and θ₂ because the blend is roughly
equidistant from both templates.

This produces **attraction**, not **swapping**. Blending is smooth
interpolation. Swapping is discrete — report one OR the other.

## What Would Produce Actual Swap Errors

To get bimodal distributions (the swap signature), the model would need:

1. **Stochastic resource allocation**: On each trial, randomly assign
   most gain to one item (e.g., 0.9/0.1 split), so the decode snaps
   near one item or the other. Over trials, this produces a bimodal
   distribution.

2. **Winner-take-all decoding**: Instead of ML decode on a continuous
   manifold, decode via discrete attractor states. Each attractor
   captures one item; noise determines which attractor wins.

3. **Separate subpopulations with crosstalk**: Each item encoded by
   its own neurons, with occasional crosstalk that substitutes one
   item's encoding for the other.

All three require something BEYOND simple manifold geometry + Gaussian
noise + ML decoding. The geometric model may need to be augmented.

## What This Means for the Archive's Theory

The manifold-bends-the-noise principle is real and demonstrated by
manifold_errors.py. But the claim that "swap errors are geometric" is
NOT supported by this simulation. The geometric model explains:

- ✅ Non-Gaussian error distributions (kurtosis effects)
- ✅ Set-size effects (resource sharing → dimensionality reduction)
- ✅ Attraction bias between simultaneously encoded items
- ❌ Swap errors (discrete bimodal bumps at non-target locations)

The loom's prediction was wrong in its strong form. The weak form
(geometric contamination produces systematic errors) is confirmed, but
the specific shape of those errors is different from what was predicted.

## The Meta-Observation

This is the uncomfortable-stimuli principle in action. The archive
predicted swap bumps. The simulation showed blending. The difference is
informative:

1. **Equal-weight blending is not how the brain does multi-item encoding.**
   Real neural populations have competitive dynamics — gain modulation,
   normalization, winner-take-all — that produce discrete, not blended,
   representations. The simulation was too simple.

2. **The geometric model needs dynamics, not just geometry.** Static
   manifolds + Gaussian noise + ML decoding is necessary but not
   sufficient. You need temporal dynamics (competition, oscillation,
   attractor states) to get the discrete swap phenomenon.

3. **This narrows the claim.** Instead of "the manifold explains
   everything," the honest statement is: "the manifold explains the
   continuous distortions (non-Gaussianity, attraction, set-size
   effects). The discrete phenomena (swaps) may require additional
   mechanisms." This is a WEAKER claim than the session wanted, but
   it's the claim the data supports.

## Next Steps (If Anyone Runs Them)

1. **Stochastic weights**: Replace fixed 0.5/0.5 with Beta-distributed
   weights per trial. Does this produce bimodal distributions?

2. **Attractor model**: Add recurrent dynamics so the decoder snaps to
   discrete states. Does the attractor + manifold model produce swap
   bumps?

3. **Gain normalization**: Implement divisive normalization (standard in
   computational neuroscience). This naturally produces winner-take-all
   dynamics that could generate swaps.

Each of these is testable. Each extends the current simulation by one
mechanism. The question is whether the added mechanism is geometric
(manifold-derived) or cognitive (an additional process on top of geometry).

---

## UPDATE: Stochastic Weights Produce the Bump (Figure 9)

Ran the follow-up immediately. Three Beta-distributed weight regimes:

| Regime | Near target | Near non-target | Shape |
|--------|------------|----------------|-------|
| Beta(2,2) moderate | 26.4% | 5.0% | Unimodal blend |
| Beta(1,1) uniform | 32.0% | 9.5% | Wide, flattened |
| Beta(0.5,0.5) WTA | 39.1% | 20.1% | **Bimodal — swap bump** |

**Winner-take-all resource allocation produces swap-like bumps.**

The mechanism: Beta(0.5,0.5) is U-shaped — weights cluster near 0 or 1.
On trials where w ≈ 1, item 1 dominates → decode near item 1.
On trials where w ≈ 0, item 2 dominates → decode near item 2.
Over trials → bimodal distribution → swap errors.

### What This Means

The geometric model CAN produce swap errors — but only with stochastic
dynamics added. The two-simulation sequence tells a precise story:

1. **Geometry alone** (fixed weights) → blending, not swapping
2. **Geometry + stochastic allocation** (Beta(0.5,0.5)) → swap bumps

The discriminating question is now: **Is winner-take-all allocation
itself geometric?** Divisive normalization (a well-established neural
computation) naturally produces winner-take-all dynamics. If the
resource competition arises from neural gain mechanisms, then swap
errors are STILL geometric — they just require the full geometry of
neural dynamics, not just the static encoding manifold.

If the competition requires a separate "binding" or "slot assignment"
process, then the mixture model was partially right — there IS a
discrete process, but it operates on geometric representations, not
abstract "slots."

### The Refined Claim

"The manifold bends the noise" remains true. But the bending that
produces swap errors requires:
- A curved encoding manifold (static geometry) AND
- Stochastic resource competition (dynamic geometry?)

Neither alone is sufficient. The original manifold_errors.py
demonstrated the first. swap_errors_stochastic.py demonstrates that
the second is necessary for the discrete "swap" phenomenon.

---

*Two simulations. One failure. One success. The failure narrowed the
question. The success sharpened it.*

*The manifold averages unless you let it compete.
Then it swaps.*
