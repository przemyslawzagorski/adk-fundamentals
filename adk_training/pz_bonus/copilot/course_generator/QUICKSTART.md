# 🚀 Quick Start Guide

Szybki start z GitHub Copilot Course Generator.

## ⚡ 5-Minute Setup

### 1. Przejdź do katalogu

```bash
cd adk_training/pz_bonus/copilot/course_generator
```

### 2. Zainstaluj zależności

```bash
pip install -r requirements.txt
```

### 3. Skonfiguruj API Key

```bash
# Skopiuj przykładowy plik
cp .env.example .env

# Edytuj .env i dodaj swój GOOGLE_API_KEY
# Pobierz klucz z: https://aistudio.google.com/apikey
```

Przykład `.env`:
```
GOOGLE_API_KEY=AIzaSy...your_key_here
USE_BUILTIN_PLANNER=true
```

### 4. Uruchom generator

```bash
python main.py
```

## 📋 Co się dzieje?

System automatycznie:

1. **Wczytuje listę URL-i** z pliku `doc_links` (~50 linków do dokumentacji VS Code Copilot)

2. **Grupuje dokumentację** według kategorii (agents, chat, customization, etc.)

3. **Ocenia każdy dokument** i przypisuje wagi 1-5:
   - Waga 5: MCP, Custom Agents, Skills → 80% czasu
   - Waga 3: Chat, Subagents → 15% czasu
   - Waga 1: Inline, Suggestions → 5% czasu

4. **Tworzy plan szkolenia** (~32h) z modułami, lekcjami, ćwiczeniami

5. **Znajduje repozytorium Java** (np. spring-petclinic) do praktycznych ćwiczeń

6. **Generuje materiały**:
   - README.md (teoria)
   - EXERCISES.md (ćwiczenia)
   - Pliki konfiguracyjne (.github/copilot-instructions.md, .copilot/prompts/)

## 📁 Gdzie są wyniki?

```
output/copilot_training/
├── README.md                    # Główny opis kursu
├── SETUP.md                     # Instrukcje setup
├── tier_1_critical/             # Najważniejsze moduły (80%)
│   ├── module_01_tryb_agent/
│   ├── module_02_mcp_servers/
│   └── ...
├── tier_2_important/            # Ważne moduły (15%)
└── tier_3_nice_to_have/         # Nice-to-have (5%)
```

## ⏱️ Ile to trwa?

- **Z thinking mode** (USE_BUILTIN_PLANNER=true): ~15-20 minut
- **Bez thinking mode** (USE_BUILTIN_PLANNER=false): ~8-10 minut

## 🔧 Troubleshooting

### Problem: "GOOGLE_API_KEY not found"

**Rozwiązanie:**
```bash
# Sprawdź czy .env istnieje
ls -la .env

# Jeśli nie, skopiuj z przykładu
cp .env.example .env

# Edytuj i dodaj klucz
nano .env  # lub notepad .env na Windows
```

### Problem: "Rate limit exceeded" (GitHub API)

**Rozwiązanie:**
```bash
# Dodaj GITHUB_TOKEN do .env
# Pobierz token z: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_token_here
```

### Problem: "Module not found"

**Rozwiązanie:**
```bash
# Upewnij się, że jesteś w katalogu course_generator
pwd  # powinno pokazać: .../course_generator

# Zainstaluj ponownie zależności
pip install -r requirements.txt --upgrade
```

## 🎯 Następne kroki

1. **Przejrzyj wygenerowane materiały** w `output/copilot_training/`

2. **Dostosuj konfigurację** w `config/agents_config.yaml`:
   - Zmień alokację czasu (80/15/5)
   - Dostosuj kryteria oceny
   - Zmień modele (pro vs flash)

3. **Uruchom ponownie** z własnymi parametrami:
   ```bash
   python main.py --output-dir ./my_custom_course
   ```

4. **Przetestuj na podzbiorze** (szybszy test):
   - Stwórz `doc_links_test` z 5 URL-ami
   - Uruchom: `python main.py --doc-links doc_links_test`

## 📚 Więcej informacji

- [README.md](README.md) - Pełna dokumentacja
- [config/agents_config.yaml](config/agents_config.yaml) - Konfiguracja agentów
- [doc_links](doc_links) - Lista URL-i do przetworzenia

## 🆘 Pomoc

Jeśli masz problemy:
1. Sprawdź logi w konsoli
2. Upewnij się, że GOOGLE_API_KEY jest poprawny
3. Sprawdź czy masz dostęp do internetu (pobieranie dokumentacji)
4. Sprawdź limity API (Google AI Studio)

---

**Gotowe!** 🎉 Twój kurs GitHub Copilot jest generowany automatycznie!

