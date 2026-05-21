"""Konfiguracja NotebookLM Agent V2."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Załaduj .env z katalogu pakietu (nie CWD)
_package_dir = Path(__file__).resolve().parent
load_dotenv(_package_dir / ".env")
# Fallback: CWD
load_dotenv()


@dataclass
class Config:
    # Vertex AI / Gemini
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    computer_use_model: str = os.getenv(
        "COMPUTER_USE_MODEL", "gemini-2.5-computer-use-preview-10-2025"
    )

    # Browser — domyślnie dedykowany profil agenta z persistent cookies
    # Możliwe wartości CHROME_PROFILE_DIR:
    #   - (puste)     → ~/.notebooklm-agent/browser-profile  (osobny profil agenta)
    #   - "real"      → używa prawdziwego Chrome User Data z CHROME_PROFILE_SUBDIR
    #   - ścieżka     → własny katalog
    chrome_profile_dir: str = os.getenv(
        "CHROME_PROFILE_DIR",
        str(Path.home() / ".notebooklm-agent" / "browser-profile"),
    )
    # Podkatalog profilu (używane gdy CHROME_PROFILE_DIR wskazuje na Chrome User Data)
    # np. "Default" lub "Profile 1"
    chrome_profile_subdir: str = os.getenv("CHROME_PROFILE_SUBDIR", "")
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # Cookie-based auth — alternatywa dla persistent profile
    # Gdy podana, PlaywrightComputer używa izolowanego context + wstrzykuje ciasteczka.
    # Eliminuje konflikty z zajętym profilem i portami CDP.
    # Wygeneruj plik: python -m notebooklm_agent.export_cookies
    cookies_path: str = os.getenv(
        "COOKIES_PATH",
        str(Path.home() / ".notebooklm-agent" / "cookies.json"),
    )

    # Tryb cookie-based: True = użyj cookies_path zamiast chrome_profile_dir
    use_cookie_auth: bool = os.getenv("USE_COOKIE_AUTH", "false").lower() == "true"
    screen_width: int = int(os.getenv("SCREEN_WIDTH", "1440"))
    screen_height: int = int(os.getenv("SCREEN_HEIGHT", "900"))

    # NotebookLM
    default_notebook_url: str = os.getenv("NOTEBOOK_URL", "")

    # Data
    data_dir: str = os.getenv(
        "DATA_DIR",
        str(Path.home() / ".notebooklm-agent"),
    )

    # Session
    max_conversation_turns: int = int(os.getenv("MAX_CONVERSATION_TURNS", "50"))

    @property
    def session_file(self) -> str:
        """Ścieżka do pliku JSON z zapisaną sesją Google (storage_state)."""
        return str(Path(self.data_dir) / "session.json")

    @property
    def library_path(self) -> str:
        return str(Path(self.data_dir) / "library.json")

    @property
    def conversations_dir(self) -> str:
        p = str(Path(self.data_dir) / "conversations")
        Path(p).mkdir(parents=True, exist_ok=True)
        return p


CONFIG = Config()
