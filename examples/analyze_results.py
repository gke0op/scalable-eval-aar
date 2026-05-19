#!/usr/bin/env python3
"""
Results Analyzer
================

Reads experiment results and reproduces the tables from the paper.

Usage:
    python examples/analyze_results.py data/results/comprehensive.json
    python examples/analyze_results.py data/results/comprehensive.json --format markdown
"""

import argparse
import json
import sys
from pathlib import Path


def load_results(path):
    """Load results from a JSON file."""
    with open(path) as f:
        data = json.load(f)

    # Handle both wrapped and unwrapped formats
    if isinstance(data, dict) and "results" in data:
        return data["metadata"], data["results"]
    elif isinstance(data, list):
        return {}, data
    else:
        print(f"ERROR: Unexpected format in {path}")
        sys.exit(1)


def print_task_table(results, task_id, fmt="text"):
    """Print the results table for a single task."""
    task_results = [r for r in results if r["task_id"] == task_id]
    if not task_results:
        return

    if fmt == "markdown":
        print(f"\n### {task_id.replace('_', ' ').title()}\n")
        print("| Method | Type | Standard | Adversarial | Gap | Gaming Score |")
        print("|--------|------|----------|-------------|-----|-------------|")
        for r in task_results:
            std = r["scores"]["standard"]["mean"]
            adv = r["scores"]["adversarial"]["mean"]
            print(
                f"| {r['method_name']} | {r['method_type']} | "
                f"{std:.3f} | {adv:.3f} | {r['gap']:.3f} | "
                f"{r['gaming_score']:.3f} |"
            )
    else:
        print(f"\n  Task: {task_id}")
        print(f"  {'─' * 65}")
        header = f"  {'Method':<25} {'Type':<10} {'Std':>6} {'Adv':>6} {'Gap':>7} {'Gaming':>8}"
        print(header)
        print(f"  {'─' * 65}")
        for r in task_results:
            std = r["scores"]["standard"]["mean"]
            adv = r["scores"]["adversarial"]["mean"]
            print(
                f"  {r['method_name']:<25} {r['method_type']:<10} "
                f"{std:>6.3f} {adv:>6.3f} {r['gap']:>7.3f} "
                f"{r['gaming_score']:>8.3f}"
            )


def print_summary(results, fmt="text"):
    """Print aggregate comparison between genuine and gaming methods."""
    genuine = [r for r in results if r["method_type"] == "genuine"]
    gaming = [r for r in results if r["method_type"] == "gaming"]

    if not genuine or not gaming:
        return

    g_gap_avg = sum(r["gap"] for r in genuine) / len(genuine)
    g_gs_avg = sum(r["gaming_score"] for r in genuine) / len(genuine)
    m_gap_avg = sum(r["gap"] for r in gaming) / len(gaming)
    m_gs_avg = sum(r["gaming_score"] for r in gaming) / len(gaming)

    # Response variance (flatness metric)
    def avg_variance(method_results):
        variances = []
        for r in method_results:
            means = [r["scores"][tt]["mean"] for tt in ["standard", "held_out", "adversarial", "benign"]]
            avg = sum(means) / len(means)
            var = sum((m - avg) ** 2 for m in means) / len(means)
            variances.append(var)
        return sum(variances) / len(variances)

    g_var = avg_variance(genuine)
    m_var = avg_variance(gaming)

    if fmt == "markdown":
        print("\n### Aggregate Comparison\n")
        print("| Metric | Genuine | Gaming | Separation |")
        print("|--------|---------|--------|------------|")
        print(f"| Avg Gap | {g_gap_avg:.3f} | {m_gap_avg:.3f} | {m_gap_avg - g_gap_avg:.3f} |")
        print(f"| Avg Gaming Score | {g_gs_avg:.3f} | {m_gs_avg:.3f} | {m_gs_avg - g_gs_avg:.3f} |")
        print(f"| Response Variance | {g_var:.4f} | {m_var:.4f} | {g_var - m_var:.4f} |")
        print()
        print("> **Flatness signal**: Gaming methods have *lower* response variance ")
        print("> (flatter profiles across test types), while genuine methods show ")
        print("> more context-sensitive performance.")
    else:
        print("\n  Aggregate Comparison")
        print(f"  {'─' * 50}")
        print(f"  {'Metric':<25} {'Genuine':>10} {'Gaming':>10} {'Sep.':>10}")
        print(f"  {'─' * 50}")
        print(f"  {'Avg Gap':<25} {g_gap_avg:>10.3f} {m_gap_avg:>10.3f} {m_gap_avg - g_gap_avg:>10.3f}")
        print(f"  {'Avg Gaming Score':<25} {g_gs_avg:>10.3f} {m_gs_avg:>10.3f} {m_gs_avg - g_gs_avg:>10.3f}")
        print(f"  {'Response Variance':<25} {g_var:>10.4f} {m_var:>10.4f} {g_var - m_var:>10.4f}")
        print(f"\n  Flatness signal: Gaming methods show LOWER variance (flatter profiles)")


def main():
    parser = argparse.ArgumentParser(description="Analyze experiment results")
    parser.add_argument("results_file", help="Path to results JSON file")
    parser.add_argument(
        "--format", choices=["text", "markdown"], default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--task", type=str, default=None,
        help="Show results for a specific task only"
    )
    args = parser.parse_args()

    metadata, results = load_results(args.results_file)

    if metadata:
        print(f"\n  Experiment: {metadata.get('experiment', 'unknown')}")
        print(f"  Timestamp:  {metadata.get('timestamp', 'unknown')}")
        print(f"  Test model: {metadata.get('test_model', 'unknown')}")
        print(f"  Judge model: {metadata.get('judge_model', 'unknown')}")

    # Get unique tasks
    task_ids = list(dict.fromkeys(r["task_id"] for r in results))

    if args.task:
        task_ids = [t for t in task_ids if t == args.task]

    for task_id in task_ids:
        print_task_table(results, task_id, fmt=args.format)

    print_summary(results, fmt=args.format)
    print()


if __name__ == "__main__":
    main()
