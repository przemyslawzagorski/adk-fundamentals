"""pytest config for module_24 tests — ensures repo root on sys.path so
`adk_training.module_24_audit_ops` can be imported as a package.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Walk up to the repo root (parent of `adk_training`)
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
