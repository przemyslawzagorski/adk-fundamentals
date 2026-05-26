# 🧠 Moduł 14: Agent Skills — Skarbnik Wiedzy Pirackiej

> *"Mądry pirat nie nosi wszystkich map w kieszeni — wie gdzie je znaleźć, gdy potrzebuje."*

## 🎯 Cele Edukacyjne

Po ukończeniu tego modułu będziesz:
- Rozumieć koncepcję **progressive disclosure** (L1 → L2 → L3) i dlaczego oszczędza tokeny
- Tworzyć **inline skills** — wiedzę zdefiniowaną bezpośrednio w Pythonie
- Budować **file-based skills** — SKILL.md + referencje w katalogu `references/`
- Ładować **external skills** — gotowe skille z repozytoriów społeczności
- Tworzyć **meta skills** — skille które uczą agenta generować nowe skille
- Łączyć wszystko w `SkillToolset` z trzema auto-generowanymi narzędziami

---

## 💡 Koncepcja: Progressive Disclosure

Tradycyjne podejście — pakowanie całej wiedzy w system prompt:
```
┌─────────────────────────────────────────────┐
│           SYSTEM PROMPT (~10 000 tok)       │
│                                             │
│  Kodeks Pirata (300 tok)                    │
│  Konserwacja Statku (500 tok)               │
│  Checklista Napraw (2000 tok)               │
│  Szkolenie Załogi (400 tok)                 │
│  Procedury Treningowe (3000 tok)            │
│  Kreator Skilli (500 tok)                   │
│  Specyfikacja (1500 tok)                    │
│  Przykład (800 tok)                         │
│                                             │
│  → Wszystko ładowane ZAWSZE,                │
│    nawet gdy pytanie dotyczy                 │
│    tylko jednej rzeczy!                     │
└─────────────────────────────────────────────┘
```

Podejście z Agent Skills — ładowanie na żądanie:
```
┌─────────────────────────────────────────────┐
│  L1 — METADATA (zawsze, ~400 tok)           │
│                                             │
│  pirate-code: Kodeks Pirata...              │
│  ship-maintenance: Konserwacja statku...    │
│  crew-training: Szkolenie załogi...         │
│  skill-creator: Kreator skilli...           │
└─────────────────────────────────────────────┘
         │  Agent decyduje →  "To pytanie o naprawy"
         ▼
┌─────────────────────────────────────────────┐
│  L2 — INSTRUCTIONS (na żądanie, ~500 tok)   │
│                                             │
│  load_skill("ship-maintenance")             │
│  → Procedury konserwacji krok po kroku      │
└─────────────────────────────────────────────┘
         │  Instrukcje mówią →  "Załaduj checklistę"
         ▼
┌─────────────────────────────────────────────┐
│  L3 — RESOURCES (na żądanie, ~2000 tok)     │
│                                             │
│  load_skill_resource("ship-maintenance",    │
│    "references/maintenance-checklist.md")    │
│  → Szczegółowa checklista napraw            │
└─────────────────────────────────────────────┘

Wynik: ~2900 tok zamiast ~10 000 tok (70% oszczędności!)
3 pozostałe skille → 0 tok (nieładowane)
```

---

## 🔑 Kluczowe Wzorce

### Wzorzec 1: Inline Skill
Skill zdefiniowany bezpośrednio w Pythonie — najprostrzy wzorzec.

```python
from google.adk.skills import models

pirate_code_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="pirate-code",               # L1: kebab-case, max 64 znaki
        description="Kodeks Pirata...",    # L1: max 1024 znaki
    ),
    instructions="Zasady:\n1. Podział łupów...",  # L2: ładowane na żądanie
)
```
**Kiedy używać**: Proste, stabilne reguły (<500 tok) które rzadko się zmieniają.

### Wzorzec 2: File-Based Skill
Skill w katalogu z `SKILL.md` i opcjonalnymi `references/`.

```
skills/ship-maintenance/
├── SKILL.md                              # Frontmatter (L1) + Instructions (L2)
└── references/
    └── maintenance-checklist.md          # Resource (L3)
```

```python
from google.adk.skills import load_skill_from_dir

ship_maintenance_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "ship-maintenance"
)
```
**Kiedy używać**: Skill z dokumentacją referencyjną, reużywalny między agentami.

