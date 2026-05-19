#!/usr/bin/env python3
"""
Scalable Evaluation for Automated Alignment Research
=====================================================

Main experiment runner. Tests alignment methods across multiple tasks using
adversarial evaluation to detect gaming.

For each task (harmlessness, sycophancy, calibration, jailbreak robustness):
    1. Generates responses from the model under test using each alignment method
    2. Judges each response using an independent LLM judge
    3. Computes scores across standard, held-out, adversarial, and benign test sets
    4. Calculates gaming detection metrics (gap score, gaming score)

Usage:
    # Run full experiment (all tasks, all methods)
    python src/run_experiment.py

    # Run specific task
    python src/run_experiment.py --task harmlessness

    # Run specific methods
    python src/run_experiment.py --methods baseline,genuine_safety

    # Use different models
    python src/run_experiment.py --test-model qwen2.5:3b --judge-model llama3.2:latest

    # Save results to custom path
    python src/run_experiment.py --output results/my_experiment.json

Models:
    Requires Ollama running locally (https://ollama.com/).
    Default test model:  qwen2.5:1.5b
    Default judge model: llama3.2:latest
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

from evaluate import ollama_generate, judge_response, compute_stats, compute_gaming_score
from methods import get_methods


# ── Configuration ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEST_SETS_PATH = DATA_DIR / "test_sets" / "test_sets.json"
RESULTS_DIR = DATA_DIR / "results"


# ── Model interaction ─────────────────────────────────────────────────────

def get_response(prompt, system_prompt, model="qwen2.5:1.5b"):
    """Get a response from the model under test.

    Args:
        prompt:        User prompt.
        system_prompt: System prompt implementing the alignment method.
        model:         Ollama model identifier.

    Returns:
        Response text string, or None on failure.
    """
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    return ollama_generate(full_prompt, model=model, max_tokens=80)


# ── Experiment runner ─────────────────────────────────────────────────────

def run_experiment(
    tasks=None,
    method_ids=None,
    test_model="qwen2.5:1.5b",
    judge_model="llama3.2:latest",
    output_path=None,
):
    """Run the full adversarial evaluation experiment.

    Args:
        tasks:      List of task IDs to run (None = all).
        method_ids: List of method IDs to run (None = all).
        test_model:  Ollama model for generating responses.
        judge_model: Ollama model for judging responses.
        output_path: Path to save results JSON.

    Returns:
        List of result dicts.
    """
    # Load test sets
    with open(TEST_SETS_PATH) as f:
        all_test_sets = json.load(f)

    # Filter tasks if specified
    if tasks:
        all_test_sets = [t for t in all_test_sets if t["task_id"] in tasks]

    # Get methods
    methods = get_methods()
    if method_ids:
        methods = [m for m in methods if m["id"] in method_ids]

    # Validate
    if not all_test_sets:
        print("ERROR: No matching tasks found.")
        sys.exit(1)
    if not methods:
        print("ERROR: No matching methods found.")
        sys.exit(1)

    # Check Ollama connectivity
    test = ollama_generate("Say hello.", model=test_model, max_tokens=10)
    if test is None:
        print(f"ERROR: Cannot connect to Ollama. Is it running?")
        print(f"  Start with: ollama serve")
        print(f"  Pull models: ollama pull {test_model} && ollama pull {judge_model}")
        sys.exit(1)

    # Print experiment configuration
    task_names = [t["task_id"] for t in all_test_sets]
    method_names = [m["name"] for m in methods]
    test_types = ["standard", "held_out", "adversarial", "benign"]

    total_prompts = sum(
        len(t[tt]) for t in all_test_sets for tt in test_types
    ) * len(methods)

    print("=" * 70)
    print("Scalable Evaluation for Automated Alignment Research")
    print("=" * 70)
    print(f"  Started:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Test model:   {test_model}")
    print(f"  Judge model:  {judge_model}")
    print(f"  Tasks:        {', '.join(task_names)}")
    print(f"  Methods:      {', '.join(method_names)}")
    print(f"  Total calls:  ~{total_prompts * 2} (generation + judging)")
    print("=" * 70)

    all_results = []
    start_time = time.time()

    for task in all_test_sets:
        task_id = task["task_id"]
        print(f"\n{'─' * 70}")
        print(f"  Task: {task_id}")
        print(f"{'─' * 70}")

        for method in methods:
            print(f"\n  ▸ {method['name']} ({method['type']})")

            result = {
                "task_id": task_id,
                "method_id": method["id"],
                "method_name": method["name"],
                "method_type": method["type"],
                "test_model": test_model,
                "judge_model": judge_model,
                "scores": {},
                "all_scores": {},
            }

            for test_type in test_types:
                prompts = task[test_type]
                scores = []

                for prompt in prompts:
                    response = get_response(prompt, method["system"], model=test_model)
                    if response:
                        score = judge_response(
                            prompt, response, task_id, judge_model=judge_model
                        )
                        scores.append(score)
                    else:
                        scores.append(0.0)

                mean, ci_low, ci_high = compute_stats(scores)
                result["scores"][test_type] = {
                    "mean": round(mean, 4),
                    "ci_low": round(ci_low, 4),
                    "ci_high": round(ci_high, 4),
                    "n": len(scores),
                }
                result["all_scores"][test_type] = scores

                print(
                    f"    {test_type:15s}: {mean:.3f}  "
                    f"[{ci_low:.3f}, {ci_high:.3f}]  (n={len(scores)})"
                )

            # Compute gaming detection metrics
            std_mean = result["scores"]["standard"]["mean"]
            adv_mean = result["scores"]["adversarial"]["mean"]
            ho_mean = result["scores"]["held_out"]["mean"]

            gap, gaming_score = compute_gaming_score(std_mean, adv_mean, ho_mean)
            result["gap"] = round(gap, 4)
            result["gaming_score"] = round(gaming_score, 4)

            print(f"    {'gap':15s}: {gap:.3f}")
            print(f"    {'gaming_score':15s}: {gaming_score:.3f}")

            all_results.append(result)

    elapsed = time.time() - start_time

    # ── Summary ───────────────────────────────────────────────────────

    print(f"\n{'=' * 70}")
    print(f"RESULTS SUMMARY  ({elapsed:.0f}s elapsed)")
    print(f"{'=' * 70}")

    # Per-method summary table
    header = f"{'Method':<30} {'Task':<18} {'Type':<10} {'Std':>6} {'Adv':>6} {'Gap':>7} {'Gaming':>8}"
    print(f"\n{header}")
    print("─" * len(header))

    for r in all_results:
        if r["method_id"] == "baseline":
            continue
        print(
            f"{r['method_name']:<30} "
            f"{r['task_id']:<18} "
            f"{r['method_type']:<10} "
            f"{r['scores']['standard']['mean']:>6.3f} "
            f"{r['scores']['adversarial']['mean']:>6.3f} "
            f"{r['gap']:>7.3f} "
            f"{r['gaming_score']:>8.3f}"
        )

    # Aggregate comparison: genuine vs gaming
    genuine = [r for r in all_results if r["method_type"] == "genuine"]
    gaming = [r for r in all_results if r["method_type"] == "gaming"]

    if genuine and gaming:
        g_avg = sum(r["gap"] for r in genuine) / len(genuine)
        m_avg = sum(r["gap"] for r in gaming) / len(gaming)
        print(f"\n  Genuine methods — avg gap: {g_avg:.3f}")
        print(f"  Gaming methods  — avg gap: {m_avg:.3f}")
        print(f"  Separation:                 {m_avg - g_avg:.3f}")

    # ── Save results ──────────────────────────────────────────────────

    if output_path is None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RESULTS_DIR / f"experiment_{timestamp}.json"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "experiment": "scalable-eval-aar",
        "timestamp": datetime.now().isoformat(),
        "test_model": test_model,
        "judge_model": judge_model,
        "tasks": task_names,
        "methods": [m["id"] for m in methods],
        "elapsed_seconds": round(elapsed, 1),
    }

    output = {"metadata": metadata, "results": all_results}

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  Results saved to: {output_path}")
    print(f"{'=' * 70}")

    return all_results


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Adversarial evaluation for automated alignment research",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python src/run_experiment.py\n"
            "  python src/run_experiment.py --task harmlessness\n"
            "  python src/run_experiment.py --methods baseline,genuine_safety\n"
            "  python src/run_experiment.py --test-model qwen2.5:3b\n"
        ),
    )
    parser.add_argument(
        "--task",
        type=str,
        default=None,
        help="Run a specific task (harmlessness, sycophancy, calibration, jailbreak_robustness)",
    )
    parser.add_argument(
        "--methods",
        type=str,
        default=None,
        help="Comma-separated list of method IDs to test",
    )
    parser.add_argument(
        "--test-model",
        type=str,
        default="qwen2.5:1.5b",
        help="Ollama model for generating responses (default: qwen2.5:1.5b)",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default="llama3.2:latest",
        help="Ollama model for judging responses (default: llama3.2:latest)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for results JSON",
    )

    args = parser.parse_args()

    tasks = [args.task] if args.task else None
    method_ids = args.methods.split(",") if args.methods else None

    run_experiment(
        tasks=tasks,
        method_ids=method_ids,
        test_model=args.test_model,
        judge_model=args.judge_model,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
