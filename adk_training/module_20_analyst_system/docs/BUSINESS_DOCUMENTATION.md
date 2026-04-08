# Analyst System — Dokumentacja biznesowa

## 1. Opis rozwiązania

**Analyst System** to inteligentny system agentowy zbudowany na platformie Google ADK (Agent Development Kit), zaprojektowany do automatyzacji zadań analitycznych w projektach IT. System działa jako cyfrowy analityk, który rozumie kontekst projektu i wykorzystuje wyspecjalizowane umiejętności (skills) do generowania dokumentacji, analizy wymagań i tworzenia epiców.

### 1.1. Problem, który rozwiązuje

| Problem | Rozwiązanie |
|---------|-------------|
| Manualne tworzenie dokumentacji technicznej jest czasochłonne | Automatyczna generacja HLD, LLD, planów testów |
| Analiza wymagań wymaga wiedzy domenowej | System ładuje kontekst projektu z kontraktu (contract) |
| Brak spójności między dokumentami | Centralna baza umiejętności (skills) i szablonów |
| Wiedza o stylu pisania nie jest ustandaryzowana | Wbudowane skill-e z Diátaxis framework i style guide |
| Generowanie nowych umiejętności wymaga manualnej pracy | Automatyczny pipeline generacji skill-i z walidacją |

### 1.2. Kluczowe wartości

- **Kontekstowość** — system rozumie domenę projektu dzięki kontraktowi wiedzy (ProjectKnowledgeContract)
- **Rozszerzalność** — nowe umiejętności tworzone automatycznie przez Knowledge Loop
- **Jakość** — każdy wynik przechodzi przez quality review przed dostarczeniem
- **Wielokanałowość** — integracja z Jira, Confluence, GitLab przez Comarch MCP

---

## 2. Architektura dwupętlowa (Dual-Loop)

System opiera się na dwóch uzupełniających się pętlach:

### 2.1. Analyst Loop (pętla analityczna)

Odpowiada za realizację zadań analitycznych — generowanie dokumentów, analizę wymagań, tworzenie epiców.

**Przepływ:**

1. Użytkownik zadaje pytanie lub zleca zadanie
2. **Analyst Captain** (router) kieruje do odpowiedniego orkiestratora
3. Orkiestrator uruchamia pipeline agentów (zbieranie → analiza → generowanie → review)
4. Wynik trafia do użytkownika

**Orkiestratory:**

| Orkiestrator | Cel | Typowe użycie |
|-------------|-----|---------------|
| `analyze_requirement` | Analiza wymagań pod kątem kompletności i ryzyk | „Przeanalizuj wymaganie: system musi obsługiwać 10k SIM" |
| `create_epic` | Tworzenie epików Jira z podziałem na user stories | „Utwórz epik dla modułu fakturowania" |
| `generate_document` | Generowanie dokumentacji technicznej (HLD, LLD, etc.) | „Wygeneruj HLD dla modułu billing" |
| `generate_test_plan` | Tworzenie planów testów | „Przygotuj plan testów integracyjnych dla Census" |
| `review_document` | Recenzja istniejących dokumentów | „Zrecenzuj ten dokument pod kątem Diátaxis" |

### 2.2. Knowledge Loop (pętla wiedzy)

Odpowiada za wytwarzanie nowych umiejętności (skills) na podstawie wiedzy zgromadzonej w projekcie.

**Przepływ:**

1. Użytkownik zleca utworzenie nowego skill-a
2. `generate_skill` uruchamia 6-etapowy pipeline:
   - Zebranie źródeł wiedzy
   - Ekstrakcja wiedzy
   - Sprawdzenie duplikatów
   - Zaprojektowanie skill-a
   - Recenzja jakości
   - Prezentacja wyniku
3. Nowy skill jest dostępny dla wszystkich orkiestratorów

---

## 3. Kontrakt wiedzy projektowej

System konfiguruje się za pomocą **Project Knowledge Contract** — pliku JSON opisującego domenę projektu.

### 3.1. Co zawiera kontrakt

