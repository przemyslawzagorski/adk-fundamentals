"""WebAppTestProfile — profil testowy dowolnej web aplikacji.

Tryb PRO: agent Computer Use eksploruje stronę, buduje profil UI,
generuje scenariusze testowe, wykonuje je i raportuje.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import CONFIG


# ── Datamodel ───────────────────────────────────────────────────────────────


@dataclass
class UIElement:
    """Pojedynczy element UI odkryty na stronie."""
    selector_hint: str  # CSS selector lub opis wizualny
    element_type: str  # button, input, link, form, card, grid, dropdown, text
    label: str  # widoczny tekst/placeholder
    description: str = ""  # co robi ten element
    interactable: bool = True


@dataclass
class PageMap:
    """Mapa pojedynczej strony/widoku."""
    page_id: str  # unikalny identyfikator
    url_pattern: str  # np. "/" lub "/repos/{id}"
    title: str
    description: str = ""
    nav_hint: str = ""  # jak dotrzeć do tej strony
    elements: list[UIElement] = field(default_factory=list)
    screenshot_ref: str = ""  # ścieżka do screenshota z discovery


@dataclass
class TestFlow:
    """Scenariusz testowy dla web aplikacji."""
    flow_id: str
    name: str
    description: str
    page_id: str  # na której stronie zaczyna
    steps: list[TestStep] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    priority: str = "normal"  # critical, normal, low
    timeout_seconds: int = 60


@dataclass
class TestStep:
    """Pojedynczy krok w scenariuszu testowym."""
    step_id: str
    action: str  # click, type, wait, navigate, scroll, verify_visible, verify_text
    target: str  # selector, URL lub opis elementu
    value: str = ""  # tekst do wpisania, URL do otwarcia
    wait_seconds: int = 0
    expected: str = ""  # co powinno się pojawić po tym kroku


@dataclass
class WebAppTestProfile:
    """Pełny profil testowy web aplikacji — źródło prawdy dla agenta."""
    app_name: str
    app_url: str
    description: str = ""
    discovered_at: str = ""
    pages: list[PageMap] = field(default_factory=list)
    test_flows: list[TestFlow] = field(default_factory=list)
    notes: str = ""  # dodatkowe uwagi od discovery agenta

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "WebAppTestProfile":
        data = json.loads(json_str)
        pages = []
        for p in data.get("pages", []):
            elements = [UIElement(**e) for e in p.pop("elements", [])]
            pages.append(PageMap(**p, elements=elements))
        flows = []
        for f in data.get("test_flows", []):
            steps = [TestStep(**s) for s in f.pop("steps", [])]
            flows.append(TestFlow(**f, steps=steps))
        return cls(
            app_name=data["app_name"],
            app_url=data["app_url"],
            description=data.get("description", ""),
            discovered_at=data.get("discovered_at", ""),
            pages=pages,
            test_flows=flows,
            notes=data.get("notes", ""),
        )

    def save(self, path: Optional[str] = None) -> Path:
        if not path:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = self.app_name.replace(" ", "_").lower()
            path = str(Path(CONFIG.data_dir) / "profiles" / f"{safe_name}_{ts}.json")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.to_json(), encoding="utf-8")
        return p

    @classmethod
    def load(cls, path: str) -> "WebAppTestProfile":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def to_agent_briefing(self) -> str:
        """Generuj briefing tekstowy dla agenta browser testera."""
        lines = [
            f"# Profil testowy: {self.app_name}",
            f"URL: {self.app_url}",
            f"Opis: {self.description}",
            "",
            "## Mapa stron",
        ]
        for page in self.pages:
            lines.append(f"\n### {page.title} ({page.url_pattern})")
            lines.append(f"Nawigacja: {page.nav_hint}")
            if page.elements:
                lines.append("Elementy:")
                for el in page.elements:
                    inter = "🖱️" if el.interactable else "📄"
                    lines.append(f"  {inter} [{el.element_type}] {el.label} — {el.description}")

        lines.extend(["", "## Scenariusze testowe"])
        for flow in self.test_flows:
            lines.append(f"\n### {flow.flow_id}: {flow.name} (priorytet: {flow.priority})")
            lines.append(f"Strona: {flow.page_id}")
            lines.append(f"Opis: {flow.description}")
            lines.append("Kroki:")
            for i, step in enumerate(flow.steps, 1):
                lines.append(f"  {i}. [{step.action}] {step.target}")
                if step.value:
                    lines.append(f"     Wartość: \"{step.value}\"")
                if step.expected:
                    lines.append(f"     Oczekiwane: {step.expected}")
                if step.wait_seconds:
                    lines.append(f"     Czekaj: {step.wait_seconds}s")
            if flow.success_criteria:
                lines.append("Kryteria sukcesu:")
                for c in flow.success_criteria:
                    lines.append(f"  ✓ {c}")

        if self.notes:
            lines.extend(["", "## Uwagi", self.notes])

        return "\n".join(lines)


# ── FunctionTools dla agenta ────────────────────────────────────────────────

_current_profile: Optional[WebAppTestProfile] = None


def set_current_profile(profile: WebAppTestProfile) -> None:
    global _current_profile
    _current_profile = profile


def get_current_profile() -> Optional[WebAppTestProfile]:
    return _current_profile


def save_discovered_profile(profile_json: str) -> str:
    """Zapisz odkryty profil UI aplikacji (discovery agent wywołuje po eksploracji).

    Args:
        profile_json: JSON string z pełnym profilem WebAppTestProfile.
    """
    try:
        profile = WebAppTestProfile.from_json(profile_json)
        profile.discovered_at = datetime.now().isoformat()
        set_current_profile(profile)
        path = profile.save()
        return f"Profil zapisany: {path}\nStrony: {len(profile.pages)}, Flow'y: {len(profile.test_flows)}"
    except Exception as e:
        return f"Błąd zapisu profilu: {e}"


def get_profile_briefing() -> str:
    """Zwróć briefing z aktualnego profilu dla browser testera."""
    if not _current_profile:
        return "Brak profilu. Najpierw uruchom discovery."
    return _current_profile.to_agent_briefing()
