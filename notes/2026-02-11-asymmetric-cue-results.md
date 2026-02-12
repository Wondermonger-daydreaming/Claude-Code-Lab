---
title: "Sim #7/#7b: Asymmetric Cue Results"
date: 2026-02-11
type: results
instance: Claude Opus 4.6
simulations: "7, 7b"
status: behavioral-range-found
---

# Asymmetric Cue Results (Sims #7 and #7b)

*Following the coupled rings breakthrough (sim #6), testing whether
attentional cueing can tune swap rates to behavioral levels.*

---

## The Question

Sim #6 produced ~50/50 swap errors (both networks equally likely to win).
Real experiments show ~15-20% swap errors. Can an attentional cue bias
competition to produce realistic rates?

## Sim #7: First Attempt (Sustained Cue, Coarse Sweep)

**Result: CLIFF.** Even cue_gain=0.3 (6% of stimulus drive) gives 100%
target, 0% swaps. The transition from 50/50 to 100/0 is all-or-nothing
at this resolution.

## Sim #7b: Three Probes

### Probe A: Fine-Grained Sustained Cue

| Cue gain | Target % | Swap % | A wins % |
|----------|----------|--------|----------|
| 0.000 | 38.1 | 34.8 | 37.9 |
| **0.020** | **64.3** | **19.7** | **66.6** |
| 0.050 | 91.8 | 3.9 | 93.4 |
| 0.080 | 99.1 | 0.1 | 99.5 |
| 0.100+ | ~100 | ~0 | ~100 |

**Finding:** The behavioral range exists at cue_gain ≈ 0.02. This is
0.4% of the stimulus drive (5.0). The regime is extremely narrow.

### Probe B: Pulse Cue (gain=1.0, varying duration)

| Duration | Target % | Swap % |
|----------|----------|--------|
| 5 steps | 81.0 | 4.8 |
| 10 steps | 93.0 | 0.2 |
| 15+ steps | ~95 | ~0 |

**Finding:** Even a 5-step pulse at gain=1.0 nearly eliminates swaps.
The system is extremely sensitive to any asymmetric input.

### Probe C: Gain × Duration Grid

|          | dur=5 | dur=10 | dur=20 |
|----------|-------|--------|--------|
| gain=0.3 | **22%** | **10%** | 1% |
| gain=0.5 | **14%** | 3% | 0% |
| gain=1.0 | 4% | 0% | 0% |

**Finding:** Four conditions hit the behavioral range (10-25%):
1. Sustained gain=0.02 → 19.7%
2. Pulse gain=0.3, dur=5 → 21.9%
3. Pulse gain=0.3, dur=10 → 10.2%
4. Pulse gain=0.5, dur=5 → 14.0%

**The pattern:** gain × duration ≈ constant for the transition.
Total integrated charge determines the outcome. Weaker gain tolerates
longer duration; stronger gain must be briefer.

## Interpretation

### What this means for the model

The coupled ring attractor model CAN produce behaviorally realistic
swap rates. But the operating regime is very narrow — the attentional
cue must be either:
- Extremely weak but sustained (~0.4% of stimulus drive), or
- Brief and moderate (~5 steps at 6% of stimulus drive)

This narrowness is not necessarily a bug. It's a PREDICTION:

**Biological attention at the level of working memory operates near
a phase transition.** Too little cueing → equal competition → 50% swaps.
Too much cueing → deterministic resolution → 0% swaps. The brain must
be tuned to the narrow intermediate zone.

### Testable predictions

1. **Retro-cue effectiveness should be all-or-nothing in individual
   trials** — the model predicts that cueing either resolves competition
   (correct report) or fails to (swap error), with little in between.

2. **Cue timing matters:** earlier cues (before competition resolves)
   should be more effective than late cues. The model predicts a
   cue-latency curve with a sharp transition.

3. **Cue strength manipulations** (e.g., varying cue validity or
   salience) should produce a steep psychometric function for swap rate,
   not a gradual one.

4. **Under dual-task or divided attention**, the effective cue gain
   should decrease, pushing the system back toward 50/50 → increased
   swap errors. This is consistent with known load effects.

### Honest limitations

1. The narrow regime means the model is fragile — small parameter
   changes could eliminate the behavioral match. This needs sensitivity
   analysis across all model parameters, not just cue gain.

2. The gain × duration tradeoff suggests the relevant variable is
   total integrated charge, which is a single scalar. A more realistic
   model might have nonlinear interactions between cue timing and the
   state of the competition at cue onset.

3. We haven't tested set-size scaling (3+ items) or separation effects.
   The model might not generalize gracefully.

---

## Updated Cascade Summary

| Sim | Model | Result | Status |
|-----|-------|--------|--------|
| #1 | Equal weights | Blending | Negative |
| #2 | Beta(0.5,0.5) | Swap bumps (stipulated) | Positive but stipulated |
| #3 | Div. normalization | Blending | Negative |
| #4 | Ring attractor v1 | Inconclusive | Failed |
| #5 | Ring attractor v2 | Blending | Negative |
| #6 | Coupled rings | **Swap bumps** | Breakthrough |
| #7 | Coupled rings + sustained cue | Cliff (all-or-nothing) | Informative negative |
| #7b | Coupled rings + fine cue | **Behavioral range found** | Success (narrow) |

---

*The manifold averages. The coupled rings compete. Attention resolves
the competition — but barely. The brain lives on the edge.*

*Trust the run.*
