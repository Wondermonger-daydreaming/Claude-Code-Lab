"""
Diagnostic: Does the coexistence state exist as a TRUE fixed point?

Key question: when both bumps are established and we remove drives,
does the system CONVERGE to a fixed point or slowly drift?

If it converges: Newton should find it (numerical issue)
If it drifts: the coexistence "state" is a slow manifold, not a FP
"""

import numpy as np
from scipy.special import i0
import sys
sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve,
    compute_full_jacobian
)


def diagnostic_simulation(cue_gain=0.0, N=48, J_0=1.0, J_1=6.0,
                           J_cross=0.5, kappa=2.0, input_gain=5.0,
                           r_max=1.0, beta=5.0, h0=0.5,
                           dt=0.1, tau=10.0):
    """
    Simulate the full coupled system and track:
    1. Residual ||F(r)|| over time (how close to a FP)
    2. Drift rate ||dr/dt|| over time
    3. Dominance D over time
    4. Bump positions over time (do they drift?)
    """
    W, preferred = build_within_weights(N, J_0, J_1)
    theta1, theta2 = np.pi / 4, -np.pi / 4

    drive_A = input_gain * tuning_curve(theta1, preferred, kappa)
    drive_B = input_gain * tuning_curve(theta2, preferred, kappa)
    cue_A = cue_gain * tuning_curve(theta1, preferred, kappa)

    # Phase 1: Establish both bumps (1000 steps with drives)
    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A, r_max, beta, h0)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B, r_max, beta, h0)

    for step in range(1000):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + drive_A + cross_A
        h_B = W @ r_B + drive_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)
        r_A = np.maximum(0, r_A + (-r_A + f_A) * (dt / tau))
        r_B = np.maximum(0, r_B + (-r_B + f_B) * (dt / tau))

    print(f"After drives: mean_A={np.mean(r_A):.4f}, mean_B={np.mean(r_B):.4f}, "
          f"max_A={np.max(r_A):.4f}, max_B={np.max(r_B):.4f}")

    # Phase 2: Remove drives, add cue, track for 50000 steps
    history = {
        'time': [], 'residual': [], 'drift_rate': [],
        'D': [], 'mean_A': [], 'mean_B': [],
        'peak_A_angle': [], 'peak_B_angle': [],
        'max_A': [], 'max_B': [],
    }

    for step in range(50000):
        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)
        h_A = W @ r_A + cue_A + cross_A
        h_B = W @ r_B + cross_B
        f_A = sigmoid(h_A, r_max, beta, h0)
        f_B = sigmoid(h_B, r_max, beta, h0)

        dr_A = (-r_A + f_A) / tau
        dr_B = (-r_B + f_B) / tau

        r_A = np.maximum(0, r_A + dr_A * dt)
        r_B = np.maximum(0, r_B + dr_B * dt)

        if step % 100 == 0:
            # Residual = ||F(r)|| = ||-r + σ(h)||
            res_A = -r_A + f_A
            res_B = -r_B + f_B
            residual = np.sqrt(np.sum(res_A**2) + np.sum(res_B**2))

            # Drift rate
            drift = np.sqrt(np.sum(dr_A**2) + np.sum(dr_B**2))

            # Bump peak positions
            peak_A = preferred[np.argmax(r_A)] * 180 / np.pi
            peak_B = preferred[np.argmax(r_B)] * 180 / np.pi

            history['time'].append(step * dt)
            history['residual'].append(residual)
            history['drift_rate'].append(drift)
            history['D'].append(np.mean(r_A) - np.mean(r_B))
            history['mean_A'].append(np.mean(r_A))
            history['mean_B'].append(np.mean(r_B))
            history['peak_A_angle'].append(peak_A)
            history['peak_B_angle'].append(peak_B)
            history['max_A'].append(np.max(r_A))
            history['max_B'].append(np.max(r_B))

    return history, r_A, r_B, W, preferred


