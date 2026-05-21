"""
GitHub Action runner: code review PR diffa.

Uruchom w workflow:
  python ci_review.py --diff-file=pr.diff --output=review.json --fail-on=major

Exit codes:
  0 = approve
  1 = found issues at/above --fail-on threshold
  2 = error wykonania
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from dotenv import load_dotenv

_HERE = pathlib.Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env", override=False)

sys.path.insert(0, str(_HERE))

SEVERITY_ORDER = {"nit": 0, "minor": 1, "major": 2, "critical": 3}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff-file", required=True)
    parser.add_argument("--output", default="review.json")
    parser.add_argument("--fail-on", default="major", choices=list(SEVERITY_ORDER))
    parser.add_argument("--repo-context", default="")
    args = parser.parse_args()

    diff_path = pathlib.Path(args.diff_file)
    if not diff_path.exists():
        print(f"ERROR: diff file not found: {diff_path}", file=sys.stderr)
        return 2

    diff = diff_path.read_text(encoding="utf-8")
    if not diff.strip():
        print("Empty diff — nothing to review")
        pathlib.Path(args.output).write_text(json.dumps({"approval": "approve", "issues": []}), encoding="utf-8")
        return 0

    from tools import code_review_pr  # po sys.path
    raw = code_review_pr(diff=diff, repo_context=args.repo_context)
    pathlib.Path(args.output).write_text(raw, encoding="utf-8")

    try:
        review = json.loads(raw)
    except json.JSONDecodeError:
        print(f"ERROR: invalid JSON from review:\n{raw}", file=sys.stderr)
        return 2

    if "error" in review:
        print(f"REVIEW ERROR: {review['error']}: {review.get('detail', '')}", file=sys.stderr)
        return 2

    threshold = SEVERITY_ORDER[args.fail_on]
    blocking = [i for i in review.get("issues", [])
                if SEVERITY_ORDER.get(i.get("severity", "nit"), 0) >= threshold]

    print(f"\n=== AI Code Review ===")
    print(f"Approval: {review.get('approval')}")
    print(f"Summary: {review.get('summary')}")
    print(f"Issues: {len(review.get('issues', []))} (blocking >= {args.fail_on}: {len(blocking)})\n")
    for i in review.get("issues", []):
        print(f"  [{i['severity']:8}] {i['file']}:{i['line']} ({i['category']})")
        print(f"             {i['description']}")
        print(f"      FIX: {i['suggested_fix']}\n")

    if blocking:
        print(f"\nFAILING build: {len(blocking)} issue(s) at >= {args.fail_on}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
