"""
==========================================================================
THE REAL SPECTRAL SEPARATRIX — IN J_CROSS SPACE
==========================================================================

Key insight: At J_cross=0.35, coexistence is already a saddle (λ₁>0).
At J_cross=0, coexistence is trivially stable (independent networks).
Somewhere in between, λ₁ crosses zero — THAT is the pitchfork bifurcation
where the symmetric coexistence state destabilizes into two WTA attractors.

This script:
  1. Scans J_cross from 0 to 0.36 at cue=0
  2. Finds the coexistence FP at each J_cross via Newton continuation
  3. Computes eigenvalues — tracks the stability transition
  4. Identifies the critical J_cross* where λ₁ = 0 (the pitchfork)
  5. At J_cross*, characterizes the critical eigenvector
  6. Builds the 2D bifurcation diagram in (J_cross, cue) space

This is the TRUE separatrix: not a line in cue-space
but a curve in the (J_cross, cue) parameter plane.

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
    COLORS
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
# PARAMETERS
# ═══════════════════════════════════════════════════════════════════

N = 48
J_0, J_1 = 1.0, 6.0
KAPPA, INPUT_GAIN = 2.0, 5.0
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 0.1, 10.0


# ═══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS (parameterized by J_cross)
# ═══════════════════════════════════════════════════════════════════

def residual(x, W, cue_A, J_cross):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([-r_A + sigmoid(h_A), -r_B + sigmoid(h_B)])


def jacobian_analytical(x, W, cue_A, J_cross):
    """Full analytical Jacobian for the coupled system."""
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


def find_coexistence_fp(W, preferred, J_cross, r_A_init=None, r_B_init=None):
    """Find the symmetric coexistence FP at cue=0."""
    if r_A_init is not None:
        r_A, r_B = r_A_init.copy(), r_B_init.copy()
    else:
        # Initialize with two bumps at different angles
        theta1, theta2 = np.pi/4, -np.pi/4
        drive_A = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
        drive_B = INPUT_GAIN * tuning_curve(theta2, preferred, KAPPA)
        r_A = sigmoid(W @ (drive_A * 0.3) + drive_A)
        r_B = sigmoid(W @ (drive_B * 0.3) + drive_B)
        # Establish bumps with drives (no cross-inhibition yet)
        for _ in range(500):
            h_A = W @ r_A + drive_A
            h_B = W @ r_B + drive_B
            r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
            r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Converge with cross-inhibition at the target J_cross
    for _ in range(100000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    # Polish with Newton
    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_0, J_cross),
                             fprime=lambda x, W, c, j: jacobian_analytical(x, W, c, j),
                             full_output=True, maxfev=10000)
    res = np.max(np.abs(residual(sol, W, cue_0, J_cross)))
    return sol[:N], sol[N:], res


def analyze_stability(r_A, r_B, W, preferred, J_cross, cue_gain=0.0):
    """Full eigenvalue analysis at a fixed point."""
    theta1 = np.pi / 4
    cue_A = cue_gain * tuning_curve(theta1, preferred, KAPPA)

    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)

    x = np.concatenate([r_A, r_B])
    J = jacobian_analytical(x, W, cue_A, J_cross)
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
        'J_cross': J_cross,
        'cue_gain': cue_gain,
        'r_A': r_A.copy(), 'r_B': r_B.copy(),
        'eigenvalues': evals,
        'eigenvectors': evecs,
        'lambda_1': evals[0].real,
        'lambda_2': evals[1].real,
        'lambda_3': evals[2].real,
        'D': np.mean(r_A) - np.mean(r_B),
        'n_positive': int(np.sum(evals.real > 1e-10)),
        'max_rA': np.max(r_A),
        'max_rB': np.max(r_B),
        'proj_cos': abs(np.dot(v1n, d_cos)),
        'proj_sin': abs(np.dot(v1n, d_sin)),
        'proj_uni': abs(np.dot(v1n, d_uni)),
        'residual': np.max(np.abs(np.concatenate([
            -r_A + sigmoid(h_A), -r_B + sigmoid(h_B)
        ]))),
    }


# ═══════════════════════════════════════════════════════════════════
# PHASE 1: SCAN J_CROSS AT CUE=0
# ═══════════════════════════════════════════════════════════════════

def scan_jcross():
    W, preferred = build_within_weights(N, J_0, J_1)

    # Dense scan near expected transition, coarser elsewhere
    jc_values = np.sort(np.unique(np.concatenate([
        np.linspace(0.0, 0.10, 6),
        np.linspace(0.10, 0.20, 8),
        np.linspace(0.20, 0.30, 15),
        np.linspace(0.30, 0.36, 15),
    ])))

    print("=" * 70)
    print("PHASE 1: Scanning J_cross at cue=0")
    print("=" * 70)

    results = []
    r_A_prev, r_B_prev = None, None

    for jc in jc_values:
        if r_A_prev is not None and jc > 0:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc, r_A_prev, r_B_prev)
        else:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

        if res > 1e-4:
            print(f"  J_cross={jc:.4f}: FAILED (res={res:.2e})")
            results.append(None)
            continue

        has_bumps = np.max(r_A) > 0.3 and np.max(r_B) > 0.3
        if not has_bumps:
            print(f"  J_cross={jc:.4f}: No bumps (max_A={np.max(r_A):.3f}, max_B={np.max(r_B):.3f})")
            results.append(None)
            continue

        result = analyze_stability(r_A, r_B, W, preferred, jc)
        results.append(result)
        r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

        marker = "SADDLE" if result['n_positive'] > 0 else "STABLE"
        print(f"  J_cross={jc:.4f}: λ₁={result['lambda_1']:+.6f}, "
              f"n_pos={result['n_positive']}, D={result['D']:+.6f}, "
              f"|cos|={result['proj_cos']:.3f}, |sin|={result['proj_sin']:.3f}  [{marker}]")

    return results, W, preferred, jc_values


# ═══════════════════════════════════════════════════════════════════
# PHASE 2: 2D BIFURCATION DIAGRAM (J_cross, cue)
# ═══════════════════════════════════════════════════════════════════

def bifurcation_2d(W, preferred):
    """Map the stability boundary in the (J_cross, cue) plane."""
    print("\n" + "=" * 70)
    print("PHASE 2: 2D bifurcation diagram")
    print("=" * 70)

    jc_vals = np.linspace(0.05, 0.35, 16)
    cue_vals = np.linspace(0.0, 0.10, 16)

    grid = np.full((len(jc_vals), len(cue_vals)), np.nan)
    n_pos_grid = np.full((len(jc_vals), len(cue_vals)), np.nan)

    for i, jc in enumerate(jc_vals):
        # First find coexistence at cue=0
        r_A, r_B, res0 = find_coexistence_fp(W, preferred, jc)
        if res0 > 1e-4 or np.max(r_A) < 0.3 or np.max(r_B) < 0.3:
            print(f"  J_cross={jc:.3f}: no coexistence at cue=0")
            continue

        for j, cg in enumerate(cue_vals):
            # Use Newton to track coexistence branch to this cue
            theta1 = np.pi / 4
            cue_A = cg * tuning_curve(theta1, preferred, KAPPA)
            x0 = np.concatenate([r_A, r_B])
            sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_A, jc),
                                     fprime=lambda x, W, c, j=jc: jacobian_analytical(x, W, c, j),
                                     full_output=True, maxfev=10000)
            res = np.max(np.abs(residual(sol, W, cue_A, jc)))
            if res > 1e-5:
                continue
            rA_s, rB_s = sol[:N], sol[N:]
            if np.max(rA_s) < 0.2 or np.max(rB_s) < 0.2:
                continue

            result = analyze_stability(rA_s, rB_s, W, preferred, jc, cg)
            grid[i, j] = result['lambda_1']
            n_pos_grid[i, j] = result['n_positive']

        done = np.sum(~np.isnan(grid[i, :]))
        print(f"  J_cross={jc:.3f}: {done}/{len(cue_vals)} points computed")

    return grid, n_pos_grid, jc_vals, cue_vals


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_results(results, jc_values, grid, n_pos_grid, jc_2d, cue_2d,
                 W, preferred, save_path):
    valid = [r for r in results if r is not None]
    jc_v = [r['J_cross'] for r in valid]

    fig = plt.figure(figsize=(22, 18))
    gs = GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.35)

    # ── (0,0) λ₁ vs J_cross ──
    ax = fig.add_subplot(gs[0, 0])
    colors = [COLORS['critical'] if r['lambda_1'] > 0 else COLORS['stable'] for r in valid]
    ax.scatter(jc_v, [r['lambda_1'] for r in valid], c=colors, s=40, zorder=3)
    ax.plot(jc_v, [r['lambda_1'] for r in valid], '-', color='gray', lw=0.8, alpha=0.5)
    ax.axhline(y=0, color='black', ls='--', lw=1.5, alpha=0.5)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue vs Cross-Inhibition', fontweight='bold')

    # Find the crossing
    for i in range(len(valid) - 1):
        if valid[i]['lambda_1'] * valid[i+1]['lambda_1'] < 0:
            jc1, jc2 = valid[i]['J_cross'], valid[i+1]['J_cross']
            l1, l2 = valid[i]['lambda_1'], valid[i+1]['lambda_1']
            jc_crit = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)
            ax.axvline(x=jc_crit, color=COLORS['dominance'], ls=':', lw=2, alpha=0.8)
            ax.annotate(f'J* = {jc_crit:.4f}', xy=(jc_crit, 0),
                       xytext=(jc_crit - 0.05, 0.015),
                       fontsize=10, fontweight='bold', color=COLORS['dominance'],
                       arrowprops=dict(arrowstyle='->', color=COLORS['dominance']))

    # ── (0,1) Top 3 eigenvalues ──
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(jc_v, [r['lambda_1'] for r in valid], 'o-', color=COLORS['critical'],
            lw=2, ms=3, label='λ₁')
    ax.plot(jc_v, [r['lambda_2'] for r in valid], 's-', color=COLORS['dominance'],
            lw=1.5, ms=2, label='λ₂')
    ax.plot(jc_v, [r['lambda_3'] for r in valid], '^-', color=COLORS['network_A'],
            lw=1, ms=2, label='λ₃')
    ax.axhline(y=0, color='gray', ls='--', alpha=0.4)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 3 Eigenvalues', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (0,2) Eigenvector projections ──
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(jc_v, [r['proj_cos'] for r in valid], 'o-', color=COLORS['critical'],
            lw=2, ms=4, label='|⟨v₁, d_cos⟩|')
    ax.plot(jc_v, [r['proj_sin'] for r in valid], '^-', color=COLORS['dominance'],
            lw=1.5, ms=3, label='|⟨v₁, d_sin⟩|')
    ax.plot(jc_v, [r['proj_uni'] for r in valid], 's--', color=COLORS['bulk'],
            lw=1, ms=3, label='|⟨v₁, d_uni⟩|')
    ax.set_xlabel('J_cross')
    ax.set_ylabel('|Projection|')
    ax.set_ylim(-0.05, 1.05)
    ax.set_title('Critical Eigenvector Character', fontweight='bold')
    ax.legend(fontsize=7)

    # ── (1,0) Number of unstable directions ──
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(jc_v, [r['n_positive'] for r in valid], 'o-', color=COLORS['dominance'],
            lw=2, ms=5)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('# positive eigenvalues')
    ax.set_title('Instability Index vs J_cross', fontweight='bold')
    ax.set_yticks(range(max([r['n_positive'] for r in valid]) + 2))

    # ── (1,1) Bump heights ──
    ax = fig.add_subplot(gs[1, 1])
    ax.plot(jc_v, [r['max_rA'] for r in valid], 'o-', color=COLORS['network_A'],
            lw=2, ms=3, label='max(r_A)')
    ax.plot(jc_v, [r['max_rB'] for r in valid], 'o-', color=COLORS['network_B'],
            lw=2, ms=3, label='max(r_B)')
    ax.set_xlabel('J_cross')
    ax.set_ylabel('Peak firing rate')
    ax.set_title('Bump Heights (cue=0)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (1,2) Activity profiles at key J_cross values ──
    ax = fig.add_subplot(gs[1, 2])
    angles = np.linspace(-180, 180, N, endpoint=False)
    show_jc = [0.0, 0.15, 0.25, 0.35]
    cmap = plt.cm.RdYlBu_r
    for idx_s, jc_target in enumerate(show_jc):
        matches = [r for r in valid if abs(r['J_cross'] - jc_target) < 0.02]
        if matches:
            m = min(matches, key=lambda r: abs(r['J_cross'] - jc_target))
            c = cmap(idx_s / (len(show_jc) - 1))
            ax.plot(angles, m['r_A'], '-', color=c, lw=2,
                    label=f'J={m["J_cross"]:.2f}, λ₁={m["lambda_1"]:.4f}')
    ax.set_xlabel('Preferred angle (°)')
    ax.set_ylabel('Activity (r_A only)')
    ax.set_title('Bump Shape vs Cross-Inhibition', fontweight='bold')
    ax.legend(fontsize=7)

    # ── (2,0) 2D bifurcation: λ₁ in (J_cross, cue) plane ──
    ax = fig.add_subplot(gs[2, 0])
    JC, CUE = np.meshgrid(jc_2d, cue_2d, indexing='ij')
    mask = ~np.isnan(grid)
    if np.any(mask):
        levels = np.linspace(-0.02, 0.02, 21)
        cf = ax.contourf(JC, CUE, grid, levels=levels, cmap='RdBu_r', extend='both')
        plt.colorbar(cf, ax=ax, label='Re(λ₁)')
        # Stability boundary
        try:
            ax.contour(JC, CUE, grid, levels=[0], colors='black', linewidths=2)
        except:
            pass
    ax.set_xlabel('J_cross')
    ax.set_ylabel('cue_gain')
    ax.set_title('Stability Boundary: λ₁ = 0', fontweight='bold')

    # ── (2,1) 2D bifurcation: number of unstable directions ──
    ax = fig.add_subplot(gs[2, 1])
    if np.any(~np.isnan(n_pos_grid)):
        cf = ax.contourf(JC, CUE, n_pos_grid, levels=[-0.5, 0.5, 1.5, 2.5, 3.5],
                         colors=['#2196F3', '#FFC107', '#F44336', '#9C27B0'])
        plt.colorbar(cf, ax=ax, label='# unstable directions', ticks=[0, 1, 2, 3])
    ax.set_xlabel('J_cross')
    ax.set_ylabel('cue_gain')
    ax.set_title('Instability Index in Parameter Space', fontweight='bold')

    # ── (2,2) Summary text ──
    ax = fig.add_subplot(gs[2, 2])
    ax.axis('off')

    # Find critical J_cross
    jc_crit_str = "not found"
    for i in range(len(valid) - 1):
        if valid[i]['lambda_1'] * valid[i+1]['lambda_1'] < 0:
            jc1, jc2 = valid[i]['J_cross'], valid[i+1]['J_cross']
            l1, l2 = valid[i]['lambda_1'], valid[i+1]['lambda_1']
            jc_crit = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)
            jc_crit_str = f"{jc_crit:.4f}"
            break

    summary = f"""THE SPECTRAL SEPARATRIX

