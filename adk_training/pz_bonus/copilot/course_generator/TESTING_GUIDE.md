# 🧪 Testing Guide - Course Generator

Przewodnik po testowaniu systemu course_generator.

---

## 🎯 Cel Testowania

Przed uruchomieniem na pełnym zbiorze ~50 URL-i, przetestuj system na małym podzbiorze (3-5 linków) z różnych tier-ów.

---

## 📋 Przygotowanie Testu

### 1. Utwórz plik testowy `doc_links_test`

Wybierz 5 URL-i reprezentujących różne tier-y:

```bash
# Utwórz plik doc_links_test
cat > doc_links_test << 'EOF'
https://code.visualstudio.com/docs/copilot/customization/mcp-servers
https://code.visualstudio.com/docs/copilot/agents/planning
https://code.visualstudio.com/docs/copilot/chat/copilot-chat
https://code.visualstudio.com/docs/copilot/chat/inline-chat
https://code.visualstudio.com/docs/copilot/best-practices
EOF
```

**Uzasadnienie wyboru:**
- **Tier 1 (waga 5)**: MCP Servers, Agent Planning
- **Tier 2 (waga 3)**: Copilot Chat
- **Tier 3 (waga 1)**: Inline Chat, Best Practices

### 2. Upewnij się, że .env jest skonfigurowany

```bash
# Sprawdź czy .env istnieje
cat .env

# Powinien zawierać:
# GOOGLE_API_KEY=AIzaSy...
# USE_BUILTIN_PLANNER=true
```

---

## 🚀 Uruchomienie Testu

### Test 1: Podstawowy (bez thinking mode)

```bash
# Wyłącz thinking mode dla szybszego testu
export USE_BUILTIN_PLANNER=false

# Uruchom na testowym zbiorze
python main.py --doc-links doc_links_test --output-dir ./output/test_basic
```

**Oczekiwany czas:** ~3-5 minut

**Oczekiwany output:**
```
output/test_basic/
├── README.md
├── SETUP.md
├── LEARNING_PATH.md
├── training_metadata.json
├── tier_1_critical/
│   ├── module_01_mcp_servers/
│   └── module_02_agent_planning/
├── tier_2_important/
│   └── module_03_copilot_chat/
└── tier_3_nice_to_have/
    ├── module_04_inline_chat/
    └── module_05_best_practices/
```

### Test 2: Z thinking mode

```bash
# Włącz thinking mode dla lepszej jakości
export USE_BUILTIN_PLANNER=true

# Uruchom na testowym zbiorze
python main.py --doc-links doc_links_test --output-dir ./output/test_thinking
```

**Oczekiwany czas:** ~8-12 minut

**Różnice vs Test 1:**
- Głębsza analiza dokumentacji
- Lepsze oceny i priorytetyzacja
- Bardziej szczegółowe plany lekcji

---

## ✅ Weryfikacja Wyników

### 1. Sprawdź strukturę katalogów

```bash
# Wyświetl drzewo katalogów
tree output/test_basic -L 3

# Lub na Windows:
dir output\test_basic /s
```

**Oczekiwane:**
- 3 katalogi tier (tier_1, tier_2, tier_3)
- 5 modułów (po jednym dla każdego URL)
- Pliki README.md, EXERCISES.md w każdym module

### 2. Sprawdź proporcje treści

```bash
# Policz słowa w README.md dla każdego tier
wc -w output/test_basic/tier_1_critical/module_01_mcp_servers/README.md
wc -w output/test_basic/tier_2_important/module_03_copilot_chat/README.md
wc -w output/test_basic/tier_3_nice_to_have/module_04_inline_chat/README.md
```

**Oczekiwane proporcje:**
- Tier 1: ~2500-3500 słów
- Tier 2: ~1000-1500 słów
- Tier 3: ~300-500 słów

### 3. Sprawdź liczbę ćwiczeń

```bash
# Policz ćwiczenia (linie zaczynające się od "## Ćwiczenie")
grep -c "## Ćwiczenie" output/test_basic/tier_1_critical/module_01_mcp_servers/EXERCISES.md
grep -c "## Ćwiczenie" output/test_basic/tier_2_important/module_03_copilot_chat/EXERCISES.md
grep -c "## Ćwiczenie" output/test_basic/tier_3_nice_to_have/module_04_inline_chat/README.md
```

**Oczekiwane:**
- Tier 1: 10-15 ćwiczeń
- Tier 2: 3-5 ćwiczeń
- Tier 3: 1-2 ćwiczenia

### 4. Sprawdź training_metadata.json

```bash
# Wyświetl metadane
cat output/test_basic/training_metadata.json | python -m json.tool
```

**Oczekiwane pola:**
```json
{
  "modules": [...],
  "total_estimated_hours": 5-8,
  "tier_1_hours": ~4-6,
  "tier_2_hours": ~1-2,
  "tier_3_hours": ~0.5-1
}
```

---

## 🐛 Troubleshooting

### Problem: Agent nie zwraca strukturyzowanego outputu

**Symptom:**
```
❌ Brak event.data, próbuję wydobyć JSON z tekstu...
```

**Rozwiązanie:**
- To normalne - ADK czasem zwraca tekst zamiast Pydantic model
- System automatycznie parsuje JSON z tekstu
- Sprawdź czy output jest poprawny mimo ostrzeżenia

### Problem: GitHub API rate limit

**Symptom:**
```
Error searching GitHub: 403 rate limit exceeded
```

**Rozwiązanie:**
```bash
# Dodaj GITHUB_TOKEN do .env
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

# Lub użyj fallback (spring-petclinic)
# Agent automatycznie zaproponuje spring-petclinic jeśli API nie działa
```

### Problem: Timeout podczas pobierania URL-i

**Symptom:**
```
Timeout fetching https://...
```

**Rozwiązanie:**
- Sprawdź połączenie internetowe
- Zwiększ timeout w `tools/web_fetcher.py` (domyślnie 30s)
- Pomiń problematyczne URL-e (usuń z doc_links_test)

---

## 📊 Metryki Sukcesu

Test jest **UDANY** jeśli:

✅ Wszystkie 5 agentów zakończyły pracę bez błędów  
✅ Wygenerowano 5 modułów (po jednym dla każdego URL)  
✅ Proporcje treści są zgodne z wagami (Tier 1 > Tier 2 > Tier 3)  
✅ Pliki konfiguracyjne są obecne w Tier 1 (.github/copilot-instructions.md, .copilot/prompts/)  
✅ Wybrano repozytorium Java (spring-petclinic lub podobne)  
✅ training_metadata.json zawiera poprawne dane  

---

## 🚀 Następny Krok: Pełne Uruchomienie

Jeśli test przeszedł pomyślnie:

```bash
# Uruchom na pełnym zbiorze ~50 URL-i
python main.py --doc-links doc_links --output-dir ./output/copilot_training

# Oczekiwany czas: ~15-20 minut (z thinking mode)
```

---

## 📝 Raportowanie Problemów

Jeśli napotkasz problemy:

1. **Zapisz logi:**
   ```bash
   python main.py --doc-links doc_links_test 2>&1 | tee test.log
   ```

2. **Sprawdź:**
   - Wersję Python (`python --version` - powinno być 3.11+)
   - Wersję ADK (`pip show google-adk` - powinno być 1.18.0)
   - Dostępność API (`curl https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY`)

3. **Dołącz do raportu:**
   - Plik `test.log`
   - Zawartość `.env` (bez API key!)
   - Output `pip list | grep google`

---

**Powodzenia w testowaniu!** 🎉

