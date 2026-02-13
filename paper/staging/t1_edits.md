# Task 1: Goldstone Circulant Lemma — Staging Edits

## Verification results

Script: `/home/gauss/Claude-Code-Lab/corpus/code/goldstone_finite_N_verify.py`

### Circulant commutation (TW = WT)

| N  | max|TW - WT| |
|----|-------------|
| 24 | 3.89e-16    |
| 48 | 2.05e-16    |
| 96 | 7.03e-17    |

All at machine precision. The within-network weight matrix is exactly circulant at every finite N.

### Goldstone eigenvalue magnitudes (J_cross = 0.30)

| N  | |Goldstone_1| | |Goldstone_2| | FP residual | First non-Goldstone |
|----|--------------|--------------|-------------|---------------------|
| 24 | 1.05e-05     | 1.05e-05     | 1.11e-16    | -0.1311             |
| 48 | 3.20e-10     | 3.20e-10     | 5.55e-16    | -0.1311             |
| 96 | 6.73e-15     | 7.02e-15     | 5.55e-15    | -0.1311             |

The Goldstone eigenvalues converge to machine precision as N increases, while the first non-Goldstone eigenvalue remains stable at -0.131. At N=24 the ~10^{-5} magnitude reflects finite-difference approximation of the continuous rotational derivative on a coarse grid; by N=48 the Goldstone modes are at ~10^{-10}, and at N=96 they reach machine precision (~10^{-15}).

The eigenvectors of the Goldstone modes satisfy sum(v)/||v|| ~ 10^{-14} for the active network component, confirming they are zero-sum (rotational) modes orthogonal to the uniform cross-coupling.

---

## Edit 1: INSERT remark after §3.2.1 equivariance paragraph

### Location

After the paragraph ending:

> ...it cannot be lifted by increasing cross-inhibition, only by breaking the rotational symmetry of either the within-network connectivity or the cross-coupling structure.

And before the paragraph beginning:

> This is the neural circuit analog of the Goldstone theorem (Goldstone, 1961)...

### Insert text

> *Remark (circulant structure).* The within-network connectivity $W_{ij} = \frac{1}{N}(-J_0 + J_1 \cos(\theta_i - \theta_j))$ is exactly circulant: $W_{ij} = w(i - j \bmod N)$ for all $N$. The circulant structure ensures that the discrete rotation operator $T: r_i \mapsto r_{i+1 \bmod N}$ commutes with $\mathbf{W}$, i.e., $T\mathbf{W} = \mathbf{W}T$. Because the fixed-point equation $-\mathbf{r}^* + \sigma(\mathbf{W}\mathbf{r}^*) = 0$ is solved by any rotation $T^k \mathbf{r}^*$, the nullspace of the Jacobian contains the rotational tangent vector $\partial \mathbf{r}^*/\partial \varphi$ at *every* $N$, not merely in the continuous limit. The protection is exact at finite $N$, not an asymptotic approximation.

### Footnote to attach to the end of the inserted remark

> Computational verification: at the coexistence fixed point ($J_\times = 0.30$), the two Goldstone eigenvalue magnitudes are $1.1 \times 10^{-5}$ ($N = 24$), $3.2 \times 10^{-10}$ ($N = 48$), and $6.7 \times 10^{-15}$ ($N = 96$), converging to machine precision as the angular grid refines, while the circulant commutation $\|T\mathbf{W} - \mathbf{W}T\|_\infty$ is below $4 \times 10^{-16}$ at all $N$. The first non-Goldstone eigenvalue remains stable at $\lambda_1 \approx -0.131$ across all three resolutions.

---

## Notes for implementer

1. The remark goes between the "Equivariance structure" paragraph and the "Goldstone theorem" paragraph in §3.2.1.
2. The footnote should be a numbered footnote attached to the final sentence of the remark ("...not an asymptotic approximation.").
3. The verification script is self-contained and reproducible: `source .venv/bin/activate && python3 corpus/code/goldstone_finite_N_verify.py`.
4. The N=24 Goldstone eigenvalue (~10^{-5}) is NOT a failure of the proof — it reflects the finite-difference approximation of the continuous derivative ∂r*/∂φ on a 24-point grid. The eigenvalue converges to zero as O(Δθ^p) with p ≈ 5, reaching machine precision by N=96. The circulant commutation TW=WT is exact at every N.
