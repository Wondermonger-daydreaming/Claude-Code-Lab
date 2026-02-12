"""
==========================================================================
SPECTRAL PORTRAIT OF THE COUPLED RING ATTRACTOR
==========================================================================

Program III of the Spectral Mathematics proposal.

We compute the FULL eigenvalue spectrum of the coupled ring attractor
system at varying cue_gain, tracking:

  1. Mean-field (4D): Eigenvalue trajectories in the complex plane
     → Which eigenvalue crosses the imaginary axis?
     → Is the critical eigenvector the dominance mode D = A₁ - A₂?

  2. Full-neuron (2N-dimensional): Spectral portrait showing
     → Bulk eigenvalues (stable modes) vs outlier (critical mode)
     → How the bulk-vs-outlier structure reorganizes at the separatrix

  3. Critical eigenvector analysis:
     → Project the critical eigenvector onto the dominance direction
     → Show that the 1D cusp reduction IS the spectral projection

This connects the cusp catastrophe V(D) = D⁴ + aD² + bD to
proper spectral bifurcation theory.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve
from scipy.special import i0
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.collections import LineCollection
import warnings
warnings.filterwarnings('ignore')

# ── Style ────────────────────────────────────────────────────────────
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

COLORS = {
    'bulk': '#95a5a6',
    'critical': '#c0392b',
    'stable': '#2d5a7b',
    'unstable': '#e67e22',
    'dominance': '#8e44ad',
    'network_A': '#2d5a7b',
    'network_B': '#c0392b',
    'cliff': '#f39c12',
    'background': '#faf8f5',
}


# ═══════════════════════════════════════════════════════════════════
# MODEL: COUPLED RING ATTRACTORS
# ═══════════════════════════════════════════════════════════════════

def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    """Sigmoid transfer function."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def sigmoid_derivative(h, r_max=1.0, beta=5.0, h0=0.5):
    """Derivative: σ'(h) = β · σ(h) · (1 - σ(h)/r_max)."""
    s = sigmoid(h, r_max, beta, h0)
    return beta * s * (1.0 - s / r_max)


def build_within_weights(N, J_0, J_1):
    """Cosine connectivity: W_ij = (-J_0 + J_1 cos(φ_i - φ_j)) / N."""
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    dphi = preferred[:, np.newaxis] - preferred[np.newaxis, :]
    W = (-J_0 + J_1 * np.cos(dphi)) / N
    return W, preferred


def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


# ═══════════════════════════════════════════════════════════════════
# PART 1: MEAN-FIELD (4D) SPECTRAL TRACKING
# ═══════════════════════════════════════════════════════════════════

def mean_field_bump(A, r_bar, ext_uniform, ext_cosine,
                    J_0, J_1, r_max=1.0, beta=5.0, h0=0.5, n_phi=500):
    """Self-consistent bump solution for a single ring."""
    phi = np.linspace(-np.pi, np.pi, n_phi, endpoint=False)
    dphi = 2 * np.pi / n_phi
    h = -J_0 * r_bar + (J_1 / 2.0) * A * np.cos(phi) + ext_uniform + ext_cosine * np.cos(phi)
    r = sigmoid(h, r_max, beta, h0)
    r_bar_new = np.sum(r) * dphi / (2 * np.pi)
    A_new = np.sum(r * np.cos(phi)) * dphi / np.pi
    return A_new, r_bar_new


def coupled_residual(x, cue_gain, J_cross, J_0=1.0, J_1=6.0,
                     r_max=1.0, beta=5.0, h0=0.5):
    """Residual for coupled mean-field fixed point."""
    A_1, r_bar_1, A_2, r_bar_2 = x
    A_1_new, r_bar_1_new = mean_field_bump(
        A_1, r_bar_1, -J_cross * r_bar_2, cue_gain, J_0, J_1, r_max, beta, h0)
    A_2_new, r_bar_2_new = mean_field_bump(
        A_2, r_bar_2, -J_cross * r_bar_1, 0.0, J_0, J_1, r_max, beta, h0)
    return [A_1_new - A_1, r_bar_1_new - r_bar_1,
            A_2_new - A_2, r_bar_2_new - r_bar_2]


