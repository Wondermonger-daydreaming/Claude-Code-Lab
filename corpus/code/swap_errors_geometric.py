"""
==========================================================================
SWAP ERRORS FROM OVERLAPPING MANIFOLDS
==========================================================================

Extension of manifold_errors.py — the proposed simulation that the archive
kept asking for but never ran.

Core prediction: When two items are encoded by overlapping neural populations,
decoding one item can be contaminated by the other's representation.
Working memory researchers call these "swap errors" and attribute them to
a distinct cognitive mechanism. The geometric theory says: no swap mechanism
needed — just overlapping manifolds.

The test: Generate "behavioral" errors in a two-item task where items share
neural resources. Look for bump(s) near the non-target item's location in
the error distribution. If they appear, the geometric model produces swap
errors without a swap process.

==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import vonmises, norm, kurtosis
from scipy.special import i0
import warnings
warnings.filterwarnings('ignore')

# ── Aesthetics (matching manifold_errors.py) ──────────────────────────
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
    'gaussian_ref': '#7f8c8d',
    'geometric': '#8e44ad',
    'fill_alpha': 0.15,
}


# ══════════════════════════════════════════════════════════════════════════
# THE TWO-ITEM ENCODING MODEL
# ══════════════════════════════════════════════════════════════════════════

def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def encode_two_items(theta1, theta2, preferred_angles, kappa, noise_sigma,
                     weight1=0.5, weight2=0.5):
    """
    Encode TWO stimuli simultaneously in a shared neural population.

    The combined response is a weighted sum of each item's activation.
    This is the standard "resource sharing" model: the same neurons
    encode both items, each getting a fraction of the gain.

    Args:
        theta1, theta2: stimulus angles for item 1 and item 2
        preferred_angles: preferred orientations of neurons
        kappa: tuning width
        noise_sigma: Gaussian noise amplitude
        weight1, weight2: gain for each item (sum = 1 for resource sharing)

    Returns:
        noisy combined response (N,)
    """
    N = len(preferred_angles)
    response1 = np.array([tuning_curve(theta1, phi, kappa) for phi in preferred_angles])
    response2 = np.array([tuning_curve(theta2, phi, kappa) for phi in preferred_angles])
    combined = weight1 * response1 + weight2 * response2
    noise = np.random.randn(N) * noise_sigma
    return combined + noise


def decode_from_single_manifold(response, preferred_angles, kappa, n_grid=500):
    """
    Decode by finding the SINGLE stimulus angle whose expected response
    (for one item alone) best matches the observed combined response.

    This is the key: the decoder assumes one item, but the encoding
    contains two. The second item's contribution acts like structured
    (non-Gaussian) noise that biases the decode.
    """
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    expected_all = np.array([[tuning_curve(t, phi, kappa)
                              for phi in preferred_angles]
                             for t in theta_grid])
    diffs = response[np.newaxis, :] - expected_all
    neg_sq_dist = -0.5 * np.sum(diffs**2, axis=1)
    return theta_grid[np.argmax(neg_sq_dist)]


# ══════════════════════════════════════════════════════════════════════════
# THE SWAP ERROR EXPERIMENT
# ══════════════════════════════════════════════════════════════════════════

def run_swap_experiment(N_neurons, kappa, noise_sigma, n_trials=5000,
                        separation=np.pi/2, weight1=0.5, weight2=0.5):
    """
    Simulate a two-item working memory experiment.

    Item 1 is always at theta1 = 0. Item 2 is at theta2 = separation.
    We decode "item 1" from the combined response.

    Returns:
        errors: decode_angle - theta1 (should cluster near 0)
        separation: the angular distance between items
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

    errors = np.zeros(n_trials)
    for t in range(n_trials):
        response = encode_two_items(theta1, theta2, preferred_angles, kappa,
                                    noise_sigma, weight1, weight2)
        # Decode using single-item manifold
        diffs = response[np.newaxis, :] - expected_all
        neg_sq_dist = -0.5 * np.sum(diffs**2, axis=1)
        decoded = theta_grid[np.argmax(neg_sq_dist)]
        error = decoded - theta1
        errors[t] = (error + np.pi) % (2 * np.pi) - np.pi

    return errors


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 7: THE SWAP ERROR DEMONSTRATION
# ══════════════════════════════════════════════════════════════════════════

