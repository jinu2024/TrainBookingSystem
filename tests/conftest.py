"""Pytest configuration helpers.

Ensure the project root is on sys.path so tests can import top-level packages
like `database`, `services`, and `cli` when pytest is run from the repo root.
"""
import sys
from pathlib import Path


def pytest_configure(config):
    repo_root = Path(__file__).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)