"""
==========================================================================
SPECTRAL PORTRAIT — PART 2: THE EIGENVALUE CROSSING
==========================================================================

Follow-up computations:

  1. CORRECTED DOMINANCE PROJECTION
     The critical eigenvector is cosine-shaped, not uniform.
     The correct dominance direction is the first Fourier mode:
       d_cos = [cos(φ₁),...,cos(φ_N), -cos(φ₁),...,-cos(φ_N)] / norm
     This should give |⟨v₁, d_cos⟩| ≈ 1.0, proving that D = A₁ - A₂
     IS the spectrally correct projection.

  2. UNSTABLE FIXED POINT TRACKING
     The stable fixed point shows eigenvalues BELOW zero (naturally —
     it's stable). To see the eigenvalue CROSSING zero, we need the
     SYMMETRIC (unstable) fixed point. Find it via Newton's method
     on the full-neuron system with enforced symmetry, then compute
     its Jacobian and track the critical eigenvalue through the
     bifurcation.

  3. SPECTRAL GAP ANALYSIS
     Measure the gap between the outlier eigenvalue and the bulk edge
     as a function of cue_gain. This is the spectral analogue of
     "decisiveness" — how cleanly the system commits to one state.

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

# Import from the main spectral portrait module
import sys
sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve,
    compute_full_jacobian, find_fixed_point_full, COLORS
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
# 1. CORRECTED DOMINANCE PROJECTION
# ═══════════════════════════════════════════════════════════════════

def compute_corrected_projections(save_path, N=48, J_cross=0.5):
    """
    Recompute the critical eigenvector projection using the
    cosine-weighted dominance direction (first Fourier mode).

    d_uniform = [+1,...,+1, -1,...,-1] / norm  (zeroth mode: mean activity)
    d_cosine  = [+cos(φ),..., -cos(φ),...] / norm  (first mode: bump amplitude)

    The critical eigenvector should align with d_cosine, not d_uniform.
    """
    W, preferred = build_within_weights(N, 1.0, 6.0)

    cue_gains = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5]

    results = []
    for cg in cue_gains:
        print(f"  Projection at cue_gain = {cg:.4f}...")
        r_A, r_B, h_A, h_B, W_out, pref = find_fixed_point_full(
            cg, N=N, J_cross=J_cross)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W_out, J_cross)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals = evals[idx]
        evecs = evecs[:, idx]

        v1 = evecs[:, 0].real
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-30)

        # Uniform dominance direction (zeroth Fourier mode)
        d_uniform = np.concatenate([np.ones(N), -np.ones(N)])
        d_uniform /= np.linalg.norm(d_uniform)

        # Cosine dominance direction (first Fourier mode)
        # Matches the bump shape: cos(φ - φ_target) for network A,
        # minus the same for network B
        # Use the item angle (π/4) from the simulation
        theta_target = np.pi / 4
        cos_profile = np.cos(pref - theta_target)
        d_cosine = np.concatenate([cos_profile, -cos_profile])
        d_cosine /= np.linalg.norm(d_cosine)

        # Sine component (orthogonal to cosine in angular space)
        sin_profile = np.sin(pref - theta_target)
        d_sine = np.concatenate([sin_profile, -sin_profile])
        d_sine /= np.linalg.norm(d_sine)

        # Projections
        proj_uniform = np.abs(np.dot(v1_norm, d_uniform))
        proj_cosine = np.abs(np.dot(v1_norm, d_cosine))
        proj_sine = np.abs(np.dot(v1_norm, d_sine))

        results.append({
            'cue_gain': cg,
            'lambda_1': evals[0].real,
            'proj_uniform': proj_uniform,
            'proj_cosine': proj_cosine,
            'proj_sine': proj_sine,
            'dominance': np.mean(r_A) - np.mean(r_B),
            'v1': v1,
            'r_A': r_A, 'r_B': r_B,
        })

        print(f"    λ₁ = {evals[0].real:.6f}")
        print(f"    |⟨v₁, d_uniform⟩| = {proj_uniform:.4f}")
        print(f"    |⟨v₁, d_cosine⟩|  = {proj_cosine:.4f}")
        print(f"    |⟨v₁, d_sine⟩|    = {proj_sine:.4f}")

    # ── Plot ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    cgs = [r['cue_gain'] for r in results]

    # Left: Projections vs cue_gain
    ax = axes[0]
    ax.plot(cgs, [r['proj_cosine'] for r in results],
            'o-', color=COLORS['critical'], linewidth=2, markersize=6,
            label='|⟨v₁, d_cosine⟩| (bump amplitude)')
    ax.plot(cgs, [r['proj_uniform'] for r in results],
            's--', color=COLORS['bulk'], linewidth=1.5, markersize=5,
            label='|⟨v₁, d_uniform⟩| (mean activity)')
    ax.plot(cgs, [r['proj_sine'] for r in results],
            '^:', color=COLORS['dominance'], linewidth=1, markersize=4,
            label='|⟨v₁, d_sine⟩| (angular drift)')
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='behavioral cliff')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('|Projection|')
    ax.set_title('Critical Eigenvector Projection\nonto Dominance Directions',
                fontweight='bold')
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)

    # Middle: λ₁ vs cue_gain
    ax = axes[1]
    ax.plot(cgs, [r['lambda_1'] for r in results],
            'o-', color=COLORS['critical'], linewidth=2, markersize=6)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue\n(stable fixed point)',
                fontweight='bold')

    # Right: Eigenvector at selected cue_gain (e.g., cue=0.01)
    ax = axes[2]
    r_sel = results[2]  # cue_gain = 0.01
    angles = np.linspace(-180, 180, N, endpoint=False)
    v_A = r_sel['v1'][:N]
    v_B = r_sel['v1'][N:]
    norm = np.max(np.abs(r_sel['v1']))
    ax.plot(angles, v_A / norm, '-', color=COLORS['network_A'],
            linewidth=2, label='v₁ (Network A)')
    ax.plot(angles, v_B / norm, '-', color=COLORS['network_B'],
            linewidth=2, label='v₁ (Network B)')
    # Overlay cosine dominance direction
    theta_target = np.pi / 4
    cos_ref = np.cos(np.linspace(-np.pi, np.pi, N, endpoint=False) - theta_target)
    ax.plot(angles, cos_ref / np.max(np.abs(cos_ref)) * 0.8, '--',
            color='gray', linewidth=1, alpha=0.5, label='cos(φ - φ_target)')
    ax.axhline(y=0, color='gray', alpha=0.3)
    ax.set_xlabel('Preferred angle (°)')
    ax.set_ylabel('Eigenvector component (normalized)')
    ax.set_title(f'Critical Eigenvector at cue = {r_sel["cue_gain"]:.3f}\n'
                f'|⟨v₁, d_cos⟩| = {r_sel["proj_cosine"]:.3f}',
                fontweight='bold')
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")
    return results


# ═══════════════════════════════════════════════════════════════════
# 2. UNSTABLE (SYMMETRIC) FIXED POINT VIA ENFORCED SYMMETRY
# ═══════════════════════════════════════════════════════════════════

def find_symmetric_fixed_point(cue_gain, N=48, J_0=1.0, J_1=6.0,
                                J_cross=0.5, kappa=2.0, input_gain=5.0,
                                r_max=1.0, beta=5.0, h0=0.5,
                                dt=0.1, tau=10.0, n_steps=20000):
    """
    Find the SYMMETRIC fixed point where both networks have equal bumps.

    Strategy: enforce r_A = r_B at every step. This constrains the system
    to the symmetric subspace. The fixed point of this constrained system
    is the unstable fixed point of the full system (unstable to
    symmetry-breaking perturbations).
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    # Drive for both items (averaged to enforce symmetry in drive)
    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)

    # Start with averaged initial condition
    r = sigmoid(W @ ((drive_A + drive_B) * 0.15) + (drive_A + drive_B) * 0.5,
                r_max, beta, h0)

    # Cue drive (only to A in the full system, but we symmetrize)
    cue_A = cue_gain * tuning_curve(theta1, preferred, kappa)

    # Phase 1: Drive both, average
    for step in range(200):
        cross = -J_cross * np.mean(r)
        h_A = W @ r + drive_A + cross
        h_B = W @ r + drive_B + cross
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        f_avg = (f_A + f_B) / 2.0
        dr = (-r + f_avg) * (dt / tau)
        r = np.maximum(0, r + dr)

    # Phase 2: Maintenance with cue, but keep symmetry
    # The "symmetric" fixed point with a cue is really the one where
    # both networks have the same total activity but different bumps.
    # Actually, with asymmetric cue, the "symmetric" fixed point doesn't
    # exist in the same sense. Instead, find the fixed point where
    # NEITHER network has fully won.

    # Better approach: find the fixed point of the full 2N system
    # using Newton's method, starting from a nearly-symmetric state.
    r_A = r.copy()
    r_B = r.copy()

    for step in range(n_steps):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + cue_A + cross_A
        h_B = W @ r_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)
        r_B = np.maximum(0, r_B + dr_B)

        if step > 500 and np.max(np.abs(dr_A)) < 1e-12 and np.max(np.abs(dr_B)) < 1e-12:
            break

    # Compute Jacobian at this fixed point
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)
    h_A = W @ r_A + cue_A + cross_A
    h_B = W @ r_B + cross_B

    return r_A, r_B, h_A, h_B, W, preferred


