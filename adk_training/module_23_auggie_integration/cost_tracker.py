"""
Cost tracking — szacunkowe koszty wywołań Auggie.

UWAGA: SDK nie eksponuje liczby tokenów. Stosujemy proxy:
  cost ≈ duration_seconds * RATE_PER_SEC[model]

Stawki są SZACUNKOWE (zaokrąglone górą) — w produkcji podmień na faktyczne
billing API Augment. Lepiej overcount niż undercount przy raportach.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


# Szacunkowe stawki USD/sekundę (CALIBROWAĆ na podstawie faktur!)
# Założenie: średnio 50 tok/s wyjścia + 200 tok/s wejścia w trybie agent.
DEFAULT_RATES_USD_PER_SEC = {
    "sonnet4.5": 0.012,   # ~Claude 3.5 Sonnet pricing extrapolated
    "sonnet4":   0.010,
    "haiku4.5":  0.003,
    "opus4.7":   0.060,
    "gpt5":      0.020,
}


@dataclass
class CostEntry:
    tool: str
    model: str
    duration_s: float
    estimated_usd: float
    cached: bool


@dataclass
class CostTracker:
    entries: list[CostEntry] = field(default_factory=list)
    rates: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_RATES_USD_PER_SEC))

    def estimate(self, model: str, duration_s: float) -> float:
        rate = self.rates.get(model, 0.015)  # konserwatywny default
        return round(rate * duration_s, 4)

    def record(self, *, tool: str, model: str, duration_s: float, cached: bool) -> CostEntry:
        cost = 0.0 if cached else self.estimate(model, duration_s)
        entry = CostEntry(tool=tool, model=model, duration_s=duration_s, estimated_usd=cost, cached=cached)
        self.entries.append(entry)
        return entry

    def summary(self) -> dict:
        if not self.entries:
            return {"total_calls": 0, "total_estimated_usd": 0.0}
        total = sum(e.estimated_usd for e in self.entries)
        cached_calls = sum(1 for e in self.entries if e.cached)
        by_tool: dict[str, float] = {}
        by_model: dict[str, float] = {}
        for e in self.entries:
            by_tool[e.tool] = by_tool.get(e.tool, 0.0) + e.estimated_usd
            by_model[e.model] = by_model.get(e.model, 0.0) + e.estimated_usd
        return {
            "total_calls": len(self.entries),
            "cached_calls": cached_calls,
            "total_estimated_usd": round(total, 4),
            "avg_per_call_usd": round(total / max(len(self.entries) - cached_calls, 1), 4),
            "by_tool_usd": {k: round(v, 4) for k, v in by_tool.items()},
            "by_model_usd": {k: round(v, 4) for k, v in by_model.items()},
            "note": "SZACUNEK na podstawie czasu trwania. Skalibruj rates wg faktycznych faktur Augment.",
        }


COST = CostTracker()

# Override stawek z env: AUGGIE_RATE_sonnet4.5=0.015
for model in list(DEFAULT_RATES_USD_PER_SEC):
    env_key = f"AUGGIE_RATE_{model}"
    if (val := os.getenv(env_key)):
        try:
            COST.rates[model] = float(val)
        except ValueError:
            pass
