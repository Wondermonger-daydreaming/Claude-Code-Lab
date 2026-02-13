#!/usr/bin/env python3
"""Kramers barrier analysis — extracted from notebook, fixed alpha calibration."""


# ======================================================================
# CELL 0
# ======================================================================

import numpy as np
from scipy.optimize import fsolve
from scipy.special import i0
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ======================================================================
# CELL 1
# ======================================================================

# ═══════════════════════════════════════════════════════════════════
# MODEL PARAMETERS
# ═══════════════════════════════════════════════════════════════════

N = 48
J_0, J_1 = 1.0, 6.0       # Global inhibition, cosine excitation
KAPPA, INPUT_GAIN = 2.0, 5.0
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 0.1, 10.0

# ═══════════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def sigmoid(h, r_max=R_MAX, beta=BETA, h0=H0):
    """Sigmoid transfer function."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))

def sigmoid_derivative(h, r_max=R_MAX, beta=BETA, h0=H0):
    """Derivative: sigma'(h) = beta * sigma(h) * (1 - sigma(h)/r_max)."""
    s = sigmoid(h, r_max, beta, h0)
    return beta * s * (1.0 - s / r_max)

def build_within_weights(N, J_0, J_1):
    """Cosine connectivity: W_ij = (-J_0 + J_1 cos(phi_i - phi_j)) / N."""
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    dphi = preferred[:, np.newaxis] - preferred[np.newaxis, :]
    W = (-J_0 + J_1 * np.cos(dphi)) / N
    return W, preferred

def tuning_curve(theta, preferred, kappa):
    """Von Mises tuning curve."""
    return np.exp(kappa * np.cos(theta - preferred)) / (2 * np.pi * i0(kappa))

# ═══════════════════════════════════════════════════════════════════
# FIXED POINT FINDING
# ═══════════════════════════════════════════════════════════════════

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
    """Find coexistence FP at cue=0 via simulation + Newton polish."""
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

def find_wta_fp(W, preferred, J_cross, dominant='A'):
    """Find WTA fixed point by initializing one network dominant."""
    theta1 = np.pi / 4
    drive = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)
    if dominant == 'A':
        r_A = sigmoid(W @ (drive * 0.5) + drive)
        r_B = np.ones(N) * 0.01
    else:
        r_A = np.ones(N) * 0.01
        r_B = sigmoid(W @ (drive * 0.5) + drive)

    for _ in range(200000):
        h_A = W @ r_A - J_cross * np.mean(r_B)
        h_B = W @ r_B - J_cross * np.mean(r_A)
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT / TAU)
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT / TAU)

    cue_0 = np.zeros(N)
    x0 = np.concatenate([r_A, r_B])
    sol, _, ier, _ = fsolve(residual, x0, args=(W, cue_0, J_cross),
                             fprime=lambda x, W, c, j: jacobian_analytical(x, W, c, j),
                             full_output=True, maxfev=10000)
    res = np.max(np.abs(residual(sol, W, cue_0, J_cross)))
    return sol[:N], sol[N:], res

print("Model defined. N =", N, "neurons per ring.")

# ======================================================================
# CELL 2
# ======================================================================

def classify_eigenvalues(evals, evecs, preferred):
    """
    Separate eigenvalues into Goldstone modes (|lambda| < threshold)
    and genuine modes. Classify each by character.
    """
    GOLDSTONE_THRESHOLD = 1e-3

    cos_p = np.cos(preferred - np.pi/4)
    sin_p = np.sin(preferred - np.pi/4)

    # Projection directions
    d_dom = np.concatenate([cos_p, -cos_p])
    d_dom /= np.linalg.norm(d_dom)

    d_drift_same = np.concatenate([sin_p, sin_p])
    d_drift_same /= np.linalg.norm(d_drift_same)

    d_drift_opp = np.concatenate([sin_p, -sin_p])
    d_drift_opp /= np.linalg.norm(d_drift_opp)

    d_uni = np.concatenate([np.ones(N), -np.ones(N)])
    d_uni /= np.linalg.norm(d_uni)

    d_gold_A = np.concatenate([sin_p, np.zeros(N)])
    d_gold_A /= np.linalg.norm(d_gold_A)

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

print("Eigenvalue classifier ready.")

# ======================================================================
# CELL 3
# ======================================================================

