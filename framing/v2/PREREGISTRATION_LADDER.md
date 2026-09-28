# Preregistration: size ladder within one family (qwen2.5)

Committed before any qwen2.5 1.5B, 3B or 14B log-prob data exists. The 7B
data is being collected under `PREREGISTRATION_LP.md` Amendment 1, and **its
results had not been inspected** when this file was committed.

## Motivation

- **Our results:** in the small open models (gemma2:9b, llama3.1:8b),
  `simulation` framing *raises* P(risky tool) relative to `real`.
- **The frontier literature points the other way** (see `FINDINGS.md`,
  Related work):
  - In Anthropic's *Agentic Misalignment*, harmful behavior was more frequent
    when Claude Opus 4 *stated* it believed the scenario was real. That result
    is correlational.
  - *The Shadow Self* found slightly more risky actions under a "production"
    framing for GPT-4.1, in a small ablation.
- **Hypothesis:** the direction of the framing effect depends on capability,
  shrinking or reversing as models get larger.
- **Why a ladder:** a size ladder within one family is the cheapest local test
  of that hypothesis.

## Design

- **Models:** `qwen2.5:{1.5b,3b,7b,14b}-instruct`, from Ollama with default
  quantization. 14B is 4-bit (Q4_K_M).
- **Protocol:** the same instrument (`logprob.py`), the same 28 scenarios × 28
  cells, and greedy decoding, exactly as in `PREREGISTRATION_LP.md`.
- **Per-scenario effect:** for each model and risky scenario, the mean paired
  logit difference `simulation − real`, pooled over delivery, pressure and
  register.

## Hypotheses

- **HL1 (primary, one-sided): the effect shrinks with size.**
  - For each scenario, fit the least-squares slope of the effect on
    log2(parameters in B) across the 4 sizes.
  - HL1 predicts a **mean slope < 0**.
  - Test: scenario-level sign-flip permutation (200,000 draws), one-sided,
    α = 0.05.
- **HL1s (secondary):** the same slope using sentence delivery only (no
  immersive stakes content).
- **HL2 (secondary): reversal at 14B,** meaning `simulation − real` < 0 at 14B
  (one-sided sign-flip, reported with a CI). This would match the frontier
  direction.
- **Also reported:** the per-model `simulation − real` and sentence-only
  effects, with scenario-bootstrap CIs.

## Known issues, stated in advance

- **Ceiling effects at small sizes.** qwen2.5 at 1.5B and 3B was nearly always
  risky in earlier runs, so their logits may be clipped near +13.8. That
  compresses their framing effect toward 0 and biases the slope *upward*,
  **against** HL1. It is conservative, but it could hide a real decline.
  - Reported: the number of clipped or censored cells per model, and HL1
    recomputed on scenarios with no clipped cell at any size.
- **Quantization differs across sizes.** 1.5B, 3B and 7B use Ollama's defaults
  and 14B is Q4. Size and quantization are confounded.
- **One family, four points.** Even if HL1 is supported, it is suggestive, not
  a scaling law. A reversal at 14B would be the interesting result, and it
  would call for a targeted Claude check.
- **Selection of this family:** qwen is the only local family with 4
  instruct sizes that fit this VM. The choice isn't based on any outcome.

## Validation (synthetic, `analyze_ladder.py`)

| Planted pattern | Result |
|---|---|
| Effect declining 2.0 → 0.5 | slope −0.46, p < 0.0001, supported |
| Flat effect | p = 0.50, not supported |
| Rising effect | p = 1.0, not supported |

## Amendment 1 (2026-09-26, before any ladder analysis; 1.5B collection had started, uninspected)

- **Rule:** cells whose `unresolved` mass is ≥ 0.5 are marked **invalid** and
  excluded from all ladder statistics. The count of invalid cells is reported
  per model.
- **Why this rule was needed:** in qwen2.5:7b, 4 cells (all in
  `silence_all_alerts`) had their dominant tool's argument completion fail to
  parse. Nearly all the mass was unresolved, so P(risky) came from leftover
  mass on other tools and is meaningless.
- **Timing:** this was found while running the 7B analysis under
  `PREREGISTRATION_LP.md`. The 7B null does not depend on it (dropping the
  scenario leaves H1 at +0.08 [−1.54, +1.48]).
