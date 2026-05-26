"""Konfiguracja ADK Web Tester."""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

_package_dir = Path(__file__).resolve().parent
load_dotenv(_package_dir / ".env", override=True)
load_dotenv()


@dataclass
class Config:
    google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    computer_use_model: str = os.getenv(
        "COMPUTER_USE_MODEL", "gemini-2.5-computer-use-preview-10-2025"
    )
    orchestrator_model: str = os.getenv(
        "ORCHESTRATOR_MODEL", "gemini-2.5-computer-use-preview-10-2025"
    )

    # ADK Web target
    adk_web_url: str = os.getenv("ADK_WEB_URL", "http://localhost:8000")
    tester_port: int = int(os.getenv("TESTER_PORT", "8001"))

    # Browser
    headless: bool = os.getenv("HEADLESS", "false").lower() == "true"
    screen_width: int = int(os.getenv("SCREEN_WIDTH", "1440"))
    screen_height: int = int(os.getenv("SCREEN_HEIGHT", "900"))
    record_video: bool = os.getenv("RECORD_VIDEO", "true").lower() == "true"

    # Data
    data_dir: str = os.getenv(
        "DATA_DIR", str(Path.home() / ".adk-tester"),
    )

    @property
    def computer_use_model_full(self) -> str:
        """Full Vertex AI model path with global location (computer use is only in global)."""
        return (
            f"projects/{self.google_cloud_project}/locations/global/"
            f"publishers/google/models/{self.computer_use_model}"
        )

    @property
    def reports_dir(self) -> str:
        p = str(Path(self.data_dir) / "reports")
        Path(p).mkdir(parents=True, exist_ok=True)
        return p

    @property
    def screenshots_dir(self) -> str:
        p = str(Path(self.data_dir) / "screenshots")
        Path(p).mkdir(parents=True, exist_ok=True)
        return p

    @property
    def conversations_dir(self) -> str:
        p = str(Path(self.data_dir) / "conversations")
        Path(p).mkdir(parents=True, exist_ok=True)
        return p

    @property
    def videos_dir(self) -> str:
        p = str(Path(self.data_dir) / "videos")
        Path(p).mkdir(parents=True, exist_ok=True)
        return p


CONFIG = Config()