# Build weight matrix
W, preferred = build_within_weights(N, J_0, J_1)

# J_cross scan values — dense near bifurcation
jc_scan = np.sort(np.unique(np.concatenate([
    np.array([0.05, 0.10, 0.15, 0.20, 0.25, 0.28, 0.30]),
    np.linspace(0.31, 0.36, 20),
])))

print(f"Scanning {len(jc_scan)} J_cross values...")
print("=" * 70)

spectral_results = []
r_A_prev, r_B_prev = None, None

for jc in jc_scan:
    if r_A_prev is not None and jc > 0:
        r_A, r_B, res = find_coexistence_fp(W, preferred, jc, r_A_prev, r_B_prev)
    else:
        r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

    if res > 1e-4 or np.max(r_A) < 0.2 or np.max(r_B) < 0.2:
        print(f"  J_cross={jc:.4f}: FAILED (res={res:.2e})")
        spectral_results.append(None)
        continue

    # Jacobian at coexistence FP
    cue_0 = np.zeros(N)
    x = np.concatenate([r_A, r_B])
    J = jacobian_analytical(x, W, cue_0, jc)
    evals, evecs = np.linalg.eig(J)
    idx = np.argsort(-evals.real)
    evals, evecs = evals[idx], evecs[:, idx]

    # Classify
    classified = classify_eigenvalues(evals, evecs, preferred)
    genuine = [c for c in classified if not c['is_goldstone']]
    genuine.sort(key=lambda c: -c['eigenvalue'])

    lam_dom = genuine[0]['eigenvalue'] if genuine else np.nan
    dom_char = genuine[0]['character'] if genuine else 'N/A'
    dom_vec = genuine[0]['eigenvector'] if genuine else None
    D_coex = np.mean(r_A) - np.mean(r_B)

    result = {
        'J_cross': jc,
        'lambda_dom': lam_dom,
        'dom_character': dom_char,
        'dom_eigenvector': dom_vec,
        'D_coex': D_coex,
        'r_A': r_A.copy(),
        'r_B': r_B.copy(),
        'mean_rA': np.mean(r_A),
        'mean_rB': np.mean(r_B),
    }
    spectral_results.append(result)
    r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

    status = "UNSTABLE" if lam_dom > 1e-5 else "stable"
    print(f"  J_cross={jc:.4f}: lambda_dom={lam_dom:+.6f} [{dom_char:10s}] "
          f"D={D_coex:+.4f} [{status}]")

print("\nDone. Successfully computed:", sum(r is not None for r in spectral_results),
      "of", len(jc_scan), "points.")

# ======================================================================
# CELL 4
# ======================================================================

# FIXED: Use J_cross values between pitchfork (0.3485) and existence limit (0.358)
# so coexistence FP still exists but is unstable (a < 0)
jc_wta_values = np.array([0.349, 0.350, 0.352, 0.354, 0.356])

print("=" * 70)
print("STEP 2: WTA fixed points and alpha estimation")
print("=" * 70)

alpha_estimates = []

for jc in jc_wta_values:
    # Find WTA FP (A-dominant)
    r_A_wta, r_B_wta, res_wta = find_wta_fp(W, preferred, jc, dominant='A')
    if res_wta > 1e-3:
        print(f"  J_cross={jc:.4f}: WTA solve FAILED (res={res_wta:.2e})")
        continue

    D_wta = np.mean(r_A_wta) - np.mean(r_B_wta)

    # Also get lambda_dom at coexistence (saddle) for a(J_cross)
    try:
        r_A_c, r_B_c, res_c = find_coexistence_fp(W, preferred, jc)
        if res_c < 1e-2 and np.max(r_A_c) > 0.05 and np.max(r_B_c) > 0.05:
            cue_0 = np.zeros(N)
            x_c = np.concatenate([r_A_c, r_B_c])
            J_c = jacobian_analytical(x_c, W, cue_0, jc)
            evals_c = np.linalg.eigvals(J_c)
            evals_real = np.sort(evals_c.real)[::-1]

            # lambda_dom: largest non-Goldstone
            non_gold = [e for e in evals_real if abs(e) > 1e-3]
            lam_dom = non_gold[0] if non_gold else np.nan

            # a(J_cross) = -lambda_dom * tau / 2
            # From: tau * dD/dt = -V'(D) = -2aD - 4alpha*D^3
            # Jacobian eigenvalue: lambda_dom = -2a/tau => a = -lambda_dom * tau / 2
            a_jc = -lam_dom * TAU / 2.0

            if abs(D_wta) > 1e-3:
                alpha_est = -a_jc / (2.0 * D_wta**2)
                alpha_estimates.append({
                    'J_cross': jc,
                    'D_wta': D_wta,
                    'lambda_dom_coex': lam_dom,
                    'a': a_jc,
                    'alpha': alpha_est,
                })
                print(f"  J_cross={jc:.4f}: D_wta={D_wta:.4f}, "
                      f"lam_dom={lam_dom:+.6f}, a={a_jc:.4f}, "
                      f"alpha={alpha_est:.2f}")
            else:
                print(f"  J_cross={jc:.4f}: D_wta too small ({D_wta:.4f})")
        else:
            print(f"  J_cross={jc:.4f}: coexistence FP not found")
    except Exception as e:
        print(f"  J_cross={jc:.4f}: error: {e}")

