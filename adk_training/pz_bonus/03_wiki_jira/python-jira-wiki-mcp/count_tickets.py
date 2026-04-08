"""
Skrypt do zliczania ticketów w Jirze (on-premise, Bearer token).
Sprawdza liczbę ticketów w lutym i marcu 2026 z podziałem
na projekt oraz typ ticketa.
Obsługuje paginację (limit 50 per strona).

Namiary:
  JIRA_BASE_URL     = https://tapir.krakow.comarch/jira/rest/api/2
  JIRA_BEARER_TOKEN = <YOUR_JIRA_BEARER_TOKEN>
"""

import sys
import requests
from collections import defaultdict
from typing import Dict, Tuple

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ── Konfiguracja ──────────────────────────────────────────────────────────────
BASE_URL = "https://tapir.krakow.comarch/jira/rest/api/2"
BEARER_TOKEN = "<YOUR_JIRA_BEARER_TOKEN>"
PAGE_SIZE = 50  # limit API Jiry

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

MONTHS = {
    "Luty 2026":   ("2026-02-01", "2026-02-28"),
    "Marzec 2026": ("2026-03-01", "2026-03-31"),
}

TOP_N = None  # None = pokaż wszystkie; liczba np. 20 = top N

# None = wszystkie projekty; lista kluczy = filtr JQL project IN (...)
PROJECTS = [
    "BIGDATA", "OSSNGSA", "OSSSD", "OSSC", "OSSCMF", "OSSDCIM", "OSSDL",
    "OSSDEF", "OSSFSM", "OSSINFRA", "OSSIPAM", "OSSKTD", "OSSMED", "OSSMIG",
    "OSSMFC", "OSSPHY", "OSSPLA", "OSSPFM", "OSSDM", "OSSDMS", "OSSFIX",
    "OSSGIS", "OSSNGSF", "OSSCON", "OSSPT", "OSSSI", "OSSPDMBIM", "OSSRAN",
    "OSSRECO", "OSSRF", "OSSRM", "OSSSELEN", "OSSTP", "OSSTRAIL", "OSSTPT",
    "OSSLF", "OSSMU", "OSSRANIF", "TELCOAI", "OSSWEB",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def probe_api() -> None:
    """Sprawdza połączenie i wypisuje dostępne projekty (max 5)."""
    print("\n── PROBE: /serverInfo ──")
    url = f"{BASE_URL}/serverInfo"
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        r.raise_for_status()
        info = r.json()
        print(f"  Wersja Jiry : {info.get('version', 'N/A')}")
        print(f"  Nazwa       : {info.get('serverTitle', 'N/A')}")
        print(f"  Base URL    : {info.get('baseUrl', 'N/A')}")
    except requests.RequestException as e:
        print(f"  [WARN] serverInfo niedostępne: {e}")

    print("\n── PROBE: projekty (max 5) ──")
    url = f"{BASE_URL}/project"
    try:
        r = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        r.raise_for_status()
        projects = r.json()
        for p in projects[:5]:
            print(f"  {p.get('key', '?'):15s}  {p.get('name', '?')}")
        if len(projects) > 5:
            print(f"  ... i {len(projects) - 5} więcej projektów")
    except requests.RequestException as e:
        print(f"  [ERROR] Nie udało się pobrać projektów: {e}")


def fetch_period(label: str, date_from: str, date_to: str) -> Dict:
    """
    Pobiera wszystkie tickety w danym przedziale datowym (paginacja).
    Zwraca słownik:
      {
        "total": int,
        "by_project":   {project_key: count},
        "by_issuetype": {type_name: count},
      }
    """
    proj_filter = ""
    if PROJECTS:
        keys = ", ".join(PROJECTS)
        proj_filter = f"project IN ({keys}) AND "
    jql = f'{proj_filter}created >= "{date_from}" AND created <= "{date_to}" ORDER BY created ASC'
    url = f"{BASE_URL}/search"

    by_project: Dict[str, int]   = defaultdict(int)
    by_issuetype: Dict[str, int] = defaultdict(int)

    start_at = 0
    total_fetched = 0
    total_reported = None

    print(f"\n── {label}  [{date_from} → {date_to}] ──")

    while True:
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": PAGE_SIZE,
            "fields": "project,issuetype",
        }
        try:
            r = requests.get(url, headers=HEADERS, params=params,
                             verify=False, timeout=30)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            print(f"  [ERROR] startAt={start_at}: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"  Response body: {e.response.text[:400]}")
            break

        if total_reported is None:
            total_reported = data.get("total", 0)
            print(f"  Jira raportuje łącznie: {total_reported} ticketów")

        issues = data.get("issues", [])
        if not issues:
            break

        for issue in issues:
            fields = issue.get("fields", {})
            proj = fields.get("project", {})
            itype = fields.get("issuetype", {})
            by_project[proj.get("key", "UNKNOWN")] += 1
            by_issuetype[itype.get("name", "Unknown")] += 1

        total_fetched += len(issues)
        pages_done = start_at // PAGE_SIZE + 1
        print(f"  Strona {pages_done:3d} | pobranych: {len(issues):3d} | łącznie: {total_fetched:5d}")

        if total_fetched >= total_reported:
            break

        start_at += PAGE_SIZE

    return {
        "total": total_fetched,
        "by_project": dict(by_project),
        "by_issuetype": dict(by_issuetype),
    }


def print_breakdown(title: str, counts: Dict[str, int], top_n) -> None:
    """Wypisuje posortowaną tabelkę breakdown z wierszem SUMA."""
    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    shown = sorted_items if top_n is None else sorted_items[:top_n]
    total = sum(counts.values())
    label = f"Wszystkie {len(sorted_items)}" if top_n is None else f"Top {top_n} z {len(sorted_items)}"
    print(f"\n  {title}  ({label}):")
    print(f"  {'Nazwa':<30s}  {'Liczba':>7s}  {'%':>6s}")
    print(f"  {'-'*30}  {'-'*7}  {'-'*6}")
    for name, cnt in shown:
        pct = cnt / total * 100 if total else 0
        print(f"  {name:<30s}  {cnt:>7d}  {pct:>5.1f}%")
    if top_n is not None and len(sorted_items) > top_n:
        rest = sum(c for _, c in sorted_items[top_n:])
        pct = rest / total * 100 if total else 0
        print(f"  {'... pozostałe (' + str(len(sorted_items)-top_n) + ' pozycji)':<30s}  {rest:>7d}  {pct:>5.1f}%")
    print(f"  {'─'*30}  {'─'*7}  {'─'*6}")
    print(f"  {'SUMA':<30s}  {total:>7d}  100.0%")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("=" * 65)
    print("  ZLICZANIE TICKETÓW JIRA  (luty / marzec 2026)")
    print("  z podziałem na projekt i typ ticketa")
    print("=" * 65)
    print(f"  Endpoint: {BASE_URL}")

    probe_api()

    all_results = {}
    for label, (date_from, date_to) in MONTHS.items():
        all_results[label] = fetch_period(label, date_from, date_to)

    # ── Podsumowanie globalne ─────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  WYNIKI ŁĄCZNE")
    print("=" * 65)
    for label, res in all_results.items():
        print(f"  {label:<20s}: {res['total']:>6d} ticketów")

    # ── Breakdown per miesiąc ─────────────────────────────────────────────────
    for label, res in all_results.items():
        print("\n" + "=" * 65)
        print(f"  BREAKDOWN: {label}  (łącznie {res['total']})")
        print("=" * 65)
        print_breakdown(f"Top {TOP_N} projektów", res["by_project"], TOP_N)
        print_breakdown(f"Typy ticketów", res["by_issuetype"], TOP_N)

    # ── Porównanie projektów między miesiącami ────────────────────────────────
    labels = list(all_results.keys())
    if len(labels) == 2:
        print("\n" + "=" * 65)
        print(f"  PORÓWNANIE PROJEKTÓW: {labels[0]} vs {labels[1]}")
        print("=" * 65)
        all_projects = set(all_results[labels[0]]["by_project"]) | \
                       set(all_results[labels[1]]["by_project"])
        rows = []
        for proj in all_projects:
            a = all_results[labels[0]]["by_project"].get(proj, 0)
            b = all_results[labels[1]]["by_project"].get(proj, 0)
            rows.append((proj, a, b, b - a))
        rows.sort(key=lambda x: x[1] + x[2], reverse=True)
        shown_rows = rows if TOP_N is None else rows[:TOP_N]
        print(f"  {'Projekt':<20s}  {labels[0]:>12s}  {labels[1]:>13s}  {'Δ':>6s}")
        print(f"  {'-'*20}  {'-'*12}  {'-'*13}  {'-'*6}")
        for proj, a, b, delta in shown_rows:
            sign = "+" if delta >= 0 else ""
            print(f"  {proj:<20s}  {a:>12d}  {b:>13d}  {sign}{delta:>5d}")
        if TOP_N is not None and len(rows) > TOP_N:
            print(f"  ... i {len(rows)-TOP_N} więcej projektów")
        sum_a = sum(r[1] for r in rows)
        sum_b = sum(r[2] for r in rows)
        print(f"  {'─'*20}  {'─'*12}  {'─'*13}  {'─'*6}")
        print(f"  {'SUMA':<20s}  {sum_a:>12d}  {sum_b:>13d}  {'+' if sum_b-sum_a >= 0 else ''}{sum_b-sum_a:>5d}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()

