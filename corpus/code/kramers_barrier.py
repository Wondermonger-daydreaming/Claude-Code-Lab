"""
==========================================================================
KRAMERS BARRIER HEIGHT FROM SPECTRAL DATA
==========================================================================

Bridge between deterministic spectral analysis and stochastic swap errors.

The pitchfork bifurcation at J_cross* ~ 0.3485 destabilizes the coexistence
fixed point. But stochastic swap errors appear BELOW J_cross*, because noise
allows escape over the finite barrier.

Strategy:
  1. At each J_cross < J_cross*, the coexistence state is a local minimum
     of the effective 1D potential V(D), D = r_bar_A - r_bar_B.
  2. The curvature at D=0 is V''(0) = 2a(J_cross), where a ~ -lambda_dom.
  3. Above J_cross*, the WTA states are the global minima. Their D_WTA
     gives the quartic coefficient alpha = |a| / (2 * D_WTA^2).
  4. Barrier height: Delta_V = a^2 / (4 alpha).
  5. Kramers rate: tau^{-1} ~ exp(-Delta_V / sigma^2).

The script computes everything from the full N=48 neuron model, using the
existing fixed-point finders and Jacobian from spectral_separatrix_goldstone.

Author: SalamanderOpus (Claude Opus 4.6)
Date: February 13, 2026
==========================================================================
"""

