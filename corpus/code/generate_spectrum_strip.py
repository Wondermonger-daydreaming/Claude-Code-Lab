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

    Design: clean, minimal, Neural Computation style.
    Y-axis zoomed to show the interesting range (-0.65 to +0.08).
    Goldstone line is a thin but distinct gold band.
    lambda_dom transitions from dark blue (stable) to red (unstable).
    Background eigenvalues fade progressively.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    jc_vals = np.array([r['J_cross'] for r in results])
    max_top = min(10, min(len(r['top_genuine']) for r in results))

    # ── Y-axis limits (set early so annotations can use them) ────
    YMIN, YMAX = -0.62, 0.06

    # ── Background eigenvalues (ranks 3-10): thin gray lines ─────
    for k in range(max_top - 1, 1, -1):
        vals = np.array([r['top_genuine'][k] for r in results])
        # Clip to visible range for cleanliness
        vals_clipped = np.clip(vals, YMIN, YMAX)
        alpha = 0.50 - 0.04 * k  # dimmer for deeper eigenvalues
        alpha = max(alpha, 0.12)
        lw = 0.9 if k <= 4 else 0.5
        ax.plot(jc_vals, vals_clipped, '-', color='#b0b0b0', lw=lw,
                alpha=alpha, zorder=1)

    # Label the background band
    # Most background eigenvalues are below YMIN, so label near the
    # bottom of the visible area with a downward indicator
    vals_r3 = np.array([r['top_genuine'][2] for r in results])
    # Place near right side where lambda_2 diverges from lambda_dom
    ax.annotate(r'$\lambda_3, \ldots, \lambda_{10}$',
                xy=(0.32, YMIN + 0.01),
                xytext=(0.22, YMIN + 0.06),
                fontsize=8, color='#888888', fontstyle='italic',
                arrowprops=dict(arrowstyle='->', color='#aaaaaa', lw=0.7))

    # ── Second genuine eigenvalue (rank 2): medium weight ────────
    vals_2 = np.array([r['top_genuine'][1] for r in results])
    ax.plot(jc_vals, vals_2, '-', color='#888888', lw=1.3,
            alpha=0.55, zorder=2)
    # Label lambda_2
    lab2_idx = len(jc_vals) // 2
    ax.text(jc_vals[lab2_idx] + 0.005, vals_2[lab2_idx] + 0.012,
            r'$\lambda_2$', fontsize=8.5, color='#777777')

    # ── Dominant genuine eigenvalue: thick, blue→red at crossing ──
    lam_dom = np.array([r['lambda_dom'] for r in results])

    crossing_idx = None
    for i in range(len(lam_dom) - 1):
        if lam_dom[i] < 0 and lam_dom[i + 1] > 0:
            crossing_idx = i
            break

    COL_STABLE = '#2d5a7b'
    COL_UNSTABLE = '#c0392b'

    if crossing_idx is not None:
        jc1, jc2 = jc_vals[crossing_idx], jc_vals[crossing_idx + 1]
        l1, l2 = lam_dom[crossing_idx], lam_dom[crossing_idx + 1]
        jc_cross = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)

        # Stable segment (blue), include the crossing point
        seg_stable_j = np.append(jc_vals[:crossing_idx + 1], jc_cross)
        seg_stable_l = np.append(lam_dom[:crossing_idx + 1], 0.0)
        ax.plot(seg_stable_j, seg_stable_l, '-',
                color=COL_STABLE, lw=2.5, zorder=5, solid_capstyle='round')

        # Unstable segment (red), from crossing point onward
        seg_unstable_j = np.insert(jc_vals[crossing_idx + 1:], 0, jc_cross)
        seg_unstable_l = np.insert(lam_dom[crossing_idx + 1:], 0, 0.0)
        ax.plot(seg_unstable_j, seg_unstable_l, '-',
                color=COL_UNSTABLE, lw=2.5, zorder=5, solid_capstyle='round')

        # Small filled circle at the crossing
        ax.plot(jc_cross, 0, 'o', color=COL_UNSTABLE, ms=4, zorder=6)
    else:
        color = COL_UNSTABLE if lam_dom[-1] > 0 else COL_STABLE
        ax.plot(jc_vals, lam_dom, '-', color=color, lw=2.5, zorder=5)

    # Label lambda_dom: place it in the stable region, left of center
    label_idx = len(jc_vals) // 3
    ax.annotate(r'$\lambda_{\mathrm{dom}}$',
                xy=(jc_vals[label_idx], lam_dom[label_idx]),
                xytext=(jc_vals[label_idx] - 0.035, lam_dom[label_idx] + 0.06),
                fontsize=11, fontweight='bold', color=COL_STABLE,
                arrowprops=dict(arrowstyle='->', color=COL_STABLE, lw=1.0,
                                connectionstyle='arc3,rad=-0.15'))

    # ── Goldstone modes: gold line at 0, distinct but not dominating ──
    ax.plot(jc_vals, np.zeros_like(jc_vals), '-', color='#d4a017',
            lw=1.8, zorder=4, solid_capstyle='round')
    # Label at the left end, slightly above
    ax.text(0.005, 0.012, r'Goldstone ($\times 2$)',
            fontsize=8, color='#b8860b', fontweight='bold', va='bottom')

    # ── Reference lines ──────────────────────────────────────────
    ax.axhline(y=0, color='#cccccc', ls='-', lw=0.5, zorder=0)

    # Vertical: J_cross* (pitchfork)
    J_CROSS_STAR = 0.349
    ax.axvline(x=J_CROSS_STAR, color='#666666', ls='--', lw=0.8,
               zorder=0, alpha=0.6)
    ax.text(J_CROSS_STAR - 0.003, YMIN + 0.02, r'$J_\times^*$',
            fontsize=9.5, color='#555555', ha='right', va='bottom',
            fontweight='bold')

    # Vertical: J_cross^exist
    J_CROSS_EXIST = 0.358
    ax.axvline(x=J_CROSS_EXIST, color='#666666', ls=':', lw=0.8,
               zorder=0, alpha=0.6)
    ax.text(J_CROSS_EXIST + 0.003, YMIN + 0.02, r'$J_\times^{\mathrm{exist}}$',
            fontsize=9, color='#555555', ha='left', va='bottom')

    # ── Axes ─────────────────────────────────────────────────────
    ax.set_xlabel(r'Cross-inhibition strength $J_\times$', fontsize=11)
    ax.set_ylabel(r'$\mathrm{Re}(\lambda)$', fontsize=11)
    ax.set_xlim(-0.01, 0.37)
    ax.set_ylim(YMIN, YMAX)
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
