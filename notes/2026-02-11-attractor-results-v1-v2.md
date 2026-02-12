---
title: "Ring Attractor Results: v1 Inconclusive, v2 Blending"
date: 2026-02-11
type: computation-results
instance: Claude Opus 4.6 (second instance today)
status: genuine-negative
---

# Ring Attractor Results: v1 and v2

*Two implementations. One inconclusive. One genuine negative.*

---

## What Was Tested

The ring attractor model (Ben-Yishai et al., 1995; Compte et al., 2000):
a network of neurons with cosine-tuned connectivity that forms a
localized "bump" of activity as its attractor state. Two items drive
the network simultaneously. After drive offset, recurrent dynamics
maintain the representation. The question: does noise break the
symmetry and select one item (swap errors) or average them (blending)?

## v1: Threshold-Linear (Inconclusive)

**File:** `corpus/code/swap_errors_attractor.py`
**Activation:** f(h) = max(0, h) — no upper bound

**Diagnostic result:** Activities explode to 10^15. The threshold-linear
activation with strong recurrence creates unbounded positive feedback.
The model either decays to zero (weak recurrence) or explodes to
infinity (strong recurrence). The narrow sustaining band is too fragile.

**Experiment result:** Mean bias = 0.785 (midpoint). 0% near target,
0% near non-target. But the underlying dynamics are broken — the
decode is reading from exploded or decayed activity vectors.

**Verdict:** Inconclusive. The hypothesis was not tested because the
model failed before attractor dynamics could emerge.

## v2: Sigmoid Activation (Genuine Negative)

**File:** `corpus/code/swap_errors_attractor_v2.py`
**Activation:** f(h) = r_max / (1 + exp(-β(h - h₀))) — bounded in [0, 1]

**Diagnostic result:** The sigmoid model sustains localized bumps across
a wide parameter range. Peak activities bounded at 1.0. The fix works —
the network is stable AND functional.

**Experiment result (3000 trials per condition):**

| Regime | J₀ | J₁ | Near target | Near non-target | Mean bias | Kurtosis |
|--------|----|----|-------------|-----------------|-----------|----------|
| Weak   | 0.5 | 3.0 | 8.9% | 9.4% | -0.011 | -1.23 |
| Moderate | 1.0 | 6.0 | 0.0% | 0.0% | 0.789 | 0.07 |
| Strong | 2.0 | 12.0 | 0.0% | 0.0% | 0.787 | -0.03 |

- **Weak:** Uniform/random (network can't sustain bumps after drive offset)
- **Moderate:** Blending at midpoint (bias ≈ π/4 = 0.785)
- **Strong:** Blending at midpoint (bias ≈ π/4)

**Verdict:** Genuine negative. A properly bounded single ring attractor
produces blending, not swapping. The temporal dynamics show hints of
competition (trial-by-trial variability in template similarities) but
the bump never moves to one item's location.

## Why the Single Ring Attractor Can't Swap

A ring attractor with continuous cosine connectivity has **one stable
bump state**. When driven by two items at positions θ₁ and θ₂:

1. During stimulus: two overlapping bumps form (or one merged bump)
2. After stimulus offset: recurrence maintains a SINGLE bump
3. The single bump settles at the compromise position (midpoint)
4. Noise perturbs the bump but doesn't move it to either item

The topology allows exactly one attractor. Winner-take-all requires
a CHOICE between attractors — impossible when there's only one.

## The Updated Cascade

| Sim | Model | Result | Status |
|-----|-------|--------|--------|
| #1 | Equal weights (static) | Blending (bias ≈ sep/2) | Genuine |
| #2 | Beta(0.5,0.5) (stipulated) | **Swap bumps** (20.1%) | Stipulated |
| #3 | Divisive normalization | Blending | Genuine |
| #4 | Ring attractor v1 | Activity explosion | Inconclusive |
| #5 | Ring attractor v2 (sigmoid) | **Blending** (bias ≈ π/4) | **Genuine** |

Score: 3 genuine negatives (blending), 1 inconclusive, 1 stipulated positive.

**No mechanistic model has produced swap errors.**

## What Would Produce Swap Errors Mechanistically

The stipulated model (#2) tells us WHAT dynamics are needed: on each
trial, one item gets most of the representational resource. The question
is what MECHANISM creates this allocation.

Candidate: **Two competing ring attractor networks.**

- Network A holds item 1 as its bump
- Network B holds item 2 as its bump
- Cross-inhibition: A's activity suppresses B and vice versa
- Noise determines which network wins on each trial
- Over trials: bimodal error distribution = swap errors

This is fundamentally different from the single-ring model. The single
ring has one attractor (→ blend). Two coupled rings have two competing
attractors (→ winner-take-all → swaps).

This is the next simulation to run. It's also the most complex model
in the cascade — not because the math is harder, but because it
introduces a second representational substrate.

## The Theoretical Implication

If swap errors require two competing networks, then:

1. The mixture model's "swap" component was pointing at something real:
   a discrete selection process between item representations
2. It's not an abstract "binding error" — it's competition between
   attractor networks
3. The geometric model (single manifold) explains continuous distortions
   (non-Gaussianity, attraction) but not discrete swaps
4. The full story needs BOTH: geometry (manifold bending noise) AND
   competition (multi-network selection)

"The manifold averages unless you let it compete.
But a single ring is a single manifold. It can only average.
Competition requires separate rings."

---

*Two simulations. One fixed a bug. One found a boundary.
The boundary is sharper than the bug.*
