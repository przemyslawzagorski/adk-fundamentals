"""
MCP Server: Public APIs (NBP Exchange Rates, Pokemon Stats, Random Jokes)
=========================================================================
Serwer MCP udostępniający narzędzia do trzech publicznych API.
Uruchamiany w trybie STDIO - agent ADK łączy się z nim automatycznie.

Uruchomienie standalone (do testów):
    python api_server.py
"""

from mcp.server.fastmcp import FastMCP
import httpx

# Inicjalizacja serwera MCP pod nazwą "PublicAPIs"
mcp = FastMCP("PublicAPIs")


@mcp.tool()
def get_exchange_rate(currency_code: str) -> str:
    """Pobiera aktualny średni kurs waluty (np. USD, EUR, CHF) w PLN z NBP."""
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency_code.upper()}/?format=json"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data["rates"][0]["mid"]
        date = data["rates"][0]["effectiveDate"]
        return f"Kurs {currency_code.upper()} z dnia {date} wynosi: {rate} PLN"
    except httpx.HTTPStatusError as e:
        return f"Błąd HTTP dla waluty {currency_code}: {e.response.status_code}"
    except Exception as e:
        return f"Błąd podczas pobierania kursu dla {currency_code}: {str(e)}"


@mcp.tool()
def get_pokemon_stats(pokemon_name: str) -> str:
    """Pobiera statystyki Pokemona (wzrost, waga, typy) po nazwie (np. pikachu, charizard)."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        weight = data["weight"] / 10
        height = data["height"] / 10
        types = [t["type"]["name"] for t in data["types"]]
        return (
            f"Pokemon {pokemon_name.capitalize()}: "
            f"Wzrost {height}m, Waga {weight}kg, "
            f"Typy: {', '.join(types)}"
        )
    except httpx.HTTPStatusError:
        return f"Nie znaleziono pokemona o nazwie: {pokemon_name}"
    except Exception as e:
        return f"Błąd: {str(e)}"


@mcp.tool()
def get_random_joke() -> str:
    """Pobiera losowy żart w języku angielskim (setup + punchline)."""
    url = "https://official-joke-api.appspot.com/random_joke"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return f"{data['setup']} ... {data['punchline']}"
    except Exception as e:
        return f"Błąd podczas pobierania żartu: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
