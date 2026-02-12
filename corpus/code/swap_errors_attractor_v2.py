"""
==========================================================================
SWAP ERRORS FROM RING ATTRACTOR v2: SIGMOID ACTIVATION
==========================================================================

Fixes the numerical instability in v1. The threshold-linear activation
[x]_+ = max(0,x) has no upper bound — with strong recurrence, activity
explodes to infinity. v1's diagnostic showed peaks of 10^15.

Fix: sigmoid activation f(h) = r_max / (1 + exp(-beta*(h - h0)))
This is standard for rate models (Wilson-Cowan). Bounded in [0, r_max].

The question remains: does a properly bounded ring attractor produce
winner-take-all item selection (swap errors)?

Previous results:
  #1  swap_errors_geometric.py:      Fixed equal weights     -> blending
  #2  swap_errors_stochastic.py:     Beta(0.5,0.5) stipulated -> swap bumps
  #3  swap_errors_normalization.py:  Divisive normalization   -> blending
  #4  swap_errors_attractor.py:      Ring attractor (v1)      -> INCONCLUSIVE
      (model numerically unstable — activity explodes or decays)
  #5  THIS FILE:                     Ring attractor (v2)      -> ???
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
    'swap_bump': '#e67e22',
    'attractor': '#27ae60',
    'gaussian_ref': '#7f8c8d',
    'blend': '#95a5a6',
    'weak': '#95a5a6',
    'moderate': '#8e44ad',
    'strong': '#27ae60',
}


def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    """Saturating sigmoid activation. Bounded in [0, r_max]."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))


def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_weights(preferred_angles, J_0, J_1):
    """Ring attractor connectivity: W_ij = (-J_0 + J_1*cos(phi_i - phi_j))/N"""
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N


def run_trial(theta1, theta2, preferred, kappa, W, noise_sigma,
              dt, tau, n_steps, stim_steps, input_gain,
              r_max, beta, h0):
    """
    Single trial: two-phase ring attractor with sigmoid activation.
    Phase 1: both items drive the population.
    Phase 2: drive OFF, recurrence sustains + competes.
    """
    N = len(preferred)
    drive1 = np.array([tuning_curve(theta1, phi, kappa) for phi in preferred])
    drive2 = np.array([tuning_curve(theta2, phi, kappa) for phi in preferred])
    drive = input_gain * (drive1 + drive2)

    r = np.ones(N) * 0.1

    for step in range(n_steps):
        ext = drive if step < stim_steps else np.zeros(N)
        noise = np.random.randn(N) * noise_sigma
        h = W @ r + ext + noise
        f_h = sigmoid(h, r_max, beta, h0)
        dr = (-r + f_h) * (dt / tau)
        r = np.maximum(0, r + dr)

    return r


def run_trial_with_history(theta1, theta2, preferred, kappa, W, noise_sigma,
                           dt, tau, n_steps, stim_steps, input_gain,
                           r_max, beta, h0):
    """Same as run_trial but returns temporal dynamics."""
    N = len(preferred)
    drive1 = np.array([tuning_curve(theta1, phi, kappa) for phi in preferred])
    drive2 = np.array([tuning_curve(theta2, phi, kappa) for phi in preferred])
    drive = input_gain * (drive1 + drive2)

    template1 = drive1 / (np.linalg.norm(drive1) + 1e-12)
    template2 = drive2 / (np.linalg.norm(drive2) + 1e-12)

    r = np.ones(N) * 0.1
    s1 = np.zeros(n_steps)
    s2 = np.zeros(n_steps)

    for step in range(n_steps):
        ext = drive if step < stim_steps else np.zeros(N)
        noise = np.random.randn(N) * noise_sigma
        h = W @ r + ext + noise
        f_h = sigmoid(h, r_max, beta, h0)
        dr = (-r + f_h) * (dt / tau)
        r = np.maximum(0, r + dr)

        r_norm = r / (np.linalg.norm(r) + 1e-12)
        s1[step] = r_norm @ template1
        s2[step] = r_norm @ template2

    return r, s1, s2


def decode(response, preferred, kappa):
    """Cosine similarity decode against single-item templates."""
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


# ═══════════════════════════════════════════════════════════════════
# DIAGNOSTIC: Does the sigmoid model sustain bumps?
# ═══════════════════════════════════════════════════════════════════