if alpha_estimates:
    alpha_vals = [ae['alpha'] for ae in alpha_estimates]
    alpha_median = np.median(alpha_vals)
    D_wta_vals = [abs(ae['D_wta']) for ae in alpha_estimates]
    D_swap = np.median(D_wta_vals)
    print(f"\n  Alpha estimates: {[f'{a:.2f}' for a in alpha_vals]}")
    print(f"  >>> Median alpha = {alpha_median:.4f}")
    print(f"  D_WTA values: {[f'{d:.4f}' for d in D_wta_vals]}")
    print(f"  >>> Median D_swap = {D_swap:.4f}")
else:
    print("\nERROR: No alpha estimates obtained.")
    alpha_median = None
    D_swap = None

# ======================================================================
# CELL 5
# ======================================================================

SIGMA = 0.1  # Noise level from stochastic simulations
T_MAINT = 500  # Maintenance steps
K0_RANGE = (0.1, 1.0)  # Attempt frequency range (per step)

print("=" * 70)
print(f"STEP 3: Barrier heights (sigma={SIGMA}, T={T_MAINT} steps)")
print("=" * 70)

kramers_data = []

for r in spectral_results:
    if r is None:
        continue

    jc = r['J_cross']
    lam_dom = r['lambda_dom']

    # a(J_cross) = -lambda_dom * tau / 2
    a_jc = -lam_dom * TAU / 2.0

    if a_jc > 0 and alpha_median is not None:
        # Below bifurcation: monostable well
        # Barrier for excursion to D_swap:
        Delta_V = alpha_median * D_swap**4 + a_jc * D_swap**2

        # Also compute the normal-form barrier |lambda|^2/(4*gamma)
        # where gamma = alpha (they're the same coefficient in 1D)
        Delta_V_nf = lam_dom**2 / (4.0 * alpha_median)

        # Kramers exponent (dimensionless)
        kramers_exp = Delta_V / SIGMA**2
    else:
        Delta_V = 0.0
        Delta_V_nf = 0.0
        kramers_exp = 0.0

    kramers_data.append({
        'J_cross': jc,
        'lambda_dom': lam_dom,
        'a': a_jc,
        'Delta_V': Delta_V,
        'Delta_V_nf': Delta_V_nf,
        'kramers_exp': kramers_exp,
    })

    if a_jc > 0:
        print(f"  J_cross={jc:.4f}: a={a_jc:+.5f}, "
              f"Delta_V={Delta_V:.6f}, "
              f"Delta_V/sigma^2={kramers_exp:.2f}")
    else:
        print(f"  J_cross={jc:.4f}: a={a_jc:+.5f}, "
              f"ABOVE BIFURCATION (spontaneous WTA)")

# ── Find predicted onset ──
print("\n" + "=" * 70)
print("KRAMERS ONSET PREDICTION")
print("=" * 70)

below_bif = [d for d in kramers_data if d['a'] > 0]

