#!/usr/bin/env python3
"""
Threshold robustness analysis for swap error classification.

Reviewer concern: the 0.3 rad threshold is arbitrary.
This script re-runs a focused subset of simulations and classifies
with multiple thresholds (0.2, 0.3, 0.4, 0.5 rad) to show that
qualitative features (onset location, valley, cliff) are robust.

Strategy: run at 16 J_cross values × 2 drive values × 200 trials,
save raw decoded errors, classify at all thresholds post-hoc.
Total: 6,400 trials (~15 min on single core).
"""

import numpy as np
from scipy.special import i0
import json
import time
import sys

# ═══════════════════════════════════════════════════════════════════
# MODEL (identical to coupled_ring_sweep.py)
# ═══════════════════════════════════════════════════════════════════

N = 48
J_0, J_1 = 1.0, 6.0
KAPPA = 2.0
R_MAX, BETA, H0 = 1.0, 5.0, 0.5
DT, TAU = 1.0, 10.0
N_STEPS, STIM_STEPS = 500, 100
NOISE_SIGMA = 0.3
SEPARATION = np.pi / 2


def sigmoid(h, r_max=R_MAX, beta=BETA, h0=H0):
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


def run_coupled_trial(theta1, theta2, preferred, W_within, J_cross,
                      input_gain):
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, KAPPA)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, KAPPA)
                                      for phi in preferred])
    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(N_STEPS):
        if step < STIM_STEPS:
            ext_A, ext_B = drive_A, drive_B
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        noise_A = np.random.randn(N) * NOISE_SIGMA
        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        r_A = np.maximum(0, r_A + (-r_A + sigmoid(h_A)) * (DT / TAU))

        noise_B = np.random.randn(N) * NOISE_SIGMA
        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        r_B = np.maximum(0, r_B + (-r_B + sigmoid(h_B)) * (DT / TAU))

        if np.any(np.isnan(r_A)) or np.any(np.isnan(r_B)):
            return None
        if np.max(r_A) > 1e6 or np.max(r_B) > 1e6:
            return None

    if np.max(r_A) < 0.01 and np.max(r_B) < 0.01:
        return None

    return r_A + r_B  # combined response


# ═══════════════════════════════════════════════════════════════════
# SWEEP
# ═══════════════════════════════════════════════════════════════════

# J_cross values: dense near onset (0.15-0.5) + sparse at higher values
J_CROSS_VALUES = np.sort(np.unique(np.concatenate([
    np.array([0.10, 0.15, 0.20, 0.22, 0.25, 0.28, 0.30, 0.35]),
    np.array([0.40, 0.50, 0.75, 1.0, 1.2, 1.5, 2.0, 3.0]),
])))

DRIVE_VALUES = [3.0, 5.0]  # moderate and strong
N_TRIALS = 200
THRESHOLDS = [0.2, 0.3, 0.4, 0.5]  # rad


def main():
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    W_within = build_within_weights(preferred, J_0, J_1)

    theta1, theta2 = 0.0, SEPARATION

    results = []
    total_points = len(J_CROSS_VALUES) * len(DRIVE_VALUES)
    t0 = time.time()

    print(f"Threshold robustness analysis")
    print(f"  {len(J_CROSS_VALUES)} J_cross × {len(DRIVE_VALUES)} drives × "
          f"{N_TRIALS} trials = {total_points * N_TRIALS} total")
    print(f"  Thresholds: {THRESHOLDS} rad")
    print("=" * 70)

    for i_jc, jc in enumerate(J_CROSS_VALUES):
        for i_d, drive in enumerate(DRIVE_VALUES):
            point_idx = i_jc * len(DRIVE_VALUES) + i_d + 1
            errors = []

            for trial in range(N_TRIALS):
                combined = run_coupled_trial(
                    theta1, theta2, preferred, W_within, jc, drive
                )
                if combined is None:
                    continue
                decoded = decode(combined, preferred, KAPPA)
                error = decoded - theta1
                error = (error + np.pi) % (2 * np.pi) - np.pi
                errors.append(float(error))

            n_valid = len(errors)
            errors_arr = np.array(errors) if errors else np.array([])

            # Classify at all thresholds
            swap_rates = {}
            correct_rates = {}
            for thresh in THRESHOLDS:
                key = f"{thresh:.1f}"
                if n_valid > 0:
                    swap_rates[key] = round(
                        float(np.mean(np.abs(errors_arr - SEPARATION) < thresh)) * 100, 2
                    )
                    correct_rates[key] = round(
                        float(np.mean(np.abs(errors_arr) < thresh)) * 100, 2
                    )
                else:
                    swap_rates[key] = 0.0
                    correct_rates[key] = 0.0

            result = {
                "J_cross": float(jc),
                "drive": float(drive),
                "n_valid": n_valid,
                "swap_rates": swap_rates,
                "correct_rates": correct_rates,
            }
            results.append(result)

            elapsed = time.time() - t0
            rate = point_idx / elapsed if elapsed > 0 else 0
            eta = (total_points - point_idx) / rate if rate > 0 else 0

            sr_str = " | ".join(f"{t}r:{swap_rates[f'{t:.1f}']:5.1f}%"
                                for t in THRESHOLDS)
            print(f"  [{point_idx:3d}/{total_points}] J_x={jc:.3f} d={drive:.0f} "
                  f"n={n_valid:3d} | {sr_str} "
                  f"({elapsed:.0f}s, ETA {eta:.0f}s)")

    # Save results
    outfile = "corpus/code/results/threshold_robustness.json"
    output = {
        "thresholds": THRESHOLDS,
        "j_cross_values": J_CROSS_VALUES.tolist(),
        "drive_values": DRIVE_VALUES,
        "n_trials": N_TRIALS,
        "model_params": {
            "N": N, "J_0": J_0, "J_1": J_1, "kappa": KAPPA,
            "noise_sigma": NOISE_SIGMA, "separation": SEPARATION,
            "n_steps": N_STEPS, "stim_steps": STIM_STEPS,
        },
        "results": results,
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    with open(outfile, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {outfile}")

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY: Swap rates by threshold (drive=5.0)")
    print("=" * 70)
    print(f"  {'J_cross':>8s}", end="")
    for t in THRESHOLDS:
        print(f"  {t:.1f}rad", end="")
    print()
    print(f"  {'--------':>8s}", end="")
    for _ in THRESHOLDS:
        print(f"  ------", end="")
    print()

    for r in results:
        if r["drive"] == 5.0:
            print(f"  {r['J_cross']:8.3f}", end="")
            for t in THRESHOLDS:
                sr = r["swap_rates"][f"{t:.1f}"]
                print(f"  {sr:5.1f}%", end="")
            print()

    # Key test: onset J_cross at each threshold
    print(f"\n  Onset J_cross (where swap > 5%):")
    for t in THRESHOLDS:
        key = f"{t:.1f}"
        onset = None
        drive5_results = [r for r in results if r["drive"] == 5.0]
        for i in range(len(drive5_results) - 1):
            sr_here = drive5_results[i]["swap_rates"][key]
            sr_next = drive5_results[i + 1]["swap_rates"][key]
            if sr_here < 5.0 and sr_next >= 5.0:
                jc1 = drive5_results[i]["J_cross"]
                jc2 = drive5_results[i + 1]["J_cross"]
                onset = jc1 + (5.0 - sr_here) * (jc2 - jc1) / (sr_next - sr_here + 1e-10)
                break
        if onset:
            print(f"    {t:.1f} rad: J_cross_onset ≈ {onset:.3f}")
        else:
            print(f"    {t:.1f} rad: onset not found in range")

    print(f"\n  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
