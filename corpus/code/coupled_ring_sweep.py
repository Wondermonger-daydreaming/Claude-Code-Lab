"""
Coupled Ring Attractor Parameter Sweep
=======================================
Self-contained simulation harness for mapping swap errors across
the (J_cross, drive_strength) parameter space.

Usage:
    python3 coupled_ring_sweep.py --agent-id 1 \
        --jcross-min 0.3 --jcross-max 0.6 \
        --drive-min 1.0 --drive-max 3.0 \
        --grid-j 8 --grid-d 8 --n-trials 500

Output: corpus/code/results/agent_{id}.json
"""

import argparse
import json
import sys
import time
import numpy as np
from scipy.special import i0

# ─── Model components (from swap_errors_coupled_rings.py) ───

def sigmoid(h, r_max=1.0, beta=5.0, h0=0.5):
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

def run_coupled_trial(theta1, theta2, preferred, kappa,
                      W_within, J_cross, noise_sigma,
                      dt, tau, n_steps, stim_steps, input_gain,
                      r_max, beta, h0):
    N = len(preferred)
    drive_A = input_gain * np.array([tuning_curve(theta1, phi, kappa)
                                      for phi in preferred])
    drive_B = input_gain * np.array([tuning_curve(theta2, phi, kappa)
                                      for phi in preferred])
    r_A = np.ones(N) * 0.1
    r_B = np.ones(N) * 0.1

    for step in range(n_steps):
        if step < stim_steps:
            ext_A, ext_B = drive_A, drive_B
        else:
            ext_A = np.zeros(N)
            ext_B = np.zeros(N)

        cross_A = -J_cross * np.mean(r_B)
        cross_B = -J_cross * np.mean(r_A)

        noise_A = np.random.randn(N) * noise_sigma
        h_A = W_within @ r_A + ext_A + cross_A + noise_A
        f_A = sigmoid(h_A, r_max, beta, h0)
        dr_A = (-r_A + f_A) * (dt / tau)
        r_A = np.maximum(0, r_A + dr_A)

        noise_B = np.random.randn(N) * noise_sigma
        h_B = W_within @ r_B + ext_B + cross_B + noise_B
        f_B = sigmoid(h_B, r_max, beta, h0)
        dr_B = (-r_B + f_B) * (dt / tau)
        r_B = np.maximum(0, r_B + dr_B)

        # NaN/explosion check
        if np.any(np.isnan(r_A)) or np.any(np.isnan(r_B)):
            return None, None, "nan"
        if np.max(r_A) > 1e6 or np.max(r_B) > 1e6:
            return None, None, "explosion"

    # Collapse check: both networks dead
    if np.max(r_A) < 0.01 and np.max(r_B) < 0.01:
        return r_A, r_B, "collapse"

    return r_A, r_B, "ok"


# ─── Grid sweep ───

def sweep_point(J_cross, input_gain, W_within, preferred, kappa,
                n_trials, dt, tau, n_steps, stim_steps,
                r_max, beta, h0, noise_sigma, separation):
    """Run n_trials at a single (J_cross, input_gain) point."""
    theta1, theta2 = 0.0, separation
    errors = []
    winners = {"A": 0, "B": 0, "tie": 0}
    failures = {"nan": 0, "explosion": 0, "collapse": 0}

    for _ in range(n_trials):
        r_A, r_B, status = run_coupled_trial(
            theta1, theta2, preferred, kappa,
            W_within, J_cross, noise_sigma,
            dt, tau, n_steps, stim_steps, input_gain,
            r_max, beta, h0
        )

        if status in ("nan", "explosion"):
            failures[status] += 1
            continue
        if status == "collapse":
            failures["collapse"] += 1
            continue

        # Decode from combined response
        combined = r_A + r_B
        decoded = decode(combined, preferred, kappa)
        error = decoded - theta1
        error = (error + np.pi) % (2 * np.pi) - np.pi
        errors.append(error)

        # Winner tracking
        sum_A, sum_B = np.sum(r_A), np.sum(r_B)
        if sum_A > sum_B * 1.5:
            winners["A"] += 1
        elif sum_B > sum_A * 1.5:
            winners["B"] += 1
        else:
            winners["tie"] += 1

    if len(errors) == 0:
        return {
            "J_cross": float(J_cross),
            "input_gain": float(input_gain),
            "n_valid": 0,
            "swap_rate": 0.0,
            "correct_rate": 0.0,
            "failures": failures,
            "status": "all_failed"
        }

    errors = np.array(errors)
    near_target = float(np.mean(np.abs(errors) < 0.3))
    near_nontarget = float(np.mean(np.abs(errors - separation) < 0.3))
    mean_error = float(np.mean(errors))
    std_error = float(np.std(errors))

    return {
        "J_cross": float(J_cross),
        "input_gain": float(input_gain),
        "n_valid": len(errors),
        "swap_rate": round(near_nontarget * 100, 2),
        "correct_rate": round(near_target * 100, 2),
        "mean_error": round(mean_error, 4),
        "std_error": round(std_error, 4),
        "winners": winners,
        "failures": failures,
        "status": "ok"
    }


