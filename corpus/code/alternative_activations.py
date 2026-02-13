"""
Alternative Activation Functions for Coupled Ring Attractors
=============================================================
Fallback experiment: if sigmoid activation fails to produce swap errors,
test 3 alternative activation functions that might create stronger
winner-take-all dynamics.

Hypothesis: The sigmoid's smooth saturation may prevent clean WTA.
Sharper or asymmetric activation functions could amplify competition.

Usage:
    python3 alternative_activations.py
"""

import json
import time
import numpy as np
from scipy.special import i0

# ─── Shared components ───

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

# ─── Activation functions ───

def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
    """Standard sigmoid (baseline)."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))

def threshold_power(h, r_max=1.0, n=3.0, h0=0.3):
    """Threshold-power law: [h - h0]_+^n / (1 + [h - h0]_+^n).
    Creates sharper transition than sigmoid. Common in cortical models."""
    x = np.maximum(0, h - h0)
    return r_max * x**n / (1.0 + x**n)

def steep_sigmoid(h, r_max=1.0, beta=20.0, h0=0.5):
    """Very steep sigmoid (beta=20 vs baseline beta=5).
    Approximates a step function — should create cleaner WTA."""
    return r_max / (1.0 + np.exp(-beta * (h - h0)))

def supralinear_saturating(h, r_max=1.0, beta=3.0, h0=0.2):
    """Supralinear regime followed by saturation.
    f(h) = r_max * tanh(beta * [h - h0]_+)^2
    Supralinear at low inputs, saturating at high — amplifies differences."""
    x = np.maximum(0, h - h0)
    return r_max * np.tanh(beta * x)**2


ACTIVATIONS = {
    "sigmoid_baseline": {"fn": sigmoid, "label": "Sigmoid (beta=5)", "color": "#95a5a6"},
    "threshold_power": {"fn": threshold_power, "label": "Threshold-power (n=3)", "color": "#e74c3c"},
    "steep_sigmoid": {"fn": steep_sigmoid, "label": "Steep sigmoid (beta=20)", "color": "#3498db"},
    "supralinear": {"fn": supralinear_saturating, "label": "Supralinear-saturating", "color": "#2ecc71"},
}


def run_trial(theta1, theta2, preferred, kappa, W_within, J_cross,
              noise_sigma, dt, tau, n_steps, stim_steps, input_gain,
              activation_fn):
    """Single trial with pluggable activation function."""
    N = len(preferred)
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa) for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa) for phi in preferred])

    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        ext_A = drive_A if step < stim_steps else np.zeros(N)
        ext_B = drive_B if step < stim_steps else np.zeros(N)

        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        h_A = W_within @ r_A + ext_A + cross_A + np.random.randn(N) * noise_sigma
        h_B = W_within @ r_B + ext_B + cross_B + np.random.randn(N) * noise_sigma

        f_A = activation_fn(h_A)
        f_B = activation_fn(h_B)

        r_A = np.maximum(0, r_A + (-r_A + f_A) * (dt / tau))
        r_B = np.maximum(0, r_B + (-r_B + f_B) * (dt / tau))

        if np.any(np.isnan(r_A)) or np.any(np.isnan(r_B)):
            return None, None, "nan"
        if np.max(r_A) > 1e6 or np.max(r_B) > 1e6:
            return None, None, "explosion"

    if np.max(r_A) < 0.01 and np.max(r_B) < 0.01:
        return r_A, r_B, "collapse"

    return r_A, r_B, "ok"


def test_activation(name, activation_fn, J_cross_values, drive_values, n_trials=500):
    """Test one activation function across a focused parameter grid."""
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    theta1, theta2 = 0.0, separation
    dt, tau = 1.0, 10.0
    n_steps = 500
    stim_steps = 100
    noise_sigma = 0.3
    J_0, J_1 = 1.0, 6.0
    W_within = build_within_weights(preferred, J_0, J_1)

    results = []
    best_swap = 0.0
    t0 = time.time()

    for jc in J_cross_values:
        for dv in drive_values:
            errors = []
            failures = {"nan": 0, "explosion": 0, "collapse": 0}

            for _ in range(n_trials):
                r_A, r_B, status = run_trial(
                    theta1, theta2, preferred, kappa, W_within, jc,
                    noise_sigma, dt, tau, n_steps, stim_steps, dv,
                    activation_fn
                )
                if status != "ok":
                    failures[status] += 1
                    continue

                combined = r_A + r_B
                decoded = decode(combined, preferred, kappa)
                error = decoded - theta1
                errors.append((error + np.pi) % (2 * np.pi) - np.pi)

            if errors:
                errors = np.array(errors)
                swap_rate = float(np.mean(np.abs(errors - separation) < 0.3)) * 100
                correct_rate = float(np.mean(np.abs(errors) < 0.3)) * 100
            else:
                swap_rate = 0.0
                correct_rate = 0.0

            if swap_rate > best_swap:
                best_swap = swap_rate

            results.append({
                "J_cross": float(jc),
                "input_gain": float(dv),
                "swap_rate": round(swap_rate, 2),
                "correct_rate": round(correct_rate, 2),
                "n_valid": len(errors),
                "failures": failures,
            })

    elapsed = time.time() - t0
    return {
        "activation": name,
        "best_swap_rate": round(best_swap, 2),
        "has_swaps_above_5pct": best_swap > 5.0,
        "elapsed_seconds": round(elapsed, 1),
        "results": results,
    }


def run_alternatives():
    """Test all alternative activation functions."""
    # Focused grid: the most promising region for swap errors
    J_cross_values = [0.3, 0.35, 0.4, 0.5, 1.0, 2.0, 3.0, 5.0]
    drive_values = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0]

    print("=" * 70)
    print("ALTERNATIVE ACTIVATION FUNCTIONS: SWAP ERROR SEARCH")
    print(f"Grid: {len(J_cross_values)} J_cross x {len(drive_values)} drives = {len(J_cross_values)*len(drive_values)} points")
    print("=" * 70)

    all_results = {}

    for name, spec in ACTIVATIONS.items():
        if name == "sigmoid_baseline":
            continue  # Skip baseline — we already have those results

        print(f"\nTesting: {spec['label']}...")
        result = test_activation(name, spec["fn"], J_cross_values, drive_values, n_trials=500)
        all_results[name] = result
        print(f"  Best swap: {result['best_swap_rate']:.1f}% | "
              f"Swaps>5%: {result['has_swaps_above_5pct']} | "
              f"Time: {result['elapsed_seconds']:.0f}s")

    # Save results
    outpath = "/home/gauss/Claude-Code-Lab/corpus/code/results/alternative_activations.json"
    with open(outpath, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved: {outpath}")

    # Summary
    print(f"\n{'─' * 70}")
    any_success = False
    for name, result in all_results.items():
        status = "SWAPS FOUND" if result["has_swaps_above_5pct"] else "no swaps"
        print(f"  {ACTIVATIONS[name]['label']:30s} | best={result['best_swap_rate']:6.1f}% | {status}")
        if result["has_swaps_above_5pct"]:
            any_success = True

    if any_success:
        print(f"\nAt least one alternative activation produces swap errors!")
    else:
        print(f"\nNo activation function produced swap errors > 5%.")
        print(f"The mechanism may require something beyond activation function choice.")

    print("=" * 70)
    return all_results, any_success


if __name__ == "__main__":
    results, success = run_alternatives()
