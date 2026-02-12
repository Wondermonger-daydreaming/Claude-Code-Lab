"""
==========================================================================
SWAP ERRORS: THREE-ITEM SET SIZE
==========================================================================

Simulation #8 in the cascade.

The critical test: does the coupled ring attractor model generalize
to set size 3? The literature shows swap rates INCREASE with set size.
If the model can't reproduce this, the two-item results are a curiosity.

Model: THREE separate ring attractor networks (A, B, C), each encoding
one item. All-to-all mutual inhibition with strength J_cross.

Phase 1 (stimulus): All three networks driven simultaneously
Phase 2 (blank): No drive, competition begins
Phase 3 (cue): Low-amplitude drive to Network A (target)

Key questions:
  1. Does the model produce swap errors at set size 3?
  2. Is the swap rate HIGHER than at set size 2?
  3. Are swaps split between the two non-targets?
  4. Does the behavioral range still exist?

Literature benchmarks:
  Set size 2: ~5-15% swaps (Zhang & Luck 2008)
  Set size 3: ~15-25% swaps
  Set size 6: ~30-40% swaps
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
    'item1': '#2d5a7b',
    'item2': '#c0392b',
    'item3': '#27ae60',
    'correct': '#2d5a7b',
    'swap': '#e67e22',
    'blend': '#95a5a6',
}


def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def tuning_curve(theta, preferred, kappa):
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_within_weights(preferred_angles, J_0, J_1):
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N


def run_three_item_trial(thetas, preferred, kappa,
                         W_within, J_cross, noise_sigma,
                         dt, tau, n_steps, stim_steps,
                         cue_onset, cue_gain, cue_target,
                         input_gain, r_max, beta, h0):
    """
    Three coupled ring attractors with mutual inhibition.

    thetas: list of 3 stimulus angles
    cue_target: index (0, 1, or 2) of the cued network
    """
    N = len(preferred)
    n_nets = 3

    # Feedforward drives
    drives = []
    for theta in thetas:
        d = input_gain * np.array([tuning_curve(theta, phi, kappa)
                                    for phi in preferred])
        drives.append(d)

    # Cue drive for target
    cue_drive = cue_gain * np.array([tuning_curve(thetas[cue_target], phi, kappa)
                                      for phi in preferred])

    # Initialize all networks
    rs = [np.ones(N) * 0.1 for _ in range(n_nets)]

    for step in range(n_steps):
        # Phase-dependent input
        exts = []
        for i in range(n_nets):
            if step < stim_steps:
                exts.append(drives[i])
            elif step >= cue_onset and i == cue_target:
                exts.append(cue_drive)
            else:
                exts.append(np.zeros(N))

        # Cross-inhibition: each network inhibited by mean of OTHER networks
        mean_activities = [np.mean(r) for r in rs]
        cross_inhibs = []
        for i in range(n_nets):
            other_mean = sum(mean_activities[j] for j in range(n_nets) if j != i) / (n_nets - 1)
            cross_inhibs.append(-J_cross * other_mean)

        # Update each network
        new_rs = []
        for i in range(n_nets):
            noise = np.random.randn(N) * noise_sigma
            h = W_within @ rs[i] + exts[i] + cross_inhibs[i] + noise
            f = sigmoid(h, r_max, beta, h0)
            dr = (-rs[i] + f) * (dt / tau)
            new_rs.append(np.maximum(0, rs[i] + dr))
        rs = new_rs

    return rs


def run_three_item_trial_with_history(thetas, preferred, kappa,
                                       W_within, J_cross, noise_sigma,
                                       dt, tau, n_steps, stim_steps,
                                       cue_onset, cue_gain, cue_target,
                                       input_gain, r_max, beta, h0):
    """Same but returns temporal dynamics."""
    N = len(preferred)
    n_nets = 3

    drives = []
    for theta in thetas:
        d = input_gain * np.array([tuning_curve(theta, phi, kappa)
                                    for phi in preferred])
        drives.append(d)

    cue_drive = cue_gain * np.array([tuning_curve(thetas[cue_target], phi, kappa)
                                      for phi in preferred])

    rs = [np.ones(N) * 0.1 for _ in range(n_nets)]
    activities = [np.zeros(n_steps) for _ in range(n_nets)]

    for step in range(n_steps):
        exts = []
        for i in range(n_nets):
            if step < stim_steps:
                exts.append(drives[i])
            elif step >= cue_onset and i == cue_target:
                exts.append(cue_drive)
            else:
                exts.append(np.zeros(N))

        mean_activities_now = [np.mean(r) for r in rs]
        cross_inhibs = []
        for i in range(n_nets):
            other_mean = sum(mean_activities_now[j] for j in range(n_nets) if j != i) / (n_nets - 1)
            cross_inhibs.append(-J_cross * other_mean)

        new_rs = []
        for i in range(n_nets):
            noise = np.random.randn(N) * noise_sigma
            h = W_within @ rs[i] + exts[i] + cross_inhibs[i] + noise
            f = sigmoid(h, r_max, beta, h0)
            dr = (-rs[i] + f) * (dt / tau)
            new_rs.append(np.maximum(0, rs[i] + dr))

        rs = new_rs
        for i in range(n_nets):
            activities[i][step] = np.mean(rs[i])

    return rs, activities


def decode(response, preferred, kappa):
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


def decode_combined(rs, preferred, kappa, target_theta):
    """Decode from sum of all network responses."""
    combined = sum(rs)
    decoded = decode(combined, preferred, kappa)
    error = decoded - target_theta
    return (error + np.pi) % (2 * np.pi) - np.pi


# ═══════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════

def run_experiment():
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)

    # Three items equally spaced (120° apart)
    thetas = [0.0, 2 * np.pi / 3, -2 * np.pi / 3]

    dt, tau = 1.0, 10.0
    n_trials = 2000
    n_steps = 500
    stim_steps = 100
    cue_onset = 150
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0
    J_0, J_1 = 1.0, 6.0
    J_cross = 0.5  # Same as two-item model
    cue_target = 0  # Cue network A

    W_within = build_within_weights(preferred, J_0, J_1)

    # Sweep cue gains
    cue_gains = [0.0, 0.01, 0.02, 0.03, 0.05, 0.1]

    results = []
    for cg in cue_gains:
        label = f'cue={cg:.2f}' if cg > 0 else 'no cue'
        print(f"  {label} — {n_trials} trials...")

        errors = np.zeros(n_trials)
        winners = {'A': 0, 'B': 0, 'C': 0, 'tie': 0}

        for t in range(n_trials):
            rs = run_three_item_trial(
                thetas, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps,
                cue_onset, cg, cue_target,
                input_gain, r_max, beta, h0
            )

            # Which network won?
            sums = [np.sum(r) for r in rs]
            max_idx = np.argmax(sums)
            if sums[max_idx] > 1.5 * np.median(sums):
                winners[['A', 'B', 'C'][max_idx]] += 1
            else:
                winners['tie'] += 1

            errors[t] = decode_combined(rs, preferred, kappa, thetas[cue_target])

        # Classify errors
        near_target = 100 * np.mean(np.abs(errors) < 0.4)
        near_nt1 = 100 * np.mean(np.abs(errors - (thetas[1] - thetas[0])) < 0.4)
        near_nt2 = 100 * np.mean(np.abs(errors - (thetas[2] - thetas[0])) < 0.4)
        # Wrap for circular comparison
        err_to_nt1 = (errors - (thetas[1] - thetas[0]) + np.pi) % (2 * np.pi) - np.pi
        err_to_nt2 = (errors - (thetas[2] - thetas[0]) + np.pi) % (2 * np.pi) - np.pi
        near_nt1 = 100 * np.mean(np.abs(err_to_nt1) < 0.4)
        near_nt2 = 100 * np.mean(np.abs(err_to_nt2) < 0.4)
        total_swap = near_nt1 + near_nt2

        pct_A = 100 * winners['A'] / n_trials
        pct_B = 100 * winners['B'] / n_trials
        pct_C = 100 * winners['C'] / n_trials

        print(f"    Target: {near_target:.1f}%  Swap(B): {near_nt1:.1f}%  Swap(C): {near_nt2:.1f}%  Total swap: {total_swap:.1f}%")
        print(f"    Winners — A: {pct_A:.1f}%  B: {pct_B:.1f}%  C: {pct_C:.1f}%")

        results.append({
            'cue_gain': cg, 'label': label, 'errors': errors,
            'near_target': near_target, 'near_nt1': near_nt1,
            'near_nt2': near_nt2, 'total_swap': total_swap,
            'pct_A': pct_A, 'pct_B': pct_B, 'pct_C': pct_C,
        })

    return results, thetas, preferred, kappa, W_within, J_cross, noise_sigma, \
           dt, tau, n_steps, stim_steps, cue_onset, input_gain, r_max, beta, h0


def plot_results(results, thetas, preferred, kappa, W_within, J_cross,
                 noise_sigma, dt, tau, n_steps, stim_steps, cue_onset,
                 input_gain, r_max, beta, h0):
    """Three-panel figure."""

    # Select 4 conditions to show
    show_gains = [0.0, 0.02, 0.03, 0.05]
    selected = [r for r in results if r['cue_gain'] in show_gains]

    fig, axes = plt.subplots(2, len(selected), figsize=(4.5 * len(selected), 10))
    cmap = plt.cm.viridis(np.linspace(0.2, 0.8, len(selected)))

    for col, (res, color) in enumerate(zip(selected, cmap)):
        # Top: error distribution
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(res['errors'], bins=bins, density=True, alpha=0.6,
                color=color, edgecolor='white', linewidth=0.3)

        # Mark all three item locations
        for i, (theta, c, lab) in enumerate(zip(
            [0, thetas[1] - thetas[0], thetas[2] - thetas[0]],
            [COLORS['item1'], COLORS['item2'], COLORS['item3']],
            ['Item 1 (target)', 'Item 2', 'Item 3']
        )):
            wrapped = (theta + np.pi) % (2 * np.pi) - np.pi
            ax.axvline(x=wrapped, color=c, ls=':', lw=2, alpha=0.7, label=lab)

        ax.set_title(res['label'], fontsize=12, fontweight='bold')
        ax.set_xlabel('Decode error (rad)')
        if col == 0:
            ax.set_ylabel('Density')
        ax.set_xlim(-np.pi, np.pi)
        ax.legend(fontsize=7)
        ax.text(0.97, 0.93,
                f'Target: {res["near_target"]:.1f}%\n'
                f'Swap(B): {res["near_nt1"]:.1f}%\n'
                f'Swap(C): {res["near_nt2"]:.1f}%\n'
                f'A wins: {res["pct_A"]:.0f}%',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor='gray', alpha=0.8))

        # Bottom: temporal dynamics
        ax2 = axes[1, col]
        for trial_i in range(8):
            _, activities = run_three_item_trial_with_history(
                thetas, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps,
                cue_onset, res['cue_gain'], 0,
                input_gain, r_max, beta, h0
            )
            time = np.arange(n_steps) * dt
            a = 0.12 if trial_i > 0 else 0.9
            lw = 0.5 if trial_i > 0 else 1.8
            for i, (act, c) in enumerate(zip(activities,
                [COLORS['item1'], COLORS['item2'], COLORS['item3']])):
                lab = f'Net {"ABC"[i]}' if trial_i == 0 else None
                ax2.plot(time, act, color=c, alpha=a, lw=lw, label=lab)

        ax2.axvline(x=stim_steps * dt, color='gray', ls='--', lw=1, alpha=0.5)
        ax2.axvline(x=cue_onset * dt, color=COLORS['correct'], ls='--', lw=1.5,
                    alpha=0.7, label='Cue ON' if col == 0 else None)
        ax2.set_xlabel('Time (a.u.)')
        if col == 0:
            ax2.set_ylabel('Mean network activity')
        ax2.legend(fontsize=7, loc='best')

    plt.suptitle(
        'Sim #8: Three-item set size — does competition scale?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig19_three_items.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 19 saved")

    # Swap rate curve comparison
    fig2, ax = plt.subplots(1, 1, figsize=(8, 5))
    cgs = [r['cue_gain'] for r in results]
    swaps = [r['total_swap'] for r in results]
    targets = [r['near_target'] for r in results]

    ax.plot(cgs, swaps, 'o-', color=COLORS['swap'], lw=2, ms=8,
            label='Total swap % (3 items)')
    ax.plot(cgs, targets, 's-', color=COLORS['correct'], lw=2, ms=8,
            label='Target % (3 items)')
    ax.axhspan(15, 30, alpha=0.12, color=COLORS['swap'],
               label='Behavioral range (set size 3)')
    ax.set_xlabel('Cue gain', fontsize=12)
    ax.set_ylabel('% trials', fontsize=12)
    ax.set_title('Swap rate vs cue strength (3 items)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig20_three_item_curve.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 20 saved")


if __name__ == '__main__':
    print("=" * 65)
    print("SIM #8: THREE-ITEM SET SIZE")
    print("Three coupled ring attractors with mutual inhibition")
    print("Does competition scale to set size 3?")
    print("=" * 65)
    print()

    results, thetas, preferred, kappa, W_within, J_cross, noise_sigma, \
        dt, tau, n_steps, stim_steps, cue_onset, input_gain, \
        r_max, beta, h0 = run_experiment()

    print()
    print("─── Plotting ───")
    plot_results(results, thetas, preferred, kappa, W_within, J_cross,
                 noise_sigma, dt, tau, n_steps, stim_steps, cue_onset,
                 input_gain, r_max, beta, h0)

    print()
    print("═══ SUMMARY ═══")
    print(f"{'Cue':>8}  {'Target%':>8}  {'SwapB%':>8}  {'SwapC%':>8}  {'TotalSwap%':>11}  {'A wins':>8}")
    print("─" * 60)
    for r in results:
        print(f"{r['cue_gain']:>8.2f}  {r['near_target']:>8.1f}  {r['near_nt1']:>8.1f}  "
              f"{r['near_nt2']:>8.1f}  {r['total_swap']:>11.1f}  {r['pct_A']:>8.1f}")

    # Compare with two-item results
    print()
    print("─── SET SIZE COMPARISON ───")
    # Two-item results from sim #7b: cue=0.02 → 19.7% swap
    # Find comparable condition for three items
    cue02 = [r for r in results if abs(r['cue_gain'] - 0.02) < 0.001]
    if cue02:
        r3 = cue02[0]
        print(f"  At cue=0.02:")
        print(f"    2 items: target=64.3%, swap=19.7%  (from sim #7b)")
        print(f"    3 items: target={r3['near_target']:.1f}%, swap={r3['total_swap']:.1f}%")
        if r3['total_swap'] > 19.7:
            print(f"    ★ Swap rate INCREASED with set size (as predicted by literature)")
        else:
            print(f"    ⚠ Swap rate did NOT increase — model fails set-size scaling")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
