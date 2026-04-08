# 🏴‍☠️ SZKOLENIE GOOGLE ADK - KOMPLETNY PAKIET
## *"Od Rekruta do Admirała: Podróż przez Archipelag ADK"*

---

## 📦 ZAWARTOŚĆ PAKIETU

Ten folder zawiera **kompletny pakiet materiałów** do przeprowadzenia 2-dniowego szkolenia z Google Agent Development Kit (ADK).

### 📚 Dokumenty Główne

| Plik | Opis | Dla Kogo |
|------|------|----------|
| **PLAN_SZKOLENIA_NARRACJA.md** | Szczegółowy plan prezentacji z narracją (co mówić, kiedy, jak) | 👨‍🏫 Trener |
| **PRZEWODNIK_TRENERA.md** | Checklist, tips, troubleshooting, timing management | 👨‍🏫 Trener |
| **MAPA_ARCHIPELAGU_ADK.md** | Wizualna mapa wszystkich modułów i zależności | 👨‍🎓 Wszyscy |
| **QUICK_REFERENCE.md** | Ściągawka - wzorce kodu, komendy, debugging | 👨‍💻 Uczestnicy |
| **SZABLON_CERTYFIKATU.md** | Szablon certyfikatu ukończenia | 👨‍🏫 Trener |

### 📂 Moduły Szkoleniowe (10 modułów)

| # | Moduł | Folder | Czas | Poziom |
|---|-------|--------|------|--------|
| 1 | Hello World | `module_01_hello_world/` | 60 min | Podstawy |
| 2 | Custom Tool | `module_02_custom_tool/` | 75 min | Podstawy |
| 3 | Sequential Agent | `module_04_sequential_agent/` | 60 min | Średni |
| 4 | Parallel Agent | `module_07_parallel_agent/` | 60 min | Średni |
| 5 | Router Agent | `module_12_router_agent/` | 45 min | Średni |
| 6 | Human-in-Loop | `module_05_human_in_loop/` | 60 min | Zaawansowany |
| 7 | Loop Critique | `module_08_loop_critique/` | 45 min | Zaawansowany |
| 8 | Database | `module_09_database_simple/` | 75 min | Zaawansowany |
| 9 | Memory Bank | `module_11_memory_bank/` | 60 min | Zaawansowany |
| 10 | RAG Agent | `module_03_rag_agent/` | 60 min | Zaawansowany |

**Łączny czas:** 12 godzin (2 dni × 6h)

---

## 🎯 DLA KOGO JEST TO SZKOLENIE?

### Uczestnicy (Wymagania)
- **Poziom:** Średniozaawansowany Python
- **Doświadczenie:** Podstawy AI/ML (mile widziane, nie wymagane)
- **Setup:** Google Cloud Project, Python 3.10+, ADK zainstalowany

### Trenerzy (Wymagania)
- **Poziom:** Zaawansowany Python + ADK
- **Doświadczenie:** Min. 3 projekty z ADK
- **Umiejętności:** Prezentacja, live coding, troubleshooting

---

## 🚀 QUICK START DLA TRENERA

### 1 Tydzień Przed Szkoleniem

```bash
# 1. Sklonuj repozytorium
git clone https://github.com/your-org/adk-training
cd adk-training

# 2. Przetestuj wszystkie moduły
for module in module_*/; do
    cd "$module"
    adk web --port 8000
    # Testuj każdy moduł
    cd ..
done

# 3. Przygotuj Vertex AI (dla Module 11, 03)
python module_11_memory_bank/create_agent_engine.py
python module_03_rag_agent/setup_datastore.py

# 4. Wydrukuj materiały
# - Certyfikaty (1 na uczestnika)
# - Handbook PDF
# - Mapa Archipelagu (poster)
```

### Dzień Szkolenia

```bash
# 1. Sprawdź setup uczestników (9:00-9:15)
# 2. Rozpocznij prezentację (9:15)
# 3. Używaj PLAN_SZKOLENIA_NARRACJA.md jako przewodnika
# 4. Chodź między uczestnikami podczas praktyki
# 5. Wręcz certyfikaty (16:00-16:30)
```

---

## 📖 JAK UŻYWAĆ MATERIAŁÓW?

### Dla Trenera

1. **Przygotowanie:**
   - Przeczytaj `PRZEWODNIK_TRENERA.md` (30 min)
   - Przejrzyj `PLAN_SZKOLENIA_NARRACJA.md` (60 min)
   - Przetestuj wszystkie moduły (3h)

2. **Podczas szkolenia:**
   - Otwórz `PLAN_SZKOLENIA_NARRACJA.md` na drugim ekranie
   - Czytaj narrację (co mówić)
   - Trzymaj się timingu
   - Używaj `PRZEWODNIK_TRENERA.md` dla troubleshooting

3. **Po szkoleniu:**
   - Wypełnij certyfikaty
   - Wyślij feedback form
   - Zbierz uwagi do następnej edycji

### Dla Uczestników

1. **Przed szkoleniem:**
   - Zainstaluj wymagania (Python, ADK, GCP)
   - Przeczytaj `QUICK_REFERENCE.md`
   - Sklonuj repozytorium

