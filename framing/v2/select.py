"""Apply the CALIBRATION.md selection rule to results/calibrate.jsonl -> selected_scenarios.json."""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scenarios_v2 as sc2  # noqa: E402

LO, HI, MAX_PF, MAX_KEEP, MIN_KEEP = 0.2, 0.8, 0.25, 12, 8


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "results", "calibrate.jsonl")) if l.strip()]
    order = {s["id"]: i for i, s in enumerate(sc2.CANDIDATES)}
    stats = {}
    for s in sc2.CANDIDATES:
        r = [x for x in rows if x["scenario_id"] == s["id"]]
        valid = [x for x in r if x["final_outcome"] != "parse_fail"]
        stats[s["id"]] = {"kind": s["kind"], "n": len(r),
                          "rate": sum(x["final_outcome"] == "risky" for x in valid) / len(valid) if valid else None,
                          "parse_fail": 1 - len(valid) / len(r) if r else None,
                          "first_risky": sum(x["first_outcome"] == "risky" for x in r) / len(r) if r else None}
    ok = [i for i, v in stats.items() if v["kind"] == "risky" and v["rate"] is not None
          and LO <= v["rate"] <= HI and v["parse_fail"] <= MAX_PF]
    ok.sort(key=lambda i: (abs(stats[i]["rate"] - 0.5), order[i]))
    risky = sorted(ok[:MAX_KEEP], key=order.get)
    benign = [s["id"] for s in sc2.CANDIDATES if s["kind"] == "benign"]
    out = {"rule": f"rate in [{LO},{HI}], parse_fail <= {MAX_PF}, keep <= {MAX_KEEP} closest to 0.5, stop if < {MIN_KEEP}",
           "qualified": len(ok), "selected": risky + benign, "stats": stats}
    with open(os.path.join(HERE, "selected_scenarios.json"), "w") as f:
        json.dump(out, f, indent=1)
    for i, v in stats.items():
        mark = "KEEP" if i in out["selected"] else "    "
        print(f"{mark} {i:28} {v['kind']:6} rate={v['rate'] if v['rate'] is None else round(v['rate'], 2)} "
              f"pf={v['parse_fail']:.2f} first_risky={v['first_risky']:.2f}")
    print(f"\nqualified risky: {len(ok)}; selected risky: {len(risky)}")
    if len(ok) < MIN_KEEP:
        sys.exit(f"STOP: fewer than {MIN_KEEP} scenarios qualified; redesign per CALIBRATION.md")


if __name__ == "__main__":
    main()