### Wzorzec 3: External Skill
Skill pobrany z repozytorium społeczności (np. `awesome-claude-skills`).

```python
# Technicznie identyczne — ta sama funkcja load_skill_from_dir
crew_training_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "crew-training"
)
```
**Kiedy używać**: Ktoś już napisał skill którego potrzebujesz. Pobierz, zweryfikuj, użyj.

### Wzorzec 4: Meta Skill
Skill który uczy agenta generować **nowe** pliki SKILL.md.

```python
skill_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="skill-creator",
        description="Kreator nowych umiejętności...",
    ),
    instructions="Gdy tworzysz nowy skill:\n1. Załaduj references/skill-spec.md...",
    resources=models.Resources(
        references={
            "skill-spec.md": "# Specyfikacja Agent Skills...",
            "example-skill.md": "# Przykład: Skill do przeglądu kodu...",
        }
    ),
)
```
**Kiedy używać**: Agent sam rozbudowuje swoje umiejętności — "self-extending".

### Łączenie w SkillToolset

```python
from google.adk.tools.skill_toolset import SkillToolset

skill_toolset = SkillToolset(skills=[
    pirate_code_skill,       # Inline
    ship_maintenance_skill,  # File-based
    crew_training_skill,     # External
    skill_creator,           # Meta
])

root_agent = Agent(
    model=MODEL,
    name="knowledge_treasurer",
    tools=[skill_toolset],   # Auto-generuje 3 narzędzia!
    instruction="...",
)
```

`SkillToolset` automatycznie tworzy 3 narzędzia:
| Narzędzie | Poziom | Kiedy wywoływane |
|-----------|--------|-----------------|
| `list_skills` | L1 | Automatycznie przy każdym zapytaniu (wstrzykiwane w kontekst) |
| `load_skill` | L2 | Agent wywołuje gdy uzna skill za trafny |
| `load_skill_resource` | L3 | Agent wywołuje gdy instrukcje wskazują na plik referencyjny |

---

## 📁 Pliki w tym module

| Plik | Opis |
|------|------|
| `agent.py` | Agent z 4 wzorcami skills + SkillToolset |
| `skills/ship-maintenance/SKILL.md` | File-based skill: konserwacja statku (L2) |
| `skills/ship-maintenance/references/maintenance-checklist.md` | Checklista napraw (L3) |
| `skills/crew-training/SKILL.md` | External skill: szkolenie załogi (L2) |
| `skills/crew-training/references/training-procedures.md` | Procedury szkoleniowe (L3) |
| `.env.template` | Szablon konfiguracji |
| `requirements.txt` | Zależności (google-adk>=1.25.0) |

---

## 🚀 Konfiguracja

```bash
# 1. Konfiguracja środowiska
cd module_14_agent_skills
cp .env.template .env
# Edytuj .env — ustaw GOOGLE_CLOUD_PROJECT i/lub GOOGLE_API_KEY

# 2. Instalacja zależności (jeśli nie zainstalowane)
pip install -r requirements.txt

# 3. Autentykacja (jeśli używasz Vertex AI)
gcloud auth application-default login
```

> ⚠️ **Uwaga**: `SkillToolset` wymaga `google-adk >= 1.25.0` i jest oznaczony jako **EXPERIMENTAL**.

---

## ▶️ Uruchomienie Agenta

```bash
# WAŻNE: uruchamiaj z katalogu NADRZĘDNEGO, nie z wnętrza modułu!
adk web .
```

> ⚠️ Używaj `adk web .` a NIE `adk web module_14_agent_skills/` —
> w przeciwnym razie ADK odkryje katalog `skills/` jako osobną aplikację.

### Przykładowe zapytania

**Test inline skill (pirate-code):**
```
Jak dzielone są łupy po udanym rajdzie?
```
→ Agent wywołuje `load_skill("pirate-code")` i odpowiada na podstawie Kodeksu Pirata

**Test file-based skill (ship-maintenance) + L3 resource:**
```
Maszt główny pęka — co robić?
```
→ Agent wywołuje `load_skill("ship-maintenance")` → potem `load_skill_resource("ship-maintenance", "references/maintenance-checklist.md")` po szczegółową checklistę

