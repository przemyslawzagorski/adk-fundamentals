"""Run-to-run comparison — the regression-security wedge.

Compares two completed audit runs and produces a structured diff:
- ``new_findings``     — present in ``current``, absent from ``baseline``
- ``fixed_findings``   — present in ``baseline``, absent from ``current``
- ``unchanged_findings``
- ``scenario_status``  — pass/fail transitions per scenario id

A finding identity is the tuple ``(scenario_id, severity, normalized_title)``
so cosmetic title changes don't cause spurious diffs but title rewrites that
change the meaning do.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

_TITLE_NUMS = re.compile(r"\d+")


def _norm_title(t: str) -> str:
    return _TITLE_NUMS.sub("#", (t or "").strip().lower())


def _key(f: Dict[str, Any]) -> Tuple[str, str, str]:
    return (
        f.get("scenario_id", ""),
        f.get("severity", "info"),
        _norm_title(f.get("title", "")),
    )


def _by_key(findings: List[Dict[str, Any]]) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    return {_key(f): f for f in findings}


def diff_runs(baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    """Produce a JSON-friendly diff between two audit dicts."""
    b_idx = _by_key(baseline.get("findings", []))
    c_idx = _by_key(current.get("findings", []))

    new = [c_idx[k] for k in c_idx.keys() - b_idx.keys()]
    fixed = [b_idx[k] for k in b_idx.keys() - c_idx.keys()]
    unchanged = [c_idx[k] for k in c_idx.keys() & b_idx.keys()]

    # Scenario pass/fail transitions
    b_sc = {s["id"]: s for s in baseline.get("scenarios", [])}
    c_sc = {s["id"]: s for s in current.get("scenarios", [])}
    transitions: List[Dict[str, Any]] = []
    for sid in sorted(b_sc.keys() | c_sc.keys()):
        b = b_sc.get(sid)
        c = c_sc.get(sid)
        if b is None:
            transitions.append({"id": sid, "kind": "added", "passed": c.get("passed")})
        elif c is None:
            transitions.append({"id": sid, "kind": "removed", "passed": b.get("passed")})
        elif b.get("passed") != c.get("passed"):
            kind = "regressed" if (b.get("passed") and not c.get("passed")) else "recovered"
            transitions.append({"id": sid, "kind": kind,
                                "baseline": b.get("passed"), "current": c.get("passed")})
    # Severity by counts
    def _counts(findings: List[Dict[str, Any]]) -> Dict[str, int]:
        out = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            s = f.get("severity", "info")
            out[s] = out.get(s, 0) + 1
        return out

    return {
        "baseline_run_id": baseline.get("run_id"),
        "current_run_id": current.get("run_id"),
        "baseline_target": baseline.get("target_url"),
        "current_target": current.get("target_url"),
        "summary": {
            "new": len(new),
            "fixed": len(fixed),
            "unchanged": len(unchanged),
            "regressions": sum(1 for t in transitions if t["kind"] == "regressed"),
            "recoveries": sum(1 for t in transitions if t["kind"] == "recovered"),
        },
        "counts": {
            "baseline": _counts(baseline.get("findings", [])),
            "current": _counts(current.get("findings", [])),
        },
        "new_findings": new,
        "fixed_findings": fixed,
        "unchanged_findings": unchanged,
        "scenario_transitions": transitions,
    }


def load_run(artifacts_dir: Path, run_id: str) -> Dict[str, Any]:
    p = artifacts_dir / run_id / "report.json"
    if not p.is_file():
        raise FileNotFoundError(f"No report.json for run {run_id}")
    return json.loads(p.read_text(encoding="utf-8"))


def render_diff_markdown(diff: Dict[str, Any]) -> str:
    s = diff["summary"]
    out: List[str] = []
    out.append(f"# AuditOps Diff — `{diff['baseline_run_id']}` → `{diff['current_run_id']}`")
    out.append("")
    out.append(f"- **Target:** {diff['current_target']}")
    out.append(f"- **New:** {s['new']}  · **Fixed:** {s['fixed']}  · "
               f"**Unchanged:** {s['unchanged']}  · "
               f"**Regressions:** {s['regressions']}  · **Recoveries:** {s['recoveries']}")
    out.append("")
    out.append("## Severity counts")
    out.append("| | critical | high | medium | low | info |")
    out.append("|---|---|---|---|---|---|")
    for label in ("baseline", "current"):
        c = diff["counts"][label]
        out.append(f"| **{label}** | {c['critical']} | {c['high']} | {c['medium']} | {c['low']} | {c['info']} |")
    out.append("")
    if diff["new_findings"]:
        out.append("## 🆕 New findings")
        for f in diff["new_findings"]:
            out.append(f"- **{f.get('severity','info').upper()}** — {f.get('title')} (`{f.get('scenario_id')}`)")
        out.append("")
    if diff["fixed_findings"]:
        out.append("## ✅ Fixed findings")
        for f in diff["fixed_findings"]:
            out.append(f"- ~~{f.get('title')}~~ (`{f.get('scenario_id')}`)")
        out.append("")
    if diff["scenario_transitions"]:
        out.append("## Scenario transitions")
        for t in diff["scenario_transitions"]:
            out.append(f"- `{t['id']}` — **{t['kind']}**")
    return "\n".join(out)
