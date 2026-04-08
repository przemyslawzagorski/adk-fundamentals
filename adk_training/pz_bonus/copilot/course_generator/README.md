# 🎓 GitHub Copilot Course Generator

System agentowy do automatycznego generowania materiałów szkoleniowych GitHub Copilot z inteligentną priorytetyzacją.

## 🎯 Cel Projektu

Stworzenie **kompletnego programu szkoleniowego** dla GitHub Copilot w VS Code:
- **Pełne pokrycie dokumentacji** - wszystkie ~50 linków z oficjalnej dokumentacji
- **Inteligentna priorytetyzacja** - najważniejsze tematy (Agents, MCP, Customization) dostają 80% czasu
- **Jedno repozytorium Java** - praktyczne ćwiczenia na spring-petclinic
- **Język polski** - wszystkie materiały
- **Struktura tier-owa** - tier_1_critical (80%), tier_2_important (15%), tier_3_nice_to_have (5%)

## 🏗️ Architektura Systemu

System składa się z **5 agentów** działających sekwencyjnie:

### **Agent 1: DocumentationIngestionAgent**
- **Zadanie**: Pobiera i grupuje dokumentację według struktury URI
- **Input**: Plik `doc_links` z listą URL-i
- **Output**: Zgrupowane dokumenty (agents, chat, customization, guides, etc.)

### **Agent 2: DocumentationEvaluatorAgent**
- **Zadanie**: Ocenia przydatność i złożoność każdego dokumentu
- **Kryteria**: Practical Value, Complexity, Uniqueness, Exercise Potential
- **Output**: Wagi 1-5 dla każdego dokumentu + rekomendacje (DEEP/MEDIUM/SHALLOW)

### **Agent 3: PriorityAwareSyllabusPlannerAgent**
- **Zadanie**: Tworzy plan szkolenia z priorytetami i alokacją czasu
- **Output**: Struktura modułów z lekcjami, ćwiczeniami, czasem (JSON)

### **Agent 4: RepositoryFinderAgent**
- **Zadanie**: Znajduje optymalne repozytorium Java do ćwiczeń
- **Kryteria**: Stars, License, Topics, Size, Activity
- **Output**: Wybrane repo (np. spring-petclinic) + alternatywy

### **Agent 5: PriorityAwareContentGeneratorAgent**
- **Zadanie**: Generuje materiały szkoleniowe proporcjonalnie do wag
- **Output**: Pliki README.md, EXERCISES.md, konfiguracje (.github/copilot-instructions.md, .copilot/prompts/)

## 📊 Macierz Priorytetów

| Tier | Waga | Tematy | Czas | Materiały |
|------|------|--------|------|-----------|
| **Tier 1** | 5 | Agents, MCP, Customization, Skills, Context | 80% (~26h) | README 3000 słów, 10-15 ćwiczeń, 5 plików config |
| **Tier 2** | 3 | Chat, Subagents, TDD, Debug | 15% (~5h) | README 1200 słów, 3-5 ćwiczeń, 2 pliki config |
| **Tier 3** | 1 | Inline, Suggestions, Best Practices | 5% (~1h) | README 400 słów, 1-2 ćwiczenia |

## 🚀 Instalacja

```bash
# 1. Przejdź do katalogu
cd adk_training/pz_bonus/copilot/course_generator

# 2. Zainstaluj zależności
pip install -r requirements.txt

# 3. Skonfiguruj zmienne środowiskowe
cp .env.example .env
# Edytuj .env i dodaj GOOGLE_API_KEY
```

## 🎮 Użycie

### Podstawowe uruchomienie

```bash
python main.py
```

### Z parametrami

```bash
python main.py --doc-links doc_links --output-dir ./output/copilot_training
```

### Parametry

- `--doc-links`: Ścieżka do pliku z listą URL-i (domyślnie: `doc_links`)
- `--output-dir`: Katalog wyjściowy (domyślnie: `./output/copilot_training`)

## 📁 Struktura Outputu

```
output/copilot_training/
├── README.md                          # Główny opis szkolenia
├── SETUP.md                           # Jak sklonować spring-petclinic
├── LEARNING_PATH.md                   # Sugerowana ścieżka nauki
├── training_metadata.json             # Metadane (wagi, czas, priorytety)
│
├── tier_1_critical/                   # 80% materiałów
│   ├── module_01_tryb_agent/          # 8h
│   │   ├── README.md                  # 3500 słów
│   │   ├── EXERCISES.md               # 15 ćwiczeń
│   │   ├── ADVANCED_SCENARIOS.md
│   │   └── .copilot/examples/
│   ├── module_02_mcp_servers/         # 6h
│   └── ...
│
├── tier_2_important/                  # 15% materiałów
│   ├── module_06_copilot_chat/        # 2h
│   └── ...
│
└── tier_3_nice_to_have/               # 5% materiałów
    ├── module_09_inline_chat/         # 30min
    └── ...
```

## 🔧 Konfiguracja

Edytuj `config/agents_config.yaml` aby dostosować:
- Modele (gemini-2.5-pro vs gemini-2.5-flash)
- Temperatury (kreatywność vs determinizm)
- Alokację czasu (80/15/5)
- Kryteria oceny dokumentacji
- Szablony treści

## 🧪 Testowanie

```bash
# Test na podzbiorze URL-i (3-5 linków)
python main.py --doc-links doc_links_test
```

## 📚 Technologie

- **Google ADK 1.18.0** - Agent Development Kit
- **Gemini 2.5 Pro** - Planowanie i ewaluacja (thinking mode)
- **Gemini 2.5 Flash** - Generowanie treści (szybsze)
- **Pydantic** - Strukturyzowane outputy
- **BeautifulSoup** - Parsowanie HTML
- **GitHub API** - Wyszukiwanie repozytoriów

## 📖 Dokumentacja

- [Architektura systemu](docs/ARCHITECTURE.md) - Szczegóły implementacji
- [Plan v2.0](docs/PLAN_v2.0.md) - Pełny plan z priorytetyzacją
- [Przykłady](docs/EXAMPLES.md) - Przykładowe outputy

## 🤝 Autorzy

Projekt stworzony w ramach szkolenia ADK Fundamentals.

## 📄 Licencja

MIT License

