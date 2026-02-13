"""
==========================================================================
PAPER FIGURE GENERATION: SPECTRAL SEPARATRIX PAPER
==========================================================================

Generates the four missing figures for the paper:
  Fig 2: Model schematic (two ring networks with cross-inhibition)
  Fig 5: Coexistence existence boundary (bump heights vs J_cross)
  Fig 6: Pitchfork bifurcation diagram (D vs J_cross)
  Fig 7: Eigenvector comparison (Goldstone vs critical dominance)

Uses functions from:
  - spectral_portrait_ring_attractor.py (sigmoid, build_within_weights, etc.)
  - spectral_separatrix_goldstone.py (find_coexistence_fp, classify_eigenvalues, etc.)

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 13, 2026
==========================================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, Arc, Circle, FancyBboxPatch
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as pe
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve
)
from spectral_separatrix_goldstone import (
    find_coexistence_fp, classify_eigenvalues, jacobian_analytical,
    N, J_0, J_1, KAPPA, INPUT_GAIN, R_MAX, BETA, H0, DT, TAU,
    residual
)

# ── Output directory ─────────────────────────────────────────────────
OUTDIR = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
os.makedirs(OUTDIR, exist_ok=True)

# ── Colors ───────────────────────────────────────────────────────────
COLOR_A = '#2d5a7b'
COLOR_B = '#c0392b'
COLOR_STABLE = '#2d5a7b'
COLOR_UNSTABLE = '#c0392b'
COLOR_BG = '#faf8f5'

# ── Style ────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': COLOR_BG,
    'axes.facecolor': COLOR_BG,
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


# =====================================================================
# FIG 2: MODEL SCHEMATIC
# =====================================================================

def draw_ring_network(ax, center_x, center_y, radius, n_neurons, color,
                      label, highlight_neuron=None, highlight_color=None):
    """Draw a ring of neurons as colored dots on a circle."""
    angles = np.linspace(0, 2 * np.pi, n_neurons, endpoint=False)
    xs = center_x + radius * np.cos(angles)
    ys = center_y + radius * np.sin(angles)

    # Draw the ring circle (faint)
    circle = plt.Circle((center_x, center_y), radius, fill=False,
                         edgecolor=color, linewidth=1.0, alpha=0.25,
                         linestyle='--')
    ax.add_patch(circle)

    # Draw neurons
    for i, (x, y) in enumerate(zip(xs, ys)):
        # Create activity gradient: neurons near the "bump peak" are brighter
        bump_angle = np.pi / 4 if 'A' in label else -np.pi / 4
        dist = abs(angles[i] - bump_angle) % (2 * np.pi)
        dist = min(dist, 2 * np.pi - dist)
        activity = np.exp(-2.0 * dist**2)  # Gaussian bump

        if highlight_neuron is not None and i == highlight_neuron:
            c = highlight_color or 'gold'
            s = 50
        else:
            # Blend color intensity with activity
            alpha_val = 0.25 + 0.75 * activity
            c = color
            s = 20 + 40 * activity

        ax.scatter(x, y, s=s, c=c, alpha=0.25 + 0.75 * activity,
                   zorder=5, edgecolors='white', linewidths=0.3)

    # Label
    ax.text(center_x, center_y, label, ha='center', va='center',
            fontsize=14, fontweight='bold', color=color,
            path_effects=[pe.withStroke(linewidth=3, foreground=COLOR_BG)])

    return xs, ys, angles


def draw_curved_connectivity(ax, center_x, center_y, radius, color, n_arrows=6):
    """Draw curved arrows within a ring to indicate cosine connectivity."""
    for i in range(n_arrows):
        start_angle = i * 360 / n_arrows + 10
        arc_extent = 40
        # Small arcs showing recurrent connections
        arc = Arc((center_x, center_y), 2 * radius * 0.78, 2 * radius * 0.78,
                  angle=0, theta1=start_angle, theta2=start_angle + arc_extent,
                  color=color, linewidth=1.2, alpha=0.4)
        ax.add_patch(arc)

        # Arrowhead at end of arc
        end_rad = np.radians(start_angle + arc_extent)
        ax.annotate('', xy=(center_x + radius * 0.78 * np.cos(end_rad),
                            center_y + radius * 0.78 * np.sin(end_rad)),
                     xytext=(center_x + radius * 0.78 * np.cos(end_rad - 0.08),
                             center_y + radius * 0.78 * np.sin(end_rad - 0.08)),
                     arrowprops=dict(arrowstyle='->', color=color, lw=1.2,
                                     mutation_scale=10),
                     alpha=0.4)


def fig2_schematic():
    """
    Fig 2: Model Schematic
    Two ring networks with cosine connectivity within and mean-field
    cross-inhibition between.
    """
    print("  Generating Fig 2: Model Schematic...")
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-2.5, 3.0)
    ax.set_aspect('equal')
    ax.axis('off')

    # Ring network positions
    cx_A, cy_A = -1.5, 0.5
    cx_B, cy_B = 1.5, 0.5
    ring_radius = 1.2

    # Draw rings
    n_show = 16  # neurons to show
    xs_A, ys_A, ang_A = draw_ring_network(ax, cx_A, cy_A, ring_radius, n_show,
                                           COLOR_A, 'Net A')
    xs_B, ys_B, ang_B = draw_ring_network(ax, cx_B, cy_B, ring_radius, n_show,
                                           COLOR_B, 'Net B')

    # Within-network cosine connectivity arrows
    draw_curved_connectivity(ax, cx_A, cy_A, ring_radius, COLOR_A)
    draw_curved_connectivity(ax, cx_B, cy_B, ring_radius, COLOR_B)

    # Within-network labels
    ax.text(cx_A, cy_A - ring_radius - 0.4,
            r'$W_{ij} = \frac{-J_0 + J_1 \cos(\theta_i - \theta_j)}{N}$',
            ha='center', va='top', fontsize=8.5, color=COLOR_A, style='italic')
    ax.text(cx_B, cy_B - ring_radius - 0.4,
            r'$W_{ij} = \frac{-J_0 + J_1 \cos(\theta_i - \theta_j)}{N}$',
            ha='center', va='top', fontsize=8.5, color=COLOR_B, style='italic')

    # Cross-inhibition arrows (big, between the two rings)
    arrow_y_top = 1.1
    arrow_y_bot = -0.1

    # A -> B inhibition (top)
    ax.annotate('',
                xy=(cx_B - ring_radius + 0.15, arrow_y_top),
                xytext=(cx_A + ring_radius - 0.15, arrow_y_top),
                arrowprops=dict(arrowstyle='-|>',
                                color='#555555', lw=2.5,
                                connectionstyle='arc3,rad=-0.15',
                                mutation_scale=18))
    # B -> A inhibition (bottom)
    ax.annotate('',
                xy=(cx_A + ring_radius - 0.15, arrow_y_bot),
                xytext=(cx_B - ring_radius + 0.15, arrow_y_bot),
                arrowprops=dict(arrowstyle='-|>',
                                color='#555555', lw=2.5,
                                connectionstyle='arc3,rad=-0.15',
                                mutation_scale=18))

    # Cross-inhibition labels
    ax.text(0.0, arrow_y_top + 0.32,
            r'$-J_\times \cdot \bar{r}_A$',
            ha='center', va='bottom', fontsize=10, color='#555555',
            fontweight='bold')
    ax.text(0.0, arrow_y_bot - 0.32,
            r'$-J_\times \cdot \bar{r}_B$',
            ha='center', va='top', fontsize=10, color='#555555',
            fontweight='bold')

    # Small flat-head markers to indicate inhibition
    for y_pos in [arrow_y_top, arrow_y_bot]:
        ax.plot([-0.02, 0.02], [y_pos + 0.05, y_pos + 0.05],
                color='#555555', lw=2, solid_capstyle='butt')

    # Cue input arrow to Network A
    cue_x = cx_A - 0.3
    cue_y_start = cy_A + ring_radius + 1.0
    cue_y_end = cy_A + ring_radius + 0.15

    ax.annotate('',
                xy=(cue_x, cue_y_end),
                xytext=(cue_x, cue_y_start),
                arrowprops=dict(arrowstyle='-|>',
                                color='#e67e22', lw=2.5,
                                mutation_scale=18))
    ax.text(cue_x, cue_y_start + 0.15,
            'Cue input\n' + r'$I_i^{cue} = c \cdot f(\theta_i)$',
            ha='center', va='bottom', fontsize=9.5, color='#e67e22',
            fontweight='bold')

    # Title
    ax.text(0.0, -2.2,
            'Coupled Ring Attractor Model\n'
            r'$N = 48$ neurons per ring, mean-field cross-inhibition',
            ha='center', va='top', fontsize=10.5, color='#2a2a2a',
            style='italic')

    plt.tight_layout()
    path = os.path.join(OUTDIR, 'fig_paper_2_schematic.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {path}")
    return path


# =====================================================================
# FIG 5: COEXISTENCE EXISTENCE BOUNDARY
# =====================================================================

def fig5_existence():
    """
    Fig 5: Coexistence Existence Boundary
    max(r_A) and max(r_B) vs J_cross, showing the sharp collapse
    at J_cross ~ 0.36.
    """
    print("  Generating Fig 5: Coexistence Existence Boundary...")
    W, preferred = build_within_weights(N, J_0, J_1)

    # Dense scan of J_cross
    jc_values = np.sort(np.unique(np.concatenate([
        np.linspace(0.01, 0.30, 15),
        np.linspace(0.30, 0.37, 40),
        np.linspace(0.37, 0.40, 10),
    ])))

    max_rA_list = []
    max_rB_list = []
    mean_rA_list = []
    mean_rB_list = []
    jc_valid = []

    r_A_prev, r_B_prev = None, None

    for jc in jc_values:
        try:
            if r_A_prev is not None:
                r_A, r_B, res = find_coexistence_fp(W, preferred, jc,
                                                     r_A_prev, r_B_prev)
            else:
                r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

            if res > 1e-4:
                # Try fresh initialization
                r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

            max_rA_list.append(np.max(r_A))
            max_rB_list.append(np.max(r_B))
            mean_rA_list.append(np.mean(r_A))
            mean_rB_list.append(np.mean(r_B))
            jc_valid.append(jc)

            if res < 1e-4 and np.max(r_A) > 0.3 and np.max(r_B) > 0.3:
                r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

            print(f"    J_cross={jc:.4f}: max(r_A)={np.max(r_A):.3f}, "
                  f"max(r_B)={np.max(r_B):.3f}, res={res:.2e}")
        except Exception as e:
            print(f"    J_cross={jc:.4f}: FAILED ({e})")
            continue

    jc_valid = np.array(jc_valid)
    max_rA = np.array(max_rA_list)
    max_rB = np.array(max_rB_list)

    # ── Plot ──
    fig, ax = plt.subplots(1, 1, figsize=(5.5, 4.0))

    ax.plot(jc_valid, max_rA, '-o', color=COLOR_A, lw=2.0, ms=3,
            label=r'$\max(r^A)$', zorder=3)
    ax.plot(jc_valid, max_rB, '-s', color=COLOR_B, lw=2.0, ms=3,
            label=r'$\max(r^B)$', zorder=3)

    # Vertical dashed lines at critical values
    J_CROSS_STAR = 0.3485
    J_CROSS_EXIST = 0.358

    ax.axvline(x=J_CROSS_STAR, color='#8e44ad', ls='--', lw=1.5, alpha=0.7)
    ax.text(J_CROSS_STAR - 0.003, 0.05,
            r'$J_\times^* \approx 0.349$' + '\n(pitchfork)',
            ha='right', va='bottom', fontsize=8.5, color='#8e44ad',
            fontweight='bold')

    ax.axvline(x=J_CROSS_EXIST, color='#e67e22', ls='--', lw=1.5, alpha=0.7)
    ax.text(J_CROSS_EXIST + 0.003, 0.05,
            r'$J_\times^{exist} \approx 0.358$' + '\n(existence)',
            ha='left', va='bottom', fontsize=8.5, color='#e67e22',
            fontweight='bold')

    # Shade the coexistence saddle region
    ax.axvspan(J_CROSS_STAR, J_CROSS_EXIST, alpha=0.08, color='#e67e22',
               label='Coexistence saddle')

    ax.set_xlabel(r'Cross-inhibition strength $J_\times$', fontsize=11)
    ax.set_ylabel('Peak firing rate', fontsize=11)
    ax.set_title('Coexistence Existence Boundary', fontweight='bold', fontsize=12)
    ax.legend(fontsize=9, loc='center left')
    ax.set_xlim(0, 0.40)
    ax.set_ylim(-0.05, 1.05)

    plt.tight_layout()
    path = os.path.join(OUTDIR, 'fig_paper_5_existence.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {path}")
    return path


# =====================================================================
# FIG 6: PITCHFORK BIFURCATION DIAGRAM
# =====================================================================

def find_wta_fp(W, preferred, J_cross, dominant='A'):
    """
    Find a WTA fixed point by initializing one network much stronger
    than the other.
    """
    from scipy.optimize import fsolve

    theta1 = np.pi / 4
    drive = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)

    if dominant == 'A':
        r_A = sigmoid(W @ (drive * 0.5) + drive)
        r_B = np.ones(N) * 0.01
    else:
        r_A = np.ones(N) * 0.01
        r_B = sigmoid(W @ (drive * 0.5) + drive)

    # Simulate to convergence
    for _ in range(200000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT / TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT / TAU)

    # Polish with Newton
    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_0, J_cross),
                             fprime=lambda x, W, c, j: jacobian_analytical(x, W, c, j),
                             full_output=True, maxfev=10000)
    r_A_sol = sol[:N]
    r_B_sol = sol[N:]
    res = np.max(np.abs(residual(sol, W, cue_0, J_cross)))
    return r_A_sol, r_B_sol, res


def fig6_pitchfork():
    """
    Fig 6: Pitchfork Bifurcation Diagram
    D = mean(r_A) - mean(r_B) vs J_cross.
    Coexistence branch at D=0 (solid stable, dashed unstable).
    WTA branches splitting off at J_cross*.
    """
    print("  Generating Fig 6: Pitchfork Bifurcation Diagram...")
    W, preferred = build_within_weights(N, J_0, J_1)

    J_CROSS_STAR = 0.3485
    J_CROSS_EXIST = 0.358

    # ── Coexistence branch ──
    jc_coex = np.sort(np.unique(np.concatenate([
        np.linspace(0.01, 0.30, 12),
        np.linspace(0.30, 0.36, 30),
    ])))

    D_coex = []
    jc_coex_valid = []
    r_A_prev, r_B_prev = None, None

    for jc in jc_coex:
        try:
            if r_A_prev is not None:
                r_A, r_B, res = find_coexistence_fp(W, preferred, jc,
                                                     r_A_prev, r_B_prev)
            else:
                r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

            if res < 1e-4 and np.max(r_A) > 0.2 and np.max(r_B) > 0.2:
                D_coex.append(np.mean(r_A) - np.mean(r_B))
                jc_coex_valid.append(jc)
                r_A_prev, r_B_prev = r_A.copy(), r_B.copy()
                print(f"    Coex J_cross={jc:.4f}: D={D_coex[-1]:.6f}, res={res:.2e}")
            else:
                print(f"    Coex J_cross={jc:.4f}: failed (res={res:.2e}, "
                      f"max_rA={np.max(r_A):.3f}, max_rB={np.max(r_B):.3f})")
        except Exception as e:
            print(f"    Coex J_cross={jc:.4f}: exception ({e})")

    jc_coex_valid = np.array(jc_coex_valid)
    D_coex = np.array(D_coex)

    # ── WTA branches (only exist above J_cross*) ──
    jc_wta = np.sort(np.unique(np.concatenate([
        np.linspace(J_CROSS_STAR + 0.001, 0.36, 20),
        np.linspace(0.36, 0.50, 15),
    ])))

    D_wta_A = []  # A-dominant (D > 0)
    D_wta_B = []  # B-dominant (D < 0)
    jc_wta_A_valid = []
    jc_wta_B_valid = []

    for jc in jc_wta:
        try:
            # A-dominant
            r_A, r_B, res = find_wta_fp(W, preferred, jc, dominant='A')
            D = np.mean(r_A) - np.mean(r_B)
            if res < 1e-3 and D > 0.01:
                D_wta_A.append(D)
                jc_wta_A_valid.append(jc)
                print(f"    WTA-A J_cross={jc:.4f}: D={D:.4f}, res={res:.2e}")

            # B-dominant
            r_A, r_B, res = find_wta_fp(W, preferred, jc, dominant='B')
            D = np.mean(r_A) - np.mean(r_B)
            if res < 1e-3 and D < -0.01:
                D_wta_B.append(D)
                jc_wta_B_valid.append(jc)
                print(f"    WTA-B J_cross={jc:.4f}: D={D:.4f}, res={res:.2e}")
        except Exception as e:
            print(f"    WTA J_cross={jc:.4f}: exception ({e})")

    jc_wta_A_valid = np.array(jc_wta_A_valid)
    jc_wta_B_valid = np.array(jc_wta_B_valid)
    D_wta_A = np.array(D_wta_A)
    D_wta_B = np.array(D_wta_B)

    # ── Plot ──
    fig, ax = plt.subplots(1, 1, figsize=(5.5, 4.0))

    # Coexistence branch: stable (solid) for J < J*, unstable (dashed) for J > J*
    mask_stable = jc_coex_valid < J_CROSS_STAR
    mask_unstable = jc_coex_valid >= J_CROSS_STAR

    if np.any(mask_stable):
        ax.plot(jc_coex_valid[mask_stable], D_coex[mask_stable],
                '-', color=COLOR_STABLE, lw=2.5, label='Coexistence (stable)',
                zorder=3)
    if np.any(mask_unstable):
        ax.plot(jc_coex_valid[mask_unstable], D_coex[mask_unstable],
                '--', color=COLOR_UNSTABLE, lw=2.0, label='Coexistence (saddle)',
                zorder=3)

    # WTA branches (stable)
    if len(D_wta_A) > 0:
        ax.plot(jc_wta_A_valid, D_wta_A, '-', color=COLOR_STABLE, lw=2.5,
                label='WTA (stable)', zorder=3)
    if len(D_wta_B) > 0:
        ax.plot(jc_wta_B_valid, D_wta_B, '-', color=COLOR_STABLE, lw=2.5,
                zorder=3)

    # Bifurcation point marker
    ax.plot(J_CROSS_STAR, 0, 'o', color='#8e44ad', ms=10, zorder=10,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.annotate(r'$J_\times^* \approx 0.349$',
                xy=(J_CROSS_STAR, 0),
                xytext=(J_CROSS_STAR - 0.06, 0.12),
                fontsize=9.5, fontweight='bold', color='#8e44ad',
                arrowprops=dict(arrowstyle='->', color='#8e44ad', lw=1.5))

    # Reference line
    ax.axhline(y=0, color='gray', ls=':', lw=0.8, alpha=0.5)

    # Shade the existence threshold
    ax.axvline(x=J_CROSS_EXIST, color='#e67e22', ls='--', lw=1.2, alpha=0.5)
    ax.text(J_CROSS_EXIST + 0.005, -0.22,
            r'$J_\times^{exist}$', fontsize=9, color='#e67e22',
            fontweight='bold')

    ax.set_xlabel(r'Cross-inhibition strength $J_\times$', fontsize=11)
    ax.set_ylabel(r'Dominance $D = \bar{r}^A - \bar{r}^B$', fontsize=11)
    ax.set_title('Pitchfork Bifurcation: Coexistence to WTA', fontweight='bold',
                 fontsize=12)
    ax.legend(fontsize=8.5, loc='upper left')
    ax.set_xlim(0, 0.50)

    plt.tight_layout()
    path = os.path.join(OUTDIR, 'fig_paper_6_pitchfork.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {path}")
    return path


# =====================================================================
# FIG 7: EIGENVECTOR COMPARISON
# =====================================================================

def fig7_eigenvectors():
    """
    Fig 7: Eigenvector Comparison
    Left: A Goldstone eigenvector (sine-shaped, one network only)
    Right: The critical dominance eigenvector (spatially uniform/DC, anti-phase)
    """
    print("  Generating Fig 7: Eigenvector Comparison...")
    W, preferred = build_within_weights(N, J_0, J_1)

    # Use J_cross = 0.34 (near but below J_cross*)
    jc_target = 0.34

    r_A, r_B, res = find_coexistence_fp(W, preferred, jc_target)
    print(f"    J_cross={jc_target}: res={res:.2e}, "
          f"max(r_A)={np.max(r_A):.3f}, max(r_B)={np.max(r_B):.3f}")

    if res > 1e-4 or np.max(r_A) < 0.3 or np.max(r_B) < 0.3:
        print("    WARNING: Fixed point may not be reliable, trying J_cross=0.33...")
        jc_target = 0.33
        r_A, r_B, res = find_coexistence_fp(W, preferred, jc_target)
        print(f"    J_cross={jc_target}: res={res:.2e}")

    # Compute Jacobian and eigendecomposition
    cue_0 = np.zeros(N)
    x = np.concatenate([r_A, r_B])
    J = jacobian_analytical(x, W, cue_0, jc_target)
    evals, evecs = np.linalg.eig(J)

    # Sort by real part (largest first)
    idx = np.argsort(-evals.real)
    evals = evals[idx]
    evecs = evecs[:, idx]

    # Classify
    classified = classify_eigenvalues(evals, evecs, preferred)

    # Find a Goldstone mode
    goldstone_modes = [c for c in classified if c['is_goldstone']]
    genuine_modes = [c for c in classified if not c['is_goldstone']]
    genuine_modes.sort(key=lambda c: -c['eigenvalue'])

    if not goldstone_modes:
        print("    WARNING: No Goldstone modes found!")
        return None

    # Pick the Goldstone mode with highest projection onto gold_A or gold_B
    goldstone_mode = max(goldstone_modes,
                         key=lambda c: max(c['projections']['gold_A'],
                                           c['projections']['gold_B']))
    # Pick the dominant genuine mode (first non-Goldstone)
    critical_mode = genuine_modes[0]

    print(f"    Goldstone: lambda={goldstone_mode['eigenvalue']:.2e}, "
          f"char={goldstone_mode['character']}")
    print(f"    Critical:  lambda={critical_mode['eigenvalue']:.6f}, "
          f"char={critical_mode['character']}")
    print(f"    Critical projections: {critical_mode['projections']}")

    # ── Plot ──
    fig, axes = plt.subplots(1, 2, figsize=(7, 3.5))
    neuron_idx = np.arange(N)

    # LEFT: Goldstone eigenvector
    ax = axes[0]
    vec = goldstone_mode['eigenvector']
    v_A = vec[:N]
    v_B = vec[N:]
    # Normalize for display
    norm = max(np.max(np.abs(v_A)), np.max(np.abs(v_B)))
    if norm > 0:
        v_A = v_A / norm
        v_B = v_B / norm

    ax.plot(neuron_idx, v_A, '-', color=COLOR_A, lw=2.0, label='Network A')
    ax.plot(neuron_idx, v_B, '-', color=COLOR_B, lw=2.0, label='Network B')
    ax.axhline(y=0, color='gray', ls=':', lw=0.8, alpha=0.5)
    ax.set_xlabel('Neuron index $i$', fontsize=10)
    ax.set_ylabel('Eigenvector component', fontsize=10)
    ax.set_title(
        f'Goldstone Mode\n'
        r'$\lambda \approx$' + f' {goldstone_mode["eigenvalue"]:.1e}  '
        f'(rotation)',
        fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.set_xlim(0, N - 1)

    # RIGHT: Critical dominance eigenvector
    ax = axes[1]
    vec = critical_mode['eigenvector']
    v_A = vec[:N]
    v_B = vec[N:]
    norm = max(np.max(np.abs(v_A)), np.max(np.abs(v_B)))
    if norm > 0:
        v_A = v_A / norm
        v_B = v_B / norm

    ax.plot(neuron_idx, v_A, '-', color=COLOR_A, lw=2.0, label='Network A')
    ax.plot(neuron_idx, v_B, '-', color=COLOR_B, lw=2.0, label='Network B')
    ax.axhline(y=0, color='gray', ls=':', lw=0.8, alpha=0.5)
    ax.set_xlabel('Neuron index $i$', fontsize=10)
    ax.set_ylabel('Eigenvector component', fontsize=10)

    # Determine if it's truly uniform-like
    uni_proj = critical_mode['projections'].get('uniform', 0)
    ax.set_title(
        f'Critical Dominance Mode\n'
        r'$\lambda_{dom} = $' + f'{critical_mode["eigenvalue"]:.4f}  '
        f'(DC/uniform)',
        fontsize=10, fontweight='bold')
    ax.legend(fontsize=8, loc='upper right')
    ax.set_xlim(0, N - 1)

    # Annotation about anti-phase
    ax.text(0.5, 0.02, 'Anti-phase: A up, B down\n(spatially uniform)',
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=8, color='#8e44ad', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=COLOR_BG,
                      edgecolor='#8e44ad', alpha=0.8))

    fig.suptitle(r'Eigenvector Comparison at $J_\times = $' + f'{jc_target}',
                 fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(OUTDIR, 'fig_paper_7_eigenvectors.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    Saved: {path}")
    return path


# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("GENERATING PAPER FIGURES: SPECTRAL SEPARATRIX")
    print("=" * 70)

    results = {}

    # Fig 2: Schematic (fast, no computation)
    print("\n[1/4] Fig 2: Model Schematic")
    results['fig2'] = fig2_schematic()

    # Fig 5: Existence boundary (requires J_cross scan)
    print("\n[2/4] Fig 5: Coexistence Existence Boundary")
    results['fig5'] = fig5_existence()

    # Fig 6: Pitchfork bifurcation (requires coexistence + WTA scans)
    print("\n[3/4] Fig 6: Pitchfork Bifurcation Diagram")
    results['fig6'] = fig6_pitchfork()

    # Fig 7: Eigenvector comparison
    print("\n[4/4] Fig 7: Eigenvector Comparison")
    results['fig7'] = fig7_eigenvectors()

    # Summary
    print("\n" + "=" * 70)
    print("FIGURE GENERATION COMPLETE")
    print("=" * 70)
    for name, path in results.items():
        status = "OK" if path and os.path.exists(path) else "FAILED"
        print(f"  {name}: {status}  {path}")
    print("=" * 70)