def find_fixed_points_mf(cue_gain, J_cross=0.5, J_0=1.0, J_1=6.0):
    """Find all mean-field fixed points."""
    solutions = []
    for A1_init in np.linspace(0.0, 0.8, 20):
        for A2_init in [0.0, 0.2, 0.4, 0.6]:
            for r_init in [0.2, 0.4]:
                x0 = [A1_init, r_init, A2_init, r_init]
                try:
                    sol, info, ier, _ = fsolve(
                        coupled_residual, x0,
                        args=(cue_gain, J_cross, J_0, J_1), full_output=True)
                    if ier == 1:
                        A1, r1, A2, r2 = sol
                        if A1 >= 0 and A2 >= 0 and r1 > 0 and r2 > 0:
                            res = coupled_residual(sol, cue_gain, J_cross, J_0, J_1)
                            if np.max(np.abs(res)) < 1e-8:
                                is_dup = any(np.max(np.abs(np.array(s) - sol)) < 1e-4
                                             for s in solutions)
                                if not is_dup:
                                    solutions.append(sol)
                except Exception:
                    pass
    return solutions


def mean_field_jacobian_eigenvalues(x_sol, cue_gain, J_cross=0.5,
                                     J_0=1.0, J_1=6.0, eps=1e-5):
    """
    Compute the 4×4 Jacobian eigenvalues at a mean-field fixed point.
    Returns eigenvalues AND eigenvectors.
    """
    n = len(x_sol)
    J = np.zeros((n, n))
    f0 = coupled_residual(list(x_sol), cue_gain, J_cross, J_0, J_1)
    for i in range(n):
        x_pert = list(x_sol)
        x_pert[i] += eps
        f_pert = coupled_residual(x_pert, cue_gain, J_cross, J_0, J_1)
        for j in range(n):
            J[j, i] = (f_pert[j] - f0[j]) / eps
    eigenvalues, eigenvectors = np.linalg.eig(J)
    return eigenvalues, eigenvectors


def track_mean_field_spectrum(cue_gains, J_cross=0.5):
    """Track all eigenvalues across cue_gain for each fixed point type."""
    results = []
    for cg in cue_gains:
        fps = find_fixed_points_mf(cg, J_cross)
        for fp in fps:
            evals, evecs = mean_field_jacobian_eigenvalues(fp, cg, J_cross)
            A1, r1, A2, r2 = fp
            # Classify
            if A1 > A2 + 0.05:
                fp_type = 'A-dominant'
            elif A2 > A1 + 0.05:
                fp_type = 'B-dominant'
            else:
                fp_type = 'symmetric'
            # Check stability
            map_eigs = 1.0 + evals
            stable = np.all(np.abs(map_eigs) < 1.0)
            results.append({
                'cue_gain': cg, 'fp': fp, 'type': fp_type,
                'eigenvalues': evals, 'eigenvectors': evecs,
                'stable': stable, 'D': A1 - A2,
            })
    return results


# ═══════════════════════════════════════════════════════════════════
# PART 2: FULL-NEURON (2N-DIMENSIONAL) SPECTRAL PORTRAIT
# ═══════════════════════════════════════════════════════════════════

def find_fixed_point_full(cue_gain, N=48, J_0=1.0, J_1=6.0, J_cross=0.5,
                          kappa=2.0, input_gain=5.0, r_max=1.0, beta=5.0,
                          h0=0.5, dt=0.5, tau=10.0, n_steps=5000):
    """
    Find fixed point of the full N-neuron coupled system by simulating
    deterministic dynamics to convergence.

    Returns (r_A*, r_B*, h_A*, h_B*) at the fixed point.
    """
    W, preferred = build_within_weights(N, J_0, J_1)

    # Items at ±π/4
    theta1, theta2 = np.pi / 4, -np.pi / 4

    # Stimulus drive
    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)

    # Initialize with stimulus-driven bumps
    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A, r_max, beta, h0)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B, r_max, beta, h0)

    # Phase 1: Drive both (100 steps)
    for step in range(100):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + drive_A + cross_A
        h_B = W @ r_B + drive_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        r_A = r_A + (-r_A + f_A) * (dt / tau)
        r_B = r_B + (-r_B + f_B) * (dt / tau)
        r_A = np.maximum(0, r_A)
        r_B = np.maximum(0, r_B)

    # Phase 2: Cue to network A only, run to convergence
    cue_drive_A = cue_gain * tuning_curve(theta1, preferred, kappa)

    for step in range(n_steps):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + cue_drive_A + cross_A
        h_B = W @ r_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)
        r_B = np.maximum(0, r_B + dr_B)

        # Check convergence
        if step > 100 and np.max(np.abs(dr_A)) < 1e-10 and np.max(np.abs(dr_B)) < 1e-10:
            break

    # Final h values at fixed point
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)
    h_A = W @ r_A + cue_drive_A + cross_A
    h_B = W @ r_B + cross_B

    return r_A, r_B, h_A, h_B, W, preferred


def compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross,
                          r_max=1.0, beta=5.0, h0=0.5, tau=10.0):
    """
    Compute the full 2N × 2N Jacobian of the coupled system.

    Dynamics: τ dr_i^A/dt = -r_i^A + σ(h_i^A)
    where h_i^A = Σ_j W_ij r_j^A + ext_i^A - J_cross * mean(r^B)

    Jacobian blocks:
      ∂(dr^A/dt)/∂r^A = (-I + diag(σ'(h^A)) · W) / τ
      ∂(dr^A/dt)/∂r^B = diag(σ'(h^A)) · (-J_cross/N) · 11^T / τ
      ∂(dr^B/dt)/∂r^A = diag(σ'(h^B)) · (-J_cross/N) · 11^T / τ
      ∂(dr^B/dt)/∂r^B = (-I + diag(σ'(h^B)) · W) / τ
    """
    N = len(r_A)

    # Sigmoid derivatives at fixed point
    sigma_prime_A = sigmoid_derivative(h_A, r_max, beta, h0)
    sigma_prime_B = sigmoid_derivative(h_B, r_max, beta, h0)

    # Diagonal matrices of σ'
    D_A = np.diag(sigma_prime_A)
    D_B = np.diag(sigma_prime_B)

    # Rank-1 cross-inhibition coupling: (-J_cross/N) * ones_matrix
    cross_mat = np.full((N, N), -J_cross / N)

    # Build 2N × 2N Jacobian
    J = np.zeros((2 * N, 2 * N))

    # Top-left: ∂(dr^A)/∂r^A
    J[:N, :N] = (-np.eye(N) + D_A @ W) / tau

    # Top-right: ∂(dr^A)/∂r^B
    J[:N, N:] = (D_A @ cross_mat) / tau

    # Bottom-left: ∂(dr^B)/∂r^A
    J[N:, :N] = (D_B @ cross_mat) / tau

    # Bottom-right: ∂(dr^B)/∂r^B
    J[N:, N:] = (-np.eye(N) + D_B @ W) / tau

    return J


def full_neuron_spectral_portrait(cue_gains, N=48, J_cross=0.5):
    """
    Compute the full spectral portrait at selected cue_gain values.
    Returns eigenvalues, eigenvectors, and the Jacobian at each point.
    """
    results = []
    for cg in cue_gains:
        print(f"  Full spectrum at cue_gain = {cg:.4f}...")
        r_A, r_B, h_A, h_B, W, preferred = find_fixed_point_full(cg, N=N, J_cross=J_cross)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals, evecs = np.linalg.eig(J)

        # Sort by real part (most unstable first)
        idx = np.argsort(-evals.real)
        evals = evals[idx]
        evecs = evecs[:, idx]

        results.append({
            'cue_gain': cg,
            'eigenvalues': evals,
            'eigenvectors': evecs,
            'r_A': r_A, 'r_B': r_B,
            'h_A': h_A, 'h_B': h_B,
            'jacobian': J,
            'dominance': np.mean(r_A) - np.mean(r_B),
        })
    return results


# ═══════════════════════════════════════════════════════════════════
# FIGURE 1: MEAN-FIELD EIGENVALUE TRAJECTORIES
# ═══════════════════════════════════════════════════════════════════

