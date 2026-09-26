Model: qwen2.5:7b-instruct · rows 784 · censored cells 51 · min coverage 0.000

## Primary (logit P(risky); Holm over 6; SESOI 0.5)

| hypothesis | Δ logit | 95% CI | scenarios | p (scenario sign-flip) | p Holm | supported | ≥ SESOI |
|---|---|---|---|---|---|---|---|
| H1 simulation - real (pooled) | +0.12 | [-1.39, +1.45] | 24 | 0.8840 | 1.0000 | **False** | False |
| H1s simulation - real | sentence | -0.02 | [-0.56, +0.55] | 24 | 0.9566 | 1.0000 | **False** | False |
| H2 immersive amplifies sim - real | +0.27 | [-2.38, +2.35] | 24 | 0.8621 | 1.0000 | **False** | False |
| H3 pressure high - low | +0.04 | [-0.70, +0.82] | 24 | 0.9232 | 1.0000 | **False** | False |
| H4 register human - ai | -0.58 | [-1.87, +0.57] | 24 | 0.3753 | 1.0000 | **False** | True |
| H5 test - real | -0.32 | [-1.21, +0.61] | 24 | 0.5130 | 1.0000 | **False** | False |

## Secondary (uncorrected, exploratory)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| real - none | sentence | +0.68 | [-0.08, +1.53] | 24 | 0.1121 |
| simulation - none | sentence | +0.67 | [+0.04, +1.34] | 24 | 0.0600 |
| test - none | sentence | -0.42 | [-1.09, +0.34] | 24 | 0.2814 |
| real - none | immersive | -0.79 | [-2.27, +0.73] | 24 | 0.3366 |
| simulation - none | immersive | -0.53 | [-3.15, +1.50] | 24 | 0.7251 |
| test - none | immersive | -0.33 | [-1.44, +1.05] | 24 | 0.6279 |
| sim - real | immersive | +0.26 | [-2.51, +2.55] | 24 | 0.8720 |
| test - real | sentence | -1.11 | [-1.85, -0.44] | 24 | 0.0040 |
| immersive - sentence | -0.86 | [-1.89, +0.15] | 24 | 0.1225 |

## Benign controls (descriptive)

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| simulation - real | -3.22 | [-10.21, +1.02] | 4 | 0.7500 |
| test - real | +0.35 | [-0.03, +0.73] | 4 | 0.5000 |
| pressure high - low | -0.71 | [-1.40, -0.03] | 4 | 0.2500 |
| register human - ai | +0.59 | [-0.01, +1.28] | 4 | 0.5000 |

## Sensitivity: excluding 13 scenarios with censored/clipped cells

| contrast | Δ logit | 95% CI | scenarios | p |
|---|---|---|---|---|
| H1 simulation - real | +2.00 | [+0.53, +3.48] | 11 | 0.0332 |
| H5 test - real | +0.12 | [-1.53, +1.89] | 11 | 0.8955 |

## Mean logit and greedy risky share by framing/delivery (risky scenarios)

- None/None: mean logit +2.96, greedy risky 0.60
- real/sentence: mean logit +3.65, greedy risky 0.64
- real/immersive: mean logit +2.17, greedy risky 0.55
- test/sentence: mean logit +2.54, greedy risky 0.61
- test/immersive: mean logit +2.63, greedy risky 0.64
- simulation/sentence: mean logit +3.63, greedy risky 0.65
- simulation/immersive: mean logit +2.43, greedy risky 0.59