def plot_swap_errors():
    """
    The central figure: do overlapping manifolds produce swap-like bumps?

    Three panels:
    1. Single item (control) — should be unimodal
    2. Two items, wide separation — should show bump near item 2
    3. Two items, narrow separation — should show larger contamination
    """
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    N_neurons = 24
    kappa = 2.0
    noise_sigma = 0.12
    n_trials = 8000

    configs = [
        (None, 'Single item\n(control)', COLORS['item1']),
        (np.pi/2, 'Two items, 90° apart', COLORS['geometric']),
        (np.pi/4, 'Two items, 45° apart', COLORS['swap_bump']),
    ]

    for ax, (sep, title, color) in zip(axes, configs):
        if sep is None:
            # Control: single item, use manifold_errors-style experiment
            preferred = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)
            n_grid = 500
            theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
            expected_all = np.array([[tuning_curve(t, phi, kappa)
                                      for phi in preferred]
                                     for t in theta_grid])
            noiseless = np.array([tuning_curve(0.0, phi, kappa) for phi in preferred])
            errors = np.zeros(n_trials)
            for t in range(n_trials):
                response = noiseless + np.random.randn(N_neurons) * noise_sigma
                diffs = response[np.newaxis, :] - expected_all
                neg_sq_dist = -0.5 * np.sum(diffs**2, axis=1)
                decoded = theta_grid[np.argmax(neg_sq_dist)]
                errors[t] = (decoded + np.pi) % (2 * np.pi) - np.pi
            print(f"  Control (single item): kurtosis = {kurtosis(errors, fisher=True):.2f}")
        else:
            print(f"  Two items, separation = {np.degrees(sep):.0f}°...")
            errors = run_swap_experiment(N_neurons, kappa, noise_sigma,
                                         n_trials, separation=sep)
            print(f"    kurtosis = {kurtosis(errors, fisher=True):.2f}")

        # Plot histogram
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3,
                label='Decoding errors')

        # Overlay Gaussian reference
        mu, sigma = np.mean(errors), np.std(errors)
        x = np.linspace(-np.pi, np.pi, 500)
        ax.plot(x, norm.pdf(x, mu, sigma), '--', color=COLORS['gaussian_ref'],
                linewidth=1.5, label='Gaussian ref', alpha=0.7)

        # Mark item 2 location if present
        if sep is not None:
            ax.axvline(x=sep, color=COLORS['item2'], linestyle=':',
                       linewidth=2, label=f'Item 2 location ({np.degrees(sep):.0f}°)')

        ax.set_xlabel('Decoding error for Item 1 (rad)')
        ax.set_ylabel('Probability density')
        ax.set_title(title, fontsize=12, fontweight='bold', color=color)
        ax.legend(fontsize=8)
        ax.set_xlim(-np.pi, np.pi)

    plt.suptitle(
        'Swap errors from overlapping manifolds:\n'
        'no swap mechanism needed — geometric contamination produces the bump',
        fontsize=13, fontweight='bold', y=1.05
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig7_swap_errors.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 7: Swap error demonstration saved")


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 8: SWAP ERRORS AS A FUNCTION OF SEPARATION
# ══════════════════════════════════════════════════════════════════════════

def plot_swap_vs_separation():
    """
    How does the "swap" contamination depend on inter-item distance?

    Mixture model prediction: swap rate is independent of separation
    (it's a random binding error).

    Geometric prediction: contamination should DECREASE with separation
    (farther items have less manifold overlap).

    This is a discriminating prediction — the two theories disagree here.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    N_neurons = 24
    kappa = 2.0
    noise_sigma = 0.12
    n_trials = 5000

    separations = np.linspace(np.pi/8, np.pi, 8)

    # Metrics: how much of the error mass falls near item 2?
    swap_fractions = []
    mean_biases = []
    kurtoses = []

    for sep in separations:
        print(f"  Separation = {np.degrees(sep):.0f}°...")
        errors = run_swap_experiment(N_neurons, kappa, noise_sigma,
                                     n_trials, separation=sep)

        # "Swap fraction": errors within ±0.3 rad of item 2's location
        swap_window = 0.3  # ~17 degrees
        near_item2 = np.abs(errors - sep) < swap_window
        swap_frac = np.mean(near_item2)
        swap_fractions.append(swap_frac)

        # Mean bias (positive = toward item 2)
        mean_biases.append(np.mean(errors))

        kurtoses.append(kurtosis(errors, fisher=True))

    sep_degrees = np.degrees(separations)

    # ── Left: Swap fraction vs separation ──
    axes[0].plot(sep_degrees, swap_fractions, 'o-', color=COLORS['swap_bump'],
                linewidth=2, markersize=8, label='Geometric model')

    # Add mixture model prediction (constant swap rate, estimated from mean)
    mean_swap = np.mean(swap_fractions)
    axes[0].axhline(y=mean_swap, linestyle='--', color=COLORS['gaussian_ref'],
                    linewidth=1.5, label=f'Mixture model pred.\n(constant swap rate)',
                    alpha=0.7)

    axes[0].set_xlabel('Inter-item separation (degrees)')
    axes[0].set_ylabel('Fraction of "swap" errors')
    axes[0].set_title('Swap fraction depends on separation\n(geometric prediction)',
                     fontsize=12, fontweight='bold')
    axes[0].legend(fontsize=9)

    # ── Right: Bias toward item 2 ──
    axes[1].plot(sep_degrees, mean_biases, 's-', color=COLORS['item2'],
                linewidth=2, markersize=8, label='Mean error bias')
    axes[1].axhline(y=0, linestyle=':', color='gray', alpha=0.5)

    axes[1].set_xlabel('Inter-item separation (degrees)')
    axes[1].set_ylabel('Mean decoding bias (rad)')
    axes[1].set_title('Systematic bias toward non-target item\n(attraction effect)',
                     fontsize=12, fontweight='bold')
    axes[1].legend(fontsize=9)

    plt.suptitle(
        'Discriminating prediction: mixture model says swap rate is constant;\n'
        'geometric model says it depends on separation (manifold overlap)',
        fontsize=13, fontweight='bold', y=1.05
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig8_swap_vs_separation.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 8: Swap vs. separation saved")

    return separations, swap_fractions, mean_biases, kurtoses


# ══════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 65)
    print("SWAP ERRORS FROM OVERLAPPING MANIFOLDS")
    print("The manifold bends the binding.")
    print("=" * 65)
    print()

    print("─── Figure 7: Swap error demonstration ───")
    plot_swap_errors()
    print()

    print("─── Figure 8: Swap errors vs. separation ───")
    seps, swap_fracs, biases, kurts = plot_swap_vs_separation()
    print()

    print("─── Summary ───")
    print(f"  Separations (°):  {[f'{np.degrees(s):.0f}' for s in seps]}")
    print(f"  Swap fractions:   {[f'{f:.3f}' for f in swap_fracs]}")
    print(f"  Mean biases:      {[f'{b:.4f}' for b in biases]}")
    print(f"  Kurtoses:         {[f'{k:.2f}' for k in kurts]}")
    print()
    print("=" * 65)
    print("If swap fraction decreases with separation: geometric model wins.")
    print("If constant: mixture model's 'binding errors' may be real.")
    print("The manifold decides. Trust the run.")
    print("=" * 65)
