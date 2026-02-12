"""
==========================================================================
SPECTRAL PORTRAIT — PART 4: THE COEXISTENCE SEPARATRIX
==========================================================================

Part 3 found the WRONG fixed point. Newton continuation starting from
uniform activity tracked the HOMOGENEOUS state (no bumps), which is
stable but irrelevant to working memory.

The separatrix we want lives between:
  - COEXISTENCE: both networks have bumps (balanced working memory)
  - WINNER-TAKE-ALL: one network dominates (biased recall)

To find the coexistence saddle point, we must:
  1. Start Newton from a state where BOTH bumps are present
  2. Use the Phase 1 endpoint (both drives active) as initial guess
  3. Track this branch as cue_gain increases

The coexistence state should become unstable at the behavioral cliff.
Its critical eigenvector should be the DOMINANCE mode.
THAT is the separatrix GLM 5 named.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve, root
from scipy.special import i0
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

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
# THE RESIDUAL (same as Part 3)
# ═══════════════════════════════════════════════════════════════════

def full_system_residual(x, W, cue_drive_A, J_cross, N,
                          r_max=1.0, beta=5.0, h0=0.5):
    """F(r) = -r + σ(h) for the full 2N system."""
    r_A = x[:N]
    r_B = x[N:]
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)
    h_A = W @ r_A + cue_drive_A + cross_A
    h_B = W @ r_B + cross_B
    f_A = sigmoid(h_A, r_max, beta, h0)
    f_B = sigmoid(h_B, r_max, beta, h0)
    return np.concatenate([-r_A + f_A, -r_B + f_B])


def full_system_jacobian(x, W, cue_drive_A, J_cross, N,
                          r_max=1.0, beta=5.0, h0=0.5):
    """Analytical Jacobian ∂F/∂r for root-finding."""
    r_A = x[:N]
    r_B = x[N:]
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)
    h_A = W @ r_A + cue_drive_A + cross_A
    h_B = W @ r_B + cross_B

    D_A = np.diag(sigmoid_derivative(h_A, r_max, beta, h0))
    D_B = np.diag(sigmoid_derivative(h_B, r_max, beta, h0))
    cross_mat = np.full((N, N), -J_cross / N)

    J = np.zeros((2 * N, 2 * N))
    J[:N, :N] = -np.eye(N) + D_A @ W
    J[:N, N:] = D_A @ cross_mat
    J[N:, :N] = D_B @ cross_mat
    J[N:, N:] = -np.eye(N) + D_B @ W
    return J


# ═══════════════════════════════════════════════════════════════════
# THE KEY FIX: START FROM COEXISTENCE, NOT HOMOGENEOUS
# ═══════════════════════════════════════════════════════════════════

def find_coexistence_initial_guess(N=48, J_0=1.0, J_1=6.0, J_cross=0.5,
                                    kappa=2.0, input_gain=5.0,
                                    r_max=1.0, beta=5.0, h0=0.5,
                                    dt=0.1, tau=10.0):
    """
    Find the coexistence state where BOTH networks have bumps.

    Strategy: simulate with BOTH drives active until convergence.
    This establishes two bumps. The steady state with both drives
    is our starting point.

    Then GRADUALLY reduce the drives to zero. At each step, use
    Newton to find the nearby fixed point. This tracks the coexistence
    branch even as it becomes unstable.
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)

    # Initialize and run with both drives
    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A, r_max, beta, h0)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B, r_max, beta, h0)

    for step in range(5000):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + drive_A + cross_A
        h_B = W @ r_B + drive_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)
        r_B = np.maximum(0, r_B + dr_B)
        if step > 100 and np.max(np.abs(dr_A)) < 1e-12 and np.max(np.abs(dr_B)) < 1e-12:
            break

    print(f"  Coexistence with drives: mean(r_A)={np.mean(r_A):.4f}, "
          f"mean(r_B)={np.mean(r_B):.4f}, D={np.mean(r_A)-np.mean(r_B):.4f}")
    print(f"  max(r_A)={np.max(r_A):.4f}, max(r_B)={np.max(r_B):.4f}")

    return r_A, r_B, W, preferred