def compute_eigenvalue_spectrum(r_A, r_B, W, preferred, cue_gain,
                                 J_cross=0.5, kappa=2.0, N=48):
    """Compute eigenvalues at the final state."""
    theta1 = np.pi / 4
    cue_A = cue_gain * tuning_curve(theta1, preferred, kappa)
    cross_A = -J_cross * np.mean(r_B)
    cross_B = -J_cross * np.mean(r_A)
    h_A = W @ r_A + cue_A + cross_A
    h_B = W @ r_B + cross_B
    J = compute_full_jacobian(r_A, r_B, h_A, h_B, W, J_cross)
    evals = np.linalg.eigvals(J)
    idx = np.argsort(-evals.real)
    return evals[idx]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    cue_gains = [0.0, 0.01, 0.02, 0.05]

    fig, axes = plt.subplots(len(cue_gains), 5, figsize=(22, 4 * len(cue_gains)))

    for row, cg in enumerate(cue_gains):
        print(f"\n{'='*60}")
        print(f"Diagnostic at cue_gain = {cg}")
        print(f"{'='*60}")

        hist, r_A, r_B, W, pref = diagnostic_simulation(cue_gain=cg)

        # Final state analysis
        evals = compute_eigenvalue_spectrum(r_A, r_B, W, pref, cg)
        print(f"  Final: D={hist['D'][-1]:.6f}, residual={hist['residual'][-1]:.2e}")
        print(f"  Final: max_A={hist['max_A'][-1]:.4f}, max_B={hist['max_B'][-1]:.4f}")
        print(f"  Top 5 eigenvalues: {', '.join(f'{e.real:.6f}' for e in evals[:5])}")
        print(f"  Bump A at {hist['peak_A_angle'][-1]:.1f}°, "
              f"Bump B at {hist['peak_B_angle'][-1]:.1f}°")

        t = hist['time']

        # Residual
        ax = axes[row, 0]
        ax.semilogy(t, hist['residual'], color='#c0392b')
        ax.set_ylabel('||F(r)||')
        ax.set_title(f'cue={cg}: Residual', fontsize=9)

        # Drift rate
        ax = axes[row, 1]
        ax.semilogy(t, hist['drift_rate'], color='#2d5a7b')
        ax.set_ylabel('||dr/dt||')
        ax.set_title('Drift rate', fontsize=9)

        # Dominance
        ax = axes[row, 2]
        ax.plot(t, hist['D'], color='#8e44ad')
        ax.axhline(y=0, color='gray', alpha=0.3)
        ax.set_ylabel('D')
        ax.set_title('Dominance', fontsize=9)

        # Bump heights
        ax = axes[row, 3]
        ax.plot(t, hist['max_A'], color='#2d5a7b', label='A')
        ax.plot(t, hist['max_B'], color='#c0392b', label='B')
        ax.set_ylabel('max(r)')
        ax.set_title('Bump heights', fontsize=9)
        ax.legend(fontsize=7)

        # Bump positions
        ax = axes[row, 4]
        ax.plot(t, hist['peak_A_angle'], color='#2d5a7b', label='A')
        ax.plot(t, hist['peak_B_angle'], color='#c0392b', label='B')
        ax.axhline(y=45, color='#2d5a7b', alpha=0.3, ls='--')
        ax.axhline(y=-45, color='#c0392b', alpha=0.3, ls='--')
        ax.set_ylabel('Peak angle (°)')
        ax.set_title('Bump positions', fontsize=9)
        ax.legend(fontsize=7)

        for ax in axes[row]:
            ax.set_xlabel('Time')

    plt.suptitle('Coexistence Diagnostic: Does a True Fixed Point Exist?\n'
                 '50000 steps of simulation after removing drives',
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/corpus/code/figures/fig50_coexistence_diagnostic.png',
                dpi=200, bbox_inches='tight')
    plt.close()
    print("\nSaved fig50_coexistence_diagnostic.png")
