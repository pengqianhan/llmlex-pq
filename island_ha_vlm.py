#!/usr/bin/env python3
"""
Island-model pipeline for vision-LLM–guided Hybrid Automata discovery.

Steps per candidate:
1) Take HA JSON (from VLM or seed), extract numeric constants as parameters.
2) Fit parameters by minimizing simulation error vs. data.
3) Simulate with Dainarx HybridAutomata, plot prediction vs. truth, compute metrics.
4) Feed metrics + comparison image back to VLM to evolve structure (optional).

This file is a prototype orchestrator wiring together components in this repo.
Enable real VLM proposals by setting USE_VLM=True and configuring OpenRouter.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import math
import os
import re
import sys
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

# Local imports (llm + Dainarx engine)
from llmlex.fit import get_n_chi_squared_from_predictions
from llmlex.llm import call_model

# Add Dainarx_code to path for simulation
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DAINARX_DIR = os.path.join(REPO_DIR, "Dainarx_code")
if DAINARX_DIR not in sys.path:
    sys.path.insert(0, DAINARX_DIR)
from src.HybridAutomata import HybridAutomata  # type: ignore


# -----------------------------
# Utility: parameter extraction
# -----------------------------

NUM_PATTERN = re.compile(r"[-+]?\d*\.\d+(?:[eE][-+]?\d+)?|[-+]?\d+(?:[eE][-+]?\d+)?")


def _inside_index(expr: str, position: int) -> bool:
    """Return True if character at position lies inside [...] index."""
    left = expr.rfind("[", 0, position)
    right = expr.rfind("]", 0, position)
    return left != -1 and left > right


def extract_param_template(ha_json: Dict[str, Any]) -> Tuple[Dict[str, Any], List[float]]:
    """Replace numeric literals in eq/conditions/resets with placeholders {p_k}.

    Returns a template JSON (with placeholders) and an initial param vector.
    """
    auto = ha_json["automaton"]
    pvals: List[float] = []
    pcount = 0

    def subst_expr(expr: str) -> str:
        nonlocal pcount, pvals
        parts: List[str] = []
        last = 0
        for m in NUM_PATTERN.finditer(expr):
            s, e = m.span()
            if _inside_index(expr, s):
                continue
            if s > 0 and expr[s - 1].isalpha():
                # Skip digits that are part of variable names like x1
                continue
            if s >= 2 and expr[s - 2:s] == "**":
                # Keep polynomial exponents fixed (avoid NaNs for non-integer powers)
                continue
            if s >= 3 and expr[s - 3:s - 1] == "**":
                continue
            lit = expr[s:e]
            parts.append(expr[last:s])
            parts.append(f"{{p_{pcount}}}")
            try:
                pvals.append(float(lit))
            except Exception:
                pvals.append(0.0)
            pcount += 1
            last = e
        parts.append(expr[last:])
        return "".join(parts)

    tpl = json.loads(json.dumps(ha_json))  # deep copy
    # modes
    for mode in tpl["automaton"].get("mode", []):
        # eq is a single string like "x1[1] = ...,x2[1] = ..."
        eq_str = mode.get("eq", "")
        rhs_joined = []
        for part in eq_str.split(","):
            # only substitute on RHS
            if "=" in part:
                lhs, rhs = part.split("=", 1)
                rhs2 = subst_expr(rhs)
                rhs_joined.append(f"{lhs}={rhs2}")
            else:
                rhs_joined.append(subst_expr(part))
        mode["eq"] = ",".join(rhs_joined)

    # edges
    for edge in tpl["automaton"].get("edge", []):
        if "condition" in edge and isinstance(edge["condition"], str):
            edge["condition"] = subst_expr(edge["condition"])
        if "reset" in edge and isinstance(edge["reset"], dict):
            for k, vlist in edge["reset"].items():
                if isinstance(vlist, list):
                    for i, v in enumerate(vlist):
                        if isinstance(v, str) and v.strip() != "":
                            edge["reset"][k][i] = subst_expr(v)

    return tpl, pvals


def apply_params(template_json: Dict[str, Any], params: List[float]) -> Dict[str, Any]:
    """Fill {p_k} placeholders with numeric values."""
    def fill(s: str) -> str:
        # Build mapping for format
        mapping = {f"p_{i}": f"{params[i]:.12g}" for i in range(len(params))}
        return s.format(**mapping)

    j = json.loads(json.dumps(template_json))
    for mode in j["automaton"].get("mode", []):
        mode["eq"] = fill(mode["eq"]) if isinstance(mode.get("eq"), str) else mode.get("eq")
    for edge in j["automaton"].get("edge", []):
        if isinstance(edge.get("condition"), str):
            edge["condition"] = fill(edge["condition"]) 
        if isinstance(edge.get("reset"), dict):
            for k, vlist in edge["reset"].items():
                if isinstance(vlist, list):
                    edge["reset"][k] = [fill(x) if isinstance(x, str) and x else x for x in vlist]
    return j


# -----------------------------
# Simulation and scoring
# -----------------------------

def simulate_ha(ha_json: Dict[str, Any], dt: float, steps: int, init_state: Dict[str, Any]) -> np.ndarray:
    """Simulate HA and return array of shape (steps, n_vars)."""
    sys_ = HybridAutomata.from_json(ha_json["automaton"])  # type: ignore
    HybridAutomata.LoopWarning = False
    sys_.reset(deepcopy(init_state))
    out = []
    for _ in range(steps):
        x, _, _ = sys_.next(dt)
        out.append(x)
    return np.array(out)


def score_prediction(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Compute metrics per variable and aggregate."""
    assert y_true.shape == y_pred.shape
    n = y_true.shape[1]
    metrics: Dict[str, float] = {}
    rmse = 0.0
    nchis = []
    for i in range(n):
        yi = y_true[:, i]
        pi = y_pred[:, i]
        rmse_i = float(np.sqrt(np.mean((yi - pi) ** 2)))
        nch_i = get_n_chi_squared_from_predictions(np.arange(len(yi)), yi, pi)
        metrics[f"rmse_x{i+1}"] = rmse_i
        metrics[f"nchi_x{i+1}"] = nch_i
        rmse += rmse_i
        nchis.append(nch_i)
    metrics["rmse_mean"] = rmse / n
    metrics["nchi_mean"] = float(np.mean(nchis))
    return metrics


