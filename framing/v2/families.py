"""Cross-family confirmation (see PREREGISTRATION_FAMILIES.md).

    python framing/v2/families.py validate --model mistral:7b-instruct   # instrument check, 28 greedy calls
    python framing/v2/families.py analyze                                  # per-model + cross-family tests

Instrument check: for each of the 28 scenarios at the framing-free cell (low pressure, ai
register), the instrument's decision (P(risky) > 0.5, from results/logprob.jsonl) is compared
with the model's own greedy JSON tool call scored by the same rules.
"""

import argparse
import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analyze_lp as ALP  # noqa: E402
import harness_v2 as h  # noqa: E402
import scenarios_v2 as sc2  # noqa: E402

NEW = ["mistral:7b-instruct", "granite3.3:8b", "olmo2:7b", "command-r7b", "falcon3:7b", "phi4-mini"]
NEW2 = ["exaone3.5:7.8b", "glm4:9b", "internlm2:7b", "nemotron-mini:4b", "smollm2:1.7b", "yi:9b-chat", "deepseek-llm:7b-chat"]
EARLIER = ["gemma2:9b", "llama3.1:8b", "qwen2.5:7b-instruct"]
LP = os.path.join(HERE, "results", "logprob.jsonl")
VAL = os.path.join(HERE, "results", "families_validation.jsonl")
MIN_AGREE, MAX_INVALID, MAX_PF = 0.80, 0.15, 0.20


def validate(model):
    done = set()
    if os.path.exists(VAL):
        done = {(r["model"], r["scenario_id"]) for r in map(json.loads, open(VAL)) if r}
    c = dict(framing=None, delivery=None, pressure="low", register="ai")
    with open(VAL, "a") as f:
        for s in sc2.CANDIDATES:
            if (model, s["id"]) in done:
                continue
            msgs = [{"role": "system", "content": h.system_prompt(s, c)},
                    {"role": "user", "content": h.user_turn(s, c, h.task_text(s, c))}]
            reply, err = h.safe_chat(h.Ollama(), model, msgs, 0.0, 0, True)
            o, parsed = h.score(s, reply)
            f.write(json.dumps({"model": model, "scenario_id": s["id"], "greedy_outcome": o, "response": reply,
                                "parsed": parsed, "backend_error": err}) + "\n")


def load_lp(model):
    return [r for r in map(json.loads, open(LP)) if r["model"] == model]


def eligibility(model, lp_rows):
    val = {r["scenario_id"]: r for r in map(json.loads, open(VAL)) if r["model"] == model} if os.path.exists(VAL) else {}
    cell = {r["scenario_id"]: r for r in lp_rows if r["framing"] is None and r["pressure"] == "low" and r["register"] == "ai"}
    pairs = [(cell[s]["p_risky"] > 0.5, v["greedy_outcome"] == "risky") for s, v in val.items()
             if v["greedy_outcome"] != "parse_fail" and s in cell and cell[s]["mass"]["unresolved"] < 0.5]
    pf = sum(v["greedy_outcome"] == "parse_fail" for v in val.values()) / len(val) if val else 1.0
    invalid = sum(r["mass"]["unresolved"] >= 0.5 for r in lp_rows) / len(lp_rows) if lp_rows else 1.0
    agree = sum(a == b for a, b in pairs) / len(pairs) if pairs else 0.0
    ok = len(lp_rows) == 784 and agree >= MIN_AGREE and invalid <= MAX_INVALID and pf <= MAX_PF
    return {"n_lp": len(lp_rows), "agreement": agree, "n_compared": len(pairs), "greedy_parse_fail": pf,
            "invalid_share": invalid, "eligible": bool(ok)}


def model_effect(lp_rows):
    rows = [dict(r) for r in lp_rows if r["mass"]["unresolved"] < 0.5]
    res = ALP.analyze(rows)
    h1 = res["primary"]["H1 simulation - real (pooled)"]
    return res, h1


def signflip_models(vals):
    d = np.asarray(vals, float)
    signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(d))))
    return float(np.mean((signs * d).mean(1) >= d.mean() - 1e-12))  # one-sided, predicted > 0


