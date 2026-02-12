"""
==========================================================================
SWAP ERRORS: ASYMMETRIC CUE EXPERIMENT
==========================================================================

Simulation #7 in the cascade.

The question: Does an attentional advantage for the target network reduce
swap errors to behaviorally realistic levels (~15-20%)?

In simulations #1-6, both networks received equal drive. After drive
offset, noise alone determined the winner → ~50/50 split → ~50% "swaps."
But real experiments cue one item: the participant must report the item
at a specific location. This cue presumably gives the target network
a competitive advantage.

Model: Same coupled ring attractors as sim #6, but with:
  - An asymmetric "cue" signal applied after drive offset
  - The cue is a low-amplitude drive to Network A only
  - Sweep cue strength to find the regime that produces ~15-20% swaps

Previous results:
  #6  Coupled rings, no cue → ~50/50 split (too many swaps)
  #7  THIS FILE: Coupled rings + cue → ???

The literature:
  Zhang & Luck (2008): ~15-20% swap errors at set size 2-3
  Bays et al. (2009):  ~10-30% depending on set size and separation
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


def run_cued_trial(theta1, theta2, preferred, kappa,
                   W_within, J_cross, noise_sigma,
                   dt, tau, n_steps, stim_steps, cue_onset, cue_gain,
                   input_gain, r_max, beta, h0):
    """
    Single trial with asymmetric retro-cue.

    Phases:
      [0, stim_steps)       : Both networks driven (stimulus display)
      [stim_steps, cue_onset): No drive (blank interval)
      [cue_onset, n_steps)  : Low-amplitude cue drive to Network A only

    The cue mimics attentional selection: the participant knows which
    item to report, giving that representation a competitive edge.
    """
    N = len(preferred)

    # Feedforward drive
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])

    # Cue drive (weaker, just enough to bias competition)
    cue_drive_A = cue_gain * np.array([tuning_curve(theta1, phi, kappa)
                                        for phi in preferred])

    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        # Phase-dependent external input
        if step < stim_steps:
            ext_A = drive_A
            ext_B = drive_B
        elif step >= cue_onset:
            ext_A = cue_drive_A  # Cue boosts target network
            ext_B = np.zeros(N)
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        # Cross-inhibition
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        # Network A
        noise_A = np.random.randn(N) * noise_sigma
        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        f_A = sigmoid(h_A, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)

        # Network B
        noise_B = np.random.randn(N) * noise_sigma
        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_B = np.maximum(0, r_B + dr_B)

    return r_A, r_B


def run_cued_trial_with_history(theta1, theta2, preferred, kappa,
                                W_within, J_cross, noise_sigma,
                                dt, tau, n_steps, stim_steps,
                                cue_onset, cue_gain,
                                input_gain, r_max, beta, h0):
    """Same but returns temporal dynamics."""
    N = len(preferred)

    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])
    cue_drive_A = cue_gain * np.array([tuning_curve(theta1, phi, kappa)
                                        for phi in preferred])

    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    activity_A = np.zeros(n_steps)
    activity_B = np.zeros(n_steps)

    for step in range(n_steps):
        if step < stim_steps:
            ext_A, ext_B = drive_A, drive_B
        elif step >= cue_onset:
            ext_A = cue_drive_A
            ext_B = np.zeros(N)
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


def decode_combined(r_A, r_B, preferred, kappa, theta1):
    """Decode from combined population response. Error relative to item 1."""
    combined = r_A + r_B
    decoded = decode(combined, preferred, kappa)
    error = decoded - theta1
    return (error + np.pi) % (2 * np.pi) - np.pi


# ═══════════════════════════════════════════════════════════════════
# MAIN: SWEEP CUE STRENGTH
# ═══════════════════════════════════════════════════════════════════

def run_experiment():
    """Sweep cue gain to find the regime producing ~15-20% swaps."""
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    theta1, theta2 = 0.0, separation
    dt, tau = 1.0, 10.0
    n_trials = 3000
    n_steps = 500
    stim_steps = 100
    cue_onset = 150  # Cue arrives 50 steps after stimulus offset
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0
    J_0, J_1 = 1.0, 6.0
    J_cross = 0.5  # Weak cross-inhibition (the regime that produced swaps)

    W_within = build_within_weights(preferred, J_0, J_1)

    # Sweep cue gain: 0 (no cue, baseline) through increasing strengths
    cue_gains = [0.0, 0.3, 0.6, 1.0, 1.5, 2.0]

    results = []
    for cg in cue_gains:
        label = f'cue={cg:.1f}' if cg > 0 else 'no cue'
        print(f"  {label} — {n_trials} trials...")

        errors = np.zeros(n_trials)
        winner_counts = {'A': 0, 'B': 0, 'tie': 0}

        for t in range(n_trials):
            r_A, r_B = run_cued_trial(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps, cue_onset, cg,
                input_gain, r_max, beta, h0
            )

            sum_A, sum_B = np.sum(r_A), np.sum(r_B)
            if sum_A > sum_B * 1.5:
                winner_counts['A'] += 1
            elif sum_B > sum_A * 1.5:
                winner_counts['B'] += 1
            else:
                winner_counts['tie'] += 1

            errors[t] = decode_combined(r_A, r_B, preferred, kappa, theta1)

        near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
        near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
        mean_b = np.mean(errors)
        k = kurtosis(errors, fisher=True)
        pct_A = 100 * winner_counts['A'] / n_trials
        pct_B = 100 * winner_counts['B'] / n_trials

        print(f"    Near target: {near_t1:.1f}%  Near non-target (swap): {near_t2:.1f}%")
        print(f"    Mean bias: {mean_b:.3f}  Kurtosis: {k:.2f}")
        print(f"    Winners — A: {pct_A:.1f}%  B: {pct_B:.1f}%")

        results.append({
            'cue_gain': cg, 'label': label, 'errors': errors,
            'near_t1': near_t1, 'near_t2': near_t2,
            'mean_bias': mean_b, 'kurtosis': k,
            'pct_A': pct_A, 'pct_B': pct_B,
        })

    return results


def plot_results(results, preferred, kappa, theta1, theta2,
                 W_within, J_cross, noise_sigma, dt, tau,
                 n_steps, stim_steps, cue_onset, input_gain,
                 r_max, beta, h0):
    """Two-panel figure: (A) error distributions, (B) swap rate vs cue strength."""
    separation = theta2 - theta1

    # ─── Figure 1: Error distributions for selected cue gains ───
    selected = [r for r in results if r['cue_gain'] in [0.0, 0.6, 1.0, 1.5]]
    n_sel = len(selected)

    fig, axes = plt.subplots(2, n_sel, figsize=(4.5 * n_sel, 10))
    cmap = plt.cm.viridis(np.linspace(0.2, 0.8, n_sel))

    for col, (res, color) in enumerate(zip(selected, cmap)):
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(res['errors'], bins=bins, density=True, alpha=0.6,
                color=color, edgecolor='white', linewidth=0.3)
        ax.axvline(x=0, color=COLORS['item1'], ls=':', lw=2, alpha=0.7,
                   label='Item 1 (target)')
        ax.axvline(x=separation, color=COLORS['item2'], ls=':', lw=2,
                   alpha=0.7, label='Item 2 (non-target)')
        ax.set_title(f'{res["label"]}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Decode error (rad)')
        if col == 0:
            ax.set_ylabel('Density')
        ax.set_xlim(-np.pi, np.pi)
        ax.legend(fontsize=7)
        ax.text(0.97, 0.93,
                f'Near target: {res["near_t1"]:.1f}%\n'
                f'Near non-target: {res["near_t2"]:.1f}%\n'
                f'A wins: {res["pct_A"]:.0f}%  B wins: {res["pct_B"]:.0f}%',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor='gray', alpha=0.8))

        # Bottom: temporal dynamics
        ax2 = axes[1, col]
        for trial_i in range(10):
            _, _, act_A, act_B = run_cued_trial_with_history(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps, cue_onset, res['cue_gain'],
                input_gain, r_max, beta, h0
            )
            time = np.arange(n_steps) * dt
            a = 0.12 if trial_i > 0 else 0.9
            lw = 0.5 if trial_i > 0 else 1.8
            lab_A = 'Net A (cued)' if trial_i == 0 else None
            lab_B = 'Net B (uncued)' if trial_i == 0 else None
            ax2.plot(time, act_A, color=COLORS['item1'], alpha=a, lw=lw, label=lab_A)
            ax2.plot(time, act_B, color=COLORS['item2'], alpha=a, lw=lw, label=lab_B)

        ax2.axvline(x=stim_steps * dt, color='gray', ls='--', lw=1, alpha=0.5,
                    label='Drive OFF')
        ax2.axvline(x=cue_onset * dt, color=COLORS['correct'], ls='--', lw=1.5,
                    alpha=0.7, label='Cue ON')
        ax2.set_xlabel('Time (a.u.)')
        if col == 0:
            ax2.set_ylabel('Mean network activity')
        ax2.set_title(f'Dynamics ({res["label"]})', fontsize=10)
        ax2.legend(fontsize=7, loc='best')

    plt.suptitle(
        'Sim #7: Asymmetric retro-cue — does attentional bias\n'
        'produce realistic swap rates (~15-20%)?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig16_asymmetric_cue.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 16 saved")

    # ─── Figure 2: Swap rate curve ───
    fig2, (ax_swap, ax_ratio) = plt.subplots(1, 2, figsize=(12, 5))

    cue_vals = [r['cue_gain'] for r in results]
    swap_rates = [r['near_t2'] for r in results]
    correct_rates = [r['near_t1'] for r in results]

    ax_swap.plot(cue_vals, swap_rates, 'o-', color=COLORS['item2'],
                 lw=2, ms=8, label='Near non-target (swap %)')
    ax_swap.plot(cue_vals, correct_rates, 's-', color=COLORS['correct'],
                 lw=2, ms=8, label='Near target (correct %)')

    # Shade the behavioral range
    ax_swap.axhspan(10, 25, alpha=0.15, color=COLORS['swap'],
                    label='Behavioral range (~10-25%)')
    ax_swap.set_xlabel('Cue gain (attentional boost)', fontsize=12)
    ax_swap.set_ylabel('% trials', fontsize=12)
    ax_swap.set_title('Swap rate vs. cue strength', fontsize=13, fontweight='bold')
    ax_swap.legend(fontsize=9)
    ax_swap.set_ylim(0, None)

    # Right panel: A-wins / B-wins ratio
    a_wins = [r['pct_A'] for r in results]
    b_wins = [r['pct_B'] for r in results]
    ax_ratio.plot(cue_vals, a_wins, 'o-', color=COLORS['item1'],
                  lw=2, ms=8, label='Network A wins')
    ax_ratio.plot(cue_vals, b_wins, 's-', color=COLORS['item2'],
                  lw=2, ms=8, label='Network B wins')
    ax_ratio.set_xlabel('Cue gain', fontsize=12)
    ax_ratio.set_ylabel('% trials', fontsize=12)
    ax_ratio.set_title('Winner selection vs. cue strength', fontsize=13,
                        fontweight='bold')
    ax_ratio.legend(fontsize=9)
    ax_ratio.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig17_swap_rate_curve.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 17 saved")


if __name__ == '__main__':
    print("=" * 65)
    print("SIM #7: ASYMMETRIC RETRO-CUE")
    print("Coupled rings + attentional bias for target network")
    print("Does cue strength control the swap rate?")
    print("=" * 65)
    print()

    results = run_experiment()

    # Reconstruct params for plotting
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    theta1, theta2 = 0.0, separation
    dt, tau = 1.0, 10.0
    n_steps = 500
    stim_steps = 100
    cue_onset = 150
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0
    J_0, J_1 = 1.0, 6.0
    J_cross = 0.5
    W_within = build_within_weights(preferred, J_0, J_1)

    print()
    print("─── Plotting ───")
    plot_results(results, preferred, kappa, theta1, theta2,
                 W_within, J_cross, noise_sigma, dt, tau,
                 n_steps, stim_steps, cue_onset, input_gain,
                 r_max, beta, h0)

    # Summary table
    print()
    print("═══ SUMMARY ═══")
    print(f"{'Cue gain':>10}  {'Target%':>8}  {'Swap%':>8}  {'A wins':>8}  {'B wins':>8}")
    print("─" * 50)
    for r in results:
        print(f"{r['cue_gain']:>10.1f}  {r['near_t1']:>8.1f}  {r['near_t2']:>8.1f}  "
              f"{r['pct_A']:>8.1f}  {r['pct_B']:>8.1f}")

    # Find the sweet spot
    behavioral = [r for r in results if 10 <= r['near_t2'] <= 25]
    if behavioral:
        best = min(behavioral, key=lambda r: abs(r['near_t2'] - 17.5))
        print(f"\n★ Closest to behavioral range: cue_gain={best['cue_gain']:.1f}")
        print(f"  Target: {best['near_t1']:.1f}%  Swap: {best['near_t2']:.1f}%")
    else:
        print("\n⚠ No cue gain produced swap rates in the 10-25% behavioral range.")
        if all(r['near_t2'] > 25 for r in results if r['cue_gain'] > 0):
            print("  All rates too HIGH → cue not strong enough to bias competition")
        elif all(r['near_t2'] < 10 for r in results if r['cue_gain'] > 0):
            print("  All rates too LOW → cue too strong, fully suppresses swaps")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
