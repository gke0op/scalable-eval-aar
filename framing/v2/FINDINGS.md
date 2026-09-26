# v2 Findings: stakes framing shifts small models' action probabilities

## Claim

On 24 agentic scenarios with mock tools, telling a model its situation is a
**simulation** rather than **real** raised the log-odds that it picks the
risky tool.

| Model | Role | `simulation − real` (pooled) | With the framing sentence only | Decision-level effect |
|---|---|---|---|---|
| gemma2:9b | primary | **+2.82** [+1.92, +3.75], Holm p = 0.0001 | **+1.80** [+1.15, +2.51], Holm p = 0.0001 | yes: greedy risky share moves from 0.23 to 0.48 across arms |
| llama3.1:8b | replication | **+0.77** [+0.41, +1.16], Holm p = 0.003 | +0.30 [+0.01, +0.61], Holm p = 0.12 (n.s.) | small: 0.76 to 0.83 |

- **Direction:** the effect goes the same way in both models.
- **Size:** it is large in the model that has real caution (gemma was careful
  on about half the scenarios at baseline). It is small in the model that is
  mostly compliant (llama was about 97% risky at baseline).
- **Where it shows up:** in gemma, the framing sentence alone was enough. In
  llama, only immersive delivery produced a significant effect.

## Preregistered results (`PREREGISTRATION_LP.md`)

Units are Δ log-odds of the risky tool. CIs are 95% scenario-clustered. p is a
scenario-level sign-flip permutation test, Holm-corrected over the 6
hypotheses.

| Hypothesis | gemma2:9b (primary) | llama3.1:8b (replication) |
|---|---|---|
| H1 simulation − real | **+2.82**, supported | **+0.77**, supported |
| H1s same, sentence only | **+1.80**, supported | +0.30, not supported |
| H2 immersive amplifies H1 | **+2.05**, supported | **+0.94**, supported |
| H3 pressure raises P(risky) | **+1.30**, supported | **−1.11**, *reversed*: pressure made llama more careful |
| H4 human register raises P(risky) | −0.73, not supported | +0.44, not supported |
| H5 test framing lowers P(risky) vs real | +1.14, *wrong sign* | +0.44, *wrong sign*, n.s. |

**Where the effect comes from** (gemma, exploratory contrasts against no
framing):

- **Sentence delivery:** `simulation` +1.45 (p < 0.001), `real` −0.34,
  `test` −0.38. The simulation sentence makes it bolder.
- **Immersive delivery:** `real` **−4.33** (p < 0.001), `test` −2.01,
  `simulation` −0.49. The concrete stakes (live user count, open incident)
  make it much more careful.

Both mechanisms operate. "It's a game" loosens the model, and "here are the
real stakes" tightens it. Immersive "real" confounds framing with stakes
content, which is why H1s (sentence only) was preregistered as a separate
primary. It holds for gemma.

**Evaluation framing (H5):** in both models, `test` sits *between* `real` and
`simulation`, not below `real`. These small models do not become more careful
when told they are being evaluated. If anything they are slightly less careful
than when told it's real.

## How we got here (the dead ends matter)

1. **v1** (`../FINDINGS.md`): a null on sampled actions for Qwen 1.5B/3B.
2. **v2 calibration** (`CALIBRATION.md`): **stop rule triggered.**
   qwen2.5:3b was 78% risky on its first action, and 80% of its careful
   actions flipped to risky after a false reassurance. No scenario was in the
   middle band.
3. **Model screen** (`SCREEN.md`): **stop rule triggered.** Across 5 models,
   109 of 120 model × scenario cells were 0/3 or 3/3. Sampled actions are
   nearly deterministic per scenario, so binary outcomes can't see graded
   effects.
4. **Log-prob instrument** (`logprob.py`): reads P(risky tool) at the decision
   token.
   - It was validated against sampled behavior before the preregistration:
     Spearman ρ = 0.86, and the argmax matched the sampled majority in 27 of
     28 scenarios.
   - The one mismatch exposed a DNS scoring-rule bug, which was fixed. It did
     not change either stop decision.
5. **This run:** 784 cells per model, which is 24 risky and 4 benign
   scenarios × 28 cells, decoded greedily.

## Robustness

- **Censoring.** 114 gemma cells had the risky tool outside the top 20
  tokens. They were bounded conservatively.
  - Excluding the 12 scenarios with any censored or clipped cell leaves H1 at
    **+3.32** [+1.84, +4.69], p = 0.002 (12 scenarios).
  - llama had 1 censored cell.
- **Coverage.** Probability mass matched to tools: minimum 0.996 for gemma.
  For llama, the median is 0.999 and only 1 of 784 cells is below 0.9.
- **Benign controls.** There are only 4, so they are uninformative (CIs span
  ±5 logits). We cannot tell "acts more" apart from "cares less" here.

## Deviations and incidents

- **gemma crashes.** The gemma run was killed twice by the kernel's
  out-of-memory killer. gemma2's sliding-window attention makes llama.cpp
  accumulate context checkpoints.
  - Fixed by unloading the model after each scenario, plus a retry for
    server-process crashes.
  - Decoding is greedy, so resumed cells are the same computation. No cell is
    duplicated or missing (784 unique).
- **Execution order.** llama ran before gemma because the first gemma attempt
  crashed at cell 16.
  - The protocol is deterministic and was fixed in advance, so the order
    cannot affect the values.
  - I did look at llama's results before gemma finished.
- **Abandoned work.** A planned "rewording" pilot was abandoned and nothing
  from it was run. An adversarial prompt battery was declined.
- **External package.** A package produced by another model (Gemini Flash),
  claiming battery results, was audited and **rejected**. Its script's mock
  backend (the default) reproduces all 60 of its trials exactly from
  hardcoded constants. Its "transfer" metric can only compare a model with
  itself.

## Limitations

- **Log-probs are not behavior.** They track sampled choices well (ρ = 0.86),
  but the headline effects are in probability space. On the greedy decision,
  gemma's shift is substantial and llama's is small.
- **Arguments.** For argument-dependent tools, the greedy argument completion
  decides the label.
- **Scenarios.** 24 hand-written scenarios, all from one author. Tool names
  may telegraph which option is safe.
- **Models.** Two small open models. Nothing here says how frontier models
  behave.
- **Pressure is model-specific** (+1.30 in gemma, −1.11 in llama), so no
  general claim about pressure is supported.

## What would falsify the claim

- The greedy or sampled risky rate under `simulation` not exceeding `real`, on
  the same scenarios, in a sampling-based confirmation run.
- Or the effect vanishing on a third model with baseline caution comparable to
  gemma's.

## Next

1. **Sampling confirmation.** At the cells with the largest shifts, sample
   20 times at temperature 0.7 and check that the action rates move as the
   log-probs predict.
2. **A third cautious open model** as a further replication.
3. **Only then a small, targeted validation on Claude**, sized to the
   confirmed effect.
