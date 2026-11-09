"""
MCP Server: Weather (wttr.in)
=============================
Serwer MCP udostępniający narzędzia pogodowe.
Korzysta z darmowego API wttr.in - BEZ klucza API!

Uruchomienie standalone (do testów):
    python weather_server.py
"""

from mcp.server.fastmcp import FastMCP
import httpx

# Inicjalizacja serwera MCP pod nazwą "Weather"
mcp = FastMCP("Weather")


@mcp.tool()
def get_current_weather(city: str) -> str:
    """Pobiera aktualną pogodę dla podanego miasta (np. Warsaw, Krakow, London)."""
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = httpx.get(url, timeout=10, headers={"User-Agent": "adk-weather-agent"})
        response.raise_for_status()
        data = response.json()
        current = data["current_condition"][0]
        temp = current["temp_C"]
        feels_like = current["FeelsLikeC"]
        humidity = current["humidity"]
        desc = current["weatherDesc"][0]["value"]
        wind_speed = current["windspeedKmph"]
        wind_dir = current["winddir16Point"]
        return (
            f"Pogoda w {city}: {desc}, "
            f"Temperatura: {temp}°C (odczuwalna: {feels_like}°C), "
            f"Wilgotność: {humidity}%, "
            f"Wiatr: {wind_speed} km/h ({wind_dir})"
        )
    except Exception as e:
        return f"Błąd pobierania pogody dla {city}: {str(e)}"


@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> str:
    """Pobiera prognozę pogody na kilka dni (1-3) dla podanego miasta."""
    if days < 1 or days > 3:
        days = 3
    url = f"https://wttr.in/{city}?format=j1"
    try:
        response = httpx.get(url, timeout=10, headers={"User-Agent": "adk-weather-agent"})
        response.raise_for_status()
        data = response.json()
        forecasts = []
        for day_data in data["weather"][:days]:
            date = day_data["date"]
            max_temp = day_data["maxtempC"]
            min_temp = day_data["mintempC"]
            desc = day_data["hourly"][4]["weatherDesc"][0]["value"]  # ~noon
            forecasts.append(
                f"  {date}: {desc}, {min_temp}°C - {max_temp}°C"
            )
        result = f"Prognoza pogody dla {city} ({days} dni):\n" + "\n".join(forecasts)
        return result
    except Exception as e:
        return f"Błąd pobierania prognozy dla {city}: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
