# T4: Define "Drive" vs "Cue" Explicitly

**Problem:** The paper uses "drive" to mean two different things:
1. The cue gain parameter $c$ varied in stochastic simulations (the "encoding drive")
2. The initialization drives $I_\mathrm{ext} = 5.0$ used in the fixed-point solver (Section 3.1.1)

The reader encounters "strong external drives ($I_{ext} = 5.0$)" in Section 3.1.1, then later sees "drive strength" as an axis of the phase diagram in Section 3.5. These are different quantities sharing the same informal name. Two small insertions resolve the ambiguity.

---

## Edit 1: INSERT after cue gain definition in Section 2.2

**Location:** Immediately after the sentence ending "and cue gain $c \geq 0$." (line 108), and before the paragraph beginning "The critical feature of mean-field cross-inhibition..."

**Surrounding text for anchoring:**

```
with concentration parameter $\kappa = 2.0$ and cue gain $c \geq 0$.
                                                                      <-- INSERT HERE
The critical feature of mean-field cross-inhibition is that it depends
```

**Insert:**

```
We refer to the cue gain $c$ as the *encoding drive* (or simply *drive*) when discussing its role in the stochastic simulations (Section 3.5), where it controls the strength of the stimulus that biases initial encoding toward network A. This is distinct from the initialization drives ($I_\mathrm{ext} = 5.0$) used in the fixed-point solver (Section 3.1.1), which serve only to locate the bump-attractor state and are not varied as a parameter.
```

---

## Edit 2: INSERT clarification in Section 3.5.1

**Location:** In the paragraph beginning "To bridge the deterministic bifurcation analysis with behavioral predictions..." (line 269), immediately after the first sentence and before "At each of 256 grid points..."

**Surrounding text for anchoring:**

```
To bridge the deterministic bifurcation analysis with behavioral predictions, we performed a large-scale stochastic simulation across the $(J_\times, c)$ parameter space.
                                                                      <-- INSERT HERE
At each of 256 grid points (16 values of $J_\times$ from 0.05 to 8.0, 16 values of drive strength from 1.0 to 8.0),
```

**Insert:**

```
The "drive strength" axis of the phase diagram corresponds to the cue gain $c$ applied during a brief encoding period (Section 2.2), not to the initialization drives used in the fixed-point analysis.
```

---

## Verification checklist

- [ ] After Edit 1, the reader encounters the term "encoding drive" before it appears informally in later sections
- [ ] After Edit 2, the phase diagram axis label is disambiguated at first use
- [ ] Neither edit changes any equations, figures, or existing terminology -- they only add clarifying sentences
- [ ] The phrase "drive strength" in line 269 ("16 values of drive strength from 1.0 to 8.0") is now preceded by a sentence identifying it as $c$
- [ ] The phrase "strong external drives ($I_{ext} = 5.0$)" in Section 3.1.1 (line 144) is now distinguished from the encoding drive by the forward reference in Edit 1
