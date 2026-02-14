"""
==========================================================================
HETEROGENEITY TEST: DOES SYMMETRY-BREAKING WIDEN THE SEPARATRIX?
==========================================================================

Prediction: adding heterogeneity (non-uniform connectivity)
should WIDEN the instability window from the razor-thin [0.349, 0.358]
to a broader regime.

Test: Add Gaussian noise to the weight matrices at various amplitudes
and measure:
  1. Where coexistence becomes unstable (λ_dom crosses zero)
  2. Where coexistence ceases to exist (bumps collapse)
  3. The width of the unstable window

If prediction is right: window widens with noise amplitude.
If wrong: window narrows or stays the same.

Also test: critical slowing down near J_cross*.
Measure convergence time as function of J_cross to see if
it diverges near the critical point.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

import sys
sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve,
    COLORS
)

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

N = 48
J_0, J_1 = 1.0, 6.0
KAPPA, INPUT_GAIN = 2.0, 5.0
BETA, H0 = 5.0, 0.5
DT, TAU = 0.1, 10.0
GOLDSTONE_THRESH = 1e-3


def build_noisy_weights(N, J_0, J_1, noise_sigma):
    """Build within-network weights with additive Gaussian noise."""
    W_clean, preferred = build_within_weights(N, J_0, J_1)
    noise = np.random.randn(N, N) * noise_sigma / np.sqrt(N)
    # Keep it symmetric (biological plausibility)
    noise = (noise + noise.T) / 2
    W = W_clean + noise
    return W, preferred, W_clean


def residual(x, W, J_cross):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([-r_A + sigmoid(h_A), -r_B + sigmoid(h_B)])


def jacobian(x, W, J_cross):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    D_A = np.diag(sigmoid_derivative(h_A))
    D_B = np.diag(sigmoid_derivative(h_B))
    cm = np.full((N, N), -J_cross / N)
    J = np.zeros((2*N, 2*N))
    J[:N, :N] = -np.eye(N) + D_A @ W
    J[:N, N:] = D_A @ cm
    J[N:, :N] = D_B @ cm
    J[N:, N:] = -np.eye(N) + D_B @ W
    return J


def find_coexistence(W, J_cross, preferred):
    """Find coexistence FP at cue=0 by simulation + Newton."""
    theta1, theta2 = np.pi/4, -np.pi/4
    drive_A = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
    drive_B = INPUT_GAIN * tuning_curve(theta2, preferred, KAPPA)

    r_A = sigmoid(W @ (drive_A * 0.3) + drive_A)
    r_B = sigmoid(W @ (drive_B * 0.3) + drive_B)
    for _ in range(500):
        h_A = W @ r_A + drive_A
        h_B = W @ r_B + drive_B
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    for _ in range(50000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, J_cross),
                             fprime=lambda x, W, j: jacobian(x, W, j),
                             full_output=True, maxfev=5000)
    res = np.max(np.abs(residual(sol, W, J_cross)))
    return sol[:N], sol[N:], res


def analyze_at_jcross(W, J_cross, preferred):
    """Return (lambda_dom, n_goldstone, has_bumps, convergence_time)."""
    r_A, r_B, res = find_coexistence(W, J_cross, preferred)

    has_bumps = np.max(r_A) > 0.3 and np.max(r_B) > 0.3
    if res > 1e-4 or not has_bumps:
        return np.nan, 0, False, np.nan

    x = np.concatenate([r_A, r_B])
    J = jacobian(x, W, J_cross)
    evals = np.linalg.eigvals(J)
    evals_real = np.sort(evals.real)[::-1]

    # Separate Goldstone from genuine
    n_gold = np.sum(np.abs(evals_real) < GOLDSTONE_THRESH)
    genuine = evals_real[np.abs(evals_real) >= GOLDSTONE_THRESH]

    if len(genuine) == 0:
        return 0.0, n_gold, True, np.nan

    lam_dom = genuine[0]

    # Convergence time: simulate perturbation and measure decay
    perturb = np.random.randn(2*N) * 0.001
    x_pert = x + perturb
    r_A_p, r_B_p = x_pert[:N], x_pert[N:]
    diffs = []
    for t in range(5000):
        h_A = W @ r_A_p - J_cross * np.mean(r_B_p)
        h_B = W @ r_B_p - J_cross * np.mean(r_A_p)
        r_A_p = np.maximum(0, r_A_p + (-r_A_p + sigmoid(h_A)) * DT/TAU)
        r_B_p = np.maximum(0, r_B_p + (-r_B_p + sigmoid(h_B)) * DT/TAU)
        diff = np.sqrt(np.mean((r_A_p - r_A)**2) + np.mean((r_B_p - r_B)**2))
        diffs.append(diff)
        if diff < 1e-8:
            break

    # Estimate convergence time as time to reach 1/e of initial
    diffs = np.array(diffs)
    initial = diffs[0] if len(diffs) > 0 else 1.0
    target = initial / np.e
    crossings = np.where(diffs < target)[0]
    conv_time = crossings[0] * DT if len(crossings) > 0 else 5000 * DT

    return lam_dom, n_gold, True, conv_time


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 1: HETEROGENEITY TEST
# ═══════════════════════════════════════════════════════════════════

def heterogeneity_experiment():
    print("=" * 70)
    print("EXPERIMENT 1: HETEROGENEITY TEST")
    print("=" * 70)

    noise_levels = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
    jc_values = np.linspace(0.25, 0.38, 30)
    n_trials = 5  # Average over random seeds

    all_data = {}

    for sigma in noise_levels:
        print(f"\n  Noise σ = {sigma:.2f}")
        trial_results = []

        for trial in range(n_trials):
            np.random.seed(42 + trial)
            W, preferred, _ = build_noisy_weights(N, J_0, J_1, sigma)
            results = []

            for jc in jc_values:
                lam, ng, has_bumps, ct = analyze_at_jcross(W, jc, preferred)
                results.append({
                    'J_cross': jc, 'lambda_dom': lam,
                    'n_goldstone': ng, 'has_bumps': has_bumps,
                    'conv_time': ct
                })

            trial_results.append(results)

            # Find boundaries for this trial
            valid = [r for r in results if r['has_bumps'] and not np.isnan(r['lambda_dom'])]
            if valid:
                jc_exist_max = max(r['J_cross'] for r in valid)
                unstable = [r for r in valid if r['lambda_dom'] > 0]
                jc_unstable_min = min(r['J_cross'] for r in unstable) if unstable else None

                if jc_unstable_min:
                    print(f"    Trial {trial}: unstable from {jc_unstable_min:.4f}, "
                          f"exists to {jc_exist_max:.4f}, "
                          f"window = {jc_exist_max - jc_unstable_min:.4f}")
                else:
                    print(f"    Trial {trial}: all stable, exists to {jc_exist_max:.4f}")
            else:
                print(f"    Trial {trial}: no valid coexistence found")

        all_data[sigma] = trial_results

    return all_data, jc_values


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT 2: CRITICAL SLOWING DOWN
# ═══════════════════════════════════════════════════════════════════

def critical_slowing_experiment():
    print("\n" + "=" * 70)
    print("EXPERIMENT 2: CRITICAL SLOWING DOWN")
    print("=" * 70)

    W, preferred = build_within_weights(N, J_0, J_1)
    jc_values = np.linspace(0.20, 0.36, 40)

    results = []
    for jc in jc_values:
        lam, ng, has_bumps, ct = analyze_at_jcross(W, jc, preferred)
        results.append({
            'J_cross': jc, 'lambda_dom': lam,
            'conv_time': ct, 'has_bumps': has_bumps
        })
        if has_bumps and not np.isnan(lam):
            print(f"  J_cross={jc:.4f}: λ_dom={lam:+.6f}, τ_conv={ct:.1f}")

    return results


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_experiments(het_data, jc_values, csd_results, save_path):
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.40)
    # Override font sizes for this multi-panel figure
    plt.rcParams.update({'font.size': 13, 'axes.titlesize': 14, 'axes.labelsize': 13})

    # ── (0,0) λ_dom vs J_cross for different noise levels ──
    ax = fig.add_subplot(gs[0, 0])
    cmap = plt.cm.viridis
    noise_levels = sorted(het_data.keys())
    for i, sigma in enumerate(noise_levels):
        trials = het_data[sigma]
        # Average lambda_dom across trials
        all_lams = []
        for trial in trials:
            lams = []
            for r in trial:
                if r['has_bumps'] and not np.isnan(r['lambda_dom']):
                    lams.append(r['lambda_dom'])
                else:
                    lams.append(np.nan)
            all_lams.append(lams)
        mean_lams = np.nanmean(all_lams, axis=0)
        c = cmap(i / max(1, len(noise_levels) - 1))
        ax.plot(jc_values, mean_lams, 'o-', color=c, ms=3, lw=1.5,
                label=f'σ={sigma:.2f}')
    ax.axhline(y=0, color='black', ls='--', lw=1.5, alpha=0.4)
    ax.set_xlabel(r'$J_\times$')
    ax.set_ylabel(r'$\lambda_{\mathrm{dom}}$ (mean over trials)')
    ax.set_title('Dominance Eigenvalue vs Noise', fontweight='bold')
    ax.legend(fontsize=7, ncol=2)

    # ── (0,1) Instability onset J_cross vs noise level ──
    ax = fig.add_subplot(gs[0, 1])
    onset_jc = []
    collapse_jc = []
    window_widths = []
    for sigma in noise_levels:
        trials = het_data[sigma]
        onsets = []
        collapses = []
        for trial in trials:
            valid = [r for r in trial if r['has_bumps'] and not np.isnan(r['lambda_dom'])]
            if not valid:
                continue
            collapse = max(r['J_cross'] for r in valid)
            collapses.append(collapse)
            unstable = [r for r in valid if r['lambda_dom'] > 0]
            if unstable:
                onsets.append(min(r['J_cross'] for r in unstable))
        onset_jc.append((np.mean(onsets) if onsets else np.nan,
                         np.std(onsets) if len(onsets) > 1 else 0))
        collapse_jc.append((np.mean(collapses) if collapses else np.nan,
                            np.std(collapses) if len(collapses) > 1 else 0))
        if onsets and collapses:
            widths = [c - o for o, c in zip(onsets, collapses) if not np.isnan(o)]
            window_widths.append((np.mean(widths) if widths else np.nan,
                                  np.std(widths) if len(widths) > 1 else 0))
        else:
            window_widths.append((np.nan, 0))

    onset_means = [o[0] for o in onset_jc]
    onset_stds = [o[1] for o in onset_jc]
    collapse_means = [c[0] for c in collapse_jc]
    collapse_stds = [c[1] for c in collapse_jc]

    ax.errorbar(noise_levels, onset_means, yerr=onset_stds,
                fmt='o-', color=COLORS['critical'], lw=2, ms=6, capsize=3,
                label='Instability onset')
    ax.errorbar(noise_levels, collapse_means, yerr=collapse_stds,
                fmt='s-', color=COLORS['stable'], lw=2, ms=6, capsize=3,
                label='Coexistence collapse')
    ax.fill_between(noise_levels, onset_means, collapse_means,
                    alpha=0.2, color=COLORS['dominance'])
    ax.set_xlabel(r'Noise $\sigma$')
    ax.set_ylabel(r'$J_\times$')
    ax.set_title('Instability Window vs Heterogeneity', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (0,2) Window width vs noise ──
    ax = fig.add_subplot(gs[0, 2])
    widths_means = [w[0] for w in window_widths]
    widths_stds = [w[1] for w in window_widths]
    ax.errorbar(noise_levels, widths_means, yerr=widths_stds,
                fmt='o-', color=COLORS['dominance'], lw=2, ms=8, capsize=4)
    ax.set_xlabel(r'Noise $\sigma$')
    ax.set_ylabel(r'$\Delta J_\times$ (window width)')
    ax.set_title('Instability Window Width', fontweight='bold')
    ax.axhline(y=widths_means[0] if not np.isnan(widths_means[0]) else 0,
               color='gray', ls=':', lw=1, alpha=0.5, label='σ=0 baseline')
    ax.legend(fontsize=8)

    # ── (1,0) Critical slowing down: λ_dom ──
    ax = fig.add_subplot(gs[1, 0])
    csd_valid = [r for r in csd_results if r['has_bumps'] and not np.isnan(r['lambda_dom'])]
    jc_csd = [r['J_cross'] for r in csd_valid]
    lam_csd = [r['lambda_dom'] for r in csd_valid]
    colors_csd = ['#e74c3c' if l > 0 else '#2196F3' for l in lam_csd]
    ax.scatter(jc_csd, lam_csd, c=colors_csd, s=30, zorder=3)
    ax.plot(jc_csd, lam_csd, '-', color='gray', lw=0.8, alpha=0.5)
    ax.axhline(y=0, color='black', ls='--', lw=1)
    ax.set_xlabel(r'$J_\times$')
    ax.set_ylabel(r'$\lambda_{\mathrm{dom}}$')
    ax.set_title(r'$\lambda_{\mathrm{dom}}$ Near Critical Point (clean)', fontweight='bold')

    # ── (1,1) Critical slowing down: convergence time ──
    ax = fig.add_subplot(gs[1, 1])
    ct_valid = [r for r in csd_valid if not np.isnan(r['conv_time']) and r['lambda_dom'] < 0]
    if ct_valid:
        ax.plot([r['J_cross'] for r in ct_valid],
                [r['conv_time'] for r in ct_valid],
                'o-', color=COLORS['dominance'], lw=2, ms=5)
        ax.set_xlabel(r'$J_\times$')
        ax.set_ylabel(r'Convergence time $\tau$')
        ax.set_title('Critical Slowing Down', fontweight='bold')

    # ── (1,2) τ vs 1/|λ_dom| (should be linear if τ ~ 1/|λ_dom|) ──
    ax = fig.add_subplot(gs[1, 2])
    if ct_valid:
        inv_lam = [1.0 / abs(r['lambda_dom']) for r in ct_valid if abs(r['lambda_dom']) > 1e-5]
        ct_vals = [r['conv_time'] for r in ct_valid if abs(r['lambda_dom']) > 1e-5]
        ax.scatter(inv_lam, ct_vals, c=COLORS['dominance'], s=30)
        # Fit line
        if len(inv_lam) > 2:
            coeffs = np.polyfit(inv_lam, ct_vals, 1)
            x_fit = np.linspace(min(inv_lam), max(inv_lam), 100)
            ax.plot(x_fit, np.polyval(coeffs, x_fit), '--', color='gray', lw=1.5,
                    label=f'slope={coeffs[0]:.2f}')
            ax.legend(fontsize=8)
        ax.set_xlabel(r'$1/|\lambda_{\mathrm{dom}}|$')
        ax.set_ylabel(r'Convergence time $\tau$')
        ax.set_title(r'$\tau$ vs $1/|\lambda_{\mathrm{dom}}|$ (Linear = CSD)', fontweight='bold')

    fig.suptitle('Heterogeneity and Critical Slowing Down',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved: {save_path}")


if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    het_data, jc_values = heterogeneity_experiment()
    csd_results = critical_slowing_experiment()

    plot_experiments(het_data, jc_values, csd_results,
                     os.path.join(outdir, 'fig54_heterogeneity_csd.png'))

    # Also save to paper figures directory
    paper_fig_dir = '/home/gauss/Claude-Code-Lab/paper/figures'
    os.makedirs(paper_fig_dir, exist_ok=True)
    plot_experiments(het_data, jc_values, csd_results,
                     os.path.join(paper_fig_dir, 'fig6_heterogeneity.png'))

    # Summary
    print(f"\n{'='*70}")
    print("HETEROGENEITY PREDICTION TEST")
    print(f"{'='*70}")
    noise_levels = sorted(het_data.keys())
    for sigma in noise_levels:
        trials = het_data[sigma]
        widths = []
        for trial in trials:
            valid = [r for r in trial if r['has_bumps'] and not np.isnan(r['lambda_dom'])]
            if not valid:
                continue
            collapse = max(r['J_cross'] for r in valid)
            unstable = [r for r in valid if r['lambda_dom'] > 0]
            if unstable:
                onset = min(r['J_cross'] for r in unstable)
                widths.append(collapse - onset)
        if widths:
            print(f"  σ={sigma:.2f}: window = {np.mean(widths):.4f} ± {np.std(widths):.4f}")
        else:
            print(f"  σ={sigma:.2f}: no instability window found")
    print(f"{'='*70}")