for k0 in [0.1, 0.5, 1.0]:
    ln_k0T = np.log(k0 * T_MAINT)
    threshold = ln_k0T  # Delta_V / sigma^2 < ln(k0*T)

    # Find crossing
    onset_jc = None
    for i in range(len(below_bif) - 1):
        if below_bif[i]['kramers_exp'] > threshold > below_bif[i+1]['kramers_exp']:
            jc1, jc2 = below_bif[i]['J_cross'], below_bif[i+1]['J_cross']
            ke1, ke2 = below_bif[i]['kramers_exp'], below_bif[i+1]['kramers_exp']
            onset_jc = jc1 + (threshold - ke1) * (jc2 - jc1) / (ke2 - ke1)
            break

    if onset_jc:
        print(f"  k0={k0}: ln(k0*T)={ln_k0T:.2f} => "
              f"J_cross^onset = {onset_jc:.4f}")
    else:
        # Check if all below threshold
        if below_bif and max(d['kramers_exp'] for d in below_bif) < threshold:
            print(f"  k0={k0}: ln(k0*T)={ln_k0T:.2f} => "
              f"All barriers below threshold (swaps everywhere)")
        elif below_bif and min(d['kramers_exp'] for d in below_bif) > threshold:
            print(f"  k0={k0}: ln(k0*T)={ln_k0T:.2f} => "
              f"All barriers above threshold (no swaps in range)")
        else:
            print(f"  k0={k0}: ln(k0*T)={ln_k0T:.2f} => "
              f"Could not interpolate onset")

print(f"\n  Observed onset from phase diagram: J_cross ~ 0.25")
print(f"  Deterministic bifurcation:         J_cross* = 0.3485")

# ======================================================================
# CELL 6
# ======================================================================

def compute_1d_potential_numerical(W, preferred, J_cross, n_D=101):
    """Compute effective 1D potential V(D) via constrained simulation."""
    r_A_ref, r_B_ref, res_ref = find_coexistence_fp(W, preferred, J_cross)
    if res_ref > 1e-3:
        return None, None, None

    D_ref = np.mean(r_A_ref) - np.mean(r_B_ref)
    D_max = 0.15
    D_vals = np.linspace(-D_max, D_max, n_D)
    forces = np.zeros(n_D)

    for i, D_target in enumerate(D_vals):
        r_A = r_A_ref.copy()
        r_B = r_B_ref.copy()
        h_bias = (D_target - D_ref) * 5.0

        for step in range(50000):
            h_A = W @ r_A - J_cross * np.mean(r_B) + h_bias
            h_B = W @ r_B - J_cross * np.mean(r_A) - h_bias
            r_A_new = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT / TAU)
            r_B_new = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT / TAU)
            if np.max(np.abs(r_A_new - r_A)) < 1e-12 and np.max(np.abs(r_B_new - r_B)) < 1e-12:
                break
            r_A, r_B = r_A_new, r_B_new

        h_A_unbiased = W @ r_A - J_cross * np.mean(r_B)
        h_B_unbiased = W @ r_B - J_cross * np.mean(r_A)
        dr_A = (-r_A + sigmoid(h_A_unbiased))
        dr_B = (-r_B + sigmoid(h_B_unbiased))
        force_D = (np.mean(dr_A) - np.mean(dr_B)) / TAU
        forces[i] = force_D

    dD = D_vals[1] - D_vals[0]
    potential = -np.cumsum(forces) * dD
    idx_zero = np.argmin(np.abs(D_vals))
    potential -= potential[idx_zero]

    return D_vals, potential, forces


# Compute at selected J_cross values
jc_for_potential = [0.15, 0.20, 0.25, 0.30, 0.32, 0.34]
numerical_potentials = {}

print("Computing numerical 1D potentials...")
for jc_p in jc_for_potential:
    result = compute_1d_potential_numerical(W, preferred, jc_p)
    if result[0] is not None:
        numerical_potentials[jc_p] = result
        D_vals, V, _ = result
        print(f"  J_cross={jc_p:.2f}: V(0)={V[len(V)//2]:.6f}, "
              f"V(D_max)={V[-1]:.6f}")
    else:
        print(f"  J_cross={jc_p:.2f}: FAILED")

print("Done.")

# ======================================================================
# CELL 7
# ======================================================================

plt.rcParams.update({
    'figure.facecolor': '#faf8f5',
    'axes.facecolor': '#faf8f5',
    'font.family': 'serif',
    'font.size': 11,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
})

J_CROSS_STAR = 0.3485
J_CROSS_EXIST = 0.358

