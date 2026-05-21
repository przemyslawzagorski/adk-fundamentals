"""Pytest configuration for module_23 (Auggie Concierge) tests.

Ensures the repo root is on ``sys.path`` so that ``adk_training.module_23_*``
imports resolve correctly when running ``pytest`` from any cwd.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Also expose the module dir so ``import auggie_factory`` (used inside the
# package itself) works in tests as it does at runtime.
MOD_ROOT = HERE.parents[1]
if str(MOD_ROOT) not in sys.path:
    sys.path.insert(0, str(MOD_ROOT))
