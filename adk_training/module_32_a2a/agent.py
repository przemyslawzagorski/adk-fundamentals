"""
Module 32 — A2A Protocol: CONSUMING AGENT (root_agent)
=======================================================

Ten plik to główny agent (consumer), który:
1. Ma lokalny tool do listowania plików (read_file_snippet)
2. Deleguje analizę bezpieczeństwa do zdalnego code_analyst_agent przez A2A

WYMAGANIA WSTĘPNE:
    # Krok 1 — uruchom zdalny serwer A2A (w osobnym terminalu):
    uvicorn adk_training.module_32_a2a.remote_a2a.code_analyst.agent:a2a_app \
        --host localhost --port 8001

    # Krok 2 — uruchom tego agenta:
    adk web adk_training/

ARCHITEKTURA:
    ┌─────────────────────┐
    │  root_agent (local) │  ← ADK web / CLI
    │  model: gemini      │
    │  tools: read_file   │  ← lokalny tool
    │  sub_agents:        │
    │    └─ prime_agent ──┼──── A2A ──► code_analyst_agent (port 8001)
    └─────────────────────┘              └─ scan_for_hardcoded_secrets()
                                         └─ scan_for_sql_injection()

JAK DZIAŁA RemoteA2aAgent:
    - agent_card: URL do well-known endpoint z metadanymi zdalnego agenta
    - use_legacy=False: używa nowego A2A executor (zalecane)
    - ADK automatycznie buduje protokół A2A, wysyła request, odbiera JSON
    - Zdalny agent widoczny jak zwykły sub_agent w orchestracji
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# URL do auto-generowanego agent-card przez to_a2a()
# Format: http://<host>:<port>/.well-known/agent-card.json
REMOTE_AGENT_URL = f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"


# =============================================================================
# LOKALNY TOOL — czyta snippet pliku z dysku (nie wymaga zdalnego serwisu)
# =============================================================================

def read_file_snippet(file_path: str, max_lines: int = 50) -> dict:
    """
    Czyta pierwsze N linii pliku z lokalnego filesystemu.

    Args:
        file_path: Ścieżka do pliku (relatywna do CWD)
        max_lines: Maksymalna liczba linii do odczytania (domyślnie 50)

    Returns:
        dict z: content, lines_read, file_exists, file_size_kb
    """
    path = Path(file_path)
    if not path.exists():
        return {"file_exists": False, "content": "", "lines_read": 0, "file_size_kb": 0}

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()[:max_lines]
        return {
            "file_exists": True,
            "content": "\n".join(lines),
            "lines_read": len(lines),
            "file_size_kb": round(path.stat().st_size / 1024, 2),
        }
    except Exception as e:
        return {"file_exists": True, "content": f"[ERROR: {e}]", "lines_read": 0, "file_size_kb": 0}


# =============================================================================
# ZDALNY SUB-AGENT — podłączony przez A2A Protocol
# =============================================================================
# UWAGA: Upewnij się że serwer A2A jest uruchomiony na port 8001!
#        uvicorn adk_training.module_32_a2a.remote_a2a.code_analyst.agent:a2a_app \
#            --host localhost --port 8001

code_analyst_remote = RemoteA2aAgent(
    name="code_analyst_agent",
    description=(
        "Zdalny agent bezpieczeństwa. Analizuje podany snippet kodu pod kątem: "
        "hardkodowanych sekretów (hasła, API keys, tokeny) oraz podatności "
        "SQL Injection. Zwraca raport JSON z oceną ryzyka i zaleceniami."
    ),
    agent_card=REMOTE_AGENT_URL,
    use_legacy=False,   # używaj nowego A2A executor
)


# =============================================================================
# ROOT AGENT — orchestruje lokalny tool + zdalny A2A agent
# =============================================================================

root_agent = LlmAgent(
    name="code_security_orchestrator",
    model=MODEL,
    description="Orchestrator: czyta pliki lokalnie, analizuje bezpieczeństwo przez zdalny A2A agent.",
    instruction="""Jesteś orchestratorem bezpieczeństwa kodu. Masz do dyspozycji:
1. read_file_snippet() — czyta plik lokalnie
2. code_analyst_agent (zdalny przez A2A) — analizuje bezpieczeństwo kodu

Przepływ pracy:
- Jeśli użytkownik poda ścieżkę do pliku → użyj read_file_snippet() aby odczytać zawartość,
  a następnie przekaż snippet do code_analyst_agent z prośbą o analizę bezpieczeństwa.
- Jeśli użytkownik wklei kod bezpośrednio → przekaż go od razu do code_analyst_agent.
- Jeśli prośba dotyczy samego odczytu pliku → użyj tylko read_file_snippet().

Po otrzymaniu raportu z code_analyst_agent, przedstaw wyniki czytelnie:
- 🔴 CRITICAL / HIGH → wyróżnij znalezione problemy
- 🟡 MEDIUM → opisz zalecenia
- 🟢 LOW → potwierdź że kod jest bezpieczny

Zawsze cytuj konkretne problemy i zalecenia z raportu.
""",
    sub_agents=[code_analyst_remote],
    tools=[FunctionTool(func=read_file_snippet)],
)