def plot_mean_field_eigenvalue_trajectories(results, save_path):
    """
    Plot eigenvalue trajectories in the complex plane as cue_gain varies.
    Color by cue_gain. Mark the stability boundary.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    for ax, fp_type, title in zip(axes,
            ['symmetric', 'A-dominant', 'B-dominant'],
            ['Symmetric Fixed Point', 'A-Dominant Fixed Point', 'B-Dominant Fixed Point']):

        subset = [r for r in results if r['type'] == fp_type]
        if not subset:
            ax.set_title(f'{title}\n(not found)', fontsize=12)
            ax.set_xlabel('Re(λ)')
            ax.set_ylabel('Im(λ)')
            continue

        cue_gains = np.array([r['cue_gain'] for r in subset])
        all_eigs = np.array([r['eigenvalues'] for r in subset])

        # Plot each eigenvalue trajectory
        for eig_idx in range(all_eigs.shape[1]):
            re_vals = all_eigs[:, eig_idx].real
            im_vals = all_eigs[:, eig_idx].imag

            # Create colored line
            points = np.array([re_vals, im_vals]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)
            lc = LineCollection(segments, cmap='coolwarm',
                              norm=plt.Normalize(cue_gains.min(), cue_gains.max()))
            lc.set_array(cue_gains[:-1])
            lc.set_linewidth(2.5)
            ax.add_collection(lc)

            # Mark start (cue=0) and end
            ax.plot(re_vals[0], im_vals[0], 'o', color=COLORS['stable'],
                    markersize=5, zorder=5)
            ax.plot(re_vals[-1], im_vals[-1], 's', color=COLORS['critical'],
                    markersize=5, zorder=5)

        # Stability boundary: unit circle around (-1, 0) for the map eigenvalues
        # For the Jacobian eigenvalues: Re(λ) = 0 line marks continuous-time stability
        # But this is a discrete-time map, so stability is |1 + λ| < 1
        theta = np.linspace(0, 2 * np.pi, 200)
        ax.plot(np.cos(theta) - 1, np.sin(theta), '--', color='gray',
                alpha=0.4, linewidth=1, label='|1+λ|=1')

        ax.axvline(x=0, color='gray', alpha=0.2, linewidth=0.5)
        ax.axhline(y=0, color='gray', alpha=0.2, linewidth=0.5)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Re(λ)')
        ax.set_ylabel('Im(λ)')
        ax.set_aspect('equal')

        # Auto-scale with margin
        if len(subset) > 0:
            all_re = all_eigs.real.flatten()
            all_im = all_eigs.imag.flatten()
            margin = 0.1
            ax.set_xlim(all_re.min() - margin, all_re.max() + margin)
            ax.set_ylim(all_im.min() - margin, all_im.max() + margin)

    plt.colorbar(plt.cm.ScalarMappable(
        norm=plt.Normalize(0, cue_gains.max()), cmap='coolwarm'),
        ax=axes, label='cue_gain', shrink=0.6)

    fig.suptitle('Mean-Field (4D) Eigenvalue Trajectories\n'
                 'Coupled Ring Attractor as cue_gain varies',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 2: DOMINANT EIGENVALUE VS CUE_GAIN
# ═══════════════════════════════════════════════════════════════════

def plot_dominant_eigenvalue_vs_cue(results, save_path):
    """
    Plot the real part of the most positive eigenvalue vs cue_gain.
    The zero-crossing is the bifurcation.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: Re(λ_max) vs cue_gain for each fixed point type
    ax = axes[0]
    for fp_type, color, marker in [
        ('symmetric', COLORS['dominance'], 'o'),
        ('A-dominant', COLORS['network_A'], 's'),
        ('B-dominant', COLORS['network_B'], '^'),
    ]:
        subset = [r for r in results if r['type'] == fp_type]
        if not subset:
            continue
        cgs = [r['cue_gain'] for r in subset]
        # Dominant eigenvalue: max Re(λ) but in terms of map stability |1+λ|
        lambda_max = []
        for r in subset:
            map_eigs = 1.0 + r['eigenvalues']
            # Find the eigenvalue of J closest to the stability boundary
            # The critical one is the one with |1+λ| closest to 1
            dists_from_boundary = np.abs(map_eigs) - 1.0
            idx = np.argmax(dists_from_boundary * np.sign(r['eigenvalues'].real))
            lambda_max.append(r['eigenvalues'][idx].real)

        ax.plot(cgs, lambda_max, marker, color=color, label=fp_type,
                markersize=3, alpha=0.7, linewidth=0)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='behavioral cliff (0.02)')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('Re(λ_dominant)')
    ax.set_title('Dominant Eigenvalue vs Control Parameter', fontweight='bold')
    ax.legend(fontsize=9)

    # Right: Dominance D = A₁ - A₂ vs cue_gain
    ax = axes[1]
    for fp_type, color in [
        ('symmetric', COLORS['dominance']),
        ('A-dominant', COLORS['network_A']),
        ('B-dominant', COLORS['network_B']),
    ]:
        subset = [r for r in results if r['type'] == fp_type]
        if not subset:
            continue
        cgs = [r['cue_gain'] for r in subset]
        Ds = [r['D'] for r in subset]
        stable = [r['stable'] for r in subset]
        for cg, D, s in zip(cgs, Ds, stable):
            ax.plot(cg, D,
                    'o' if s else 'x',
                    color=color, markersize=4 if s else 3,
                    alpha=0.8 if s else 0.4)

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='behavioral cliff')
    ax.set_xlabel('cue_gain')
    ax.set_ylabel('D = A₁ - A₂ (dominance)')
    ax.set_title('Bifurcation Diagram: Dominance Variable', fontweight='bold')
    ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 3: FULL-NEURON SPECTRAL PORTRAIT
