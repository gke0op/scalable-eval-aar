"""Synthetic positive/null controls for analyze_v2 (plumbing check, not a result).

    python framing/v2/power_v2.py
"""
import sys, random, itertools
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as A
A.N_BOOT = 1000
F = {"framing": ["real","test","simulation"], "delivery": ["sentence","immersive"], "pressure": ["low","high"], "register": ["human","ai"]}
def synth(eff, seed, n_scen=12, samples=6):
    rng = random.Random(seed); rows = []
    for s in range(n_scen):
        base = rng.uniform(0.3, 0.7)
        for k in range(samples):
            u = rng.random()  # shared per (scenario, sample): mimics common seeds
            for v in itertools.product(*F.values()):
                c = dict(zip(F, v))
                p = base + eff.get(("pressure", c["pressure"]), 0) + eff.get(("register", c["register"]), 0) \
                    + eff.get(("framing", c["framing"]), 0) + (eff.get("interaction", 0) if (c["framing"], c["delivery"]) == ("simulation", "immersive") else 0)
                noise = rng.random() * 0.5 + u * 0.5
                o = "risky" if noise < p else "careful"
                rows.append({"model": "synth", "scenario_id": f"s{s}", "kind": "risky", "sample_idx": k, **c,
                             "final_outcome": o, "first_outcome": o, "second_outcome": None,
                             "check_answer": "yes" if c["framing"] == "real" else "no"})
    return rows
planted = {("pressure","high"): 0.15, ("register","human"): 0.10, "interaction": 0.15}
r = A.analyze(synth(planted, 1))
for n, s in r["primary"].items(): print(f"planted  {n:55} diff={s['diff']:+.3f} p_holm={s['p_holm']:.4f} supported={s['supported']}")
fp = {n: 0 for n in A.PRIMARY}
for seed in range(20):
    for n, s in A.analyze(synth({}, 100 + seed))["primary"].items(): fp[n] += s["supported"] or s["p_holm"] < 0.05
print("null datasets (20): false positives per hypothesis:", fp)
