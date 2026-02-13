"""
Generate Figure 8: Phase Diagram in (J_cross, drive_strength) Space
====================================================================
Publication-quality phase diagram for the spectral separatrix paper.

Loads 128,000-trial parameter sweep results from 4 parallel agents,
interpolates the swap error landscape, and annotates regions with
mechanistic labels and Alleman et al. (2024) mapping.

Data coverage (4 agents, each 8x8 grid):
  Agent 1: J=[0.2, 0.5]  x drive=[1.0, 3.5]
  Agent 2: J=[0.2, 0.5]  x drive=[3.5, 8.0]
  Agent 3: J=[0.5, 3.0]  x drive=[1.0, 3.5]
  Agent 4: J=[3.0, 8.0]  x drive=[3.5, 8.0]

Note: Two quadrants are NOT covered:
  - J=[0.5, 3.0] x drive=[3.5, 8.0]  (mid-J, high drive)
  - J=[3.0, 8.0] x drive=[1.0, 3.5]  (high-J, low drive)

Usage:
    python3 generate_fig8_phase_diagram.py
"""

import json
import glob
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib import ticker
from scipy.interpolate import griddata, RBFInterpolator

# ── Paths ──────────────────────────────────────────────────────────
RESULTS_DIR = "/home/gauss/Claude-Code-Lab/corpus/code/results"
FIGURES_DIR = "/home/gauss/Claude-Code-Lab/corpus/code/figures"
OUTPUT_PATH = os.path.join(FIGURES_DIR, "fig_paper_8_phase_diagram.png")

# ── Style ──────────────────────────────────────────────────────────
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
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'xtick.minor.size': 2,
    'ytick.minor.size': 2,
})


def load_all_results():
    """Load and merge all agent results into arrays."""
    all_j, all_d, all_swap, all_correct = [], [], [], []
    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "agent_*.json"))):
        with open(path) as f:
            data = json.load(f)
        for r in data["results"]:
            if r["status"] == "ok":
                all_j.append(r["J_cross"])
                all_d.append(r["input_gain"])
                all_swap.append(r["swap_rate"])
                all_correct.append(r["correct_rate"])
    return (np.array(all_j), np.array(all_d),
            np.array(all_swap), np.array(all_correct))


def make_colormap():
    """
    Perceptually clear colormap:
      Deep teal (0%) -> pale (5%) -> warm amber (20%) -> deep brick (50%)
    The 5% contour should sit at the visual transition from cool to warm.
    """
    anchors = [
        (0.00, (0.08, 0.18, 0.30)),    # deep ocean
        (0.04, (0.15, 0.35, 0.52)),    # dark teal
        (0.10, (0.55, 0.70, 0.75)),    # light teal
        (0.15, (0.88, 0.86, 0.80)),    # warm cream
        (0.25, (0.92, 0.78, 0.40)),    # amber gold
        (0.40, (0.85, 0.48, 0.20)),    # burnt orange
        (0.55, (0.70, 0.22, 0.15)),    # brick
        (1.00, (0.35, 0.08, 0.06)),    # deep maroon
    ]
    positions = [a[0] for a in anchors]
    colors_rgb = [a[1] for a in anchors]
    cdict = {'red': [], 'green': [], 'blue': []}
    for pos, (r, g, b) in zip(positions, colors_rgb):
        cdict['red'].append((pos, r, r))
        cdict['green'].append((pos, g, g))
        cdict['blue'].append((pos, b, b))
    return LinearSegmentedColormap('phase_swap', cdict, N=512)


