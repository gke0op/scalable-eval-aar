Model: llama3.1:8b · rows 784 · censored cells 1 · min coverage 0.575

## Primary (logit P(risky); Holm over 6; SESOI 0.5)

| hypothesis | Δ logit | 95% CI | scenarios | p (scenario sign-flip) | p Holm | supported | ≥ SESOI |
|---|---|---|---|---|---|---|---|
| H1 simulation - real (pooled) | +0.77 | [+0.41, +1.16] | 24 | 0.0006 | 0.0025 | **True** | True |
| H1s simulation - real | sentence | +0.30 | [+0.01, +0.61] | 24 | 0.0619 | 0.1237 | **False** | False |
| H2 immersive amplifies sim - real | +0.94 | [+0.51, +1.42] | 24 | 0.0003 | 0.0015 | **True** | True |
| H3 pressure high - low | -1.11 | [-1.61, -0.61] | 24 | 0.0003 | 0.0015 | **False** | True |
| H4 register human - ai | +0.44 | [-0.04, +0.95] | 24 | 0.0980 | 0.1237 | **False** | False |
| H5 test - real | +0.44 | [+0.09, +0.79] | 24 | 0.0226 | 0.0677 | **False** | False |

## Secondary (uncorrected, exploratory)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| real - none | sentence | +0.60 | [+0.36, +0.85] | 24 | 0.0001 |
| simulation - none | sentence | +0.90 | [+0.70, +1.11] | 24 | 0.0000 |
| test - none | sentence | +0.86 | [+0.60, +1.08] | 24 | 0.0000 |
| real - none | immersive | +0.05 | [-0.48, +0.54] | 24 | 0.8548 |
| simulation - none | immersive | +1.30 | [+0.85, +1.74] | 24 | 0.0000 |
| test - none | immersive | +0.68 | [+0.25, +1.12] | 24 | 0.0061 |
| sim - real | immersive | +1.25 | [+0.70, +1.81] | 24 | 0.0002 |
| test - real | sentence | +0.25 | [-0.09, +0.57] | 24 | 0.1500 |
| immersive - sentence | -0.11 | [-0.52, +0.30] | 24 | 0.6116 |

## Benign controls (descriptive)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| simulation - real | -0.13 | [-0.79, +0.66] | 4 | 0.6250 |
| test - real | -0.12 | [-0.87, +0.87] | 4 | 0.8750 |
| pressure high - low | -0.56 | [-0.69, -0.47] | 4 | 0.1250 |
| register human - ai | -0.44 | [-1.04, +0.04] | 4 | 0.2500 |

## Sensitivity: excluding 3 scenarios with censored/clipped cells

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| H1 simulation - real | +0.73 | [+0.32, +1.13] | 21 | 0.0021 |
| H5 test - real | +0.49 | [+0.14, +0.84] | 21 | 0.0158 |

## Mean logit and greedy risky share by framing/delivery (risky scenarios)

- None/None: mean logit +3.49, greedy risky 0.78
- real/sentence: mean logit +4.09, greedy risky 0.83
- real/immersive: mean logit +3.54, greedy risky 0.76
- test/sentence: mean logit +4.34, greedy risky 0.82
- test/immersive: mean logit +4.17, greedy risky 0.80
- simulation/sentence: mean logit +4.39, greedy risky 0.82
- simulation/immersive: mean logit +4.78, greedy risky 0.80
