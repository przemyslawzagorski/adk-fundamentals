"""Audit Wiki — Karpathy LLM-Wiki pattern, deterministic Python writer.

Layout (per target host slug, under ``cfg.artifacts_dir/wiki/<slug>/``)::

    index.md             ← always-current TOC, hot-cache for the planner
    log.md               ← append-only chronological event log
    findings/F-<slug>.md ← entity page per (severity, normalized_title)
    runs/<run_id>.md     ← short stub linking to the actual report
    synthesis/           ← LLM-authored, HITL-gated (created by api endpoint)

Design rules (lessons learned from the gist comment war):

1. **Python writes the wiki.** The LLM never edits index.md, log.md, or
   findings/*. That removes the read-your-own-prose corruption risk.
2. **runs/<id>.md is immutable.** Existing files are not rewritten — we only
   append to log.md and update index.md / findings/*.
3. **Findings are atomic** (Zettelkasten-style stable ID). Each new run adds
   one line to the existing finding page; the page never deletes prior runs.
4. **Lint** (`lint_wiki`) flags broken links and orphans — operators run it
   in CI to keep the wiki healthy.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


_SAFE_SLUG_RE = re.compile(r"[^a-z0-9._-]+")
_TITLE_NUMS = re.compile(r"\d+")
_SEV_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


# ----------------------------- helpers --------------------------------------


def target_slug(url: str) -> str:
    """Stable host slug from a URL — empty hostname falls back to ``unknown``."""
    host = (urlparse(url).hostname or "unknown").lower()
    return _SAFE_SLUG_RE.sub("-", host).strip("-") or "unknown"


def finding_slug(severity: str, title: str) -> str:
    norm = _TITLE_NUMS.sub("#", (title or "").strip().lower())
    norm = _SAFE_SLUG_RE.sub("-", norm).strip("-")
    sev = (severity or "info").strip().lower()
    return f"{sev}-{norm or 'untitled'}"[:80]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ----------------------------- writer ---------------------------------------


@dataclass
class WikiPaths:
    root: Path           # wiki/<slug>
    index: Path          # wiki/<slug>/index.md
    log: Path            # wiki/<slug>/log.md
    findings_dir: Path   # wiki/<slug>/findings/
    runs_dir: Path       # wiki/<slug>/runs/
    synthesis_dir: Path  # wiki/<slug>/synthesis/


def wiki_paths(artifacts_dir: Path, target_url: str) -> WikiPaths:
    root = artifacts_dir / "wiki" / target_slug(target_url)
    return WikiPaths(
        root=root,
        index=root / "index.md",
        log=root / "log.md",
        findings_dir=root / "findings",
        runs_dir=root / "runs",
        synthesis_dir=root / "synthesis",
    )


# ---- run stub --------------------------------------------------------------


def _render_run_stub(audit: Dict[str, Any]) -> str:
    run_id = audit.get("run_id") or "unknown"
    findings = audit.get("findings") or []
    counts = {sev: 0 for sev in _SEV_RANK}
    for f in findings:
        sev = (f.get("severity") or "info").lower()
        counts[sev] = counts.get(sev, 0) + 1
    lines = [
        f"# Run `{run_id}`",
        "",
        f"- **Target:** {audit.get('target_url')}",
        f"- **Started:** {audit.get('started_at')}",
        f"- **Duration:** {audit.get('duration_s', 0):.1f}s",
        "- **Severity:** "
        + ", ".join(f"{k}={v}" for k, v in counts.items() if v),
        f"- **Report:** [report.md](../../../{run_id}/report.md)",
        "",
        "## Findings recorded",
    ]
    if not findings:
        lines.append("- (none)")
    for f in findings:
        sev = f.get("severity", "info")
        title = f.get("title", "")
        slug = finding_slug(sev, title)
        lines.append(f"- [{sev}] [{title}](../findings/F-{slug}.md)")
    return "\n".join(lines) + "\n"


# ---- finding entity page ---------------------------------------------------


def _render_finding_page(finding: Dict[str, Any], occurrences: List[Dict[str, str]]) -> str:
    sev = finding.get("severity", "info")
    title = finding.get("title", "(untitled)")
    owasp = finding.get("owasp") or "(custom)"
    lines = [
        f"# {title}",
        "",
        f"- **Severity:** {sev}",
        f"- **OWASP:** {owasp}",
        f"- **Scenario id:** `{finding.get('scenario_id', '')}`",
        f"- **First seen:** {occurrences[0]['ts'] if occurrences else _now_iso()}",
        f"- **Last seen:** {occurrences[-1]['ts'] if occurrences else _now_iso()}",
        f"- **Occurrences:** {len(occurrences)}",
        "",
        "## Run history",
    ]
    for occ in occurrences:
        lines.append(f"- {occ['ts']} — [{occ['run_id']}](../runs/{occ['run_id']}.md)")
    return "\n".join(lines) + "\n"


_FINDING_OCC_RE = re.compile(
    r"^- (?P<ts>.+? UTC) — \[(?P<run>[^\]]+)\]",
    re.MULTILINE,
)


def _parse_finding_occurrences(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    return [{"ts": m["ts"], "run_id": m["run"]} for m in _FINDING_OCC_RE.finditer(text)]


# ---- index.md (rebuilt from disk to guarantee accuracy) --------------------


def _rebuild_index(paths: WikiPaths, target_url: str) -> str:
    runs = sorted([p.stem for p in paths.runs_dir.glob("*.md")], reverse=True)
    findings = sorted(p.stem for p in paths.findings_dir.glob("F-*.md"))

    lines = [
        f"# Audit Wiki — `{target_url}`",
        "",
        f"_Generated by `wiki._rebuild_index` at {_now_iso()}_  ",
        f"_Slug: `{paths.root.name}`_",
        "",
        "## Stats",
        f"- Runs recorded: **{len(runs)}**",
        f"- Distinct findings: **{len(findings)}**",
        "",
        "## Recent runs (newest first)",
    ]
    for r in runs[:25]:
        lines.append(f"- [{r}](runs/{r}.md)")
    if not runs:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Findings (alphabetical by severity-title)")
    for fid in findings:
        lines.append(f"- [{fid[2:]}](findings/{fid}.md)")
    if not findings:
        lines.append("- (none)")
    lines.append("")
    syn = sorted(paths.synthesis_dir.glob("*.md")) if paths.synthesis_dir.is_dir() else []
    lines.append("## Synthesis (LLM-authored, human-approved)")
    for s in syn:
        lines.append(f"- [{s.stem}](synthesis/{s.name})")
    if not syn:
        lines.append("- (none)")
    return "\n".join(lines) + "\n"


# ---- log.md (append-only) --------------------------------------------------


def _append_log(paths: WikiPaths, audit: Dict[str, Any]) -> None:
    counts = {sev: 0 for sev in _SEV_RANK}
    for f in audit.get("findings", []):
        sev = (f.get("severity") or "info").lower()
        counts[sev] = counts.get(sev, 0) + 1
    sev_str = " ".join(f"{k}={v}" for k, v in counts.items() if v) or "none"
    line = (
        f"## [{_now_iso()}] run | {audit.get('run_id')} | "
        f"findings={len(audit.get('findings', []))} | {sev_str}\n"
    )
    paths.log.parent.mkdir(parents=True, exist_ok=True)
    if not paths.log.is_file():
        paths.log.write_text(f"# Audit log\n\n{line}", encoding="utf-8")
    else:
        with paths.log.open("a", encoding="utf-8") as f:
            f.write(line)


# ----------------------------- public API -----------------------------------


def record_run(artifacts_dir: Path, audit: Dict[str, Any]) -> WikiPaths:
    """Idempotently update wiki for a completed audit.

    - never rewrites a previously recorded run stub,
    - merges new finding occurrences into existing entity pages,
    - rebuilds index.md from disk every call (cheap, accurate),
    - appends one line to log.md.
    """
    target_url = audit.get("target_url") or ""
    paths = wiki_paths(artifacts_dir, target_url)
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.findings_dir.mkdir(parents=True, exist_ok=True)
    paths.runs_dir.mkdir(parents=True, exist_ok=True)
    paths.synthesis_dir.mkdir(parents=True, exist_ok=True)

    run_id = audit.get("run_id") or "unknown"
    run_stub = paths.runs_dir / f"{run_id}.md"
    if not run_stub.is_file():
        _write(run_stub, _render_run_stub(audit))

    now_iso = _now_iso()
    for f in audit.get("findings", []):
        sev = f.get("severity", "info")
        title = f.get("title", "")
        slug = finding_slug(sev, title)
        page = paths.findings_dir / f"F-{slug}.md"
        existing = _parse_finding_occurrences(_read(page))
        # Skip if this run is already recorded for this finding (idempotent).
        if any(occ["run_id"] == run_id for occ in existing):
            continue
        existing.append({"ts": now_iso, "run_id": run_id})
        _write(page, _render_finding_page(f, existing))

    _append_log(paths, audit)
    _write(paths.index, _rebuild_index(paths, target_url))
    return paths


# ----------------------------- reader (V3 input) ----------------------------


def history_skill_text(artifacts_dir: Path, target_url: str, *, max_findings: int = 25) -> str:
    """Render a synthetic SKILL.md body for the dynamic ``audit-history`` skill.

    Returns an empty string when no wiki exists yet for the target — the
    caller treats that as "skip injection".
    """
    paths = wiki_paths(artifacts_dir, target_url)
    if not paths.index.is_file():
        return ""

    finding_files = sorted(paths.findings_dir.glob("F-*.md"))
    runs = sorted((p.stem for p in paths.runs_dir.glob("*.md")), reverse=True)

    lines = [
        f"Prior audit history for `{target_url}` (read-only, summarized).",
        "",
        f"- Runs recorded: {len(runs)}",
        f"- Distinct findings: {len(finding_files)}",
        "",
        "Known findings (do NOT re-test from scratch — confirm or refute):",
    ]
    items: List[str] = []
    for ff in finding_files[:max_findings]:
        text = _read(ff)
        # Title is the first H1.
        m = re.search(r"^# (.+)$", text, re.MULTILINE)
        sev_m = re.search(r"\*\*Severity:\*\*\s*([a-z]+)", text)
        occ_m = re.search(r"\*\*Occurrences:\*\*\s*(\d+)", text)
        title = m.group(1).strip() if m else ff.stem
        sev = sev_m.group(1) if sev_m else "info"
        occ = occ_m.group(1) if occ_m else "1"
        items.append(f"- [{sev}] {title} (seen {occ}×)")
    items.sort(key=lambda s: _SEV_RANK.get(s.split("]")[0][2:].strip(), 9))
    lines.extend(items)
    lines.append("")
    lines.append(
        "Planning hints: prefer scenarios that confirm whether a known finding "
        "is *still* present (regression evidence) over speculative new probes."
    )
    return "\n".join(lines)


# ----------------------------- lint -----------------------------------------


@dataclass
class LintIssue:
    kind: str          # "broken_link" | "orphan_finding" | "missing_run_stub"
    path: str
    detail: str

    def to_dict(self) -> Dict[str, str]:
        return {"kind": self.kind, "path": self.path, "detail": self.detail}


_MD_LINK_RE = re.compile(r"\]\(([^)]+)\)")


def lint_wiki(artifacts_dir: Path, target_url: str) -> List[LintIssue]:
    """Walk the per-target wiki and report integrity issues.

    Cheap, deterministic, no LLM. Designed to be called from CLI in CI.
    """
    paths = wiki_paths(artifacts_dir, target_url)
    issues: List[LintIssue] = []
    if not paths.root.is_dir():
        return issues

    finding_pages = list(paths.findings_dir.glob("F-*.md"))
    run_stubs = {p.stem for p in paths.runs_dir.glob("*.md")}

    # 1) Broken links inside finding pages and run stubs.
    for md in [*finding_pages, *paths.runs_dir.glob("*.md"), paths.index]:
        if not md.is_file():
            continue
        text = _read(md)
        for link in _MD_LINK_RE.findall(text):
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (md.parent / link).resolve()
            if not target.exists():
                issues.append(LintIssue(
                    kind="broken_link",
                    path=str(md.relative_to(paths.root)),
                    detail=link,
                ))

    # 2) Orphan finding pages (no run stub references them).
    referenced_runs: set[str] = set()
    for fp in finding_pages:
        for occ in _parse_finding_occurrences(_read(fp)):
            referenced_runs.add(occ["run_id"])
    missing = referenced_runs - run_stubs
    for run_id in sorted(missing):
        issues.append(LintIssue(
            kind="missing_run_stub",
            path=f"runs/{run_id}.md",
            detail=f"finding pages reference run {run_id} but stub is missing",
        ))

    return issues


def lint_all(artifacts_dir: Path) -> Dict[str, List[Dict[str, str]]]:
    """Lint every target wiki under artifacts_dir/wiki/."""
    out: Dict[str, List[Dict[str, str]]] = {}
    base = artifacts_dir / "wiki"
    if not base.is_dir():
        return out
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        # Reverse-engineer a target_url from slug — only the slug matters here.
        fake_url = f"https://{child.name}/"
        issues = lint_wiki(artifacts_dir, fake_url)
        if issues:
            out[child.name] = [i.to_dict() for i in issues]
    return out
