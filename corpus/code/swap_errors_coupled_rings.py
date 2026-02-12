"""
==========================================================================
SWAP ERRORS FROM COUPLED RING ATTRACTORS
==========================================================================

Simulation #6 in the cascade.

The hypothesis: swap errors arise from competition between SEPARATE
attractor networks, not from dynamics within a single manifold.

Model:
    Two ring attractor networks (A and B), each with sigmoid activation
    and cosine connectivity (identical to v2). Each network receives
    drive from one item.

    Within-network: J_0 (inhibition), J_1 (excitation) — sustains bumps
    Between-network: J_cross (mutual inhibition) — creates competition

    Phase 1 (stimulus): Network A driven by item 1, Network B by item 2
    Phase 2 (maintenance): Drive OFF. Cross-inhibition creates competition.

    If noise favors A: A's bump survives, B dies -> decode near item 1
    If noise favors B: B's bump survives, A dies -> decode near item 2
    Over trials: bimodal distribution = swap errors

Previous results:
  #1  Equal weights              -> blending
  #2  Beta(0.5,0.5) stipulated   -> swap bumps
  #3  Divisive normalization      -> blending
  #4  Ring attractor v1           -> inconclusive (explodes)
  #5  Ring attractor v2 (sigmoid) -> blending (single ring = one attractor)
  #6  THIS FILE                   -> ???
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
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
    'swap': '#e67e22',
    'correct': '#27ae60',
    'blend': '#95a5a6',
    'weak': '#95a5a6',
    'moderate': '#8e44ad',
    'strong': '#27ae60',
}


def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    """Saturating sigmoid. Bounded in [0, r_max]."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_within_weights(preferred_angles, J_0, J_1):
    """Within-network cosine connectivity."""
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N


def run_coupled_trial(theta1, theta2, preferred, kappa,
                      W_within, J_cross, noise_sigma,
                      dt, tau, n_steps, stim_steps, input_gain,
                      r_max, beta, h0):
    """
    Single trial: two coupled ring attractors.

    Network A receives item 1 drive.
    Network B receives item 2 drive.
    Cross-inhibition: each network's total activity suppresses the other.
    """
    N = len(preferred)

    # Feedforward drive (each network gets ONE item)
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])

    # Initialize both networks
    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        # Phase-dependent drive
        if step < stim_steps:
            ext_A = drive_A
            ext_B = drive_B
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        # Cross-inhibition: total activity of other network
        # Uniform inhibition proportional to mean activity of the other network
        cross_A = -J_cross * np.mean(r_B)  # B inhibits A
        cross_B = -J_cross * np.mean(r_A)  # A inhibits B

        # Network A dynamics
        noise_A = np.random.randn(N) * noise_sigma
        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        f_A = sigmoid(h_A, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)

        # Network B dynamics
        noise_B = np.random.randn(N) * noise_sigma
        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_B = np.maximum(0, r_B + dr_B)

    return r_A, r_B


def run_coupled_trial_with_history(theta1, theta2, preferred, kappa,
                                    W_within, J_cross, noise_sigma,
                                    dt, tau, n_steps, stim_steps, input_gain,
                                    r_max, beta, h0):
    """Same but returns temporal dynamics of both networks."""
    N = len(preferred)

    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])

    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    activity_A = np.zeros(n_steps)
    activity_B = np.zeros(n_steps)

    for step in range(n_steps):
        if step < stim_steps:
            ext_A, ext_B = drive_A, drive_B
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        noise_A = np.random.randn(N) * noise_sigma
        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        f_A = sigmoid(h_A, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)

        noise_B = np.random.randn(N) * noise_sigma
        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_B = np.maximum(0, r_B + dr_B)

        activity_A[step] = np.mean(r_A)
        activity_B[step] = np.mean(r_B)

    return r_A, r_B, activity_A, activity_B


def decode(response, preferred, kappa):
    """Cosine similarity decode."""
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


def decode_winner(r_A, r_B, preferred, kappa, theta1):
    """
    Decode from the winning network.

    Logic: read out from whichever network has higher total activity.
    This mimics a downstream readout that attends to the stronger signal.
    The error is measured relative to item 1 (theta1).
    """
    if np.sum(r_A) > np.sum(r_B):
        # Network A won -> decode from A -> should be near item 1
        decoded = decode(r_A, preferred, kappa)
    else:
        # Network B won -> decode from B -> should be near item 2
        decoded = decode(r_B, preferred, kappa)

    error = decoded - theta1
    return (error + np.pi) % (2 * np.pi) - np.pi


def decode_combined(r_A, r_B, preferred, kappa, theta1):
    """
    Decode from the combined population response.

    This is the more realistic readout: a downstream area sees the
    sum of both networks' activity. It decodes as if from a single
    population. This is where swap errors should appear — the combined
    signal is dominated by whichever network won.
    """
    combined = r_A + r_B
    decoded = decode(combined, preferred, kappa)
    error = decoded - theta1
    return (error + np.pi) % (2 * np.pi) - np.pi


# ═══════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════