At cue = 0, the coexistence fixed point undergoes
a pitchfork bifurcation in the cross-inhibition
strength J_cross:

  J_cross < J*:  Coexistence STABLE
                 (both bumps self-sustain)

  J_cross > J*:  Coexistence SADDLE
                 (WTA basins emerge)

  Critical J* ≈ {jc_crit_str}

At the bifurcation:
  - λ₁ crosses zero continuously
  - Two WTA attractors are born
  - The coexistence FP becomes a saddle
  - Its stable manifold IS the separatrix

This is the pitchfork that creates the
winner-take-all competition.

The behavioral cliff in cue-space is a
CONSEQUENCE of this structural instability
in J_cross-space.
"""
    ax.text(0.05, 0.95, summary, transform=ax.transAxes,
            fontsize=9, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0', alpha=0.8))

    fig.suptitle('The Real Spectral Separatrix: Pitchfork Bifurcation in J_cross\n'
                 'Coexistence → Saddle transition at cue = 0',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    # Phase 1: J_cross scan at cue=0
    results, W, preferred, jc_values = scan_jcross()

    # Phase 2: 2D bifurcation diagram
    grid, n_pos_grid, jc_2d, cue_2d = bifurcation_2d(W, preferred)

    # Plot
    plot_results(results, jc_values, grid, n_pos_grid, jc_2d, cue_2d,
                 W, preferred,
                 os.path.join(outdir, 'fig52_spectral_separatrix_jcross.png'))

    # Print summary
    valid = [r for r in results if r is not None]
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Valid solutions: {len(valid)}/{len(jc_values)}")
    if valid:
        stable = [r for r in valid if r['n_positive'] == 0]
        saddle = [r for r in valid if r['n_positive'] > 0]
        print(f"  Stable: {len(stable)}")
        print(f"  Saddle: {len(saddle)}")
        print(f"  λ₁ range: [{min(r['lambda_1'] for r in valid):.6f}, "
              f"{max(r['lambda_1'] for r in valid):.6f}]")

        # Find critical J_cross
        for i in range(len(valid) - 1):
            if valid[i]['lambda_1'] * valid[i+1]['lambda_1'] < 0:
                jc1, jc2 = valid[i]['J_cross'], valid[i+1]['J_cross']
                l1, l2 = valid[i]['lambda_1'], valid[i+1]['lambda_1']
                jc_crit = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)
                print(f"\n  *** PITCHFORK BIFURCATION at J_cross* ≈ {jc_crit:.4f} ***")
                print(f"      (between {jc1:.4f} [λ₁={l1:+.6f}] and {jc2:.4f} [λ₁={l2:+.6f}])")

                # Characterize the critical eigenvector at the nearest point
                near = min(valid, key=lambda r: abs(r['J_cross'] - jc_crit))
                print(f"      Near J*: |cos|={near['proj_cos']:.3f}, |sin|={near['proj_sin']:.3f}")
                print(f"      Bump heights: max(rA)={near['max_rA']:.3f}, max(rB)={near['max_rB']:.3f}")
                break
    print(f"{'='*70}")
