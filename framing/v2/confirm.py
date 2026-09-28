"""Sampling confirmation of log-prob predictions (see CONFIRMATION.md).

    python framing/v2/confirm.py select            # -> confirm_cells.json
    python framing/v2/confirm.py run --model gemma2:9b
    python framing/v2/confirm.py analyze --model gemma2:9b
"""

import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness_v2 as h  # noqa: E402
import logprob as L  # noqa: E402
import scenarios_v2 as sc2  # noqa: E402

MODELS = ["gemma2:9b", "llama3.1:8b"]
N_PAIRS, SAMPLES, TEMP = 10, 20, 1.0
SEL = os.path.join(HERE, "confirm_cells.json")
OUT = os.path.join(HERE, "results", "confirm.jsonl")
IDX = {s["id"]: i for i, s in enumerate(sc2.CANDIDATES)}


def select():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "results", "logprob.jsonl")) if l.strip()]
    cell = {(r["model"], r["scenario_id"], r["framing"], r["delivery"]): r["p_risky"] for r in rows
            if r["kind"] == "risky" and r["pressure"] == "low" and r["register"] == "ai" and r["framing"]}
    out = {}
    for m in MODELS:
        pairs = []
        for s in sc2.CANDIDATES:
            if s["kind"] != "risky":
                continue
            for d in ("sentence", "immersive"):
                pr, ps = cell.get((m, s["id"], "real", d)), cell.get((m, s["id"], "simulation", d))
                if pr is None or ps is None or pr != pr or ps != ps:
                    continue
                if max(pr, ps) >= 0.05 and min(pr, ps) <= 0.95:
                    pairs.append({"scenario_id": s["id"], "delivery": d, "p_real": pr, "p_sim": ps, "pred_delta": ps - pr})
        pairs.sort(key=lambda p: (-abs(p["pred_delta"]), IDX[p["scenario_id"]]))
        out[m] = {"eligible": len(pairs), "selected": pairs[:N_PAIRS]}
        print(f"{m}: eligible {len(pairs)}, selected {len(out[m]['selected'])}")
        for p in out[m]["selected"]:
            print(f"   {p['scenario_id']:28} {p['delivery']:9} P_real={p['p_real']:.3f} P_sim={p['p_sim']:.3f} Δp={p['pred_delta']:+.3f}")
    json.dump(out, open(SEL, "w"), indent=1)


def run(model):
    sel = json.load(open(SEL))[model]["selected"]
    by = {s["id"]: s for s in sc2.CANDIDATES}
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            r = json.loads(line)
            done.add((r["model"], r["scenario_id"], r["framing"], r["delivery"], r["sample_idx"]))
    with open(OUT, "a") as f:
        for p in sel:
            s = by[p["scenario_id"]]
            for k in range(SAMPLES):
                seed = 40_000 + 1000 * IDX[s["id"]] + k
                for fr in ("real", "simulation"):
                    if (model, s["id"], fr, p["delivery"], k) in done:
                        continue
                    c = dict(framing=fr, delivery=p["delivery"], pressure="low", register="ai")
                    msgs = [{"role": "system", "content": h.system_prompt(s, c)},
                            {"role": "user", "content": h.user_turn(s, c, h.task_text(s, c))}]
                    t0 = time.time()
                    reply, err = h.safe_chat(h.Ollama(), model, msgs, TEMP, seed, True)
                    o, parsed = h.score(s, reply)
                    f.write(json.dumps({"model": model, "scenario_id": s["id"], "framing": fr, "delivery": p["delivery"],
                                        "sample_idx": k, "seed": seed, "temperature": TEMP, "response": reply,
                                        "parsed": parsed, "outcome": o, "backend_error": err,
                                        "latency_s": round(time.time() - t0, 2)}) + "\n")
                    f.flush()
            L.unload(model)
            print(f"  {p['scenario_id']}/{p['delivery']} done", flush=True)


