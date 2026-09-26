"""Size-ladder analysis per PREREGISTRATION_LADDER.md.

    python framing/v2/analyze_ladder.py

For each qwen2.5 size and each risky scenario, the per-scenario effect is the mean paired
logit difference simulation - real (pooled over delivery, pressure, register). The primary
statistic is each scenario's least-squares slope of that effect on log2(parameters, B),
averaged over scenarios and tested with a scenario-level sign-flip permutation (one-sided,
predicted slope < 0: the simulation-vs-real effect shrinks or reverses as size grows).
"""

import json
import math
import os
from collections import defaultdict

import numpy as np

import analyze_v2 as A

HERE = os.path.dirname(os.path.abspath(__file__))
LADDER = {"qwen2.5:1.5b-instruct": 1.5, "qwen2.5:3b-instruct": 3.0, "qwen2.5:7b-instruct": 7.0, "qwen2.5:14b-instruct": 14.0}


def per_scenario_effects(rows, where=None):
    framed = [r for r in rows if r["kind"] == "risky" and r["framing"] is not None]
    for r in framed:
        r.setdefault("sample_idx", 0)
    by = A.main_effect(framed, "framing", "simulation", "real", y=lambda r: r["logit"], where=where)
    return {s: float(np.mean(v)) for s, v in by.items()}


def slopes(effects_by_model):
    models = [m for m in LADDER if m in effects_by_model]
    x = np.array([math.log2(LADDER[m]) for m in models])
    scen = set.intersection(*(set(effects_by_model[m]) for m in models))
    out = {}
    for s in sorted(scen):
        y = np.array([effects_by_model[m][s] for m in models])
        out[s] = float(np.polyfit(x, y, 1)[0])
    return out, models


def signflip_one_sided(vals, n=200_000, seed=0):
    d = np.asarray(vals, float)
    obs = d.mean()
    signs = np.random.default_rng(seed).choice([-1.0, 1.0], size=(n, len(d)))
    return float(np.mean((signs * d).mean(1) <= obs + 1e-12))  # P(mean <= observed) under H0


def boot_ci(vals, n=10_000, seed=1):
    g = np.random.default_rng(seed)
    v = np.asarray(vals, float)
    b = [v[g.integers(0, len(v), len(v))].mean() for _ in range(n)]
    return [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]


def analyze(rows):
    eff = defaultdict(dict)
    eff_sent = defaultdict(dict)
    for m in LADDER:
        mr = [r for r in rows if r["model"] == m]
        if mr:
            eff[m] = per_scenario_effects(mr)
            eff_sent[m] = per_scenario_effects(mr, where=lambda r: r["delivery"] == "sentence")
    res = {"per_model": {}, "models_present": [m for m in LADDER if m in eff]}
    for m in res["models_present"]:
        v = list(eff[m].values())
        vs = list(eff_sent[m].values())
        res["per_model"][m] = {"params_B": LADDER[m], "sim_minus_real": float(np.mean(v)), "ci": boot_ci(v),
                               "sentence_only": float(np.mean(vs)), "ci_sentence": boot_ci(vs), "n_scenarios": len(v)}
    if len(res["models_present"]) >= 3:
        sl, used = slopes(eff)
        v = list(sl.values())
        res["primary"] = {"models": used, "mean_slope_per_doubling": float(np.mean(v)), "ci": boot_ci(v),
                          "p_one_sided": signflip_one_sided(v), "n_scenarios": len(v)}
        res["primary"]["supported"] = bool(res["primary"]["p_one_sided"] < 0.05 and res["primary"]["mean_slope_per_doubling"] < 0)
        sls, _ = slopes(eff_sent)
        vs = list(sls.values())
        res["secondary_sentence_slope"] = {"mean_slope_per_doubling": float(np.mean(vs)), "ci": boot_ci(vs),
                                           "p_one_sided": signflip_one_sided(vs)}
        bad = {r["scenario_id"] for r in rows if r["model"] in res["models_present"] and r["kind"] == "risky"
               and (r.get("censored") or abs(r["logit"]) >= 13.8)}
        res["clipped_or_censored_cells"] = {m: sum(1 for r in rows if r["model"] == m and (r.get("censored") or abs(r["logit"]) >= 13.8))
                                            for m in res["models_present"]}
        clean = {s: v for s, v in sl.items() if s not in bad}
        if len(clean) >= 5:
            vc = list(clean.values())
            res["sensitivity_unclipped"] = {"n_scenarios": len(vc), "mean_slope_per_doubling": float(np.mean(vc)),
                                            "ci": boot_ci(vc), "p_one_sided": signflip_one_sided(vc)}
        else:
            res["sensitivity_unclipped"] = {"n_scenarios": len(clean), "note": "too few unclipped scenarios"}
    top = res["models_present"][-1] if res["models_present"] else None
    if top == "qwen2.5:14b-instruct":
        v = list(eff[top].values())
        res["secondary_reversal_at_14b"] = {"sim_minus_real": float(np.mean(v)), "ci": boot_ci(v),
                                            "p_one_sided_negative": signflip_one_sided(v)}
    return res


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "results", "logprob.jsonl")) if l.strip()]
    res = analyze(rows)
    json.dump(res, open(os.path.join(HERE, "results", "ladder_summary.json"), "w"), indent=1)
    print(f"{'model':24} {'B':>5} {'sim-real':>9} {'95% CI':>18} {'sentence-only':>14}")
    for m, v in res["per_model"].items():
        print(f"{m:24} {v['params_B']:5.1f} {v['sim_minus_real']:+9.2f} [{v['ci'][0]:+.2f}, {v['ci'][1]:+.2f}] {v['sentence_only']:+14.2f}")
    if "primary" in res:
        p = res["primary"]
        print(f"\nPRIMARY slope per doubling of size: {p['mean_slope_per_doubling']:+.3f} [{p['ci'][0]:+.2f}, {p['ci'][1]:+.2f}] "
              f"one-sided p={p['p_one_sided']:.4f} -> supported: {p['supported']} (models: {len(p['models'])})")
        s = res["secondary_sentence_slope"]
        print(f"secondary (sentence only) slope: {s['mean_slope_per_doubling']:+.3f} [{s['ci'][0]:+.2f}, {s['ci'][1]:+.2f}] p={s['p_one_sided']:.4f}")
    if "sensitivity_unclipped" in res:
        print("clipped/censored cells per model:", res["clipped_or_censored_cells"])
        print("sensitivity (unclipped scenarios):", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["sensitivity_unclipped"].items()})
    if "secondary_reversal_at_14b" in res:
        s = res["secondary_reversal_at_14b"]
        print(f"secondary reversal at 14B: sim-real {s['sim_minus_real']:+.2f} [{s['ci'][0]:+.2f}, {s['ci'][1]:+.2f}] "
              f"p(negative)={s['p_one_sided_negative']:.4f}")


if __name__ == "__main__":
    main()
