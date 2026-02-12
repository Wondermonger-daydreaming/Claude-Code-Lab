"""
==========================================================================
SPECTRAL PORTRAIT — PART 3: NEWTON'S METHOD AND THE TRUE BIFURCATION
==========================================================================

The missing piece: forward simulation cannot hold an unstable fixed point.
But Newton's method CAN find it — it solves F(r) = 0 algebraically,
indifferent to stability.

This script:

  1. NEWTON'S METHOD FOR THE UNSTABLE FIXED POINT
     Solve the 96D root-finding problem:
       F_i^A = -r_i^A + σ(h_i^A) = 0
       F_i^B = -r_i^B + σ(h_i^B) = 0
     with initial guess from the symmetric/coexistence state.
     This finds the UNSTABLE equilibrium that forward simulation can't hold.

  2. THE TRUE EIGENVALUE CROSSING
     Track the dominant eigenvalue of the unstable FP's Jacobian.
     It should be POSITIVE — that's what makes it unstable.
     Track it alongside the stable FP's eigenvalue.
     Where they meet (or were born from the same state) = the bifurcation.

  3. BIFURCATION PORTRAIT: BOTH FIXED POINTS
     The complete picture: two branches of fixed points, one stable,
     one unstable. The separatrix is the unstable manifold.

  4. BBP vs BIFURCATION (addressing GLM 5's blind spot #6)
     BBP: "when does a signal eigenvalue EMERGE from noise?"
     Bifurcation: "when does an equilibrium's eigenvalue CROSS zero?"
     Same geometry (threshold behavior). Different mechanism.
     We compute both and overlay them.

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

# Import shared infrastructure
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
# 1. THE FULL-SYSTEM ROOT-FINDING PROBLEM
# ═══════════════════════════════════════════════════════════════════

def full_system_residual(x, W, cue_drive_A, J_cross, N,
                          r_max=1.0, beta=5.0, h0=0.5):
    """
    Residual F(r) = -r + σ(h) for the full 2N system.

    At a fixed point, F(r) = 0.

    x = [r_A_0, ..., r_A_{N-1}, r_B_0, ..., r_B_{N-1}]
    """
    r_A = x[:N]
    r_B = x[N:]

    # Input currents
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)

    h_A = W @ r_A + cue_drive_A + cross_A
    h_B = W @ r_B + cross_B

    f_A = sigmoid(h_A, r_max, beta, h0)
    f_B = sigmoid(h_B, r_max, beta, h0)

    # F(r) = -r + σ(h) = 0 at fixed point
    residual = np.concatenate([
        -r_A + f_A,
        -r_B + f_B,
    ])
    return residual


def full_system_jacobian_for_rootfinding(x, W, cue_drive_A, J_cross, N,
                                          r_max=1.0, beta=5.0, h0=0.5):
    """
    Analytical Jacobian of F(r) = -r + σ(h) for root-finding.

    This is NOT the dynamical Jacobian (which is F/τ).
    This is ∂F/∂r for the root-finding problem.

    ∂F_A/∂r_A = -I + diag(σ'(h_A)) · W
    ∂F_A/∂r_B = diag(σ'(h_A)) · (-J_cross/N) · 1·1^T
    etc.
    """
    r_A = x[:N]
    r_B = x[N:]

    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)

    h_A = W @ r_A + cue_drive_A + cross_A
    h_B = W @ r_B + cross_B

    sigma_prime_A = sigmoid_derivative(h_A, r_max, beta, h0)
    sigma_prime_B = sigmoid_derivative(h_B, r_max, beta, h0)

    D_A = np.diag(sigma_prime_A)
    D_B = np.diag(sigma_prime_B)

    cross_mat = np.full((N, N), -J_cross / N)

    J = np.zeros((2 * N, 2 * N))
    J[:N, :N] = -np.eye(N) + D_A @ W
    J[:N, N:] = D_A @ cross_mat
    J[N:, :N] = D_B @ cross_mat
    J[N:, N:] = -np.eye(N) + D_B @ W

    return J


def find_unstable_fp_newton(cue_gain, N=48, J_0=1.0, J_1=6.0,
                             J_cross=0.5, kappa=2.0, input_gain=5.0,
                             r_max=1.0, beta=5.0, h0=0.5):
    """
    Find the UNSTABLE fixed point using Newton's method (scipy.fsolve).

    Strategy: Start from a nearly-symmetric initial guess where both
    networks have similar activity. For small cue_gain, this should
    be close to the coexistence state (both bumps present).

    The key trick: use the solution at a slightly smaller cue_gain
    as the initial guess for the next one (continuation method).
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    # Cue drive (only to network A)
    cue_drive_A = cue_gain * tuning_curve(theta1, preferred, kappa)

    # Initial guess: symmetric coexistence state
    # Both networks have bumps, but equal total activity
    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)

    # Start from the average of both drives
    h_init_A = W @ (drive_A * 0.3) + drive_A * 0.5 + cue_drive_A * 0.3
    h_init_B = W @ (drive_B * 0.3) + drive_B * 0.5
    r_A_init = sigmoid(h_init_A, r_max, beta, h0)
    r_B_init = sigmoid(h_init_B, r_max, beta, h0)

    # Make initial activities similar (push toward symmetry)
    r_avg = (r_A_init + r_B_init) / 2.0
    r_A_init = 0.7 * r_A_init + 0.3 * r_avg
    r_B_init = 0.7 * r_B_init + 0.3 * r_avg

    x0 = np.concatenate([r_A_init, r_B_init])

    # Solve with analytical Jacobian
    sol, info, ier, msg = fsolve(
        full_system_residual, x0,
        args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
        fprime=full_system_jacobian_for_rootfinding,
        full_output=True,
        maxfev=5000,
    )

    r_A_sol = sol[:N]
    r_B_sol = sol[N:]

    # Compute residual quality
    res = full_system_residual(sol, W, cue_drive_A, J_cross, N, r_max, beta, h0)
    max_residual = np.max(np.abs(res))

    # Compute h at solution
    cross_A = -J_cross * np.mean(r_B_sol)
    cross_B = -J_cross * np.mean(r_A_sol)
    h_A = W @ r_A_sol + cue_drive_A + cross_A
    h_B = W @ r_B_sol + cross_B

    success = ier == 1 and max_residual < 1e-6

    return r_A_sol, r_B_sol, h_A, h_B, W, preferred, max_residual, success


def find_unstable_fp_continuation(cue_gains, N=48, J_0=1.0, J_1=6.0,
                                   J_cross=0.5, kappa=2.0, input_gain=5.0,
                                   r_max=1.0, beta=5.0, h0=0.5):
    """
    Continuation method: find the unstable FP by starting at cue=0
    (where the system is symmetric) and tracking the solution as
    cue_gain increases.

    At cue=0, both networks are identical → the symmetric state IS
    a fixed point. As cue increases, we follow this branch even
    when it becomes unstable.
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    results = []

    # Start at cue=0: find the symmetric fixed point
    # At cue=0, both networks should have identical bumps
    drive = input_gain * tuning_curve(theta1, preferred, kappa)
    h_init = W @ (drive * 0.3) + drive * 0.5
    r_init = sigmoid(h_init, r_max, beta, h0)

    # Simulate the single-network to convergence (both are identical at cue=0)
    r = r_init.copy()
    for step in range(5000):
        cross = -J_cross * np.mean(r)
        h = W @ r + cross
        f = sigmoid(h, r_max, beta, h0)
        dr = -r + f
        r = np.maximum(0, r + 0.05 * dr)
        if np.max(np.abs(dr)) < 1e-12:
            break

    # This is the base state: both networks at r
    x_prev = np.concatenate([r, r])

    for cg in cue_gains:
        cue_drive_A = cg * tuning_curve(theta1, preferred, kappa)

        # Try multiple strategies for initial guess
        solutions = []
        residuals = []

        # Strategy 1: Continue from previous solution
        sol1, info1, ier1, _ = fsolve(
            full_system_residual, x_prev,
            args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
            fprime=full_system_jacobian_for_rootfinding,
            full_output=True, maxfev=5000)
        res1 = np.max(np.abs(full_system_residual(
            sol1, W, cue_drive_A, J_cross, N, r_max, beta, h0)))
        if res1 < 1e-6:
            solutions.append(sol1)
            residuals.append(res1)

        # Strategy 2: Symmetrized initial guess
        r_avg = (x_prev[:N] + x_prev[N:]) / 2.0
        x_sym = np.concatenate([r_avg, r_avg])
        sol2, info2, ier2, _ = fsolve(
            full_system_residual, x_sym,
            args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
            fprime=full_system_jacobian_for_rootfinding,
            full_output=True, maxfev=5000)
        res2 = np.max(np.abs(full_system_residual(
            sol2, W, cue_drive_A, J_cross, N, r_max, beta, h0)))
        if res2 < 1e-6:
            solutions.append(sol2)
            residuals.append(res2)

        # Strategy 3: scipy.optimize.root with Krylov method
        result3 = root(
            full_system_residual, x_prev,
            args=(W, cue_drive_A, J_cross, N, r_max, beta, h0),
            method='hybr',
            jac=full_system_jacobian_for_rootfinding,
            options={'maxfev': 5000})
        if result3.success:
            res3 = np.max(np.abs(result3.fun))
            if res3 < 1e-6:
                solutions.append(result3.x)
                residuals.append(res3)

        if not solutions:
            print(f"  cue={cg:.4f}: NO SOLUTION FOUND")
            results.append(None)
            continue

        # Among solutions, find the one CLOSEST to symmetric (smallest |D|)
        best_sol = None
        best_D = float('inf')
        for sol in solutions:
            r_A = sol[:N]
            r_B = sol[N:]
            D = abs(np.mean(r_A) - np.mean(r_B))
            if D < best_D:
                best_D = D
                best_sol = sol

        # Also find the one FARTHEST from symmetric (the stable A-dominant)
        # We want BOTH for comparison
        worst_sol = None
        worst_D = -1
        for sol in solutions:
            r_A = sol[:N]
            r_B = sol[N:]
            D = abs(np.mean(r_A) - np.mean(r_B))
            if D > worst_D:
                worst_D = D
                worst_sol = sol

        r_A = best_sol[:N]
        r_B = best_sol[N:]
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + cue_drive_A + cross_A
        h_B = W @ r_B + cross_B

        # Compute Jacobian eigenvalues
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals = np.sort(np.linalg.eigvals(J).real)[::-1]

        D_val = np.mean(r_A) - np.mean(r_B)
        n_positive = np.sum(evals > 0)

        results.append({
            'cue_gain': cg,
            'r_A': r_A, 'r_B': r_B,
            'h_A': h_A, 'h_B': h_B,
            'eigenvalues': evals,
            'lambda_1': evals[0],
            'lambda_2': evals[1],
            'lambda_3': evals[2],
            'D': D_val,
            'n_positive': n_positive,
            'mean_rA': np.mean(r_A),
            'mean_rB': np.mean(r_B),
        })

        x_prev = best_sol  # Continue from this solution

        print(f"  cue={cg:.4f}: D={D_val:+.4f}, "
              f"λ₁={evals[0]:.6f}, n_pos={n_positive}")

    return results


# ═══════════════════════════════════════════════════════════════════
# 2. BBP PHASE TRANSITION — THE DETECTION PROBLEM
# ═══════════════════════════════════════════════════════════════════

def bbp_eigenvalue_emergence(signal_strengths, gamma=0.5, N=200, n_trials=20):
    """
    BBP transition: when does a planted signal emerge from the noise spectrum?

    Spiked covariance model: Σ = I + θ · v·v^T
    Sample N observations from N(0, Σ), compute sample covariance.

    The BBP threshold: θ_c = √γ (where γ = p/n ratio).
    Below θ_c: the top eigenvalue stays at the MP bulk edge (1+√γ)².
    Above θ_c: it detaches as θ + 1 + γ/θ.

    This is a DETECTION problem: can you tell there's a signal?
    """
    p = N
    n = int(p / gamma)

    results = []
    for theta in signal_strengths:
        top_eigs = []
        for trial in range(n_trials):
            # Plant a rank-1 signal
            v = np.random.randn(p)
            v /= np.linalg.norm(v)

            # Generate data: X = Z · Σ^{1/2}
            # Σ^{1/2} = I + (√(1+θ) - 1) · v·v^T
            Z = np.random.randn(n, p)
            X = Z + np.sqrt(theta) * (Z @ v[:, np.newaxis]) @ v[np.newaxis, :]

            # Sample covariance
            S = X.T @ X / n
            evals = np.linalg.eigvalsh(S)
            top_eigs.append(evals[-1])

        results.append({
            'theta': theta,
            'top_eig_mean': np.mean(top_eigs),
            'top_eig_std': np.std(top_eigs),
        })

    return results


# ═══════════════════════════════════════════════════════════════════
# 3. PLOTTING: THE TRUE BIFURCATION
# ═══════════════════════════════════════════════════════════════════

def plot_true_bifurcation(continuation_results, stable_results, save_path, N=48):
    """
    The money plot: both fixed point branches with their eigenvalues.

    Shows:
    (a) Dominant eigenvalue — unstable FP (λ₁ > 0) vs stable FP (λ₁ < 0)
    (b) Dominance D — the bifurcation diagram in the order parameter
    (c) Number of unstable directions — how many eigenvalues are positive
    (d) The top 3 eigenvalues of the continuation branch
    """
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

    # Filter out None results
    cont_valid = [r for r in continuation_results if r is not None]
    cg_cont = [r['cue_gain'] for r in cont_valid]

    # ── (a) Dominant eigenvalue: both branches ──
    ax = fig.add_subplot(gs[0, 0])
    ax.plot(cg_cont, [r['lambda_1'] for r in cont_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁ (Newton/continuation)')
    ax.plot([r['cue_gain'] for r in stable_results],
            [r['lambda_1'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='λ₁ (stable FP)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁)')
    ax.set_title('Dominant Eigenvalue\nNewton-Found FP vs Stable FP',
                fontweight='bold')
    ax.legend(fontsize=9)
    ax.annotate('bifurcation?', xy=(0.02, 0), fontsize=8,
               color=COLORS['cliff'], ha='center', va='bottom',
               xytext=(0.06, 0.01),
               arrowprops=dict(arrowstyle='->', color=COLORS['cliff'], lw=1))

    # ── (b) Dominance D: the order parameter ──
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(cg_cont, [r['D'] for r in cont_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='Newton/continuation')
    ax.plot([r['cue_gain'] for r in stable_results],
            [r['D'] for r in stable_results],
            's-', color=COLORS['stable'], linewidth=2, markersize=3,
            label='Stable FP')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance Variable\n(Order Parameter)', fontweight='bold')
    ax.legend(fontsize=9)

    # ── (c) Instability index ──
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(cg_cont, [r['n_positive'] for r in cont_valid],
            'o-', color=COLORS['dominance'], linewidth=2, markersize=4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('# positive eigenvalues')
    ax.set_title('Instability Index\n(Newton/continuation FP)',
                fontweight='bold')
    ax.set_ylim(-0.5, max([r['n_positive'] for r in cont_valid]) + 1.5)

    # ── (d) Top 3 eigenvalues of continuation branch ──
    ax = fig.add_subplot(gs[1, 1])
    ax.plot(cg_cont, [r['lambda_1'] for r in cont_valid],
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁')
    ax.plot(cg_cont, [r['lambda_2'] for r in cont_valid],
            's-', color=COLORS['dominance'], linewidth=1.5, markersize=2,
            label='λ₂')
    ax.plot(cg_cont, [r['lambda_3'] for r in cont_valid],
            '^-', color=COLORS['network_A'], linewidth=1, markersize=2,
            label='λ₃')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5)
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 3 Eigenvalues\n(Newton/continuation branch)',
                fontweight='bold')
    ax.legend(fontsize=9)

    fig.suptitle('The True Bifurcation: Newton\'s Method Finds What Simulation Cannot\n'
                 'Unstable fixed points and the spectral separatrix',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


def plot_bbp_vs_bifurcation(continuation_results, save_path, gamma=0.5):
    """
    GLM 5's blind spot #6: BBP transition vs bifurcation.

    BBP: detection — "when does a signal emerge from noise?"
       Threshold: θ_c = √γ
       Observable: top eigenvalue of sample covariance

    Bifurcation: dynamics — "when does an equilibrium split?"
       Threshold: cue_c ≈ 0.02 (empirical)
       Observable: sign change of dominant Jacobian eigenvalue

    Same geometry (threshold → detachment). Different mechanism.
    We overlay both to show the parallel and the distinction.
    """
    # Compute BBP
    theta_c = np.sqrt(gamma)
    mp_edge = (1 + np.sqrt(gamma))**2

    signal_strengths = np.linspace(0, 3.0, 40)
    print("  Computing BBP transition...")
    bbp_results = bbp_eigenvalue_emergence(signal_strengths, gamma=gamma)

    # Theoretical BBP curve
    theta_theory = np.linspace(theta_c, 3.0, 100)
    bbp_theory = theta_theory + 1 + gamma / theta_theory

    # Get continuation results
    cont_valid = [r for r in continuation_results if r is not None]
    cg_cont = np.array([r['cue_gain'] for r in cont_valid])
    lambda_cont = np.array([r['lambda_1'] for r in cont_valid])

    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    # ── (a) BBP transition ──
    ax = axes[0]
    thetas = [r['theta'] for r in bbp_results]
    means = [r['top_eig_mean'] for r in bbp_results]
    stds = [r['top_eig_std'] for r in bbp_results]
    ax.errorbar(thetas, means, yerr=stds, fmt='o', color=COLORS['stable'],
                markersize=4, capsize=2, alpha=0.7, label='empirical top eigenvalue')
    ax.plot(theta_theory, bbp_theory, '-', color=COLORS['critical'],
            linewidth=2, label='BBP: θ + 1 + γ/θ')
    ax.axhline(y=mp_edge, color=COLORS['bulk'], linestyle='--', alpha=0.6,
               linewidth=1.5, label=f'MP edge: (1+√γ)² = {mp_edge:.2f}')
    ax.axvline(x=theta_c, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label=f'θ_c = √γ = {theta_c:.2f}')
    ax.set_xlabel('Signal strength θ')
    ax.set_ylabel('Top eigenvalue of sample covariance')
    ax.set_title('BBP Phase Transition\n(DETECTION: signal emerges from noise)',
                fontweight='bold')
    ax.legend(fontsize=7, loc='upper left')

    # ── (b) Bifurcation transition ──
    ax = axes[1]
    ax.plot(cg_cont, lambda_cont,
            'o-', color=COLORS['critical'], linewidth=2, markersize=3,
            label='λ₁ (continuation branch)')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='behavioral cliff ≈ 0.02')
    # Shade the unstable region
    ax.fill_between(cg_cont[lambda_cont > 0],
                     0, lambda_cont[lambda_cont > 0],
                     color=COLORS['critical'], alpha=0.15, label='unstable (λ₁ > 0)')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ₁) of Jacobian')
    ax.set_title('Bifurcation Transition\n(DYNAMICS: equilibrium loses stability)',
                fontweight='bold')
    ax.legend(fontsize=7)

    # ── (c) Geometric comparison ──
    ax = axes[2]
    # Normalize both to show the shared geometry
    # BBP: deviation from bulk edge
    bbp_dev = np.array(means) - mp_edge
    bbp_dev_norm = bbp_dev / max(abs(bbp_dev.max()), 1e-6)
    theta_norm = np.array(thetas) / theta_c  # Normalize by critical value

    # Bifurcation: just the eigenvalue itself (already has zero-crossing)
    # Normalize cue_gain by approximate critical value
    cue_c_approx = 0.015  # Where eigenvalue approaches zero
    cg_norm = cg_cont / cue_c_approx if cue_c_approx > 0 else cg_cont

    ax.plot(theta_norm, bbp_dev_norm, 'o-', color=COLORS['stable'],
            linewidth=2, markersize=3, alpha=0.7,
            label='BBP: (top eig - MP edge), normalized')
    ax.plot(cg_norm, lambda_cont / max(abs(lambda_cont.max()), 1e-6),
            's-', color=COLORS['critical'],
            linewidth=2, markersize=3, alpha=0.7,
            label='Bifurcation: λ₁, normalized')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=1.0, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='critical threshold (= 1)')
    ax.set_xlabel('Control parameter / critical value')
    ax.set_ylabel('Normalized observable')
    ax.set_title('Geometric Comparison\n(Same threshold behavior, different mechanism)',
                fontweight='bold')
    ax.legend(fontsize=7)
    ax.set_xlim(-0.2, 4)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# 4. ACTIVITY PROFILES AT THE UNSTABLE FP
# ═══════════════════════════════════════════════════════════════════

def plot_activity_profiles(continuation_results, stable_results, save_path, N=48):
    """
    Compare the activity profiles (r_A, r_B) at the unstable vs stable FPs.

    At the unstable FP: both networks should have similar activity.
    At the stable FP: one network dominates.
    """
    # Select a few cue_gain values
    cue_targets = [0.0, 0.01, 0.02, 0.05, 0.1]
    angles = np.linspace(-180, 180, N, endpoint=False)

    fig, axes = plt.subplots(2, len(cue_targets), figsize=(3.5 * len(cue_targets), 7))

    for col, cg_target in enumerate(cue_targets):
        # Find closest continuation result
        cont_valid = [r for r in continuation_results if r is not None]
        cont_match = min(cont_valid, key=lambda r: abs(r['cue_gain'] - cg_target))

        # Find closest stable result
        stable_match = min(stable_results, key=lambda r: abs(r['cue_gain'] - cg_target))

        # Top row: Newton/continuation (hopefully unstable)
        ax = axes[0, col]
        ax.plot(angles, cont_match['r_A'], '-', color=COLORS['network_A'],
                linewidth=2, label='r_A')
        ax.plot(angles, cont_match['r_B'], '-', color=COLORS['network_B'],
                linewidth=2, label='r_B')
        ax.set_title(f'cue = {cont_match["cue_gain"]:.3f}\n'
                    f'D = {cont_match["D"]:.3f}, '
                    f'λ₁ = {cont_match["lambda_1"]:.4f}',
                    fontsize=9, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        if col == 0:
            ax.set_ylabel('Newton/Continuation')
            ax.legend(fontsize=7)

        # Bottom row: stable FP
        ax = axes[1, col]
        # Need to get r_A, r_B for stable results
        # Re-compute since stable_results may not store them
        r_A_s, r_B_s, h_A_s, h_B_s, W_s, pref_s = find_fixed_point_full(
            stable_match['cue_gain'], N=N)
        ax.plot(angles, r_A_s, '-', color=COLORS['network_A'],
                linewidth=2, label='r_A')
        ax.plot(angles, r_B_s, '-', color=COLORS['network_B'],
                linewidth=2, label='r_B')
        ax.set_title(f'D = {stable_match["D"]:.3f}, '
                    f'λ₁ = {stable_match["lambda_1"]:.4f}',
                    fontsize=9, fontweight='bold')
        ax.set_ylim(-0.05, 1.05)
        ax.set_xlabel('Preferred angle (°)')
        if col == 0:
            ax.set_ylabel('Stable FP')
            ax.legend(fontsize=7)

    fig.suptitle('Activity Profiles: Unstable (Newton) vs Stable Fixed Points\n'
                 'The unstable FP is the coexistence state; the stable FP is the winner-take-all',
                 fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# 5. THE CRITICAL EIGENVECTOR AT THE UNSTABLE FP
# ═══════════════════════════════════════════════════════════════════

def plot_critical_eigenvector_unstable(continuation_results, save_path, N=48):
    """
    The critical eigenvector of the UNSTABLE fixed point.

    This is the direction along which the system WANTS to move —
    the direction of symmetry-breaking. It should look like
    "Network A up, Network B down" = the dominance mode.

    THIS is where the cosine projection should be large.
    """
    cont_valid = [r for r in continuation_results if r is not None]
    # Select a few points
    cue_targets = [0.0, 0.005, 0.01, 0.02, 0.05]
    angles = np.linspace(-180, 180, N, endpoint=False)

    fig, axes = plt.subplots(2, len(cue_targets),
                             figsize=(3.5 * len(cue_targets), 7))

    W, preferred = build_within_weights(N, 1.0, 6.0)
    theta_target = np.pi / 4

    for col, cg_target in enumerate(cue_targets):
        match = min(cont_valid, key=lambda r: abs(r['cue_gain'] - cg_target))

        # Compute eigenvectors
        J = compute_full_jacobian(match['r_A'], match['r_B'],
                                  match['h_A'], match['h_B'], W, 0.5)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals = evals[idx]
        evecs = evecs[:, idx]

        v1 = evecs[:, 0].real
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-30)

        # Projection directions
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

        # Top row: eigenvector shape
        ax = axes[0, col]
        norm = np.max(np.abs(v1)) + 1e-30
        ax.plot(angles, v1[:N] / norm, '-', color=COLORS['network_A'],
                linewidth=2, label='v₁ (Net A)')
        ax.plot(angles, v1[N:] / norm, '-', color=COLORS['network_B'],
                linewidth=2, label='v₁ (Net B)')
        ax.axhline(y=0, color='gray', alpha=0.3)
        ax.set_title(f'cue = {match["cue_gain"]:.3f}\n'
                    f'λ₁ = {evals[0].real:.4f}',
                    fontsize=9, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Eigenvector component')
            ax.legend(fontsize=7)

        # Bottom row: projection summary
        ax = axes[1, col]
        bars = ax.bar(['cos', 'sin', 'uniform'],
                      [proj_cos, proj_sin, proj_uni],
                      color=[COLORS['critical'], COLORS['dominance'],
                             COLORS['bulk']])
        ax.set_ylim(0, 1.1)
        ax.set_title(f'|⟨v₁, d_cos⟩| = {proj_cos:.3f}\n'
                    f'|⟨v₁, d_sin⟩| = {proj_sin:.3f}',
                    fontsize=8)
        ax.set_xlabel('Projection direction')
        if col == 0:
            ax.set_ylabel('|Projection|')

    fig.suptitle('Critical Eigenvector at the UNSTABLE Fixed Point\n'
                 'This is the symmetry-breaking direction — '
                 'the mode that DRIVES the bifurcation',
                 fontsize=12, fontweight='bold', y=1.02)
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
    print("SPECTRAL PORTRAIT — PART 3")
    print("Newton's Method and the True Bifurcation")
    print("=" * 70)

    # ── Step 1: Find stable FP branch (for comparison) ────────────
    print("\n[1/5] Computing stable FP branch...")
    cue_gains_dense = np.concatenate([
        np.linspace(0.0, 0.005, 8),
        np.linspace(0.005, 0.03, 20),
        np.linspace(0.03, 0.1, 15),
        np.linspace(0.1, 0.5, 10),
    ])

    stable_results = []
    for cg in cue_gains_dense:
        r_A, r_B, h_A, h_B, W, pref = find_fixed_point_full(cg, N=N)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, 0.5)
        evals = np.sort(np.linalg.eigvals(J).real)[::-1]
        stable_results.append({
            'cue_gain': cg,
            'lambda_1': evals[0],
            'D': np.mean(r_A) - np.mean(r_B),
        })
        print(f"  cue={cg:.4f}: D={np.mean(r_A)-np.mean(r_B):+.4f}, λ₁={evals[0]:.6f}")

    # ── Step 2: Newton/continuation for the OTHER branch ─────────
    print("\n[2/5] Newton continuation for the unstable branch...")
    cue_gains_cont = np.concatenate([
        np.linspace(0.0, 0.005, 8),
        np.linspace(0.005, 0.03, 20),
        np.linspace(0.03, 0.1, 15),
        np.linspace(0.1, 0.5, 10),
    ])
    cont_results = find_unstable_fp_continuation(cue_gains_cont, N=N)

    # ── Step 3: Plot the true bifurcation ────────────────────────
    print("\n[3/5] Plotting the true bifurcation...")
    plot_true_bifurcation(
        cont_results, stable_results,
        os.path.join(outdir, 'fig42_true_bifurcation.png'), N=N)

    # ── Step 4: BBP vs Bifurcation comparison ────────────────────
    print("\n[4/5] BBP vs Bifurcation comparison...")
    plot_bbp_vs_bifurcation(
        cont_results,
        os.path.join(outdir, 'fig43_bbp_vs_bifurcation.png'))

    # ── Step 5: Activity profiles and eigenvector analysis ───────
    print("\n[5/5] Activity profiles and critical eigenvector...")
    plot_activity_profiles(
        cont_results, stable_results,
        os.path.join(outdir, 'fig44_activity_profiles.png'), N=N)

    plot_critical_eigenvector_unstable(
        cont_results,
        os.path.join(outdir, 'fig45_critical_eigvec_unstable.png'), N=N)

    print("\n" + "=" * 70)
    print("DONE. Four figures saved to:", outdir)
    print("=" * 70)

    # ── Summary ──
    print("\n── SUMMARY ──")
    cont_valid = [r for r in cont_results if r is not None]
    print(f"  Continuation found {len(cont_valid)}/{len(cont_results)} solutions")
    n_positive_any = sum(1 for r in cont_valid if r['n_positive'] > 0)
    print(f"  Of these, {n_positive_any} have positive eigenvalues (unstable)")
    if cont_valid:
        max_lambda = max(r['lambda_1'] for r in cont_valid)
        print(f"  Maximum λ₁ on continuation branch: {max_lambda:.6f}")
        min_D = min(abs(r['D']) for r in cont_valid)
        print(f"  Minimum |D| on continuation branch: {min_D:.6f}")