import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/gauss/Claude-Code-Lab/corpus/code')
from spectral_portrait_ring_attractor import (
    sigmoid, sigmoid_derivative, build_within_weights, tuning_curve,
    COLORS
)
from spectral_separatrix_goldstone import (
    find_coexistence_fp, jacobian_analytical, classify_eigenvalues,
    residual,
    N, J_0, J_1, KAPPA, INPUT_GAIN, R_MAX, BETA, H0, DT, TAU,
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

OUTDIR = '/home/gauss/Claude-Code-Lab/corpus/code/figures'
os.makedirs(OUTDIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════
# STEP 1: Find coexistence FP and dominant eigenvalue at each J_cross
# ═══════════════════════════════════════════════════════════════════

def find_wta_fp(W, preferred, J_cross, dominant='A'):
    """
    Find a winner-take-all fixed point by initializing one network
    much stronger than the other, then polishing with Newton.
    """
    theta1 = np.pi / 4
    drive = INPUT_GAIN * tuning_curve(theta1, preferred, KAPPA)

    if dominant == 'A':
        r_A = sigmoid(W @ (drive * 0.5) + drive)
        r_B = np.ones(N) * 0.01
    else:
        r_A = np.ones(N) * 0.01
        r_B = sigmoid(W @ (drive * 0.5) + drive)

    # Simulate to convergence (long run for reliability)
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


def compute_spectral_data(jc_values):
    """
    At each J_cross, find the coexistence FP, compute the Jacobian,
    and extract lambda_dom (the dominant non-Goldstone eigenvalue).
    """
    W, preferred = build_within_weights(N, J_0, J_1)

    results = []
    r_A_prev, r_B_prev = None, None

    print("=" * 70)
    print("STEP 1: Coexistence eigenvalues vs J_cross")
    print("=" * 70)

    for jc in jc_values:
        if r_A_prev is not None and jc > 0:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc,
                                                  r_A_prev, r_B_prev)
        else:
            r_A, r_B, res = find_coexistence_fp(W, preferred, jc)

        if res > 1e-4 or np.max(r_A) < 0.2 or np.max(r_B) < 0.2:
            print(f"  J_cross={jc:.4f}: FAILED (res={res:.2e})")
            results.append(None)
            continue

        # Jacobian at the coexistence FP
        cue_0 = np.zeros(N)
        x = np.concatenate([r_A, r_B])
        J = jacobian_analytical(x, W, cue_0, jc)
        evals, evecs = np.linalg.eig(J)
        idx = np.argsort(-evals.real)
        evals, evecs = evals[idx], evecs[:, idx]

        # Classify: separate Goldstone from genuine
        classified = classify_eigenvalues(evals, evecs, preferred)
        goldstone = [c for c in classified if c['is_goldstone']]
        genuine = [c for c in classified if not c['is_goldstone']]
        genuine.sort(key=lambda c: -c['eigenvalue'])

        lam_dom = genuine[0]['eigenvalue'] if genuine else np.nan
        dom_char = genuine[0]['character'] if genuine else 'N/A'

        # Dominance order parameter at coexistence
        D_coex = np.mean(r_A) - np.mean(r_B)

        result = {
            'J_cross': jc,
            'lambda_dom': lam_dom,
            'dom_character': dom_char,
            'D_coex': D_coex,
            'r_A': r_A.copy(),
            'r_B': r_B.copy(),
            'mean_rA': np.mean(r_A),
            'mean_rB': np.mean(r_B),
        }
        results.append(result)
        r_A_prev, r_B_prev = r_A.copy(), r_B.copy()

        status = "UNSTABLE" if lam_dom > 1e-5 else "stable"
        print(f"  J_cross={jc:.4f}: lambda_dom={lam_dom:+.6f} [{dom_char:10s}] "
              f"D={D_coex:+.4f} [{status}]")

    return results, W, preferred


# ═══════════════════════════════════════════════════════════════════
# STEP 2: Estimate alpha from WTA fixed points above J_cross*
# ═══════════════════════════════════════════════════════════════════

def estimate_alpha(W, preferred, jc_wta_values):
    """
    For J_cross values above J_cross*, find WTA fixed points.
    Use D_WTA and the (known) a(J_cross) to estimate alpha.

    At the WTA equilibrium: V'(D_WTA) = 0
      => 4*alpha*D^3 + 2*a*D = 0
      => D^2 = -a / (2*alpha)   [for D != 0]
      => alpha = -a / (2 * D^2)
    """
    print("\n" + "=" * 70)
    print("STEP 2: WTA fixed points and alpha estimation")
    print("=" * 70)

    alpha_estimates = []

    for jc in jc_wta_values:
        # Find WTA FP (A-dominant)
        r_A, r_B, res = find_wta_fp(W, preferred, jc, dominant='A')

        if res > 1e-3:
            print(f"  J_cross={jc:.4f}: WTA solve FAILED (res={res:.2e})")
            continue

        D_wta = np.mean(r_A) - np.mean(r_B)

        # Also get lambda_dom at coexistence (if it exists) for a(J_cross)
        # For J_cross above bifurcation, coexistence is a saddle
        try:
            r_A_c, r_B_c, res_c = find_coexistence_fp(W, preferred, jc)
            if res_c < 1e-3 and np.max(r_A_c) > 0.1 and np.max(r_B_c) > 0.1:
                cue_0 = np.zeros(N)
                x_c = np.concatenate([r_A_c, r_B_c])
                J_c = jacobian_analytical(x_c, W, cue_0, jc)
                evals_c = np.linalg.eigvals(J_c)
                evals_real = np.sort(evals_c.real)[::-1]

                # lambda_dom: largest non-Goldstone
                # Filter out Goldstone (|lambda| < 1e-3)
                non_gold = [e for e in evals_real if abs(e) > 1e-3]
                lam_dom = non_gold[0] if non_gold else np.nan

                # a(J_cross) = -lambda_dom / 2  (the potential curvature is
                # related to the Jacobian eigenvalue; V''(0) = 2a, and the
                # Jacobian eigenvalue of the linearized dynamics at the
                # coexistence FP along the dominance direction is proportional
                # to -V''(0)/tau. So lambda_dom ~ -2a/tau => a ~ -lambda_dom*tau/2)
                #
                # More precisely: the 1D reduced dynamics is
                #   tau * dD/dt = -V'(D) = -2aD - 4alpha*D^3
                # So the Jacobian at D=0 is: d(dD/dt)/dD = -2a/tau
                # Hence lambda_dom = -2a/tau => a = -lambda_dom * tau / 2
                a_jc = -lam_dom * TAU / 2.0

                if abs(D_wta) > 1e-3:
                    alpha_est = -a_jc / (2.0 * D_wta**2)
                    alpha_estimates.append({
                        'J_cross': jc,
                        'D_wta': D_wta,
                        'lambda_dom_coex': lam_dom,
                        'a': a_jc,
                        'alpha': alpha_est,
                        'mean_rA_wta': np.mean(r_A),
                        'mean_rB_wta': np.mean(r_B),
                    })
                    print(f"  J_cross={jc:.4f}: D_wta={D_wta:.4f}, "
                          f"lam_dom={lam_dom:+.6f}, a={a_jc:.4f}, "
                          f"alpha={alpha_est:.2f}")
                else:
                    print(f"  J_cross={jc:.4f}: D_wta too small ({D_wta:.4f})")
            else:
                print(f"  J_cross={jc:.4f}: coexistence FP not found above bifurcation")
        except Exception as e:
            print(f"  J_cross={jc:.4f}: error: {e}")

    return alpha_estimates


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Compute barrier heights and Kramers rates
# ═══════════════════════════════════════════════════════════════════

def compute_barrier_and_kramers(spectral_results, alpha, sigma=0.1):
    """
    Given a(J_cross) from spectral data and alpha from WTA calibration,
    compute:
      - Delta_V(J_cross) = a^2 / (4*alpha)   [barrier at zero cue]
      - Kramers rate: tau^{-1} ~ exp(-Delta_V / sigma^2)

    The 1D cusp potential is: V(D) = alpha*D^4 + a*D^2
    where a < 0 for J_cross < J_cross* (bistable) and a > 0 above.
    """
    print("\n" + "=" * 70)
    print(f"STEP 3: Barrier heights and Kramers rates (sigma={sigma})")
    print("=" * 70)

    barrier_data = []

    for r in spectral_results:
        if r is None:
            continue

        jc = r['J_cross']
        lam_dom = r['lambda_dom']

        # a(J_cross) = -lambda_dom * tau / 2
        a_jc = -lam_dom * TAU / 2.0

        # Below bifurcation: a < 0 (since lambda_dom < 0, a > 0 -- wait,
        # lambda_dom is NEGATIVE below bifurcation (stable), so
        # a = -lam_dom*tau/2 is POSITIVE below bifurcation.
        # But we need a < 0 for double well!
        #
        # Clarification: The Jacobian eigenvalue lambda_dom is
        # the decay rate of perturbations. It's NEGATIVE when the
        # coexistence FP is stable (below bifurcation). The potential
        # curvature V''(0) = 2a must be POSITIVE at the bottom of a well
        # (stable), meaning a > 0 below bifurcation.
        #
        # But wait -- the standard cusp normal form V = D^4 + a*D^2 has
        # a single minimum at D=0 when a > 0, and two minima when a < 0.
        # So for coexistence to be a minimum: a > 0 (no WTA states).
        # For coexistence to be a saddle: a < 0 (WTA states exist).
        #
        # This means: below bifurcation (coexistence stable), a > 0.
        # The barrier to escape from D=0 when there IS no double well
        # is infinite. There are no WTA wells to escape into.
        #
        # The barrier makes physical sense only near/above the bifurcation,
        # where a becomes negative. As J_cross approaches J_cross* from below,
        # a -> 0+. Just above, a -> 0-.
        #
        # For the Kramers escape problem, we actually want the barrier
        # from the WTA well (D_WTA) back to D=0. But at zero cue with
        # exact symmetry, the two WTA wells have equal depth, and the
        # saddle is at D=0.
        #
        # So the barrier from WTA to coexistence:
        #   Delta_V = V(D=0) - V(D_WTA) = 0 - (alpha*D_WTA^4 + a*D_WTA^2)
        #           = -(alpha*D_WTA^4 + a*D_WTA^2)
        # With D_WTA^2 = -a/(2*alpha):
        #   Delta_V = -(alpha * a^2/(4*alpha^2) + a * (-a/(2*alpha)))
        #           = -(a^2/(4*alpha) - a^2/(2*alpha))
        #           = -(-a^2/(4*alpha))
        #           = a^2/(4*alpha)
        #
        # This is positive when a < 0 (above bifurcation).
        #
        # But we want the barrier BELOW bifurcation (where stochastic swaps
        # happen). Below bifurcation, a > 0 and there are no WTA states.
        # The system is in the coexistence well and there's nothing to escape to...
        # unless noise pushes it far enough that the nonlinear dynamics carry it
        # to a quasi-WTA state.
        #
        # Revised understanding: The effective potential is valid near the
        # bifurcation. For J_cross slightly below J_cross*, the potential
        # V(D) = alpha*D^4 + a*D^2 with a small positive a creates a
        # single well whose curvature (width) decreases as a -> 0.
        # The relevant quantity for stochastic escape is the WELL DEPTH
        # at D values where the system starts to run away.
        #
        # For the cusp with a > 0 (monostable), the noise must push D
        # far enough that the quartic term starts to matter. The
        # "effective barrier" for large excursions is set by the well shape.
        #
        # Actually, the right framework is: with noise sigma, the probability
        # of a fluctuation to |D| > D_c is ~ exp(-V(D_c)/sigma^2), where
        # D_c is the threshold beyond which deterministic dynamics runs away.
        # For the cusp just below bifurcation, V(D) = alpha*D^4 + a*D^2
        # and there IS no runaway (it's monostable). The WTA state requires
        # nonlinear effects beyond the quartic approximation.
        #
        # Let me reconsider. The correct picture is:
        #
        # The FULL potential (not just quartic truncation) has WTA states
        # for J_cross > J_cross_exist ~ 0.358 (or earlier with the full
        # nonlinearity). The quartic approximation captures the ONSET
        # of the double-well structure.
        #
        # Near J_cross*:
        #   - Just above: double well with tiny barrier a^2/(4*alpha)
        #   - At J_cross*: single well, zero curvature
        #   - Just below: single well, positive curvature
        #
        # The Kramers escape rate is for the case a < 0 (above bifurcation):
        # escape from WTA well over the saddle at D=0. This gives the
        # rate of spontaneous RECOVERY from a swap error, not the onset.
        #
        # For swap ERROR onset: noise pushes the system from D=0 to |D| >> 0.
        # The barrier is V(D_threshold) - V(0) evaluated at the full potential.
        # In the cusp approximation:
        #   V(D) - V(0) = alpha*D^4 + a*D^2
        #
        # For a > 0 (below bifurcation): this is always positive, so any
        # fluctuation costs energy proportional to a*D^2 at small D.
        # The characteristic escape size is D ~ sigma/sqrt(a), and the
        # probability of reaching a given D falls as exp(-a*D^2/sigma^2).
        #
        # The KEY insight: swap errors don't require escaping to a true WTA
        # state. They require a fluctuation large enough that network A's
        # bump decays while B's is reinforced (or vice versa). This happens
        # when |D| exceeds some threshold D_swap where the nonlinear
        # dynamics takes over.
        #
        # For the Kramers picture, we need: what is the probability of a
        # fluctuation |D| > D_swap during the maintenance period?
        #
        # P_swap ~ exp(-V(D_swap) / sigma^2)
        #        = exp(-(alpha * D_swap^4 + a * D_swap^2) / sigma^2)
        #
        # Near the bifurcation (a -> 0), this reduces to:
        #   P_swap ~ exp(-alpha * D_swap^4 / sigma^2)  [at the bifurcation]
        #
        # Away from bifurcation (a >> 0):
        #   P_swap ~ exp(-a * D_swap^2 / sigma^2)  [Gaussian suppression]
        #
        # The crossover is at a ~ alpha * D_swap^2.
        #
        # So the effective "barrier height" controlling swap probability is:
        #   Delta_V(J_cross) = alpha * D_swap^4 + a(J_cross) * D_swap^2
        #
        # where D_swap is the threshold for irreversible dominance.
        # We can estimate D_swap from the WTA state: D_swap ~ D_WTA.
        #
        # REVISED APPROACH: compute the full 1D potential numerically.

        barrier_data.append({
            'J_cross': jc,
            'lambda_dom': lam_dom,
            'a': a_jc,
        })

    return barrier_data


# ═══════════════════════════════════════════════════════════════════
# STEP 3 (REVISED): Numerical 1D potential along dominance direction
# ═══════════════════════════════════════════════════════════════════

def compute_1d_potential_numerical(W, preferred, J_cross, n_D=201):
    """
    Compute the effective 1D potential V(D) by constrained minimization.

    For each target D = mean(r_A) - mean(r_B), find the constrained
    fixed point and compute the "restoring force" F(D) = -dV/dD.
    Then integrate to get V(D).

    Method: Start from the coexistence FP and slowly bias the system
    toward different D values by adding a Lagrange multiplier term.
    """
    # First, find the coexistence FP as the reference
    r_A_ref, r_B_ref, res_ref = find_coexistence_fp(W, preferred, J_cross)
    if res_ref > 1e-3:
        return None, None, None, None

    D_ref = np.mean(r_A_ref) - np.mean(r_B_ref)
    D_max = 0.15  # Range of D to explore

    D_vals = np.linspace(-D_max, D_max, n_D)
    forces = np.zeros(n_D)

    for i, D_target in enumerate(D_vals):
        # Use a bias field to push toward D_target
        # Add a uniform field: +h to A, -h to B, and find equilibrium
        # Then measure the actual D and the force

        # Initialize from coexistence
        r_A = r_A_ref.copy()
        r_B = r_B_ref.copy()

        # Apply a small biasing field and let the system relax
        # The bias h_bias pushes D toward the target
        h_bias = (D_target - D_ref) * 5.0  # Proportional control

        # Simulate with bias
        for step in range(50000):
            h_A = W @ r_A - J_cross * np.mean(r_B) + h_bias
            h_B = W @ r_B - J_cross * np.mean(r_A) - h_bias
            r_A_new = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * DT / TAU)
            r_B_new = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * DT / TAU)
            if np.max(np.abs(r_A_new - r_A)) < 1e-12 and np.max(np.abs(r_B_new - r_B)) < 1e-12:
                break
            r_A, r_B = r_A_new, r_B_new

        D_actual = np.mean(r_A) - np.mean(r_B)

        # The "force" at this D: the unbiased restoring tendency
        # Without bias, the dynamics would be tau*dD/dt = ...
        # At the biased equilibrium, the bias exactly balances the force:
        #   F(D) + 2*h_bias/N_eff = 0  (approximately)
        # So F(D) ~ -2*h_bias (the unbiased force toward D=0)
        #
        # More precisely: the unbiased force at this state is
        h_A_unbiased = W @ r_A - J_cross * np.mean(r_B)
        h_B_unbiased = W @ r_B - J_cross * np.mean(r_A)
        dr_A = (-r_A + sigmoid(h_A_unbiased))
        dr_B = (-r_B + sigmoid(h_B_unbiased))
        # Force on D = d(mean(r_A) - mean(r_B))/dt
        force_D = (np.mean(dr_A) - np.mean(dr_B)) / TAU
        forces[i] = force_D

    # Integrate force to get potential: V(D) = -integral(F(D) dD)
    dD = D_vals[1] - D_vals[0]
    potential = -np.cumsum(forces) * dD
    # Set V(D=0) = 0
    idx_zero = np.argmin(np.abs(D_vals))
    potential -= potential[idx_zero]

    return D_vals, potential, forces, (r_A_ref, r_B_ref)


