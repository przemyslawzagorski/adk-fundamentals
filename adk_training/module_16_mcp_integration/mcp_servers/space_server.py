"""
MCP Server: Space (ISS Position, Astronauts)
=============================================
Serwer MCP udostępniający dane kosmiczne z darmowych API.

Narzędzia:
- get_iss_position() — aktualna pozycja ISS
- get_astronauts_in_space() — lista astronautów na orbicie

Uruchomienie standalone (do testów):
    python space_server.py
"""

from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Space")


@mcp.tool()
def get_iss_position() -> str:
    """Pobiera aktualną pozycję Międzynarodowej Stacji Kosmicznej (ISS) — szerokość i długość geograficzną."""
    url = "http://api.open-notify.org/iss-now.json"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        pos = data["iss_position"]
        lat = pos["latitude"]
        lon = pos["longitude"]
        ts = data["timestamp"]
        return (
            f"ISS jest teraz nad: {lat}°N, {lon}°E "
            f"(timestamp: {ts})"
        )
    except Exception as e:
        return f"Błąd pobierania pozycji ISS: {str(e)}"


@mcp.tool()
def get_astronauts_in_space() -> str:
    """Pobiera listę astronautów aktualnie przebywających w kosmosie — imiona i nazwy statków."""
    url = "http://api.open-notify.org/astros.json"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        count = data["number"]
        people = data["people"]
        lines = [f"  • {p['name']} ({p['craft']})" for p in people]
        return (
            f"Astronautów w kosmosie: {count}\n" + "\n".join(lines)
        )
    except Exception as e:
        return f"Błąd pobierania listy astronautów: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