def interpolate_swap(j_vals, d_vals, swap_vals, n_grid=250):
    """
    RBF interpolation of swap rate onto a regular grid.
    Handles the irregular L-shaped data coverage gracefully.
    """
    # Normalize coordinates for RBF (important for anisotropic ranges)
    j_norm = (j_vals - j_vals.min()) / (j_vals.max() - j_vals.min())
    d_norm = (d_vals - d_vals.min()) / (d_vals.max() - d_vals.min())

    j_grid = np.linspace(j_vals.min(), j_vals.max(), n_grid)
    d_grid = np.linspace(d_vals.min(), d_vals.max(), n_grid)
    J_mesh, D_mesh = np.meshgrid(j_grid, d_grid)

    j_mesh_norm = (J_mesh - j_vals.min()) / (j_vals.max() - j_vals.min())
    d_mesh_norm = (D_mesh - d_vals.min()) / (d_vals.max() - d_vals.min())

    # RBF interpolation (thin plate spline, good for scattered data)
    coords = np.column_stack([j_norm, d_norm])
    query = np.column_stack([j_mesh_norm.ravel(), d_mesh_norm.ravel()])
    rbf = RBFInterpolator(coords, swap_vals, kernel='thin_plate_spline',
                          smoothing=1.0)
    swap_grid = rbf(query).reshape(J_mesh.shape)

    # Clip to physical range
    swap_grid = np.clip(swap_grid, 0, 55)

    return J_mesh, D_mesh, swap_grid


