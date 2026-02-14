"""
==========================================================================
MULTIPLICATIVE NOISE CONTROL: ADDITIVE vs POISSON-LIKE NOISE COMPARISON
==========================================================================

Reviewer 3 critical requirement: "Re-run a slice of the phase diagram
using noise that scales with the square root of the instantaneous firing
rate (Poisson-like variance)."

Compares two noise models:
  Additive:       η = σ · ξ                        (constant variance)
  Multiplicative: η = σ · √(max(r, ε)) · ξ         (Poisson-like variance)

where ε = 0.01 prevents division issues at baseline firing rates.

Key diagnostic: do the isocontours of swap error rate tilt when noise
becomes state-dependent? If vertical → drive-is-secondary finding holds.
If tilted → the finding is noise-model-dependent.

Uses σ = 0.3 to match the original 128K-trial sweep (agent_*.json data).

Author: Claude Opus 4.6 (Paper v8 revision)
Date: February 2026
==========================================================================
"""

import numpy as np
import json
import time
import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib import ticker
from scipy.special import i0
from scipy.interpolate import RBFInterpolator

# ─── Model components (identical to coupled_ring_sweep.py) ───────────

def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    return r_max / (1.0 + np.exp(-beta * (h - h0)))

def tuning_curve(theta, preferred, kappa):
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))

def build_within_weights(preferred_angles, J_0, J_1):
    N = len(preferred_angles)
    dphi = preferred_angles[:, np.newaxis] - preferred_angles[np.newaxis, :]
    return (-J_0 + J_1 * np.cos(dphi)) / N

def decode(response, preferred, kappa):
    n_grid = 500
    theta_grid = np.linspace(-np.pi, np.pi, n_grid, endpoint=False)
    templates = np.array([[tuning_curve(t, phi, kappa) for phi in preferred]
                          for t in theta_grid])
    r_norm = response / (np.linalg.norm(response) + 1e-12)
    t_norms = templates / (np.linalg.norm(templates, axis=1, keepdims=True) + 1e-12)
    sims = t_norms @ r_norm
    return theta_grid[np.argmax(sims)]


# ─── Trial runner with noise model selection ─────────────────────────

NOISE_FLOOR = 0.01  # ε: prevents sqrt(0) in multiplicative model

def run_trial(theta1, theta2, preferred, kappa,
              W_within, J_cross, noise_sigma,
              dt, tau, n_steps, stim_steps, input_gain,
              r_max, beta, h0, noise_model='additive'):
    """
    Run a single coupled ring attractor trial.

    noise_model: 'additive' or 'multiplicative'
      additive:       η_i = σ · ξ_i
      multiplicative:  η_i = σ · √(max(r_i, ε)) · ξ_i
    """
    N = len(preferred)
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])
    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        if step < stim_steps:
            ext_A, ext_B = drive_A, drive_B
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        # Noise generation — the key difference
        if noise_model == 'multiplicative':
            noise_A = np.random.randn(N) * noise_sigma * np.sqrt(np.maximum(r_A, NOISE_FLOOR))
            noise_B = np.random.randn(N) * noise_sigma * np.sqrt(np.maximum(r_B, NOISE_FLOOR))
        else:
            noise_A = np.random.randn(N) * noise_sigma
            noise_B = np.random.randn(N) * noise_sigma

        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        f_A = sigmoid(h_A, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)

        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_B = np.maximum(0, r_B + dr_B)

        if np.any(np.isnan(r_A)) or np.any(np.isnan(r_B)):
            return None, None, "nan"
        if np.max(r_A) > 1e6 or np.max(r_B) > 1e6:
            return None, None, "explosion"

    if np.max(r_A) < 0.01 and np.max(r_B) < 0.01:
        return r_A, r_B, "collapse"

    return r_A, r_B, "ok"


# ─── Sweep at a single parameter point ──────────────────────────────

