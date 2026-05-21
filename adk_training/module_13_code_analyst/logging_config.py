"""
Konfiguracja loggera — JSON lub czytelny plaintext.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Optional


class _JsonFormatter(logging.Formatter):
    """Minimalny JSON formatter — strukturyzowane logi do produkcji."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Dodatkowe pola z `extra={...}`
        for key, value in record.__dict__.items():
            if key in {
                "args", "msg", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno",
                "funcName", "created", "msecs", "relativeCreated", "thread",
                "threadName", "processName", "process", "name", "taskName",
                "message",
            }:
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = repr(value)
        return json.dumps(payload, ensure_ascii=False)


_CONFIGURED = False


def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Skonfiguruj root logger. Idempotentne — można wołać wielokrotnie."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    if json_format:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-5s %(name)s :: %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Wycisz zbyt gadatliwe biblioteki
    for noisy in ("httpx", "httpcore", "urllib3", "watchfiles", "google_genai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name)