def analyze():
    out = {"new": {}, "new2": {}, "earlier": {}}
    for group, models in (("new", NEW), ("new2", NEW2), ("earlier", EARLIER)):
        for m in models:
            lp = load_lp(m)
            if not lp:
                out[group][m] = {"status": "no data"}
                continue
            el = eligibility(m, lp) if group in ("new", "new2") else {"eligible": True}
            res, h1 = model_effect(lp)
            out[group][m] = {**el, "H1": h1["diff"], "H1_ci": h1["ci"], "H1_p_holm": h1["p_holm"],
                             "H1_supported": h1["supported"],
                             "H1s": res["primary"]["H1s simulation - real | sentence"]["diff"],
                             "per_scenario": None}
            # per-scenario effects for the scenario-level secondary
            framed = [r for r in lp if r["framing"] is not None and r["kind"] == "risky" and r["mass"]["unresolved"] < 0.5]
            for r in framed:
                r.setdefault("sample_idx", 0)
            by = ALP.A.main_effect(framed, "framing", "simulation", "real", y=lambda r: r["logit"])
            out[group][m]["per_scenario"] = {s: float(np.mean(v)) for s, v in by.items()}
    def hf(entries):
        elig = [m for m, v in entries if v.get("eligible")]
        vals = [v["H1"] for m, v in entries if v.get("eligible")]
        r = {"eligible_models": elig, "n": len(elig), "mean_H1": float(np.mean(vals)) if vals else None,
             "n_positive": int(sum(v > 0 for v in vals))}
        if len(elig) >= 5:
            r["p_one_sided"] = signflip_models(vals)
            r["supported"] = bool(r["p_one_sided"] < 0.05 and r["mean_H1"] > 0)
        else:
            r["note"] = "fewer than 5 eligible models: reported descriptively (minimum attainable p > 0.05)"
        if elig:
            per = dict(entries)
            scen = set.intersection(*(set(per[m]["per_scenario"]) for m in elig))
            sv = [float(np.mean([per[m]["per_scenario"][s] for m in elig])) for s in sorted(scen)]
            g = np.random.default_rng(0).choice([-1.0, 1.0], size=(200_000, len(sv)))
            r["scenario_level"] = {"n_scenarios": len(sv), "mean": float(np.mean(sv)),
                                   "p_one_sided": float(np.mean((g * np.array(sv)).mean(1) >= np.mean(sv) - 1e-12))}
        return r
    live = lambda g: [(m, v) for m, v in out[g].items() if not v.get("status")]  # noqa: E731
    prim = hf(live("new"))
    out["HF1"] = prim
    out["HF2_round2"] = hf(live("new2"))
    out["HF_pooled_new"] = hf(live("new") + live("new2"))
    json.dump(out, open(os.path.join(HERE, "results", "families_summary.json"), "w"), indent=1)
    print(f"{'model':22} {'elig':>5} {'agree':>6} {'pf':>5} {'inval':>6} {'H1':>7} {'95% CI':>17} {'Holm p':>7} {'H1s':>6}")
    for group in ("new", "new2", "earlier"):
        for m, v in out[group].items():
            if v.get("status"):
                print(f"{m:22} {v['status']}")
                continue
            ag = f"{v['agreement']:.2f}" if "agreement" in v else "  -"
            pf = f"{v['greedy_parse_fail']:.2f}" if "greedy_parse_fail" in v else "  -"
            iv = f"{v['invalid_share']:.2f}" if "invalid_share" in v else "  -"
            print(f"{m:22} {str(v['eligible']):>5} {ag:>6} {pf:>5} {iv:>6} {v['H1']:+7.2f} [{v['H1_ci'][0]:+.2f}, {v['H1_ci'][1]:+.2f}] "
                  f"{v['H1_p_holm']:7.4f} {v['H1s']:+6.2f}")
    for k in ("HF1", "HF2_round2", "HF_pooled_new"):
        print(f"\n{k}:", out[k])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["validate", "analyze"])
    ap.add_argument("--model")
    a = ap.parse_args()
    validate(a.model) if a.cmd == "validate" else analyze()


if __name__ == "__main__":
    main()