def run_experiment():
    """Sweep cross-inhibition strength."""
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    theta1, theta2 = 0.0, separation
    dt, tau = 1.0, 10.0
    n_trials = 3000
    n_steps = 500
    stim_steps = 100
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0

    # Within-network params (from v2 diagnostic: J_0=1.0, J_1=6.0 sustains bumps)
    J_0, J_1 = 1.0, 6.0
    W_within = build_within_weights(preferred, J_0, J_1)

    # Three cross-inhibition regimes
    configs = [
        (0.5, 'Weak cross-inhibition', COLORS['weak']),
        (2.0, 'Moderate cross-inhibition', COLORS['moderate']),
        (5.0, 'Strong cross-inhibition', COLORS['strong']),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    all_errors = []

    for col, (J_cross, label, color) in enumerate(configs):
        print(f"  {label} (J_cross={J_cross}) — {n_trials} trials...")

        errors = np.zeros(n_trials)
        winner_counts = {'A': 0, 'B': 0, 'tie': 0}

        for t in range(n_trials):
            r_A, r_B = run_coupled_trial(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps, input_gain,
                r_max, beta, h0
            )

            # Track which network won
            sum_A, sum_B = np.sum(r_A), np.sum(r_B)
            if sum_A > sum_B * 1.5:
                winner_counts['A'] += 1
            elif sum_B > sum_A * 1.5:
                winner_counts['B'] += 1
            else:
                winner_counts['tie'] += 1

            # Decode from combined response (realistic readout)
            errors[t] = decode_combined(r_A, r_B, preferred, kappa, theta1)

        all_errors.append(errors)

        # Stats
        near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
        near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
        mean_b = np.mean(errors)
        k = kurtosis(errors, fisher=True)
        pct_A = 100 * winner_counts['A'] / n_trials
        pct_B = 100 * winner_counts['B'] / n_trials
        pct_tie = 100 * winner_counts['tie'] / n_trials

        print(f"    Near target: {near_t1:.1f}%  Near non-target: {near_t2:.1f}%")
        print(f"    Mean bias: {mean_b:.3f}  Kurtosis: {k:.2f}")
        print(f"    Winners — A: {pct_A:.1f}%  B: {pct_B:.1f}%  Tie: {pct_tie:.1f}%")

        # Top: error distribution
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)
        ax.axvline(x=0, color=COLORS['item1'], ls=':', lw=2, alpha=0.7,
                   label='Item 1 (target)')
        ax.axvline(x=separation, color=COLORS['item2'], ls=':', lw=2,
                   alpha=0.7, label='Item 2 (non-target)')
        ax.set_title(f'{label}\n(J_cross={J_cross})',
                     fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('Decode error (rad)')
        ax.set_ylabel('Density')
        ax.set_xlim(-np.pi, np.pi)
        ax.legend(fontsize=7)
        ax.text(0.97, 0.93,
                f'Near target: {near_t1:.1f}%\n'
                f'Near non-target: {near_t2:.1f}%\n'
                f'Mean bias: {mean_b:.3f}\n'
                f'Net A wins: {pct_A:.0f}%  B: {pct_B:.0f}%',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.8))

        # Bottom: temporal dynamics (8 example trials)
        ax2 = axes[1, col]
        for trial_i in range(10):
            _, _, act_A, act_B = run_coupled_trial_with_history(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps, input_gain,
                r_max, beta, h0
            )
            time = np.arange(n_steps) * dt
            a = 0.12 if trial_i > 0 else 0.9
            lw = 0.5 if trial_i > 0 else 1.8
            lab_A = 'Net A (item 1)' if trial_i == 0 else None
            lab_B = 'Net B (item 2)' if trial_i == 0 else None
            ax2.plot(time, act_A, color=COLORS['item1'], alpha=a, lw=lw, label=lab_A)
            ax2.plot(time, act_B, color=COLORS['item2'], alpha=a, lw=lw, label=lab_B)

        ax2.axvline(x=stim_steps * dt, color='gray', ls='--', lw=1, alpha=0.5,
                    label='Drive OFF')
        ax2.set_xlabel('Time (a.u.)')
        ax2.set_ylabel('Mean network activity')
        ax2.set_title(f'Network competition (J_cross={J_cross})', fontsize=10,
                      color=color)
        ax2.legend(fontsize=7, loc='best')

    plt.suptitle(
        'Coupled ring attractors: does inter-network competition\n'
        'produce winner-take-all swap errors?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig15_coupled_rings.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("\n✓ Figure 15 saved")

    return all_errors


if __name__ == '__main__':
    print("=" * 65)
    print("COUPLED RING ATTRACTORS: INTER-NETWORK COMPETITION")
    print("Two networks, one item each, mutual inhibition")
    print("The test: does competition between networks produce swaps?")
    print("=" * 65)
    print()

    results = run_experiment()
    print()

    # Final summary
    strong = results[2]
    swap_pct = 100 * np.mean(np.abs(strong - np.pi/2) < 0.3)
    target_pct = 100 * np.mean(np.abs(strong) < 0.3)

    print("─── Summary (strong cross-inhibition) ───")
    print(f"  Near target (correct): {target_pct:.1f}%")
    print(f"  Near non-target (swap): {swap_pct:.1f}%")

    if swap_pct > 10 and target_pct > 10:
        print(f"\n  *** BIMODAL: SWAP ERRORS DETECTED ***")
        print(f"  Inter-network competition produces winner-take-all.")
        print(f"  The mechanism: noise selects which network survives.")
        print(f"  The mixture model's 'swap' = probabilistic attractor selection.")
    elif swap_pct > 5:
        print(f"\n  Partial swap signal. Competition exists but incomplete.")
    elif target_pct > 50:
        print(f"\n  Network A dominates. Cross-inhibition too weak or asymmetric.")
    else:
        print(f"\n  No swap bumps. The coupled model also fails.")
        print(f"  Swap errors may require mechanisms beyond attractor competition.")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
