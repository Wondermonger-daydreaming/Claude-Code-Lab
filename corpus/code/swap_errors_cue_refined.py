"""
==========================================================================
SWAP ERRORS: REFINED CUE EXPERIMENT
==========================================================================

Simulation #7b — following up on #7's cliff result.

Finding: ANY sustained cue (even gain=0.3) completely resolves the
competition → 100% target, 0% swaps. The transition is a cliff.

Two probes:
  A) Fine-grained cue sweep (0.0 to 0.3 in small steps) — find the cliff
  B) Brief pulse cue (transient, not sustained) — test if duration matters

The hypothesis: real attention is more like a brief bias signal than a
sustained drive. A transient cue should partially bias competition
without deterministically resolving it.
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
    'swap': '#e67e22',
    'correct': '#27ae60',
    'blend': '#95a5a6',
    'pulse': '#8e44ad',
    'sustained': '#2d5a7b',
}


def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def tuning_curve(theta, preferred, kappa):
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_within_weights(preferred_angles, J_0, J_1):
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N


def run_trial(theta1, theta2, preferred, kappa,
              W_within, J_cross, noise_sigma,
              dt, tau, n_steps, stim_steps,
              cue_onset, cue_offset, cue_gain,
              input_gain, r_max, beta, h0):
    """
    Flexible trial: cue can be sustained or pulse (cue_onset to cue_offset).
    """
    N = len(preferred)

    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])
    cue_drive_A = cue_gain * np.array([tuning_curve(theta1, phi, kappa)
                                        for phi in preferred])

    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        if step < stim_steps:
            ext_A, ext_B = drive_A, drive_B
        elif cue_onset <= step < cue_offset:
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

    return r_A, r_B


def decode(response, preferred, kappa):
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


def decode_combined(r_A, r_B, preferred, kappa, theta1):
    combined = r_A + r_B
    decoded = decode(combined, preferred, kappa)
    error = decoded - theta1
    return (error + np.pi) % (2 * np.pi) - np.pi


def run_sweep(cue_gains, cue_onset, cue_offset, label_prefix,
              preferred, kappa, theta1, theta2, W_within, J_cross,
              noise_sigma, dt, tau, n_steps, stim_steps,
              input_gain, r_max, beta, h0, n_trials):
    """Run a sweep of cue gains and return results."""
    separation = theta2 - theta1
    results = []

    for cg in cue_gains:
        errors = np.zeros(n_trials)
        a_wins = 0

        for t in range(n_trials):
            r_A, r_B = run_trial(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps,
                cue_onset, cue_offset, cg,
                input_gain, r_max, beta, h0
            )
            if np.sum(r_A) > np.sum(r_B) * 1.5:
                a_wins += 1
            errors[t] = decode_combined(r_A, r_B, preferred, kappa, theta1)

        near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
        near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
        pct_A = 100 * a_wins / n_trials

        results.append({
            'cue_gain': cg, 'near_t1': near_t1, 'near_t2': near_t2,
            'pct_A': pct_A, 'errors': errors,
        })

    return results


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Shared params
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    theta1, theta2 = 0.0, separation
    dt, tau = 1.0, 10.0
    n_trials = 2000  # Fewer trials for the sweep (still enough for % estimates)
    n_steps = 500
    stim_steps = 100
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    input_gain = 5.0
    J_0, J_1 = 1.0, 6.0
    J_cross = 0.5
    W_within = build_within_weights(preferred, J_0, J_1)

    print("=" * 65)
    print("SIM #7b: REFINED CUE EXPERIMENT")
    print("=" * 65)

    # ─── Probe A: Fine-grained sustained cue sweep ───
    print("\n─── PROBE A: Fine-grained sustained cue (step 150→500) ───")
    cue_gains_fine = [0.0, 0.02, 0.05, 0.08, 0.1, 0.15, 0.2, 0.3]
    results_sustained = run_sweep(
        cue_gains_fine, cue_onset=150, cue_offset=n_steps,
        label_prefix='sustained',
        preferred=preferred, kappa=kappa, theta1=theta1, theta2=theta2,
        W_within=W_within, J_cross=J_cross, noise_sigma=noise_sigma,
        dt=dt, tau=tau, n_steps=n_steps, stim_steps=stim_steps,
        input_gain=input_gain, r_max=r_max, beta=beta, h0=h0,
        n_trials=n_trials
    )

    print(f"\n{'Cue gain':>10}  {'Target%':>8}  {'Swap%':>8}  {'A wins%':>8}")
    print("─" * 40)
    for r in results_sustained:
        print(f"{r['cue_gain']:>10.3f}  {r['near_t1']:>8.1f}  {r['near_t2']:>8.1f}  "
              f"{r['pct_A']:>8.1f}")

    # ─── Probe B: Brief pulse cues (varying duration) ───
    print("\n─── PROBE B: Brief pulse cue (gain=1.0, varying duration) ───")
    pulse_durations = [5, 10, 15, 20, 30, 50]
    cue_onset = 150
    results_pulse = []

    for dur in pulse_durations:
        cue_offset = cue_onset + dur
        print(f"  pulse={dur} steps (gain=1.0)...", end=" ", flush=True)

        errors = np.zeros(n_trials)
        a_wins = 0
        for t in range(n_trials):
            r_A, r_B = run_trial(
                theta1, theta2, preferred, kappa,
                W_within, J_cross, noise_sigma,
                dt, tau, n_steps, stim_steps,
                cue_onset, cue_offset, 1.0,
                input_gain, r_max, beta, h0
            )
            if np.sum(r_A) > np.sum(r_B) * 1.5:
                a_wins += 1
            errors[t] = decode_combined(r_A, r_B, preferred, kappa, theta1)

        near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
        near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
        pct_A = 100 * a_wins / n_trials
        print(f"target={near_t1:.1f}%  swap={near_t2:.1f}%  A_wins={pct_A:.1f}%")

        results_pulse.append({
            'duration': dur, 'near_t1': near_t1, 'near_t2': near_t2,
            'pct_A': pct_A, 'errors': errors,
        })

    # ─── Probe C: Pulse cues with varying gain AND duration ───
    print("\n─── PROBE C: Pulse cue grid (gain × duration) ───")
    pulse_gains = [0.3, 0.5, 1.0]
    pulse_durs = [5, 10, 20]
    results_grid = {}

    for pg in pulse_gains:
        for pd in pulse_durs:
            cue_offset = cue_onset + pd
            errors = np.zeros(n_trials)
            a_wins = 0
            for t in range(n_trials):
                r_A, r_B = run_trial(
                    theta1, theta2, preferred, kappa,
                    W_within, J_cross, noise_sigma,
                    dt, tau, n_steps, stim_steps,
                    cue_onset, cue_offset, pg,
                    input_gain, r_max, beta, h0
                )
                if np.sum(r_A) > np.sum(r_B) * 1.5:
                    a_wins += 1
                errors[t] = decode_combined(r_A, r_B, preferred, kappa, theta1)

            near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
            near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
            pct_A = 100 * a_wins / n_trials
            results_grid[(pg, pd)] = {
                'near_t1': near_t1, 'near_t2': near_t2, 'pct_A': pct_A,
                'errors': errors,
            }

    print(f"\n{'':>12}", end="")
    for pd in pulse_durs:
        print(f"{'dur=' + str(pd):>16}", end="")
    print()
    print("─" * 60)
    for pg in pulse_gains:
        print(f"gain={pg:<6.1f}", end="  ")
        for pd in pulse_durs:
            r = results_grid[(pg, pd)]
            print(f"T={r['near_t1']:4.0f}% S={r['near_t2']:4.0f}%", end="  ")
        print()

    # ─── PLOTTING ───
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    # Panel A: Sustained cue sweep
    ax = axes[0]
    cg = [r['cue_gain'] for r in results_sustained]
    swap = [r['near_t2'] for r in results_sustained]
    target = [r['near_t1'] for r in results_sustained]
    ax.plot(cg, swap, 'o-', color=COLORS['item2'], lw=2, ms=8, label='Swap %')
    ax.plot(cg, target, 's-', color=COLORS['correct'], lw=2, ms=8, label='Target %')
    ax.axhspan(10, 25, alpha=0.15, color=COLORS['swap'], label='Behavioral range')
    ax.set_xlabel('Sustained cue gain')
    ax.set_ylabel('% trials')
    ax.set_title('A: Sustained cue (fine sweep)', fontweight='bold')
    ax.legend(fontsize=8)

    # Panel B: Pulse duration sweep
    ax = axes[1]
    durs = [r['duration'] for r in results_pulse]
    swap_p = [r['near_t2'] for r in results_pulse]
    target_p = [r['near_t1'] for r in results_pulse]
    ax.plot(durs, swap_p, 'o-', color=COLORS['item2'], lw=2, ms=8, label='Swap %')
    ax.plot(durs, target_p, 's-', color=COLORS['correct'], lw=2, ms=8, label='Target %')
    ax.axhspan(10, 25, alpha=0.15, color=COLORS['swap'], label='Behavioral range')
    ax.set_xlabel('Pulse duration (steps)')
    ax.set_ylabel('% trials')
    ax.set_title('B: Pulse cue (gain=1.0, vary duration)', fontweight='bold')
    ax.legend(fontsize=8)

    # Panel C: Grid heatmap (swap %)
    ax = axes[2]
    grid_data = np.zeros((len(pulse_gains), len(pulse_durs)))
    for i, pg in enumerate(pulse_gains):
        for j, pd in enumerate(pulse_durs):
            grid_data[i, j] = results_grid[(pg, pd)]['near_t2']

    im = ax.imshow(grid_data, cmap='RdYlGn_r', aspect='auto',
                   vmin=0, vmax=40)
    ax.set_xticks(range(len(pulse_durs)))
    ax.set_xticklabels([str(d) for d in pulse_durs])
    ax.set_yticks(range(len(pulse_gains)))
    ax.set_yticklabels([f'{g:.1f}' for g in pulse_gains])
    ax.set_xlabel('Pulse duration (steps)')
    ax.set_ylabel('Pulse gain')
    ax.set_title('C: Swap % (gain × duration)', fontweight='bold')
    for i in range(len(pulse_gains)):
        for j in range(len(pulse_durs)):
            val = grid_data[i, j]
            color = 'white' if val > 20 else 'black'
            ax.text(j, i, f'{val:.0f}%', ha='center', va='center',
                    fontsize=12, fontweight='bold', color=color)
    plt.colorbar(im, ax=ax, label='Swap %')

    plt.suptitle('Sim #7b: Refined cue — finding the intermediate regime',
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig18_cue_refined.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("\n✓ Figure 18 saved")

    # ─── Final diagnostic ───
    behavioral_hits = []
    for r in results_sustained:
        if 10 <= r['near_t2'] <= 25:
            behavioral_hits.append(('sustained', r['cue_gain'], r['near_t2']))
    for r in results_pulse:
        if 10 <= r['near_t2'] <= 25:
            behavioral_hits.append(('pulse', r['duration'], r['near_t2']))
    for (pg, pd), r in results_grid.items():
        if 10 <= r['near_t2'] <= 25:
            behavioral_hits.append((f'grid({pg},{pd})', 0, r['near_t2']))

    print("\n═══ BEHAVIORAL-RANGE HITS ═══")
    if behavioral_hits:
        for mode, param, swap_pct in behavioral_hits:
            print(f"  ★ {mode}: swap={swap_pct:.1f}%")
    else:
        print("  ⚠ NO conditions produced swap rates in the 10-25% range.")
        print("  The competition is all-or-nothing: 50% or 0%.")
        print("  This is a genuine model limitation.")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