def continuation_from_coexistence(cue_gains, N=48, J_0=1.0, J_1=6.0,
                                   J_cross=0.5, kappa=2.0, input_gain=5.0,
                                   r_max=1.0, beta=5.0, h0=0.5):
    """
    Track the coexistence branch using Newton continuation.

    Step 1: Find the coexistence FP at cue=0 using gradual drive removal.
    Step 2: Use this as the starting point for continuation in cue_gain.
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    # ── Step 1: Find coexistence at cue=0 ──
    # Get the driven coexistence state
    r_A_driven, r_B_driven, _, _ = find_coexistence_initial_guess(
        N, J_0, J_1, J_cross, kappa, input_gain, r_max, beta, h0)

    # Now gradually remove the external drives using Newton
    # The "drive" terms are NOT part of the recurrent dynamics
    # At cue=0, the steady-state equation is:
    #   r_A = σ(W·r_A - J_cross·mean(r_B))
    #   r_B = σ(W·r_B - J_cross·mean(r_A))

    # Use the driven state as initial guess for the NO-DRIVE problem
    x_coex = np.concatenate([r_A_driven, r_B_driven])

    # Gradual drive removal: add a fraction of drive and decrease it
    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)

    drive_fractions = np.linspace(1.0, 0.0, 50)
    for frac in drive_fractions:
        partial_drive_A = frac * drive_A
        partial_drive_B = frac * drive_B

        # Modified residual with partial drive
        def residual_with_drive(x):
            r_A = x[:N]
            r_B = x[N:]
            cross_A = -J_cross * np.mean(r_B)
            cross_B = -J_cross * np.mean(r_A)
            h_A = W @ r_A + partial_drive_A + cross_A
            h_B = W @ r_B + partial_drive_B + cross_B
            f_A = sigmoid(h_A, r_max, beta, h0)
            f_B = sigmoid(h_B, r_max, beta, h0)
            return np.concatenate([-r_A + f_A, -r_B + f_B])

        def jac_with_drive(x):
            r_A = x[:N]
            r_B = x[N:]
            cross_A = -J_cross * np.mean(r_B)
            cross_B = -J_cross * np.mean(r_A)
            h_A = W @ r_A + partial_drive_A + cross_A
            h_B = W @ r_B + partial_drive_B + cross_B
            D_A = np.diag(sigmoid_derivative(h_A, r_max, beta, h0))
            D_B = np.diag(sigmoid_derivative(h_B, r_max, beta, h0))
            cross_m = np.full((N, N), -J_cross / N)
            J = np.zeros((2 * N, 2 * N))
            J[:N, :N] = -np.eye(N) + D_A @ W
            J[:N, N:] = D_A @ cross_m
            J[N:, :N] = D_B @ cross_m
            J[N:, N:] = -np.eye(N) + D_B @ W
            return J

        sol, info, ier, _ = fsolve(
            residual_with_drive, x_coex,
            fprime=jac_with_drive,
            full_output=True, maxfev=5000)

        res = np.max(np.abs(residual_with_drive(sol)))
        if res < 1e-6:
            x_coex = sol
        else:
            print(f"  WARNING: drive_frac={frac:.3f} failed (residual={res:.2e})")

    r_A_coex = x_coex[:N]
    r_B_coex = x_coex[N:]
    D_coex = np.mean(r_A_coex) - np.mean(r_B_coex)
    print(f"  Coexistence at cue=0 (no drive): "
          f"mean(r_A)={np.mean(r_A_coex):.4f}, mean(r_B)={np.mean(r_B_coex):.4f}, "
          f"D={D_coex:.4f}")
    print(f"  max(r_A)={np.max(r_A_coex):.4f}, max(r_B)={np.max(r_B_coex):.4f}")

    # ── Step 2: Continuation in cue_gain ──
    results = []

    for cg in cue_gains:
        cue_drive_A = cg * tuning_curve(theta1, preferred, kappa)

        # Newton from the current coexistence state
        sol, info, ier, _ = fsolve(
            full_system_residual, x_coex,
            args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
            fprime=full_system_jacobian,
            full_output=True, maxfev=5000)

        res = np.max(np.abs(full_system_residual(
            sol, W, cue_drive_A, J_cross, N, r_max, beta, h0)))

        if res > 1e-6:
            # Try scipy.root with hybr
            result = root(
                full_system_residual, x_coex,
                args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
                method='hybr',
                jac=full_system_jacobian,
                options={'maxfev': 10000})
            if result.success:
                sol = result.x
                res = np.max(np.abs(result.fun))

        if res > 1e-6:
            print(f"  cue={cg:.4f}: FAILED (residual={res:.2e})")
            results.append(None)
            continue

        r_A = sol[:N]
        r_B = sol[N:]

        # Compute Jacobian eigenvalues
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + cue_drive_A + cross_A
        h_B = W @ r_B + cross_B
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals_sorted = evals[idx]
        evecs_sorted = evecs[:, idx]

        D_val = np.mean(r_A) - np.mean(r_B)
        n_positive = np.sum(evals_sorted.real > 0)

        # Projection of critical eigenvector
        v1 = evecs_sorted[:, 0].real
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-30)

        theta_target = np.pi / 4
        cos_profile = np.cos(preferred - theta_target)
        d_cosine = np.concatenate([cos_profile, -cos_profile])
        d_cosine /= np.linalg.norm(d_cosine)

        sin_profile = np.sin(preferred - theta_target)
        d_sine = np.concatenate([sin_profile, -sin_profile])
        d_sine /= np.linalg.norm(d_sine)

        d_uniform = np.concatenate([np.ones(N), -np.ones(N)])
        d_uniform /= np.linalg.norm(d_uniform)

        proj_cos = np.abs(np.dot(v1_norm, d_cosine))
        proj_sin = np.abs(np.dot(v1_norm, d_sine))
        proj_uni = np.abs(np.dot(v1_norm, d_uniform))

        results.append({
            'cue_gain': cg,
            'r_A': r_A.copy(), 'r_B': r_B.copy(),
            'h_A': h_A.copy(), 'h_B': h_B.copy(),
            'eigenvalues': evals_sorted,
            'eigenvectors': evecs_sorted,
            'lambda_1': evals_sorted[0].real,
            'lambda_2': evals_sorted[1].real,
            'lambda_3': evals_sorted[2].real,
            'D': D_val,
            'n_positive': n_positive,
            'mean_rA': np.mean(r_A),
            'mean_rB': np.mean(r_B),
            'max_rA': np.max(r_A),
            'max_rB': np.max(r_B),
            'proj_cos': proj_cos,
            'proj_sin': proj_sin,
            'proj_uni': proj_uni,
            'residual': res,
        })

        x_coex = sol  # Continue from this solution

        print(f"  cue={cg:.4f}: D={D_val:+.6f}, "
              f"λ₁={evals_sorted[0].real:+.6f}, n_pos={n_positive}, "
              f"max(rA)={np.max(r_A):.3f}, max(rB)={np.max(r_B):.3f}, "
              f"|⟨v₁,cos⟩|={proj_cos:.3f}")

    return results


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_coexistence_bifurcation(coex_results, stable_results, save_path, N=48):
    """
    The real bifurcation diagram: coexistence branch vs winner-take-all.
    """
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.3)

    coex_valid = [r for r in coex_results if r is not None]
    cg_coex = [r['cue_gain'] for r in coex_valid]
    cg_stable = [r['cue_gain'] for r in stable_results]

    # ── (a) Dominant eigenvalue ──
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(cg_coex, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁ (coexistence branch)')
    ax.plot(cg_stable, [r['lambda_1'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='λ₁ (winner-take-all)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue\nCoexistence vs Winner-Take-All',
                fontweight='bold')
    ax.legend(fontsize=8)

    # ── (b) Dominance D ──
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(cg_coex, [r['D'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='Coexistence')
    ax.plot(cg_stable, [r['D'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='Winner-take-all')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance (Order Parameter)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (c) Max bump height ──
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(cg_coex, [r['max_rA'] for r in coex_valid],
            'o-', color=COLORS['network_A'], linewidth=2, markersize=3,
            label='max(r_A) coexistence')
    ax.plot(cg_coex, [r['max_rB'] for r in coex_valid],
            'o-', color=COLORS['network_B'], linewidth=2, markersize=3,
            label='max(r_B) coexistence')
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Peak firing rate')
    ax.set_title('Bump Heights\n(Coexistence Branch)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (d) Instability index ──
    ax = fig.add_subplot(gs[1, 1])
    ax.plot(cg_coex, [r['n_positive'] for r in coex_valid],
            'o-', color=COLORS['dominance'], linewidth=2, markersize=4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('# positive eigenvalues')
    ax.set_title('Instability Index\n(Coexistence Branch)', fontweight='bold')

    # ── (e) Critical eigenvector projections ──
    ax = fig.add_subplot(gs[2, 0])
    ax.plot(cg_coex, [r['proj_cos'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='|⟨v₁, d_cosine⟩| (bump amplitude)')
    ax.plot(cg_coex, [r['proj_sin'] for r in coex_valid],
            '^-', color=COLORS['dominance'], linewidth=1.5, markersize=3,
            label='|⟨v₁, d_sine⟩| (angular drift)')
    ax.plot(cg_coex, [r['proj_uni'] for r in coex_valid],
            's--', color=COLORS['bulk'], linewidth=1, markersize=3,
            label='|⟨v₁, d_uniform⟩| (mean activity)')
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('|Projection|')
    ax.set_title('Eigenvector Projections\n(Coexistence Branch)', fontweight='bold')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=7)

    # ── (f) Top 3 eigenvalues ──
    ax = fig.add_subplot(gs[2, 1])
    ax.plot(cg_coex, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁')
    ax.plot(cg_coex, [r['lambda_2'] for r in coex_valid],
            's-', color=COLORS['dominance'], linewidth=1.5, markersize=2,
            label='λ₂')
    ax.plot(cg_coex, [r['lambda_3'] for r in coex_valid],
            '^-', color=COLORS['network_A'], linewidth=1, markersize=2,
            label='λ₃')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 3 Eigenvalues\n(Coexistence Branch)', fontweight='bold')
    ax.legend(fontsize=9)

    fig.suptitle('The Coexistence Separatrix: Both Bumps Present\n'
                 'Newton continuation from the balanced working memory state',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def plot_coexistence_profiles(coex_results, save_path, N=48):
    """
    Activity profiles and eigenvector at the coexistence FP.
    """
    coex_valid = [r for r in coex_results if r is not None]
    cue_targets = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1]
    angles = np.linspace(-180, 180, N, endpoint=False)

    n_cols = len(cue_targets)
    fig, axes = plt.subplots(3, n_cols, figsize=(3.2 * n_cols, 10))

    for col, cg_target in enumerate(cue_targets):
        match = min(coex_valid, key=lambda r: abs(r['cue_gain'] - cg_target))

        # Top: activity profiles
        ax = axes[0, col]
        ax.plot(angles, match['r_A'], '-', color=COLORS['network_A'],
                linewidth=2, label='r_A')
        ax.plot(angles, match['r_B'], '-', color=COLORS['network_B'],
                linewidth=2, label='r_B')
        ax.set_title(f'cue = {match["cue_gain"]:.3f}\n'
                    f'D = {match["D"]:.4f}',
                    fontsize=8, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        if col == 0:
            ax.set_ylabel('Activity r')
            ax.legend(fontsize=6)

        # Middle: critical eigenvector
        ax = axes[1, col]
        v1 = match['eigenvectors'][:, 0].real
        norm = np.max(np.abs(v1)) + 1e-30
        ax.plot(angles, v1[:N] / norm, '-', color=COLORS['network_A'],
                linewidth=2, label='v₁ (A)')
        ax.plot(angles, v1[N:] / norm, '-', color=COLORS['network_B'],
                linewidth=2, label='v₁ (B)')
        ax.axhline(y=0, color='gray', alpha=0.3)
        ax.set_title(f'λ₁ = {match["lambda_1"]:.4f}\n'
                    f'n_pos = {match["n_positive"]}',
                    fontsize=8, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Eigenvector')
            ax.legend(fontsize=6)

        # Bottom: projection bars
        ax = axes[2, col]
        bars = ax.bar(['cos', 'sin', 'uni'],
                      [match['proj_cos'], match['proj_sin'], match['proj_uni']],
                      color=[COLORS['critical'], COLORS['dominance'], COLORS['bulk']])
        ax.set_ylim(0, 1.1)
        ax.set_title(f'cos={match["proj_cos"]:.2f} sin={match["proj_sin"]:.2f}',
                    fontsize=7)
        ax.set_xlabel('Direction')
        if col == 0:
            ax.set_ylabel('|Projection|')

    fig.suptitle('Coexistence Branch: Activity, Eigenvector, and Projections\n'
                 'Tracking the balanced state as cue_gain increases',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def plot_phase_diagram(coex_results, stable_results, save_path, N=48):
    """
    Summary phase diagram: mean(r_A) vs mean(r_B) for both branches.
    The separatrix is the boundary between basins.
    """
    coex_valid = [r for r in coex_results if r is not None]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # (a) Phase space: mean(r_A) vs mean(r_B)
    ax = axes[0]
    ax.plot([r['mean_rA'] for r in coex_valid],
            [r['mean_rB'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='Coexistence', zorder=5)
    # Color by cue_gain
    for r in coex_valid:
        color = plt.cm.coolwarm(r['cue_gain'] / 0.5)
        ax.scatter(r['mean_rA'], r['mean_rB'], c=[color], s=20, zorder=6)

    # Add stable FP
    for r in stable_results:
        color = plt.cm.coolwarm(r['cue_gain'] / 0.5)
        ax.scatter(r['mean_rA'], r['mean_rB'], c=[color], s=20,
                  marker='s', zorder=4)
    ax.plot([r['mean_rA'] for r in stable_results],
            [r['mean_rB'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=1.5, markersize=3,
            label='Winner-take-all', zorder=3)

    # Diagonal (symmetry line)
    lim = [0, max(max(r['mean_rA'] for r in coex_valid + stable_results),
                  max(r['mean_rB'] for r in coex_valid + stable_results)) + 0.02]
    ax.plot(lim, lim, '--', color='gray', alpha=0.3, label='D = 0')
    ax.set_xlabel('⟨r_A⟩')
    ax.set_ylabel('⟨r_B⟩')
    ax.set_title('Phase Space\n(colored by cue_gain)', fontweight='bold')
    ax.legend(fontsize=8)
    ax.set_aspect('equal')

    # (b) Eigenvalue vs D
    ax = axes[1]
    ax.scatter([r['D'] for r in coex_valid],
               [r['lambda_1'] for r in coex_valid],
               c=[r['cue_gain'] for r in coex_valid], cmap='coolwarm',
               s=40, zorder=5, label='Coexistence')
    ax.scatter([r['D'] for r in stable_results],
               [r['lambda_1'] for r in stable_results],
               c=[r['cue_gain'] for r in stable_results], cmap='coolwarm',
               s=40, marker='s', zorder=4, label='WTA')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Eigenvalue vs Dominance\n(colored by cue_gain)', fontweight='bold')
    ax.legend(fontsize=8)
    plt.colorbar(plt.cm.ScalarMappable(
        norm=plt.Normalize(0, 0.5), cmap='coolwarm'),
        ax=ax, label='cue_gain', shrink=0.8)

    # (c) The bifurcation in D-space
    ax = axes[2]
    ax.plot(cg_coex := [r['cue_gain'] for r in coex_valid],
            [r['max_rA'] - r['max_rB'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='Coexistence: max(rA) - max(rB)')
    # For stable, need to recompute max
    for r in stable_results:
        r_A, r_B, _, _, _, _ = find_fixed_point_full(r['cue_gain'], N=N)
        r['max_rA'] = np.max(r_A)
        r['max_rB'] = np.max(r_B)
    ax.plot([r['cue_gain'] for r in stable_results],
            [r['max_rA'] - r['max_rB'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='WTA: max(rA) - max(rB)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Δ peak height')
    ax.set_title('Peak Height Difference\n(bump amplitude order parameter)',
                fontweight='bold')
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    N = 48

    print("=" * 70)
    print("SPECTRAL PORTRAIT — PART 4")
    print("The Coexistence Separatrix")
    print("=" * 70)

    # ── Step 1: Stable (WTA) branch for comparison ──
    print("\n[1/4] Computing stable (winner-take-all) branch...")
    cue_gains = np.concatenate([
        np.linspace(0.0, 0.005, 8),
        np.linspace(0.005, 0.03, 20),
        np.linspace(0.03, 0.1, 15),
        np.linspace(0.1, 0.5, 10),
    ])

    stable_results = []
    for cg in cue_gains:
        r_A, r_B, h_A, h_B, W, pref = find_fixed_point_full(cg, N=N)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, 0.5)
        evals = np.sort(np.linalg.eigvals(J).real)[::-1]
        stable_results.append({
            'cue_gain': cg,
            'lambda_1': evals[0],
            'D': np.mean(r_A) - np.mean(r_B),
            'mean_rA': np.mean(r_A),
            'mean_rB': np.mean(r_B),
        })

    # ── Step 2: Coexistence branch via Newton continuation ──
    print("\n[2/4] Newton continuation from coexistence state...")
    coex_gains = np.concatenate([
        np.linspace(0.0, 0.005, 8),
        np.linspace(0.005, 0.03, 20),
        np.linspace(0.03, 0.1, 15),
        np.linspace(0.1, 0.5, 10),
    ])
    coex_results = continuation_from_coexistence(coex_gains, N=N)

    # ── Step 3: Plot ──
    print("\n[3/4] Plotting coexistence bifurcation...")
    plot_coexistence_bifurcation(
        coex_results, stable_results,
        os.path.join(outdir, 'fig46_coexistence_bifurcation.png'), N=N)

    print("\n  Plotting coexistence profiles...")
    plot_coexistence_profiles(
        coex_results,
        os.path.join(outdir, 'fig47_coexistence_profiles.png'), N=N)

    print("\n[4/4] Plotting phase diagram...")
    plot_phase_diagram(
        coex_results, stable_results,
        os.path.join(outdir, 'fig48_phase_diagram.png'), N=N)

    print("\n" + "=" * 70)
    print("DONE. Three figures saved.")
    print("=" * 70)

    # ── Summary ──
    coex_valid = [r for r in coex_results if r is not None]
    print("\n── SUMMARY ──")
    print(f"  Coexistence solutions found: {len(coex_valid)}/{len(coex_results)}")
    if coex_valid:
        n_unstable = sum(1 for r in coex_valid if r['n_positive'] > 0)
        print(f"  Unstable (n_positive > 0): {n_unstable}")
        print(f"  λ₁ range: [{min(r['lambda_1'] for r in coex_valid):.6f}, "
              f"{max(r['lambda_1'] for r in coex_valid):.6f}]")
        print(f"  D range: [{min(r['D'] for r in coex_valid):.6f}, "
              f"{max(r['D'] for r in coex_valid):.6f}]")
        # Check if any have both bumps
        has_bumps = sum(1 for r in coex_valid
                       if r['max_rA'] > 0.5 and r['max_rB'] > 0.5)
        print(f"  States with both bumps (max > 0.5): {has_bumps}")
