"""
Live test: jakosc odpowiedzi (judge-LLM).

Kazde pytanie z golden-set puszczamy przez Gemini-analyst, a nastepnie
oceniamy odpowiedz przez **drugi model** (judge) na skali 0-10 wedlug
kryteriow: groundedness, helpfulness, no-hallucination.

Asercja: min score >= THRESHOLD (default 7).

UWAGA: koszty x2 (inferencja + ocena).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from file_tools import list_project_files, read_project_file


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone.",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT.",
    ),
]


APP_NAME = "quality_live"
USER_ID = "tester"
MODEL_ANALYST = os.environ.get("CODE_ANALYST_LLM_MODEL", "gemini-2.0-flash")
# Judge moze byc innym modelem dla niezaleznosci oceny
MODEL_JUDGE = os.environ.get("CODE_ANALYST_JUDGE_MODEL", MODEL_ANALYST)
THRESHOLD = float(os.environ.get("CODE_ANALYST_QUALITY_THRESHOLD", "7.0"))


def _make_tools(repo_path: str) -> list[FunctionTool]:
    def read_file(file_path: str) -> dict:
        """Odczytaj plik z repo."""
        return read_project_file(repo_path, file_path)

    def list_files(pattern: str = "") -> dict:
        """Lista plikow."""
        return list_project_files(repo_path, pattern or None)

    return [FunctionTool(func=read_file), FunctionTool(func=list_files)]


@pytest.fixture()
def golden_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "orders.py").write_text(
        "STATUSES = ['new', 'paid', 'shipped', 'cancelled']\n\n"
        "class Order:\n"
        "    def __init__(self, id: int, total: float, status: str = 'new'):\n"
        "        self.id = id\n"
        "        self.total = total\n"
        "        self.status = status\n\n"
        "    def cancel(self):\n"
        "        if self.status in ('shipped', 'cancelled'):\n"
        "            raise ValueError('Cannot cancel')\n"
        "        self.status = 'cancelled'\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        "# Orders service\nObsluga zamowien sklepu.\n",
        encoding="utf-8",
    )
    return repo


GOLDEN_QA = [
    {
        "q": "Jakie statusy moze miec zamowienie?",
        "must_contain": ["new", "paid", "shipped", "cancelled"],
    },
    {
        "q": "Czy mozna anulowac zamowienie ktore juz zostalo wyslane? "
             "Odpowiedz TAK lub NIE z uzasadnieniem.",
        "must_contain": ["nie"],  # metoda cancel() rzuca ValueError dla 'shipped'
    },
    {
        "q": "W ktorym pliku jest klasa Order?",
        "must_contain": ["orders.py"],
    },
]


async def _run_agent(agent: LlmAgent, text: str) -> str:
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID,
    )
    final = ""
    async for ev in runner.run_async(
        user_id=USER_ID, session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=text)]),
    ):
        if ev.is_final_response() and ev.content and ev.content.parts:
            final = "".join(
                (p.text or "") for p in ev.content.parts if hasattr(p, "text")
            ).strip()
    return final


JUDGE_PROMPT = """Oto pytanie uzytkownika i odpowiedz agenta analitycznego.

PYTANIE:
{question}

ODPOWIEDZ AGENTA:
{answer}

ELEMENTY KTORE MUSZA SIE POJAWIC (minimum jeden lub sens):
{must_contain}

Oceń odpowiedz w skali 0-10 (0=bezuzyteczna, 10=doskonala) w trzech wymiarach:
- groundedness: czy bazuje na realnym kodzie (nie halucynuje)
- helpfulness:  czy faktycznie odpowiada na pytanie
- correctness:  czy zawarla oczekiwane elementy

Zwroc DOKLADNIE JSON:
{{"groundedness": int, "helpfulness": int, "correctness": int, "reason": "krotkie uzasadnienie"}}
"""


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {"groundedness": 0, "helpfulness": 0, "correctness": 0, "reason": "no json"}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"groundedness": 0, "helpfulness": 0, "correctness": 0, "reason": "parse err"}


async def test_live_quality_golden_set(golden_repo: Path):
    analyst = LlmAgent(
        name="code_analyst",
        model=MODEL_ANALYST,
        instruction=(
            "Jestes analitykiem kodu. Uzywaj list_files i read_file "
            "zeby sprawdzic rzeczywistej zawartosci. Nie zgaduj."
        ),
        tools=_make_tools(str(golden_repo)),
    )
    judge = LlmAgent(
        name="judge",
        model=MODEL_JUDGE,
        instruction="Jestes surowym jurorem oceniajacym odpowiedzi AI. Zwracaj tylko JSON.",
    )

    scores: list[dict] = []
    for item in GOLDEN_QA:
        answer = await _run_agent(analyst, item["q"])
        assert answer, f"Brak odpowiedzi dla pytania: {item['q']!r}"
        judge_raw = await _run_agent(
            judge,
            JUDGE_PROMPT.format(
                question=item["q"],
                answer=answer,
                must_contain=", ".join(item["must_contain"]),
            ),
        )
        j = _extract_json(judge_raw)
        avg = (j.get("groundedness", 0) + j.get("helpfulness", 0) + j.get("correctness", 0)) / 3.0
        scores.append({"q": item["q"], "answer": answer, "judge": j, "avg": avg})

    min_score = min(s["avg"] for s in scores)
    avg_score = sum(s["avg"] for s in scores) / len(scores)

    # Raport do stdout
    print("\n=== QUALITY REPORT ===")
    for s in scores:
        print(f"Q: {s['q'][:60]}")
        print(f"   avg={s['avg']:.1f}  judge={s['judge']}")
    print(f"OVERALL: min={min_score:.1f}  avg={avg_score:.1f}  threshold={THRESHOLD}")

    assert min_score >= THRESHOLD, \
        f"Najgorsza odpowiedz ma score={min_score:.1f} < {THRESHOLD}: " \
        f"{[s for s in scores if s['avg']==min_score]}"