def plot_comparison(t: np.ndarray, y_true: np.ndarray, y_pred: np.ndarray, out_path: str) -> str:
    plt.figure(figsize=(8, 4))
    for i in range(y_true.shape[1]):
        plt.plot(t, y_true[:, i], label=f"x{i+1} true", lw=2)
        plt.plot(t, y_pred[:, i], "--", label=f"x{i+1} pred", lw=1.5)
    plt.xlabel("t")
    plt.ylabel("state")
    plt.legend(ncol=max(1, y_true.shape[1]))
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# -----------------------------
# VLM proposal (stub/optional)
# -----------------------------

def vlm_propose(client: Any, model: str, base64_img: str, current_json: Dict[str, Any], metrics: Dict[str, float]) -> Dict[str, Any]:
    """Ask VLM to refine HA JSON based on comparison image + metrics.
    Returns a parsed JSON dict. Caller should validate.
    """
    system_prompt = (
        "You are a hybrid automata architect. You receive a comparison plot and metrics. "
        "Propose an improved automaton JSON strictly in the provided schema. Return ONLY JSON."
    )
    guidance = (
        "Refine dynamics/guards/resets to reduce rmse_mean and nchi_mean. "
        "Use concise arithmetic with numpy-safe functions. Avoid text commentary."
    )
    prompt = (
        "Current metrics:\n" + json.dumps(metrics, indent=2) +
        "\nCurrent JSON (automaton):\n" + json.dumps(current_json["automaton"], indent=2)
    )
    resp = call_model(client, model, base64_img, prompt, system_prompt=system_prompt + "\n" + guidance)
    # Extract JSON from response
    content = resp.choices[0].message.content  # type: ignore[attr-defined]
    try:
        # Some models return code blocks; strip them
        s = content.strip()
        if s.startswith("```"):
            s = s.strip("`\n")
            s = re.sub(r"^json\n", "", s)
        out = json.loads(s)
        if "automaton" not in out:
            out = {"automaton": out}
        return out
    except Exception:
        raise RuntimeError("Failed to parse JSON from VLM response")


