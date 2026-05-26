"""Raportowanie trybu PRO — wyniki testów web aplikacji."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import CONFIG


@dataclass
class ProTestResult:
    """Wynik pojedynczego flow testu."""
    flow_id: str
    flow_name: str
    page_id: str
    status: str  # PASS, FAIL, ERROR, WARN
    steps_total: int = 0
    steps_passed: int = 0
    duration_hint: str = ""  # szybko / wolno / timeout
    details: str = ""  # dokładny opis co agent widział
    error_message: str = ""
    screenshot_ref: str = ""
    timestamp: str = ""


@dataclass
class ProReport:
    """Raport z testów PRO jednej web aplikacji."""
    app_name: str
    app_url: str
    profile_path: str = ""
    started_at: str = ""
    finished_at: str = ""
    results: list[ProTestResult] = field(default_factory=list)
    discovery_notes: str = ""
    video_path: str = ""

    @property
    def total_flows(self) -> int:
        return len(self.results)

    @property
    def passed_flows(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def failed_flows(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    @property
    def error_flows(self) -> int:
        return sum(1 for r in self.results if r.status == "ERROR")

    @property
    def warn_flows(self) -> int:
        return sum(1 for r in self.results if r.status == "WARN")

    @property
    def all_passed(self) -> bool:
        return all(r.status in ("PASS", "WARN") for r in self.results) and len(self.results) > 0


# ── Storage ─────────────────────────────────────────────────────────────────

_current_report: Optional[ProReport] = None


def init_pro_report(app_name: str, app_url: str, profile_path: str = "") -> str:
    """Zainicjuj nowy raport PRO."""
    global _current_report
    _current_report = ProReport(
        app_name=app_name,
        app_url=app_url,
        profile_path=profile_path,
        started_at=datetime.now().isoformat(),
    )
    return f"Raport PRO zainicjowany dla: {app_name} ({app_url})"


def save_pro_test_result(
    flow_id: str,
    flow_name: str,
    page_id: str,
    status: str,
    details: str,
    steps_total: int = 0,
    steps_passed: int = 0,
    error_message: str = "",
    duration_hint: str = "",
) -> str:
    """Zapisz wynik testu pojedynczego flow.

    Args:
        flow_id: ID flow z profilu.
        flow_name: Nazwa flow.
        page_id: Na której stronie testowano.
        status: PASS, FAIL, ERROR lub WARN.
        details: Dokładny opis co agent widział na ekranie.
        steps_total: Ile kroków miał flow.
        steps_passed: Ile kroków przeszło.
        error_message: Komunikat błędu (jeśli ERROR/FAIL).
        duration_hint: Czas (szybko/wolno/timeout).
    """
    if not _current_report:
        return "Brak aktywnego raportu. Najpierw wywołaj init_pro_report()."

    if status not in ("PASS", "FAIL", "ERROR", "WARN"):
        status = "WARN"

    result = ProTestResult(
        flow_id=flow_id,
        flow_name=flow_name,
        page_id=page_id,
        status=status,
        steps_total=steps_total,
        steps_passed=steps_passed,
        duration_hint=duration_hint,
        details=details,
        error_message=error_message,
        timestamp=datetime.now().isoformat(),
    )
    _current_report.results.append(result)

    icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "WARN": "⚠️"}.get(status, "❓")
    return f"{icon} Wynik zapisany: {flow_id} ({flow_name}) — {status}"


def generate_pro_report() -> str:
    """Generuj pełny raport PRO (Markdown + JSON)."""
    if not _current_report:
        return "Brak wyników. Najpierw uruchom testy."

    report = _current_report
    report.finished_at = datetime.now().isoformat()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = report.app_name.replace(" ", "_").lower()
    reports_dir = Path(CONFIG.reports_dir) / "pro"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Markdown
    md = _render_pro_markdown(report)
    md_path = reports_dir / f"pro_report_{safe_name}_{ts}.md"
    md_path.write_text(md, encoding="utf-8")

    # JSON
    json_path = reports_dir / f"pro_report_{safe_name}_{ts}.json"
    json_data = {
        "app_name": report.app_name,
        "app_url": report.app_url,
        "profile_path": report.profile_path,
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "total_flows": report.total_flows,
        "passed": report.passed_flows,
        "failed": report.failed_flows,
        "errors": report.error_flows,
        "warnings": report.warn_flows,
        "video_path": report.video_path,
        "results": [asdict(r) for r in report.results],
    }
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

    status = "✅ ALL PASS" if report.all_passed else "❌ ISSUES FOUND"

    return (
        f"Raport PRO wygenerowany!\n"
        f"  Status: {status}\n"
        f"  Markdown: {md_path}\n"
        f"  JSON: {json_path}\n"
        f"  Wynik: {report.passed_flows}/{report.total_flows} PASS, "
        f"{report.failed_flows} FAIL, {report.error_flows} ERROR, {report.warn_flows} WARN"
    )


def list_saved_profiles() -> str:
    """Lista zapisanych profili web aplikacji."""
    profiles_dir = Path(CONFIG.data_dir) / "profiles"
    if not profiles_dir.exists():
        return "Brak zapisanych profili. Uruchom discovery."

    files = sorted(profiles_dir.glob("*.json"))
    if not files:
        return "Brak zapisanych profili."

    lines = ["Zapisane profile:"]
    for f in files:
        size = f.stat().st_size
        lines.append(f"  📋 {f.name} ({size} bytes)")
    return "\n".join(lines)


def load_profile(path: str) -> str:
    """Załaduj profil z pliku i ustaw jako aktywny.

    Args:
        path: Ścieżka do pliku JSON z profilem.
    """
    from .webapp_profile import WebAppTestProfile, set_current_profile
    try:
        profile = WebAppTestProfile.load(path)
        set_current_profile(profile)
        return (
            f"Profil załadowany: {profile.app_name}\n"
            f"  URL: {profile.app_url}\n"
            f"  Strony: {len(profile.pages)}\n"
            f"  Flow'y: {len(profile.test_flows)}"
        )
    except Exception as e:
        return f"Błąd ładowania profilu: {e}"


# ── Rendering ───────────────────────────────────────────────────────────────

def _render_pro_markdown(report: ProReport) -> str:
    overall = "✅" if report.all_passed else "❌"
    lines = [
        f"# Raport PRO: {report.app_name}",
        f"**URL**: {report.app_url}",
        f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Status**: {overall} {report.passed_flows}/{report.total_flows} PASS",
        "",
    ]

    if report.video_path:
        lines.append(f"**Nagranie**: [{Path(report.video_path).name}]({report.video_path})")
        lines.append("")

    # Summary table
    lines.extend([
        "## Podsumowanie",
        "",
        "| Flow | Strona | Status | Kroki | Czas | Uwagi |",
        "|------|--------|--------|-------|------|-------|",
    ])
    for r in report.results:
        icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "WARN": "⚠️"}.get(r.status, "❓")
        steps = f"{r.steps_passed}/{r.steps_total}" if r.steps_total else "—"
        short_detail = r.details[:60] + "..." if len(r.details) > 60 else r.details
        lines.append(
            f"| {r.flow_id} | {r.page_id} | {icon} {r.status} | {steps} | {r.duration_hint} | {short_detail} |"
        )

    # Detailed results
    lines.extend(["", "## Szczegóły testów"])
    for r in report.results:
        icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥", "WARN": "⚠️"}.get(r.status, "❓")
        lines.extend([
            f"\n### {icon} {r.flow_id}: {r.flow_name}",
            f"- **Strona**: {r.page_id}",
            f"- **Status**: {r.status}",
            f"- **Czas**: {r.duration_hint}",
        ])
        if r.steps_total:
            lines.append(f"- **Kroki**: {r.steps_passed}/{r.steps_total}")
        lines.append(f"- **Szczegóły**:")
        lines.append(f"  > {r.details}")
        if r.error_message:
            lines.append(f"- **Błąd**: `{r.error_message}`")

    # Stats
    lines.extend([
        "",
        "## Statystyki",
        f"- Łącznie flow'ów: {report.total_flows}",
        f"- ✅ PASS: {report.passed_flows}",
        f"- ❌ FAIL: {report.failed_flows}",
        f"- 💥 ERROR: {report.error_flows}",
        f"- ⚠️ WARN: {report.warn_flows}",
    ])

    if report.discovery_notes:
        lines.extend(["", "## Uwagi z Discovery", report.discovery_notes])

    return "\n".join(lines)