fig = plt.figure(figsize=(16, 14))
gs = GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

jc_vals = np.array([d['J_cross'] for d in kramers_data])
lam_dom_vals = np.array([d['lambda_dom'] for d in kramers_data])
a_vals = np.array([d['a'] for d in kramers_data])
DV_vals = np.array([d['Delta_V'] for d in kramers_data])
below = a_vals > 0
above = a_vals <= 0
colors_pts = ['#2196F3' if a > 0 else '#e74c3c' for a in a_vals]

# ── Panel A: lambda_dom vs J_cross ──
ax = fig.add_subplot(gs[0, 0])
ax.scatter(jc_vals, lam_dom_vals, c=colors_pts, s=50, zorder=3,
           edgecolors='black', linewidths=0.5)
ax.plot(jc_vals, lam_dom_vals, '-', color='gray', lw=0.8, alpha=0.5)
ax.axhline(0, color='black', ls='--', lw=1, alpha=0.4)
ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7,
           label=f'$J_\\times^* = {J_CROSS_STAR}$')
ax.set_xlabel('$J_\\times$')
ax.set_ylabel('$\\lambda_{\\mathrm{dom}}$')
ax.set_title('(A) Dominant eigenvalue at coexistence FP', fontweight='bold')
ax.legend(fontsize=9)

# ── Panel B: Curvature parameter a(J_cross) ──
ax = fig.add_subplot(gs[0, 1])
ax.scatter(jc_vals, a_vals, c=colors_pts, s=50, zorder=3,
           edgecolors='black', linewidths=0.5)
ax.plot(jc_vals, a_vals, '-', color='gray', lw=0.8, alpha=0.5)
ax.axhline(0, color='black', ls='--', lw=1, alpha=0.4)
ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7)
ax.set_xlabel('$J_\\times$')
ax.set_ylabel('$a(J_\\times) = -\\lambda_{\\mathrm{dom}} \\tau / 2$')
ax.set_title('(B) Cusp curvature parameter', fontweight='bold')

# ── Panel C: Barrier height ──
ax = fig.add_subplot(gs[1, 0])
ax.plot(jc_vals[below], DV_vals[below], 'o-', color='#2d5a7b',
        lw=2, ms=6, label='$\\Delta V$ (barrier to swap)')
if np.any(above):
    ax.scatter(jc_vals[above], DV_vals[above], c='#e74c3c',
               s=80, marker='x', zorder=3, lw=2,
               label='Above bifurcation ($\\Delta V = 0$)')
ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7)
ax.axhline(SIGMA**2, color='#f39c12', ls='--', lw=2, alpha=0.8,
           label=f'$\\sigma^2 = {SIGMA**2}$')

# Mark predicted onset
for i in range(len(jc_vals[below]) - 1):
    if DV_vals[below][i] > SIGMA**2 and DV_vals[below][i+1] < SIGMA**2:
        jc1 = jc_vals[below][i]
        jc2 = jc_vals[below][i+1]
        dv1 = DV_vals[below][i]
        dv2 = DV_vals[below][i+1]
        jc_onset = jc1 + (SIGMA**2 - dv1) * (jc2 - jc1) / (dv2 - dv1)
        ax.axvline(jc_onset, color='#f39c12', ls='-', lw=1.5, alpha=0.5)
        ax.annotate(f'$J_\\times^{{onset}} \\approx {jc_onset:.3f}$',
                   xy=(jc_onset, SIGMA**2),
                   xytext=(jc_onset - 0.08, SIGMA**2 * 3),
                   fontsize=10, fontweight='bold', color='#f39c12',
                   arrowprops=dict(arrowstyle='->', color='#f39c12'))
        break

ax.set_xlabel('$J_\\times$')
ax.set_ylabel('$\\Delta V(J_\\times)$')
ax.set_title('(C) Barrier height vs. cross-inhibition', fontweight='bold')
ax.legend(fontsize=8, loc='upper left')
ax.set_yscale('log')
ax.set_ylim(bottom=1e-4)

# ── Panel D: Kramers rate for multiple sigma ──
ax = fig.add_subplot(gs[1, 1])
sigmas = [0.05, 0.08, 0.10, 0.12, 0.15]
cmap = plt.cm.viridis(np.linspace(0.2, 0.9, len(sigmas)))