# -----------------------------
# Data loading & preprocessing
# -----------------------------

def fit_periodic_input(t: np.ndarray, u: np.ndarray) -> Tuple[str, Dict[str, Any]]:
    """Fit a simple periodic function u(t) ≈ a*cos(ωt) + b*sin(ωt) + c."""
    if t.size < 3:
        mean_val = float(np.mean(u)) if u.size else 0.0
        return f"{mean_val:.6g}", {"coeffs": [mean_val], "omega": 0.0, "freq": 0.0}

    dt = float(t[1] - t[0]) if t.size > 1 else 1.0
    centered = u - np.mean(u)
    spectrum = np.fft.rfft(centered)
    freqs = np.fft.rfftfreq(u.size, dt)
    if len(freqs) <= 1:
        mean_val = float(np.mean(u))
        return f"{mean_val:.6g}", {"coeffs": [mean_val], "omega": 0.0, "freq": 0.0}

    amps = np.abs(spectrum)
    idx = int(np.argmax(amps[1:]) + 1)  # skip zero frequency
    freq = float(freqs[idx])
    omega = 2.0 * math.pi * freq

    basis = np.column_stack([
        np.cos(omega * t),
        np.sin(omega * t),
        np.ones_like(t),
    ])
    coeffs, *_ = np.linalg.lstsq(basis, u, rcond=None)
    coeffs = coeffs.astype(float)

    terms: List[str] = []
    if abs(coeffs[0]) > 1e-6:
        terms.append(f"{coeffs[0]:.6g} * cos({omega:.6g} * t)")
    if abs(coeffs[1]) > 1e-6:
        terms.append(f"{coeffs[1]:.6g} * sin({omega:.6g} * t)")
    if abs(coeffs[2]) > 1e-6 or not terms:
        terms.append(f"{coeffs[2]:.6g}")

    expr = " + ".join(terms)
    info = {
        "coeffs": coeffs.tolist(),
        "omega": omega,
        "freq": freq,
        "residual_norm": float(np.linalg.norm(basis @ coeffs - u) / math.sqrt(u.size)),
    }
    return expr, info


def load_duffing_npz(
    path: str,
    dt_override: float | None = None,
    steps: int | None = None,
    stride: int = 1,
) -> Tuple[np.ndarray, np.ndarray, float, Dict[str, Any], Dict[str, Any]]:
    """Load Duffing dataset (state & input) and prepare time series and init state."""
    with np.load(path) as data:
        state_raw = np.array(data["state"], dtype=float)  # shape (1, N)
        input_raw = np.array(data["input"], dtype=float)
        mode_seq = np.array(data["mode"], dtype=int)
    # print("state_raw.shape: ", state_raw.shape, "input_raw.shape: ", input_raw.shape, "mode_seq.shape: ", mode_seq.shape)
    # (1, 10001) (1, 10001) (10001,) for duffing

    total_steps = state_raw.shape[1]
    if steps is not None:
        total_steps = min(total_steps, steps)

    base_dt = dt_override if dt_override is not None else 0.001 # default 0.001
    stride = max(1, int(stride)) # default 5

    state_clipped = state_raw[:, :total_steps]
    input_clipped = input_raw[:, :total_steps]

    state = state_clipped[:, ::stride]
    input_series = input_clipped[:, ::stride]

    steps_used = state.shape[1]
    dt_effective = base_dt * stride
    t = np.arange(steps_used, dtype=float) * dt_effective
    y = state.T  # (steps, n_vars)
    u = input_series[0]

    input_expr, input_info = fit_periodic_input(t, u)
    dx0 = (state_clipped[0, 1] - state_clipped[0, 0]) / base_dt if state_clipped.shape[1] > 1 else 0.0
    init_state = {
        "mode": int(mode_seq[0]) if mode_seq.size else 1,
        "x": [float(state_clipped[0, 0]), float(dx0)],
        "u": input_expr,
    }

    info = {
        "input_expr": input_expr,
        "input_fit": input_info,
        "dt_base": base_dt,
        "dt_effective": dt_effective,
        "stride": stride,
        "steps_used": steps_used,
        "path": path,
        "input_series": u.copy(),
    }
    return t, y, dt_effective, init_state, info


