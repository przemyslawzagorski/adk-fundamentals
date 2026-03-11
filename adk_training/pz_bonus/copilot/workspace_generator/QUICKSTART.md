# 🚀 QUICKSTART - 5 Minut do Pierwszego Workspace'a

**Najszybsza droga do uruchomienia systemu agentowego**

---

## ⚡ SUPER QUICK START (1 minuta)

```bash
# 1. Clone & Install
git clone <repo>
cd workspace_generator
pip install -r requirements.txt

# 2. Configure API
export GOOGLE_API_KEY="your-api-key-here"

# 3. Run!
python main.py --training-plan ../opis_szkolenia_plan_copilot

# 4. Check output
ls -la ./output/copilot_masterclass_workspace/
```

**Gotowe!** 🎉

---

## 📋 PREREQUISITES (2 minuty)

### 1. Python 3.10+

```bash
# Check version
python --version  # Should be 3.10 or higher

# If not, install:
# - Windows: https://www.python.org/downloads/
# - Mac: brew install python@3.10
# - Linux: sudo apt install python3.10
```

### 2. Google AI Studio API Key

```bash
# Get API key from:
# https://aistudio.google.com/app/apikey

# Set environment variable
export GOOGLE_API_KEY="AIza..."

# Or create .env file
echo "GOOGLE_API_KEY=AIza..." > .env
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🎯 PODSTAWOWE UŻYCIE (5 minut)

### Krok 1: Przygotuj Plan Szkolenia

```bash
# Użyj istniejącego planu
cat ../opis_szkolenia_plan_copilot

# Lub stwórz własny
cat > my_training_plan.txt << EOF
Program Szkolenia: GitHub Copilot Masterclass
Moduł 1: Komunikacja z AI
Moduł 2: Refaktoring
...
EOF
```

### Krok 2: Uruchom Generator

```bash
# Podstawowe uruchomienie
python main.py --training-plan ../opis_szkolenia_plan_copilot

# Z custom output directory
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --output-dir ./my_workspace

# Verbose mode (więcej logów)
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --verbose
```

### Krok 3: Sprawdź Wyniki

```bash
# Lista wygenerowanych plików
ls -la ./output/copilot_masterclass_workspace/

# Sprawdź raport
cat ./output/copilot_masterclass_workspace/FINAL_REPORT.md

# Sprawdź state
cat ./output/copilot_masterclass_workspace/generation_state.json | jq .
```

---

## 🔧 ZAAWANSOWANE OPCJE (10 minut)

### Dry Run (Tylko Planning)

```bash
# Generuj tylko plan, bez plików
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --dry-run

# Sprawdź execution plan
cat ./output/execution_plan.json | jq .
```

### Custom Configuration

```bash
# Użyj custom config
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --config config/custom_config.yaml
```

### Single Module Generation

```python
# generate_single_module.py
from workspace_generator import CopilotMasterclassWorkspaceGenerator

generator = CopilotMasterclassWorkspaceGenerator(
    training_plan_path="opis_szkolenia_plan_copilot",
    output_dir="./output/module5_only"
)

# Generate only Module 5
result = generator.generate_module(module_id=5)
```

---

## 🐛 TROUBLESHOOTING

### Problem: "ModuleNotFoundError: No module named 'google.adk'"

**Rozwiązanie:**
```bash
# Google ADK może nie być jeszcze w PyPI
# Zainstaluj z GitHub:
pip install git+https://github.com/google/adk.git

# Lub użyj mock implementation (development)
# System automatycznie wykryje brak ADK i użyje mock
```

### Problem: "API Key not found"

**Rozwiązanie:**
```bash
# Sprawdź czy zmienna jest ustawiona
echo $GOOGLE_API_KEY

# Jeśli pusta, ustaw:
export GOOGLE_API_KEY="your-key"

# Lub dodaj do .env
echo "GOOGLE_API_KEY=your-key" > .env
```

### Problem: "Rate limit exceeded"

**Rozwiązanie:**
```bash
# Zmniejsz batch size w config
# config/agents_config.yaml
orchestration:
  execution_phase:
    batch_size: 1  # Zamiast 3

# Lub dodaj delay między requestami
global:
  retry_delay_seconds: 10  # Zamiast 5
```

---

## 📊 CO DALEJ?

### Dla Beginnerów
1. ✅ Uruchomiłeś system - **GRATULACJE!** 🎉
2. 📖 Przeczytaj [README.md](README.md) - zrozum architekturę
3. 📚 Zobacz [EXAMPLES.md](docs/EXAMPLES.md) - przykłady użycia
4. 🧪 Eksperymentuj z parametrami

### Dla Intermediate
1. 📐 Przeczytaj [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. 🛠️ Zaimplementuj własne narzędzie
3. 🤖 Stwórz custom agenta
4. 🧪 Napisz testy

### Dla Advanced
1. 📖 Przeczytaj całą dokumentację ([INDEX.md](docs/INDEX.md))
2. 🔧 Zoptymalizuj system
3. 🚀 Deploy do produkcji
4. 🤝 Kontrybuuj do projektu

---

## 📚 DOKUMENTACJA

| Dokument | Opis | Czas |
|----------|------|------|
| [README.md](README.md) | Główna dokumentacja | 10 min |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architektura systemu | 30 min |
| [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | Przewodnik implementacji | 45 min |
| [EXAMPLES.md](docs/EXAMPLES.md) | 7 przykładów użycia | 30 min |
| [INDEX.md](docs/INDEX.md) | Spis treści | 5 min |
| [SUMMARY.md](SUMMARY.md) | Podsumowanie systemu | 10 min |

---

## 🎯 NASTĘPNE KROKI

```bash
# 1. Przeczytaj README
cat README.md

# 2. Zobacz przykłady
cat docs/EXAMPLES.md

# 3. Zrozum architekturę
cat docs/ARCHITECTURE.md

# 4. Eksperymentuj!
python main.py --help
```

---

## 💡 WSKAZÓWKI

### Tip 1: Zacznij od Dry Run
```bash
# Najpierw zobacz plan, potem generuj
python main.py --training-plan plan.txt --dry-run
```

### Tip 2: Użyj Verbose Mode
```bash
# Więcej logów = łatwiejszy debugging
python main.py --training-plan plan.txt --verbose
```

### Tip 3: Zapisuj Intermediate Results
```bash
# W config/agents_config.yaml
global:
  save_intermediate_results: true
```

### Tip 4: Testuj na Małym Planie
```bash
# Stwórz mini plan (1-2 moduły) do testów
cat > mini_plan.txt << EOF
Moduł 1: Test
Moduł 2: Test
EOF

python main.py --training-plan mini_plan.txt
```

---

## 🎉 GRATULACJE!

Uruchomiłeś system agentowy! 🚀

**Co teraz?**
- 📖 Czytaj dokumentację
- 🧪 Eksperymentuj
- 🤖 Twórz własnych agentów
- 🤝 Dziel się wynikami!

---

**Powodzenia! 🏴‍☠️**

