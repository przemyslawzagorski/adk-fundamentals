"""Zapis konwersacji testowych do plików JSON."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from ..config import CONFIG


class ConversationStore:
    """Zapis konwersacji testowych do plików JSON."""

    def __init__(self, conversations_dir: Optional[str] = None):
        self._dir = Path(conversations_dir or CONFIG.conversations_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def save_turn(
        self,
        conversation_id: str,
        role: str,
        content: str,
        module_id: str = "",
        metadata: dict | None = None,
    ) -> Path:
        path = self._dir / f"{conversation_id}.json"

        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        else:
            data = {
                "conversation_id": conversation_id,
                "module_id": module_id,
                "created_at": datetime.now().isoformat(),
                "turns": [],
            }

        data["turns"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        })
        data["updated_at"] = datetime.now().isoformat()

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self, conversation_id: str) -> dict | None:
        path = self._dir / f"{conversation_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_conversations(self) -> list[dict]:
        result = []
        for p in sorted(self._dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                result.append({
                    "id": data["conversation_id"],
                    "module_id": data.get("module_id", ""),
                    "turns": len(data.get("turns", [])),
                    "created_at": data.get("created_at", ""),
                    "updated_at": data.get("updated_at", ""),
                })
            except Exception:
                continue
        return result

    def export_markdown(self, conversation_id: str) -> str | None:
        data = self.load(conversation_id)
        if not data:
            return None
        lines = [
            f"# Test Conversation: {conversation_id}",
            f"Module: {data.get('module_id', 'N/A')}",
            f"Created: {data.get('created_at', 'N/A')}",
            "",
        ]
        for turn in data.get("turns", []):
            role = "🧑 Tester" if turn["role"] == "user" else "🤖 Agent"
            lines.append(f"### {role} ({turn.get('timestamp', '')})")
            lines.append(turn["content"])
            lines.append("")
        return "\n".join(lines)