# -----------------------------
# Evolutionary islands
# -----------------------------

@dataclass
class Candidate:
    json: Dict[str, Any]
    tpl: Dict[str, Any]
    p0: List[float]
    params: List[float]
    metrics: Dict[str, float]
    plot_path: str


def fit_params(tpl: Dict[str, Any], p0: List[float], dt: float, t: np.ndarray, y: np.ndarray, init_state: Dict[str, Any], max_iter: int = 80) -> Tuple[List[float], Dict[str, float]]:
    """Simple Nelder-Mead over parameters with HA simulation as objective."""
    from scipy.optimize import minimize

    def objective(p: np.ndarray) -> float:
        j = apply_params(tpl, list(p))
        try:
            y_pred = simulate_ha(j, dt, len(t), init_state)
        except Exception:
            return 1e6  # infeasible
        m = score_prediction(y, y_pred)
        # primary objective: mean n-chi + small rmse
        return float(m["nchi_mean"] + 0.05 * m["rmse_mean"]) 

    res = minimize(objective, np.array(p0, dtype=float), method="Nelder-Mead", options={"maxiter": max_iter, "xatol": 1e-3, "fatol": 1e-3})
    p_opt = list(res.x)
    j_opt = apply_params(tpl, p_opt)
    y_pred = simulate_ha(j_opt, dt, len(t), init_state)
    metrics = score_prediction(y, y_pred)
    return p_opt, metrics


def evaluate_candidate(ha_json: Dict[str, Any], dt: float, t: np.ndarray, y: np.ndarray, init_state: Dict[str, Any], out_dir: str) -> Candidate:
    tpl, p0 = extract_param_template(ha_json)
    params, metrics = fit_params(tpl, p0, dt, t, y, init_state)
    j_fit = apply_params(tpl, params)
    y_pred = simulate_ha(j_fit, dt, len(t), init_state)
    plot_path = plot_comparison(t, y, y_pred, os.path.join(out_dir, "compare.png"))
    return Candidate(json=j_fit, tpl=tpl, p0=p0, params=params, metrics=metrics, plot_path=plot_path)


