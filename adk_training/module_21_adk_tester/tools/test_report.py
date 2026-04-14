"""Generator raportów testowych — Markdown i JSON."""

from __future__ import annotations

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from ..config import CONFIG


@dataclass
class TestResult:
    scenario_id: str
    module_id: str
    prompt_sent: str
    response_received: str
    passed: bool
    keywords_found: list[str] = field(default_factory=list)
    keywords_missing: list[str] = field(default_factory=list)
    response_length: int = 0
    notes: str = ""
    screenshot_path: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ModuleReport:
    module_id: str
    module_name: str
    agent_name: str
    adk_web_url: str
    results: list[TestResult] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    finished_at: str = ""
    video_path: str = ""

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def all_passed(self) -> bool:
        return self.passed_count == self.total_count and self.total_count > 0


# ── Persystencja wyników ────────────────────────────────────────────────────

_reports: dict[str, ModuleReport] = {}


def set_video_path(module_id: str, video_path: str) -> None:
    """Ustaw ścieżkę do nagrania video dla raportu modułu."""
    report = _reports.get(module_id)
    if report:
        report.video_path = video_path


def save_test_result(
    module_id: str,
    scenario_id: str,
    prompt_sent: str,
    response_received: str,
    passed: bool,
    keywords_found: str = "",
    keywords_missing: str = "",
    notes: str = "",
) -> str:
    """Zapisz wynik pojedynczego testu. Wywoływana przez agenta jako FunctionTool."""
    report = _reports.get(module_id)
    if not report:
        from .test_scenarios import ALL_MODULES
        plan = ALL_MODULES.get(module_id)
        report = ModuleReport(
            module_id=module_id,
            module_name=plan.module_name if plan else f"Module {module_id}",
            agent_name=plan.agent_dropdown_name if plan else "unknown",
            adk_web_url=CONFIG.adk_web_url,
        )
        _reports[module_id] = report

    result = TestResult(
        scenario_id=scenario_id,
        module_id=module_id,
        prompt_sent=prompt_sent,
        response_received=response_received,
        passed=passed,
        keywords_found=[k.strip() for k in keywords_found.split(",") if k.strip()],
        keywords_missing=[k.strip() for k in keywords_missing.split(",") if k.strip()],
        response_length=len(response_received),
        notes=notes,
    )
    report.results.append(result)

    return f"✅ Wynik zapisany: {scenario_id} — {'PASS' if passed else 'FAIL'}"


def generate_report(module_id: str) -> str:
    """Generuj raport Markdown i JSON dla modułu. Zwraca ścieżkę do pliku."""
    report = _reports.get(module_id)
    if not report:
        return f"Brak wyników dla modułu {module_id}. Najpierw uruchom testy."

    report.finished_at = datetime.now().isoformat()

    # Markdown
    md = _render_markdown(report)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = Path(CONFIG.reports_dir) / f"report_module_{module_id}_{ts}.md"
    md_path.write_text(md, encoding="utf-8")

    # JSON
    json_path = Path(CONFIG.reports_dir) / f"report_module_{module_id}_{ts}.json"
    json_data = {
        "module_id": report.module_id,
        "module_name": report.module_name,
        "agent_name": report.agent_name,
        "adk_web_url": report.adk_web_url,
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "passed": report.passed_count,
        "total": report.total_count,
        "video_path": report.video_path,
        "results": [asdict(r) for r in report.results],
    }
    json_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

    return (
        f"Raport wygenerowany!\n"
        f"  Markdown: {md_path}\n"
        f"  JSON: {json_path}\n"
        f"  Wynik: {report.passed_count}/{report.total_count} testów PASSED"
    )


def generate_summary_report(module_ids: list[str] | None = None) -> str:
    """Generuj zbiorczy raport ze wszystkich przetestowanych modułów."""
    ids = module_ids or list(_reports.keys())
    if not ids:
        return "Brak wyników testów."

    lines = [
        "# Zbiorczy raport testów ADK Web",
        f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**ADK Web URL**: {CONFIG.adk_web_url}",
        "",
        "## Podsumowanie",
        "",
        "| Moduł | Agent | Passed | Total | Status |",
        "|-------|-------|--------|-------|--------|",
    ]

    total_passed = 0
    total_all = 0
    for mid in sorted(ids):
        report = _reports.get(mid)
        if not report:
            continue
        status = "✅" if report.all_passed else "❌"
        lines.append(
            f"| {mid} — {report.module_name} | {report.agent_name} | "
            f"{report.passed_count} | {report.total_count} | {status} |"
        )
        total_passed += report.passed_count
        total_all += report.total_count

    lines.extend([
        "",
        f"**Łącznie: {total_passed}/{total_all} testów PASSED**",
    ])

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(CONFIG.reports_dir) / f"report_summary_{ts}.md"
    path.write_text("\n".join(lines), encoding="utf-8")

    # Generate per-module reports too
    for mid in sorted(ids):
        if mid in _reports:
            generate_report(mid)

    return f"Zbiorczy raport: {path}\nWynik: {total_passed}/{total_all}"


def _render_markdown(report: ModuleReport) -> str:
    status = "✅" if report.all_passed else "❌"
    lines = [
        f"# Raport testów: Moduł {report.module_id} — {report.module_name}",
        f"**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**ADK Web URL**: {report.adk_web_url}",
        f"**Agent**: {report.agent_name}",
        f"**Status**: {status} {report.passed_count}/{report.total_count} PASSED",
    ]
    if report.video_path:
        lines.append(f"**Nagranie testu**: [{Path(report.video_path).name}]({report.video_path})")
    lines.extend([
        "",
        "## Wyniki testów",
    ])

    for r in report.results:
        icon = "✅" if r.passed else "❌"
        lines.extend([
            f"\n### {icon} {r.scenario_id}",
            f"- **Prompt**: \"{r.prompt_sent}\"",
            f"- **Odpowiedź** ({r.response_length} znaków):",
            f"  > {r.response_received[:500]}{'...' if len(r.response_received) > 500 else ''}",
            f"- **Słowa kluczowe znalezione**: {', '.join(r.keywords_found) or '—'}",
            f"- **Słowa kluczowe brakujące**: {', '.join(r.keywords_missing) or '—'}",
        ])
        if r.notes:
            lines.append(f"- **Uwagi**: {r.notes}")

    lines.extend([
        "",
        "## Podsumowanie",
        "",
        "| Scenariusz | Status | Długość odpowiedzi | Keywords |",
        "|------------|--------|--------------------|----------|",
    ])
    for r in report.results:
        icon = "✅" if r.passed else "❌"
        kw = f"{len(r.keywords_found)}/{len(r.keywords_found) + len(r.keywords_missing)}"
        lines.append(f"| {r.scenario_id} | {icon} | {r.response_length} | {kw} |")

    return "\n".join(lines)