2. **Podczas szkolenia:**
   - Używaj `QUICK_REFERENCE.md` jako ściągawki
   - Zobacz `MAPA_ARCHIPELAGU_ADK.md` dla kontekstu
   - Rób notatki w kodzie

3. **Po szkoleniu:**
   - Zachowaj `QUICK_REFERENCE.md` (przyda się!)
   - Zbuduj własny projekt
   - Dołącz do community

---

## 🎓 STRUKTURA SZKOLENIA

### Dzień 1: Fundamenty Piractwa (6h)
```
09:00-09:15  Wprowadzenie
09:15-10:15  Module 01: Hello World
10:15-10:30  Przerwa
10:30-11:45  Module 02: Custom Tool
11:45-12:00  Przerwa
12:00-13:00  Module 04: Sequential Agent
13:00-14:00  LUNCH
14:00-15:00  Module 07: Parallel Agent
15:00-15:15  Przerwa
15:15-16:00  Module 12: Router Agent
16:00-16:15  Podsumowanie Dnia 1
```

### Dzień 2: Zaawansowane Wyprawy (6h)
```
09:00-09:15  Powitanie + Recap
09:15-10:15  Module 05: Human-in-Loop
10:15-10:30  Przerwa
10:30-11:15  Module 08: Loop Critique
11:15-11:30  Przerwa
11:30-12:45  Module 09: Database
12:45-13:45  LUNCH
13:45-14:45  Module 11: Memory Bank
14:45-15:00  Przerwa
15:00-16:00  Module 03: RAG Agent
16:00-16:30  Podsumowanie + Certyfikaty
```

---

## 🛠️ WYMAGANIA TECHNICZNE

### Dla Uczestników

**Hardware:**
- Laptop (Windows/Mac/Linux)
- Min. 8GB RAM
- 10GB wolnego miejsca
- Stabilne WiFi

**Software:**
- Python 3.10+ (`python --version`)
- Google Cloud SDK (`gcloud --version`)
- Google ADK (`pip install google-adk`)
- Git (`git --version`)
- IDE (VS Code, PyCharm, etc.)

**Google Cloud:**
- Projekt GCP utworzony
- Billing włączony
- Vertex AI API włączony
- Quota sprawdzona

### Dla Trenera

**Dodatkowo:**
- Projektor + HDMI
- Mikrofon (jeśli sala >20 osób)
- Whiteboard + markery
- Drukarka (certyfikaty)
- Backup USB (kod + materiały)

---

## 📊 METRYKI SUKCESU

Po szkoleniu uczestnicy powinni umieć:

- [ ] Stworzyć podstawowego agenta (LlmAgent)
- [ ] Dodać narzędzia (FunctionTool)
- [ ] Orkiestrować wielu agentów (Sequential, Parallel, Router)
- [ ] Dodać zatwierdzenia (Human-in-Loop)
- [ ] Zapisywać dane (Database)
- [ ] Używać pamięci długoterminowej (Memory Bank)
- [ ] Integrować z dokumentami (RAG)
- [ ] Wdrożyć agenta na Cloud Run (bonus)

**Cel:** Min. 80% uczestników osiąga wszystkie punkty

---

## 🔗 LINKI I ZASOBY

### Dokumentacja
- [ADK Docs](https://google.github.io/adk-docs/)
- [Gemini API](https://ai.google.dev/gemini-api)
- [Vertex AI](https://cloud.google.com/vertex-ai)

### Community
- [GitHub](https://github.com/google/adk)
- [Discord](https://discord.gg/google-adk)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-adk)

### Przykłady
- [ADK Examples](https://github.com/google/adk/tree/main/examples)
- [Cookbook](https://github.com/google/adk-cookbook)

---

## 📝 FEEDBACK I KONTAKT

### Dla Uczestników
- Ankieta po szkoleniu: [link]
- Pytania: [email trenera]
- Community: [Discord/Slack]

### Dla Trenerów
- Zgłoś błędy: [GitHub Issues]
- Sugestie: [email organizatora]
- Udostępnij materiały: [link]

---

## 📜 LICENCJA

Materiały szkoleniowe są dostępne na licencji [MIT/Apache 2.0].

Możesz:
- ✅ Używać do szkoleń komercyjnych
- ✅ Modyfikować i dostosowywać
- ✅ Udostępniać innym

Musisz:
- ✅ Zachować informację o autorach
- ✅ Udostępnić zmiany (jeśli publikujesz)

---

## 🎉 PODZIĘKOWANIA

Dziękujemy:
- **Google** za stworzenie ADK
- **Społeczności ADK** za feedback
- **Trenerom** za prowadzenie szkoleń
- **Uczestnikom** za udział i zaangażowanie

---

## 🏴‍☠️ AHOJ, KAPITANIE!

Gotowy na podróż przez Archipelag ADK?

**Powodzenia!** ⚓

---

*Ostatnia aktualizacja: 2024-01-15*  
*Wersja: 1.0*  
*Autorzy: [Twoje Imię]*

