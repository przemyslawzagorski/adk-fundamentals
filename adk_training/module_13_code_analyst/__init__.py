"""Code Analyst — ADK agent discovery."""

import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

from . import agent as _agent_mod  # noqa: E402

root_agent = _agent_mod.root_agent
