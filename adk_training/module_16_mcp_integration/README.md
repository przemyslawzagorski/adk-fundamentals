# 🔌 Moduł 16: MCP Integration — Agent z wieloma serwerami MCP

## 📚 Czego się nauczysz?

- ✅ Czym jest **MCP (Model Context Protocol)** i dlaczego to standard
- ✅ Jak napisać **własny serwer MCP** z FastMCP
- ✅ Jak podłączyć agenta ADK do serwera MCP przez **StdioServerParameters**
- ✅ Jak podłączyć **wiele serwerów MCP** do jednego agenta
- ✅ Różnica między MCP (STDIO) a MCP (SSE/HTTP)

**Czas: ~30 minut** ⚡

---

## 🧠 Teoria: Co to MCP?

### Problem
Każdy framework AI ma swój sposób definiowania narzędzi. Jeśli napiszesz narzędzie
dla jednego frameworka (np. LangChain), nie zadziała w innym (np. ADK).

### Rozwiązanie: MCP
**Model Context Protocol** to otwarty standard komunikacji między agentami AI
a zewnętrznymi narzędziami/danymi. Działa na zasadzie klient-serwer:

```
┌─────────────┐     MCP Protocol     ┌─────────────────┐
│  ADK Agent  │ ◄──────────────────► │  MCP Server      │
│  (klient)   │    stdio / SSE       │  (narzędzia)     │
└─────────────┘                      └─────────────────┘
```

- **MCP Server** — udostępnia narzędzia (tools), dane (resources), prompty
- **MCP Client** — agent łączący się z serwerem i korzystający z narzędzi
- **Transport** — STDIO (lokalne procesy) lub SSE/HTTP (zdalne serwery)

### ADK + MCP
ADK ma wbudowaną klasę **`MCPToolset`** która:
1. Łączy się z serwerem MCP
2. Odkrywa dostępne narzędzia (`tools/list`)
3. Tłumaczy schematy MCP → narzędzia ADK
4. Proxy'uje wywołania narzędzi (`tools/call`)

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

tools = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["my_mcp_server.py"],
    )
)
```

---

## 🏗️ Architektura modułu

```
                          ┌──────────────────────┐
                          │   ADK Agent (Gemini)  │
                          │   mcp_multi_agent     │
                          └──────┬───────┬────────┘
                                 │       │
                    MCP/STDIO    │       │    MCP/STDIO
                                 │       │
              ┌──────────────────┘       └──────────────────┐
              ▼                                             ▼
┌─────────────────────────┐               ┌─────────────────────────┐
│  MCP Server: PublicAPIs │               │  MCP Server: Weather    │
│                         │               │                         │
│  • get_exchange_rate()  │               │  • get_current_weather()│
│  • get_pokemon_stats()  │               │  • get_weather_forecast()│
│  • get_random_joke()    │               │                         │
│                         │               │  API: wttr.in (free)    │
│  API: NBP, PokeAPI,     │               └─────────────────────────┘
│       Joke API          │
└─────────────────────────┘
```

**Kluczowa linia kodu:**
```python
root_agent = LlmAgent(
    ...
    tools=[api_tools, weather_tools],  # 2 MCPToolset = 2 serwery MCP!
)
```

---

## 🚀 Szybki Start

### Krok 1: Sprawdź zależności
```bash
pip install mcp httpx
```

### Krok 2: Przetestuj serwery MCP ręcznie (opcjonalnie)
```bash
# Terminal 1 - test api_server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_servers/api_server.py

# Terminal 2 - test weather_server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_servers/weather_server.py
```

### Krok 3: Uruchom agenta
```bash
cd adk_training
adk web module_16_mcp_integration
```

### Krok 4: Przetestuj w przeglądarce
Przykładowe zapytania:
- *"Jaki jest kurs dolara?"*
- *"Jaka jest pogoda w Warszawie?"*
- *"Podaj statystyki Pikachu"*
- *"Opowiedz żart"*
- *"Jaka pogoda w Londynie i ile kosztuje funt?"* ← łączy 2 serwery MCP!

---

## 📖 Jak napisać własny serwer MCP?

### Szablon minimalny

```python
from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("MojSerwer")

@mcp.tool()
def moje_narzedzie(parametr: str) -> str:
    """Opis narzędzia - agent CZYTA ten docstring!"""
    # Tu logika - np. wywołanie API
    response = httpx.get(f"https://api.example.com/{parametr}", timeout=10)
    return response.text

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Zasady:
1. **Docstring jest OBOWIĄZKOWY** — agent go czyta, żeby wiedzieć co robi narzędzie
2. **Adnotacje typów** — parametry muszą mieć typy (`str`, `int`, `float`)
3. **Zwracaj `str`** — wynik zawsze jako tekst
4. **Timeout w HTTP** — zawsze ustawiaj `timeout` w requestach
5. **Obsługa błędów** — zwróć czytelny komunikat, nie stacktrace