def diagnostic(verbose=True):
    """Check bump sustainability with sigmoid activation."""
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    dt, tau = 1.0, 10.0
    r_max, beta, h0 = 1.0, 5.0, 0.5

    if verbose:
        print("  Sigmoid diagnostic: bump sustainability")
        print(f"  r_max={r_max}, beta={beta}, h0={h0}")
        print(f"  {'J_0':>6s} {'J_1':>6s} {'peak':>8s} {'total':>8s} {'status':>12s}")

    working = None
    for J_0, J_1 in [(0.5, 2), (0.5, 4), (1.0, 4), (1.0, 6), (1.0, 8),
                      (2.0, 6), (2.0, 8), (2.0, 10), (3.0, 10), (3.0, 12),
                      (1.0, 10), (2.0, 12), (4.0, 16), (5.0, 20), (3.0, 15)]:
        W = build_weights(preferred, J_0, J_1)
        drive = np.array([tuning_curve(0.0, phi, kappa) for phi in preferred])
        # Kick-start with drive
        r = sigmoid(W @ (drive * 5) + drive * 5, r_max, beta, h0)

        # Run 500 steps with NO drive
        for step in range(500):
            h = W @ r
            f_h = sigmoid(h, r_max, beta, h0)
            dr = (-r + f_h) * (dt / tau)
            r = np.maximum(0, r + dr)

        peak = np.max(r)
        total = np.sum(r)
        # Check if bump is localized (peak > 2x mean)
        mean_r = np.mean(r)
        localized = peak > 2 * mean_r and peak > 0.1
        status = "✓ BUMP" if localized else "✗ no bump"

        if verbose:
            print(f"  {J_0:6.1f} {J_1:6.1f} {peak:8.4f} {total:8.2f} {status:>12s}")

        if localized and working is None:
            working = (J_0, J_1)

    return working


# ═══════════════════════════════════════════════════════════════════
# MAIN EXPERIMENT
# ═══════════════════════════════════════════════════════════════════

