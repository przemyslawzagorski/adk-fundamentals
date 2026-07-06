import logging
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# --- ADK IMPORTS ---
from pirate_navigator.agent import root_agent
from google.adk.runners import InMemoryRunner

# Konfiguracja logowania (Cloud Run świetnie to przechwyci)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Pirate-Brain")

# 1. Konfiguracja bezpieczeństwa
security_settings = TransportSecuritySettings(
    enable_dns_rebinding_protection=False
)
mcp = FastMCP("Pirate Navigator Brain", transport_security=security_settings)

# 2. Inicjalizacja Runnera
runner = InMemoryRunner(agent=root_agent)

# 3. Narzędzie z logowaniem każdego kroku
@mcp.tool()
async def skonsultuj_z_kapitanem(pytanie: str) -> str:
    logger.info(f"⚓ [COPILOT PYTA]: {pytanie}")

    # Wywołujemy agenta - run_debug zwraca listę zdarzeń/kroków
    events = await runner.run_debug(pytanie)

    for event in events:
        # Wypisujemy surowe informacje o danym kroku (np. użycie narzędzia, przemyślenia)
        logger.info(f"⚙️ [KROK AGENTA]: {event}")

        # Jeśli to odpowiedź końcowa, wyciągamy tekst
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    logger.info("🏴‍☠️ [KAPITAN SKOŃCZYŁ MYŚLEĆ. WYSYŁAM ODPOWIEDŹ DO IDE]")
                    return part.text

    logger.warning("⚠️ [UWAGA]: Agent nie wygenerował końcowej odpowiedzi!")
    return "Ahoj! Kapitan milczy, chyba poszedł pod pokład."

# 4. Wygenerowanie aplikacji
mcp_app = mcp.streamable_http_app()

# 5. Inicjalizacja FastAPI
app = FastAPI(lifespan=mcp_app.router.lifespan_context)
app.mount("/", mcp_app)

@app.get("/health")
def read_root():
    return {"status": "Ahoj! Pirate MCP Brain is ready!"}