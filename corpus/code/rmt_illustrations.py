"""
==========================================================================
RANDOM MATRIX THEORY ILLUSTRATIONS
==========================================================================

Programs II and IV of the Spectral Mathematics proposal.

Three fundamental results, visualized:

  1. MARCHENKO-PASTUR LAW (Program II)
     The eigenvalue distribution of sample covariance matrices.
     The null model: what spectra look like when there's NO structure.

  2. BBP TRANSITION (Programs II & III)
     The Baik-Ben Arous-Péché phase transition: when a spiked eigenvalue
     separates from the bulk. This IS the separatrix in spectral form.

  3. FREE MULTIPLICATIVE CONVOLUTION (Program IV)
     What happens when you multiply many random matrices (depth).
     The singular value distribution of a product = free ⊠ of individuals.
     This IS the mathematics of deep networks.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

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
    'empirical': '#2d5a7b',
    'theory': '#c0392b',
    'spike': '#e67e22',
    'bulk': '#95a5a6',
    'product': '#8e44ad',
    'layer1': '#2980b9',
    'layer2': '#27ae60',
    'layer4': '#c0392b',
    'layer8': '#8e44ad',
    'layer16': '#e67e22',
}


# ═══════════════════════════════════════════════════════════════════
# MARCHENKO-PASTUR LAW
# ═══════════════════════════════════════════════════════════════════

def marchenko_pastur_density(x, gamma, sigma2=1.0):
    """
    Marchenko-Pastur density.

    For S = (1/n) X^T X where X is n×p with i.i.d. entries,
    as n,p → ∞ with p/n → γ:

      f_γ(λ) = √((λ₊ - λ)(λ - λ₋)) / (2π σ² γ λ)

    supported on [λ₋, λ₊] where λ± = σ²(1 ± √γ)².
    """
    lambda_minus = sigma2 * (1 - np.sqrt(gamma))**2
    lambda_plus = sigma2 * (1 + np.sqrt(gamma))**2

    density = np.zeros_like(x, dtype=float)
    mask = (x >= lambda_minus) & (x <= lambda_plus) & (x > 0)
    density[mask] = np.sqrt((lambda_plus - x[mask]) * (x[mask] - lambda_minus)) / \
                    (2 * np.pi * sigma2 * gamma * x[mask])
    return density


def plot_marchenko_pastur(save_path):
    """
    Figure: Marchenko-Pastur law for various aspect ratios γ = p/n.
    Empirical eigenvalue histograms vs theoretical prediction.
    """
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    gammas = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
    n = 500  # sample size

    for idx, gamma in enumerate(gammas):
        ax = fig.add_subplot(gs[idx // 3, idx % 3])

        p = int(gamma * n)
        sigma2 = 1.0

        # Generate random matrix and compute sample covariance eigenvalues
        X = np.random.randn(n, p) * np.sqrt(sigma2)
        S = X.T @ X / n  # p × p sample covariance
        eigs = np.linalg.eigvalsh(S)

        # Theoretical MP density
        lambda_minus = sigma2 * (1 - np.sqrt(gamma))**2
        lambda_plus = sigma2 * (1 + np.sqrt(gamma))**2
        x_theory = np.linspace(max(0, lambda_minus - 0.2),
                               lambda_plus + 0.5, 500)
        density = marchenko_pastur_density(x_theory, gamma, sigma2)

        # Plot
        ax.hist(eigs, bins=60, density=True, color=COLORS['empirical'],
                alpha=0.5, edgecolor='white', linewidth=0.3,
                label=f'Empirical (n={n}, p={p})')
        ax.plot(x_theory, density, '-', color=COLORS['theory'],
                linewidth=2.5, label='MP theory')

        # Mark bulk edges
        ax.axvline(x=lambda_minus, color=COLORS['theory'], linestyle='--',
                  alpha=0.5, linewidth=1)
        ax.axvline(x=lambda_plus, color=COLORS['theory'], linestyle='--',
                  alpha=0.5, linewidth=1)

        ax.set_title(f'γ = p/n = {gamma}', fontweight='bold', fontsize=12)
        ax.set_xlabel('λ')
        if idx % 3 == 0:
            ax.set_ylabel('Density')
        ax.legend(fontsize=7, loc='upper right')
        ax.set_ylim(bottom=0)

    fig.suptitle('Marchenko-Pastur Law: The Null Model\n'
                 'Eigenvalue distribution of random covariance matrices '
                 '— what spectra look like with NO learned structure',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# BBP TRANSITION: THE SEPARATRIX IN SPECTRAL FORM
# ═══════════════════════════════════════════════════════════════════

def plot_bbp_transition(save_path):
    """
    Figure: Baik-Ben Arous-Péché phase transition.

    A 'spiked' covariance model: true covariance has one large eigenvalue
    (the signal) on top of identity (noise). As the spike strength increases
    past the BBP threshold, the top sample eigenvalue separates from the bulk.

    This IS the separatrix: the threshold where signal becomes detectable.
    """
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    n = 500
    gamma = 0.5  # p/n
    p = int(gamma * n)
    sigma2 = 1.0

    # BBP threshold: spike must exceed σ²(1 + √γ) for detection
    # Actually for spiked model with Σ = I + θ e₁e₁ᵀ,
    # the BBP threshold is θ_c = √γ
    # Above: top eigenvalue separates. Below: absorbed into bulk.
    theta_c = np.sqrt(gamma)
    lambda_plus = sigma2 * (1 + np.sqrt(gamma))**2

    spike_strengths = [0.0, 0.3, theta_c * 0.9, theta_c, theta_c * 1.5, theta_c * 3.0]
    labels = ['No spike', f'θ = 0.3 (below)',
              f'θ ≈ {theta_c*0.9:.2f} (near)',
              f'θ = √γ = {theta_c:.2f} (BBP)',
              f'θ = {theta_c*1.5:.2f} (above)',
              f'θ = {theta_c*3:.2f} (well above)']

    for idx, (theta, label) in enumerate(zip(spike_strengths, labels)):
        ax = fig.add_subplot(gs[idx // 3, idx % 3])

        # True covariance: Σ = I + θ * e₁e₁ᵀ
        # Generate: X = Z @ Σ^{1/2} where Z is i.i.d. N(0,1)
        # Σ^{1/2} = I + (√(1+θ) - 1) * e₁e₁ᵀ
        Z = np.random.randn(n, p) * np.sqrt(sigma2)
        if theta > 0:
            # Spike the first component
            Z[:, 0] *= np.sqrt(1 + theta)

        S = Z.T @ Z / n
        eigs = np.sort(np.linalg.eigvalsh(S))[::-1]

        # Theoretical MP for bulk
        x_theory = np.linspace(0, lambda_plus + 1.5, 500)
        density = marchenko_pastur_density(x_theory, gamma, sigma2)

        # Plot
        ax.hist(eigs[1:], bins=50, density=True, color=COLORS['bulk'],
                alpha=0.5, edgecolor='white', linewidth=0.3, label='Bulk')

        # Top eigenvalue as a spike indicator
        ax.axvline(x=eigs[0], color=COLORS['spike'], linewidth=2.5,
                  alpha=0.9, label=f'λ₁ = {eigs[0]:.2f}')

        # Theory
        ax.plot(x_theory, density, '-', color=COLORS['theory'],
                linewidth=2, alpha=0.7, label='MP bulk')

        # BBP prediction for top eigenvalue location (when above threshold)
        if theta > theta_c:
            predicted_top = sigma2 * (1 + theta) * (1 + gamma / theta)
            ax.axvline(x=predicted_top, color=COLORS['spike'], linewidth=1,
                      linestyle='--', alpha=0.5, label=f'BBP pred: {predicted_top:.2f}')

        # Bulk edge
        ax.axvline(x=lambda_plus, color=COLORS['theory'], linewidth=1,
                  linestyle=':', alpha=0.4)

        ax.set_title(label, fontweight='bold', fontsize=10)
        ax.set_xlabel('λ')
        if idx % 3 == 0:
            ax.set_ylabel('Density')
        ax.legend(fontsize=6, loc='upper right')
        ax.set_ylim(bottom=0)

    fig.suptitle('BBP Phase Transition: The Separatrix in Spectral Form\n'
                 f'Spiked covariance model. BBP threshold: θ_c = √γ = {theta_c:.3f}. '
                 'Below: spike invisible. Above: spike separates.',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# BBP TRANSITION CURVE: TOP EIGENVALUE VS SPIKE STRENGTH
# ═══════════════════════════════════════════════════════════════════

def plot_bbp_curve(save_path):
    """
    The BBP transition curve: top sample eigenvalue as a function of
    spike strength θ. Shows the phase transition cleanly.
    """
    n = 800
    gamma = 0.5
    p = int(gamma * n)
    theta_c = np.sqrt(gamma)
    lambda_plus = (1 + np.sqrt(gamma))**2

    thetas = np.linspace(0, 3, 60)
    n_trials = 20  # Average over random instances

    top_eigs_mean = []
    top_eigs_std = []
    second_eigs_mean = []

    for theta in thetas:
        tops = []
        seconds = []
        for _ in range(n_trials):
            Z = np.random.randn(n, p)
            if theta > 0:
                Z[:, 0] *= np.sqrt(1 + theta)
            S = Z.T @ Z / n
            eigs = np.sort(np.linalg.eigvalsh(S))[::-1]
            tops.append(eigs[0])
            seconds.append(eigs[1])
        top_eigs_mean.append(np.mean(tops))
        top_eigs_std.append(np.std(tops))
        second_eigs_mean.append(np.mean(seconds))

    top_eigs_mean = np.array(top_eigs_mean)
    top_eigs_std = np.array(top_eigs_std)
    second_eigs_mean = np.array(second_eigs_mean)

    # Theoretical prediction
    thetas_above = thetas[thetas > theta_c]
    predicted_top = (1 + thetas_above) * (1 + gamma / thetas_above)

    fig, ax = plt.subplots(figsize=(10, 6))

    # Bulk edge
    ax.axhline(y=lambda_plus, color=COLORS['bulk'], linestyle='--',
              linewidth=1.5, alpha=0.6, label=f'MP bulk edge λ₊ = {lambda_plus:.2f}')

    # BBP threshold
    ax.axvline(x=theta_c, color=COLORS['spike'], linestyle=':',
              linewidth=2, alpha=0.6, label=f'BBP threshold θ_c = √γ = {theta_c:.3f}')

    # Empirical top eigenvalue
    ax.plot(thetas, top_eigs_mean, 'o-', color=COLORS['spike'],
            markersize=4, linewidth=1.5, label='Top eigenvalue λ₁ (empirical)')
    ax.fill_between(thetas,
                    top_eigs_mean - top_eigs_std,
                    top_eigs_mean + top_eigs_std,
                    color=COLORS['spike'], alpha=0.15)

    # Second eigenvalue (stays at bulk edge)
    ax.plot(thetas, second_eigs_mean, 's-', color=COLORS['bulk'],
            markersize=3, linewidth=1, alpha=0.6, label='Second eigenvalue λ₂')

    # Theory above threshold
    ax.plot(thetas_above, predicted_top, '--', color=COLORS['theory'],
            linewidth=2.5, label='BBP prediction (above θ_c)')

    # Annotations
    ax.annotate('BELOW:\nspike absorbed\ninto bulk\n(undetectable)',
               xy=(theta_c * 0.4, lambda_plus + 0.1), fontsize=9,
               color=COLORS['bulk'], ha='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.annotate('ABOVE:\nspike separates\nfrom bulk\n(detectable = learned feature)',
               xy=(theta_c * 2.2, predicted_top[len(predicted_top)//2] + 0.3),
               fontsize=9, color=COLORS['spike'], ha='center',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    ax.set_xlabel('Spike strength θ (signal-to-noise)', fontsize=12)
    ax.set_ylabel('Eigenvalue', fontsize=12)
    ax.set_title('BBP Phase Transition = The Separatrix\n'
                 'The threshold where signal becomes detectable is a spectral phase transition',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# FREE MULTIPLICATIVE CONVOLUTION: WHAT DEPTH DOES
# ═══════════════════════════════════════════════════════════════════

def plot_product_of_random_matrices(save_path):
    """
    Figure: Singular value distribution of products of random matrices.

    P = W_L · W_{L-1} · ... · W₁

    As L increases, the singular value distribution spreads:
    log-singular-values become approximately Gaussian (by CLT).
    This is the exploding/vanishing gradient problem, stated spectrally.
    """
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)

    d = 200  # Matrix dimension
    depths = [1, 2, 4, 8, 16, 32]

    for idx, L in enumerate(depths):
        ax = fig.add_subplot(gs[idx // 3, idx % 3])

        # Product of L random matrices, each scaled for unit singular values
        # Xavier init: each W has entries ~ N(0, 1/d)
        P = np.eye(d)
        for _ in range(L):
            W = np.random.randn(d, d) / np.sqrt(d)
            P = W @ P

        # Singular values
        svs = np.linalg.svd(P, compute_uv=False)
        log_svs = np.log10(svs + 1e-300)

        # Plot log-singular-value distribution
        ax.hist(log_svs, bins=40, density=True, color=COLORS[f'layer{min(L, 16)}']
                if f'layer{min(L, 16)}' in COLORS else COLORS['product'],
                alpha=0.6, edgecolor='white', linewidth=0.3)

        # For comparison: Gaussian fit to log-SVs
        mu, sigma = np.mean(log_svs), np.std(log_svs)
        x_fit = np.linspace(log_svs.min() - 0.5, log_svs.max() + 0.5, 200)
        gaussian = np.exp(-0.5 * ((x_fit - mu) / sigma)**2) / (sigma * np.sqrt(2 * np.pi))
        ax.plot(x_fit, gaussian, '--', color='black', linewidth=1.5,
                alpha=0.6, label=f'Gaussian fit\nμ={mu:.2f}, σ={sigma:.2f}')

        ax.axvline(x=0, color='gray', linestyle=':', alpha=0.5, linewidth=1)
        ax.set_title(f'Depth L = {L}', fontweight='bold', fontsize=11)
        ax.set_xlabel('log₁₀(singular value)')
        if idx % 3 == 0:
            ax.set_ylabel('Density')
        ax.legend(fontsize=7)

        # Condition number
        if svs[-1] > 0:
            cond = svs[0] / svs[-1]
            ax.annotate(f'κ = {cond:.1e}', xy=(0.95, 0.95),
                       xycoords='axes fraction', fontsize=8, ha='right', va='top',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    fig.suptitle('Free Multiplicative Convolution: What Depth Does to Information\n'
                 'Singular value distribution of W_L · W_{L-1} · ... · W₁  '
                 '(Xavier init, d=200)',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# DEPTH VS CONDITION NUMBER
# ═══════════════════════════════════════════════════════════════════

def plot_condition_vs_depth(save_path):
    """
    How the condition number of the product matrix grows with depth.
    Exponential growth = exploding/vanishing gradient problem.
    """
    d = 200
    depths = range(1, 41)
    n_trials = 20

    log_cond_mean = []
    log_cond_std = []

    for L in depths:
        log_conds = []
        for _ in range(n_trials):
            P = np.eye(d)
            for _ in range(L):
                W = np.random.randn(d, d) / np.sqrt(d)
                P = W @ P
            svs = np.linalg.svd(P, compute_uv=False)
            if svs[-1] > 1e-300:
                log_conds.append(np.log10(svs[0] / svs[-1]))
            else:
                log_conds.append(300)  # Effectively infinite
        log_cond_mean.append(np.mean(log_conds))
        log_cond_std.append(np.std(log_conds))

    log_cond_mean = np.array(log_cond_mean)
    log_cond_std = np.array(log_cond_std)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(list(depths), log_cond_mean, 'o-', color=COLORS['product'],
            linewidth=2, markersize=4)
    ax.fill_between(list(depths),
                    log_cond_mean - log_cond_std,
                    log_cond_mean + log_cond_std,
                    color=COLORS['product'], alpha=0.2)

    # Linear fit (exponential growth in log scale = linear in log-log)
    valid = log_cond_mean < 200
    coeffs = np.polyfit(np.array(list(depths))[valid],
                        log_cond_mean[valid], 1)
    ax.plot(list(depths), np.polyval(coeffs, list(depths)), '--',
            color=COLORS['theory'], linewidth=2,
            label=f'Linear fit: log₁₀(κ) ≈ {coeffs[0]:.2f}·L + {coeffs[1]:.2f}')

    ax.set_xlabel('Depth L (number of layers)', fontsize=12)
    ax.set_ylabel('log₁₀(condition number κ)', fontsize=12)
    ax.set_title('Condition Number vs Depth: The Exploding/Vanishing Gradient Problem\n'
                 'Exponential growth of κ with depth — why deep networks need careful initialization',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# WIGNER SEMICIRCLE (BONUS)
# ═══════════════════════════════════════════════════════════════════

def plot_wigner_semicircle(save_path):
    """
    Wigner's semicircle law: eigenvalue distribution of symmetric random matrices.
    The free CLT: sum of many freely independent variables → semicircle (not Gaussian!).
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ns = [50, 200, 1000]

    for ax, n in zip(axes, ns):
        # GOE: symmetric random matrix with Gaussian entries
        A = np.random.randn(n, n)
        M = (A + A.T) / (2 * np.sqrt(n))  # Normalize
        eigs = np.linalg.eigvalsh(M)

        # Theoretical semicircle
        x = np.linspace(-2.2, 2.2, 500)
        semicircle = np.where(np.abs(x) <= 2,
                              np.sqrt(4 - x**2) / (2 * np.pi), 0)

        ax.hist(eigs, bins=60, density=True, color=COLORS['empirical'],
                alpha=0.5, edgecolor='white', linewidth=0.3,
                label=f'GOE (n={n})')
        ax.plot(x, semicircle, '-', color=COLORS['theory'],
                linewidth=2.5, label='Semicircle law')

        ax.set_title(f'n = {n}', fontweight='bold')
        ax.set_xlabel('λ')
        if ax == axes[0]:
            ax.set_ylabel('Density')
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=0, top=0.45)

    fig.suptitle('Wigner Semicircle Law: The Free Central Limit Theorem\n'
                 'Sum of freely independent → semicircle (not Gaussian!). '
                 'This is the free probability analogue of the classical CLT.',
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

    print("=" * 70)
    print("RANDOM MATRIX THEORY ILLUSTRATIONS")
    print("Programs II & IV: RMT, BBP, and Free Probability")
    print("=" * 70)

    print("\n[1/6] Marchenko-Pastur Law (the null model)...")
    plot_marchenko_pastur(os.path.join(outdir, 'fig34_marchenko_pastur.png'))

    print("\n[2/6] BBP Phase Transition (spectral separatrix)...")
    plot_bbp_transition(os.path.join(outdir, 'fig35_bbp_transition.png'))

    print("\n[3/6] BBP Transition Curve...")
    plot_bbp_curve(os.path.join(outdir, 'fig36_bbp_curve.png'))

    print("\n[4/6] Product of Random Matrices (depth)...")
    plot_product_of_random_matrices(os.path.join(outdir, 'fig37_product_matrices.png'))

    print("\n[5/6] Condition Number vs Depth...")
    plot_condition_vs_depth(os.path.join(outdir, 'fig38_condition_vs_depth.png'))

    print("\n[6/6] Wigner Semicircle Law (free CLT)...")
    plot_wigner_semicircle(os.path.join(outdir, 'fig39_wigner_semicircle.png'))

    print("\n" + "=" * 70)
    print("DONE. Six figures saved to:", outdir)
    print("=" * 70)
