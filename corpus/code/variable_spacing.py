"""
==========================================================================
VARIABLE SPACING: A TESTABLE PREDICTION
==========================================================================

Simulation #9 in the cascade.

The coupled ring attractor model makes a prediction that simple mixture
models cannot: when items are UNEQUALLY SPACED, swap errors should be
biased toward the CLOSER non-target.

Why? Cross-inhibition is mediated through mean activity, but the tuning
curves of nearby items overlap more. Two close items compete more
intensely → the closer non-target is a stronger competitor → it wins
more swap trials.

Simple mixture models (e.g., Zhang & Luck 2008) are position-invariant:
they don't distinguish between close and far non-targets.

This experiment:
  1. Three items: target at 0°, close non-target at 40°, far at 160°
  2. Cue the target
  3. Classify swaps: how many go to close vs. far non-target?
  4. Prediction: more swaps to the close non-target

If confirmed, this is a UNIQUE prediction of the coupled attractor model.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 2026
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
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
    'target': '#2d5a7b',
    'close': '#c0392b',
    'far': '#27ae60',
    'equal': '#8e44ad',
}


def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def tuning_curve(theta, preferred, kappa):
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_within_weights(preferred_angles, J_0, J_1):
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N


def run_trial(thetas, preferred, kappa, W_within, J_cross, noise_sigma,
              dt, tau, n_steps, stim_steps, cue_onset, cue_gain,
              cue_target, input_gain, r_max, beta, h0):
    """Three coupled ring attractors."""
    N = len(preferred)
    n_nets = len(thetas)

    drives = []
    for theta in thetas:
        d = input_gain * np.array([tuning_curve(theta, phi, kappa)
                                    for phi in preferred])
        drives.append(d)

    cue_drive = cue_gain * np.array([tuning_curve(thetas[cue_target], phi, kappa)
                                      for phi in preferred])

    rs = [np.ones(N) * 0.1 for _ in range(n_nets)]

    for step in range(n_steps):
        exts = []
        for i in range(n_nets):
            if step < stim_steps:
                exts.append(drives[i])
            elif step >= cue_onset and i == cue_target:
                exts.append(cue_drive)
            else:
                exts.append(np.zeros(N))

        mean_activities = [np.mean(r) for r in rs]
        cross_inhibs = []
        for i in range(n_nets):
            other_mean = sum(mean_activities[j] for j in range(n_nets) if j != i) / (n_nets - 1)
            cross_inhibs.append(-J_cross * other_mean)

        new_rs = []
        for i in range(n_nets):
            noise = np.random.randn(N) * noise_sigma
            h = W_within @ rs[i] + exts[i] + cross_inhibs[i] + noise
            f = sigmoid(h, r_max, beta, h0)
            dr = (-rs[i] + f) * (dt / tau)
            new_rs.append(np.maximum(0, rs[i] + dr))
        rs = new_rs

    return rs


def decode(response, preferred, kappa):
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


def classify_error(error, thetas, target_idx, threshold=0.4):
    """Classify a decode error as target, close-swap, far-swap, or other."""
    target_theta = thetas[target_idx]
    if abs(error) < threshold:
        return 'target'

    # Check each non-target
    non_target_errors = {}
    for i, theta in enumerate(thetas):
        if i == target_idx:
            continue
        expected_error = (theta - target_theta + np.pi) % (2 * np.pi) - np.pi
        actual_dist = (error - expected_error + np.pi) % (2 * np.pi) - np.pi
        non_target_errors[i] = abs(actual_dist)

    # Which non-target is closest to the decode?
    closest_nt = min(non_target_errors, key=non_target_errors.get)
    if non_target_errors[closest_nt] < threshold:
        return f'swap_{closest_nt}'
    return 'other'


# ═══════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════

def run_spacing_experiment():
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)

    dt, tau = 1.0, 10.0
    n_trials = 2000
    n_steps = 500
    stim_steps = 100
    cue_onset = 150
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0
    J_0, J_1 = 1.0, 6.0
    J_cross = 0.5
    cue_gain = 0.02  # Operating at the cliff

    W_within = build_within_weights(preferred, J_0, J_1)

    # Spacing conditions
    conditions = [
        {
            'name': 'Equal (120°/120°)',
            'thetas': [0.0, 2*np.pi/3, -2*np.pi/3],  # 120° apart
            'color': COLORS['equal'],
        },
        {
            'name': 'Close-Far (40°/160°)',
            'thetas': [0.0, np.radians(40), np.radians(160)],  # 40° and 160°
            'color': COLORS['close'],
        },
        {
            'name': 'Close-Far (60°/180°)',
            'thetas': [0.0, np.radians(60), np.pi],  # 60° and 180°
            'color': COLORS['far'],
        },
        {
            'name': 'Very close (30°/150°)',
            'thetas': [0.0, np.radians(30), np.radians(150)],
            'color': COLORS['target'],
        },
    ]

    all_results = []

    for cond in conditions:
        thetas = cond['thetas']
        name = cond['name']
        print(f"\n  Condition: {name}")
        print(f"    Items at: {[f'{np.degrees(t):.0f}°' for t in thetas]}")

        errors = np.zeros(n_trials)
        classifications = {'target': 0, 'other': 0}
        for i in range(len(thetas)):
            if i > 0:
                classifications[f'swap_{i}'] = 0

        for t in range(n_trials):
            rs = run_trial(
                thetas, preferred, kappa, W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps, cue_onset, cue_gain, 0,
                input_gain, r_max, beta, h0
            )

            combined = sum(rs)
            decoded = decode(combined, preferred, kappa)
            error = (decoded - thetas[0] + np.pi) % (2 * np.pi) - np.pi
            errors[t] = error

            cat = classify_error(error, thetas, 0)
            if cat in classifications:
                classifications[cat] += 1
            else:
                classifications['other'] += 1

        # Compute percentages
        pcts = {k: 100 * v / n_trials for k, v in classifications.items()}

        # Angular distances to non-targets
        sep_1 = abs(np.degrees((thetas[1] - thetas[0] + np.pi) % (2 * np.pi) - np.pi))
        sep_2 = abs(np.degrees((thetas[2] - thetas[0] + np.pi) % (2 * np.pi) - np.pi))

        swap_1 = pcts.get('swap_1', 0)
        swap_2 = pcts.get('swap_2', 0)

        print(f"    Target: {pcts['target']:.1f}%")
        print(f"    Swap to item 2 ({sep_1:.0f}°): {swap_1:.1f}%")
        print(f"    Swap to item 3 ({sep_2:.0f}°): {swap_2:.1f}%")
        print(f"    Other: {pcts['other']:.1f}%")

        if swap_1 > 0 and swap_2 > 0:
            ratio = swap_1 / swap_2
            closer = "item 2" if sep_1 < sep_2 else "item 3"
            print(f"    Swap ratio (item2/item3): {ratio:.2f}")
            if sep_1 < sep_2:
                print(f"    → Closer item ({closer}, {min(sep_1,sep_2):.0f}°) gets {'MORE' if ratio > 1.2 else 'similar'} swaps")
            else:
                print(f"    → Closer item ({closer}, {min(sep_1,sep_2):.0f}°) gets {'MORE' if ratio < 0.8 else 'similar'} swaps")

        all_results.append({
            'name': name, 'thetas': thetas, 'errors': errors,
            'pcts': pcts, 'swap_1': swap_1, 'swap_2': swap_2,
            'sep_1': sep_1, 'sep_2': sep_2, 'color': cond['color'],
        })

    return all_results


def plot_results(all_results):
    """Two-panel figure: error distributions + swap ratio summary."""

    n_conds = len(all_results)
    fig, axes = plt.subplots(2, n_conds, figsize=(4.5 * n_conds, 10),
                              gridspec_kw={'height_ratios': [2, 1]})

    # Top row: error distributions
    for col, res in enumerate(all_results):
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(res['errors'], bins=bins, density=True, alpha=0.6,
                color=res['color'], edgecolor='white', linewidth=0.3)

        # Mark item locations
        for i, theta in enumerate(res['thetas']):
            expected_error = (theta - res['thetas'][0] + np.pi) % (2 * np.pi) - np.pi
            colors = [COLORS['target'], COLORS['close'], COLORS['far']]
            labels = ['Target', f"NT ({res['sep_1']:.0f}°)", f"NT ({res['sep_2']:.0f}°)"]
            ax.axvline(x=expected_error, color=colors[i], ls=':', lw=2,
                       alpha=0.7, label=labels[i])

        ax.set_title(res['name'], fontsize=12, fontweight='bold')
        ax.set_xlabel('Decode error (rad)')
        if col == 0:
            ax.set_ylabel('Density')
        ax.set_xlim(-np.pi, np.pi)
        ax.legend(fontsize=7)

        # Stats box
        ax.text(0.97, 0.93,
                f'Target: {res["pcts"]["target"]:.1f}%\n'
                f'Swap({res["sep_1"]:.0f}°): {res["swap_1"]:.1f}%\n'
                f'Swap({res["sep_2"]:.0f}°): {res["swap_2"]:.1f}%',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor='gray', alpha=0.8))

    # Bottom row: swap ratio bar charts
    for col, res in enumerate(all_results):
        ax = axes[1, col]
        separations = [res['sep_1'], res['sep_2']]
        swaps = [res['swap_1'], res['swap_2']]
        colors_bar = [COLORS['close'], COLORS['far']]

        bars = ax.bar(range(2), swaps, color=colors_bar, alpha=0.7, edgecolor='white')
        ax.set_xticks(range(2))
        ax.set_xticklabels([f"{s:.0f}°" for s in separations])
        ax.set_xlabel('Angular separation from target')
        if col == 0:
            ax.set_ylabel('Swap rate (%)')

        # Ratio annotation
        if swaps[0] > 0 and swaps[1] > 0:
            ratio = swaps[0] / swaps[1]
            ax.text(0.5, 0.85, f'Ratio: {ratio:.2f}',
                    transform=ax.transAxes, ha='center', fontsize=10,
                    fontweight='bold')

    plt.suptitle(
        'Sim #9: Variable spacing — closer non-targets attract more swaps?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig26_variable_spacing.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("\n✓ Figure 26 saved: variable spacing experiment")

    # Summary bar chart: swap ratio vs separation asymmetry
    fig2, ax = plt.subplots(1, 1, figsize=(8, 5))

    for res in all_results:
        if res['sep_1'] != res['sep_2']:
            closer_swap = res['swap_1'] if res['sep_1'] < res['sep_2'] else res['swap_2']
            farther_swap = res['swap_2'] if res['sep_1'] < res['sep_2'] else res['swap_1']
            closer_sep = min(res['sep_1'], res['sep_2'])
            farther_sep = max(res['sep_1'], res['sep_2'])
            asymmetry = farther_sep - closer_sep

            ax.plot(asymmetry, closer_swap / max(farther_swap, 0.1), 'o',
                    color=res['color'], ms=12, label=res['name'])

    ax.axhline(y=1.0, color='gray', ls=':', lw=1.5, alpha=0.5,
               label='Equal swaps (mixture model prediction)')
    ax.set_xlabel('Spacing asymmetry (far° - close°)', fontsize=12)
    ax.set_ylabel('Swap ratio (close / far)', fontsize=12)
    ax.set_title('Proximity bias: closer non-targets attract more swaps',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig27_proximity_bias.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 27 saved: proximity bias summary")


if __name__ == '__main__':
    print("=" * 65)
    print("SIM #9: VARIABLE SPACING")
    print("Does angular proximity bias swap errors?")
    print("A prediction that distinguishes coupled attractors from mixture models")
    print("=" * 65)

    results = run_spacing_experiment()

    print("\n─── Plotting ───")
    plot_results(results)

    print()
    print("═══ KEY PREDICTION ═══")
    print()
    print("  If the coupled attractor model is correct:")
    print("    Closer non-targets should attract MORE swap errors")
    print("    (because their tuning curves overlap more with the target)")
    print()
    print("  If the mixture model is correct:")
    print("    Swap rate should be INDEPENDENT of non-target distance")
    print("    (because swaps are random reassignments, not competition)")
    print()
    print("  This is a testable prediction with existing psychophysics paradigms.")
    print()

    # Check prediction
    close_far = [r for r in results if 'Close-Far' in r['name']]
    for r in close_far:
        closer = min(r['sep_1'], r['sep_2'])
        farther = max(r['sep_1'], r['sep_2'])
        closer_swap = r['swap_1'] if r['sep_1'] < r['sep_2'] else r['swap_2']
        farther_swap = r['swap_2'] if r['sep_1'] < r['sep_2'] else r['swap_1']
        ratio = closer_swap / max(farther_swap, 0.1)
        print(f"  {r['name']}: close({closer:.0f}°)={closer_swap:.1f}% vs far({farther:.0f}°)={farther_swap:.1f}%  ratio={ratio:.2f}")

    print()
    print("=" * 65)