| Sekcja | Zawartość | Przykład |
|--------|----------|---------|
| `project_name` | Nazwa projektu | „IoT Connect" |
| `domain` | Konteksty domenowe, encje, słownik | Census, Catalog, Iungo, Motus |
| `documentation` | Framework, język, uwagi stylistyczne | Diátaxis, Polski |
| `jira` | URL i klucz projektu Jira | `https://jira.comarch/` |
| `wiki` | URL przestrzeni Confluence | `https://wiki.comarch/` |
| `tech_stack` | Używane technologie | Scala 2.13, Cats Effect, Kafka |

### 3.2. Jak działa kontekstowość

Każdy agent w systemie otrzymuje automatycznie wstrzyknięty kontekst z kontraktu — wie o projekcie, domenie, terminologii i oczekiwanym stylu dokumentacji. Dzięki temu generowane dokumenty są spójne z istniejącą bazą wiedzy projektu.

---

## 4. Wbudowane umiejętności (skills)

System startuje z 4 wbudowanymi umiejętnościami:

| Skill | Przeznaczenie |
|-------|---------------|
| `diataxis-writing` | Pisanie dokumentacji według frameworku Diátaxis (tutorial, how-to, reference, explanation) |
| `style-guide` | Konwencje stylistyczne inspirowane Microsoft Writing Style Guide |
| `document-templates` | Szablony HLD, LLD, epików i planów testów |
| `requirement-analysis` | Analiza wymagań: jasność, kompletność, wykonalność, ryzyka |

### 4.1. Dynamiczne ładowanie skill-i

Orkiestratory automatycznie dobierają odpowiednie skill-e do zadania. Na przykład `generate_document` w kontekście HLD załaduje `diataxis-writing`, `style-guide` i `document-templates`.

---

## 5. Integracje zewnętrzne

System integruje się z narzędziami zespołu przez **Comarch MCP** (Model Context Protocol):

| System | Możliwości |
|--------|-----------|
| **Jira** | Odczyt ticketów, szukanie epiców, analiza backlogu |
| **Confluence** | Odczyt stron wiki, wyszukiwanie dokumentacji |
| **GitLab** | Przeglądanie kodu, analiza merge requestów |

Integracja jest opcjonalna — system działa również bez MCP, korzystając z lokalnych plików i skill-i.

---

## 6. Typowe scenariusze użycia

### 6.1. Generowanie HLD dla nowego modułu

> „Wygeneruj High-Level Design dla modułu zarządzania alertami sieciowymi"

System: zbiera kontekst projektu → ładuje szablon HLD → generuje dokument z uwzględnieniem domeny → przeprowadza review jakości → zapisuje plik.

### 6.2. Analiza wymagania przed implementacją

> „Przeanalizuj wymaganie: System musi obsługiwać masową aktywację 10 000 kart SIM w partii"

System: 4 analitycy równolegle badają jasność, zakres, zależności i luki dokumentacyjne → synteza generuje raport.

### 6.3. Tworzenie epiku z user stories

> „Utwórz epik dla implementacji eksportu CDR do formatu CSV"

System: zbiera kontekst → pisze dokument epiku → reviewer sprawdza jakość → template writer formatuje do szablonu.

### 6.4. Rozbudowa bazy wiedzy

> „Utwórz nowy skill dotyczący konwencji nazewnictwa w API GraphQL"

System: zbiera źródła z kodu i wiki → ekstrahuje wiedzę → sprawdza duplikaty → projektuje skill → review → prezentacja.

---

## 7. Korzyści biznesowe

1. **Redukcja czasu tworzenia dokumentacji** — automatyczna generacja z kontekstem projektu
2. **Spójność** — jeden standard dzięki centralnej bazie skill-i i szablonów
3. **Samorozwój** — system buduje nowe umiejętności na podstawie wiedzy zespołu
4. **Skalowalność** — dodanie nowego modułu/domeny to dodanie wpisu w kontrakcie
5. **Niski próg wejścia** — naturalny język jako interfejs, brak potrzeby nauki nowych narzędzi
