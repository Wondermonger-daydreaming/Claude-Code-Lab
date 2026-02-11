"""
==========================================================================
SWAP ERRORS: STOCHASTIC RESOURCE ALLOCATION
==========================================================================

Follow-up to swap_errors_geometric.py.

The equal-weight model produced blending, not swapping.
Hypothesis: if resource allocation is stochastic (one item randomly gets
most of the gain on each trial), the error distribution should become
BIMODAL — bumps at both item 1 and item 2 locations.

This tests whether swap errors require stochastic dynamics on top of
manifold geometry.
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, kurtosis, beta
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


def tuning_curve(theta, preferred, kappa):
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def run_stochastic_swap(N_neurons, kappa, noise_sigma, n_trials,
                        separation, alpha_beta=2.0, beta_beta=2.0):
    """
    Two-item experiment with STOCHASTIC resource allocation.

    On each trial, draw weight w ~ Beta(alpha, beta).
    Item 1 gets weight w, item 2 gets weight (1-w).

    Beta(2, 2): symmetric, moderate variance — weights cluster around 0.5
    Beta(0.5, 0.5): U-shaped — weights near 0 or 1 (winner-take-all)
    Beta(1, 1): uniform — any allocation equally likely
    """
    preferred_angles = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)
    theta1 = 0.0
    theta2 = separation

    # Precompute single-item manifold for decoding
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    expected_all = np.array([[tuning_curve(t, phi, kappa)
                              for phi in preferred_angles]
                             for t in theta_grid])

    # Precompute each item's noiseless response
    response1 = np.array([tuning_curve(theta1, phi, kappa) for phi in preferred_angles])
    response2 = np.array([tuning_curve(theta2, phi, kappa) for phi in preferred_angles])

    errors = np.zeros(n_trials)
    weights_used = np.zeros(n_trials)

    for t in range(n_trials):
        # Stochastic resource allocation
        w = np.random.beta(alpha_beta, beta_beta)
        weights_used[t] = w
        combined = w * response1 + (1 - w) * response2
        noise = np.random.randn(N_neurons) * noise_sigma
        response = combined + noise

        # ML decode (single-item manifold)
        diffs = response[np.newaxis, :] - expected_all
        neg_sq_dist = -0.5 * np.sum(diffs**2, axis=1)
        decoded = theta_grid[np.argmax(neg_sq_dist)]
        error = decoded - theta1
        errors[t] = (error + np.pi) % (2 * np.pi) - np.pi

    return errors, weights_used


def plot_stochastic_comparison():
    """
    Compare three resource allocation regimes.
    """
    fig, axes = plt.subplots(2, 3, figsize=(17, 10))

    N_neurons = 24
    kappa = 2.0
    noise_sigma = 0.10
    n_trials = 10000
    separation = np.pi / 2  # 90 degrees

    configs = [
        (2.0, 2.0, 'Beta(2,2): Moderate variance\n(clustered around 0.5)', '#2d5a7b'),
        (1.0, 1.0, 'Beta(1,1): Uniform allocation\n(any split equally likely)', '#8e44ad'),
        (0.5, 0.5, 'Beta(0.5,0.5): Winner-take-all\n(one item dominates)', '#e67e22'),
    ]

    for col, (a, b, title, color) in enumerate(configs):
        print(f"  Running Beta({a},{b}) regime ({n_trials} trials)...")
        errors, weights = run_stochastic_swap(
            N_neurons, kappa, noise_sigma, n_trials, separation, a, b
        )

        # Top row: error distributions
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 100)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)

        # Mark item locations
        ax.axvline(x=0, color='#2d5a7b', linestyle=':', linewidth=2,
                   label='Item 1 (target)', alpha=0.7)
        ax.axvline(x=separation, color='#c0392b', linestyle=':', linewidth=2,
                   label='Item 2 (non-target)', alpha=0.7)

        # Gaussian reference
        mu, sigma = np.mean(errors), np.std(errors)
        x = np.linspace(-np.pi, np.pi, 500)
        ax.plot(x, norm.pdf(x, mu, sigma), '--', color='gray',
                linewidth=1, alpha=0.5)

        k = kurtosis(errors, fisher=True)
        ax.set_title(title, fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('Decoding error for Item 1 (rad)')
        ax.set_ylabel('Probability density')
        ax.legend(fontsize=7, loc='upper left')
        ax.set_xlim(-np.pi, np.pi)

        # Count errors near item 2
        near_item2 = np.abs(errors - separation) < 0.3
        swap_pct = 100 * np.mean(near_item2)
        near_item1 = np.abs(errors) < 0.3
        correct_pct = 100 * np.mean(near_item1)
        ax.text(0.97, 0.93,
                f'Near target: {correct_pct:.1f}%\n'
                f'Near non-target: {swap_pct:.1f}%\n'
                f'Kurtosis: {k:.2f}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.8))

        # Bottom row: weight distributions
        ax2 = axes[1, col]
        ax2.hist(weights, bins=50, density=True, alpha=0.5,
                 color=color, edgecolor='white', linewidth=0.3)
        w_x = np.linspace(0, 1, 200)
        if a > 0 and b > 0:
            ax2.plot(w_x, beta.pdf(w_x, a, b), color=color, linewidth=2)
        ax2.set_xlabel('Weight for Item 1')
        ax2.set_ylabel('Density')
        ax2.set_title(f'Weight distribution: Beta({a},{b})',
                     fontsize=10, color=color)
        ax2.set_xlim(0, 1)

    plt.suptitle(
        'Stochastic resource allocation: does winner-take-all produce swap bumps?\n'
        f'(24 neurons, κ=2.0, σ={noise_sigma}, items 90° apart)',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig9_stochastic_swaps.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 9: Stochastic swap comparison saved")


if __name__ == '__main__':
    print("=" * 65)
    print("STOCHASTIC RESOURCE ALLOCATION & SWAP ERRORS")
    print("Does winner-take-all produce the bump?")
    print("=" * 65)
    print()
    plot_stochastic_comparison()
    print()
    print("=" * 65)
    print("If Beta(0.5,0.5) shows bimodal bumps: swaps need dynamics.")
    print("If still unimodal: something else is going on.")
    print("Trust the run.")
    print("=" * 65)