def run_sweep(args):
    """Run the full grid sweep for one agent's region."""
    N = 48
    kappa = 2.0
    preferred = np.linspace(-np.pi, np.pi, N, endpoint=False)
    separation = np.pi / 2
    dt, tau = 1.0, 10.0
    n_steps = 500
    stim_steps = 100
    r_max, beta, h0 = 1.0, 5.0, 0.5
    noise_sigma = 0.3
    J_0, J_1 = 1.0, 6.0
    W_within = build_within_weights(preferred, J_0, J_1)

    j_values = np.linspace(args.jcross_min, args.jcross_max, args.grid_j)
    d_values = np.linspace(args.drive_min, args.drive_max, args.grid_d)

    results = []
    total = args.grid_j * args.grid_d
    count = 0
    best_swap = 0.0
    t0 = time.time()

    print(f"Agent {args.agent_id}: Sweeping J_cross=[{args.jcross_min:.2f}, {args.jcross_max:.2f}] x drive=[{args.drive_min:.1f}, {args.drive_max:.1f}]")
    print(f"  Grid: {args.grid_j}x{args.grid_d} = {total} points, {args.n_trials} trials each")

    for jc in j_values:
        for dv in d_values:
            count += 1
            result = sweep_point(
                jc, dv, W_within, preferred, kappa,
                args.n_trials, dt, tau, n_steps, stim_steps,
                r_max, beta, h0, noise_sigma, separation
            )
            results.append(result)

            if result["swap_rate"] > best_swap:
                best_swap = result["swap_rate"]

            # Retry logic: if all failed due to NaN/explosion, try with smaller dt
            if result["status"] == "all_failed":
                print(f"  [{count}/{total}] J={jc:.3f} d={dv:.1f} -> ALL FAILED, retrying dt=0.5...")
                result2 = sweep_point(
                    jc, dv, W_within, preferred, kappa,
                    args.n_trials, 0.5, tau, n_steps * 2, stim_steps * 2,
                    r_max, beta, h0, noise_sigma * 0.5, separation
                )
                if result2["status"] == "ok":
                    result2["retried"] = True
                    results[-1] = result2
                    if result2["swap_rate"] > best_swap:
                        best_swap = result2["swap_rate"]
                    print(f"           -> Retry OK: swap={result2['swap_rate']:.1f}%")
                else:
                    print(f"           -> Retry also failed")

            if count % 5 == 0 or count == total:
                elapsed = time.time() - t0
                rate = count / elapsed if elapsed > 0 else 0
                eta = (total - count) / rate if rate > 0 else 0
                print(f"  [{count}/{total}] best_swap={best_swap:.1f}% ({elapsed:.0f}s elapsed, ~{eta:.0f}s remaining)")

    elapsed = time.time() - t0

    # Summary
    swap_rates = [r["swap_rate"] for r in results if r["status"] == "ok"]
    has_swaps = any(s > 5.0 for s in swap_rates)

    output = {
        "agent_id": args.agent_id,
        "region": {
            "jcross_min": args.jcross_min,
            "jcross_max": args.jcross_max,
            "drive_min": args.drive_min,
            "drive_max": args.drive_max,
        },
        "grid": {"n_j": args.grid_j, "n_d": args.grid_d},
        "n_trials": args.n_trials,
        "elapsed_seconds": round(elapsed, 1),
        "best_swap_rate": round(best_swap, 2),
        "has_swaps_above_5pct": has_swaps,
        "n_points_total": total,
        "n_points_ok": sum(1 for r in results if r["status"] == "ok"),
        "results": results,
        "model_params": {
            "N": N, "kappa": kappa, "separation": separation,
            "dt": dt, "tau": tau, "n_steps": n_steps,
            "stim_steps": stim_steps, "r_max": r_max,
            "beta": beta, "h0": h0, "noise_sigma": noise_sigma,
            "J_0": J_0, "J_1": J_1,
            "activation": "sigmoid"
        }
    }

    outpath = f"/home/gauss/Claude-Code-Lab/corpus/code/results/agent_{args.agent_id}.json"
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nAgent {args.agent_id} DONE in {elapsed:.1f}s")
    print(f"  Best swap rate: {best_swap:.1f}%")
    print(f"  Swaps > 5%: {has_swaps}")
    print(f"  Results: {outpath}")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coupled ring attractor sweep")
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--jcross-min", type=float, required=True)
    parser.add_argument("--jcross-max", type=float, required=True)
    parser.add_argument("--drive-min", type=float, required=True)
    parser.add_argument("--drive-max", type=float, required=True)
    parser.add_argument("--grid-j", type=int, default=8)
    parser.add_argument("--grid-d", type=int, default=8)
    parser.add_argument("--n-trials", type=int, default=500)
    args = parser.parse_args()
    run_sweep(args)
