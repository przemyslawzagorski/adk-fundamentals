"""Pakiet-wrapper dla `AgentEvaluator`.

Konwencja ADK: `agent_module` przekazany do `AgentEvaluator.evaluate()` musi albo
konczyc sie `.agent`, albo zawierac atrybut/submodul `agent`. Uzywamy submodulu
[agent.py](agent.py) - wiec prawidlowe wywolanie to:

    AgentEvaluator.evaluate(agent_module="agent_for_eval.agent", ...)

Re-eksport `root_agent` tutaj jest dla wygody importow ad-hoc (np. w testach).
"""
from .agent import root_agent  # noqa: F401
