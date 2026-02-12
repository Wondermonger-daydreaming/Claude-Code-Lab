"""
==========================================================================
SEPARATING GOLDSTONE MODES FROM GENUINE INSTABILITY
==========================================================================

The J_cross scan (fig52) showed λ₁ ≈ 0 everywhere — but this is the
Goldstone mode (neutral rotation), not a genuine instability.

The mean-field cross-inhibition (-J_cross * mean(r_B)) doesn't depend
on WHERE bumps sit, only on their AMPLITUDE. So rotational symmetry
is never broken, and the Goldstone modes (bump rotation) stay at zero.

The REAL question: what happens to the first NON-Goldstone eigenvalue?
That's the mode governing amplitude competition (dominance).

This script:
  1. At each J_cross, identifies and removes Goldstone eigenvalues (|λ| < ε)
  2. Tracks the first non-Goldstone eigenvalue λ_dom(J_cross)
  3. Finds the critical J_cross where λ_dom crosses zero
  4. Characterizes the critical eigenvector (is it dominance? drift? mixed?)
  5. Fine-grained scan near the critical point

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 12, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve
from scipy.special import i0
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
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 0.1, 10.0


def residual(x, W, cue_A, J_cross):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
    h_B = W @ r_B - J_cross * np.mean(r_A)
    return np.concatenate([-r_A + sigmoid(h_A), -r_B + sigmoid(h_B)])


def jacobian_analytical(x, W, cue_A, J_cross):
    r_A, r_B = x[:N], x[N:]
    h_A = W @ r_A + cue_A - J_cross * np.mean(r_B)
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


def find_coexistence_fp(W, preferred, J_cross, r_A_init=None, r_B_init=None):
    """Find coexistence FP at cue=0."""
    if r_A_init is not None:
        r_A, r_B = r_A_init.copy(), r_B_init.copy()
    else:
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

    for _ in range(100000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT/TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT/TAU)

    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_0, J_cross),
                             fprime=lambda x, W, c, j: jacobian_analytical(x, W, c, j),
                             full_output=True, maxfev=10000)
    res = np.max(np.abs(residual(sol, W, cue_0, J_cross)))
    return sol[:N], sol[N:], res


def classify_eigenvalues(evals, evecs, preferred):
    """
    Separate eigenvalues into Goldstone modes (|λ| < threshold)
    and genuine modes (|λ| ≥ threshold).

    For each eigenvector, also compute its character (dominance vs drift).
    """
    GOLDSTONE_THRESHOLD = 1e-3  # Generous — Goldstone should be ~1e-10

    cos_p = np.cos(preferred - np.pi/4)
    sin_p = np.sin(preferred - np.pi/4)

    # Four projection directions:
    # 1. Symmetric dominance: A↑ B↓ (cosine envelope)
    d_dom = np.concatenate([cos_p, -cos_p])
    d_dom /= np.linalg.norm(d_dom)

    # 2. Symmetric drift: both bumps shift in same direction (sine envelope)
    d_drift_same = np.concatenate([sin_p, sin_p])
    d_drift_same /= np.linalg.norm(d_drift_same)

    # 3. Antisymmetric drift: bumps shift in opposite directions
    d_drift_opp = np.concatenate([sin_p, -sin_p])
    d_drift_opp /= np.linalg.norm(d_drift_opp)

    # 4. Uniform: A↑ B↓ uniform (DC mode)
    d_uni = np.concatenate([np.ones(N), -np.ones(N)])
    d_uni /= np.linalg.norm(d_uni)

    # 5. Goldstone direction A: derivative of bump A w.r.t. rotation
    d_gold_A = np.concatenate([sin_p, np.zeros(N)])
    d_gold_A /= np.linalg.norm(d_gold_A)

    # 6. Goldstone direction B: derivative of bump B w.r.t. rotation
    d_gold_B = np.concatenate([np.zeros(N), sin_p])
    d_gold_B /= np.linalg.norm(d_gold_B)

    results = []
    for i in range(len(evals)):
        ev = evals[i].real
        vec = evecs[:, i].real
        vec_n = vec / (np.linalg.norm(vec) + 1e-30)

        is_goldstone = abs(ev) < GOLDSTONE_THRESHOLD

        proj = {
            'dominance': abs(np.dot(vec_n, d_dom)),
            'drift_same': abs(np.dot(vec_n, d_drift_same)),
            'drift_opp': abs(np.dot(vec_n, d_drift_opp)),
            'uniform': abs(np.dot(vec_n, d_uni)),
            'gold_A': abs(np.dot(vec_n, d_gold_A)),
            'gold_B': abs(np.dot(vec_n, d_gold_B)),
        }
        best_char = max(proj, key=proj.get)

        results.append({
            'eigenvalue': ev,
            'eigenvector': vec_n,
            'is_goldstone': is_goldstone,
            'projections': proj,
            'character': best_char,
        })

    return results


def run_analysis():
    W, preferred = build_within_weights(N, J_0, J_1)

    # Coarse scan + fine scan near critical region
    jc_values = np.sort(np.unique(np.concatenate([
        np.linspace(0.0, 0.30, 10),
        np.linspace(0.30, 0.36, 30),
    ])))

    print("=" * 70)
    print("GOLDSTONE-SEPARATED EIGENVALUE ANALYSIS")
    print("=" * 70)

    all_results = []
    r_A_prev, r_B_prev = None, None

    for jc in jc_values:
        if r_A_prev is not None and jc > 0:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc, r_A_prev, r_B_prev)
        else:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

        if res > 1e-4 or np.max(r_A) < 0.3 or np.max(r_B) < 0.3:
            print(f"  J_cross={jc:.4f}: FAILED or no bumps")
            all_results.append(None)
            continue

        # Full Jacobian
        cue_0 = np.zeros(N)
        h_A = W @ r_A + cue_0 - jc * np.mean(r_B)
        h_B = W @ r_B - jc * np.mean(r_A)
        x = np.concatenate([r_A, r_B])
        J = jacobian_analytical(x, W, cue_0, jc)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals, evecs = evals[idx], evecs[:, idx]

        classified = classify_eigenvalues(evals, evecs, preferred)

        # Separate Goldstone from genuine
        goldstone = [c for c in classified if c['is_goldstone']]
        genuine = [c for c in classified if not c['is_goldstone']]

        # Sort genuine by eigenvalue (largest first)
        genuine.sort(key=lambda c: -c['eigenvalue'])

        n_gold = len(goldstone)
        n_genuine_pos = sum(1 for c in genuine if c['eigenvalue'] > 1e-6)
        lam_dom = genuine[0]['eigenvalue'] if genuine else np.nan
        dom_char = genuine[0]['character'] if genuine else 'N/A'
        dom_proj = genuine[0]['projections'] if genuine else {}

        result = {
            'J_cross': jc,
            'max_rA': np.max(r_A), 'max_rB': np.max(r_B),
            'D': np.mean(r_A) - np.mean(r_B),
            'n_goldstone': n_gold,
            'n_genuine_positive': n_genuine_pos,
            'lambda_dom': lam_dom,
            'dom_character': dom_char,
            'dom_projections': dom_proj,
            'goldstone_evals': [c['eigenvalue'] for c in goldstone[:4]],
            'top_genuine_evals': [c['eigenvalue'] for c in genuine[:5]],
            'top_genuine_chars': [c['character'] for c in genuine[:5]],
            'all_evals': evals,
        }
        all_results.append(result)
        r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

        marker = "UNSTABLE" if n_genuine_pos > 0 else "stable"
        gold_str = f"({n_gold} Goldstone)"
        print(f"  J_cross={jc:.4f}: λ_dom={lam_dom:+.6f} [{dom_char}], "
              f"genuine_pos={n_genuine_pos}, {gold_str}  [{marker}]")

        # Print Goldstone eigenvalues for verification
        if n_gold > 0:
            gold_evals_str = ", ".join(f"{e:.2e}" for e in result['goldstone_evals'])
            print(f"    Goldstone eigenvalues: {gold_evals_str}")

    return all_results, W, preferred, jc_values


def plot_goldstone_analysis(results, save_path):
    valid = [r for r in results if r is not None]
    jc_v = [r['J_cross'] for r in valid]

    fig = plt.figure(figsize=(22, 14))
    gs = GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

    # ── (0,0) λ_dom vs J_cross (the money plot) ──
    ax = fig.add_subplot(gs[0, 0])
    lam_dom = [r['lambda_dom'] for r in valid]
    colors = ['#e74c3c' if l > 1e-4 else '#2196F3' for l in lam_dom]
    ax.scatter(jc_v, lam_dom, c=colors, s=40, zorder=3, edgecolors='black', linewidths=0.5)
    ax.plot(jc_v, lam_dom, '-', color='gray', lw=0.8, alpha=0.5)
    ax.axhline(y=0, color='black', ls='--', lw=1.5, alpha=0.4)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('λ_dom (first non-Goldstone)')
    ax.set_title('Dominance Eigenvalue\n(Goldstone modes removed)', fontweight='bold')

    # Find crossing
    for i in range(len(valid) - 1):
        l1, l2 = valid[i]['lambda_dom'], valid[i+1]['lambda_dom']
        if l1 < -1e-4 and l2 > 1e-4:
            jc1, jc2 = valid[i]['J_cross'], valid[i+1]['J_cross']
            jc_crit = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)
            ax.axvline(x=jc_crit, color='#e74c3c', ls=':', lw=2, alpha=0.8)
            ax.annotate(f'J* = {jc_crit:.4f}', xy=(jc_crit, 0),
                       xytext=(jc_crit - 0.08, max(lam_dom) * 0.7),
                       fontsize=11, fontweight='bold', color='#e74c3c',
                       arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=1.5))

    # ── (0,1) Number of Goldstone modes ──
    ax = fig.add_subplot(gs[0, 1])
    ax.plot(jc_v, [r['n_goldstone'] for r in valid], 'o-', color='#9C27B0',
            lw=2, ms=5)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('# Goldstone modes (|λ| < 10⁻³)')
    ax.set_title('Goldstone Mode Count', fontweight='bold')
    ax.set_yticks(range(max(r['n_goldstone'] for r in valid) + 2))

    # ── (0,2) Top 5 genuine eigenvalues ──
    ax = fig.add_subplot(gs[0, 2])
    for k in range(min(5, min(len(r['top_genuine_evals']) for r in valid))):
        vals = [r['top_genuine_evals'][k] for r in valid]
        ax.plot(jc_v, vals, 'o-', ms=2, lw=1.5, label=f'λ_{k+1}(genuine)')
    ax.axhline(y=0, color='black', ls='--', alpha=0.4)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('Re(λ)')
    ax.set_title('Top 5 Non-Goldstone Eigenvalues', fontweight='bold')
    ax.legend(fontsize=7)

    # ── (1,0) Eigenvector character ──
    ax = fig.add_subplot(gs[1, 0])
    # For the dominant genuine mode, plot projections
    proj_keys = ['dominance', 'drift_same', 'drift_opp', 'uniform']
    proj_colors = {'dominance': '#e74c3c', 'drift_same': '#2196F3',
                   'drift_opp': '#9C27B0', 'uniform': '#4CAF50'}
    for key in proj_keys:
        vals = [r['dom_projections'].get(key, 0) for r in valid]
        ax.plot(jc_v, vals, 'o-', color=proj_colors[key], lw=1.5, ms=3, label=key)
    ax.set_xlabel('J_cross')
    ax.set_ylabel('|Projection|')
    ax.set_title('Dominant Mode Character', fontweight='bold')
    ax.legend(fontsize=7)
    ax.set_ylim(-0.05, 1.05)

    # ── (1,1) Goldstone eigenvalue magnitudes ──
    ax = fig.add_subplot(gs[1, 1])
    for k in range(4):
        vals = []
        jcs = []
        for r in valid:
            if len(r['goldstone_evals']) > k:
                vals.append(abs(r['goldstone_evals'][k]))
                jcs.append(r['J_cross'])
        if vals:
            ax.semilogy(jcs, vals, 'o-', ms=3, lw=1, label=f'|λ_gold_{k+1}|')
    ax.set_xlabel('J_cross')
    ax.set_ylabel('|λ| (log scale)')
    ax.set_title('Goldstone Eigenvalue Magnitudes', fontweight='bold')
    ax.legend(fontsize=7)

    # ── (1,2) Bump heights ──
    ax = fig.add_subplot(gs[1, 2])
    ax.plot(jc_v, [r['max_rA'] for r in valid], 'o-', color=COLORS['network_A'],
            lw=2, ms=3, label='max(r_A)')
    ax.plot(jc_v, [r['max_rB'] for r in valid], 'o-', color=COLORS['network_B'],
            lw=2, ms=3, label='max(r_B)')
    ax.set_xlabel('J_cross')
    ax.set_ylabel('Peak firing rate')
    ax.set_title('Bump Heights (cue=0)', fontweight='bold')
    ax.legend(fontsize=8)

    # ── (2,0) Full eigenvalue spectrum at 3 key J_cross values ──
    show_jc = [0.1, 0.3, 0.35]
    for col, jc_target in enumerate(show_jc):
        ax = fig.add_subplot(gs[2, col])
        matches = [r for r in valid if abs(r['J_cross'] - jc_target) < 0.015]
        if matches:
            m = min(matches, key=lambda r: abs(r['J_cross'] - jc_target))
            evals_sorted = np.sort(m['all_evals'].real)[::-1]
            colors_ev = ['#e74c3c' if e > 1e-3 else '#9C27B0' if abs(e) < 1e-3
                         else '#2196F3' for e in evals_sorted]
            ax.bar(range(len(evals_sorted)), evals_sorted, color=colors_ev, width=1.0)
            ax.axhline(y=0, color='black', ls='--', lw=1, alpha=0.5)
            ax.set_xlabel('Eigenvalue index')
            ax.set_ylabel('Re(λ)')
            ax.set_title(f'Full Spectrum at J_cross={m["J_cross"]:.3f}\n'
                        f'Gold={m["n_goldstone"]}, Unstable={m["n_genuine_positive"]}',
                        fontsize=9, fontweight='bold')
            ax.set_xlim(-1, min(30, len(evals_sorted)))

    fig.suptitle('Goldstone-Separated Spectral Analysis\n'
                 'Distinguishing neutral rotation modes from genuine instability',
                 fontsize=14, fontweight='bold', y=1.01)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved: {save_path}")


if __name__ == '__main__':
    import os
    outdir = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
    os.makedirs(outdir, exist_ok=True)

    results, W, preferred, jc_values = run_analysis()

    plot_goldstone_analysis(
        results,
        os.path.join(outdir, 'fig53_goldstone_separated.png'))

    # Final summary
    valid = [r for r in results if r is not None]
    print(f"\n{'='*70}")
    print("GOLDSTONE-SEPARATED SUMMARY")
    print(f"{'='*70}")

    for r in valid:
        status = "UNSTABLE" if r['n_genuine_positive'] > 0 else "stable"
        print(f"  J={r['J_cross']:.4f}: λ_dom={r['lambda_dom']:+.6f} "
              f"[{r['dom_character']:15s}] gold={r['n_goldstone']} "
              f"gen_pos={r['n_genuine_positive']}  {status}")

    # Precise critical point
    for i in range(len(valid) - 1):
        l1, l2 = valid[i]['lambda_dom'], valid[i+1]['lambda_dom']
        if l1 < -1e-4 and l2 > 1e-4:
            jc1, jc2 = valid[i]['J_cross'], valid[i+1]['J_cross']
            jc_crit = jc1 + (0 - l1) * (jc2 - jc1) / (l2 - l1)
            print(f"\n  *** CRITICAL J_cross* ≈ {jc_crit:.4f} ***")
            print(f"      λ_dom goes from {l1:+.6f} ({valid[i]['dom_character']}) "
                  f"to {l2:+.6f} ({valid[i+1]['dom_character']})")
            near = min(valid, key=lambda r: abs(r['J_cross'] - jc_crit))
            print(f"      Near critical: dominance proj = "
                  f"{near['dom_projections'].get('dominance', 0):.3f}")
            print(f"      Near critical: drift_opp proj = "
                  f"{near['dom_projections'].get('drift_opp', 0):.3f}")
            break
    print(f"{'='*70}")
