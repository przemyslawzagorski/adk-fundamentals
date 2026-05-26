# 🏨 Simple Database Agent - SQLite Example

## 📚 Czego się nauczysz?

Ten przykład pokazuje **najprostszy sposób** użycia ADK z bazą danych:
- ✅ **SQLite** - baza danych w pliku, zero konfiguracji
- ✅ **Funkcje Python jako narzędzia** - bez MCP, bez Docker
- ✅ **Działa offline** - nie wymaga internetu
- ✅ **Gotowe dane testowe** - 15 hoteli w Polsce

**Czas setup: 30 sekund!** ⚡

---

## 🎯 Architektura

```
User Question
    ↓
Agent (Gemini)
    ↓
Python Functions (search_hotels_by_name, search_hotels_by_location, etc.)
    ↓
SQLite Database (hotels.db)
    ↓
Results → Agent → User
```

**Brak:** MCP, Docker, Cloud Run, AlloyDB, IAM permissions 🎉

---

## 🚀 Szybki Start

### 1. Inicjalizuj bazę danych

```bash
cd module_09_database_simple
python init_database.py
```

**Output:**
```
✅ Database created successfully: hotels.db
✅ Inserted 15 hotels
📊 Sample data:
  - Hotel Bristol (Warsaw) - Rating: 4.8
  - Hotel Marriott (Warsaw) - Rating: 4.5
  ...
```

### 2. (Opcjonalnie) Uruchom Query Monitor 🔍

**Query Monitor** to prosty web dashboard do monitorowania zapytań SQL w czasie rzeczywistym.

#### Jak to działa?

```
Agent wykonuje zapytanie
    ↓
database_tools.py → log_query()
    ↓
query_logger.py → zapisuje do query_log.db (SQLite)
    ↓
query_monitor.py (Flask) → czyta z query_log.db
    ↓
Przeglądarka → wyświetla zapytania w czasie rzeczywistym
```

**Kluczowe cechy:**
- ✅ **Thread-safe i process-safe** - używa SQLite z automatycznym lockingiem
- ✅ **Niezawodne** - ACID transactions, brak race conditions
- ✅ **Szybkie** - indeksy SQL, efektywne zapytania
- ✅ **Proste** - tylko SQLite, bez zewnętrznych zależności (oprócz Flask)

#### Uruchomienie:

```bash
# Terminal 1: Uruchom Query Monitor
pip install flask  # jeśli nie masz
python query_monitor.py

# Terminal 2: Uruchom agenta lub testy
python test_query_logging.py  # test queries
# LUB
adk web .  # uruchom agenta
```

Otwórz w przeglądarce: **http://localhost:5001**

#### Co zobaczysz:

**Dashboard pokazuje:**
- 📊 **Statystyki** - total queries, unique functions, total results
- 🔍 **Lista zapytań** - wszystkie SQL queries (najnowsze na górze)
- ⏱️ **Timestamp** - kiedy każde zapytanie zostało wykonane
- 📝 **Parametry** - jakie wartości były użyte (np. `'%Warsaw%'`)
- ✅ **Liczba wyników** - ile rekordów zwróciło zapytanie
- 🔄 **Auto-refresh** - odświeża się co 5 sekund

**API Endpoints:**
- `GET /api/queries?limit=100` - JSON z zapytaniami
- `GET /api/stats` - JSON ze statystykami
- `POST /api/clear` - wyczyść historię zapytań

### 2. Testuj funkcje bazodanowe (opcjonalnie)

```bash
python database_tools.py
```

### 3. Skonfiguruj środowisko

```bash
cp .env.template .env
# Edytuj .env i ustaw swój GOOGLE_CLOUD_PROJECT
```

### 4. Uruchom agenta

```bash
python agent.py
```

---

## 💡 Przykładowe zapytania