def generate_figure():
    """Generate the publication-quality phase diagram."""
    j_vals, d_vals, swap_vals, correct_vals = load_all_results()
    n_points = len(j_vals)
    print(f"Loaded {n_points} data points from 4 agents")
    print(f"  J_cross range: [{j_vals.min():.3f}, {j_vals.max():.3f}]")
    print(f"  Drive range:   [{d_vals.min():.3f}, {d_vals.max():.3f}]")
    print(f"  Swap range:    [{swap_vals.min():.1f}%, {swap_vals.max():.1f}%]")

    # Valley stats
    valley_mask = (j_vals > 1.0) & (j_vals < 2.0) & (d_vals < 3.5)
    if valley_mask.any():
        v_swap = swap_vals[valley_mask]
        v_j = j_vals[valley_mask]
        v_d = d_vals[valley_mask]
        min_i = np.argmin(v_swap)
        print(f"  Valley minimum: {v_swap[min_i]:.1f}% "
              f"at J_cross={v_j[min_i]:.3f}, drive={v_d[min_i]:.2f}")

    # ── Interpolation ─────────────────────────────────────────────
    J_mesh, D_mesh, swap_grid = interpolate_swap(j_vals, d_vals, swap_vals)

    # ── Figure setup ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 5))

    cmap = make_colormap()
    vmax = 52  # Slightly above 50% for breathing room

    # Heatmap base layer
    im = ax.pcolormesh(
        J_mesh, D_mesh, swap_grid,
        cmap=cmap, norm=Normalize(vmin=0, vmax=vmax),
        shading='gouraud', rasterized=True,
    )

    # ── Contour lines ─────────────────────────────────────────────
    # The 5% contour is the key boundary; others are guides
    contour_levels = [5, 10, 20, 30, 40]
    line_widths = [1.8, 0.7, 0.7, 0.7, 0.7]
    line_styles = ['solid', 'dashed', 'dashed', 'dashed', 'dashed']

    cs = ax.contour(
        J_mesh, D_mesh, swap_grid,
        levels=contour_levels,
        colors='white', linewidths=line_widths, linestyles=line_styles,
        alpha=0.65,
    )
    # Label contours
    fmt = {5: '5%', 10: '10%', 20: '20%', 30: '30%', 40: '40%'}
    ax.clabel(cs, levels=[5, 20, 40], fontsize=7.5, fmt=fmt,
              colors='white', inline=True, inline_spacing=8)

    # ── Scatter: raw data points ──────────────────────────────────
    ax.scatter(
        j_vals, d_vals,
        s=10, c='white', alpha=0.3, edgecolors='none',
        zorder=5, marker='o',
    )

    # ── Colorbar ──────────────────────────────────────────────────
    cbar = fig.colorbar(im, ax=ax, shrink=0.85, aspect=28, pad=0.015)
    cbar.set_label('Swap error rate (%)', fontsize=11, labelpad=10)
    cbar.ax.tick_params(labelsize=9)
    cbar.set_ticks([0, 5, 10, 20, 30, 40, 50])

    # ── Critical vertical lines ───────────────────────────────────
    # Pitchfork bifurcation
    ax.axvline(x=0.3485, color='#00e5ff', ls='--', lw=1.5, alpha=0.9,
               zorder=10)
    # Coexistence existence threshold
    ax.axvline(x=0.358, color='#76ff03', ls=':', lw=1.3, alpha=0.85,
               zorder=10)

    # ── Stroke helper for text on heatmap ─────────────────────────
    stroke_dark = [pe.withStroke(linewidth=3.0, foreground='#111111')]
    stroke_medium = [pe.withStroke(linewidth=2.0, foreground='#1a1a1a')]

    # ── Region labels ─────────────────────────────────────────────

    # 1. COEXISTENCE (low J, all drives -- the deep teal region)
    ax.text(0.215, 5.0, 'Coexistence',
            fontsize=11, color='#b0d8e8', fontweight='bold', fontstyle='italic',
            ha='center', va='center', rotation=90,
            path_effects=stroke_dark, zorder=20)

    # 2. WTA ONSET (J ~ 0.25-0.5 -- warm transition zone)
    ax.text(0.42, 4.5, 'WTA onset',
            fontsize=9, color='#fff3e0', fontweight='bold', fontstyle='italic',
            ha='center', va='center', rotation=90,
            path_effects=stroke_dark, zorder=20)

    # 3. THE VALLEY (J ~ 1.2-1.6, low drive -- the cool dip)
    ax.text(1.5, 2.0, 'The Valley',
            fontsize=10.5, color='#b0d8e8', fontweight='bold', fontstyle='italic',
            ha='center', va='center',
            path_effects=stroke_dark, zorder=20)

    # 4. OVERPOWERING (high J, moderate-to-high drive -- the dark red)
    ax.text(5.0, 4.5, 'Overpowering',
            fontsize=11, color='#ffcdd2', fontweight='bold', fontstyle='italic',
            ha='center', va='center',
            path_effects=stroke_dark, zorder=20)

    # ── Alleman et al. annotations ────────────────────────────────

    # Selection failure: points to the WTA onset band
    ax.annotate(
        'Selection failure\n(Alleman et al., 2024)',
        xy=(0.5, 3.0), xytext=(2.2, 6.8),
        fontsize=8.5, color='#e0e0e0', fontstyle='italic', ha='center',
        arrowprops=dict(arrowstyle='->', color='#cccccc', lw=1.0,
                        connectionstyle='arc3,rad=0.2'),
        path_effects=stroke_medium, zorder=20,
    )

    # Representation failure: points into the overpowering regime
    ax.annotate(
        'Representation failure',
        xy=(6.0, 5.0), xytext=(6.2, 7.5),
        fontsize=8.5, color='#e0e0e0', fontstyle='italic', ha='center',
        arrowprops=dict(arrowstyle='->', color='#cccccc', lw=1.0,
                        connectionstyle='arc3,rad=-0.1'),
        path_effects=stroke_medium, zorder=20,
    )

    # ── Critical line legend (custom) ─────────────────────────────
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='#00e5ff', ls='--', lw=1.5,
               label=r'$J_{\mathrm{cross}}^{\,*} \approx 0.349$  (pitchfork)'),
        Line2D([0], [0], color='#76ff03', ls=':', lw=1.3,
               label=r'$J_{\mathrm{cross}}^{\,\mathrm{exist}} \approx 0.358$  (existence limit)'),
    ]
    legend = ax.legend(
        handles=legend_elements,
        loc='lower right', fontsize=8,
        framealpha=0.92, facecolor=BG_COLOR,
        edgecolor='#888888', borderpad=0.5,
        handlelength=2.5,
    )
    legend.get_frame().set_linewidth(0.5)

    # ── Narrow window annotation ──────────────────────────────────
    # Use an inset zoom to make the narrow delta-J visible
    # Place a bracket + label at a clear y-level
    y_bkt = 7.6
    ax.plot([0.3485, 0.3485], [y_bkt - 0.2, y_bkt + 0.2],
            color='#ffeb3b', lw=1.3, zorder=25)
    ax.plot([0.358, 0.358], [y_bkt - 0.2, y_bkt + 0.2],
            color='#ffeb3b', lw=1.3, zorder=25)
    ax.plot([0.3485, 0.358], [y_bkt, y_bkt],
            color='#ffeb3b', lw=1.3, zorder=25)
    ax.text(
        0.353, y_bkt + 0.35, r'$\Delta J \!\approx\! 0.01$',
        fontsize=7, color='#ffeb3b', ha='center', va='bottom',
        path_effects=stroke_dark, zorder=25,
    )

    # ── Axes ──────────────────────────────────────────────────────
    ax.set_xlabel(r'Cross-inhibition strength  $J_{\mathrm{cross}}$', fontsize=12)
    ax.set_ylabel('Drive strength  (input gain)', fontsize=12)
    ax.set_xlim(0.15, 8.2)
    ax.set_ylim(0.8, 8.2)

    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

    # ── Title ─────────────────────────────────────────────────────
    ax.set_title(
        'Phase diagram of swap errors in coupled ring attractors\n'
        f'$N\\!=\\!48$ neurons/ring, 500 trials/point, {n_points} parameter points',
        fontsize=12, fontweight='bold', pad=8,
        linespacing=1.6,
    )
    # Make the subtitle line smaller by using the title's second line
    # (matplotlib doesn't support per-line sizing in title, so we use
    #  a secondary text object instead)
    ax.set_title(
        'Phase diagram of swap errors in coupled ring attractors',
        fontsize=12.5, fontweight='bold', pad=18,
    )
    ax.text(
        0.5, 1.005,
        f'$N\\!=\\!48$ neurons/ring  |  500 trials/point  |  {n_points} parameter points',
        fontsize=8, color='#777777', ha='center', va='bottom',
        transform=ax.transAxes,
    )

    # ── Save ──────────────────────────────────────────────────────
    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight', facecolor=BG_COLOR)
    plt.close()
    print(f"\nFigure saved: {OUTPUT_PATH}")
    return OUTPUT_PATH


