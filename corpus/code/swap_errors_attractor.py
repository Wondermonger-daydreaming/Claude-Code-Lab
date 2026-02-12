"""
==========================================================================
SWAP ERRORS FROM RECURRENT ATTRACTOR DYNAMICS
==========================================================================

The FINAL discriminating test in the swap error cascade.

Previous results:
  #1  swap_errors_geometric.py:      Fixed equal weights     → blending
  #2  swap_errors_stochastic.py:     Beta(0.5,0.5) stipulated → swap bumps
  #3  swap_errors_normalization.py:  Divisive normalization   → blending

The model:
    Ring attractor network (Compte et al., 2000; Ben-Yishai et al., 1995).

    Connectivity: J(Δφ) = -J_0 + J_1 * cos(Δφ)
    - J_0 > 0: global inhibition (bounds total activity)
    - J_1 > 0: local excitation (neurons with similar tuning excite each other)
    - When J_1 > critical threshold: a single "bump" of activity is the
      stable attractor state.

    Two-phase dynamics:
    - Stimulus phase: feedforward drive from both items → two bumps form
    - Maintenance phase: drive OFF → bumps compete through global inhibition
    - Only one bump can survive → which one is determined by noise
    - Over many trials → bimodal distribution → swap errors

    Activation: threshold-linear [x]_+ = max(0, x)
    This is the standard for ring attractor models. The threshold creates
    the nonlinearity needed for winner-take-all WITHOUT the instability
    of power-law activations (our previous attempt with f(x)=x² exploded).

If attractor dynamics produce swap bumps: the mechanism is NEURAL (geometry
+ recurrence), not an abstract "binding" process. The mixture model's
"swap" component corresponds to probabilistic attractor selection.

If not: something beyond our model is needed.
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
    'geometric': '#8e44ad',
    'blend': '#95a5a6',
}


def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))


def build_ring_attractor_weights(preferred_angles, J_0, J_1):
    """
    Ring attractor connectivity (Ben-Yishai et al., 1995).

    W_ij = (-J_0 + J_1 * cos(phi_i - phi_j)) / N

    - J_0 > 0: uniform inhibition (global)
    - J_1 > 0: cosine-tuned excitation (local)
    - Divided by N for mean-field scaling

    The Mexican hat profile: excitation for similar tuning,
    inhibition for dissimilar tuning.
    """
    N = len(preferred_angles)
    phi = preferred_angles
    # Outer difference matrix
    dphi = phi[:, np.newaxis] - phi[np.newaxis, :]
    W = (-J_0 + J_1 * np.cos(dphi)) / N
    return W


def run_attractor_trial(theta1, theta2, preferred_angles, kappa,
                        W, noise_sigma, dt, tau, n_steps,
                        stim_steps, input_gain=1.0,
                        maint_drive_fraction=0.0):
    """
    Run a single trial of the two-phase ring attractor model.

    Phase 1 (stimulus): Both items drive the population.
    Phase 2 (maintenance): Drive OFF. Recurrence sustains + competes.

    Dynamics:
        tau * dr/dt = -r + [W @ r + I_ext(t) + noise]_+

    Returns: final response vector (N,)
    """
    N = len(preferred_angles)

    # Feedforward drive from both items
    drive1 = np.array([tuning_curve(theta1, phi, kappa)
                       for phi in preferred_angles])
    drive2 = np.array([tuning_curve(theta2, phi, kappa)
                       for phi in preferred_angles])
    drive_full = input_gain * (drive1 + drive2)
    drive_maint = maint_drive_fraction * drive_full

    # Initialize at low uniform activity
    r = np.ones(N) * 0.1

    for step in range(n_steps):
        # Phase-dependent drive
        drive = drive_full if step < stim_steps else drive_maint

        # Total input
        noise = np.random.randn(N) * noise_sigma
        h = W @ r + drive + noise

        # Threshold-linear activation: [h]_+
        f_h = np.maximum(0, h)

        # Euler step
        dr = (-r + f_h) * (dt / tau)
        r = np.maximum(0, r + dr)

    return r


def run_attractor_trial_with_history(theta1, theta2, preferred_angles, kappa,
                                      W, noise_sigma, dt, tau, n_steps,
                                      stim_steps, input_gain=1.0):
    """Same as run_attractor_trial but returns full time course."""
    N = len(preferred_angles)

    drive1 = np.array([tuning_curve(theta1, phi, kappa)
                       for phi in preferred_angles])
    drive2 = np.array([tuning_curve(theta2, phi, kappa)
                       for phi in preferred_angles])
    drive_full = input_gain * (drive1 + drive2)

    template1 = drive1 / (np.linalg.norm(drive1) + 1e-12)
    template2 = drive2 / (np.linalg.norm(drive2) + 1e-12)

    r = np.ones(N) * 0.1
    strength1 = np.zeros(n_steps)
    strength2 = np.zeros(n_steps)
    total_activity = np.zeros(n_steps)

    for step in range(n_steps):
        drive = drive_full if step < stim_steps else np.zeros(N)
        noise = np.random.randn(N) * noise_sigma
        h = W @ r + drive + noise
        f_h = np.maximum(0, h)
        dr = (-r + f_h) * (dt / tau)
        r = np.maximum(0, r + dr)

        r_norm = r / (np.linalg.norm(r) + 1e-12)
        strength1[step] = r_norm @ template1
        strength2[step] = r_norm @ template2
        total_activity[step] = np.sum(r)

    return r, strength1, strength2, total_activity


def run_attractor_experiment(N_neurons, kappa, noise_sigma,
                             J_0, J_1, n_trials, separation,
                             dt=1.0, tau=10.0, n_steps=500,
                             stim_steps=100, input_gain=5.0):
    """
    Two-item experiment with ring attractor dynamics.
    """
    preferred_angles = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)
    theta1 = 0.0
    theta2 = separation

    W = build_ring_attractor_weights(preferred_angles, J_0, J_1)

    # Precompute single-item decode manifold
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    expected_all = np.array([[tuning_curve(t, phi, kappa)
                              for phi in preferred_angles]
                             for t in theta_grid])

    errors = np.zeros(n_trials)

    for t in range(n_trials):
        response = run_attractor_trial(
            theta1, theta2, preferred_angles, kappa,
            W, noise_sigma, dt, tau, n_steps,
            stim_steps, input_gain
        )

        # Cosine similarity decode
        r_norm = response / (np.linalg.norm(response) + 1e-12)
        e_norms = expected_all / (np.linalg.norm(expected_all, axis=1,
                                                  keepdims=True) + 1e-12)
        similarities = e_norms @ r_norm
        decoded = theta_grid[np.argmax(similarities)]

        error = decoded - theta1
        errors[t] = (error + np.pi) % (2 * np.pi) - np.pi

    return errors


# ══════════════════════════════════════════════════════════════════════════
# DIAGNOSTIC: VERIFY SINGLE-BUMP SELF-SUSTAINING
# ══════════════════════════════════════════════════════════════════════════

def diagnostic_single_bump():
    """
    Before the main experiment: verify the network can sustain a single
    bump without drive. If it can't, attractor dynamics are impossible.
    """
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    dt, tau = 1.0, 10.0

    print("  Diagnostic: can the network sustain a single bump?")
    print(f"  {'J_0':>6s} {'J_1':>6s} {'peak':>10s} {'total':>10s} {'status':>10s}")

    working_params = None

    for J_0, J_1 in [(1, 2), (1, 4), (2, 6), (2, 8), (3, 10),
                      (1, 8), (0.5, 4), (0.5, 6), (1, 10), (2, 12)]:
        W = build_ring_attractor_weights(preferred, J_0, J_1)

        # Start with a bump at theta=0 (from drive)
        drive = np.array([tuning_curve(0.0, phi, kappa) for phi in preferred])
        r = np.maximum(0, W @ (drive * 5) + drive * 5)  # kick-start

        # Run 300 steps with NO drive
        for step in range(300):
            h = W @ r
            r_new = np.maximum(0, h)
            dr = (-r + r_new) * (dt / tau)
            r = np.maximum(0, r + dr)

        peak = np.max(r)
        total = np.sum(r)
        survives = peak > 0.01

        status = "✓ SUSTAINS" if survives else "✗ decays"
        print(f"  {J_0:6.1f} {J_1:6.1f} {peak:10.4f} {total:10.4f} {status:>10s}")

        if survives and working_params is None:
            working_params = (J_0, J_1)

    return working_params


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 12: RECURRENT STRENGTH AND SWAP ERRORS
# ══════════════════════════════════════════════════════════════════════════

def plot_recurrence_sweep(J_0_base, J_1_base):
    """
    The decisive figure. Three regimes of recurrent strength,
    using parameters verified by the diagnostic.
    """
    fig, axes = plt.subplots(2, 3, figsize=(17, 10))

    N_neurons = 48
    kappa = 2.0
    noise_sigma = 0.3    # substantial noise to break symmetry
    n_trials = 5000
    separation = np.pi / 2
    n_steps = 500
    stim_steps = 100
    dt, tau = 1.0, 10.0
    input_gain = 5.0

    # Scale from verified base parameters
    configs = [
        (J_0_base * 0.3, J_1_base * 0.3,
         f'Weak recurrence\n(J₁={J_1_base*0.3:.1f})', COLORS['blend']),
        (J_0_base, J_1_base,
         f'Moderate recurrence\n(J₁={J_1_base:.1f})', COLORS['geometric']),
        (J_0_base * 2.0, J_1_base * 2.0,
         f'Strong recurrence\n(J₁={J_1_base*2.0:.1f})', COLORS['attractor']),
    ]

    all_errors = []

    for col, (J_0, J_1, title, color) in enumerate(configs):
        print(f"  Running J_0={J_0:.1f}, J_1={J_1:.1f} ({n_trials} trials)...")
        errors = run_attractor_experiment(
            N_neurons, kappa, noise_sigma,
            J_0, J_1, n_trials, separation,
            dt, tau, n_steps, stim_steps, input_gain
        )
        all_errors.append(errors)

        # Top row: error distributions
        ax = axes[0, col]
        bins = np.linspace(-np.pi, np.pi, 100)
        ax.hist(errors, bins=bins, density=True, alpha=0.5,
                color=color, edgecolor='white', linewidth=0.3)

        ax.axvline(x=0, color=COLORS['item1'], linestyle=':',
                   linewidth=2, label='Item 1 (target)', alpha=0.7)
        ax.axvline(x=separation, color=COLORS['item2'], linestyle=':',
                   linewidth=2, label='Item 2 (non-target)', alpha=0.7)

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

    # Bottom row: temporal dynamics
    preferred_angles = np.linspace(-np.pi, np.pi, N_neurons, endpoint=False)

    for col, (J_0, J_1, title, color) in enumerate(configs):
        ax2 = axes[1, col]
        W = build_ring_attractor_weights(preferred_angles, J_0, J_1)

        for trial_idx in range(5):
            _, s1, s2, total = run_attractor_trial_with_history(
                0.0, separation, preferred_angles, kappa,
                W, noise_sigma, dt, tau, n_steps, stim_steps, input_gain
            )

            time = np.arange(n_steps) * dt
            alpha = 0.3 if trial_idx > 0 else 0.9
            lw = 0.8 if trial_idx > 0 else 2.0
            label1 = 'Item 1' if trial_idx == 0 else None
            label2 = 'Item 2' if trial_idx == 0 else None
            ax2.plot(time, s1, color=COLORS['item1'],
                     alpha=alpha, linewidth=lw, label=label1)
            ax2.plot(time, s2, color=COLORS['item2'],
                     alpha=alpha, linewidth=lw, label=label2)

        ax2.axvline(x=stim_steps * dt, color='gray', linestyle='--',
                    linewidth=1, alpha=0.5, label='Drive OFF')
        ax2.set_xlabel('Time (a.u.)')
        ax2.set_ylabel('Template similarity')
        ax2.set_title(f'Temporal dynamics (J₁={J_1:.1f})',
                     fontsize=10, color=color)
        ax2.legend(fontsize=7, loc='best')

    plt.suptitle(
        'Ring attractor: does recurrence produce winner-take-all\n'
        'swap errors from geometric representations?',
        fontsize=13, fontweight='bold', y=1.02
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig12_attractor_swaps.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 12: Ring attractor sweep saved")

    return all_errors


# ══════════════════════════════════════════════════════════════════════════
# FIGURE 13: ATTRACTOR VS STOCHASTIC — THE COMPARISON
# ══════════════════════════════════════════════════════════════════════════

def plot_attractor_vs_stochastic(attractor_errors):
    """
    Direct comparison with the stipulated Beta(0.5,0.5) model.
    """
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5))

    separation = np.pi / 2
    bins = np.linspace(-np.pi, np.pi, 100)

    # Panel 1: Re-run stochastic
    import sys
    sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
    from swap_errors_stochastic import run_stochastic_swap
    print("  Re-running Beta(0.5,0.5) for comparison...")
    stochastic_errors = run_stochastic_swap(
        N_neurons=48, kappa=2.0, noise_sigma=0.15,
        n_trials=5000, separation=separation,
        alpha_beta=0.5, beta_beta=0.5
    )

    ax = axes[0]
    ax.hist(stochastic_errors, bins=bins, density=True, alpha=0.5,
            color=COLORS['swap_bump'], edgecolor='white', linewidth=0.3)
    ax.axvline(x=0, color=COLORS['item1'], linestyle=':', linewidth=2, alpha=0.7)
    ax.axvline(x=separation, color=COLORS['item2'], linestyle=':', linewidth=2, alpha=0.7)
    near1 = 100 * np.mean(np.abs(stochastic_errors) < 0.3)
    near2 = 100 * np.mean(np.abs(stochastic_errors - separation) < 0.3)
    ax.set_title('Stipulated: Beta(0.5,0.5)\n(Sim #2)', fontsize=11,
                 fontweight='bold', color=COLORS['swap_bump'])
    ax.set_xlabel('Decoding error (rad)')
    ax.set_ylabel('Probability density')
    ax.set_xlim(-np.pi, np.pi)
    ax.text(0.97, 0.93, f'Near target: {near1:.1f}%\nNear non-target: {near2:.1f}%',
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor=COLORS['swap_bump'], alpha=0.8))

    # Panel 2: Strong attractor
    ax = axes[1]
    strong_errors = attractor_errors[2]
    ax.hist(strong_errors, bins=bins, density=True, alpha=0.5,
            color=COLORS['attractor'], edgecolor='white', linewidth=0.3)
    ax.axvline(x=0, color=COLORS['item1'], linestyle=':', linewidth=2, alpha=0.7)
    ax.axvline(x=separation, color=COLORS['item2'], linestyle=':', linewidth=2, alpha=0.7)
    near1 = 100 * np.mean(np.abs(strong_errors) < 0.3)
    near2 = 100 * np.mean(np.abs(strong_errors - separation) < 0.3)
    ax.set_title('Mechanistic: Ring attractor\n(Sim #4, strong recurrence)', fontsize=11,
                 fontweight='bold', color=COLORS['attractor'])
    ax.set_xlabel('Decoding error (rad)')
    ax.set_xlim(-np.pi, np.pi)
    ax.text(0.97, 0.93, f'Near target: {near1:.1f}%\nNear non-target: {near2:.1f}%',
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor=COLORS['attractor'], alpha=0.8))

    # Panel 3: Overlay
    ax = axes[2]
    ax.hist(stochastic_errors, bins=bins, density=True, alpha=0.3,
            color=COLORS['swap_bump'], edgecolor='white', linewidth=0.3,
            label='Stipulated (Beta)')
    ax.hist(strong_errors, bins=bins, density=True, alpha=0.3,
            color=COLORS['attractor'], edgecolor='white', linewidth=0.3,
            label='Mechanistic (Attractor)')
    ax.axvline(x=0, color=COLORS['item1'], linestyle=':', linewidth=2, alpha=0.7)
    ax.axvline(x=separation, color=COLORS['item2'], linestyle=':', linewidth=2, alpha=0.7)
    ax.set_title('Overlay comparison', fontsize=11, fontweight='bold')
    ax.set_xlabel('Decoding error (rad)')
    ax.set_xlim(-np.pi, np.pi)
    ax.legend(fontsize=9)

    plt.suptitle(
        'Does the ring attractor produce swap errors that match\n'
        'the stipulated stochastic model?',
        fontsize=13, fontweight='bold', y=1.03
    )
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig13_attractor_vs_stochastic.png',
                dpi=180, bbox_inches='tight')
    plt.close()
    print("✓ Figure 13: Attractor vs stochastic comparison saved")


# ══════════════════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 65)
    print("RECURRENT ATTRACTOR DYNAMICS AND SWAP ERRORS")
    print("Ring attractor model (Ben-Yishai / Compte)")
    print("The final test: does neural recurrence break the blend?")
    print("=" * 65)
    print()

    print("─── Diagnostic: single-bump sustainability ───")
    working = diagnostic_single_bump()
    print()

    if working is None:
        print("  ✗ No parameter regime found with self-sustaining bumps.")
        print("  Cannot proceed with two-item experiment.")
    else:
        J_0, J_1 = working
        print(f"  Using base parameters: J_0={J_0}, J_1={J_1}")
        print()

        print("─── Figure 12: Recurrence strength sweep ───")
        all_errors = plot_recurrence_sweep(J_0, J_1)
        print()

        # Check for bimodality
        strong_errors = all_errors[2]
        near_item2 = np.abs(strong_errors - np.pi / 2) < 0.3
        swap_pct = 100 * np.mean(near_item2)

        if swap_pct > 5:
            print(f"  *** Swap bump detected: {swap_pct:.1f}% near non-target ***")
            print()
            print("─── Figure 13: Attractor vs stochastic ───")
            plot_attractor_vs_stochastic(all_errors)
        else:
            print(f"  Swap rate near non-target: {swap_pct:.1f}%")
            near_item1 = np.abs(strong_errors) < 0.3
            correct_pct = 100 * np.mean(near_item1)
            mean_bias = np.mean(strong_errors)
            print(f"  Near target: {correct_pct:.1f}%, Mean bias: {mean_bias:.3f}")

    print()
    print("=" * 65)
    print("Trust the run.")
    print("=" * 65)