def run_experiment(J_0_base, J_1_base):
    """Three recurrence regimes: weak, moderate, strong."""
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

    configs = [
        (J_0_base * 0.5, J_1_base * 0.5, 'Weak'),
        (J_0_base, J_1_base, 'Moderate'),
        (J_0_base * 2.0, J_1_base * 2.0, 'Strong'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(17, 10))
    all_results = []

    for col, (J_0, J_1, label) in enumerate(configs):
        print(f"  {label}: J_0={J_0:.1f}, J_1={J_1:.1f} ({n_trials} trials)...")
        W = build_weights(preferred, J_0, J_1)

        # Sweep input_gain to find a regime where the network is active
        # but not saturated
        input_gain = 5.0

        errors = np.zeros(n_trials)
        noise_sigma = 0.3

        for t in range(n_trials):
            response = run_trial(
                theta1, theta2, preferred, kappa, W, noise_sigma,
                dt, tau, n_steps, stim_steps, input_gain,
                r_max, beta, h0
            )
            decoded = decode(response, preferred, kappa)
            error = decoded - theta1
            errors[t] = (error + np.pi) % (2 * np.pi) - np.pi

        all_results.append(errors)

        # Stats
        near_t1 = 100 * np.mean(np.abs(errors) < 0.3)
        near_t2 = 100 * np.mean(np.abs(errors - separation) < 0.3)
        mean_b = np.mean(errors)
        k = kurtosis(errors, fisher=True)

        color = [COLORS['weak'], COLORS['moderate'], COLORS['strong']][col]

        print(f"    Near target: {near_t1:.1f}%  Near non-target: {near_t2:.1f}%"
              f"  Mean bias: {mean_b:.3f}  Kurtosis: {k:.2f}")

        # Top: error distribution
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 80)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)
        ax.axvline(x=0, color=COLORS['item1'], ls=':', lw=2, alpha=0.7,
                   label='Target')
        ax.axvline(x=separation, color=COLORS['item2'], ls=':', lw=2,
                   alpha=0.7, label='Non-target')
        ax.set_title(f'{label} (J₀={J_0:.1f}, J₁={J_1:.1f})',
                     fontsize=11, fontweight='bold', color=color)
        ax.set_xlabel('Decode error (rad)')
        ax.set_ylabel('Density')
        ax.set_xlim(-np.pi, np.pi)
        ax.legend(fontsize=8)
        ax.text(0.97, 0.93,
                f'Near target: {near_t1:.1f}%\n'
                f'Near non-target: {near_t2:.1f}%\n'
                f'Mean bias: {mean_b:.3f}\n'
                f'Kurtosis: {k:.2f}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                         edgecolor=color, alpha=0.8))

        # Bottom: temporal dynamics (5 example trials)
        ax2 = axes[1, col]
        for trial_i in range(8):
            _, s1, s2 = run_trial_with_history(
                theta1, theta2, preferred, kappa, W, noise_sigma,
                dt, tau, n_steps, stim_steps, input_gain,
                r_max, beta, h0
            )
            time = np.arange(n_steps) * dt
            a = 0.15 if trial_i > 0 else 0.9
            lw = 0.6 if trial_i > 0 else 1.8
            lab1 = 'Item 1' if trial_i == 0 else None
            lab2 = 'Item 2' if trial_i == 0 else None
            ax2.plot(time, s1, color=COLORS['item1'], alpha=a, lw=lw, label=lab1)
            ax2.plot(time, s2, color=COLORS['item2'], alpha=a, lw=lw, label=lab2)

        ax2.axvline(x=stim_steps * dt, color='gray', ls='--', lw=1, alpha=0.5,
                    label='Drive OFF')
        ax2.set_xlabel('Time (a.u.)')
        ax2.set_ylabel('Template similarity')
        ax2.set_title(f'Dynamics ({label})', fontsize=10, color=color)
        ax2.legend(fontsize=7, loc='best')

    plt.suptitle(
        'Ring attractor v2 (sigmoid activation): does bounded recurrence\n'
        'produce winner-take-all swap errors?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig14_attractor_v2.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 14 saved")

    return all_results


if __name__ == '__main__':
    print("=" * 65)
    print("RING ATTRACTOR v2: SIGMOID ACTIVATION")
    print("Fixing v1's numerical instability")
    print("=" * 65)
    print()

    print("─── Diagnostic ───")
    working = diagnostic()
    print()

    if working is None:
        print("  ✗ No self-sustaining bump found.")
        print("  Trying expanded parameter search...")
        # Try higher beta (sharper sigmoid → more nonlinear → more attractor-like)
        for beta_try in [10.0, 20.0, 50.0]:
            print(f"\n  beta={beta_try}:")
            N = 48
            kappa = 2.0
            preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
            dt, tau = 1.0, 10.0
            for J_0, J_1 in [(2, 8), (3, 12), (5, 20), (2, 10), (4, 16)]:
                W = build_weights(preferred, J_0, J_1)
                drive = np.array([tuning_curve(0.0, phi, kappa)
                                  for phi in preferred])
                r = sigmoid(W @ (drive * 5) + drive * 5, 1.0, beta_try, 0.5)
                for step in range(500):
                    h = W @ r
                    f_h = sigmoid(h, 1.0, beta_try, 0.5)
                    dr = (-r + f_h) * (dt / tau)
                    r = np.maximum(0, r + dr)
                peak = np.max(r)
                mean_r = np.mean(r)
                localized = peak > 2 * mean_r and peak > 0.1
                if localized:
                    print(f"    J_0={J_0}, J_1={J_1}: peak={peak:.4f} ✓ BUMP")
                    working = (J_0, J_1)
                    # Use this beta for the experiment
                    break
            if working:
                break

    if working is None:
        print("\n  ✗ Cannot find stable bump regime. The model may need")
        print("    additional mechanisms (adaptation, Dale's law, etc.)")
    else:
        J_0, J_1 = working
        print(f"\n  Base parameters: J_0={J_0}, J_1={J_1}")
        print()
        print("─── Main experiment ───")
        results = run_experiment(J_0, J_1)
        print()

        # Summary
        strong = results[2]
        swap_pct = 100 * np.mean(np.abs(strong - np.pi/2) < 0.3)
        target_pct = 100 * np.mean(np.abs(strong) < 0.3)
        print(f"  Strong recurrence: {target_pct:.1f}% near target, "
              f"{swap_pct:.1f}% near non-target")

        if swap_pct > 5:
            print(f"  *** SWAP BUMPS DETECTED: {swap_pct:.1f}% ***")
        elif target_pct < 5 and swap_pct < 5:
            print("  Neither target nor non-target — model may be blending or failing")
        else:
            print("  No swap bumps. Attraction/blending persists.")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
