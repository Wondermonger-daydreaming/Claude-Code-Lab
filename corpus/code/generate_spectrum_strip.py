"""
Generate Figure 9: Spectrum Strip
==================================

Top ~10 eigenvalues of the 96D coupled ring attractor Jacobian
as a function of J_cross, with Goldstone modes pinned at zero.

For the paper: "Spectral Separatrix" (Neural Computation submission).
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_separatrix_goldstone import (
    N, J_0, J_1, KAPPA, INPUT_GAIN, R_MAX, BETA, H0, DT, TAU,
    build_within_weights, find_coexistence_fp, jacobian_analytical,
    classify_eigenvalues,
)

# ── Publication style ────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#333333',
    'text.color': '#1a1a1a',
    'axes.labelcolor': '#1a1a1a',
    'xtick.color': '#333333',
    'ytick.color': '#333333',
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'mathtext.fontset': 'dejavuserif',
})


def compute_spectrum_strip():
    """
    Sweep J_cross from 0 to 0.36, compute the full 96D Jacobian
    eigenspectrum at the coexistence fixed point, and return the
    top ~10 eigenvalues (sorted by real part, most positive first)
    plus the Goldstone modes.
    """
    W, preferred = build_within_weights(N, J_0, J_1)

    # ~30 J_cross values, denser near the critical region
    jc_values = np.sort(np.unique(np.concatenate([
        np.linspace(0.00, 0.25, 8),
        np.linspace(0.25, 0.36, 22),
    ])))

    results = []
    r_A_prev, r_B_prev = None, None

    for jc in jc_values:
        if r_A_prev is not None and jc > 0:
            r_A, r_B, res = find_coexistence_fp(
                W, preferred, jc, r_A_prev, r_B_prev)
        else:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

        if res > 1e-4 or np.max(r_A) < 0.3 or np.max(r_B) < 0.3:
            print(f"  J_cross={jc:.4f}: FAILED (res={res:.2e})")
            continue

        # Jacobian at the coexistence fixed point
        cue_0 = np.zeros(N)
        x = np.concatenate([r_A, r_B])
        J = jacobian_analytical(x, W, cue_0, jc)
        evals, evecs = np.linalg.eig(J)

        # Sort by descending real part
        idx = np.argsort(-evals.real)
        evals = evals[idx]
        evecs = evecs[:, idx]

        classified = classify_eigenvalues(evals, evecs, preferred)
        goldstone = [c for c in classified if c['is_goldstone']]
        genuine = [c for c in classified if not c['is_goldstone']]
        genuine.sort(key=lambda c: -c['eigenvalue'])

        # Extract top 10 genuine eigenvalues
        top_genuine = [g['eigenvalue'] for g in genuine[:10]]
        n_gold = len(goldstone)
        gold_evals = [g['eigenvalue'] for g in goldstone]

        results.append({
            'J_cross': jc,
            'top_genuine': top_genuine,
            'n_goldstone': n_gold,
            'goldstone_evals': gold_evals,
            'lambda_dom': top_genuine[0] if top_genuine else np.nan,
        })

        status = "UNSTABLE" if top_genuine[0] > 1e-4 else "stable"
        print(f"  J_cross={jc:.4f}: lambda_dom={top_genuine[0]:+.5f}  "
              f"gold={n_gold}  [{status}]")

        r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

    return results


def plot_spectrum_strip(results, save_path):
    """
    Publication figure: top eigenvalues vs J_cross.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    jc_vals = np.array([r['J_cross'] for r in results])

    # ── Background eigenvalues (ranks 3-10): thin gray lines ─────
    # Determine the max number of top genuine eigenvalues available
    max_top = min(10, min(len(r['top_genuine']) for r in results))

    # Plot ranks 3..10 first (back to front, dimmer for higher ranks)
    for k in range(max_top - 1, 1, -1):
        vals = np.array([r['top_genuine'][k] for r in results])
        alpha = 0.15 + 0.05 * (max_top - k)  # dimmer for deeper eigenvalues
        alpha = min(alpha, 0.5)
        ax.plot(jc_vals, vals, '-', color='#999999', lw=0.6,
                alpha=alpha, zorder=1)

    # Label the background band
    # Use rank 2 (the first "other" eigenvalue) for positioning
    vals_r2 = np.array([r['top_genuine'][2] for r in results])
    vals_r9 = np.array([r['top_genuine'][min(9, max_top - 1)] for r in results])
    mid_idx = len(jc_vals) // 4
    ax.annotate(r'$\lambda_3 \ldots \lambda_{10}$',
                xy=(jc_vals[mid_idx], vals_r2[mid_idx]),
                xytext=(jc_vals[mid_idx] - 0.04, vals_r2[mid_idx] + 0.04),
                fontsize=8.5, color='#777777', fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color='#999999',
                                lw=0.7, connectionstyle='arc3,rad=0.2'))

    # ── Second genuine eigenvalue (rank 2): medium gray ──────────
    vals_2 = np.array([r['top_genuine'][1] for r in results])
    ax.plot(jc_vals, vals_2, '-', color='#777777', lw=1.2,
            alpha=0.6, zorder=2, label=r'$\lambda_2$')

    # ── Dominant genuine eigenvalue: thick, colored by sign ───────
    lam_dom = np.array([r['lambda_dom'] for r in results])

    # Split into stable (blue) and unstable (red) segments
    # Find the crossing index
    crossing_idx = None
    for i in range(len(lam_dom) - 1):
        if lam_dom[i] < 0 and lam_dom[i + 1] > 0:
            crossing_idx = i
            break

    if crossing_idx is not None:
        # Interpolate the exact crossing point
        jc1, jc2 = jc_vals[crossing_idx], jc_vals[crossing_idx + 1]
        l1, l2 = lam_dom[crossing_idx], lam_dom[crossing_idx + 1]
        jc_cross = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)

        # Stable segment (blue)
        stable_mask = np.arange(len(jc_vals)) <= crossing_idx
        ax.plot(jc_vals[stable_mask], lam_dom[stable_mask], '-',
                color='#2d5a7b', lw=2.5, zorder=5)

        # Unstable segment (red)
        unstable_mask = np.arange(len(jc_vals)) >= crossing_idx
        ax.plot(jc_vals[unstable_mask], lam_dom[unstable_mask], '-',
                color='#c0392b', lw=2.5, zorder=5)

        # Connect through the crossing with both colors meeting
        ax.plot([jc_vals[crossing_idx], jc_cross],
                [lam_dom[crossing_idx], 0], '-', color='#2d5a7b', lw=2.5,
                zorder=5)
        ax.plot([jc_cross, jc_vals[crossing_idx + 1]],
                [0, lam_dom[crossing_idx + 1]], '-', color='#c0392b', lw=2.5,
                zorder=5)
    else:
        # All stable or all unstable
        color = '#c0392b' if lam_dom[-1] > 0 else '#2d5a7b'
        ax.plot(jc_vals, lam_dom, '-', color=color, lw=2.5, zorder=5)

    # Label lambda_dom
    label_idx = len(jc_vals) * 2 // 3
    ax.annotate(r'$\lambda_{\mathrm{dom}}$',
                xy=(jc_vals[label_idx], lam_dom[label_idx]),
                xytext=(jc_vals[label_idx] + 0.012, lam_dom[label_idx] + 0.05),
                fontsize=11, fontweight='bold', color='#c0392b',
                arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.2))

    # ── Goldstone modes: bold gold line at ~0 ────────────────────
    # They are at ~1e-10, effectively zero. Draw as a bold line at 0.
    ax.plot(jc_vals, np.zeros_like(jc_vals), '-', color='#d4a017',
            lw=3.0, zorder=4, solid_capstyle='round')
    ax.annotate('Goldstone ($\\times 2$)',
                xy=(jc_vals[3], 0),
                xytext=(jc_vals[3] - 0.01, 0.06),
                fontsize=9, color='#b8860b', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#b8860b', lw=0.9))

    # ── Reference lines ──────────────────────────────────────────
    # Horizontal: lambda = 0
    ax.axhline(y=0, color='#aaaaaa', ls='--', lw=0.7, zorder=0)

    # Vertical: J_cross* (pitchfork)
    J_CROSS_STAR = 0.349
    ax.axvline(x=J_CROSS_STAR, color='#555555', ls='--', lw=0.9,
               zorder=0, alpha=0.7)
    ax.text(J_CROSS_STAR + 0.002, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else -0.55,
            r'$J_\times^*$', fontsize=10, color='#555555', va='bottom',
            fontweight='bold')

    # Vertical: J_cross^exist
    J_CROSS_EXIST = 0.358
    ax.axvline(x=J_CROSS_EXIST, color='#555555', ls=':', lw=0.9,
               zorder=0, alpha=0.7)
    ax.text(J_CROSS_EXIST + 0.002, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else -0.55,
            r'$J_\times^{\mathrm{exist}}$', fontsize=10, color='#555555',
            va='bottom')

    # ── Axes ─────────────────────────────────────────────────────
    ax.set_xlabel(r'Cross-inhibition strength $J_\times$', fontsize=11)
    ax.set_ylabel(r'$\mathrm{Re}(\lambda)$', fontsize=11)
    ax.set_xlim(-0.01, 0.37)

    # Let the y-axis be set by data, then adjust the vertical reference labels
    ax.figure.canvas.draw()

    # Update the J_cross* and J_cross^exist label positions after axis limits are set
    ymin, ymax = ax.get_ylim()
    # Remove old text and re-place
    for txt in ax.texts:
        if txt.get_text() in [r'$J_\times^*$', r'$J_\times^{\mathrm{exist}}$']:
            txt.set_position((txt.get_position()[0], ymin + 0.02 * (ymax - ymin)))

    ax.tick_params(axis='both', which='major', labelsize=9)

    plt.tight_layout()

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"\nSaved: {save_path}")


if __name__ == '__main__':
    print("=" * 60)
    print("SPECTRUM STRIP: Top eigenvalues vs J_cross")
    print("=" * 60)

    results = compute_spectrum_strip()

    save_path = '/home/gauss/Claude-Code-Lab/paper/figures/fig9_spectrum_strip.png'
    plot_spectrum_strip(results, save_path)

    print("=" * 60)
    print("Done.")
    print("=" * 60)