**Test external skill (crew-training) + L3 resource:**
```
Mamy 5 nowych rekrutów. Przygotuj plan szkolenia dla artylerzystów.
```
→ Agent ładuje skill szkoleniowy + procedury z references/

**Test meta skill (skill-creator):**
```
Stwórz nowy skill do nawigacji po gwiazdach.
```
→ Agent ładuje skill-creatora, czyta specyfikację i przykład z references/, generuje kompletny SKILL.md

**Test negatywny (brak pasującego skilla):**
```
Jak naprawić silnik odrzutowy?
```
→ Agent sprawdza listę skilli, nie znajduje pasującego, informuje o braku i proponuje stworzenie nowego

---

## 🔄 Jak To Działa

```
Użytkownik: "Jak konserwować kadłub?"
    │
    ▼
┌─ L1: Agent skanuje metadata (zawsze w kontekście) ──────────┐
│  pirate-code: Kodeks Pirata, zasady, prawa...        ✗      │
│  ship-maintenance: Konserwacja statku, naprawy...    ✓ HIT  │
│  crew-training: Szkolenie załogi, rekrutacja...      ✗      │
│  skill-creator: Kreator nowych umiejętności...       ✗      │
└──────────────────────────────────────────────────────────────┘
    │
    ▼ Agent wywołuje: load_skill("ship-maintenance")
┌─ L2: Pełne instrukcje skilla ───────────────────────────────┐
│  "Krok 1: Identyfikacja obszaru — kadłub, pokład, maszty..." │
│  "Krok 2: Załaduj references/maintenance-checklist.md"       │
│  "Krok 3: Diagnoza i rekomendacja"                           │
└──────────────────────────────────────────────────────────────┘
    │
    ▼ Instrukcje wskazują: load_skill_resource("references/maintenance-checklist.md")
┌─ L3: Szczegółowa checklista ────────────────────────────────┐
│  "Kadłub: sprawdź grubość desek (min. 3 cale dębu)..."     │
│  "Procedura karenowania: 1. Znajdź piaszczystą zatokę..."  │
│  "Materiały: 20 desek dębowych, 5 beczek smoły..."         │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
Agent: "Karenowanie to kluczowa procedura! Oto plan napraw kadłuba..."
```

---

## 🏋️ Ćwiczenia

### Ćwiczenie 1: Dodaj Nowy Inline Skill (10 min)

Stwórz inline skill `treasure-appraisal` — wycena skarbów pirackich.

1. W `agent.py` zdefiniuj nowy `models.Skill()`:
   - `name`: `"treasure-appraisal"`
   - `description`: opis wskazujący na wycenę złota, klejnotów, artefaktów
   - `instructions`: zasady wyceny (waga, czystość złota, rzadkość klejnotów, wartość historyczna)
2. Dodaj go do listy `skills=[]` w `SkillToolset`
3. Uruchom agenta i zapytaj: *"Ile wart jest ten szmaragdowy naszyjnik?"*
4. Obserwuj w logach, że agent wywołuje `load_skill("treasure-appraisal")`

### Ćwiczenie 2: Stwórz File-Based Skill (15 min)

Stwórz file-based skill `sea-navigation` — nawigacja astronomiczna.

1. Utwórz katalog `skills/sea-navigation/`
2. Napisz `SKILL.md` z YAML frontmatter (`name: sea-navigation`) + instrukcje nawigacyjne
3. Utwórz `references/star-charts.md` z tabelą gwiazd nawigacyjnych (Polaris, Sirius, Canopus...)
4. W `agent.py` załaduj: `load_skill_from_dir(pathlib.Path(__file__).parent / "skills" / "sea-navigation")`
5. Dodaj do `SkillToolset` i przetestuj: *"Jak wyznaczyć pozycję z gwiazd?"*
6. Sprawdź, że agent ładuje L2 instrukcje, a potem L3 tabelę gwiazd

> 💡 **Pamiętaj**: Nazwa katalogu MUSI odpowiadać polu `name` w SKILL.md frontmatter!

### Ćwiczenie 3: Self-Extending Agent (20 min)

Użyj meta skill-creatora aby agent sam stworzył nowy skill.

1. Zapytaj agenta: *"Stwórz skill do pierwszej pomocy na morzu"*
2. Agent powinien:
   - Załadować `skill-creator`
   - Pobrać `references/skill-spec.md` i `references/example-skill.md`
   - Wygenerować kompletny SKILL.md
