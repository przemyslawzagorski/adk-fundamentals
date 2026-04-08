from mcp.server.fastmcp import FastMCP
import httpx

# Inicjalizacja serwera pod nazwą "PublicAPIs"
mcp = FastMCP("PublicAPIs")

@mcp.tool()
def get_exchange_rate(currency_code: str) -> str:
    """Pobiera aktualny średni kurs podanej waluty (np. USD, EUR, CHF) w PLN z NBP."""
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency_code.upper()}/?format=json"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
        rate = data['rates'][0]['mid']
        date = data['rates'][0]['effectiveDate']
        return f"Kurs {currency_code.upper()} z dnia {date} wynosi: {rate} PLN"
    except Exception as e:
        return f"Błąd podczas pobierania kursu dla {currency_code}: {str(e)}"

@mcp.tool()
def get_pokemon_stats(pokemon_name: str) -> str:
    """Pobiera szczegółowe statystyki (wzrost, waga, typy) dla danego Pokemona (np. pikachu)."""
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
        weight = data['weight'] / 10  # waga w kg
        height = data['height'] / 10  # wzrost w metrach
        types = [t['type']['name'] for t in data['types']]
        return f"Pokemon {pokemon_name.capitalize()}: Wzrost {height}m, Waga {weight}kg, Typy: {', '.join(types)}"
    except Exception as e:
        return f"Nie znaleziono pokemona o nazwie {pokemon_name} lub wystąpił błąd: {str(e)}"

@mcp.tool()
def get_random_joke() -> str:
    """Pobiera losowy żart w języku angielskim."""
    url = "https://official-joke-api.appspot.com/random_joke"
    try:
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()
        return f"{data['setup']} ... {data['punchline']}"
    except Exception as e:
        return f"Błąd podczas pobierania żartu: {str(e)}"

if __name__ == "__main__":
    # Uruchomienie serwera w trybie STDIO (wymagane przez klienty MCP)
    mcp.run(transport='stdio')