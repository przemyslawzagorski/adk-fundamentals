# 🎓 PRZEWODNIK DLA TRENERA
## Szkolenie Google ADK - 2 Dni

---

## 📋 CHECKLIST PRZED SZKOLENIEM

### 1 Tydzień Przed (T-7)
- [ ] Wyślij uczestnikom email z wymaganiami technicznymi
- [ ] Poproś o instalację: Python 3.10+, Google Cloud SDK, ADK
- [ ] Poproś o utworzenie Google Cloud Project
- [ ] Wyślij link do repozytorium GitHub
- [ ] Zarezerwuj salę szkoleniową (projektor, WiFi, gniazdka)

### 3 Dni Przed (T-3)
- [ ] Przypomnij o wymaganiach technicznych
- [ ] Wyślij agendę szczegółową
- [ ] Przygotuj certyfikaty (szablony PDF)
- [ ] Przetestuj wszystkie moduły na czystym środowisku
- [ ] Przygotuj backup USB z kodem (na wypadek problemów z WiFi)

### 1 Dzień Przed (T-1)
- [ ] Sprawdź salę (projektor działa, WiFi działa)
- [ ] Wydrukuj certyfikaty
- [ ] Przygotuj materiały (handbook PDF, mapy)
- [ ] Przetestuj live demo (RAG, Memory Bank)
- [ ] Przygotuj Vertex AI Data Store dla Module 03

### Rano w Dniu Szkolenia
- [ ] Przyjdź 30 min wcześniej
- [ ] Sprawdź projektor, laptop, WiFi
- [ ] Rozłóż materiały na stołach
- [ ] Przygotuj kawę/wodę
- [ ] Napisz na tablicy: WiFi password, GitHub repo URL

---

## 🎯 KLUCZOWE ZASADY PROWADZENIA

### 1. Tempo
- **Teoria:** Max 15-20 min (ludzie się nudzą)
- **Praktyka:** Min 30-45 min (hands-on jest najważniejsze)
- **Przerwy:** Co 60-75 min (ludzie potrzebują odpoczynku)

### 2. Interaktywność
- **Pytaj często:** "Kto już to zrobił?", "Kto ma problem?"
- **Live coding:** Koduj razem z uczestnikami (nie tylko slajdy)
- **Pokaż błędy:** Celowo zrób błąd i napraw - uczą się więcej
- **Ochotnicy:** Poproś o pokazanie rozwiązań (2-3 osoby na moduł)

### 3. Pomoc
- **Chodź między uczestnikami:** Nie stój tylko przy tablicy
- **Asystent:** Jeśli grupa >10 osób, poproś kogoś o pomoc
- **Slack/Discord:** Stwórz kanał dla szkolenia - szybsza pomoc
- **Pair programming:** Zachęć do pracy w parach

### 4. Energia
- **Entuzjazm:** Jeśli Ty się nudzisz, oni się nudzą
- **Humor:** Żarty pirackie ("Arrr!", "Shiver me timbers!")
- **Wow moments:** Podkreślaj cool rzeczy (Memory Bank, RAG)
- **Przerwy:** Nie skracaj przerw - ludzie potrzebują odpoczynku

---

## ⚠️ TYPOWE PROBLEMY I ROZWIĄZANIA

### Problem 1: "ADK nie działa"
**Objawy:** Import error, module not found

**Rozwiązanie:**
```bash
# Sprawdź wersję Python
python --version  # Musi być 3.10+

# Reinstaluj ADK
pip uninstall google-adk
pip install google-adk --upgrade

# Sprawdź instalację
python -c "from google.adk.agents import LlmAgent; print('OK')"
```

### Problem 2: "Google Cloud nie działa"
**Objawy:** Authentication error, quota exceeded

**Rozwiązanie:**
```bash
# Zaloguj ponownie
gcloud auth login
gcloud auth application-default login

# Sprawdź projekt
gcloud config get-value project

# Sprawdź quota
gcloud alpha billing quotas list --service=aiplatform.googleapis.com
```

### Problem 3: "adk web nie startuje"
**Objawy:** Port zajęty, błąd importu

**Rozwiązanie:**
```bash
# Zmień port
adk web --port 8001

# Sprawdź czy agent.py ma błędy
python -m py_compile agent.py

# Sprawdź .env
cat .env  # Czy wszystkie zmienne są ustawione?
```

### Problem 4: "Vertex AI Memory Bank nie działa"
**Objawy:** Agent Engine not found

**Rozwiązanie:**
```bash
# Sprawdź czy Agent Engine istnieje
gcloud ai agent-engines list --location=us-central1

# Sprawdź AGENT_ENGINE_RESOURCE_NAME w .env
echo $AGENT_ENGINE_RESOURCE_NAME

# Poczekaj 5 min po utworzeniu (propagacja)
```

### Problem 5: "Uczestnik daleko w tyle"
**Rozwiązanie:**
- Przydziel mu asystenta (innego uczestnika który skończył)
- Daj mu working code (z `agent_solution.py`)
- Powiedz "Nadrobisz w przerwie, teraz obserwuj"
- Nie zatrzymuj całej grupy dla 1 osoby

---

## 🎬 TIPS DLA KAŻDEGO MODUŁU