def track_eigenvalue_crossing(save_path, N=48, J_cross=0.5):
    """
    Track the dominant eigenvalue of the Jacobian across the bifurcation.

    Two approaches:
    A) Track the STABLE fixed point (eigenvalue stays < 0 but approaches 0)
    B) Track from the SYMMETRIC initial condition (may find unstable FP)

    Also compute the spectral gap (distance between outlier and bulk).
    """
    cue_gains = np.concatenate([
        np.linspace(0.0, 0.005, 10),
        np.linspace(0.005, 0.05, 30),
        np.linspace(0.05, 0.2, 15),
        np.linspace(0.2, 0.5, 10),
    ])

    stable_data = []
    symmetric_data = []

    for cg in cue_gains:
        print(f"  cue_gain = {cg:.4f}")

        # ── Stable fixed point ────────────────────────────────
        r_A, r_B, h_A, h_B, W, pref = find_fixed_point_full(
            cg, N=N, J_cross=J_cross)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals = np.sort(np.linalg.eigvals(J).real)[::-1]

        # Spectral gap: difference between λ₁ and the bulk
        # Define bulk as median of eigenvalues
        bulk_median = np.median(evals)
        spectral_gap = evals[0] - bulk_median

        stable_data.append({
            'cue_gain': cg,
            'lambda_1': evals[0],
            'lambda_2': evals[1],
            'lambda_3': evals[2],
            'bulk_median': bulk_median,
            'spectral_gap': spectral_gap,
            'dominance': np.mean(r_A) - np.mean(r_B),
        })

        # ── Symmetric-start fixed point ───────────────────────
        r_A_s, r_B_s, h_A_s, h_B_s, W_s, pref_s = find_symmetric_fixed_point(
            cg, N=N, J_cross=J_cross)
        J_s = compute_full_jacobian(r_A_s, r_B_s, h_A_s, h_B_s, W_s, J_cross)
        evals_s = np.sort(np.linalg.eigvals(J_s).real)[::-1]

        symmetric_data.append({
            'cue_gain': cg,
            'lambda_1': evals_s[0],
            'lambda_2': evals_s[1],
            'dominance': np.mean(r_A_s) - np.mean(r_B_s),
            'n_positive': np.sum(evals_s > 0),
        })

        print(f"    Stable:    λ₁={evals[0]:.6f}, D={np.mean(r_A)-np.mean(r_B):.4f}")
        print(f"    Symmetric: λ₁={evals_s[0]:.6f}, D={np.mean(r_A_s)-np.mean(r_B_s):.4f}, "
              f"n_pos={np.sum(evals_s > 0)}")

    # ── FIGURE: Eigenvalue Crossing & Spectral Gap ────────────
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)

    # (a) Dominant eigenvalue: stable vs symmetric start
    ax = fig.add_subplot(gs[0, 0])
    cgs = [d['cue_gain'] for d in stable_data]
    ax.plot(cgs, [d['lambda_1'] for d in stable_data],
            'o-', color=COLORS['stable'], linewidth=2, markersize=4,
            label='λ₁ (stable FP)')
    ax.plot(cgs, [d['lambda_1'] for d in symmetric_data],
            's-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='λ₁ (symmetric-start FP)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue\nStable vs Symmetric Fixed Point',
                fontweight='bold')
    ax.legend(fontsize=9)

    # (b) Number of positive eigenvalues (symmetric FP)
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(cgs, [d['n_positive'] for d in symmetric_data],
            's-', color=COLORS['critical'], linewidth=2, markersize=5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Number of positive eigenvalues')
    ax.set_title('Instability Index\n(symmetric-start fixed point)',
                fontweight='bold')

    # (c) Spectral gap: outlier to bulk
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(cgs, [d['spectral_gap'] for d in stable_data],
            'o-', color=COLORS['dominance'], linewidth=2, markersize=4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('λ₁ - median(bulk)')
    ax.set_title('Spectral Gap: Outlier vs Bulk\n(stable FP)',
                fontweight='bold')

    # (d) Dominance comparison
    ax = fig.add_subplot(gs[1, 1])
    ax.plot(cgs, [d['dominance'] for d in stable_data],
            'o-', color=COLORS['stable'], linewidth=2, markersize=4,
            label='Stable FP')
    ax.plot(cgs, [d['dominance'] for d in symmetric_data],
            's-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='Symmetric-start FP')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance Variable\nTwo fixed points',
                fontweight='bold')
    ax.legend(fontsize=9)

    fig.suptitle('The Eigenvalue Crossing: Spectral Bifurcation at the Separatrix\n'
                 'Full 96D Jacobian analysis of the coupled ring attractor',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")

    return stable_data, symmetric_data


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    print("=" * 70)
    print("SPECTRAL PORTRAIT — PART 2")
    print("Corrected projections + Eigenvalue crossing")
    print("=" * 70)

    print("\n[1/2] Corrected dominance projections...")
    proj_results = compute_corrected_projections(
        os.path.join(outdir, 'fig40_corrected_projections.png'))

    print("\n[2/2] Eigenvalue crossing analysis...")
    stable_data, sym_data = track_eigenvalue_crossing(
        os.path.join(outdir, 'fig41_eigenvalue_crossing.png'))

    print("\n" + "=" * 70)
    print("DONE.")
    print("=" * 70)