def print_data_summary(j_vals, d_vals, swap_vals):
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("DATA SUMMARY FOR FIGURE 8")
    print("=" * 60)

    regions = [
        ("J_cross < 0.25", j_vals < 0.25, "Coexistence"),
        ("J_cross in [0.25,0.5]", (j_vals >= 0.25) & (j_vals <= 0.5), "WTA onset"),
        ("J_cross in (0.5,2.0]", (j_vals > 0.5) & (j_vals <= 2.0), "Valley + rise"),
        ("J_cross > 2.0", j_vals > 2.0, "Overpowering"),
    ]
    for label, mask, regime in regions:
        if mask.any():
            s = swap_vals[mask]
            print(f"  {label:25s}: swap = {s.mean():.1f}% +/- {s.std():.1f}%  "
                  f"(n={mask.sum()}, '{regime}')")

    # Valley detail
    valley_mask = (j_vals > 1.0) & (j_vals < 2.0)
    if valley_mask.any():
        v = swap_vals[valley_mask]
        vj = j_vals[valley_mask]
        vd = d_vals[valley_mask]
        mi = np.argmin(v)
        print(f"\n  Valley min: {v[mi]:.1f}% at J={vj[mi]:.3f}, drive={vd[mi]:.2f}")

    # Transition sharpness
    j_unique = np.sort(np.unique(j_vals))
    print(f"\n  Unique J_cross values: {len(j_unique)}")
    for j in j_unique[:10]:
        mask = j_vals == j
        print(f"    J={j:.4f}: swap={swap_vals[mask].mean():5.1f}% "
              f"+/- {swap_vals[mask].std():4.1f}%  (n={mask.sum():2d})")

    print("=" * 60)


if __name__ == "__main__":
    j_vals, d_vals, swap_vals, correct_vals = load_all_results()
    print_data_summary(j_vals, d_vals, swap_vals)
    generate_figure()