### Module 01: Hello World
- **Tip:** Pokaż różne temperature (0.1 vs 0.9) - widać różnicę
- **Pułapka:** Ludzie zapominają `adk web` - przypominaj
- **Wow:** Zmień instruction na coś śmiesznego - agent się zmienia!

### Module 02: Custom Tool
- **Tip:** Pokaż jak agent SAM decyduje kiedy użyć tool
- **Pułapka:** Brak docstring → agent nie wie co robi tool
- **Wow:** Chain 3 tools w jednym zapytaniu

### Module 04: Sequential
- **Tip:** Narysuj diagram flow na tablicy
- **Pułapka:** Zapominają o `output_key` → dane się nie przekazują
- **Wow:** Pokaż jak state rośnie z każdym agentem

### Module 07: Parallel
- **Tip:** Zmierz czas Sequential vs Parallel - konkretne liczby
- **Pułapka:** Myślą że Parallel = zawsze lepszy (nie dla zależnych zadań)
- **Wow:** 4 agentów równocześnie = 4x szybciej

### Module 12: Router
- **Tip:** Pokaż jak zmiana description zmienia routing
- **Pułapka:** Zbyt podobne descriptions → router się myli
- **Wow:** Zadaj pytanie które pasuje do 2 ekspertów - router wybierze!

### Module 05: Human-in-Loop
- **Tip:** Pokaż UI approval flow (kliknij APPROVE/REJECT)
- **Pułapka:** Zapominają dodać FunctionTool wrapper
- **Wow:** Approval log - audit trail

### Module 08: Loop Critique
- **Tip:** Pokaż jak jakość rośnie z iteracjami (iteracja 1 vs 3)
- **Pułapka:** Brak max_iterations → nieskończona pętla
- **Wow:** Quality score - konkretne liczby

### Module 09: Database
- **Tip:** Pokaż plik `kronika.db` w DB Browser
- **Pułapka:** Zapominają `conn.commit()` → dane się nie zapisują
- **Wow:** Restart agenta - dane przetrwały!

### Module 11: Memory Bank
- **Tip:** Pokaż 2 sesje obok siebie - agent pamięta!
- **Pułapka:** Agent Engine creation trwa 5 min - zrób wcześniej
- **Wow:** "Jaka jest moja ulubiona temperatura?" → agent wie!

### Module 03: RAG
- **Tip:** Przygotuj Data Store WCZEŚNIEJ (indexing 15-30 min)
- **Pułapka:** Brak dokumentów → nic nie znajdzie
- **Wow:** Agent cytuje źródła - enterprise ready!

---

## 📊 TIMING MANAGEMENT

### Jeśli Jesteś Przed Czasem (+30 min)
1. Dodaj bonusowe ćwiczenia
2. Więcej live demo
3. Dłuższe Q&A
4. Pokaż zaawansowane przykłady

### Jeśli Jesteś Za Czasem (-30 min)
1. Skróć Module 08 (45 min → 30 min)
2. Skróć Module 11 (60 min → 45 min, demo zamiast hands-on)
3. Pomiń Module 03 (RAG) - opcjonalny
4. Skróć przerwy (15 min → 10 min)

### Jeśli Jesteś Bardzo Za Czasem (-60 min)
1. Pomiń Module 08 (Loop Critique)
2. Pomiń Module 03 (RAG)
3. Module 11 tylko demo (15 min)
4. Skróć ćwiczenia (1 zamiast 2)

---

## 🎤 PRZYKŁADOWE FRAZY

### Rozpoczęcie Modułu
> "Dobra, następny moduł! To będzie ciekawe - [nazwa modułu]. Kto słyszał o [koncepcja]? [pauza] Świetnie! Pokażę Wam jak to działa w ADK."

### Przejście do Praktyki
> "Teoria za nami - teraz najważniejsze: PRAKTYKA! Otwórzcie `[ścieżka]`. Macie [X] minut. Pytania? Nie? To START!"

### Pomoc
> "Widzę że niektórzy mają problem. To normalne! Podchodzę, pomogę. Reszta - pracujcie dalej."

### Podsumowanie
> "Świetnie! Widzę że większość ma działające rozwiązanie. Kto chce pokazać? [wybierz 2 osoby] Brawo! Następny moduł..."

### Motywacja
> "To był trudny moduł, ale daliście radę! Teraz jesteście [poziom]. Jeszcze [X] modułów i będziecie admirałami! ⚓"

---

## 📝 FEEDBACK

### Po Każdym Module (szybkie)
- "Thumbs up jeśli było OK, thumbs down jeśli za trudne"
- Dostosuj tempo na podstawie reakcji

### Po Dniu 1
- "Co było najlepsze? Co poprawić jutro?"
- Krótka ankieta (3 pytania, 2 min)

### Po Szkoleniu
- Pełna ankieta (link)
- Zbierz certyfikaty podpisane
- Zdjęcie grupowe

---

## 🎁 BONUSY

### Dla Szybkich Uczestników
- Zaawansowane ćwiczenia w `agent_solution.py`
- "Połącz 3 moduły w jeden system"
- "Dodaj własny use case"

### Dla Wszystkich
- Handbook PDF (wszystkie przykłady)
- Mapa Archipelagu ADK (poster)
- Dostęp do Slack/Discord community
- Certyfikat PDF + fizyczny

---

**Powodzenia, Kapitanie-Trenerze!** ⚓🏴‍☠️