def analyze(model):
    sel = json.load(open(SEL))[model]["selected"]
    rows = [json.loads(l) for l in open(OUT) if l.strip()]
    rows = [r for r in rows if r["model"] == model]
    res, pred, obs, cal = [], [], [], []
    for p in sel:
        rates = {}
        for fr in ("real", "simulation"):
            v = [r["outcome"] == "risky" for r in rows if r["scenario_id"] == p["scenario_id"]
                 and r["delivery"] == p["delivery"] and r["framing"] == fr and r["outcome"] != "parse_fail"]
            rates[fr] = (sum(v) / len(v)) if v else float("nan")
            rates[fr + "_n"] = len(v)
        d = rates["simulation"] - rates["real"]
        res.append({**p, "rate_real": rates["real"], "rate_sim": rates["simulation"], "obs_delta": d,
                    "n_real": rates["real_n"], "n_sim": rates["simulation_n"]})
        pred.append(p["pred_delta"])
        obs.append(d)
        cal += [abs(p["p_real"] - rates["real"]), abs(p["p_sim"] - rates["simulation"])]
    pred, obs = np.array(pred), np.array(obs)
    r_obs = float(np.corrcoef(pred, obs)[0, 1])
    perms = np.array([np.corrcoef(pred, obs[list(q)])[0, 1] for q in itertools.permutations(range(len(obs)))])
    p_perm = float(np.mean(perms >= r_obs - 1e-12))
    agree = int(sum(np.sign(a) == np.sign(b) and b != 0 for a, b in zip(pred, obs)))
    rng = np.random.default_rng(0)
    scen = sorted({x["scenario_id"] for x in res})
    boots = []
    for _ in range(10_000):
        pick = rng.choice(len(scen), len(scen))
        vals = [x["obs_delta"] for i in pick for x in res if x["scenario_id"] == scen[i]]
        boots.append(np.mean(vals))
    pf = sum(r["outcome"] == "parse_fail" for r in rows) / len(rows)
    out = {"model": model, "pairs": res, "pearson_r": r_obs, "p_perm_one_sided": p_perm, "sign_agree": agree,
           "confirmed": bool(r_obs > 0 and p_perm < 0.05 and agree >= 8), "calibration_mae": float(np.mean(cal)),
           "pooled_obs_delta": float(np.mean(obs)), "pooled_ci": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
           "pooled_pred_delta": float(np.mean(pred)), "parse_fail": pf, "n_rows": len(rows)}
    tag = model.replace(":", "_").replace(".", "_")
    json.dump(out, open(os.path.join(HERE, "results", f"confirm_{tag}.json"), "w"), indent=1)
    print(f"{model}: rows={len(rows)} parse_fail={pf:.1%}")
    print(f"{'scenario':28} {'delivery':9} {'P_real':>7} {'rate':>5} {'P_sim':>7} {'rate':>5} {'pred Δ':>7} {'obs Δ':>6}")
    for x in res:
        print(f"{x['scenario_id']:28} {x['delivery']:9} {x['p_real']:7.3f} {x['rate_real']:5.2f} {x['p_sim']:7.3f} "
              f"{x['rate_sim']:5.2f} {x['pred_delta']:+7.3f} {x['obs_delta']:+6.2f}")
    print(f"\nPearson r(pred, obs) = {r_obs:.2f}, one-sided permutation p = {p_perm:.4f}; sign agreement {agree}/{len(res)}")
    print(f"pooled obs Δ = {out['pooled_obs_delta']:+.3f} {out['pooled_ci']} (pred {out['pooled_pred_delta']:+.3f}); "
          f"calibration MAE = {out['calibration_mae']:.3f}\nCONFIRMED: {out['confirmed']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["select", "run", "analyze"])
    ap.add_argument("--model")
    a = ap.parse_args()
    {"select": lambda: select(), "run": lambda: run(a.model), "analyze": lambda: analyze(a.model)}[a.cmd]()


if __name__ == "__main__":
    main()
