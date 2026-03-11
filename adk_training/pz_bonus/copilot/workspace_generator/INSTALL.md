# 🚀 INSTALACJA - GitHub Copilot Masterclass Workspace Generator

**Wersja:** 1.0.0  
**Google ADK:** 1.18.0  
**Status:** ✅ Gotowy do użycia

---

## 📋 WYMAGANIA

### 1. Python 3.10+
```bash
python --version  # Powinno być >= 3.10
```

### 2. Google Cloud Project (opcjonalne, ale zalecane)
- Projekt GCP z włączonym Vertex AI
- API Key dla Gemini (lub Application Default Credentials)

---

## 🔧 INSTALACJA KROK PO KROKU

### Krok 1: Klonuj repozytorium (jeśli jeszcze nie masz)
```bash
cd adk_training/pz_bonus/copilot/workspace_generator
```

### Krok 2: Stwórz virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Krok 3: Zainstaluj zależności
```bash
# Instalacja podstawowa (wymagane)
pip install --upgrade pip
pip install google-adk==1.18.0
pip install google-cloud-aiplatform[adk,agent_engines]==1.126.1
pip install python-dotenv
pip install pydantic>=2.0.0
pip install pyyaml>=6.0.0

# Instalacja narzędzi (wymagane)
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0
pip install googlesearch-python>=1.2.0
pip install aiohttp

# Instalacja walidacji kodu (wymagane)
pip install javalang>=0.13.0

# Instalacja MCP (dla modułu 7)
pip install fastmcp==2.12.5

# LUB zainstaluj wszystko naraz:
pip install -r requirements.txt
```

### Krok 4: Konfiguracja API Key
```bash
# Opcja A: Plik .env (zalecane)
echo "GOOGLE_API_KEY=your-api-key-here" > .env
echo "ADK_MODEL=gemini-2.5-flash" >> .env

# Opcja B: Environment variable
export GOOGLE_API_KEY="your-api-key-here"
export ADK_MODEL="gemini-2.5-flash"

# Windows (PowerShell)
$env:GOOGLE_API_KEY="your-api-key-here"
$env:ADK_MODEL="gemini-2.5-flash"
```

### Krok 5: Weryfikacja instalacji
```bash
# Test importów
python -c "from google.adk.agents import LlmAgent; print('✅ ADK OK')"
python -c "from pydantic import BaseModel; print('✅ Pydantic OK')"
python -c "import yaml; print('✅ YAML OK')"
```

---

## 🎯 SZYBKI START

### Test 1: Dry Run (tylko planowanie)
```bash
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --dry-run
```

### Test 2: Generowanie workspace'a
```bash
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --output-dir ./output/test_workspace
```

### Test 3: Verbose mode (więcej logów)
```bash
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --verbose
```

---

## 🔍 TROUBLESHOOTING

### Problem 1: "ModuleNotFoundError: No module named 'google.adk'"
```bash
# Rozwiązanie:
pip uninstall google-adk
pip install google-adk==1.18.0
pip install google-cloud-aiplatform[adk,agent_engines]==1.126.1
```

### Problem 2: "ImportError: cannot import name 'LlmAgent'"
```bash
# Sprawdź wersję:
pip show google-adk

# Powinna być: 1.18.0
# Jeśli nie, przeinstaluj:
pip install --force-reinstall google-adk==1.18.0
```

### Problem 3: "API Key not found"
```bash
# Sprawdź czy zmienna jest ustawiona:
echo $GOOGLE_API_KEY  # Linux/Mac
echo %GOOGLE_API_KEY%  # Windows CMD
$env:GOOGLE_API_KEY    # Windows PowerShell

# Jeśli pusta, ustaw:
export GOOGLE_API_KEY="your-key"  # Linux/Mac
set GOOGLE_API_KEY=your-key       # Windows CMD
$env:GOOGLE_API_KEY="your-key"    # Windows PowerShell
```

### Problem 4: "googlesearch-python not found"
```bash
# To nie jest błąd krytyczny - system użyje mocka
# Ale jeśli chcesz prawdziwe wyszukiwanie:
pip install googlesearch-python>=1.2.0
```

### Problem 5: "Pydantic validation error"
```bash
# Sprawdź wersję Pydantic:
pip show pydantic

# Powinna być >= 2.0.0
# Jeśli nie, zaktualizuj:
pip install --upgrade pydantic>=2.0.0
```

---

## 📦 INSTALACJA OPCJONALNYCH KOMPONENTÓW

### Google Cloud Services (dla zaawansowanych funkcji)
```bash
pip install google-cloud-storage
pip install google-cloud-bigquery
pip install google-cloud-spanner==3.56.0
```

### UI & Monitoring
```bash
pip install gradio
pip install locust
pip install colorlog>=6.8.0
pip install tqdm>=4.66.0
```

### Testing
```bash
pip install pytest>=8.0.0
pip install pytest-asyncio>=0.23.0
pip install pytest-cov>=4.1.0
```

---

## ✅ WERYFIKACJA KOMPLETNA

Po instalacji, uruchom:
```bash
python -c "
from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from pydantic import BaseModel, Field
import yaml
print('✅ Wszystkie importy działają!')
print('✅ System gotowy do użycia!')
"
```

---

## 🎓 NASTĘPNE KROKI

1. ✅ Przeczytaj [README.md](README.md)
2. ✅ Przeczytaj [QUICKSTART.md](QUICKSTART.md)
3. ✅ Uruchom dry-run
4. ✅ Wygeneruj pierwszy workspace

---

**Powodzenia! 🚀🏴‍☠️**