def compute_all_potentials(W, preferred, jc_values):
    """Compute 1D potentials for all J_cross values."""
    print("\n" + "=" * 70)
    print("STEP 3: Numerical 1D potential V(D) along dominance direction")
    print("=" * 70)

    all_potentials = []
    for jc in jc_values:
        result = compute_1d_potential_numerical(W, preferred, jc)
        if result[0] is None:
            print(f"  J_cross={jc:.4f}: FAILED")
            all_potentials.append(None)
            continue

        D_vals, V, forces, _ = result
        V_max_barrier = np.max(V[:len(V)//2]) if np.any(V[:len(V)//2] > 0) else 0
        V_min_center = V[len(V)//2]

        # For a monostable well (below bifurcation), the barrier is
        # the potential at the edge of our D range
        # For a double well (above), there's a local max at D=0
        print(f"  J_cross={jc:.4f}: V(D_max)={V[-1]:.6f}, "
              f"V(0)={V[len(V)//2]:.6f}, max(V)={np.max(V):.6f}")

        all_potentials.append({
            'J_cross': jc,
            'D': D_vals,
            'V': V,
            'forces': forces,
        })

    return all_potentials


# ═══════════════════════════════════════════════════════════════════
# ALTERNATIVE: Direct spectral + analytic cusp approach
# ═══════════════════════════════════════════════════════════════════

def compute_kramers_from_spectral(jc_scan_values, jc_wta_values):
    """
    The clean analytic approach:

    1. lambda_dom(J_cross) from eigenvalue analysis
    2. a(J_cross) = -lambda_dom * tau / 2
    3. alpha from WTA calibration at a reference J_cross above bifurcation
    4. For J_cross above bifurcation:
         - Barrier from WTA to saddle: Delta_V = a^2 / (4*alpha)
         - This is the barrier for RECOVERY from a swap error
    5. For J_cross below bifurcation:
         - No true double well, but the well becomes shallow
         - The variance of D fluctuations is: <D^2> = sigma^2 / (2*|a|)
           (Ornstein-Uhlenbeck process)
         - Probability of large D excursion to D_c:
           P(|D| > D_c) ~ exp(-a * D_c^2 / sigma^2)
    6. The swap probability combines both effects:
         - Below J_cross*: P_swap ~ exp(-a(J_cross) * D_c^2 / sigma^2)
         - Above J_cross*: P_swap ~ 1 - exp(-R_kramers * T)
           where R_kramers ~ exp(-a^2/(4*alpha*sigma^2))
    """

    W, preferred = build_within_weights(N, J_0, J_1)

    # ── Get lambda_dom at each J_cross ──
    spectral_results, _, _ = compute_spectral_data(jc_scan_values)

    # ── Get alpha from WTA calibration ──
    alpha_estimates = estimate_alpha(W, preferred, jc_wta_values)

    if not alpha_estimates:
        print("\nERROR: No alpha estimates obtained. Cannot proceed.")
        return None

    # Use median alpha as the quartic coefficient
    alpha_vals = [ae['alpha'] for ae in alpha_estimates]
    alpha_median = np.median(alpha_vals)
    print(f"\n  Alpha estimates: {[f'{a:.1f}' for a in alpha_vals]}")
    print(f"  Using median alpha = {alpha_median:.2f}")

    # Also estimate D_swap from the WTA D values
    D_wta_vals = [abs(ae['D_wta']) for ae in alpha_estimates]
    D_swap = np.median(D_wta_vals)
    print(f"  D_WTA values: {[f'{d:.4f}' for d in D_wta_vals]}")
    print(f"  Using D_swap = {D_swap:.4f}")

    # ── Compute barriers ──
    print("\n" + "=" * 70)
    print("STEP 4: Barrier heights and Kramers escape rates")
    print("=" * 70)

    sigma = 0.1  # Noise level from stochastic simulations

    kramers_data = []

    for r in spectral_results:
        if r is None:
            continue

        jc = r['J_cross']
        lam_dom = r['lambda_dom']
        a_jc = -lam_dom * TAU / 2.0  # Curvature parameter

        if a_jc > 0:
            # Below bifurcation: monostable, barrier is from quadratic well
            # Effective barrier for excursion to D_swap:
            # Delta_V = alpha * D_swap^4 + a * D_swap^2
            Delta_V = alpha_median * D_swap**4 + a_jc * D_swap**2

            # Also compute: barrier for excursion to D = sqrt(sigma^2/a)
            # (the 1-sigma thermal excursion)
            D_thermal = sigma / np.sqrt(max(a_jc, 1e-10))

            # Kramers-like escape rate (not true Kramers, but same
            # exponential suppression):
            if Delta_V / sigma**2 < 50:
                log_rate = -Delta_V / sigma**2
            else:
                log_rate = -50  # Cap for numerical stability

        else:
            # Above bifurcation: coexistence is a saddle
            # True double well with barrier Delta_V = a^2 / (4*alpha)
            Delta_V_recovery = a_jc**2 / (4.0 * alpha_median)
            # Swap probability is high (system goes to WTA spontaneously)
            # The RECOVERY barrier is a^2/(4*alpha)
            Delta_V = 0.0  # No barrier to reach WTA (coexistence is unstable)
            log_rate = 0.0  # Rate is O(1)
            D_thermal = np.inf

        kramers_data.append({
            'J_cross': jc,
            'lambda_dom': lam_dom,
            'a': a_jc,
            'Delta_V': Delta_V,
            'log_rate': log_rate,
            'D_thermal': D_thermal if a_jc > 0 else np.inf,
        })

        if a_jc > 0:
            print(f"  J_cross={jc:.4f}: a={a_jc:+.4f}, "
                  f"Delta_V={Delta_V:.6f}, "
                  f"Delta_V/sigma^2={Delta_V/sigma**2:.2f}, "
                  f"D_thermal={D_thermal:.4f}")
        else:
            print(f"  J_cross={jc:.4f}: a={a_jc:+.4f}, "
                  f"ABOVE BIFURCATION (spontaneous WTA)")

    return {
        'kramers_data': kramers_data,
        'alpha': alpha_median,
        'D_swap': D_swap,
        'alpha_estimates': alpha_estimates,
        'spectral_results': spectral_results,
        'sigma': sigma,
        'W': W,
        'preferred': preferred,
    }


# ═══════════════════════════════════════════════════════════════════
# PLOTTING
# ═══════════════════════════════════════════════════════════════════

def plot_kramers_analysis(data, save_path):
    """
    Four-panel figure:
      A: lambda_dom vs J_cross (spectral data)
      B: Barrier height Delta_V vs J_cross
      C: log(Kramers rate) vs J_cross for several sigma
      D: 1D potential V(D) at several J_cross values
    """
    kd = data['kramers_data']
    alpha = data['alpha']
    D_swap = data['D_swap']
    sigma = data['sigma']

    jc_vals = np.array([d['J_cross'] for d in kd])
    lam_dom = np.array([d['lambda_dom'] for d in kd])
    a_vals = np.array([d['a'] for d in kd])
    DV_vals = np.array([d['Delta_V'] for d in kd])

    # Separate below/above bifurcation
    below = a_vals > 0
    above = a_vals <= 0

    fig = plt.figure(figsize=(16, 14))
    gs = GridSpec(3, 2, figure=fig, hspace=0.4, wspace=0.35)

    J_CROSS_STAR = 0.3485
    J_CROSS_EXIST = 0.358

    # ── Panel A: lambda_dom vs J_cross ──
    ax = fig.add_subplot(gs[0, 0])
    colors_pts = ['#2196F3' if a > 0 else '#e74c3c' for a in a_vals]
    ax.scatter(jc_vals, lam_dom, c=colors_pts, s=50, zorder=3,
               edgecolors='black', linewidths=0.5)
    ax.plot(jc_vals, lam_dom, '-', color='gray', lw=0.8, alpha=0.5)
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

    # Annotate the sign convention
    ax.annotate('a > 0: monostable\n(coexistence stable)',
                xy=(0.15, max(a_vals[below]) * 0.7),
                fontsize=8, color='#2196F3', ha='center')
    ax.annotate('a < 0: bistable\n(coexistence unstable)',
                xy=(0.35, min(a_vals) * 0.5),
                fontsize=8, color='#e74c3c', ha='center')

    # ── Panel C: Barrier height ──
    ax = fig.add_subplot(gs[1, 0])
    ax.plot(jc_vals[below], DV_vals[below], 'o-', color='#2d5a7b',
            lw=2, ms=6, label='$\\Delta V$ (barrier to swap)')
    if np.any(above):
        ax.scatter(jc_vals[above], DV_vals[above], c='#e74c3c',
                   s=80, marker='x', zorder=3, lw=2,
                   label='Above bifurcation ($\\Delta V = 0$)')
    ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7)

    # Mark sigma^2 level
    ax.axhline(sigma**2, color='#f39c12', ls='--', lw=2, alpha=0.8,
               label=f'$\\sigma^2 = {sigma**2}$')

    # Find predicted onset (where Delta_V = sigma^2)
    for i in range(len(jc_vals[below]) - 1):
        if DV_vals[below][i] > sigma**2 and DV_vals[below][i+1] < sigma**2:
            jc1 = jc_vals[below][i]
            jc2 = jc_vals[below][i+1]
            dv1 = DV_vals[below][i]
            dv2 = DV_vals[below][i+1]
            jc_onset = jc1 + (sigma**2 - dv1) * (jc2 - jc1) / (dv2 - dv1)
            ax.axvline(jc_onset, color='#f39c12', ls='-', lw=1.5, alpha=0.5)
            ax.annotate(f'$J_\\times^{{onset}} \\approx {jc_onset:.3f}$',
                       xy=(jc_onset, sigma**2),
                       xytext=(jc_onset - 0.08, sigma**2 * 3),
                       fontsize=10, fontweight='bold', color='#f39c12',
                       arrowprops=dict(arrowstyle='->', color='#f39c12'))
            break

    ax.set_xlabel('$J_\\times$')
    ax.set_ylabel('$\\Delta V(J_\\times)$')
    ax.set_title('(C) Barrier height vs. cross-inhibition', fontweight='bold')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_yscale('log')
    ax.set_ylim(bottom=1e-4)

    # ── Panel D: Kramers rate vs J_cross for multiple sigma ──
    ax = fig.add_subplot(gs[1, 1])
    sigmas = [0.05, 0.08, 0.10, 0.12, 0.15]
    cmap = plt.cm.viridis(np.linspace(0.2, 0.9, len(sigmas)))

    for sig, color in zip(sigmas, cmap):
        # Compute rate for below-bifurcation points
        log_rates = []
        jc_below = []
        for d in kd:
            if d['a'] > 0:  # Below bifurcation
                lr = -d['Delta_V'] / sig**2
                log_rates.append(lr)
                jc_below.append(d['J_cross'])
            else:
                log_rates.append(0)  # Above bifurcation: rate ~ O(1)
                jc_below.append(d['J_cross'])

        ax.plot(jc_below, log_rates, 'o-', color=color, lw=1.5, ms=4,
                label=f'$\\sigma = {sig}$')

    ax.axvline(J_CROSS_STAR, color='#e74c3c', ls=':', lw=2, alpha=0.7)
    ax.axhline(-1, color='gray', ls='--', lw=1, alpha=0.4,
               label='$\\tau_{escape} \\approx e \\cdot \\tau_0$')
    ax.set_xlabel('$J_\\times$')
    ax.set_ylabel('$\\log(\\tau^{-1}_{escape}) = -\\Delta V / \\sigma^2$')
    ax.set_title('(D) Kramers escape rate vs. $J_\\times$', fontweight='bold')
    ax.legend(fontsize=7, ncol=2)
    ax.set_ylim(bottom=-30)

    # ── Panel E: Cusp potential V(D) at several J_cross ──
    ax = fig.add_subplot(gs[2, 0])
    jc_show = [0.20, 0.28, 0.32, 0.34, 0.345, J_CROSS_STAR]
    cmap_show = plt.cm.coolwarm(np.linspace(0.1, 0.9, len(jc_show)))

    D_plot = np.linspace(-0.15, 0.15, 300)
    for jc_s, col in zip(jc_show, cmap_show):
        # Find a(J_cross) by interpolation
        idx = np.argmin(np.abs(jc_vals - jc_s))
        a_s = a_vals[idx]
        V_plot = alpha * D_plot**4 + a_s * D_plot**2
        ax.plot(D_plot, V_plot, '-', color=col, lw=2,
                label=f'$J_\\times={jc_s:.3f}$, $a={a_s:.3f}$')

    ax.axhline(0, color='gray', ls='--', lw=0.5, alpha=0.4)
    # Mark sigma^2 level
    ax.axhline(sigma**2, color='#f39c12', ls=':', lw=1.5, alpha=0.7,
               label=f'$\\sigma^2 = {sigma**2}$')
    ax.set_xlabel('$D = \\bar{{r}}_A - \\bar{{r}}_B$')
    ax.set_ylabel('$V(D) = \\alpha D^4 + a(J_\\times) D^2$')
    ax.set_title('(E) Cusp potential at various $J_\\times$', fontweight='bold')
    ax.legend(fontsize=7, ncol=2)
    ax.set_ylim(-0.002, max(0.02, sigma**2 * 5))

    # ── Panel F: Numerical verification (if available) ──
    ax = fig.add_subplot(gs[2, 1])

    # Plot the numerically computed 1D potentials
    jc_numerical = [0.20, 0.28, 0.32, 0.34, 0.345]
    W = data['W']
    preferred = data['preferred']

    has_numerical = False
    for jc_n, col in zip(jc_numerical, cmap_show[:len(jc_numerical)]):
        result = compute_1d_potential_numerical(W, preferred, jc_n, n_D=101)
        if result[0] is not None:
            D_num, V_num, _, _ = result
            ax.plot(D_num, V_num, '-', color=col, lw=2,
                    label=f'$J_\\times={jc_n:.3f}$ (numerical)')
            has_numerical = True

    if has_numerical:
        ax.axhline(0, color='gray', ls='--', lw=0.5, alpha=0.4)
        ax.axhline(sigma**2, color='#f39c12', ls=':', lw=1.5, alpha=0.7,
                   label=f'$\\sigma^2 = {sigma**2}$')
        ax.set_xlabel('$D = \\bar{{r}}_A - \\bar{{r}}_B$')
        ax.set_ylabel('$V(D)$ (numerical)')
        ax.set_title('(F) Numerical 1D potential (verification)',
                     fontweight='bold')
        ax.legend(fontsize=7, ncol=2)
    else:
        ax.text(0.5, 0.5, 'Numerical potential\ncomputation failed',
                transform=ax.transAxes, ha='center', va='center')

    fig.suptitle(
        "Kramers escape theory for coupled ring attractors\n"
        "Bridging spectral analysis and stochastic swap errors",
        fontsize=14, fontweight='bold', y=1.01
    )

    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"\n  Saved: {save_path}")


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 70)
    print("KRAMERS BARRIER: SPECTRAL THEORY -> STOCHASTIC SWAP ERRORS")
    print("=" * 70)

    # J_cross values for the coexistence eigenvalue scan
    jc_scan = np.sort(np.unique(np.concatenate([
        np.array([0.10, 0.15, 0.20, 0.25, 0.28, 0.30]),
        np.linspace(0.31, 0.36, 20),
    ])))

    # J_cross values for WTA calibration (above bifurcation)
    jc_wta = np.array([0.36, 0.38, 0.40, 0.45, 0.50])

    # Run the full computation
    data = compute_kramers_from_spectral(jc_scan, jc_wta)

    if data is not None:
        # Plot
        save_path = os.path.join(OUTDIR, 'fig56_kramers_barrier.png')
        plot_kramers_analysis(data, save_path)

        # ── Summary ──
        kd = data['kramers_data']
        alpha = data['alpha']
        D_swap = data['D_swap']
        sigma = data['sigma']

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\n  Model parameters:")
        print(f"    N = {N}, J_0 = {J_0}, J_1 = {J_1}")
        print(f"    tau = {TAU}, beta = {BETA}, h0 = {H0}")
        print(f"\n  Key results:")
        print(f"    J_cross* (pitchfork) = 0.3485")
        print(f"    J_cross^exist        = 0.358")
        print(f"    alpha (quartic coeff) = {alpha:.2f}")
        print(f"    D_swap (WTA order parameter) = {D_swap:.4f}")
        print(f"    sigma (noise level) = {sigma}")

        print(f"\n  Barrier heights Delta_V(J_cross):")
        for d in kd:
            if d['a'] > 0:
                ratio = d['Delta_V'] / sigma**2
                print(f"    J_cross={d['J_cross']:.4f}: "
                      f"a={d['a']:+.4f}, "
                      f"Delta_V={d['Delta_V']:.6f}, "
                      f"Delta_V/sigma^2={ratio:.2f}")

        # Find predicted onset
        print(f"\n  Predicted swap onset (Delta_V = sigma^2 = {sigma**2}):")
        for i in range(len(kd) - 1):
            if kd[i]['a'] > 0 and kd[i+1]['a'] > 0:
                if kd[i]['Delta_V'] > sigma**2 > kd[i+1]['Delta_V']:
                    jc1, jc2 = kd[i]['J_cross'], kd[i+1]['J_cross']
                    dv1, dv2 = kd[i]['Delta_V'], kd[i+1]['Delta_V']
                    jc_onset = jc1 + (sigma**2 - dv1) * (jc2 - jc1) / (dv2 - dv1)
                    print(f"    J_cross^onset ~ {jc_onset:.4f}")
                    print(f"    (interpolated between J_cross={jc1:.4f} "
                          f"and {jc2:.4f})")
                    break
        else:
            # Check if all barriers are below sigma^2
            below_bif = [d for d in kd if d['a'] > 0]
            if below_bif:
                min_DV = min(d['Delta_V'] for d in below_bif)
                max_DV = max(d['Delta_V'] for d in below_bif)
                if max_DV < sigma**2:
                    print(f"    All barriers < sigma^2 = {sigma**2}")
                    print(f"    Max barrier = {max_DV:.6f} at J_cross = "
                          f"{max(below_bif, key=lambda d: d['Delta_V'])['J_cross']:.4f}")
                    print(f"    Swaps probable everywhere in scanned range")
                elif min_DV > sigma**2:
                    print(f"    All barriers > sigma^2 = {sigma**2}")
                    print(f"    Min barrier = {min_DV:.6f}")
                    print(f"    Need lower J_cross or higher sigma for onset")

        print(f"\n  Physical interpretation:")
        print(f"    Below J_cross*: coexistence is stable, barrier ~ a*D_swap^2")
        print(f"    The barrier collapses as a -> 0 (approaching bifurcation)")
        print(f"    Swap onset when Delta_V ~ sigma^2 (Kramers criterion)")
        print(f"    Above J_cross*: spontaneous WTA, no barrier needed")

        print("\n" + "=" * 70)
        print("DONE")
        print("=" * 70)
