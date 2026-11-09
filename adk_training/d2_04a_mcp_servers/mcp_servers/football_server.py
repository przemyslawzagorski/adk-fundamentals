"""
MCP Server: Football (piłka nożna)
===================================
Serwer MCP z danymi piłkarskimi z darmowego API football-data.org (v4, bez klucza).
Gdy limit free API zostanie przekroczony, używa backupu z API-FOOTBALL (free tier).

Narzędzia:
- get_league_standings() — tabela wybranej ligi
- get_team_info() — info o drużynie po nazwie
- get_today_matches() — dzisiejsze mecze w wybranej lidze

Darmowe API: https://www.thesportsdb.com/api.php (open, bez rejestracji)

Uruchomienie standalone (do testów):
    python football_server.py
"""

from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Football")

# TheSportsDB — darmowe API bez klucza (klucz testowy: "3")
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

# Mapowanie popularnych lig na ID w TheSportsDB
LEAGUE_IDS = {
    "premier league": "4328",
    "la liga": "4335",
    "bundesliga": "4331",
    "serie a": "4332",
    "ligue 1": "4334",
    "ekstraklasa": "4422",
    "champions league": "4480",
    "eredivisie": "4337",
}


@mcp.tool()
def get_league_standings(league_name: str, season: str = "2024-2025") -> str:
    """Pobiera tabelę (standings) wybranej ligi piłkarskiej.
    Dostępne ligi: Premier League, La Liga, Bundesliga, Serie A, Ligue 1,
    Ekstraklasa, Champions League, Eredivisie.
    Sezon w formacie: 2024-2025."""
    league_key = league_name.lower().strip()
    league_id = LEAGUE_IDS.get(league_key)
    if not league_id:
        available = ", ".join(LEAGUE_IDS.keys())
        return f"Nieznana liga: '{league_name}'. Dostępne: {available}"

    url = f"{BASE_URL}/lookuptable.php?l={league_id}&s={season}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        table = data.get("table")
        if not table:
            return f"Brak danych dla {league_name} w sezonie {season}"

        lines = []
        for row in table[:20]:
            pos = row.get("intRank", "?")
            name = row.get("strTeam", "?")
            played = row.get("intPlayed", 0)
            wins = row.get("intWin", 0)
            draws = row.get("intDraw", 0)
            losses = row.get("intLoss", 0)
            points = row.get("intPoints", 0)
            gf = row.get("intGoalsFor", 0)
            ga = row.get("intGoalsAgainst", 0)
            lines.append(
                f"  {pos}. {name} — {points} pkt "
                f"({played} meczy: {wins}W {draws}D {losses}L, bramki: {gf}:{ga})"
            )
        header = f"Tabela {league_name} ({season}):"
        return header + "\n" + "\n".join(lines)
    except Exception as e:
        return f"Błąd pobierania tabeli {league_name}: {str(e)}"


@mcp.tool()
def get_team_info(team_name: str) -> str:
    """Pobiera informacje o drużynie piłkarskiej po nazwie (np. Barcelona, Real Madrid, Legia Warszawa)."""
    url = f"{BASE_URL}/searchteams.php?t={team_name}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        teams = data.get("teams")
        if not teams:
            return f"Nie znaleziono drużyny: {team_name}"

        team = teams[0]
        name = team.get("strTeam", "?")
        alt_name = team.get("strAlternate", "")
        league = team.get("strLeague", "?")
        country = team.get("strCountry", "?")
        stadium = team.get("strStadium", "?")
        stadium_cap = team.get("intStadiumCapacity", "?")
        year = team.get("intFormedYear", "?")
        desc = team.get("strDescriptionPL") or team.get("strDescriptionEN") or "Brak opisu"
        # Skróć opis do 300 znaków
        if len(desc) > 300:
            desc = desc[:300] + "..."

        return (
            f"🏟️ {name} ({alt_name})\n"
            f"  Liga: {league} ({country})\n"
            f"  Stadion: {stadium} (pojemność: {stadium_cap})\n"
            f"  Założony: {year}\n"
            f"  Opis: {desc}"
        )
    except Exception as e:
        return f"Błąd pobierania info o {team_name}: {str(e)}"


@mcp.tool()
def get_next_matches(team_name: str) -> str:
    """Pobiera najbliższe zaplanowane mecze danej drużyny piłkarskiej."""
    # Najpierw szukamy ID drużyny
    search_url = f"{BASE_URL}/searchteams.php?t={team_name}"
    try:
        resp = httpx.get(search_url, timeout=10)
        resp.raise_for_status()
        teams = resp.json().get("teams")
        if not teams:
            return f"Nie znaleziono drużyny: {team_name}"

        team_id = teams[0]["idTeam"]
        team_full = teams[0]["strTeam"]

        # Pobierz następne mecze
        events_url = f"{BASE_URL}/eventsnext.php?id={team_id}"
        resp2 = httpx.get(events_url, timeout=10)
        resp2.raise_for_status()
        events = resp2.json().get("events")
        if not events:
            return f"Brak zaplanowanych meczy dla {team_full}"

        lines = []
        for ev in events[:5]:
            date = ev.get("dateEvent", "?")
            time = ev.get("strTime", "?")
            home = ev.get("strHomeTeam", "?")
            away = ev.get("strAwayTeam", "?")
            league = ev.get("strLeague", "?")
            lines.append(f"  📅 {date} {time[:5]} — {home} vs {away} ({league})")

        return f"Najbliższe mecze {team_full}:\n" + "\n".join(lines)
    except Exception as e:
        return f"Błąd pobierania meczy {team_name}: {str(e)}"


@mcp.tool()
def get_last_results(team_name: str) -> str:
    """Pobiera ostatnie wyniki meczów danej drużyny piłkarskiej."""
    search_url = f"{BASE_URL}/searchteams.php?t={team_name}"
    try:
        resp = httpx.get(search_url, timeout=10)
        resp.raise_for_status()
        teams = resp.json().get("teams")
        if not teams:
            return f"Nie znaleziono drużyny: {team_name}"

        team_id = teams[0]["idTeam"]
        team_full = teams[0]["strTeam"]

        results_url = f"{BASE_URL}/eventslast.php?id={team_id}"
        resp2 = httpx.get(results_url, timeout=10)
        resp2.raise_for_status()
        results = resp2.json().get("results")
        if not results:
            return f"Brak wyników dla {team_full}"

        lines = []
        for ev in results[:5]:
            date = ev.get("dateEvent", "?")
            home = ev.get("strHomeTeam", "?")
            away = ev.get("strAwayTeam", "?")
            score_h = ev.get("intHomeScore", "?")
            score_a = ev.get("intAwayScore", "?")
            league = ev.get("strLeague", "?")
            lines.append(
                f"  {date} — {home} {score_h}:{score_a} {away} ({league})"
            )

        return f"Ostatnie wyniki {team_full}:\n" + "\n".join(lines)
    except Exception as e:
        return f"Błąd pobierania wyników {team_name}: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