def sweep_point(J_cross, input_gain, W_within, preferred, kappa,
                n_trials, dt, tau, n_steps, stim_steps,
                r_max, beta, h0, noise_sigma, separation,
                noise_model='additive'):
    theta1, theta2 = 0.0, separation
    errors = []
    failures = {"nan": 0, "explosion": 0, "collapse": 0}

    for _ in range(n_trials):
        r_A, r_B, status = run_trial(
            theta1, theta2, preferred, kappa,
            W_within, J_cross, noise_sigma,
            dt, tau, n_steps, stim_steps, input_gain,
            r_max, beta, h0, noise_model
        )

        if status in ("nan", "explosion"):
            failures[status] += 1
            continue
        if status == "collapse":
            failures["collapse"] += 1
            continue

        combined = r_A + r_B
        decoded = decode(combined, preferred, kappa)
        error = decoded - theta1
        error = (error + np.pi) % (2 * np.pi) - np.pi
        errors.append(error)

    if len(errors) == 0:
        return {"J_cross": float(J_cross), "input_gain": float(input_gain),
                "n_valid": 0, "swap_rate": 0.0, "correct_rate": 0.0,
                "failures": failures, "status": "all_failed"}

    errors = np.array(errors)
    near_target = float(np.mean(np.abs(errors) < 0.3))
    near_nontarget = float(np.mean(np.abs(errors - separation) < 0.3))

    return {
        "J_cross": float(J_cross),
        "input_gain": float(input_gain),
        "n_valid": len(errors),
        "swap_rate": round(near_nontarget * 100, 2),
        "correct_rate": round(near_target * 100, 2),
        "mean_error": round(float(np.mean(errors)), 4),
        "std_error": round(float(np.std(errors)), 4),
        "failures": failures,
        "status": "ok"
    }


# ─── Main sweep ─────────────────────────────────────────────────────

def run_comparison_sweep():
    """
    Focused comparison: 2 noise models × 12 J_× values × 6 drive levels × 500 trials.
    Total: 72,000 trials (~30-60 min on CPU).
    """
    # Model parameters (matching original sweep exactly)
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    dt, tau = 1.0, 10.0
    n_steps = 500
    stim_steps = 100
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    J_0, J_1 = 1.0, 6.0
    W_within = build_within_weights(preferred, J_0, J_1)
    n_trials = 500

    # Focused grid: concentrate on the near-critical region where
    # drive-is-secondary was observed, plus some higher J_× for context
    j_values = np.array([0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50,
                         0.75, 1.0, 1.5, 2.0, 4.0])
    d_values = np.array([1.0, 2.0, 3.0, 4.0, 6.0, 8.0])

    noise_models = ['additive', 'multiplicative']
    all_results = {}

    total_points = len(j_values) * len(d_values) * len(noise_models)
    count = 0
    t0 = time.time()

    for model in noise_models:
        print(f"\n{'='*60}")
        print(f"  Noise model: {model.upper()}")
        print(f"{'='*60}")
        results = []
        for jc in j_values:
            for dv in d_values:
                count += 1
                result = sweep_point(
                    jc, dv, W_within, preferred, kappa,
                    n_trials, dt, tau, n_steps, stim_steps,
                    r_max, beta, h0, noise_sigma, separation,
                    noise_model=model
                )
                results.append(result)

                if count % 10 == 0 or count == total_points:
                    elapsed = time.time() - t0
                    rate = count / elapsed if elapsed > 0 else 0
                    eta = (total_points - count) / rate if rate > 0 else 0
                    print(f"  [{count}/{total_points}] J={jc:.2f} d={dv:.1f} "
                          f"swap={result['swap_rate']:5.1f}% "
                          f"({elapsed:.0f}s, ~{eta:.0f}s left)")

        all_results[model] = results

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s ({elapsed/60:.1f} min)")

    # Save results
    output = {
        "description": "Multiplicative noise control comparison (R3 requirement)",
        "noise_sigma": noise_sigma,
        "noise_floor_epsilon": NOISE_FLOOR,
        "n_trials_per_point": n_trials,
        "j_values": j_values.tolist(),
        "d_values": d_values.tolist(),
        "elapsed_seconds": round(elapsed, 1),
        "model_params": {
            "N": N, "kappa": kappa, "separation": separation,
            "dt": dt, "tau": tau, "n_steps": n_steps,
            "stim_steps": stim_steps, "r_max": r_max,
            "beta": beta, "h0": h0, "noise_sigma": noise_sigma,
            "J_0": J_0, "J_1": J_1
        },
        "additive": all_results['additive'],
        "multiplicative": all_results['multiplicative']
    }

    outdir = "/home/gauss/Claude-Code-Lab/corpus/code/results"
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, "multiplicative_noise_comparison.json")
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {outpath}")

    return output


# ─── Figure generation ───────────────────────────────────────────────

def make_colormap():
    """Same colormap as the main phase diagram (Fig 5)."""
    anchors = [
        (0.00, (0.07, 0.16, 0.28)),
        (0.04, (0.13, 0.32, 0.50)),
        (0.10, (0.50, 0.65, 0.72)),
        (0.14, (0.85, 0.84, 0.78)),
        (0.24, (0.92, 0.78, 0.40)),
        (0.38, (0.85, 0.48, 0.20)),
        (0.55, (0.70, 0.22, 0.15)),
        (1.00, (0.32, 0.07, 0.05)),
    ]
    positions = [a[0] for a in anchors]
    colors_rgb = [a[1] for a in anchors]
    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, (r, g, b) in zip(positions, colors_rgb):
        cdict['red'].append((pos, r, r))
        cdict['green'].append((pos, g, g))
        cdict['blue'].append((pos, b, b))
    return LinearSegmentedColormap('phase_swap', cdict, N=512)


