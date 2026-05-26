# 🏨 MCP Database Agent - PostgreSQL Example

## 📚 Czego się nauczysz?

Ten przykład pokazuje **profesjonalny sposób** użycia ADK z bazą danych:
- ✅ **PostgreSQL** - prawdziwa baza danych (darmowa w chmurze!)
- ✅ **MCP (Model Context Protocol)** - standardowy protokół dla narzędzi AI
- ✅ **Toolbox** - serwer MCP od Google
- ✅ **Production-ready** - architektura gotowa na produkcję

**Czas setup: 5 minut!** ⚡

---

## 🎯 Architektura

```
User Question
    ↓
Agent (Gemini)
    ↓
MCP Toolset (SSE connection)
    ↓
Toolbox Server (MCP)
    ↓
PostgreSQL Database (Neon.tech / Supabase / Railway)
    ↓
Results → Toolbox → Agent → User
```

**Nowe elementy:** MCP Protocol, Toolbox Server, Cloud PostgreSQL

---

## 🆚 Porównanie z adk04-simple-database

| Aspekt | Simple (SQLite) | Ten przykład (MCP + PostgreSQL) |
|--------|-----------------|----------------------------------|
| Baza danych | SQLite (plik) | PostgreSQL (cloud) |
| Protokół | Bezpośrednie wywołania | MCP (standardowy) |
| Serwer | Nie wymagany | Toolbox (MCP server) |
| Setup | 30 sekund | 5 minut |
| Dla nauki | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Dla produkcji | ⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🚀 Szybki Start

### Krok 1: Stwórz darmową bazę PostgreSQL

**Opcja A: Neon.tech (REKOMENDOWANE)**

1. Idź na https://neon.tech
2. Zarejestruj się (darmowe konto)
3. Kliknij "Create Project"
4. Skopiuj **Connection String**:
   ```
   postgresql://neondb_owner:xxxxx@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

**Opcja B: Supabase**

1. Idź na https://supabase.com
2. Zarejestruj się
3. Stwórz nowy projekt
4. Idź do Settings → Database
5. Skopiuj **Connection String** (Transaction mode)

**Opcja C: Railway.app**

1. Idź na https://railway.app
2. Zarejestruj się ($5 darmowych kredytów)
3. Dodaj PostgreSQL
4. Skopiuj **Connection String**

---

### Krok 2: Zainicjalizuj bazę danych

1. Otwórz SQL editor w swoim providerze (Neon/Supabase/Railway)
2. Skopiuj zawartość `setup_db.sql`
3. Wykonaj SQL
4. Sprawdź czy masz 15 hoteli w tabeli `hotels`

**Alternatywnie (z linii komend):**
```bash
psql "your-connection-string" -f setup_db.sql
```

---

### Krok 3: Skonfiguruj Toolbox

Edytuj `toolbox.yaml` i wklej swój connection string:

```yaml
sources:
  hotels-database:
    kind: "postgres"
    connection_string: "postgresql://user:pass@host:5432/db"  # ← TUTAJ!
```

---

### Krok 4: Pobierz i uruchom Toolbox

**Windows (WSL2):**
```bash
# W WSL2
curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v0.20.0/linux/amd64/toolbox
chmod +x toolbox
./toolbox --tools-file toolbox.yaml
```

**Linux:**
```bash
curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v0.20.0/linux/amd64/toolbox
chmod +x toolbox
./toolbox --tools-file toolbox.yaml
```

**macOS:**
```bash
curl -L -o toolbox https://storage.googleapis.com/genai-toolbox/v0.20.0/darwin/amd64/toolbox
chmod +x toolbox
./toolbox --tools-file toolbox.yaml
```

**Output:**
```
✅ Toolbox server started on http://127.0.0.1:5000
✅ MCP endpoint: http://127.0.0.1:5000/mcp/sse
✅ Connected to PostgreSQL
✅ Loaded 5 tools from toolset: hotel_search_toolset
```

---

### Krok 5: Skonfiguruj środowisko

```bash
cp .env.template .env
# Edytuj .env i ustaw:
# - GOOGLE_CLOUD_PROJECT
# - TOOLBOX_URL (domyślnie http://127.0.0.1:5000)
```

---

### Krok 6: Uruchom agenta

```bash
python agent.py
```

---

## 💡 Przykładowe zapytania

```python
"Find me luxury hotels in Warsaw"
→ MCP wywołuje: search-hotels-by-location("Warsaw")