for sig, color in zip(sigmas, cmap):
    log_rates = []
    jc_plot = []
    for d in kramers_data:
        if d['a'] > 0:
            lr = -d['Delta_V'] / sig**2
        else:
            lr = 0
        log_rates.append(lr)
        jc_plot.append(d['J_cross'])
    ax.plot(jc_plot, log_rates, 'o-', color=color, lw=1.5, ms=4,
            label=f'$\\sigma = {sig}$')

ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7)
ax.axhline(-1, color='gray', ls='--', lw=1, alpha=0.4)
ax.set_xlabel('$J_\\times$')
ax.set_ylabel('$-\\Delta V / \\sigma^2$')
ax.set_title('(D) Kramers escape rate vs. $J_\\times$', fontweight='bold')
ax.legend(fontsize=7, ncol=2)
ax.set_ylim(bottom=-30)

# ── Panel E: Cusp potential at various J_cross (analytic) ──
ax = fig.add_subplot(gs[2, 0])
jc_show = [0.15, 0.20, 0.25, 0.30, 0.34, J_CROSS_STAR]
cmap_show = plt.cm.coolwarm(np.linspace(0.1, 0.9, len(jc_show)))
D_plot = np.linspace(-0.15, 0.15, 300)

if alpha_median is not None:
    for jc_s, col in zip(jc_show, cmap_show):
        idx = np.argmin(np.abs(jc_vals - jc_s))
        a_s = a_vals[idx]
        V_plot = alpha_median * D_plot**4 + a_s * D_plot**2
        ax.plot(D_plot, V_plot, '-', color=col, lw=2,
                label=f'$J_\\times={jc_s:.3f}$')

ax.axhline(0, color='gray', ls='--', lw=0.5, alpha=0.4)
ax.axhline(SIGMA**2, color='#f39c12', ls=':', lw=1.5, alpha=0.7,
           label=f'$\\sigma^2 = {SIGMA**2}$')
ax.set_xlabel('$D = \\bar{r}_A - \\bar{r}_B$')
ax.set_ylabel('$V(D) = \\alpha D^4 + a D^2$')
ax.set_title('(E) Analytic cusp potential at various $J_\\times$', fontweight='bold')
ax.legend(fontsize=7, ncol=2)
ax.set_ylim(-0.002, max(0.02, SIGMA**2 * 5))

# ── Panel F: Numerical 1D potential (verification) ──
ax = fig.add_subplot(gs[2, 1])
if numerical_potentials:
    colors_num = plt.cm.coolwarm(np.linspace(0.1, 0.9, len(numerical_potentials)))
    for (jc_n, (D_num, V_num, _)), col in zip(
            sorted(numerical_potentials.items()), colors_num):
        ax.plot(D_num, V_num, '-', color=col, lw=2,
                label=f'$J_\\times={jc_n:.2f}$ (numerical)')
    ax.axhline(0, color='gray', ls='--', lw=0.5, alpha=0.4)
    ax.axhline(SIGMA**2, color='#f39c12', ls=':', lw=1.5, alpha=0.7,
               label=f'$\\sigma^2 = {SIGMA**2}$')
    ax.set_xlabel('$D = \\bar{r}_A - \\bar{r}_B$')
    ax.set_ylabel('$V(D)$ (numerical)')
    ax.set_title('(F) Numerical 1D potential (verification)', fontweight='bold')
    ax.legend(fontsize=7, ncol=2)
else:
    ax.text(0.5, 0.5, 'Numerical potential\ncomputation failed',
            transform=ax.transAxes, ha='center', va='center')

fig.suptitle(
    "Kramers escape theory for coupled ring attractors\n"
    "Bridging spectral analysis and stochastic swap errors",
    fontsize=14, fontweight='bold', y=1.01
)

plt.savefig('/home/gauss/Claude-Code-Lab/paper/kramers_barrier_analysis.png', dpi=200, bbox_inches='tight')
# plt.show()  # disabled for batch run
print("Figure saved: kramers_barrier_analysis.png")

# ======================================================================
# CELL 8
# ======================================================================

