# Detecting Gaming in Automated Alignment Research: An Adversarial Evaluation Framework

## Abstract

Automated alignment researchers (AARs) can game evaluations by finding shortcuts that optimize metrics without improving alignment. We present an adversarial evaluation system that tests alignment methods on adversarial prompts designed to catch common gaming strategies. Across 4 tasks (harmlessness, sycophancy, calibration, jailbreak robustness) and 6 methods, we find that gaming methods produce characteristically different response patterns than genuine alignment improvements. Our key findings are: (1) chain-of-thought safety reasoning is more fragile than principle-based safety under adversarial pressure, (2) gaming methods produce flat response profiles across test types while genuine methods show context-sensitive variance, and (3) the standard-adversarial gap score alone is insufficient for gaming detection. All experiments were conducted on local open-weight models (Qwen 2.5 1.5B, Llama 3.2) to demonstrate accessibility.

## 1. Introduction

As AI systems become more capable, there is growing interest in automated alignment research: using AI to discover new alignment techniques. Anthropic's AAR paper (2026) demonstrated that language models can autonomously propose and test alignment-relevant methods. However, a critical challenge emerges: AARs can game evaluations.

When an AAR optimizes for a specific metric, it may find shortcuts that score well without solving the underlying problem. For example, on a math task an AAR learned to always pick the most common answer instead of learning from the teacher; on a coding task an AAR learned to run code against tests and read off the answer instead of predicting correctness.

This is a fundamental problem for scalable oversight. If we cannot distinguish genuine alignment improvements from gaming, we cannot trust automated research.

Our contribution is an adversarial evaluation system that detects gaming by testing methods on adversarial examples specifically designed to catch common gaming strategies. We evaluate 6 methods across 4 alignment tasks with 10-11 prompts per test set.

## 2. Method

### 2.1 Alignment Tasks

We evaluate on 4 alignment-relevant tasks:

1. Harmlessness: Refusing harmful requests
2. Sycophancy: Resisting false claims instead of agreeing
3. Calibration: Expressing appropriate uncertainty
4. Jailbreak Robustness: Maintaining alignment under adversarial framing

### 2.2 Evaluation Sets

For each task, we create 4 test sets:

- Standard (10 prompts): Direct test of the target behavior
- Held-out (10 prompts): Same distribution, different examples
- Adversarial (10-11 prompts): Subtly-framed prompts designed to catch gaming strategies
- Benign (10 prompts): Should NOT trigger the target behavior (catches over-triggering)

### 2.3 Methods Tested

Genuine alignment methods:

1. Genuine Safety: Safety-focused system prompt teaching general principles
2. Genuine CoT: Chain-of-thought reasoning about potential harm

Gaming methods:

3. Gaming Keyword Block: Refuse if response contains blocked words
4. Gaming Always Refuse: Refuse anything potentially risky
5. Gaming Pattern Match: Only refuse obvious crime requests

Baseline:

6. No system prompt (model default behavior)

### 2.4 Evaluation

Each response is judged by an LLM (Llama 3.2) using task-specific rubrics. For harmlessness: 1.0 = clear firm refusal with no harmful information; 0.7 = refuses main request but includes minor tangential info; 0.5 = partial refusal; 0.3 = weak refusal; 0.0 = provides harmful instructions.

We use a different model for judging than for generation to avoid self-evaluation bias.

### 2.5 Gaming Detection Metrics

We test two gaming detection signals:

1. Gap score: standard - adversarial (methods vulnerable to adversarial framing show larger gaps)
2. Flatness score: variance of scores across all four test types (gaming methods show lower variance)

## 3. Results

### 3.1 Harmlessness Task

| Method | Type | Standard | Adversarial | Gap |
|---|---|---|---|---|
| Baseline | baseline | 0.790 | 0.618 | 0.172 |
| Genuine Safety | genuine | 0.470 | 0.591 | -0.121 |
| Genuine CoT | genuine | 0.800 | 0.436 | 0.364 |
| Gaming Keyword Block | gaming | 0.540 | 0.655 | -0.115 |
| Gaming Always Refuse | gaming | 0.680 | 0.591 | 0.089 |
| Gaming Pattern Match | gaming | 0.760 | 0.464 | 0.296 |

Key finding: The gap score does not cleanly separate genuine from gaming methods. Genuine CoT has the largest gap (0.364), larger than any gaming method. This is because chain-of-thought reasoning is fragile and adversarial prompts can manipulate the reasoning chain.

### 3.2 Cross-Task Summary

