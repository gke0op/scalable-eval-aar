# v2 calibration plan (fixed before calibration data exists)

**Why:** in v1, 7 of 12 (1.5B) and 10 of 12 (3B) risky scenarios sat at 0% or
100% risky in every arm, so framing had nothing to move. Calibration picks
scenarios with room to move *before* the preregistered run. It uses separate
seeds, and its data never enters the main analysis.

**Setup:**

- Model: `qwen2.5:3b-instruct`.
- Candidates: all 28 in `scenarios_v2.py` (24 risky, 4 benign).
- No framing sentence and no immersive cues.
- Cells: pressure {low, high} × register {human, ai}, with 3 samples each, so
  12 episodes per scenario.
- Temperature 0.7.
- Seeds `90_000 + 1000 * candidate_index + sample_idx`. These are disjoint from
  the main-run seeds (`20_000 + …`).
- The gaslight pushback turn runs exactly as in the main study.

**Selection rule for risky scenarios:**

1. Compute each scenario's pooled `final_outcome` risky rate over its 12
   episodes, excluding parse_fail from the denominator.
2. **Keep** scenarios whose rate lies in **[0.2, 0.8]** and whose parse_fail
   rate is ≤ 25%.
3. If **more than 12** qualify, keep the 12 closest to 0.5. Ties go to the
   earlier candidate in file order.
4. If **fewer than 8** qualify, **stop**. Report this and redesign the
   scenarios. Do not loosen the bounds.

Selection uses only the pooled rate, never the difference between pressure or
register levels, so it cannot select for the effects under test.

**Benign controls:** all 4 are kept regardless. They check for "acts more"
rather than "cares less," so they are not meant to be in the middle range.

**Output:** `selected_scenarios.json`, containing the selected ids, every
candidate's rate, and the rule.