```python
"Find me luxury hotels in Warsaw"
→ Agent użyje: search_hotels_by_location("Warsaw")

"Show me all Hilton hotels"
→ Agent użyje: search_hotels_by_name("Hilton")

"I need a hotel between 300 and 400 PLN per night"
→ Agent użyje: search_hotels_by_price_range(300, 400)

"Tell me about hotel ID 5"
→ Agent użyje: get_hotel_by_id(5)
```

---

## 📂 Struktura plików

```
adk04-simple-database/
├── agent.py              # Agent ADK z narzędziami
├── database_tools.py     # Funkcje do obsługi SQLite
├── init_database.py      # Skrypt inicjalizujący bazę
├── hotels.db             # Baza danych SQLite (generowana)
├── .env.template         # Szablon konfiguracji
└── README.md             # Ta dokumentacja
```

---

## 🔍 Jak to działa?

### 1. Funkcje jako narzędzia

```python
def search_hotels_by_name(name: str) -> List[Dict[str, Any]]:
    """Search for hotels based on name."""
    conn = sqlite3.connect(DB_PATH)
    # ... SQL query ...
    return results
```

### 2. Agent używa funkcji

```python
root_agent = Agent(
    model="gemini-2.5-flash-exp",
    tools=[
        search_hotels_by_name,
        search_hotels_by_location,
        search_hotels_by_price_range,
        get_hotel_by_id
    ]
)
```

### 3. Agent automatycznie wybiera narzędzie

Gdy użytkownik pyta: *"Find hotels in Krakow"*
- Agent rozumie intencję
- Wywołuje `search_hotels_by_location("Krakow")`
- Formatuje wyniki w naturalny sposób

---

## 🆚 Porównanie z MCP

| Aspekt | Ten przykład (SQLite) | MCP (adk04-mcp-postgres) |
|--------|----------------------|--------------------------|
| Setup time | 30 sekund | 5 minut |
| Wymaga internetu | ❌ NIE | ✅ TAK |
| Wymaga zewnętrznych serwisów | ❌ NIE | ✅ TAK (Neon.tech) |
| Pokazuje MCP | ❌ NIE | ✅ TAK |
| Dla nauki ADK | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Dla produkcji | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🎓 Kluczowe koncepcje

1. **Funkcje Python = Narzędzia ADK**
   - Każda funkcja z docstringiem może być narzędziem
   - Agent automatycznie rozumie parametry i zwracane wartości

2. **SQLite = Idealna baza do nauki**
   - Baza danych w pliku
   - Pełny SQL
   - Zero konfiguracji

3. **Prostota > Komplikacja**
   - Nie potrzebujesz MCP do nauki ADK
   - Zacznij od prostego, potem dodawaj złożoność

---

## 🔬 Jak działa Query Monitoring (szczegóły techniczne)

### Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent (adk web)                          │
│  User: "Find hotels in Warsaw"                              │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              database_tools.py                              │
│  search_hotels_by_location("Warsaw")                        │
│    ├─ Execute SQL: SELECT ... WHERE location LIKE '%Warsaw%'│
│    ├─ Get results: 3 hotels                                 │
│    └─ Call: log_query(...)                                  │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              query_logger.py                                │
│  log_query("search_hotels_by_location", query, params, 3)  │
│    └─ INSERT INTO query_log.db                              │
│       (timestamp, function, query, params, result_count)    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              query_log.db (SQLite)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ id │ timestamp │ function │ query │ params │ results │   │
│  ├────┼───────────┼──────────┼───────┼────────┼─────────┤   │
│  │ 1  │ 14:35:14  │ search.. │ SEL.. │ ["%W.."]│   3    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         ↑
┌─────────────────────────────────────────────────────────────┐
│         query_monitor.py (Flask web server)                 │
│  GET / → get_query_history() → SELECT * FROM query_log      │
│  GET /api/queries → JSON response                           │
│  GET /api/stats → COUNT(*), SUM(result_count)               │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Browser (http://localhost:5001)                │
│  ┌────────────────────────────────────────────────────┐     │
│  │ 🔍 SQL Query Monitor                               │     │
│  │ ┌──────────┬──────────────┬─────────────┐          │     │
│  │ │ Total: 12│ Functions: 4 │ Results: 45 │          │     │
│  │ └──────────┴──────────────┴─────────────┘          │     │
│  │ search_hotels_by_location  14:35:14                │     │
│  │ SELECT ... WHERE location LIKE ?                   │     │
│  │ Params: ["%Warsaw%"]  Results: 3                   │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Pliki

| Plik | Rola | Opis |
|------|------|------|
| `database_tools.py` | **Narzędzia agenta** | Funkcje do wyszukiwania hoteli + wywołanie `log_query()` |
| `query_logger.py` | **Logger** | Zapisuje zapytania do `query_log.db` (SQLite) |
| `query_log.db` | **Baza logów** | SQLite database z historią zapytań |
| `query_monitor.py` | **Web dashboard** | Flask app do wyświetlania zapytań |
| `test_query_logging.py` | **Testy** | Skrypt testowy do generowania przykładowych zapytań |

### Dlaczego SQLite zamiast JSON?

**Poprzednie rozwiązanie (JSON file):**
```python
# ❌ Problemy:
# - File locking (fcntl) - skomplikowane, tylko Linux
# - Race conditions między procesami
# - Trzeba ręcznie parsować JSON
# - Brak transakcji
```

**Obecne rozwiązanie (SQLite):**
```python
# ✅ Zalety:
# - Thread-safe i process-safe (wbudowane w SQLite)
# - Automatyczne locking (ACID transactions)
# - Szybkie zapytania (indeksy, SQL)
# - Statystyki w SQL (COUNT, SUM, GROUP BY)
# - Działa na Windows, Linux, Mac
```

### Przykład użycia API

```bash
# Pobierz ostatnie 10 zapytań
curl http://localhost:5001/api/queries?limit=10

# Pobierz statystyki
curl http://localhost:5001/api/stats

# Wyczyść historię
curl -X POST http://localhost:5001/api/clear
```

**Response `/api/queries`:**
```json
[
  {
    "timestamp": "2026-02-21T14:35:14.465612",
    "function": "search_hotels_by_location",
    "query": "SELECT id, name, location... WHERE location LIKE ?",
    "params": ["%Warsaw%"],
    "result_count": 3
  }
]
```

**Response `/api/stats`:**
```json
{
  "total_queries": 12,
  "unique_functions": 4,
  "total_results": 45
}
```

---

## 🔧 Troubleshooting

**Problem:** `hotels.db` nie istnieje
```bash
python init_database.py
```

**Problem:** Błąd importu `google.adk`
```bash
pip install google-adk
```

**Problem:** Agent nie odpowiada
- Sprawdź czy `.env` jest poprawnie skonfigurowany
- Sprawdź czy masz dostęp do Vertex AI

---

## 📖 Następne kroki

1. ✅ **Zrozum ten przykład** - najprostszy sposób ADK + Database
2. ➡️ **Zobacz adk04-mcp-postgres** - jak używać MCP z prawdziwym PostgreSQL
3. 🚀 **Stwórz własny agent** - dodaj więcej funkcji, inne dane

---

## 🤝 Porównaj z innymi przykładami

- **adk04a-db-toolbox-setup** - Skomplikowany setup z AlloyDB
- **adk04b-db-toolbox-local** - Wymaga uruchomienia toolbox
- **adk04c-db-toolbox-remote** - Wymaga Cloud Run
- **👉 adk04-simple-database** - TEN PRZYKŁAD - najprostszy!
- **adk04-mcp-postgres** - MCP z darmowym PostgreSQL

---

**Pytania? Problemy? Sprawdź kod - jest prosty i dobrze skomentowany!** 🎉