def generate_figure(data, save_path):
    """
    Side-by-side heatmaps: additive (left) vs multiplicative (right).
    Key diagnostic: compare isocontour orientation.
    """
    BG_COLOR = '#faf8f5'
    plt.rcParams.update({
        'figure.facecolor': BG_COLOR,
        'axes.facecolor': BG_COLOR,
        'font.family': 'serif',
        'font.size': 11,
        'mathtext.fontset': 'cm',
        'axes.spines.top': True,
        'axes.spines.right': True,
        'axes.linewidth': 0.7,
        'axes.edgecolor': '#444444',
        'text.color': '#1a1a1a',
        'axes.labelcolor': '#1a1a1a',
        'xtick.color': '#444444',
        'ytick.color': '#444444',
    })

    cmap = make_colormap()
    vmax = 52

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)

    titles = ['(A) Additive noise: $\\eta = \\sigma \\xi$',
              '(B) Multiplicative noise: $\\eta = \\sigma \\sqrt{\\max(r, \\varepsilon)}\\, \\xi$']
    keys = ['additive', 'multiplicative']

    contour_sets = []

    for ax_idx, (ax, key, title) in enumerate(zip(axes, keys, titles)):
        results = data[key]
        j_vals = np.array([r['J_cross'] for r in results if r['status'] == 'ok'])
        d_vals = np.array([r['input_gain'] for r in results if r['status'] == 'ok'])
        swap_vals = np.array([r['swap_rate'] for r in results if r['status'] == 'ok'])

        if len(j_vals) == 0:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes, ha='center')
            continue

        # RBF interpolation in log-J space
        log_j = np.log10(j_vals)
        log_j_min, log_j_max = np.log10(0.12), np.log10(5.0)
        d_min, d_max = 0.5, 8.5
        j_norm = (log_j - log_j_min) / (log_j_max - log_j_min)
        d_norm = (d_vals - d_min) / (d_max - d_min)

        n_grid = 200
        log_j_grid = np.linspace(log_j_min, log_j_max, n_grid)
        d_grid = np.linspace(d_min, d_max, n_grid)
        LOG_J_mesh, D_mesh = np.meshgrid(log_j_grid, d_grid)
        J_mesh = 10**LOG_J_mesh

        j_mesh_norm = (LOG_J_mesh - log_j_min) / (log_j_max - log_j_min)
        d_mesh_norm = (D_mesh - d_min) / (d_max - d_min)

        coords = np.column_stack([j_norm, d_norm])
        query = np.column_stack([j_mesh_norm.ravel(), d_mesh_norm.ravel()])
        rbf = RBFInterpolator(coords, swap_vals, kernel='thin_plate_spline',
                              smoothing=0.8)
        swap_grid = rbf(query).reshape(J_mesh.shape)
        swap_grid = np.clip(swap_grid, 0, 55)

        # Heatmap
        im = ax.pcolormesh(J_mesh, D_mesh, swap_grid,
                           cmap=cmap, norm=Normalize(vmin=0, vmax=vmax),
                           shading='gouraud', rasterized=True)
        ax.set_xscale('log')

        # Contour lines
        contour_levels = [5, 10, 20, 30, 40]
        cs = ax.contour(J_mesh, D_mesh, swap_grid,
                        levels=contour_levels,
                        colors='white',
                        linewidths=[1.6, 0.6, 0.6, 0.6, 0.6],
                        linestyles=['solid', 'dashed', 'dashed', 'dashed', 'dashed'],
                        alpha=0.7)
        fmt_dict = {5: '5%', 10: '10%', 20: '20%', 30: '30%', 40: '40%'}
        ax.clabel(cs, levels=[5, 20, 40], fontsize=7.5, fmt=fmt_dict,
                  colors='white', inline=True, inline_spacing=6)
        contour_sets.append(cs)

        # Data points
        ax.scatter(j_vals, d_vals, s=12, c='white', alpha=0.35,
                   edgecolors='none', zorder=5, marker='o')

        # Critical lines
        ax.axvline(x=0.3485, color='#00e5ff', ls='--', lw=1.2, alpha=0.8, zorder=10)
        ax.axvline(x=0.358, color='#76ff03', ls=':', lw=1.2, alpha=0.7, zorder=10)

        ax.set_title(title, fontsize=11, fontweight='bold', pad=8)
        ax.set_xlabel(r'Cross-inhibition strength  $J_\times$', fontsize=11)
        ax.set_xticks([0.2, 0.3, 0.5, 1, 2, 4])
        ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())
        ax.get_xaxis().set_minor_formatter(ticker.NullFormatter())
        ax.xaxis.set_minor_locator(ticker.NullLocator())
        ax.set_xlim(0.12, 5.0)
        ax.set_ylim(0.5, 8.5)

    axes[0].set_ylabel(r'Encoding cue gain $c$', fontsize=11)

    # Shared colorbar
    cbar = fig.colorbar(im, ax=axes, shrink=0.85, aspect=28, pad=0.02)
    cbar.set_label('Swap error rate (%)', fontsize=10, labelpad=10)
    cbar.ax.tick_params(labelsize=9)
    cbar.set_ticks([0, 5, 10, 20, 30, 40, 50])

    # Legend
    legend_elements = [
        Line2D([0], [0], color='#00e5ff', ls='--', lw=1.2,
               label=r'$J_\times^{\,*} \approx 0.349$'),
        Line2D([0], [0], color='#76ff03', ls=':', lw=1.2,
               label=r'$J_\times^{\,\mathrm{exist}} \approx 0.358$'),
    ]
    axes[1].legend(handles=legend_elements, loc='lower right', fontsize=7.5,
                   framealpha=0.9, facecolor=BG_COLOR, edgecolor='#888888')

    fig.suptitle('Noise model comparison: additive vs. multiplicative (Poisson-like)',
                 fontsize=12.5, fontweight='bold', y=1.02)

    subtitle = (f'$N\\!=\\!48$  |  {data["n_trials_per_point"]} trials/point  |  '
                f'$\\sigma\\!=\\!{data["noise_sigma"]}$  |  '
                f'$\\varepsilon\\!=\\!{data["noise_floor_epsilon"]}$')
    fig.text(0.5, 0.99, subtitle, fontsize=8, color='#777777',
             ha='center', va='bottom')

    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print(f"\nFigure saved: {save_path}")

    # ── Quantitative isocontour analysis ─────────────────────────────
    print("\n" + "=" * 60)
    print("ISOCONTOUR TILT ANALYSIS")
    print("=" * 60)

    for model_key in keys:
        results = data[model_key]
        ok_results = [r for r in results if r['status'] == 'ok']

        # Compare swap rates at fixed J_× but different drive levels
        print(f"\n  {model_key.upper()} noise:")
        j_unique = sorted(set(r['J_cross'] for r in ok_results))
        for jc in j_unique:
            at_j = [r for r in ok_results if r['J_cross'] == jc]
            at_j.sort(key=lambda r: r['input_gain'])
            swaps = [r['swap_rate'] for r in at_j]
            drives = [r['input_gain'] for r in at_j]
            if len(swaps) >= 2:
                spread = max(swaps) - min(swaps)
                print(f"    J={jc:5.2f}: swap range [{min(swaps):5.1f}%, {max(swaps):5.1f}%] "
                      f"spread={spread:5.1f}%  (drives {drives[0]:.0f}–{drives[-1]:.0f})")

    # Summary: compare drive-sensitivity between models
    print(f"\n  DRIVE SENSITIVITY COMPARISON (near-critical J=0.25–0.50):")
    for model_key in keys:
        results = data[model_key]
        near_crit = [r for r in results
                     if r['status'] == 'ok' and 0.25 <= r['J_cross'] <= 0.50]
        if near_crit:
            by_drive = {}
            for r in near_crit:
                d = r['input_gain']
                by_drive.setdefault(d, []).append(r['swap_rate'])
            mean_by_drive = {d: np.mean(v) for d, v in sorted(by_drive.items())}
            drives = sorted(mean_by_drive.keys())
            if len(drives) >= 2:
                low_drive_mean = mean_by_drive[drives[0]]
                high_drive_mean = mean_by_drive[drives[-1]]
                delta = low_drive_mean - high_drive_mean
                print(f"    {model_key:15s}: low-drive mean={low_drive_mean:5.1f}%, "
                      f"high-drive mean={high_drive_mean:5.1f}%, "
                      f"Δ={delta:+5.1f}%")

    print("=" * 60)


if __name__ == '__main__':
    print("=" * 70)
    print("MULTIPLICATIVE NOISE CONTROL SIMULATION")
    print("R3 critical requirement for paper acceptance")
    print("=" * 70)

    data = run_comparison_sweep()

    fig_path = "/home/gauss/Claude-Code-Lab/paper/figures/fig11_noise_comparison.png"
    generate_figure(data, fig_path)

    # Also save to corpus/code/figures
    fig_path2 = "/home/gauss/Claude-Code-Lab/corpus/code/figures/fig11_noise_comparison.png"
    generate_figure(data, fig_path2)

    print("\nDone. Check isocontour tilt analysis above.")
    print("If isocontours remain vertical → structural argument confirmed.")
    print("If tilted → drive-is-secondary finding is noise-model-dependent.")
