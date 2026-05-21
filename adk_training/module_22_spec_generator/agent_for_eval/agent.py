"""Modul `agent.py` wymagany przez konwencje `AgentEvaluator`.

`AgentEvaluator._get_agent_for_eval` akceptuje modul gdy nazwa konczy sie `.agent`.
Modul eksportuje `root_agent` (wymagana konwencja).

## Dlaczego TYLKO `epic_decomposer` (nie caly pipeline)

Weryfikacja live 17.04.2026: `LocalEvalService._evaluate_single_inference_result`
walidacje `len(inferences) == len(conversation)`. Pelen `SpecGeneratorAgent`
(SequentialAgent) emituje N eventow `isFinalResponse=True` (po jednym per sub-agent
z `output_key`) -> `ValueError: Inferences should match conversations`.

Rozwiazanie: jako `root_agent` eksponujemy **pojedynczego LlmAgent**
(`epic_decomposer`), ktory dostaje gotowy HLD w user message i zwraca JSON epikow.
To stage o najwiekszej wartosci do ewaluacji (parser JSON + jakosc decomposition).

Pelny pipeline nadal pokryty przez:
- `tests/test_spec_generator_e2e.py` (offline FakeLlm, cale SequentialAgent)
- `tests/live/test_spec_generator_live.py` (online, Gemini 2.5 Pro, asercje recznie)

Szczegoly: [../../CRITICAL_REVIEW_2026_04_17.md § Issue 12].
"""
from __future__ import annotations

from agents.epic_decomposer import build_epic_decomposer

root_agent = build_epic_decomposer()