"Show me all Hilton hotels"
→ MCP wywołuje: search-hotels-by-name("Hilton")

"What are the top 5 rated hotels?"
→ MCP wywołuje: get-top-rated-hotels(5)

"Find hotels between 300 and 400 PLN"
→ MCP wywołuje: search-hotels-by-price-range(300, 400)
```

---

## 📂 Struktura plików

```
adk04-mcp-postgres/
├── agent.py              # Agent ADK z MCP toolset
├── toolbox.yaml          # Konfiguracja MCP toolbox
├── setup_db.sql          # SQL do inicjalizacji bazy
├── .env.template         # Szablon konfiguracji
└── README.md             # Ta dokumentacja
```

---

## 🔍 Jak to działa?

### 1. Toolbox jako MCP Server

```yaml
# toolbox.yaml
tools:
  search-hotels-by-name:
    kind: postgres-sql
    statement: SELECT * FROM hotels WHERE name ILIKE '%' || $1 || '%'
```

Toolbox:
- Czyta `toolbox.yaml`
- Łączy się z PostgreSQL
- Udostępnia narzędzia przez MCP protocol (SSE)

### 2. Agent łączy się przez MCP

```python
connection_params = SseConnectionParams(
    url=f"{TOOLBOX_URL}/mcp/sse"
)
mcp_toolset = MCPToolset(connection_params=connection_params)
```

### 3. Komunikacja przez MCP

```
Agent → MCP Request → Toolbox → SQL Query → PostgreSQL
PostgreSQL → Results → Toolbox → MCP Response → Agent
```

---

## 🎓 Kluczowe koncepcje

### 1. **MCP (Model Context Protocol)**
- Standardowy protokół dla narzędzi AI
- Niezależny od providera (działa z Claude, Gemini, etc.)
- Server-Sent Events (SSE) dla real-time communication

### 2. **Toolbox**
- Serwer MCP od Google
- Przekształca SQL w narzędzia
- Obsługuje PostgreSQL, AlloyDB, BigQuery

### 3. **Deklaratywne narzędzia**
- Definiujesz w YAML, nie w kodzie
- Łatwe w utrzymaniu
- Bezpieczne (parametryzowane zapytania)

---

## 🔧 Troubleshooting

**Problem:** Toolbox nie może połączyć się z bazą
```
❌ Error: connection refused
```
**Rozwiązanie:**
- Sprawdź connection string w `toolbox.yaml`
- Upewnij się że baza jest dostępna (Neon/Supabase)
- Sprawdź czy `sslmode=require` jest w connection string

---

**Problem:** Agent nie może połączyć się z Toolbox
```
❌ Error: MCP connection failed
```
**Rozwiązanie:**
- Sprawdź czy Toolbox działa: `curl http://127.0.0.1:5000/health`
- Sprawdź `TOOLBOX_URL` w `.env`

---

**Problem:** Toolbox nie działa na Windows
**Rozwiązanie:**
- Użyj WSL2 (Windows Subsystem for Linux)
- LUB wdróż Toolbox na Cloud Run (zobacz adk04c)

---

## 📖 Następne kroki

1. ✅ **Zrozum MCP** - zobacz jak działa protokół
2. ✅ **Porównaj z SQLite** - zobacz różnice w architekturze
3. 🚀 **Wdróż na Cloud Run** - zobacz adk04c-db-toolbox-remote
4. 🎯 **Dodaj własne narzędzia** - edytuj `toolbox.yaml`

---

## 🌐 Darmowe PostgreSQL Providers

| Provider | Free Tier | Limit | SSL Required |
|----------|-----------|-------|--------------|
| **Neon.tech** | ✅ | 0.5 GB | ✅ |
| **Supabase** | ✅ | 500 MB | ✅ |
| **Railway** | ✅ | $5 credits | ✅ |
| **ElephantSQL** | ❌ (deprecated) | - | - |

---

