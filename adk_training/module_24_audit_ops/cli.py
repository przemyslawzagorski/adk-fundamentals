"""AuditOps CLI — runs an audit headless and exits with a CI-friendly code.

Examples:
    python -m adk_training.module_24_audit_ops.cli \\
        --url https://staging.acme.test \\
        --allow-domain acme.test \\
        --fail-on high \\
        --report-dir ./audit_artifacts \\
        --junit ./audit_artifacts/junit.xml

Exit codes:
    0  no findings at or above ``--fail-on``
    1  findings >= threshold
    2  configuration / runtime error
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Optional
from xml.sax.saxutils import escape

from .auth import AuthContext, make_auth
from .config import AuditConfig
from .pentest_agent import auto_pentest, guided_pentest
from .reporter import write_report
from .safety import DisclaimerAck
from . import wiki as wiki_mod

_SEV_ORDER = ["info", "low", "medium", "high", "critical"]


def _max_severity(findings: List[dict]) -> str:
    rank = {s: i for i, s in enumerate(_SEV_ORDER)}
    return max((f.get("severity", "info") for f in findings), key=lambda s: rank.get(s, 0), default="info")


def _to_junit(audit, threshold: str) -> str:
    """Render audit as a minimal JUnit XML report (one testcase per scenario)."""
    rank = {s: i for i, s in enumerate(_SEV_ORDER)}
    cutoff = rank.get(threshold, 3)
    cases = []
    failures = 0
    for sc in audit.scenarios:
        bad = [f for f in sc["findings"] if rank.get(f.get("severity", "info"), 0) >= cutoff]
        if bad or not sc.get("passed", True):
            failures += 1
            details = "\n".join(f"- [{f.get('severity')}] {f.get('title')}" for f in bad) or sc.get("error", "")
            cases.append(
                f'<testcase classname="auditops" name="{escape(sc["name"])}" time="{sc.get("duration_s",0):.2f}">'
                f'<failure message="{escape(sc.get("error") or "findings exceeded threshold")}">'
                f'{escape(details)}</failure></testcase>'
            )
        else:
            cases.append(
                f'<testcase classname="auditops" name="{escape(sc["name"])}" time="{sc.get("duration_s",0):.2f}"/>'
            )
    body = "".join(cases)
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<testsuite name="auditops" tests="{len(cases)}" failures="{failures}" '
        f'time="{audit.duration_s:.2f}">{body}</testsuite>'
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="auditops", description="LLM-driven web pentest CI runner.")
    p.add_argument("--url", required=True, help="Target URL (must be in allowed domains).")
    p.add_argument("--mode", choices=["auto", "guided"], default="auto")
    p.add_argument("--scenario-nl", help="Natural-language scenario for --mode guided")
    p.add_argument("--allow-domain", action="append", default=[],
                   help="Allowed domain (repeat). Defaults to AUDITOPS_ALLOWED_DOMAINS env var.")
    p.add_argument("--fail-on", choices=_SEV_ORDER, default="high",
                   help="Minimum severity that fails the run (default: high).")
    p.add_argument("--report-dir", help="Override AUDITOPS_ARTIFACTS_DIR.")
    p.add_argument("--cookie", action="append", default=[],
                   help='Auth cookie as "name=value;domain=.example.com" (repeatable).')
    p.add_argument("--header", action="append", default=[],
                   help='Auth header as "Name: value" (repeatable).')
    p.add_argument("--junit", help="Write JUnit XML report to this path.")
    p.add_argument("--user-id", default="ci", help="User id recorded in disclaimer ack.")
    return p


def _parse_cookie(spec: str) -> dict:
    """Parse 'name=value;domain=.example.com;path=/' style cookie spec."""
    parts = [s.strip() for s in spec.split(";") if s.strip()]
    if not parts:
        raise ValueError(f"empty cookie spec: {spec!r}")
    name, _, value = parts[0].partition("=")
    if not name:
        raise ValueError(f"cookie missing name: {spec!r}")
    out = {"name": name, "value": value, "path": "/"}
    for kv in parts[1:]:
        k, _, v = kv.partition("=")
        out[k.strip().lower()] = v.strip()
    out.setdefault("domain", "")
    return out


def _build_auth(args) -> Optional[AuthContext]:
    if not args.cookie and not args.header:
        return None
    cookies = [_parse_cookie(c) for c in args.cookie]
    headers = {}
    for h in args.header:
        k, _, v = h.partition(":")
        if not k or not v:
            raise SystemExit(f"invalid --header {h!r}, expected 'Name: value'")
        headers[k.strip()] = v.strip()
    return make_auth(label="ci-auth", cookies=cookies, headers=headers)


def _build_lint_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="auditops wiki-lint",
                                description="Lint the audit wiki (broken links, orphan stubs).")
    p.add_argument("--report-dir", help="Override AUDITOPS_ARTIFACTS_DIR.")
    p.add_argument("--target", help="Limit lint to a single target slug or URL.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable.")
    return p


def _wiki_lint_main(argv: Optional[List[str]]) -> int:
    args = _build_lint_parser().parse_args(argv)
    if args.report_dir:
        os.environ["AUDITOPS_ARTIFACTS_DIR"] = args.report_dir
    cfg = AuditConfig.from_env()
    if args.target:
        if "://" in args.target:
            issues = wiki_mod.lint_wiki(cfg.artifacts_dir, args.target)
            results = {wiki_mod.target_slug(args.target): [i.to_dict() for i in issues]}
        else:
            issues = wiki_mod.lint_wiki(cfg.artifacts_dir, f"https://{args.target}/")
            results = {args.target: [i.to_dict() for i in issues]}
    else:
        results = wiki_mod.lint_all(cfg.artifacts_dir)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("wiki-lint: clean (no targets or no issues).")
        for slug, issues in results.items():
            print(f"\n[{slug}] {len(issues)} issue(s)")
            for i in issues:
                print(f"  - {i['kind']}: {i['path']} — {i['detail']}")
    has_issues = any(results.values())
    return 1 if has_issues else 0


async def _run(args) -> int:
    if args.allow_domain:
        os.environ["AUDITOPS_ALLOWED_DOMAINS"] = ",".join(args.allow_domain)
    if args.report_dir:
        os.environ["AUDITOPS_ARTIFACTS_DIR"] = args.report_dir
    # CI doesn't want a UI prompt — disclaimer is implicit by running this CLI.
    os.environ["AUDITOPS_REQUIRE_DISCLAIMER"] = "0"

    cfg = AuditConfig.from_env()
    if not cfg.allowed_domains:
        print("ERROR: no allowed domains configured. Use --allow-domain.", file=sys.stderr)
        return 2

    ack = DisclaimerAck(
        acknowledged=True, user_id=args.user_id, target_url=args.url,
        timestamp=time.time(),
        statement="CI run — operator confirms authorization to test the target.",
    )
    auth = _build_auth(args)

    if args.mode == "guided":
        if not args.scenario_nl:
            print("ERROR: --scenario-nl is required when --mode guided", file=sys.stderr)
            return 2
        audit = await guided_pentest(args.url, args.scenario_nl, cfg, ack=ack, auth=auth)
    else:
        audit = await auto_pentest(args.url, cfg, ack=ack, auth=auth)

    audit_dict = audit.to_dict()
    paths = write_report(audit_dict, cfg)
    print(f"report: {paths['markdown_path']}")
    print(f"json:   {paths['json_path']}")

    # V2: wiki update — best-effort, never fails the run.
    try:
        wiki_mod.record_run(cfg.artifacts_dir, audit_dict)
    except Exception as e:
        print(f"WARN: wiki update failed: {e}", file=sys.stderr)

    if args.junit:
        Path(args.junit).parent.mkdir(parents=True, exist_ok=True)
        Path(args.junit).write_text(_to_junit(audit, args.fail_on), encoding="utf-8")
        print(f"junit:  {args.junit}")

    rank = {s: i for i, s in enumerate(_SEV_ORDER)}
    cutoff = rank[args.fail_on]
    worst = _max_severity(audit.findings)
    print(f"max severity: {worst}  threshold: {args.fail_on}  findings: {len(audit.findings)}")
    return 1 if rank.get(worst, 0) >= cutoff else 0


def main(argv: Optional[List[str]] = None) -> int:
    raw = sys.argv[1:] if argv is None else list(argv)
    if raw and raw[0] == "wiki-lint":
        return _wiki_lint_main(raw[1:])
    args = _build_parser().parse_args(raw)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
