"""
Telemetria LLM dla modulu 13 (ADK).

Zbiera dla kazdej odpowiedzi modelu:
  - model, agent, app_name, session_id
  - prompt_tokens, completion_tokens, total_tokens
  - latency_ms
  - cost_usd (szacowany)
  - status (ok|error)

Persystencja: SQLite (data/telemetry.db).
Metryki: Prometheus (jesli zainstalowany) - histogramy i liczniki per model.
Callback: LlmCallback (before_model / after_model) do podpiecia pod Runner / LlmAgent.

Uzycie:
    from telemetry import TelemetryCollector, make_model_callbacks

    collector = TelemetryCollector()
    before_cb, after_cb = make_model_callbacks(collector, agent_name="code_analyst")
    agent = LlmAgent(
        name="code_analyst", model="gemini-2.0-flash",
        before_model_callback=before_cb,
        after_model_callback=after_cb,
        ...
    )
"""

from __future__ import annotations

import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional


# -----------------------------------------------------------------------------
# Cennik modeli (USD per 1M tokenow) - snapshot. Aktualizowac okresowo.
# -----------------------------------------------------------------------------

PRICING_USD_PER_MTOK: dict[str, dict[str, float]] = {
    # Gemini 2.0 Flash (Vertex AI)
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    # Gemini 2.5 Flash
    "gemini-2.5-flash": {"input": 0.30, "output": 2.50},
    # Gemini 2.5 Pro
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    # fallback
    "_default": {"input": 0.30, "output": 2.50},
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Prosty szacunek kosztu na podstawie tabeli cen."""
    key = model.lower()
    if key not in PRICING_USD_PER_MTOK:
        # dopasuj po prefiksie (gemini-2.0-flash-001 -> gemini-2.0-flash)
        for k in PRICING_USD_PER_MTOK:
            if key.startswith(k):
                key = k
                break
        else:
            key = "_default"
    p = PRICING_USD_PER_MTOK[key]
    return (prompt_tokens / 1_000_000) * p["input"] + (completion_tokens / 1_000_000) * p["output"]


# -----------------------------------------------------------------------------
# Prometheus (opcjonalne)
# -----------------------------------------------------------------------------

try:
    from prometheus_client import REGISTRY, Counter, Histogram
    _PROM = True
except ImportError:  # pragma: no cover
    _PROM = False


def _or_existing(cls, name: str, doc: str, labels: list[str]):
    if not _PROM:
        return None
    existing = getattr(REGISTRY, "_names_to_collectors", {}).get(name)
    if existing is not None:
        return existing
    return cls(name, doc, labels)


METRIC_LLM_LATENCY = _or_existing(
    Histogram, "adk_llm_latency_seconds",
    "Czas wywolania modelu LLM",
    ["model", "agent", "status"],
)
METRIC_LLM_TOKENS_IN = _or_existing(
    Counter, "adk_llm_prompt_tokens_total",
    "Laczne tokeny wejsciowe", ["model", "agent"],
)
METRIC_LLM_TOKENS_OUT = _or_existing(
    Counter, "adk_llm_completion_tokens_total",
    "Laczne tokeny wyjsciowe", ["model", "agent"],
)
METRIC_LLM_COST = _or_existing(
    Counter, "adk_llm_cost_usd_total",
    "Laczny koszt LLM w USD (szacunek)", ["model", "agent"],
)
METRIC_LLM_CALLS = _or_existing(
    Counter, "adk_llm_calls_total",
    "Liczba wywolan LLM", ["model", "agent", "status"],
)


# -----------------------------------------------------------------------------
# Persystencja: SQLite
# -----------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS llm_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              REAL NOT NULL,
    app_name        TEXT,
    agent           TEXT,
    model           TEXT,
    session_id      TEXT,
    prompt_tokens   INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens    INTEGER DEFAULT 0,
    latency_ms      REAL,
    cost_usd        REAL,
    status          TEXT,
    error           TEXT
);
CREATE INDEX IF NOT EXISTS ix_llm_events_ts ON llm_events(ts);
CREATE INDEX IF NOT EXISTS ix_llm_events_model ON llm_events(model);
CREATE INDEX IF NOT EXISTS ix_llm_events_session ON llm_events(session_id);
"""


@dataclass
class LlmEvent:
    ts: float
    app_name: str = ""
    agent: str = ""
    model: str = ""
    session_id: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    status: str = "ok"
    error: str = ""


class TelemetryCollector:
    """Thread-safe zbieracz zdarzen LLM."""

    def __init__(self, db_path: Optional[str | os.PathLike] = None):
        self._db_path = Path(db_path or os.environ.get(
            "ADK_TELEMETRY_DB", "data/telemetry.db"
        ))
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as c:
            c.executescript(_DDL)

    @contextmanager
    def _connect(self):
        con = sqlite3.connect(str(self._db_path))
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def record(self, ev: LlmEvent) -> None:
        with self._lock, self._connect() as c:
            c.execute(
                """INSERT INTO llm_events
                   (ts, app_name, agent, model, session_id,
                    prompt_tokens, completion_tokens, total_tokens,
                    latency_ms, cost_usd, status, error)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (ev.ts, ev.app_name, ev.agent, ev.model, ev.session_id,
                 ev.prompt_tokens, ev.completion_tokens, ev.total_tokens,
                 ev.latency_ms, ev.cost_usd, ev.status, ev.error),
            )
        # Prometheus
        if _PROM:
            labels_lat = (ev.model or "?", ev.agent or "?", ev.status or "?")
            labels = (ev.model or "?", ev.agent or "?")
            METRIC_LLM_LATENCY.labels(*labels_lat).observe(ev.latency_ms / 1000.0)
            METRIC_LLM_TOKENS_IN.labels(*labels).inc(ev.prompt_tokens)
            METRIC_LLM_TOKENS_OUT.labels(*labels).inc(ev.completion_tokens)
            METRIC_LLM_COST.labels(*labels).inc(ev.cost_usd)
            METRIC_LLM_CALLS.labels(*labels_lat).inc()

    def summary(self, since_hours: int = 24) -> dict[str, Any]:
        cutoff = time.time() - since_hours * 3600
        with self._connect() as c:
            row = c.execute(
                """SELECT COUNT(*), COALESCE(SUM(prompt_tokens),0),
                          COALESCE(SUM(completion_tokens),0),
                          COALESCE(SUM(cost_usd),0),
                          COALESCE(AVG(latency_ms),0)
                   FROM llm_events WHERE ts >= ?""",
                (cutoff,),
            ).fetchone()
            by_model = c.execute(
                """SELECT model, COUNT(*), COALESCE(SUM(cost_usd),0)
                   FROM llm_events WHERE ts >= ?
                   GROUP BY model""",
                (cutoff,),
            ).fetchall()
        return {
            "window_hours": since_hours,
            "calls": row[0],
            "prompt_tokens": row[1],
            "completion_tokens": row[2],
            "cost_usd": round(row[3], 6),
            "avg_latency_ms": round(row[4], 1),
            "by_model": [
                {"model": m, "calls": n, "cost_usd": round(c, 6)}
                for m, n, c in by_model
            ],
        }


# -----------------------------------------------------------------------------
# Callback dla ADK LlmAgent
# -----------------------------------------------------------------------------

def _extract_usage(llm_response: Any) -> tuple[int, int, int]:
    """Wyciaga (prompt, completion, total) z LlmResponse. Tolerancyjne."""
    try:
        um = getattr(llm_response, "usage_metadata", None)
        if um is not None:
            p = int(getattr(um, "prompt_token_count", 0) or 0)
            cand = int(getattr(um, "candidates_token_count", 0) or 0)
            tot = int(getattr(um, "total_token_count", 0) or (p + cand))
            return p, cand, tot
    except Exception:
        pass
    return 0, 0, 0


def make_model_callbacks(
    collector: TelemetryCollector,
    *,
    agent_name: str,
    app_name: str = "code_analyst",
) -> tuple[Callable, Callable]:
    """Zwraca (before_model_callback, after_model_callback) podpinane do LlmAgent.

    Poniewaz ADK nie przekazuje automatycznie kontekstu czasu miedzy callbackami,
    startujemy timer w atrybucie na callback_context (robimy to przez closure nad dict).
    """
    state: dict[str, float] = {}

    def before_model_callback(callback_context, llm_request):
        # unikalny klucz per wywolanie - uzywamy id obiektu zadania
        state[id(llm_request)] = time.time()
        return None  # nie modyfikujemy requestu

    def after_model_callback(callback_context, llm_response):
        t0 = state.pop(id(llm_response), None)
        if t0 is None:
            # w niektorych przebiegach ADK id request != id response; fallback - teraz
            t0 = time.time()
        latency_ms = (time.time() - t0) * 1000.0

        model = getattr(callback_context, "model_name", "") or \
                getattr(llm_response, "model_version", "") or ""
        session = getattr(callback_context, "session_id", "") or \
                  getattr(callback_context, "_invocation_context", None)
        session_id = ""
        try:
            session_id = callback_context._invocation_context.session.id  # type: ignore[attr-defined]
        except Exception:
            pass

        p, cand, tot = _extract_usage(llm_response)
        cost = estimate_cost_usd(model or "", p, cand)
        err_msg = ""
        status = "ok"
        err = getattr(llm_response, "error_code", None)
        if err:
            status = "error"
            err_msg = str(err)

        ev = LlmEvent(
            ts=time.time(),
            app_name=app_name,
            agent=agent_name,
            model=model or "",
            session_id=session_id,
            prompt_tokens=p,
            completion_tokens=cand,
            total_tokens=tot,
            latency_ms=latency_ms,
            cost_usd=cost,
            status=status,
            error=err_msg,
        )
        try:
            collector.record(ev)
        except Exception:  # pragma: no cover - nie wolno wywrocic runnera
            pass
        return None

    return before_model_callback, after_model_callback


# -----------------------------------------------------------------------------
# Singleton wygodny
# -----------------------------------------------------------------------------

_DEFAULT: Optional[TelemetryCollector] = None


def default_collector() -> TelemetryCollector:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = TelemetryCollector()
    return _DEFAULT
