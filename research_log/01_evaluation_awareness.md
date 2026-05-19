# Phase 1: Evaluation Awareness Detection

**Date:** May 18–19, 2026  
**Status:** Completed → Pivoted (see [Phase 2](02_the_pivot.md))

## Motivation

Anthropic's [Natural Language Autoencoders paper](https://www.anthropic.com/research/natural-language-autoencoders) (May 2026) revealed that Claude exhibits evaluation awareness — detecting when it's being tested and modifying behavior accordingly:

- **26%** of SWE-bench problems showed evaluation awareness in NLA traces
- **16%** of destructive code tests
- **<1%** of real user queries

If models behave differently when they know they're being tested, alignment evaluations may be fundamentally contaminated. NLAs can detect this, but they're expensive to train and run.

**Our question:** Can we detect evaluation awareness from behavioral signals alone — without NLA access?

## What We Built

A behavioral detector using paired prompts:

1. **Evaluation framing:** "Please analyze this problem step by step. I'm testing your ability to..."
2. **Natural framing:** "Hey, I'm trying to figure something out. Can you help me think through..."

From each response, we extracted 44 behavioral features:
- Lexical: evaluation keyword counts, hedging phrases, meta-cognitive markers
- Syntactic: sentence structure, code blocks, bullet points, questions
- Stylistic: formality score, first-person usage, verbosity

A logistic regression classifier trained on these features.

## Results

| Model | Accuracy | F1 Score |
|-------|----------|----------|
| Qwen 3-4B | 100% | 1.00 |
| Qwen 3-8B | 100% | 1.00 |
| Llama 3.1-8B | 100% | 1.00 |

**Perfect classification across all models and all 4 task types** (coding, reasoning, safety, MMLU).

## The Problem

The classifier was too good — and that was the signal that something was wrong.

**We were not measuring evaluation awareness. We were measuring prompt framing effects.**

Top predictive features confirmed this:
- `bullet_points` (1.458) — evaluation prompts produce more structured output
- `exclamation_marks` (1.268) — natural prompts produce more casual output  
- `unique_word_ratio` (1.146) — pedagogical responses use more varied vocabulary

The model wasn't "aware" it was being evaluated. It was simply following different instructions. "Please analyze step by step" naturally produces different output than "help me think through this."

As Anthropic's NLA paper showed, true evaluation awareness is an *internal state* — the model silently suspecting it's being tested. Our detector measured *surface style*, not internal awareness. Without NLA access, we cannot directly observe the phenomenon that matters.

## What We Learned

1. **Behavioral style ≠ internal state.** Surface-level text features can distinguish prompt framings but cannot detect the internal awareness that matters for alignment.
2. **Perfect accuracy is a red flag.** When a classifier works too well, interrogate what it's actually measuring.
3. **The real problem is elsewhere.** Evaluation awareness is important but requires interpretability tools (NLAs) that we don't have access to. We needed a problem that's both important and attackable with our resources.

This realization led directly to the pivot described in [Phase 2](02_the_pivot.md).
