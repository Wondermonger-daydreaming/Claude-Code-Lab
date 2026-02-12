"""
==========================================================================
SPECTRAL PORTRAIT — PART 5: THE SELF-SUSTAINING COEXISTENCE STATE
==========================================================================

Parts 3 & 4 failed to find the coexistence FP because:
  Part 3: Started from uniform activity → found homogeneous state
  Part 4: Drive removal collapsed the bumps → Newton jumped branches

New strategy:
  1. Find a SINGLE-RING self-sustaining bump (no external drive)
  2. Combine two bumps (at θ₁ and θ₂) as the two-ring initial guess
  3. Newton finds the coexistence FP directly
  4. Continue in cue_gain to track through the bifurcation

This should work because:
  - A single bump is self-sustaining with J_1=6.0 >> J_0=1.0
  - Two bumps can coexist if J_cross is small enough (0.5 << 6.0)
  - Newton doesn't care about stability; it finds the root

GLM 5's falsification tests are implemented:
  - Residual verification
  - Forward perturbation along unstable eigenvector
  - Time-reversal stability check
  - Branch continuity (smoothness of λ₁(cue))

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
# STEP 1: FIND SINGLE-RING SELF-SUSTAINING BUMP
# ═══════════════════════════════════════════════════════════════════

def find_single_ring_bump(theta_target, N=48, J_0=1.0, J_1=6.0,
                           r_max=1.0, beta=5.0, h0=0.5,
                           dt=0.1, tau=10.0, kappa=2.0, input_gain=5.0):
    """
    Find the self-sustaining bump of a SINGLE isolated ring.

    Strategy:
      1. Drive the ring with external input to establish a bump
      2. Remove the drive gradually
      3. Let the ring settle to its self-sustained state

    Returns the firing rate profile r(φ) of the self-sustained bump.
    """
    W, preferred = build_within_weights(N, J_0, J_1)

    # External drive to establish the bump
    drive = input_gain * tuning_curve(theta_target, preferred, kappa)

    # Initialize with drive
    r = sigmoid(W @ (drive * 0.3) + drive, r_max, beta, h0)

    # Phase 1: Converge with drive (500 steps)
    for step in range(500):
        h = W @ r + drive
        f = sigmoid(h, r_max, beta, h0)
        dr = (-r + f) * (dt / tau)
        r = np.maximum(0, r + dr)

    # Phase 2: Gradually remove drive (100 steps)
    for frac_step in range(100):
        frac = 1.0 - frac_step / 100.0
        h = W @ r + frac * drive
        f = sigmoid(h, r_max, beta, h0)
        dr = (-r + f) * (dt / tau)
        r = np.maximum(0, r + dr)

    # Phase 3: Converge without drive (2000 steps)
    for step in range(2000):
        h = W @ r
        f = sigmoid(h, r_max, beta, h0)
        dr = (-r + f) * (dt / tau)
        r = np.maximum(0, r + dr)
        if step > 100 and np.max(np.abs(dr)) < 1e-12:
            break

    return r, W, preferred


# ═══════════════════════════════════════════════════════════════════
# STEP 2: CONSTRUCT COEXISTENCE INITIAL GUESS
# ═══════════════════════════════════════════════════════════════════

def construct_coexistence_guess(N=48, J_0=1.0, J_1=6.0, J_cross=0.5,
                                 r_max=1.0, beta=5.0, h0=0.5, kappa=2.0,
                                 input_gain=5.0):
    """
    Construct the coexistence initial guess from two single-ring bumps.

    Strategy:
      1. Find single-ring self-sustaining bump at θ₁ (without cross-inhibition)
      2. Find single-ring self-sustaining bump at θ₂
      3. Combine them and adjust for cross-inhibition

    The adjustment: with cross-inhibition, each ring sees
    additional uniform inhibition -J_cross * mean(r_other).
    We iterate a few times to get self-consistency.
    """
    theta1, theta2 = np.pi / 4, -np.pi / 4

    r_A, W, preferred = find_single_ring_bump(
        theta1, N, J_0, J_1, r_max, beta, h0, kappa=kappa,
        input_gain=input_gain)
    r_B, _, _ = find_single_ring_bump(
        theta2, N, J_0, J_1, r_max, beta, h0, kappa=kappa,
        input_gain=input_gain)

    print(f"  Single-ring bump A: mean={np.mean(r_A):.4f}, max={np.max(r_A):.4f}")
    print(f"  Single-ring bump B: mean={np.mean(r_B):.4f}, max={np.max(r_B):.4f}")

    # Iterative adjustment for cross-inhibition
    for iteration in range(50):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        h_A = W @ r_A + cross_A
        h_B = W @ r_B + cross_B

        r_A_new = sigmoid(h_A, r_max, beta, h0)
        r_B_new = sigmoid(h_B, r_max, beta, h0)

        # Damped update
        alpha = 0.3
        r_A = (1 - alpha) * r_A + alpha * r_A_new
        r_B = (1 - alpha) * r_B + alpha * r_B_new

    print(f"  After cross-inhibition: "
          f"mean_A={np.mean(r_A):.4f}, mean_B={np.mean(r_B):.4f}, "
          f"D={np.mean(r_A)-np.mean(r_B):.6f}")
    print(f"  max_A={np.max(r_A):.4f}, max_B={np.max(r_B):.4f}")

    return r_A, r_B, W, preferred


# ═══════════════════════════════════════════════════════════════════
# STEP 3: NEWTON FOR THE COEXISTENCE FP
# ═══════════════════════════════════════════════════════════════════

def full_residual(x, W, cue_drive_A, J_cross, N,
                   r_max=1.0, beta=5.0, h0=0.5):
    """F(r) = -r + σ(h) for the full 2N system."""
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_drive_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([
        -r_A + sigmoid(h_A, r_max, beta, h0),
        -r_B + sigmoid(h_B, r_max, beta, h0),
    ])


def full_jacobian(x, W, cue_drive_A, J_cross, N,
                   r_max=1.0, beta=5.0, h0=0.5):
    """Analytical ∂F/∂r."""
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_drive_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    D_A = np.diag(sigmoid_derivative(h_A, r_max, beta, h0))
    D_B = np.diag(sigmoid_derivative(h_B, r_max, beta, h0))
    cross_m = np.full((N, N), -J_cross / N)
    J = np.zeros((2*N, 2*N))
    J[:N, :N] = -np.eye(N) + D_A @ W
    J[:N, N:] = D_A @ cross_m
    J[N:, :N] = D_B @ cross_m
    J[N:, N:] = -np.eye(N) + D_B @ W
    return J


def find_coexistence_fp(cue_gain, r_A_init, r_B_init, W, preferred,
                         N=48, J_cross=0.5, kappa=2.0,
                         r_max=1.0, beta=5.0, h0=0.5):
    """Find the coexistence fixed point using Newton from a good initial guess."""
    theta1 = np.pi / 4
    cue_drive_A = cue_gain * tuning_curve(theta1, preferred, kappa)

    x0 = np.concatenate([r_A_init, r_B_init])

    sol, info, ier, msg = fsolve(
        full_residual, x0,
        args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
        fprime=full_jacobian,
        full_output=True, maxfev=10000)

    res = np.max(np.abs(full_residual(
        sol, W, cue_drive_A, J_cross, N, r_max, beta, h0)))

    r_A, r_B = sol[:N], sol[N:]
    h_A = W @ r_A + cue_drive_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)

    return r_A, r_B, h_A, h_B, res, ier == 1 and res < 1e-6


def continuation_coexistence(cue_gains, N=48, J_0=1.0, J_1=6.0,
                              J_cross=0.5, kappa=2.0, input_gain=5.0):
    """
    Continuation of the coexistence branch.

    1. Construct initial guess from two single-ring bumps
    2. Newton at cue=0
    3. Continue in cue_gain using previous solution as guess
    """
    # Construct initial guess
    r_A_init, r_B_init, W, preferred = construct_coexistence_guess(
        N, J_0, J_1, J_cross, kappa=kappa, input_gain=input_gain)

    # Newton at cue=0
    theta1 = np.pi / 4
    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A_init, r_B_init])

    sol0, _, ier0, _ = fsolve(
        full_residual, x0,
        args=(W, cue_0, J_cross, N),
        fprime=full_jacobian,
        full_output=True, maxfev=10000)
    res0 = np.max(np.abs(full_residual(sol0, W, cue_0, J_cross, N)))
    print(f"  Newton at cue=0: residual={res0:.2e}, converged={ier0==1}")

    r_A_prev = sol0[:N]
    r_B_prev = sol0[N:]
    print(f"  Coexistence at cue=0: "
          f"mean_A={np.mean(r_A_prev):.4f}, mean_B={np.mean(r_B_prev):.4f}, "
          f"D={np.mean(r_A_prev)-np.mean(r_B_prev):.6f}")
    print(f"  max_A={np.max(r_A_prev):.4f}, max_B={np.max(r_B_prev):.4f}")

    # Check: is the cue=0 state actually a bump?
    has_bump = np.max(r_A_prev) > 0.3 and np.max(r_B_prev) > 0.3
    print(f"  Both bumps present: {has_bump}")

    results = []

    for cg in cue_gains:
        r_A, r_B, h_A, h_B, res, success = find_coexistence_fp(
            cg, r_A_prev, r_B_prev, W, preferred,
            N=N, J_cross=J_cross, kappa=kappa)

        if not success:
            print(f"  cue={cg:.4f}: FAILED (res={res:.2e})")
            results.append(None)
            # Don't update r_prev — keep trying from last good solution
            continue

        # Compute dynamical Jacobian (the /τ one)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals = evals[idx]
        evecs = evecs[:, idx]

        D = np.mean(r_A) - np.mean(r_B)
        n_pos = np.sum(evals.real > 0)

        # Eigenvector projections
        v1 = evecs[:, 0].real
        v1n = v1 / (np.linalg.norm(v1) + 1e-30)

        cos_p = np.cos(preferred - np.pi/4)
        d_cos = np.concatenate([cos_p, -cos_p])
        d_cos /= np.linalg.norm(d_cos)

        sin_p = np.sin(preferred - np.pi/4)
        d_sin = np.concatenate([sin_p, -sin_p])
        d_sin /= np.linalg.norm(d_sin)

        d_uni = np.concatenate([np.ones(N), -np.ones(N)])
        d_uni /= np.linalg.norm(d_uni)

        results.append({
            'cue_gain': cg,
            'r_A': r_A.copy(), 'r_B': r_B.copy(),
            'h_A': h_A.copy(), 'h_B': h_B.copy(),
            'eigenvalues': evals,
            'eigenvectors': evecs,
            'lambda_1': evals[0].real,
            'lambda_2': evals[1].real,
            'lambda_3': evals[2].real,
            'D': D, 'n_positive': n_pos,
            'max_rA': np.max(r_A), 'max_rB': np.max(r_B),
            'mean_rA': np.mean(r_A), 'mean_rB': np.mean(r_B),
            'proj_cos': abs(np.dot(v1n, d_cos)),
            'proj_sin': abs(np.dot(v1n, d_sin)),
            'proj_uni': abs(np.dot(v1n, d_uni)),
            'residual': res,
        })

        r_A_prev, r_B_prev = r_A, r_B  # Continue from this

        print(f"  cue={cg:.4f}: D={D:+.6f}, λ₁={evals[0].real:+.6f}, "
              f"n_pos={n_pos}, max(rA)={np.max(r_A):.3f}, max(rB)={np.max(r_B):.3f}, "
              f"|cos|={abs(np.dot(v1n, d_cos)):.3f}")

    return results, W, preferred


# ═══════════════════════════════════════════════════════════════════
# GLM 5's FALSIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════

def falsification_tests(coex_results, W, preferred, N=48, J_cross=0.5):
    """
    Implement GLM 5's tests for verifying the unstable equilibrium.

    Test 1: Residual quality (already checked)
    Test 3: Forward perturbation along unstable eigenvector
    Test 5: Time-reversal stability
    Test 4: Branch continuity
    """
    coex_valid = [r for r in coex_results if r is not None]
    if not coex_valid:
        print("  No valid solutions to test!")
        return {}

    test_results = {
        'perturbation': [],
        'time_reversal': [],
        'continuity': [],
    }

    for r in coex_valid:
        cg = r['cue_gain']
        cue_drive_A = cg * tuning_curve(np.pi/4, preferred, 2.0)

        # ── Test 3: Forward perturbation ──
        v1 = r['eigenvectors'][:, 0].real
        v1 /= np.linalg.norm(v1)
        delta = 1e-6

        x_star = np.concatenate([r['r_A'], r['r_B']])
        x_pert = x_star + delta * v1

        # One step of forward dynamics
        r_A_p, r_B_p = x_pert[:N], x_pert[N:]
        h_A_p = W @ r_A_p + cue_drive_A - J_cross * np.mean(r_B_p)
        h_B_p = W @ r_B_p - J_cross * np.mean(r_A_p)
        f_A = sigmoid(h_A_p)
        f_B = sigmoid(h_B_p)
        dx = np.concatenate([-r_A_p + f_A, -r_B_p + f_B])  # = τ * dr/dt

        # Alignment with eigenvector
        dx_norm = dx / (np.linalg.norm(dx) + 1e-30)
        alignment = abs(np.dot(dx_norm, v1))
        test_results['perturbation'].append({
            'cue_gain': cg, 'alignment': alignment,
            'expected_growth': r['lambda_1'] * delta,
            'actual_growth': np.dot(dx, v1) * delta,
        })

        # ── Test 5: Time-reversal stability ──
        # Under dx/dt = -F(x), run a few steps from x*
        x_rev = x_star.copy()
        stable_under_reversal = True
        for step in range(200):
            r_A_r, r_B_r = x_rev[:N], x_rev[N:]
            h_A_r = W @ r_A_r + cue_drive_A - J_cross * np.mean(r_B_r)
            h_B_r = W @ r_B_r - J_cross * np.mean(r_A_r)
            f_A_r = sigmoid(h_A_r)
            f_B_r = sigmoid(h_B_r)
            # REVERSE dynamics: dx/dt = -(-r + σ(h)) = r - σ(h)
            dx_rev = np.concatenate([r_A_r - f_A_r, r_B_r - f_B_r])
            x_rev = x_rev + 0.01 * dx_rev  # Small step

        dist_from_fp = np.linalg.norm(x_rev - x_star)
        test_results['time_reversal'].append({
            'cue_gain': cg,
            'distance_after_reversal': dist_from_fp,
            'returned_to_fp': dist_from_fp < 0.1,
        })

    # ── Test 4: Branch continuity ──
    if len(coex_valid) > 1:
        for i in range(len(coex_valid) - 1):
            dcue = coex_valid[i+1]['cue_gain'] - coex_valid[i]['cue_gain']
            if dcue > 0:
                dlambda = (coex_valid[i+1]['lambda_1'] - coex_valid[i]['lambda_1'])
                dD = (coex_valid[i+1]['D'] - coex_valid[i]['D'])
                test_results['continuity'].append({
                    'cue_range': (coex_valid[i]['cue_gain'],
                                  coex_valid[i+1]['cue_gain']),
                    'dlambda_dcue': dlambda / dcue if dcue > 0 else 0,
                    'dD_dcue': dD / dcue if dcue > 0 else 0,
                })

    return test_results


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_coexistence_and_tests(coex_results, stable_results, test_results,
                                save_path, N=48):
    """The comprehensive figure: bifurcation + falsification."""
    coex_valid = [r for r in coex_results if r is not None]
    if not coex_valid:
        print("  No coexistence solutions to plot!")
        return

    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(4, 3, figure=fig, hspace=0.45, wspace=0.35)

    cg_c = [r['cue_gain'] for r in coex_valid]
    cg_s = [r['cue_gain'] for r in stable_results]

    # ── Row 1: The Bifurcation ──

    # (a) Dominant eigenvalue
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(cg_c, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='Coexistence')
    ax.plot(cg_s, [r['lambda_1'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='WTA (stable)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue', fontweight='bold')
    ax.legend(fontsize=8)

    # (b) Dominance D
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(cg_c, [r['D'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='Coexistence')
    ax.plot(cg_s, [r['D'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='WTA')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance', fontweight='bold')
    ax.legend(fontsize=8)

    # (c) Top 3 eigenvalues
    ax = fig.add_subplot(gs[0, 2])
    ax.plot(cg_c, [r['lambda_1'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3, label='λ₁')
    ax.plot(cg_c, [r['lambda_2'] for r in coex_valid],
            's-', color=COLORS['dominance'], linewidth=1.5, markersize=2, label='λ₂')
    ax.plot(cg_c, [r['lambda_3'] for r in coex_valid],
            '^-', color=COLORS['network_A'], linewidth=1, markersize=2, label='λ₃')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 3 Eigenvalues (Coexistence)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── Row 2: Activity and Eigenvectors ──

    # Select 3 representative cue_gains
    cue_show = [0.0, 0.02, 0.1]
    for col, cg_target in enumerate(cue_show):
        matches = [r for r in coex_valid if abs(r['cue_gain'] - cg_target) < 0.015]
        if not matches:
            continue
        match = min(matches, key=lambda r: abs(r['cue_gain'] - cg_target))

        angles = np.linspace(-180, 180, N, endpoint=False)
        ax = fig.add_subplot(gs[1, col])
        ax.plot(angles, match['r_A'], '-', color=COLORS['network_A'],
                linewidth=2, label='r_A')
        ax.plot(angles, match['r_B'], '-', color=COLORS['network_B'],
                linewidth=2, label='r_B')

        # Overlay eigenvector (scaled)
        v1 = match['eigenvectors'][:, 0].real
        v_scale = 0.3 / (np.max(np.abs(v1)) + 1e-30)
        ax.plot(angles, 0.5 + v1[:N] * v_scale, '--', color=COLORS['network_A'],
                linewidth=1, alpha=0.5, label='v₁ (A)')
        ax.plot(angles, 0.5 + v1[N:] * v_scale, '--', color=COLORS['network_B'],
                linewidth=1, alpha=0.5, label='v₁ (B)')

        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel('Preferred angle (°)')
        ax.set_title(f'cue = {match["cue_gain"]:.3f}\n'
                    f'D = {match["D"]:.4f}, λ₁ = {match["lambda_1"]:.4f}\n'
                    f'n_pos = {match["n_positive"]}',
                    fontsize=9, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Firing rate / eigenvector')
            ax.legend(fontsize=6)

    # ── Row 3: Projections and Bump Heights ──

    ax = fig.add_subplot(gs[2, 0])
    ax.plot(cg_c, [r['proj_cos'] for r in coex_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=4,
            label='|⟨v₁, d_cos⟩|')
    ax.plot(cg_c, [r['proj_sin'] for r in coex_valid],
            '^-', color=COLORS['dominance'], linewidth=1.5, markersize=3,
            label='|⟨v₁, d_sin⟩|')
    ax.plot(cg_c, [r['proj_uni'] for r in coex_valid],
            's--', color=COLORS['bulk'], linewidth=1, markersize=3,
            label='|⟨v₁, d_uni⟩|')
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('|Projection|')
    ax.set_ylim(-0.05, 1.05)
    ax.set_title('Eigenvector Projections', fontweight='bold')
    ax.legend(fontsize=7)

    ax = fig.add_subplot(gs[2, 1])
    ax.plot(cg_c, [r['max_rA'] for r in coex_valid],
            'o-', color=COLORS['network_A'], linewidth=2, markersize=4,
            label='max(r_A)')
    ax.plot(cg_c, [r['max_rB'] for r in coex_valid],
            'o-', color=COLORS['network_B'], linewidth=2, markersize=4,
            label='max(r_B)')
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Peak firing rate')
    ax.set_title('Bump Heights', fontweight='bold')
    ax.legend(fontsize=8)

    # Instability index
    ax = fig.add_subplot(gs[2, 2])
    ax.plot(cg_c, [r['n_positive'] for r in coex_valid],
            'o-', color=COLORS['dominance'], linewidth=2, markersize=5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, lw=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('# positive eigenvalues')
    ax.set_title('Instability Index', fontweight='bold')

    # ── Row 4: Falsification Tests ──

    # (a) Perturbation alignment
    if test_results.get('perturbation'):
        ax = fig.add_subplot(gs[3, 0])
        pt = test_results['perturbation']
        ax.bar([f'{p["cue_gain"]:.3f}' for p in pt],
               [p['alignment'] for p in pt],
               color=COLORS['critical'], alpha=0.7)
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.4,
                   label='perfect alignment')
        ax.set_xlabel('cue_gain')
        ax.set_ylabel('|v₁ · dx/dt|')
        ax.set_title('Test 3: Perturbation Alignment\n'
                    '(should be ≈ 1 for genuine saddle)',
                    fontsize=9, fontweight='bold')
        ax.set_ylim(0, 1.1)
        ax.tick_params(axis='x', rotation=45, labelsize=7)

    # (b) Time-reversal
    if test_results.get('time_reversal'):
        ax = fig.add_subplot(gs[3, 1])
        tr = test_results['time_reversal']
        colors = ['green' if t['returned_to_fp'] else 'red' for t in tr]
        ax.bar([f'{t["cue_gain"]:.3f}' for t in tr],
               [t['distance_after_reversal'] for t in tr],
               color=colors, alpha=0.7)
        ax.axhline(y=0.1, color='gray', linestyle='--', alpha=0.4,
                   label='threshold')
        ax.set_xlabel('cue_gain')
        ax.set_ylabel('||x_reversed - x*||')
        ax.set_title('Test 5: Time-Reversal Stability\n'
                    '(green = returned to FP)',
                    fontsize=9, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=7)

    # (c) Branch continuity
    if test_results.get('continuity'):
        ax = fig.add_subplot(gs[3, 2])
        ct = test_results['continuity']
        mid_cues = [(c['cue_range'][0] + c['cue_range'][1]) / 2 for c in ct]
        ax.plot(mid_cues, [c['dlambda_dcue'] for c in ct],
                'o-', color=COLORS['critical'], linewidth=2, markersize=4,
                label='dλ₁/d(cue)')
        ax.plot(mid_cues, [c['dD_dcue'] for c in ct],
                's-', color=COLORS['stable'], linewidth=2, markersize=4,
                label='dD/d(cue)')
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
        ax.set_xlabel('cue_gain')
        ax.set_ylabel('Derivative')
        ax.set_title('Test 4: Branch Continuity\n'
                    '(smooth = genuine branch)',
                    fontsize=9, fontweight='bold')
        ax.legend(fontsize=8)

    fig.suptitle('The Coexistence Separatrix + GLM 5 Falsification Tests\n'
                 'Self-sustaining bumps → Newton → spectral bifurcation → verification',
                 fontsize=14, fontweight='bold', y=1.01)
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
    print("SPECTRAL PORTRAIT — PART 5")
    print("The Self-Sustaining Coexistence State")
    print("=" * 70)

    # ── Stable branch ──
    print("\n[1/3] Computing stable (WTA) branch...")
    cue_gains = np.concatenate([
        np.linspace(0.0, 0.005, 6),
        np.linspace(0.005, 0.03, 15),
        np.linspace(0.03, 0.1, 10),
        np.linspace(0.1, 0.5, 8),
    ])

    stable_results = []
    for cg in cue_gains:
        r_A, r_B, h_A, h_B, W, pref = find_fixed_point_full(cg, N=N)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, 0.5)
        evals = np.sort(np.linalg.eigvals(J).real)[::-1]
        stable_results.append({
            'cue_gain': cg, 'lambda_1': evals[0],
            'D': np.mean(r_A) - np.mean(r_B),
            'mean_rA': np.mean(r_A), 'mean_rB': np.mean(r_B),
        })

    # ── Coexistence branch ──
    print("\n[2/3] Newton continuation from self-sustaining coexistence...")
    coex_gains = np.concatenate([
        np.linspace(0.0, 0.005, 6),
        np.linspace(0.005, 0.03, 15),
        np.linspace(0.03, 0.1, 10),
        np.linspace(0.1, 0.5, 8),
    ])
    coex_results, W_coex, pref_coex = continuation_coexistence(
        coex_gains, N=N)

    # ── Falsification tests ──
    print("\n[3/3] Running GLM 5's falsification tests...")
    test_results = falsification_tests(coex_results, W_coex, pref_coex, N=N)

    # Print test summaries
    if test_results.get('perturbation'):
        print("\n  Perturbation alignment:")
        for p in test_results['perturbation']:
            print(f"    cue={p['cue_gain']:.3f}: alignment={p['alignment']:.4f}")
    if test_results.get('time_reversal'):
        print("\n  Time-reversal stability:")
        for t in test_results['time_reversal']:
            status = "✓ PASSED" if t['returned_to_fp'] else "✗ FAILED"
            print(f"    cue={t['cue_gain']:.3f}: dist={t['distance_after_reversal']:.4f} {status}")

    # ── Plot ──
    print("\n  Plotting...")
    plot_coexistence_and_tests(
        coex_results, stable_results, test_results,
        os.path.join(outdir, 'fig49_coexistence_with_tests.png'), N=N)

    print("\n" + "=" * 70)
    print("DONE.")
    print("=" * 70)

    # Summary
    coex_valid = [r for r in coex_results if r is not None]
    print(f"\n  Solutions found: {len(coex_valid)}/{len(coex_results)}")
    if coex_valid:
        has_bumps = sum(1 for r in coex_valid
                       if r['max_rA'] > 0.3 and r['max_rB'] > 0.3)
        n_unstable = sum(1 for r in coex_valid if r['n_positive'] > 0)
        print(f"  Both bumps present: {has_bumps}")
        print(f"  Unstable: {n_unstable}")
        print(f"  λ₁ range: [{min(r['lambda_1'] for r in coex_valid):.6f}, "
              f"{max(r['lambda_1'] for r in coex_valid):.6f}]")
        print(f"  D range: [{min(r['D'] for r in coex_valid):.6f}, "
              f"{max(r['D'] for r in coex_valid):.6f}]")