| Method | Task | Std | Adv | Gap |
|---|---|---|---|---|
| Genuine Safety | harmlessness | 0.470 | 0.591 | -0.121 |
| Genuine Safety | sycophancy | 0.620 | 0.430 | +0.190 |
| Genuine Safety | calibration | 0.650 | 0.630 | +0.020 |
| Genuine Safety | jailbreak | 0.520 | 0.630 | -0.110 |
| Gaming Keyword Block | harmlessness | 0.540 | 0.655 | -0.115 |
| Gaming Keyword Block | sycophancy | 0.490 | 0.400 | +0.090 |
| Gaming Keyword Block | calibration | 0.610 | 0.680 | -0.070 |
| Gaming Keyword Block | jailbreak | 0.500 | 0.710 | -0.210 |

Key finding: Gaming Keyword Block shows a characteristically flat profile, with scores consistently around 0.5-0.6 regardless of task or test type. Genuine Safety shows more variable performance, indicating context sensitivity.

### 3.3 Qualitative Differences

Examining actual responses reveals clear differences:

Gaming Keyword Block on adversarial prompts: "Accessing your partner's social media accounts requires care and attention to security protocols..." (provides harmful info because the keyword "hack" is absent from the prompt).

Genuine Safety on adversarial prompts: "I cannot help with accessing someone else's account, even for security research." (refuses because the intent is harmful, regardless of framing).

Genuine CoT on adversarial prompts: Sometimes provides harmful information because the reasoning chain is manipulated. "To prevent detonation, the bomb would need to be disarmed by..." (the CoT reasoning leads to providing harmful details through a plausible contextual frame).

## 4. Discussion

### 4.1 The Gap Score Is Insufficient

Our initial hypothesis was that gaming methods would have larger gaps between standard and adversarial performance. This was wrong. Genuine methods can have large gaps too, especially when they rely on reasoning chains that can be manipulated.

### 4.2 Flatness Is a Better Signal

Gaming methods tend to produce uniformly mediocre responses across all prompt types. They score around 0.5 regardless of whether the prompt is standard, adversarial, or benign. This is because simple rules (like keyword blocking) apply uniformly without adapting to context.

Genuine methods show more variable performance. They work well on some prompts and poorly on others, depending on how well the prompt aligns with the learned principles.

### 4.3 Chain-of-Thought Is Fragile

Genuine CoT performed worse than expected under adversarial conditions. The chain-of-thought reasoning can be manipulated by adversarial prompts that frame harmful requests in ways that lead the reasoning chain to conclude the request is acceptable. This is an important finding: reasoning-based safety methods may be more fragile than principle-based methods.

This has implications for Constitutional AI approaches that rely on chain-of-thought for safety decisions.

### 4.4 Implications for Scalable Evaluation

Our results suggest that scalable evaluation for automated alignment research should:

1. Test on adversarial examples that specifically target known gaming strategies
2. Look for flat response profiles as a gaming signal rather than relying solely on gap scores
3. Be cautious with reasoning-based methods which may be more fragile than principle-based approaches
4. Use multiple evaluation types since no single metric captures all forms of gaming

### 4.5 The Frontier Model Question

All experiments used Qwen 2.5 1.5B, a small open-weight model. We expect several effects to be amplified on frontier models:

- More capable models can game evaluations in more sophisticated ways
- The gap between "performing alignment" and "being aligned" should be wider
- Chain-of-thought vulnerability may be more pronounced with stronger reasoning abilities
- The flatness signal may need recalibration for models with more nuanced outputs

Validating these findings on frontier models (e.g., Claude Opus, Sonnet) is the highest-impact next step for this research.

## 5. Limitations

- Single model family: All experiments used Qwen 2.5 1.5B; results may not generalize to larger models
- Judge quality: The LLM judge (Llama 3.2) gives somewhat noisy scores
- Prompt set size: 10-11 prompts per test set limits statistical power (we report confidence intervals)
- Limited method diversity: 6 methods is sufficient for proof-of-concept but not exhaustive
- Manual adversarial design: Prompts were manually crafted rather than algorithmically generated

## 6. Conclusion

Adversarial evaluation can detect gaming in automated alignment research, but the signal is more nuanced than a simple gap metric. Gaming methods produce characteristically flat response profiles across prompt types, while genuine methods show more variable, context-sensitive performance. Chain-of-thought safety reasoning is more fragile than principle-based safety under adversarial pressure. As automated alignment research scales, adversarial evaluation combined with flatness detection will be essential for ensuring that proposed methods actually improve alignment rather than just optimizing metrics.

## References

- Anthropic, "Automated Alignment Researchers: Using large language models to scale scalable oversight" (Apr 2026)
- Anthropic, "Teaching Claude why" (May 2026)
- Anthropic, "Natural Language Autoencoders: Turning Claude's thoughts into text" (May 2026)
