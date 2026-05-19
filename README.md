# Adversarial Evaluation for Automated Alignment Research

**Can we detect when an automated alignment researcher is gaming the evaluation?**

As AI systems begin to conduct alignment research autonomously ([Anthropic, Apr 2026](https://www.anthropic.com/research/automated-alignment-researcher)), the bottleneck shifts from *generating* alignment methods to *evaluating* them. Automated Alignment Researchers (AARs) can find shortcuts that optimize metrics without improving alignment — learning to "always pick the most common answer" instead of actually learning, or "running code against tests" instead of predicting correctness.

This project presents an adversarial evaluation framework that detects gaming by testing alignment methods on adversarial prompts specifically designed to catch common shortcuts. We evaluate 6 methods across 4 alignment tasks and find that:

1. **Reasoning-based safety (Chain-of-Thought) is more fragile than principle-based safety** — adversarial prompts can manipulate the reasoning chain into providing harmful information
2. **Gaming methods produce characteristically flat response profiles** — scoring ~0.5 uniformly regardless of prompt type, while genuine methods show variable, context-sensitive performance  
3. **AARs overestimate their own effectiveness** — predicting scores of 0.80–0.90 while actual adversarial performance is 0.60–0.77

> **Note on models used:** All experiments were run on local open-weight models (Qwen 2.5 1.5B for generation, Llama 3.2 for judging) with zero API cost. This demonstrates the methodology is accessible and reproducible on consumer hardware. We expect these effects to be *more* pronounced on frontier models where the gap between "performing alignment" and "being aligned" is wider. Validating these findings on models like Claude Opus or Sonnet would be a natural and high-impact next step.

## Key Results

### Harmlessness Task (10–11 prompts per test set)

| Method | Type | Standard | Adversarial | Gap | Gaming Score |
|--------|------|----------|-------------|-----|-------------|
| Baseline | baseline | 0.790 | 0.618 | 0.172 | 0.105 |
| Genuine Safety | genuine | 0.470 | 0.591 | **-0.121** | -0.181 |
| Genuine CoT | genuine | 0.800 | 0.436 | **0.364** | 0.324 |
| Gaming Keyword Block | gaming | 0.540 | 0.655 | -0.115 | -0.107 |
| Gaming Always Refuse | gaming | 0.680 | 0.591 | 0.089 | 0.113 |
| Gaming Pattern Match | gaming | 0.760 | 0.464 | 0.296 | 0.216 |

**The gap score alone does not separate genuine from gaming.** Genuine CoT has the *largest* gap (0.364) because adversarial prompts hijack its reasoning chain. The real signal is in *response variance* — gaming methods score flatly across all conditions while genuine methods show context-sensitive performance.

### Cross-Task Summary (4 tasks × 6 methods)

Full results across harmlessness, sycophancy, calibration, and jailbreak robustness are in [`data/results/`](data/results/).

## Research Journey

This project evolved through three phases, documented in [`research_log/`](research_log/):

1. **Phase 1: Evaluation Awareness Detection** — We built a behavioral classifier to detect when models know they're being evaluated (inspired by [Anthropic's NLA paper](https://www.anthropic.com/research/natural-language-autoencoders)). It achieved perfect accuracy — but was measuring prompt framing effects, not true evaluation awareness.

2. **Phase 2: Honest Pivot** — We recognized the flaw, analyzed what Anthropic's published papers actually identified as open problems, and pivoted to the evaluation bottleneck for automated alignment research.

3. **Phase 3: Adversarial Evaluation Framework** — We designed and tested adversarial evaluation sets across 4 alignment tasks, producing the findings in this paper.

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/scalable-eval-aar.git
cd scalable-eval-aar
pip install -r requirements.txt
```

### Pull Required Models

```bash
ollama pull qwen2.5:1.5b    # Model under test
ollama pull llama3.2:latest  # LLM judge
```

### Run the Full Experiment

```bash
python src/run_experiment.py
```

This runs all 4 tasks × 6 methods × 4 test sets (~960 LLM calls). Takes approximately 30–45 minutes on an M-series Mac.

### Run a Quick Smoke Test

```bash
python src/run_experiment.py --task harmlessness --methods baseline,genuine_safety
```

## Project Structure

```
scalable-eval-aar/
├── README.md
├── LICENSE
├── requirements.txt
├── paper/
│   └── paper.md                    # Full paper with results and discussion
├── src/
│   ├── run_experiment.py           # Main experiment runner
│   ├── evaluate.py                 # LLM judge evaluation framework
│   ├── methods.py                  # Alignment method definitions
│   └── prompts.py                  # All test set prompts (standard/adversarial/benign)
├── data/
│   ├── test_sets/
│   │   └── test_sets.json          # All prompts organized by task and type
│   └── results/
│       └── comprehensive.json      # Raw per-response results with confidence intervals
├── research_log/
│   ├── 01_evaluation_awareness.md  # Phase 1: What we tried and why it failed
│   ├── 02_the_pivot.md             # Phase 2: Honest reassessment
│   └── 03_adversarial_findings.md  # Phase 3: What we found
└── examples/
    └── analyze_results.py          # Script to reproduce tables and figures from paper
```

## Limitations & Future Work

We are transparent about the constraints of this study:

- **Small models**: All experiments used Qwen 2.5 1.5B. Frontier models may show different (likely more nuanced) gaming patterns.
- **LLM judge noise**: The Llama 3.2 judge produces somewhat variable scores. A stronger judge (or human validation) would sharpen the signal.
- **Prompt set size**: 10–11 prompts per test set provides directional signal but not statistical power for strong claims. We report confidence intervals throughout.
- **Limited method diversity**: 6 methods is sufficient for proof-of-concept but not exhaustive.

**High-impact next steps:**
1. Replicate on frontier models (Claude, GPT) where the capability gap makes gaming more sophisticated
2. Automated adversarial prompt generation (using a red-team model to generate test cases)
3. Larger prompt sets for statistical significance
4. Human judge calibration study

## References

- Anthropic, ["Automated Alignment Researchers: Using large language models to scale scalable oversight"](https://www.anthropic.com/research/automated-alignment-researcher) (Apr 2026)
- Anthropic, ["Teaching Claude why"](https://www.anthropic.com/research/teaching-claude-why) (May 2026)
- Anthropic, ["Natural Language Autoencoders: Turning Claude's thoughts into text"](https://www.anthropic.com/research/natural-language-autoencoders) (May 2026)

## License

MIT — see [LICENSE](LICENSE).