3. Skopiuj wygenerowany SKILL.md do nowego katalogu `skills/first-aid/SKILL.md`
4. Załaduj go w `agent.py` przez `load_skill_from_dir`
5. Zrestartuj agenta i przetestuj: *"Marynarz spadł z masztu, co robić?"*
6. Obserwuj jak nowo stworzony skill jest widoczny w L1 metadata i ładowany przez agenta

---

## ❓ Częste Problemy

| Problem | Rozwiązanie |
|---------|-------------|
| `ValueError: duplicate skill name` | Dwa skille mają to samo `name`. Każda nazwa musi być unikatowa. |
| `load_skill_from_dir` validation error | Nazwa katalogu (`ship-maintenance/`) nie zgadza się z `name` w SKILL.md fronmatter. Muszą być identyczne. |
| ADK odkrywa `skills/` jako osobną aplikację | Uruchamiaj `adk web .` z katalogu **nadrzędnego**, nie z wnętrza `module_14_agent_skills/`. |
| Agent nie ładuje skilli | Sprawdź czy `SkillToolset` jest w liście `tools=[]` agenta, nie w `sub_agents`. |
| `ImportError: cannot import SkillToolset` | Wymaga `google-adk >= 1.25.0`. Zaktualizuj: `pip install --upgrade google-adk` |
| Agent ignoruje dostępne skille | Upewnij się, że `description` w frontmatter zawiera konkretne słowa kluczowe pasujące do pytań. Opis "Pomocny skill" nie działa — "Konserwacja statku, naprawy, kadłub" działa. |

---

## 🆚 Skills vs MCP vs System Prompt

| Aspekt | System Prompt | Agent Skills | MCP Tools |
|--------|--------------|--------------|-----------|
| **Czym jest** | Tekst wstrzykiwany w każde zapytanie | Wiedza ładowana na żądanie | Narzędzia do akcji (API, bazy) |
| **Kiedy ładowane** | Zawsze | Gdy agent uzna za trafne | Gdy agent zdecyduje wykonać akcję |
| **Tokeny** | ~10 000 tok (wszystko zawsze) | ~400 tok baseline + on-demand | Definicje narzędzi w kontekście |
| **Cel** | Tożsamość i ogólne reguły | Wiedza domenowa i procedury | Łączność z zewnętrznymi systemami |
| **Reużywalność** | Kopiuj-wklej między agentami | Uniwersalny format SKILL.md | Standardowy protokół MCP |

**Skills i MCP się uzupełniają**: Skill mówi agentowi *co robić*, MCP daje *jak to wykonać*.

---

## 📝 Kluczowe Wnioski

1. **Progressive disclosure** redukuje bazowy kontekst o ~90% — agent ładuje wiedzę tylko gdy jej potrzebuje
2. **4 wzorce skills** pokrywają różne scenariusze: od prostych reguł (inline) po self-extending agents (meta)
3. **SkillToolset** automatycznie generuje 3 narzędzia (`list_skills`, `load_skill`, `load_skill_resource`) — zero boilerplate'u
4. **Opis (`description`)** jest kluczowy — to jedyny tekst który agent widzi w L1 i na jego podstawie decyduje czy skill załadować
5. **Agent Skills to otwarty standard** (agentskills.io) — te same pliki SKILL.md działają w ADK, Claude Code, Gemini CLI, Cursor i 40+ innych narzędziach

---

## 📚 Dalsze Materiały

- [ADK Skills — oficjalna dokumentacja](https://google.github.io/adk-docs/skills/)
- [Agent Skills Specification (agentskills.io)](https://agentskills.io/specification)
- [Seria blogowa Lavi Nigam — 3 części o ADK Skills](https://lavinigam.com/posts/adk-agent-skills-part1/)
- [awesome-claude-skills — 100+ gotowych skilli](https://github.com/ComposioHQ/awesome-claude-skills)
- [ADK skills_agent — oficjalny sample](https://github.com/google/adk-python/tree/main/contributing/samples/skills_agent/)
- [Companion repo (blog)](https://github.com/lavinigam-gcp/build-with-adk/tree/main/adk-agent-skills-tutorial)
