"""
==========================================================================
THE SPECTRAL SEPARATRIX — AT THE CORRECT PARAMETERS
==========================================================================

The diagnostic revealed: coexistence only exists for J_cross < 0.36.
At J_cross = 0.5, both bumps collapse — no coexistence FP exists.

Now we work at J_cross = 0.35 (just below critical), where:
  - Both bumps self-sustain (coexistence IS a fixed point)
  - The cue breaks the symmetry
  - The coexistence FP should become unstable → the separatrix

This is Program III of the spectral proposal, done right.

Key computations:
  1. Find coexistence FP at cue=0 via simulation + Newton
  2. Track coexistence branch via Newton continuation in cue_gain
  3. Track WTA branch for comparison
  4. Compute eigenvalues, eigenvectors, and projections
  5. Identify the bifurcation point
  6. Run GLM 5's falsification tests

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve
from scipy.special import i0
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve,
    compute_full_jacobian, COLORS
)

plt.rcParams.update({
    'figure.facecolor': '#faf8f5',
    'axes.facecolor': '#faf8f5',
    'font.family': 'serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#444444',
    'text.color': '#2a2a2a',
    'axes.labelcolor': '#2a2a2a',
    'xtick.color': '#555555',
    'ytick.color': '#555555',
})

# ═══════════════════════════════════════════════════════════════════
# PARAMETERS: THE CORRECT REGIME
# ═══════════════════════════════════════════════════════════════════

J_CROSS = 0.35  # Just below critical (0.36)
N = 48
J_0, J_1 = 1.0, 6.0
KAPPA, INPUT_GAIN = 2.0, 5.0
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 0.1, 10.0


# ═══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def residual(x, W, cue_A, J_cross=J_CROSS):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([-r_A + sigmoid(h_A), -r_B + sigmoid(h_B)])


def jacobian_rootfinding(x, W, cue_A, J_cross=J_CROSS):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
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


def find_coexistence_at_cue0(W, preferred):
    """Find the coexistence FP at cue=0 by simulation + Newton."""
    theta1, theta2 = np.pi/4, -np.pi/4
    drive_A = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
    drive_B = INPUT_GAIN * tuning_curve(theta2, preferred, KAPPA)

    # Establish bumps with drives
    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B)
    for _ in range(1000):
        h_A = W @ r_A + drive_A - J_CROSS * np.mean(r_B)
        h_B = W @ r_B + drive_B - J_CROSS * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Remove drives, converge
    for _ in range(50000):
        h_A = W @ r_A - J_CROSS * np.mean(r_B)
        h_B = W @ r_B - J_CROSS * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Polish with Newton
    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_0),
                             fprime=jacobian_rootfinding,
                             full_output=True, maxfev=10000)
    res = np.max(np.abs(residual(sol, W, cue_0)))
    return sol[:N], sol[N:], res


def find_wta_at_cue(cue_gain, W, preferred):
    """Find WTA (A-dominant) FP by simulation with cue."""
    theta1, theta2 = np.pi/4, -np.pi/4
    drive_A = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
    drive_B = INPUT_GAIN * tuning_curve(theta2, preferred, KAPPA)
    cue_A = cue_gain * tuning_curve(theta1, preferred, KAPPA)

    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B)
    for _ in range(500):
        h_A = W @ r_A + drive_A - J_CROSS * np.mean(r_B)
        h_B = W @ r_B + drive_B - J_CROSS * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Cue phase
    for _ in range(50000):
        h_A = W @ r_A + cue_A - J_CROSS * np.mean(r_B)
        h_B = W @ r_B - J_CROSS * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    return r_A, r_B


def analyze_fp(r_A, r_B, W, preferred, cue_gain, J_cross=J_CROSS):
    """Full eigenvalue/eigenvector analysis at a fixed point."""
    theta1 = np.pi/4
    cue_A = cue_gain * tuning_curve(theta1, preferred, KAPPA)

    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)

    J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
    evals, evecs = np.linalg.eig(J)
    idx = np.argsort(-evals.real)
    evals, evecs = evals[idx], evecs[:, idx]

    v1 = evecs[:, 0].real
    v1n = v1 / (np.linalg.norm(v1) + 1e-30)

    # Projection directions
    cos_p = np.cos(preferred - np.pi/4)
    d_cos = np.concatenate([cos_p, -cos_p])
    d_cos /= np.linalg.norm(d_cos)

    sin_p = np.sin(preferred - np.pi/4)
    d_sin = np.concatenate([sin_p, -sin_p])
    d_sin /= np.linalg.norm(d_sin)

    d_uni = np.concatenate([np.ones(N), -np.ones(N)])
    d_uni /= np.linalg.norm(d_uni)

    return {
        'cue_gain': cue_gain,
        'r_A': r_A.copy(), 'r_B': r_B.copy(),
        'h_A': h_A, 'h_B': h_B,
        'eigenvalues': evals, 'eigenvectors': evecs,
        'lambda_1': evals[0].real, 'lambda_2': evals[1].real,
        'lambda_3': evals[2].real,
        'D': np.mean(r_A) - np.mean(r_B),
        'n_positive': np.sum(evals.real > 0),
        'max_rA': np.max(r_A), 'max_rB': np.max(r_B),
        'proj_cos': abs(np.dot(v1n, d_cos)),
        'proj_sin': abs(np.dot(v1n, d_sin)),
        'proj_uni': abs(np.dot(v1n, d_uni)),
    }


# ═══════════════════════════════════════════════════════════════════
# MAIN COMPUTATION
# ═══════════════════════════════════════════════════════════════════

def run_full_analysis():
    W, preferred = build_within_weights(N, J_0, J_1)

    # ── Find coexistence at cue=0 ──
    print("=" * 70)
    print(f"SPECTRAL SEPARATRIX at J_cross = {J_CROSS}")
    print("=" * 70)

    print("\n[1/3] Finding coexistence FP at cue=0...")
    r_A_coex, r_B_coex, res0 = find_coexistence_at_cue0(W, preferred)
    print(f"  Residual: {res0:.2e}")
    print(f"  max(r_A)={np.max(r_A_coex):.4f}, max(r_B)={np.max(r_B_coex):.4f}")
    print(f"  D = {np.mean(r_A_coex)-np.mean(r_B_coex):.6f}")

    has_coex = np.max(r_A_coex) > 0.3 and np.max(r_B_coex) > 0.3
    print(f"  Coexistence confirmed: {has_coex}")

    if not has_coex:
        print("  ERROR: No coexistence at cue=0. Aborting.")
        return

    # ── Newton continuation of coexistence branch ──
    print("\n[2/3] Newton continuation of coexistence branch...")
    cue_gains = np.concatenate([
        np.linspace(0.0, 0.005, 8),
        np.linspace(0.005, 0.05, 25),
        np.linspace(0.05, 0.2, 15),
        np.linspace(0.2, 0.5, 8),
    ])

    coex_results = []
    r_A_prev, r_B_prev = r_A_coex.copy(), r_B_coex.copy()

    for cg in cue_gains:
        cue_A = cg * tuning_curve(np.pi/4, preferred, KAPPA)
        x0 = np.concatenate([r_A_prev, r_B_prev])

        sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_A),
                                 fprime=jacobian_rootfinding,
                                 full_output=True, maxfev=10000)
        res = np.max(np.abs(residual(sol, W, cue_A)))

        if res > 1e-6:
            print(f"  cue={cg:.4f}: FAILED (res={res:.2e})")
            coex_results.append(None)
            continue

        r_A, r_B = sol[:N], sol[N:]
        result = analyze_fp(r_A, r_B, W, preferred, cg)
        coex_results.append(result)

        r_A_prev, r_B_prev = r_A, r_B

        print(f"  cue={cg:.4f}: D={result['D']:+.6f}, "
              f"λ₁={result['lambda_1']:+.6f}, n_pos={result['n_positive']}, "
              f"max(rA)={result['max_rA']:.3f}, max(rB)={result['max_rB']:.3f}, "
              f"|cos|={result['proj_cos']:.3f}")

    # ── WTA branch for comparison ──
    print("\n[3/3] Computing WTA branch...")
    wta_results = []
    for cg in cue_gains:
        if cg == 0:
            # At cue=0 with J_cross=0.35, forward sim might give coexistence
            # Use asymmetric initial condition to get WTA
            r_A_w, r_B_w = find_wta_at_cue(max(cg, 0.001), W, preferred)
        else:
            r_A_w, r_B_w = find_wta_at_cue(cg, W, preferred)

        # Polish with Newton
        cue_A = cg * tuning_curve(np.pi/4, preferred, KAPPA)
        x0 = np.concatenate([r_A_w, r_B_w])
        sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_A),
                                 fprime=jacobian_rootfinding,
                                 full_output=True, maxfev=10000)
        res = np.max(np.abs(residual(sol, W, cue_A)))
        if res < 1e-6:
            r_A_w, r_B_w = sol[:N], sol[N:]

        result = analyze_fp(r_A_w, r_B_w, W, preferred, cg)
        wta_results.append(result)

    return coex_results, wta_results, W, preferred


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_spectral_separatrix(coex_results, wta_results, save_path):
    """The definitive spectral separatrix figure."""
    coex_valid = [r for r in coex_results if r is not None]
    cg_c = [r['cue_gain'] for r in coex_valid]
    cg_w = [r['cue_gain'] for r in wta_results]

    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── Row 1: The Bifurcation ──
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(cg_c, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁ (coexistence)')
    ax.plot(cg_w, [r['lambda_1'] for r in wta_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='λ₁ (WTA)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title(f'Dominant Eigenvalue (J_cross={J_CROSS})', fontweight='bold')
    ax.legend(fontsize=8)

    ax = fig.add_subplot(gs[0, 1])
    ax.plot(cg_c, [r['D'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3, label='Coexistence')
    ax.plot(cg_w, [r['D'] for r in wta_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3, label='WTA')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance', fontweight='bold')
    ax.legend(fontsize=8)

    ax = fig.add_subplot(gs[0, 2])
    ax.plot(cg_c, [r['n_positive'] for r in coex_valid],
            'o-', color=COLORS['dominance'], linewidth=2, markersize=4)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('# positive eigenvalues')
    ax.set_title('Instability Index (Coexistence)', fontweight='bold')

    # ── Row 2: Top eigenvalues + projections ──
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(cg_c, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], lw=2, ms=3, label='λ₁')
    ax.plot(cg_c, [r['lambda_2'] for r in coex_valid],
            's-', color=COLORS['dominance'], lw=1.5, ms=2, label='λ₂')
    ax.plot(cg_c, [r['lambda_3'] for r in coex_valid],
            '^-', color=COLORS['network_A'], lw=1, ms=2, label='λ₃')
    ax.axhline(y=0, color='gray', ls='--', alpha=0.4)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 3 Eigenvalues (Coexistence)', fontweight='bold')
    ax.legend(fontsize=8)

    ax = fig.add_subplot(gs[1, 1])
    ax.plot(cg_c, [r['proj_cos'] for r in coex_valid],
            'o-', color=COLORS['critical'], lw=2, ms=4, label='|⟨v₁, d_cos⟩|')
    ax.plot(cg_c, [r['proj_sin'] for r in coex_valid],
            '^-', color=COLORS['dominance'], lw=1.5, ms=3, label='|⟨v₁, d_sin⟩|')
    ax.plot(cg_c, [r['proj_uni'] for r in coex_valid],
            's--', color=COLORS['bulk'], lw=1, ms=3, label='|⟨v₁, d_uni⟩|')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('|Projection|')
    ax.set_ylim(-0.05, 1.05)
    ax.set_title('Eigenvector Projections', fontweight='bold')
    ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[1, 2])
    ax.plot(cg_c, [r['max_rA'] for r in coex_valid],
            'o-', color=COLORS['network_A'], lw=2, ms=3, label='max(r_A)')
    ax.plot(cg_c, [r['max_rB'] for r in coex_valid],
            'o-', color=COLORS['network_B'], lw=2, ms=3, label='max(r_B)')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Peak firing rate')
    ax.set_title('Bump Heights (Coexistence)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── Row 3: Activity profiles at key cue values ──
    angles = np.linspace(-180, 180, N, endpoint=False)
    cue_show = [0.0, 0.01, 0.02, 0.05, 0.1, 0.2]
    for col, cg_target in enumerate(cue_show[:3]):
        matches = [r for r in coex_valid if abs(r['cue_gain'] - cg_target) < 0.008]
        if not matches:
            continue
        m = min(matches, key=lambda r: abs(r['cue_gain'] - cg_target))
        ax = fig.add_subplot(gs[2, col])
        ax.plot(angles, m['r_A'], '-', color=COLORS['network_A'], lw=2, label='r_A')
        ax.plot(angles, m['r_B'], '-', color=COLORS['network_B'], lw=2, label='r_B')
        v1 = m['eigenvectors'][:, 0].real
        vs = 0.3 / (np.max(np.abs(v1)) + 1e-30)
        ax.plot(angles, 0.5 + v1[:N]*vs, '--', color=COLORS['network_A'], lw=1, alpha=0.5)
        ax.plot(angles, 0.5 + v1[N:]*vs, '--', color=COLORS['network_B'], lw=1, alpha=0.5)
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel('Preferred angle (°)')
        ax.set_title(f'cue={m["cue_gain"]:.3f}, D={m["D"]:.4f}\n'
                    f'λ₁={m["lambda_1"]:.4f}, n_pos={m["n_positive"]}',
                    fontsize=8, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Activity / eigenvector')
            ax.legend(fontsize=6)

    # ── Row 4: More profiles ──
    for col, cg_target in enumerate(cue_show[3:6]):
        matches = [r for r in coex_valid if abs(r['cue_gain'] - cg_target) < 0.015]
        if not matches:
            continue
        m = min(matches, key=lambda r: abs(r['cue_gain'] - cg_target))
        ax = fig.add_subplot(gs[3, col])
        ax.plot(angles, m['r_A'], '-', color=COLORS['network_A'], lw=2, label='r_A')
        ax.plot(angles, m['r_B'], '-', color=COLORS['network_B'], lw=2, label='r_B')
        v1 = m['eigenvectors'][:, 0].real
        vs = 0.3 / (np.max(np.abs(v1)) + 1e-30)
        ax.plot(angles, 0.5 + v1[:N]*vs, '--', color=COLORS['network_A'], lw=1, alpha=0.5)
        ax.plot(angles, 0.5 + v1[N:]*vs, '--', color=COLORS['network_B'], lw=1, alpha=0.5)
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel('Preferred angle (°)')
        ax.set_title(f'cue={m["cue_gain"]:.3f}, D={m["D"]:.4f}\n'
                    f'λ₁={m["lambda_1"]:.4f}, n_pos={m["n_positive"]}',
                    fontsize=8, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Activity / eigenvector')
            ax.legend(fontsize=6)

    fig.suptitle(f'The Spectral Separatrix at J_cross = {J_CROSS}\n'
                 'Coexistence FP + eigenvalue tracking + critical eigenvector',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    coex, wta, W, pref = run_full_analysis()

    print("\n  Plotting...")
    plot_spectral_separatrix(
        coex, wta,
        os.path.join(outdir, 'fig51_spectral_separatrix_correct.png'))

    # Summary
    coex_valid = [r for r in coex if r is not None]
    print(f"\n{'='*70}")
    print(f"SUMMARY: J_cross = {J_CROSS}")
    print(f"  Coexistence solutions: {len(coex_valid)}/{len(coex)}")
    if coex_valid:
        n_unstable = sum(1 for r in coex_valid if r['n_positive'] > 0)
        has_bumps = sum(1 for r in coex_valid if r['max_rA'] > 0.3 and r['max_rB'] > 0.3)
        print(f"  With both bumps: {has_bumps}")
        print(f"  Unstable: {n_unstable}")
        print(f"  λ₁ range: [{min(r['lambda_1'] for r in coex_valid):.6f}, "
              f"{max(r['lambda_1'] for r in coex_valid):.6f}]")
        print(f"  D range: [{min(r['D'] for r in coex_valid):.6f}, "
              f"{max(r['D'] for r in coex_valid):.6f}]")

        # Check for bifurcation: where does λ₁ cross zero?
        for i in range(len(coex_valid) - 1):
            if coex_valid[i]['lambda_1'] * coex_valid[i+1]['lambda_1'] < 0:
                # Zero crossing
                cg1, cg2 = coex_valid[i]['cue_gain'], coex_valid[i+1]['cue_gain']
                l1, l2 = coex_valid[i]['lambda_1'], coex_valid[i+1]['lambda_1']
                cg_crit = cg1 + (0 - l1) * (cg2 - cg1) / (l2 - l1)
                print(f"  BIFURCATION at cue_gain ≈ {cg_crit:.4f}")
                print(f"    (between {cg1:.4f} [λ₁={l1:.6f}] and {cg2:.4f} [λ₁={l2:.6f}])")
    print(f"{'='*70}")