### Jak podłączyć do agenta ADK:

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

my_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["sciezka/do/moj_server.py"],
    )
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="moj_agent",
    tools=[my_tools],
    ...
)
```

---

## 🆚 STDIO vs SSE — kiedy co?

| Aspekt | STDIO | SSE (Server-Sent Events) |
|--------|-------|--------------------------|
| Transport | stdin/stdout | HTTP |
| Uruchomienie | Sub-proces (automatycznie) | Osobny serwer (ręcznie) |
| Lokalizacja | Lokalnie | Lokalnie lub zdalnie |
| Setup | Zerowy | Wymaga uruchomienia serwera |
| Skalowanie | 1:1 (agent:serwer) | N:1 (wielu klientów) |
| **Użyj gdy** | Rozwój, prototypy | Produkcja, Cloud Run |

**Ten moduł używa STDIO** — prostsze, zero konfiguracji.

Moduł 09 (PostgreSQL) używa **SSE** — bo Toolbox to osobny serwer.

---

## 🏋️ Zadania

### Zadanie 1: Napisz własny serwer MCP ⭐

Napisz serwer MCP `mcp_servers/space_server.py` z narzędziami:

1. **`get_iss_position()`** — aktualna pozycja Międzynarodowej Stacji Kosmicznej
   - API: `http://api.open-notify.org/iss-now.json`
   - Zwróć: szerokość/długość geograficzną + timestamp

2. **`get_astronauts_in_space()`** — lista astronautów aktualnie na orbicie
   - API: `http://api.open-notify.org/astros.json`
   - Zwróć: liczbę + imiona astronautów i na jakim statku

**Wymagania:**
- Użyj `FastMCP` z nazwą `"Space"`
- Każde narzędzie z docstringiem po polsku
- Obsługa błędów (try/except)
- Timeout 10 sekund

**Podpowiedź:** Wzoruj się na `api_server.py` — struktura identyczna.

---

### Zadanie 2: Podłącz 3 serwery MCP do agenta ⭐⭐

Po napisaniu `space_server.py`:

1. Otwórz `agent.py` (lub stwórz nowy)
2. Dodaj trzeci `MCPToolset` dla space_server
3. Zaktualizuj prompt agenta — dodaj info o kosmosie
4. Przetestuj: *"Gdzie jest teraz ISS i jaka tam pogoda?"*

**Kluczowa zmiana:**
```python
tools=[api_tools, weather_tools, space_tools]  # 3 serwery!
```

---

### Zadanie 3: Kreatywne MCP ⭐⭐⭐

Wybierz **dowolne darmowe API** i napisz serwer MCP:

**Propozycje:**
| API | URL | Narzędzia |
|-----|-----|-----------|
| Cat Facts | catfact.ninja/fact | Losowy fakt o kotach |
| Bored API | bored-api.appbrewery.com/random | Losowa aktywność |
| Numbers | numbersapi.com | Ciekawostki o liczbach |
| Dog CEO | dog.ceo/api/breeds/list/all | Lista ras psów + zdjęcia |
| Open Library | openlibrary.org/search.json | Wyszukiwanie książek |
| Country Info | restcountries.com/v3.1/name/{name} | Info o krajach |

**Wymagania:**
- Min. 2 narzędzia w serwerze
- Podłącz do agenta obok istniejących serwerów
- Przetestuj kombinację narzędzi z różnych serwerów

---

### Zadanie 4 (BONUS): MCP Server z parametrami środowiskowymi ⭐⭐⭐

Napisz serwer MCP, który wymaga klucza API (np. OpenWeatherMap, NewsAPI).

Podłącz go do agenta z przekazaniem zmiennych środowiskowych:

```python
MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["mcp_servers/news_server.py"],
        env={"NEWS_API_KEY": os.getenv("NEWS_API_KEY")},
    )
)
```

---

## 🔍 Częste problemy

### Agent nie widzi narzędzi MCP
- Sprawdź czy serwer MCP uruchamia się poprawnie: `python mcp_servers/api_server.py`
- Upewnij się, że `mcp` jest zainstalowane: `pip install mcp`
- Sprawdź ścieżkę w `StdioServerParameters`

### Timeout / brak odpowiedzi
- Dodaj `timeout=10` do wywołań `httpx.get()`
- Sprawdź dostępność API (curl/browser)

### "ModuleNotFoundError: No module named 'mcp'"
```bash
pip install mcp httpx
```

### Agent używa tylko jednego serwera MCP
- Upewnij się, że oba serwery są na liście `tools=[..., ...]`
- Sprawdź prompt — agent musi wiedzieć o dostępnych możliwościach

---

## 📚 Materiały dodatkowe

- [ADK Docs: MCP Tools](https://google.github.io/adk-docs/tools/mcp-tools/)
- [ADK meets MCP: Bridging Worlds (Medium)](https://medium.com/google-cloud/adk-meets-mcp-bridging-worlds-of-ai-agents-1ed96ef5399c)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)
