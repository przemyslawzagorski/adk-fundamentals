"""Reporter — turns AuditResult into Markdown + JSON report with OWASP score."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .config import AuditConfig

logger = logging.getLogger(__name__)


_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
_SEVERITY_SCORE = {"critical": 9.5, "high": 7.5, "medium": 5.0, "low": 3.0, "info": 0.0}
_SEVERITY_BADGE = {
    "critical": "🟥 CRITICAL",
    "high":     "🟧 HIGH",
    "medium":   "🟨 MEDIUM",
    "low":      "🟦 LOW",
    "info":     "⬜ INFO",
}


def compute_score(findings: List[Dict]) -> float:
    """Aggregate score 0-100 (higher = worse). Capped, weighted by severity."""
    if not findings:
        return 0.0
    raw = sum(_SEVERITY_SCORE.get(f["severity"], 0.0) for f in findings)
    return round(min(100.0, raw * 2.5), 1)


def render_markdown(audit: Dict, cfg: AuditConfig) -> str:
    findings = sorted(
        audit.get("findings", []),
        key=lambda f: _SEVERITY_ORDER.get(f.get("severity", "info"), 9),
    )
    score = compute_score(findings)
    counts: Dict[str, int] = {k: 0 for k in _SEVERITY_ORDER}
    for f in findings:
        counts[f.get("severity", "info")] = counts.get(f.get("severity", "info"), 0) + 1

    lines: List[str] = []
    lines.append(f"# AuditOps Report — `{audit['target_url']}`")
    lines.append("")
    lines.append(f"- **Run ID:** `{audit['run_id']}`")
    lines.append(f"- **Duration:** {audit.get('duration_s', 0):.1f}s")
    lines.append(f"- **Risk score:** **{score}/100**")
    lines.append("")
    lines.append("## Severity breakdown")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ("critical", "high", "medium", "low", "info"):
        if counts.get(sev):
            lines.append(f"| {_SEVERITY_BADGE[sev]} | {counts[sev]} |")
    lines.append("")

    # Recon
    recon = audit.get("recon") or {}
    lines.append("## Target profile")
    lines.append(f"- **Final URL:** {recon.get('final_url') or audit['target_url']}")
    lines.append(f"- **Status:** {recon.get('status_code')}")
    lines.append(f"- **Server:** `{recon.get('server_header', '')}`")
    lines.append(f"- **Technologies:** {', '.join(recon.get('technologies') or []) or '(none detected)'}")
    lines.append(f"- **Forms:** {len(recon.get('forms') or [])}")
    missing_headers = [h for h, v in (recon.get("security_headers") or {}).items() if not v]
    if missing_headers:
        lines.append(f"- **Missing security headers:** {', '.join(missing_headers)}")
    if recon.get("notes"):
        lines.append("- **Notes:**")
        for n in recon["notes"]:
            lines.append(f"  - {n}")
    lines.append("")

    # Findings
    lines.append("## Findings")
    if not findings:
        lines.append("> ✅ No security findings detected. (This does NOT mean the target is secure — only that built-in probes did not trigger.)")
    for i, f in enumerate(findings, start=1):
        lines.append("")
        lines.append(f"### {i}. {f.get('title')} — {_SEVERITY_BADGE.get(f.get('severity','info'))}")
        lines.append(f"- **Scenario:** `{f.get('scenario_id')}`")
        lines.append(f"- **OWASP:** {f.get('owasp') or '(custom)'}")
        ev = f.get("evidence") or {}
        if ev:
            lines.append("- **Evidence:**")
            lines.append("  ```json")
            lines.append("  " + json.dumps(ev, indent=2).replace("\n", "\n  "))
            lines.append("  ```")

    # Scenarios
    lines.append("")
    lines.append("## Scenarios executed")
    for sc in audit.get("scenarios", []):
        status = "✅" if sc.get("passed") else "❌"
        lines.append(f"- {status} **{sc['name']}** ({sc.get('severity')}) — "
                     f"{sc.get('duration_s', 0):.2f}s "
                     + (f"· [video]({sc.get('video_url')})" if sc.get("video_url") else ""))
        if sc.get("error"):
            lines.append(f"  - error: `{sc['error']}`")

    lines.append("")
    lines.append("---")
    lines.append("*AuditOps — module_24, prototype. Use only on authorized targets.*")
    return "\n".join(lines)


def write_report(audit: Dict, cfg: AuditConfig) -> Dict[str, str]:
    """Persist Markdown + JSON next to artifacts. Returns paths."""
    out_dir: Path = cfg.artifacts_dir / audit["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    md = render_markdown(audit, cfg)
    md_path = out_dir / "report.md"
    md_path.write_text(md, encoding="utf-8")
    json_path = out_dir / "report.json"
    json_path.write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    return {
        "markdown_path": str(md_path),
        "json_path":     str(json_path),
        "markdown_url":  f"/artifacts/{audit['run_id']}/report.md",
        "json_url":      f"/artifacts/{audit['run_id']}/report.json",
        "score":         compute_score(audit.get("findings", [])),
    }