print("=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"\n  Model: N={N}, J_0={J_0}, J_1={J_1}, tau={TAU}, beta={BETA}, h0={H0}")
print(f"  Noise: sigma={SIGMA}, T_maint={T_MAINT} steps")

print(f"\n  SPECTRAL RESULTS:")
print(f"    J_cross* (pitchfork)  = 0.3485")
print(f"    J_cross^exist         = 0.358")
if alpha_median is not None:
    print(f"    alpha (quartic, from WTA) = {alpha_median:.4f}")
    print(f"    D_swap (WTA order param)  = {D_swap:.4f}")

print(f"\n  BARRIER TABLE:")
print(f"    {'J_cross':>8s}  {'lambda_dom':>10s}  {'a(J)':>8s}  {'Delta_V':>10s}  {'DV/sigma2':>10s}")
print(f"    {'-'*8}  {'-'*10}  {'-'*8}  {'-'*10}  {'-'*10}")
for d in kramers_data:
    if d['a'] > 0:
        print(f"    {d['J_cross']:8.4f}  {d['lambda_dom']:+10.6f}  {d['a']:8.5f}  "
              f"{d['Delta_V']:10.6f}  {d['kramers_exp']:10.2f}")

print(f"\n  KRAMERS PREDICTION:")
for k0 in [0.1, 0.5, 1.0]:
    ln_k0T = np.log(k0 * T_MAINT)
    for i in range(len(below_bif) - 1):
        if below_bif[i]['kramers_exp'] > ln_k0T > below_bif[i+1]['kramers_exp']:
            jc1, jc2 = below_bif[i]['J_cross'], below_bif[i+1]['J_cross']
            ke1, ke2 = below_bif[i]['kramers_exp'], below_bif[i+1]['kramers_exp']
            onset = jc1 + (ln_k0T - ke1) * (jc2 - jc1) / (ke2 - ke1)
            print(f"    k0={k0}: threshold={ln_k0T:.2f} => J_onset={onset:.4f}")
            break

print(f"\n  Observed onset: J_cross ~ 0.25")

# Implied gamma from onset
if alpha_median is not None:
    # lambda_dom at J=0.25 (from data)
    j025 = [d for d in kramers_data if abs(d['J_cross'] - 0.25) < 0.01]
    if j025:
        lam_at_025 = j025[0]['lambda_dom']
        print(f"\n  COMPUTED lambda_dom(0.25) = {lam_at_025:.6f}")
        print(f"  (vs linear-near-critical estimate: -0.328)")
        print(f"  (vs linear-global estimate: -0.162)")

        for k0 in [0.1, 1.0]:
            ln_k0T = np.log(k0 * T_MAINT)
            # From DV = lam^2 / (4*gamma), and DV/sigma^2 = ln(k0*T):
            gamma_implied = lam_at_025**2 / (4.0 * SIGMA**2 * ln_k0T)
            print(f"  Implied gamma (k0={k0}): {gamma_implied:.4f}")

print("\n" + "=" * 70)

# ======================================================================
# CELL 9
# ======================================================================

if numerical_potentials and alpha_median is not None:
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()

    for i, jc_p in enumerate(jc_for_potential):
        if jc_p not in numerical_potentials or i >= 6:
            continue

        ax = axes[i]
        D_num, V_num, _ = numerical_potentials[jc_p]

        # Numerical
        ax.plot(D_num, V_num, '-', color='#2d5a7b', lw=2.5, label='Numerical')

        # Analytic cusp
        idx = np.argmin(np.abs(jc_vals - jc_p))
        a_s = a_vals[idx]
        V_analytic = alpha_median * D_num**4 + a_s * D_num**2
        ax.plot(D_num, V_analytic, '--', color='#e74c3c', lw=2, label='Cusp fit')

        ax.axhline(SIGMA**2, color='#f39c12', ls=':', lw=1, alpha=0.7)
        ax.set_title(f'$J_\\times = {jc_p:.2f}$', fontweight='bold')
        ax.set_xlabel('$D$')
        if i % 3 == 0:
            ax.set_ylabel('$V(D)$')
        ax.legend(fontsize=8)

    plt.suptitle('Analytic cusp vs numerical potential', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('/home/gauss/Claude-Code-Lab/paper/cusp_vs_numerical.png', dpi=150, bbox_inches='tight')
    # plt.show()  # disabled for batch run
    print("Saved: cusp_vs_numerical.png")
else:
    print("Skipping comparison (missing data).")