# ═══════════════════════════════════════════════════════════════════

def plot_full_spectral_portrait(full_results, save_path):
    """
    Plot the full 2N eigenvalue spectrum at selected cue_gain values.
    Shows the transition from bulk+outlier structure to reorganization.
    """
    n_panels = len(full_results)
    fig, axes = plt.subplots(1, n_panels, figsize=(4 * n_panels, 4))
    if n_panels == 1:
        axes = [axes]

    for ax, res in zip(axes, full_results):
        evals = res['eigenvalues']
        cg = res['cue_gain']

        # Separate real and complex eigenvalues
        re_parts = evals.real
        im_parts = evals.imag

        # Color by distance from the most positive eigenvalue
        # Highlight the critical (most positive Re) eigenvalues
        max_re = re_parts[0]  # Already sorted
        colors_arr = np.where(re_parts > max_re - 0.02,
                              COLORS['critical'], COLORS['bulk'])

        for i, (re, im, c) in enumerate(zip(re_parts, im_parts, colors_arr)):
            size = 40 if c == COLORS['critical'] else 12
            alpha = 0.9 if c == COLORS['critical'] else 0.4
            zorder = 10 if c == COLORS['critical'] else 1
            ax.scatter(re, im, c=c, s=size, alpha=alpha, zorder=zorder,
                      edgecolors='none')

        # Mark the dominant eigenvalue
        ax.scatter(re_parts[0], im_parts[0], c=COLORS['critical'],
                  s=100, marker='*', zorder=20, edgecolors='black',
                  linewidths=0.5, label=f'λ₁ = {re_parts[0]:.4f}')

        # Reference lines
        ax.axvline(x=0, color='gray', alpha=0.3, linewidth=0.5)
        ax.axhline(y=0, color='gray', alpha=0.3, linewidth=0.5)

        # Annotate
        dom = res['dominance']
        ax.set_title(f'cue = {cg:.3f}\nD = {dom:.3f}',
                    fontsize=10, fontweight='bold')
        ax.set_xlabel('Re(λ)')
        if ax == axes[0]:
            ax.set_ylabel('Im(λ)')
        ax.legend(fontsize=7, loc='lower left')

    fig.suptitle(f'Full Spectral Portrait (N={len(full_results[0]["eigenvalues"])}D)\n'
                 'Eigenvalues of the coupled ring attractor Jacobian',
                 fontsize=13, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 4: CRITICAL EIGENVECTOR ANALYSIS
# ═══════════════════════════════════════════════════════════════════

def plot_critical_eigenvector(full_results, save_path):
    """
    Analyze the eigenvector of the dominant eigenvalue.
    Does it correspond to the dominance mode (A up, B down)?
    """
    n_panels = len(full_results)
    fig, axes = plt.subplots(2, n_panels, figsize=(4 * n_panels, 7))
    if n_panels == 1:
        axes = axes.reshape(2, 1)

    N = len(full_results[0]['r_A'])  # neurons per network

    for col, res in enumerate(full_results):
        cg = res['cue_gain']
        evec = res['eigenvectors'][:, 0]  # Critical eigenvector (largest Re(λ))

        # The eigenvector is 2N-dimensional: [v_A, v_B]
        # If it's the dominance mode: v_A > 0, v_B < 0 (or vice versa)
        v_A = evec[:N].real
        v_B = evec[N:].real

        # Normalize
        norm = np.max(np.abs(evec.real))
        if norm > 0:
            v_A /= norm
            v_B /= norm

        # Top row: eigenvector components
        ax = axes[0, col]
        angles = np.linspace(-180, 180, N, endpoint=False)
        ax.plot(angles, v_A, '-', color=COLORS['network_A'],
                linewidth=2, label='Network A')
        ax.plot(angles, v_B, '-', color=COLORS['network_B'],
                linewidth=2, label='Network B')
        ax.axhline(y=0, color='gray', alpha=0.3)
        ax.set_title(f'cue = {cg:.3f}\nλ₁ = {res["eigenvalues"][0].real:.4f}',
                    fontsize=10, fontweight='bold')
        if col == 0:
            ax.set_ylabel('Eigenvector component')
        ax.legend(fontsize=7)

        # Bottom row: fixed point activity profiles
        ax = axes[1, col]
        ax.plot(angles, res['r_A'], '-', color=COLORS['network_A'],
                linewidth=2, label='r_A (fixed pt)')
        ax.plot(angles, res['r_B'], '-', color=COLORS['network_B'],
                linewidth=2, label='r_B (fixed pt)')
        ax.axhline(y=0, color='gray', alpha=0.3)
        if col == 0:
            ax.set_ylabel('Activity r')
        ax.set_xlabel('Preferred angle (°)')
        ax.legend(fontsize=7)

        # Compute dominance projection
        # Define dominance vector: d = [+1/√N, ..., +1/√N, -1/√N, ..., -1/√N]
        d = np.concatenate([np.ones(N), -np.ones(N)]) / np.sqrt(2 * N)
        projection = np.abs(np.dot(evec.real / np.linalg.norm(evec.real), d))

        ax.set_title(f'|⟨v₁, d⟩| = {projection:.3f}', fontsize=9,
                    color=COLORS['dominance'])

    fig.suptitle('Critical Eigenvector Analysis\n'
                 'Is the critical mode the dominance variable D = A₁ - A₂?',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 5: SPECTRAL DENSITY — BULK VS OUTLIER
# ═══════════════════════════════════════════════════════════════════

def plot_spectral_density(full_results, save_path):
    """
    Histogram of eigenvalue real parts showing bulk vs outlier.
    """
    n_panels = len(full_results)
    fig, axes = plt.subplots(1, n_panels, figsize=(4 * n_panels, 4))
    if n_panels == 1:
        axes = [axes]

    for ax, res in zip(axes, full_results):
        re_parts = res['eigenvalues'].real
        cg = res['cue_gain']

        # Histogram
        ax.hist(re_parts, bins=30, color=COLORS['bulk'], alpha=0.6,
                edgecolor='white', linewidth=0.5, density=True)

        # Mark the top eigenvalue(s) as outliers
        # Use a gap criterion: outlier if it's more than 2σ from the bulk mean
        bulk_mean = np.mean(re_parts[3:])  # Exclude top 3
        bulk_std = np.std(re_parts[3:])
        for i in range(min(5, len(re_parts))):
            if re_parts[i] > bulk_mean + 2 * bulk_std:
                ax.axvline(x=re_parts[i], color=COLORS['critical'],
                          linewidth=2, alpha=0.8, linestyle='-')
                ax.annotate(f'λ_{i+1}={re_parts[i]:.3f}',
                           xy=(re_parts[i], 0), xytext=(re_parts[i] + 0.01, 0.5),
                           fontsize=7, color=COLORS['critical'],
                           arrowprops=dict(arrowstyle='->', color=COLORS['critical']))

        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.4)
        ax.set_xlabel('Re(λ)')
        ax.set_title(f'cue = {cg:.3f}', fontweight='bold')
        if ax == axes[0]:
            ax.set_ylabel('Density')

    fig.suptitle('Spectral Density: Bulk vs Outlier Eigenvalues\n'
                 'Outliers (red) carry the system dynamics; bulk (gray) is stable modes',
                 fontsize=12, fontweight='bold', y=1.05)
    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FIGURE 6: EIGENVALUE TRACKING ACROSS CUE_GAIN (FULL SYSTEM)
# ═══════════════════════════════════════════════════════════════════

def plot_eigenvalue_tracking_full(save_path, N=48, J_cross=0.5):
    """
    Track the top eigenvalues of the full system across a dense sweep of cue_gain.
    This is the spectral version of the bifurcation diagram.
    """
    cue_gains = np.concatenate([
        np.linspace(0.0, 0.05, 25),
        np.linspace(0.05, 0.2, 15),
        np.linspace(0.2, 0.5, 10),
    ])

    top_eigs = []  # Track top 5 eigenvalues
    dominances = []

    for cg in cue_gains:
        print(f"  Tracking: cue_gain = {cg:.4f}")
        r_A, r_B, h_A, h_B, W, preferred = find_fixed_point_full(cg, N=N, J_cross=J_cross)
        J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
        evals = np.linalg.eigvals(J)
        idx = np.argsort(-evals.real)
        top_eigs.append(evals[idx[:5]])
        dominances.append(np.mean(r_A) - np.mean(r_B))

    top_eigs = np.array(top_eigs)  # Shape: (n_cue, 5)

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Top: Re(λ) for top 5 eigenvalues
    ax = axes[0]
    labels = ['λ₁ (critical)', 'λ₂', 'λ₃', 'λ₄', 'λ₅']
    colors_list = [COLORS['critical'], COLORS['dominance'], COLORS['network_A'],
                   COLORS['bulk'], COLORS['bulk']]
    for i in range(5):
        lw = 2.5 if i == 0 else 1.0
        alpha = 1.0 if i < 3 else 0.5
        ax.plot(cue_gains, top_eigs[:, i].real, '-', color=colors_list[i],
                linewidth=lw, alpha=alpha, label=labels[i])

    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6,
               linewidth=1.5, label='behavioral cliff')
    ax.set_ylabel('Re(λ)')
    ax.set_title(f'Top 5 Eigenvalues of Full {2*N}D Jacobian\n'
                 'Spectral Bifurcation = Separatrix', fontweight='bold')
    ax.legend(fontsize=9, ncol=3)

    # Bottom: Dominance
    ax = axes[1]
    ax.plot(cue_gains, dominances, '-', color=COLORS['dominance'], linewidth=2)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.4)
    ax.axvline(x=0.02, color=COLORS['cliff'], linestyle=':', alpha=0.6, linewidth=1.5)
    ax.set_xlabel('cue_gain (control parameter)')
    ax.set_ylabel('D = ⟨r_A⟩ - ⟨r_B⟩')
    ax.set_title('Dominance Variable', fontweight='bold')

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

    print("=" * 70)
    print("SPECTRAL PORTRAIT OF THE COUPLED RING ATTRACTOR")
    print("Program III: Spectral Theory of the Separatrix")
    print("=" * 70)

    # ── Part 1: Mean-field eigenvalue tracking ────────────────────
    print("\n[1/6] Mean-field (4D) eigenvalue tracking...")
    cue_gains_mf = np.concatenate([
        np.linspace(0.0, 0.005, 10),
        np.linspace(0.005, 0.03, 40),
        np.linspace(0.03, 0.1, 20),
        np.linspace(0.1, 0.5, 15),
    ])
    mf_results = track_mean_field_spectrum(cue_gains_mf)
    print(f"  Found {len(mf_results)} (cue_gain, fixed_point) pairs")

    print("\n[2/6] Plotting mean-field eigenvalue trajectories...")
    plot_mean_field_eigenvalue_trajectories(
        mf_results, os.path.join(outdir, 'fig28_mf_eigenvalue_trajectories.png'))

    print("\n[3/6] Plotting dominant eigenvalue vs cue_gain...")
    plot_dominant_eigenvalue_vs_cue(
        mf_results, os.path.join(outdir, 'fig29_dominant_eigenvalue.png'))

    # ── Part 2: Full-neuron spectral portrait ──────────────────
    print("\n[4/6] Full-neuron spectral portrait at selected cue_gains...")
    selected_cues = [0.0, 0.01, 0.02, 0.05, 0.1, 0.3]
    full_results = full_neuron_spectral_portrait(selected_cues, N=48)

    plot_full_spectral_portrait(
        full_results, os.path.join(outdir, 'fig30_full_spectral_portrait.png'))

    print("\n[5/6] Critical eigenvector analysis...")
    plot_critical_eigenvector(
        full_results, os.path.join(outdir, 'fig31_critical_eigenvector.png'))

    plot_spectral_density(
        full_results, os.path.join(outdir, 'fig32_spectral_density.png'))

    # ── Part 3: Dense eigenvalue tracking (full system) ────────
    print("\n[6/6] Dense eigenvalue tracking across cue_gain (full system)...")
    plot_eigenvalue_tracking_full(
        os.path.join(outdir, 'fig33_eigenvalue_tracking_full.png'), N=48)

    print("\n" + "=" * 70)
    print("DONE. Six figures saved to:", outdir)
    print("=" * 70)
