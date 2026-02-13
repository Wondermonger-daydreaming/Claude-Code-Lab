"""
Synthesize Phase Diagram from Parallel Agent Results
=====================================================
Reads agent_1.json through agent_4.json, merges into a single
(J_cross, drive_strength) phase diagram, and generates a
publication-quality figure.

Usage:
    python3 synthesize_phase_diagram.py
"""

import json
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
import os

RESULTS_DIR = "/home/gauss/Claude-Code-Lab/corpus/code/results"
FIGURES_DIR = "/home/gauss/Claude-Code-Lab/corpus/code/figures"

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


def load_all_results():
    """Load and merge all agent results."""
    all_points = []
    agent_summaries = []

    for path in sorted(glob.glob(os.path.join(RESULTS_DIR, "agent_*.json"))):
        with open(path) as f:
            data = json.load(f)

        agent_summaries.append({
            "agent_id": data["agent_id"],
            "region": data["region"],
            "elapsed": data["elapsed_seconds"],
            "best_swap": data["best_swap_rate"],
            "has_swaps": data["has_swaps_above_5pct"],
            "n_ok": data["n_points_ok"],
            "n_total": data["n_points_total"],
        })

        for r in data["results"]:
            if r["status"] in ("ok",):
                all_points.append({
                    "J_cross": r["J_cross"],
                    "drive": r["input_gain"],
                    "swap_rate": r["swap_rate"],
                    "correct_rate": r["correct_rate"],
                    "mean_error": r.get("mean_error", 0),
                    "agent": data["agent_id"],
                })

    return all_points, agent_summaries


def make_phase_diagram(all_points, agent_summaries):
    """Generate the main phase diagram figure."""
    if not all_points:
        print("ERROR: No valid data points found!")
        return

    j_vals = np.array([p["J_cross"] for p in all_points])
    d_vals = np.array([p["drive"] for p in all_points])
    swap_vals = np.array([p["swap_rate"] for p in all_points])
    correct_vals = np.array([p["correct_rate"] for p in all_points])

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # ─── Panel A: Swap Error Rate ───
    ax = axes[0]
    sc = ax.scatter(j_vals, d_vals, c=swap_vals, cmap='hot_r',
                    s=80, edgecolors='#333', linewidths=0.5,
                    norm=Normalize(vmin=0, vmax=max(50, swap_vals.max())))
    plt.colorbar(sc, ax=ax, label='Swap error rate (%)', shrink=0.8)
    ax.axvline(x=0.3485, color='cyan', ls='--', lw=1.5, alpha=0.7,
               label=r'$J_{cross}^* \approx 0.3485$')
    ax.set_xlabel(r'$J_{cross}$ (cross-inhibition)')
    ax.set_ylabel('Drive strength (input gain)')
    ax.set_title('A. Swap Error Rate', fontweight='bold')
    ax.legend(fontsize=8, loc='upper left')

    # Mark the 5% threshold contour
    swap_above_5 = swap_vals > 5.0
    if swap_above_5.any():
        ax.scatter(j_vals[swap_above_5], d_vals[swap_above_5],
                   s=120, facecolors='none', edgecolors='lime',
                   linewidths=1.5, label='Swap > 5%', zorder=5)
        ax.legend(fontsize=8, loc='upper left')

    # ─── Panel B: Correct Rate ───
    ax = axes[1]
    sc2 = ax.scatter(j_vals, d_vals, c=correct_vals, cmap='YlGn',
                     s=80, edgecolors='#333', linewidths=0.5,
                     norm=Normalize(vmin=0, vmax=100))
    plt.colorbar(sc2, ax=ax, label='Correct rate (%)', shrink=0.8)
    ax.axvline(x=0.3485, color='cyan', ls='--', lw=1.5, alpha=0.7)
    ax.set_xlabel(r'$J_{cross}$ (cross-inhibition)')
    ax.set_ylabel('Drive strength (input gain)')
    ax.set_title('B. Correct Rate', fontweight='bold')

    # ─── Panel C: Competition Index (swap / (swap + correct)) ───
    ax = axes[2]
    total = swap_vals + correct_vals
    competition = np.where(total > 0, swap_vals / total, 0)
    sc3 = ax.scatter(j_vals, d_vals, c=competition, cmap='RdYlBu_r',
                     s=80, edgecolors='#333', linewidths=0.5,
                     norm=Normalize(vmin=0, vmax=1))
    plt.colorbar(sc3, ax=ax, label='Competition index\n(swap / (swap+correct))', shrink=0.8)
    ax.axvline(x=0.3485, color='cyan', ls='--', lw=1.5, alpha=0.7)
    ax.set_xlabel(r'$J_{cross}$ (cross-inhibition)')
    ax.set_ylabel('Drive strength (input gain)')
    ax.set_title('C. Competition Index', fontweight='bold')

    # Annotate critical region
    ax.axhline(y=3.5, color='gray', ls=':', lw=1, alpha=0.5)
    ax.text(0.3485, max(d_vals) * 1.02, 'bifurcation', ha='center',
            fontsize=8, color='cyan', fontstyle='italic')

    fig.suptitle(
        'Phase diagram: swap errors in coupled ring attractors\n'
        f'({len(all_points)} parameter points, 4 agents)',
        fontsize=14, fontweight='bold', y=1.02
    )
    plt.tight_layout()

    outpath = os.path.join(FIGURES_DIR, "fig55_phase_diagram_swap_errors.png")
    plt.savefig(outpath, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Phase diagram saved: {outpath}")

    return outpath


def print_summary(all_points, agent_summaries):
    """Print human-readable summary."""
    print("=" * 70)
    print("PHASE DIAGRAM SYNTHESIS: COUPLED RING ATTRACTOR SWAP ERRORS")
    print("=" * 70)

    for s in agent_summaries:
        r = s["region"]
        print(f"\n  Agent {s['agent_id']}: J=[{r['jcross_min']:.2f}, {r['jcross_max']:.2f}] "
              f"x drive=[{r['drive_min']:.1f}, {r['drive_max']:.1f}]")
        print(f"    {s['n_ok']}/{s['n_total']} points OK | "
              f"Best swap: {s['best_swap']:.1f}% | "
              f"Swaps>5%: {s['has_swaps']} | "
              f"Time: {s['elapsed']:.0f}s")

    swap_vals = [p["swap_rate"] for p in all_points]
    above_5 = [p for p in all_points if p["swap_rate"] > 5.0]

    print(f"\n{'─' * 70}")
    print(f"  Total points: {len(all_points)}")
    print(f"  Points with swap > 5%: {len(above_5)}")
    print(f"  Max swap rate: {max(swap_vals):.1f}%")

    if above_5:
        best = max(above_5, key=lambda p: p["swap_rate"])
        print(f"  Best swap point: J_cross={best['J_cross']:.3f}, "
              f"drive={best['drive']:.1f}, swap={best['swap_rate']:.1f}%")

        # Find the boundary
        j_at_swap = sorted(set(p["J_cross"] for p in above_5))
        print(f"  J_cross values with swaps: {[f'{j:.3f}' for j in j_at_swap[:10]]}")
    else:
        print("  NO SWAP ERRORS > 5% FOUND IN ANY REGION")

    print(f"{'─' * 70}")
    return len(above_5) > 0


if __name__ == "__main__":
    all_points, agent_summaries = load_all_results()
    has_swaps = print_summary(all_points, agent_summaries)
    fig_path = make_phase_diagram(all_points, agent_summaries)

    # Return exit code based on whether swaps were found
    import sys
    sys.exit(0 if has_swaps else 1)