def evolve_islands(
    seed_json: Dict[str, Any],
    t: np.ndarray,
    y: np.ndarray,
    dt: float,
    init_state: Dict[str, Any],
    num_islands: int = 3,
    pop_size: int = 3,
    generations: int = 4,
    migrate_every: int = 2,
    use_vlm: bool = False,
    client: Any = None,
    model: str = "openai/gpt-5-nano-2025-08-07",
    work_dir: str = "build/islands_run",
) -> Dict[str, Any]:
    os.makedirs(work_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(work_dir, timestamp)
    os.makedirs(run_dir, exist_ok=True)

    # Initialize population: replicate seed
    islands: List[List[Candidate]] = []
    for i in range(num_islands):
        island_dir = os.path.join(run_dir, f"island_{i}")
        os.makedirs(island_dir, exist_ok=True)
        island = []
        for j in range(pop_size):
            cand_dir = os.path.join(island_dir, f"gen0_cand{j}")
            os.makedirs(cand_dir, exist_ok=True)
            c = evaluate_candidate(seed_json, dt, t, y, init_state, cand_dir)
            island.append(c)
        islands.append(island)

    def select_best(island: List[Candidate]) -> Candidate:
        return sorted(island, key=lambda c: c.metrics["nchi_mean"]) [0]

    # Evolution
    for gen in range(1, generations + 1):
        for i in range(num_islands):
            base = select_best(islands[i])
            new_island: List[Candidate] = [base]  # elitism
            for j in range(1, pop_size):
                cand_dir = os.path.join(run_dir, f"island_{i}", f"gen{gen}_cand{j}")
                os.makedirs(cand_dir, exist_ok=True)

                # Variation
                if use_vlm and client is not None:
                    img_b64 = image_to_base64(base.plot_path)
                    try:
                        proposal = vlm_propose(client, model, img_b64, base.json, base.metrics)
                    except Exception:
                        proposal = base.json
                else:
                    # Local numeric jitter on parameters (no structural change)
                    proposal = json.loads(json.dumps(base.json))
                    # multiply small noise into numeric constants via template mechanism
                    tpl_loc, p0_loc = extract_param_template(proposal)
                    noise = np.random.normal(scale=0.1, size=len(p0_loc))
                    params_loc = list((np.array(p0_loc) * (1.0 + noise)).astype(float))
                    proposal = apply_params(tpl_loc, params_loc)

                # Evaluate
                cand = evaluate_candidate(proposal, dt, t, y, init_state, cand_dir)
                new_island.append(cand)
            islands[i] = new_island

        # Migration
        if migrate_every > 0 and gen % migrate_every == 0 and num_islands > 1:
            bests = [select_best(island) for island in islands]
            # ring migration: send best i to island (i+1)
            for i in range(num_islands):
                j = (i + 1) % num_islands
                islands[j].append(bests[i])

    # Return best overall
    all_cands = [c for island in islands for c in island]
    best = sorted(all_cands, key=lambda c: c.metrics["nchi_mean"]) [0]
    # Persist
    with open(os.path.join(run_dir, "best_automaton.json"), "w", encoding="utf-8") as f:
        json.dump(best.json, f, indent=2, ensure_ascii=False)
    return best.json


# -----------------------------
# CLI
# -----------------------------

def default_seed_json() -> Dict[str, Any]:
    """Seed automaton resembling a two-mode Duffing oscillator."""
    return {
        "automaton": {
            "var": "x",
            "input": "u",
            "mode": [
                {
                    "id": 1,
                    "eq": "x[2] = u - 0.45 * x[1] + 0.9 * x[0] - 1.0 * x[0] ** 3",
                },
                {
                    "id": 2,
                    "eq": "x[2] = u - 0.25 * x[1] + 0.8 * x[0] - 0.6 * x[0] ** 3",
                },
            ],
            "edge": [
                {
                    "direction": "1 -> 2",
                    "condition": "abs(x) <= 1.0",
                    "reset": {"x": ["", "x[1] * 0.95"]},
                },
                {
                    "direction": "2 -> 1",
                    "condition": "abs(x) >= 1.3",
                    "reset": {"x": ["", "x[1] * 0.95"]},
                },
            ],
        }
    }


def main():
    p = argparse.ArgumentParser(description="VLM-guided islands for Hybrid Automata")
    p.add_argument("--use-vlm", action="store_true", help="Enable VLM proposals (requires API key)")
    p.add_argument("--model", default="openai/gpt-5-nano-2025-08-07", help="Vision model id")
    p.add_argument("--data", default="data_duffing/test_data0.npz", help="Path to NPZ file containing state/input")
    p.add_argument("--dt", type=float, default=None, help="Override base dt (default 0.001)")
    p.add_argument("--islands", type=int, default=3)
    p.add_argument("--pop", type=int, default=3)
    p.add_argument("--gens", type=int, default=4)
    p.add_argument("--migrate", type=int, default=2)
    p.add_argument("--steps", type=int, default=None, help="Number of time steps to use (default all)")
    p.add_argument("--stride", type=int, default=5, help="Temporal down-sampling factor")
    args = p.parse_args()

    # Data
    t, y, dt_eff, init_state, data_info = load_duffing_npz(
        args.data,
        dt_override=args.dt,
        steps=args.steps,
        stride=args.stride,
    )
    print("Loaded data from", data_info["path"])
    print(f"  steps used: {data_info['steps_used']} (stride={data_info['stride']})")
    print(f"  dt_effective: {data_info['dt_effective']}")
    print(f"  fitted input expression: u(t) = {data_info['input_expr']}")

    # Seed HA
    seed = default_seed_json()

    # Optional VLM client
    client = None
    if args.use_vlm:
        import openai
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")
        client = openai.OpenAI(base_url=base_url, api_key=api_key)

    best = evolve_islands(
        seed, t, y, dt_eff, init_state,
        num_islands=args.islands,
        pop_size=args.pop,
        generations=args.gens,
        migrate_every=args.migrate,
        use_vlm=args.use_vlm,
        client=client,
        model=args.model,
    )
    print("Best automaton saved. Summary:\n", json.dumps(best, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
