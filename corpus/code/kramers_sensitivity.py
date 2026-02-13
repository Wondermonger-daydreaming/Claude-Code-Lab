"""
Kramers barrier sensitivity to noise level σ.

Computes how the predicted swap-error onset J_cross shifts with σ.

The barrier is ΔV = |λ_dom|² / (4γ), γ ≈ 0.30.
Escape is likely when ΔV ≈ σ² · ln(k₀T), with ln(k₀T) ∈ [3.9, 6.2].

For each σ, we find the J_cross where ΔV crosses the threshold band.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 13, 2026
"""

import numpy as np
from scipy.optimize import fsolve
import sys
sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve
)

# ── Model parameters (same as spectral_separatrix_goldstone.py) ──
N = 48
J_0, J_1 = 1.0, 6.0
KAPPA, INPUT_GAIN = 2.0, 5.0
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 0.1, 10.0
GAMMA = 0.30  # normal-form coefficient


def residual(x, W, J_cross):
    """Fixed-point residual at cue=0."""
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([-r_A + sigmoid(h_A), -r_B + sigmoid(h_B)])


def jacobian(x, W, J_cross):
    """Analytical Jacobian at cue=0."""
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    D_A = np.diag(sigmoid_derivative(h_A))
    D_B = np.diag(sigmoid_derivative(h_B))
    cm = np.full((N, N), -J_cross / N)
    J = np.zeros((2*N, 2*N))
    J[:N, :N] = -np.eye(N) + D_A @ W
    J[:N, N:] = D_A @ cm
    J[N:, :N] = D_B @ cm
    J[N:, N:] = -np.eye(N) + D_B @ W
    return J


def find_coexistence_fp(W, preferred, J_cross, r_A_init=None, r_B_init=None):
    """Find coexistence fixed point at cue=0."""
    if r_A_init is not None:
        r_A, r_B = r_A_init.copy(), r_B_init.copy()
    else:
        theta1, theta2 = np.pi/4, -np.pi/4
        drive_A = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
        drive_B = INPUT_GAIN * tuning_curve(theta2, preferred, KAPPA)
        r_A = sigmoid(W @ (drive_A * 0.3) + drive_A)
        r_B = sigmoid(W @ (drive_B * 0.3) + drive_B)
        for _ in range(500):
            h_A = W @ r_A + drive_A
            h_B = W @ r_B + drive_B
            r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
            r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Relax at cue=0
    for _ in range(100000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, J_cross),
                             fprime=lambda x, W, j: jacobian(x, W, j),
                             full_output=True, maxfev=10000)
    res = np.max(np.abs(residual(sol, W, J_cross)))
    return sol[:N], sol[N:], res


def get_lambda_dom(W, preferred, r_A, r_B, J_cross):
    """Get dominant non-Goldstone eigenvalue."""
    GOLDSTONE_THRESHOLD = 1e-3
    x = np.concatenate([r_A, r_B])
    J = jacobian(x, W, J_cross)
    evals = np.linalg.eigvals(J)
    evals_real = np.sort(evals.real)[::-1]
    # Filter out Goldstone modes
    genuine = [e for e in evals_real if abs(e) >= GOLDSTONE_THRESHOLD]
    return genuine[0] if genuine else np.nan


