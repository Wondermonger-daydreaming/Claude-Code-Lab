"""
==========================================================================
SWAP ERRORS FROM DIVISIVE NORMALIZATION
==========================================================================

The discriminating experiment: does biologically realistic gain competition
produce winner-take-all dynamics that generate swap bumps?

Previous results:
- swap_errors_geometric.py: Fixed equal weights → blending (no swaps)
- swap_errors_stochastic.py: Arbitrary Beta(0.5,0.5) → swap bumps

This simulation tests whether DIVISIVE NORMALIZATION — a standard neural
computation (Carandini & Heeger, 2012) — naturally produces the winner-
take-all dynamics needed for swap errors.

The normalization model:
    r_i = drive_i^n / (sigma^n + sum_j(drive_j^n))

When two items activate overlapping populations, normalization suppresses
the weaker signal. With noise, which item "wins" varies trial-to-trial.
This could produce the bimodal distributions that characterize swap errors
WITHOUT any arbitrary Beta distribution — just neural physics.

If this works: swap errors are geometric ALL THE WAY DOWN.
If not: something beyond population geometry is needed.
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, kurtosis
from scipy.special import i0
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
    'item1': '#2d5a7b',
    'item2': '#c0392b',
    'swap_bump': '#e67e22',
    'normalized': '#27ae60',
    'gaussian_ref': '#7f8c8d',
    'geometric': '#8e44ad',
}


def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def divisive_normalization(drives, sigma, n_exp):
    """
    Divisive normalization (Carandini & Heeger, 2012).

    r_i = drive_i^n / (sigma^n + sum(drive_j^n))

    Args:
        drives: array of input drives (N,) — non-negative
        sigma: semi-saturation constant (controls competition strength)
        n_exp: exponent (higher = sharper competition)

    Returns:
        normalized responses (N,)
    """
    drives_pos = np.maximum(drives, 0)  # rectify
    numerator = drives_pos ** n_exp
    denominator = sigma ** n_exp + np.sum(numerator)
    return numerator / denominator


def encode_two_items_normalized(theta1, theta2, preferred_angles, kappa,
                                 noise_sigma, sigma_norm, n_exp,
                                 gain1=1.0, gain2=1.0):
    """
    Encode two items with divisive normalization.

    Each item generates a drive signal. Noise is added to drives BEFORE
    normalization (this is key — pre-normalization noise is what creates
    trial-to-trial winner variability).

    The normalization then creates competition: whichever item happens to
    have higher drive (due to noise) gets amplified; the other gets
    suppressed. Stronger normalization (lower sigma, higher n) = more
    winner-take-all.
    """
    N = len(preferred_angles)

    # Compute drive from each item
    drive1 = gain1 * np.array([tuning_curve(theta1, phi, kappa)
                                for phi in preferred_angles])
    drive2 = gain2 * np.array([tuning_curve(theta2, phi, kappa)
                                for phi in preferred_angles])

    # Add noise to drives BEFORE normalization
    noisy_drive1 = drive1 + np.random.randn(N) * noise_sigma
    noisy_drive2 = drive2 + np.random.randn(N) * noise_sigma

    # Total drive (both items compete)
    total_drive = noisy_drive1 + noisy_drive2

    # Apply divisive normalization to combined activity
    normalized = divisive_normalization(total_drive, sigma_norm, n_exp)

    return normalized


def run_normalization_experiment(N_neurons, kappa, noise_sigma,
                                 sigma_norm, n_exp, n_trials,
                                 separation):
    """
    Two-item experiment with divisive normalization.

    Decode by matching normalized response to single-item templates.
    """
    preferred_angles = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)
    theta1 = 0.0
    theta2 = separation

    # Precompute single-item decode manifold (no normalization, no noise)
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    expected_all = np.array([[tuning_curve(t, phi, kappa)
                              for phi in preferred_angles]
                             for t in theta_grid])

    errors = np.zeros(n_trials)

    for t in range(n_trials):
        response = encode_two_items_normalized(
            theta1, theta2, preferred_angles, kappa,
            noise_sigma, sigma_norm, n_exp
        )

        # ML decode against single-item manifold
        diffs = response[np.newaxis, :] - expected_all
        neg_sq_dist = -0.5 * np.sum(diffs**2, axis=1)
        decoded = theta_grid[np.argmax(neg_sq_dist)]
        error = decoded - theta1
        errors[t] = (error + np.pi) % (2 * np.pi) - np.pi

    return errors


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 10: NORMALIZATION STRENGTH AND SWAP ERRORS
# ══════════════════════════════════════════════════════════════════════════

def plot_normalization_sweep():
    """
    The key figure: how does normalization strength affect swap errors?

    Three regimes:
    1. Weak normalization (high sigma) → behaves like equal-weight blending
    2. Moderate normalization → partial competition
    3. Strong normalization (low sigma) → winner-take-all → swap bumps?
    """
    fig, axes = plt.subplots(2, 3, figsize=(17, 10))

    N_neurons = 24
    kappa = 2.0
    noise_sigma = 0.04  # moderate noise on drives
    n_trials = 10000
    separation = np.pi / 2  # 90 degrees
    n_exp = 2.0  # quadratic normalization

    configs = [
        (2.0,  'Weak normalization\n(σ=2.0, near-linear)', COLORS['item1']),
        (0.3,  'Moderate normalization\n(σ=0.3, competitive)', COLORS['geometric']),
        (0.05, 'Strong normalization\n(σ=0.05, winner-take-all)', COLORS['swap_bump']),
    ]

    for col, (sigma_norm, title, color) in enumerate(configs):
        print(f"  Running σ_norm={sigma_norm} ({n_trials} trials)...")
        errors = run_normalization_experiment(
            N_neurons, kappa, noise_sigma,
            sigma_norm, n_exp, n_trials, separation
        )

        # Top row: error distributions
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 100)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)

        # Mark item locations
        ax.axvline(x=0, color=COLORS['item1'], linestyle=':',
                   linewidth=2, label='Item 1 (target)', alpha=0.7)
        ax.axvline(x=separation, color=COLORS['item2'], linestyle=':',
                   linewidth=2, label='Item 2 (non-target)', alpha=0.7)

        # Stats
        k = kurtosis(errors, fisher=True)
        near_item1 = np.abs(errors) < 0.3
        near_item2 = np.abs(errors - separation) < 0.3
        correct_pct = 100 * np.mean(near_item1)
        swap_pct = 100 * np.mean(near_item2)
        mean_bias = np.mean(errors)

        ax.set_title(title, fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('Decoding error for Item 1 (rad)')
        ax.set_ylabel('Probability density')
        ax.legend(fontsize=7, loc='upper left')
        ax.set_xlim(-np.pi, np.pi)

        ax.text(0.97, 0.93,
                f'Near target: {correct_pct:.1f}%\n'
                f'Near non-target: {swap_pct:.1f}%\n'
                f'Mean bias: {mean_bias:.3f}\n'
                f'Kurtosis: {k:.2f}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.8))

        # Bottom row: show what normalization does to a single trial
        ax2 = axes[1, col]

        # Generate one example trial showing the competition
        preferred_angles = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)
        drive1 = np.array([tuning_curve(0.0, phi, kappa)
                           for phi in preferred_angles])
        drive2 = np.array([tuning_curve(separation, phi, kappa)
                           for phi in preferred_angles])

        # Show drives and normalized output
        x_neurons = np.arange(N_neurons)
        ax2.bar(x_neurons - 0.2, drive1, 0.35, alpha=0.4,
                color=COLORS['item1'], label='Item 1 drive')
        ax2.bar(x_neurons + 0.2, drive2, 0.35, alpha=0.4,
                color=COLORS['item2'], label='Item 2 drive')

        # Normalized combined (no noise, for visualization)
        combined = drive1 + drive2
        normalized = divisive_normalization(combined, sigma_norm, n_exp)
        ax2.plot(x_neurons, normalized, 'o-', color=color,
                 linewidth=2, markersize=4, label='Normalized output')

        ax2.set_xlabel('Neuron index')
        ax2.set_ylabel('Response')
        ax2.set_title(f'Neural responses (σ_norm={sigma_norm})',
                     fontsize=10, color=color)
        ax2.legend(fontsize=7, loc='upper right')

    plt.suptitle(
        'Divisive normalization: does biologically realistic competition\n'
        'produce winner-take-all swap errors?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig10_normalization_swaps.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 10: Normalization sweep saved")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 11: NORMALIZATION EXPONENT EFFECT
# ══════════════════════════════════════════════════════════════════════════

def plot_exponent_effect():
    """
    How does the normalization exponent affect swap probability?

    n=1: sublinear (soft competition)
    n=2: quadratic (standard)
    n=4: supralinear (sharp competition)

    Higher exponents should produce stronger winner-take-all and more swaps.
    """
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    N_neurons = 24
    kappa = 2.0
    noise_sigma = 0.04
    n_trials = 10000
    separation = np.pi / 2
    sigma_norm = 0.15  # moderate normalization

    exponents = [1.0, 2.0, 4.0]
    colors = [COLORS['item1'], COLORS['geometric'], COLORS['swap_bump']]
    labels = ['n=1 (soft)', 'n=2 (standard)', 'n=4 (sharp)']

    for ax, n_exp, color, label in zip(axes, exponents, colors, labels):
        print(f"  Running n_exp={n_exp} ({n_trials} trials)...")
        errors = run_normalization_experiment(
            N_neurons, kappa, noise_sigma,
            sigma_norm, n_exp, n_trials, separation
        )

        bins = np.linspace(-np.pi, np.pi, 100)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)

        ax.axvline(x=0, color=COLORS['item1'], linestyle=':',
                   linewidth=2, alpha=0.7)
        ax.axvline(x=separation, color=COLORS['item2'], linestyle=':',
                   linewidth=2, alpha=0.7)

        k = kurtosis(errors, fisher=True)
        near_item2 = np.abs(errors - separation) < 0.3
        swap_pct = 100 * np.mean(near_item2)
        near_item1 = np.abs(errors) < 0.3
        correct_pct = 100 * np.mean(near_item1)

        ax.set_title(f'Exponent {label}', fontsize=12,
                     fontweight='bold', color=color)
        ax.set_xlabel('Decoding error (rad)')
        ax.set_ylabel('Probability density')
        ax.set_xlim(-np.pi, np.pi)

        ax.text(0.97, 0.93,
                f'Near target: {correct_pct:.1f}%\n'
                f'Near non-target: {swap_pct:.1f}%\n'
                f'Kurtosis: {k:.2f}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.8))

    plt.suptitle(
        'Normalization exponent: sharper competition → more swap-like errors?',
        fontsize=13, fontweight='bold', y=1.03
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig11_exponent_effect.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 11: Exponent effect saved")


# ══════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 65)
    print("DIVISIVE NORMALIZATION AND SWAP ERRORS")
    print("Does neural physics produce the bump?")
    print("=" * 65)
    print()

    print("─── Figure 10: Normalization strength sweep ───")
    plot_normalization_sweep()
    print()

    print("─── Figure 11: Exponent effect ───")
    plot_exponent_effect()
    print()

    print("=" * 65)
    print("If strong normalization → bimodal bumps:")
    print("  Swap errors are geometric ALL THE WAY DOWN.")
    print("If still unimodal:")
    print("  The competition needs something beyond gain control.")
    print("The manifold decides. Trust the run.")
    print("=" * 65)
