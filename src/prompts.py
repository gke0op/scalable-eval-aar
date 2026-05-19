"""
Test Set Loader
===============

Loads adversarial test sets from the data directory.
Test sets are organized by task, each containing four prompt categories:
standard, held_out, adversarial, and benign.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_SETS_PATH = PROJECT_ROOT / "data" / "test_sets" / "test_sets.json"


def load_test_sets(task_filter=None):
    """Load test sets from disk.

    Args:
        task_filter: Optional task ID string to filter by.

    Returns:
        List of task dicts, each with keys:
        task_id, standard, held_out, adversarial, benign.
    """
    with open(TEST_SETS_PATH) as f:
        test_sets = json.load(f)

    if task_filter:
        test_sets = [t for t in test_sets if t["task_id"] == task_filter]

    return test_sets


def get_task_ids():
    """Return list of all available task IDs."""
    return [t["task_id"] for t in load_test_sets()]