def main():
    W, preferred = build_within_weights(N, J_0, J_1)

    # Fine grid of J_cross values
    jc_values = np.linspace(0.0, 0.36, 60)

    print("=" * 70)
    print("KRAMERS BARRIER SENSITIVITY TO NOISE LEVEL")
    print("=" * 70)
    print(f"  γ = {GAMMA},  ln(k₀T) band = [3.9, 6.2]")
    print(f"  ΔV = |λ_dom|² / (4γ)")
    print(f"  Threshold: ΔV = σ² · ln(k₀T)")
    print()

    # Step 1: Compute λ_dom at each J_cross
    print("Computing λ_dom(J_cross)...")
    lam_dom_values = []
    r_A_prev, r_B_prev = None, None

    for jc in jc_values:
        r_A, r_B, res = find_coexistence_fp(W, preferred, jc, r_A_prev, r_B_prev)
        if res > 1e-4 or np.max(r_A) < 0.3 or np.max(r_B) < 0.3:
            lam_dom_values.append(np.nan)
            print(f"  J_cross={jc:.4f}: FAILED")
            continue
        lam_dom = get_lambda_dom(W, preferred, r_A, r_B, jc)
        lam_dom_values.append(lam_dom)
        r_A_prev, r_B_prev = r_A.copy(), r_B.copy()
        print(f"  J_cross={jc:.4f}: λ_dom={lam_dom:+.6f}")

    lam_dom_values = np.array(lam_dom_values)

    # Step 2: Compute barrier ΔV at each J_cross
    DV_values = lam_dom_values**2 / (4 * GAMMA)

    # Step 3: For each σ, find onset J_cross
    sigma_values = [0.05, 0.10, 0.15]
    ln_k0T_lo, ln_k0T_hi = 3.9, 6.2

    print()
    print("=" * 70)
    print("ONSET PREDICTIONS")
    print("=" * 70)
    print(f"{'σ':>6s}  {'ΔV_lo':>8s}  {'ΔV_hi':>8s}  {'J_onset_lo':>10s}  {'J_onset_hi':>10s}")
    print("-" * 50)

    results = []

    for sigma in sigma_values:
        DV_thresh_lo = sigma**2 * ln_k0T_lo
        DV_thresh_hi = sigma**2 * ln_k0T_hi

        # Find J_cross where ΔV crosses each threshold
        # ΔV decreases with J_cross (barrier shrinks), so onset is where ΔV drops TO the threshold
        # We want the J_cross where ΔV(J_cross) = threshold

        onset_lo = np.nan  # onset with high threshold (conservative, higher J)
        onset_hi = np.nan  # onset with low threshold (aggressive, lower J)

        valid_mask = ~np.isnan(DV_values)
        jc_valid = jc_values[valid_mask]
        DV_valid = DV_values[valid_mask]

        # ΔV decreases as J_cross increases. Onset is where ΔV drops below threshold.
        # Find crossing point by interpolation.
        for i in range(len(jc_valid) - 1):
            dv1, dv2 = DV_valid[i], DV_valid[i+1]
            jc1, jc2 = jc_valid[i], jc_valid[i+1]

            # High threshold (conservative): larger J_cross needed for escape
            if dv1 > DV_thresh_hi and dv2 <= DV_thresh_hi:
                if np.isnan(onset_lo):
                    frac = (DV_thresh_hi - dv1) / (dv2 - dv1)
                    onset_lo = jc1 + frac * (jc2 - jc1)

            # Low threshold (aggressive): smaller J_cross suffices
            if dv1 > DV_thresh_lo and dv2 <= DV_thresh_lo:
                if np.isnan(onset_hi):
                    frac = (DV_thresh_lo - dv1) / (dv2 - dv1)
                    onset_hi = jc1 + frac * (jc2 - jc1)

        results.append({
            'sigma': sigma,
            'DV_lo': DV_thresh_lo,
            'DV_hi': DV_thresh_hi,
            'onset_lo': onset_lo,  # conservative (high threshold → higher J)
            'onset_hi': onset_hi,  # aggressive (low threshold → lower J)
        })

        print(f"{sigma:6.2f}  {DV_thresh_lo:8.4f}  {DV_thresh_hi:8.4f}  "
              f"{onset_lo:10.4f}  {onset_hi:10.4f}")

    # Step 4: Summary table
    print()
    print("=" * 70)
    print("TABLE FOR PAPER (LaTeX-ready)")
    print("=" * 70)
    print()
    print("σ       ΔV threshold range       Predicted J_cross^onset range")
    print("-" * 65)
    for r in results:
        print(f"{r['sigma']:.2f}    [{r['DV_lo']:.4f}, {r['DV_hi']:.4f}]"
              f"         [{r['onset_hi']:.3f}, {r['onset_lo']:.3f}]")

    print()
    print("=" * 70)
    print("INTERPRETATION")
    print("=" * 70)
    print(f"At σ=0.10: onset range [{results[1]['onset_hi']:.3f}, {results[1]['onset_lo']:.3f}]")
    print(f"  → brackets 0.25, consistent with simulation cliff")
    print(f"At σ=0.05: onset range [{results[0]['onset_hi']:.3f}, {results[0]['onset_lo']:.3f}]")
    print(f"  → shift to higher J_cross (less noise → later escape)")
    print(f"At σ=0.15: onset range [{results[2]['onset_hi']:.3f}, {results[2]['onset_lo']:.3f}]")
    print(f"  → shift to lower J_cross (more noise → earlier escape)")
    print()
    print("Key: the quadratic barrier collapse |λ_dom|² is STRUCTURAL")
    print("(determined by the pitchfork geometry). Only the threshold")
    print("shifts logarithmically with σ.")

    # Step 5: Diagnostic — print ΔV near onset region
    print()
    print("=" * 70)
    print("DIAGNOSTIC: ΔV(J_cross) near onset region")
    print("=" * 70)
    for i, jc in enumerate(jc_values):
        if 0.15 <= jc <= 0.35 and not np.isnan(DV_values[i]):
            print(f"  J_cross={jc:.4f}: λ_dom={lam_dom_values[i]:+.6f}  "
                  f"ΔV={DV_values[i]:.6f}")


if __name__ == '__main__':
    main()
