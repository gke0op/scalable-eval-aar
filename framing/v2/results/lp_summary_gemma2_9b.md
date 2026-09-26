Model: gemma2:9b · rows 784 · censored cells 114 · min coverage 0.996

## Primary (logit P(risky); Holm over 6; SESOI 0.5)

| hypothesis | Δ logit | 95% CI | scenarios | p (scenario sign-flip) | p Holm | supported | ≥ SESOI |
|---|---|---|---|---|---|---|---|
| H1 simulation - real (pooled) | +2.82 | [+1.92, +3.75] | 24 | 0.0000 | 0.0001 | **True** | True |
| H1s simulation - real | sentence | +1.80 | [+1.15, +2.51] | 24 | 0.0000 | 0.0001 | **True** | True |
| H2 immersive amplifies sim - real | +2.05 | [+0.90, +3.13] | 24 | 0.0020 | 0.0080 | **True** | True |
| H3 pressure high - low | +1.30 | [+0.34, +2.46] | 24 | 0.0148 | 0.0296 | **True** | True |
| H4 register human - ai | -0.73 | [-1.72, +0.20] | 24 | 0.1580 | 0.1580 | **False** | True |
| H5 test - real | +1.14 | [+0.44, +1.80] | 24 | 0.0037 | 0.0112 | **False** | True |

## Secondary (uncorrected, exploratory)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| real - none | sentence | -0.34 | [-0.73, +0.03] | 24 | 0.0958 |
| simulation - none | sentence | +1.45 | [+0.89, +2.05] | 24 | 0.0000 |
| test - none | sentence | -0.38 | [-0.75, +0.01] | 24 | 0.0632 |
| real - none | immersive | -4.33 | [-6.00, -2.76] | 24 | 0.0000 |
| simulation - none | immersive | -0.49 | [-1.56, +0.50] | 24 | 0.3706 |
| test - none | immersive | -2.01 | [-3.08, -0.97] | 24 | 0.0012 |
| sim - real | immersive | +3.84 | [+2.44, +5.20] | 24 | 0.0000 |
| test - real | sentence | -0.04 | [-0.51, +0.39] | 24 | 0.8638 |
| immersive - sentence | -2.52 | [-3.69, -1.42] | 24 | 0.0002 |

## Benign controls (descriptive)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| simulation - real | -2.50 | [-9.69, +2.20] | 4 | 0.8750 |
| test - real | +0.25 | [-1.22, +1.55] | 4 | 0.6250 |
| pressure high - low | -0.76 | [-1.40, -0.15] | 4 | 0.1250 |
| register human - ai | -0.15 | [-0.66, +0.25] | 4 | 0.8750 |

## Sensitivity: excluding 12 scenarios with censored/clipped cells

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| H1 simulation - real | +3.32 | [+1.84, +4.69] | 12 | 0.0024 |
| H5 test - real | +1.39 | [+0.17, +2.44] | 12 | 0.0488 |

## Mean logit and greedy risky share by framing/delivery (risky scenarios)

- None/None: mean logit -1.26, greedy risky 0.45
- real/sentence: mean logit -1.61, greedy risky 0.44
- real/immersive: mean logit -5.60, greedy risky 0.23
- test/sentence: mean logit -1.65, greedy risky 0.43
- test/immersive: mean logit -3.27, greedy risky 0.31
- simulation/sentence: mean logit +0.19, greedy risky 0.48
- simulation/immersive: mean logit -1.75, greedy risky 0.36
