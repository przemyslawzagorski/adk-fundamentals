# 🏴‍☠️ PLAN PREZENTACJI SZKOLENIA GOOGLE ADK
## *"Od Rekruta do Kapitana: Podróż przez Archipelag ADK"*

---

## 📋 SPIS TREŚCI
1. [Wprowadzenie do Szkolenia](#wprowadzenie)
2. [Dzień 1: Fundamenty Piractwa](#dzień-1)
3. [Dzień 2: Zaawansowane Wyprawy](#dzień-2)
4. [Zakończenie i Certyfikaty](#zakończenie)

---

# 🎬 WPROWADZENIE DO SZKOLENIA (09:00 - 09:15)

## Slajd 1: Powitanie
**Co mówić:**
> "Dzień dobry! Witam Was na pokładzie naszego szkolenia z Google ADK. Przez najbliższe 2 dni będziemy razem odkrywać archipelag technologii agentów AI. Nazywam się [Imię] i będę Waszym kapitanem w tej podróży."

**Akcja:** Przedstaw się, poproś uczestników o krótkie przedstawienie się (imię, doświadczenie z AI)

---

## Slajd 2: Metafora Piracka
**Co mówić:**
> "Dlaczego piraci? Bo budowanie agentów AI to jak dowodzenie pirackim statkiem:
> - **Kapitan** = Ty (developer)
> - **Załoga** = Twoi agenci AI
> - **Skarby** = Dane i wyniki
> - **Wyprawy** = Projekty AI
> 
> Każdy agent ma swoją rolę: Quartermaster zarządza skarbami, Navigator planuje trasy, Zwiadowcy zbierają informacje. Dokładnie jak w prawdziwym zespole!"

**Akcja:** Pokaż diagram statku z różnymi rolami

---

## Slajd 3: Czym jest Google ADK?
**Co mówić:**
> "ADK to Agent Development Kit - framework od Google do budowania agentów AI. To nie jest chatbot. To inteligentny system który:
> - Używa narzędzi (tools)
> - Współpracuje z innymi agentami
> - Pamięta kontekst
> - Podejmuje decyzje
> 
> Dzisiaj zbudujemy 10 różnych agentów - od prostego 'Hello World' do zaawansowanych systemów z pamięcią i bazami danych."

**Akcja:** Pokaż przykład działającego agenta (live demo - 2 minuty)

---

## Slajd 4: Plan Szkolenia
**Co mówić:**
> "Nasza mapa wyprawy wygląda tak:
> 
> **DZIEŃ 1 - Fundamenty:**
> 1. Hello World - pierwszy agent
> 2. Custom Tools - narzędzia
> 3. Sequential Agent - pipeline
> 4. Parallel Agent - równoległość
> 5. Router Agent - routing
> 
> **DZIEŃ 2 - Zaawansowane:**
> 6. Human-in-Loop - zatwierdzenia
> 7. Loop Critique - iteracje
> 8. Database - persistence
> 9. Memory Bank - pamięć długoterminowa
> 10. RAG Agent - wyszukiwanie w dokumentach
> 
> Każdy moduł to 45-75 minut: teoria (15 min) + praktyka (30-60 min)."

**Akcja:** Pokaż mapę archipelagu z wyspami (każda wyspa = moduł)

---

## Slajd 5: Wymagania Techniczne
**Co mówić:**
> "Zanim wypłyniemy, sprawdźmy czy wszyscy mają:
> - ✅ Python 3.10+
> - ✅ Google Cloud Project
> - ✅ ADK zainstalowany (`pip install google-adk`)
> - ✅ Plik `.env` skonfigurowany
> 
> Jeśli ktoś ma problem - dajcie znać TERAZ, pomożemy."

**Akcja:** Quick check - poproś o podniesienie ręki kto ma wszystko gotowe

---

# 📚 DZIEŃ 1: FUNDAMENTY PIRACTWA

---

# 1️⃣ MODULE 01: HELLO WORLD (09:15 - 10:15, 60 min)

## Slajd 6: Kapitan Blackbeard - Pierwszy Agent
**Co mówić:**
> "Zaczynamy od podstaw. Nasz pierwszy agent to Kapitan Blackbeard - prosty asystent kapitana. To 'Hello World' świata ADK."

---

## TEORIA (15 min)

### Slajd 7: Czym jest LlmAgent?
**Co mówić:**
> "LlmAgent to podstawowy building block ADK. To wrapper wokół modelu LLM (np. Gemini) który:
> - Zarządza konwersacją
> - Śledzi kontekst
> - Może używać narzędzi
> 
> Minimalna konfiguracja to 3 parametry:
> ```python
> agent = LlmAgent(
>     name='kapitan_blackbeard',      # Identyfikator
>     model='gemini-2.5-flash',       # Model LLM
>     instruction='Jesteś kapitanem...' # System prompt
> )
> ```"

**Akcja:** Pokaż kod na ekranie, wyjaśnij każdy parametr

---

### Slajd 8: System Prompt - Najważniejszy Parametr
**Co mówić:**
> "Instruction to system prompt - najważniejszy parametr! To instrukcje dla agenta:
> - Kim jest? (rola)
> - Co robi? (zadania)
> - Jak się zachowuje? (ton, styl)
> 
> Przykład dla Kapitana:
> ```
> Jesteś Kapitanem Blackbeardem, dowódcą galeonu 'Czarna Perła'.
> 
> Twoje zadania:
> - Witaj załogę na pokładzie
> - Odpowiadaj na pytania o życie pirata
> - Opowiadaj historie z morza
> 
> Mów jak prawdziwy pirat: 'Ahoj!', 'Arrr!', 'Shiver me timbers!'
> ```
> 
> Im lepszy prompt, tym lepszy agent!"

**Akcja:** Pokaż przykłady dobrego vs złego promptu

---

### Slajd 9: Wybór Modelu
**Co mówić:**
> "Google oferuje różne modele Gemini:
> - **gemini-2.5-flash** - szybki, tani, dobry na start (POLECAM)
> - **gemini-2.5-pro** - wolniejszy, droższy, bardziej inteligentny
> - **gemini-2.0-flash-exp** - eksperymentalny
> 
> Dla nauki: używajmy Flash. Dla produkcji: testuj oba i wybierz."

---

## PRAKTYKA (45 min)

### Slajd 10: Hands-On - Stwórz Kapitana
**Co mówić:**
> "Teraz Wy! Otwórzcie `adk_training/module_01_hello_world/agent.py`
> 
> **Zadanie 1 (10 min):**
> 1. Przeczytaj kod
> 2. Zmodyfikuj instruction - dodaj własny styl
> 3. Uruchom: `adk web`
> 4. Testuj w przeglądarce
> 
> **Pytania testowe:**
> - 'Ahoj! Kim jesteś?'
> - 'Opowiedz historię o skarbie'
> - 'Jakie są zasady na statku?'
> 
> Macie 10 minut - START!"

**Akcja:** Chodź między uczestnikami, pomagaj, odpowiadaj na pytania

---

### Slajd 11: Demo - Pokaż Swoje Rozwiązania
**Co mówić (po 10 min):**
> "Kto chce pokazać swojego kapitana? [wybierz 2-3 osoby]
> 
> Świetnie! Widzicie jak różne mogą być agenci przy tej samej bazie kodu? To moc system promptu!"

**Akcja:** Poproś ochotników o pokazanie ich agentów (screen sharing)

---

### Slajd 12: Ćwiczenie 1.1 - Zmień Rolę
**Co mówić:**
> "**Ćwiczenie 1.1 (15 min):**
> Zmień agenta z Kapitana na:
> - **Quartermaster** (zarządca skarbów)
> - **Navigator** (nawigator)
> - **Cook** (kucharz)
> 
> Zmień: name, instruction, description
> 
> Wskazówka: Quartermaster mówi o skarbch, Navigator o trasach, Cook o jedzeniu.
> 
> Macie 15 minut!"

---

### Slajd 13: Ćwiczenie 1.2 - Temperatura i Parametry
**Co mówić:**
> "**Ćwiczenie 1.2 (10 min):**
> Dodaj konfigurację modelu:
> ```python
> agent = LlmAgent(
>     ...,
>     generate_content_config=types.GenerateContentConfig(
>         temperature=0.9  # 0.0 = deterministyczny, 1.0 = kreatywny
>     )
> )
> ```
> 
> Przetestuj z temperature=0.1 i temperature=0.9. Jaka różnica?"

---

### Slajd 14: Podsumowanie Module 01
**Co mówić:**
> "Gratulacje! Stworzyliście pierwszego agenta! 🎉
> 
> **Czego się nauczyliście:**
> - ✅ LlmAgent to podstawa ADK
> - ✅ System prompt (instruction) to klucz
> - ✅ Model selection ma znaczenie
> - ✅ `adk web` uruchamia agenta
> 
> **Następny krok:** Dodamy narzędzia (tools) - Quartermaster będzie zarządzał prawdziwym skarbcem!"

---

## ☕ PRZERWA (10:15 - 10:30, 15 min)

---

# 2️⃣ MODULE 02: CUSTOM TOOL (10:30 - 11:45, 75 min)

## Slajd 15: Quartermaster - Agent z Narzędziami
**Co mówić:**
> "Witamy z powrotem! Teraz robimy krok dalej. Nasz Quartermaster będzie zarządzał PRAWDZIWYM skarbcem - nie tylko gadał o nim, ale faktycznie sprawdzał stan, dodawał łupy, liczył wartość.
> 
> To wprowadza najważniejszą koncepcję ADK: **Tools** (narzędzia)."

---

## TEORIA (20 min)

### Slajd 16: Czym są Tools?
**Co mówić:**
> "Tools to funkcje Python które agent może wywoływać. To jak dać agentowi ręce:
> - Bez tools: agent tylko MÓWI
> - Z tools: agent DZIAŁA
> 
> Przykłady:
> - `sprawdz_skarb()` - sprawdza ile mamy złota
> - `dodaj_lup()` - dodaje zdobycz do skarbca
> - `wyslij_email()` - wysyła email
> - `zapisz_do_bazy()` - zapisuje dane
> 
> Agent SAM decyduje kiedy użyć narzędzia!"

---

### Slajd 17: Wymagania dla Tools
**Co mówić:**
> "Każde narzędzie MUSI mieć:
> 
> **1. Type hints** (adnotacje typów):
> ```python
> def sprawdz_skarb(nazwa: str) -> str:  # ← MUSI być!
> ```
> 
> **2. Docstring** (dokumentacja):
> ```python
> def sprawdz_skarb(nazwa: str) -> str:
>     '''Sprawdza ile mamy danego skarbu.
>     
>     Args:
>         nazwa: Nazwa skarbu (np. 'zlote_dublony')
>     '''
> ```
> 
> **3. Jasne nazwy** parametrów i funkcji
> 
> Dlaczego? Agent CZYTA docstring aby zrozumieć co robi narzędzie!"

**Akcja:** Pokaż przykład dobrego vs złego narzędzia

---

### Slajd 18: Jak Agent Używa Tools?
**Co mówić:**
> "Flow wygląda tak:
> 
> ```
> 1. User: 'Ile mamy złotych dublonów?'
>    ↓
> 2. Agent: Analizuje pytanie
>    ↓
> 3. Agent: 'Potrzebuję sprawdzić skarbiec'
>    ↓
> 4. Agent: Wywołuje sprawdz_skarb('zlote_dublony')
>    ↓
> 5. Tool: Zwraca '1500 sztuk'
>    ↓
> 6. Agent: 'Mamy 1500 złotych dublonów w skarbcu!'
> ```
> 
> Agent SAM decyduje czy użyć tool, który tool, i z jakimi parametrami!"

---

### Slajd 19: Przekazywanie Tools do Agenta
**Co mówić:**
> "Dodajemy tools przez parametr `tools=[]`:
> 
> ```python
> quartermaster = LlmAgent(
>     name='quartermaster',
>     instruction='Zarządzaj skarbami...',
>     tools=[sprawdz_skarb, dodaj_lup, oblicz_wartosc]  # Lista funkcji
> )
> ```
> 
> Tyle! ADK automatycznie:
> - Czyta docstringi
> - Generuje opisy dla modelu
> - Obsługuje wywołania
> - Zwraca wyniki"

---

## PRAKTYKA (55 min)

### Slajd 20: Hands-On - Quartermaster
**Co mówić:**
> "Otwórzcie `adk_training/module_02_custom_tool/agent.py`
> 
> **Zadanie 2.1 (15 min):**
> 1. Przeczytaj kod - zobacz jak działają tools
> 2. Uruchom: `adk web`
> 3. Testuj:
>    - 'Ile mamy złotych dublonów?'
>    - 'Dodaj 100 rubinów'
>    - 'Pokaż wszystkie skarby'
>    - 'Oblicz wartość skarbca'
> 
> Obserwuj jak agent UŻYWA narzędzi!"

**Akcja:** Chodź, pomagaj, pokazuj jak agent wywołuje tools

---

### Slajd 21: Ćwiczenie 2.1 - Dodaj Nowe Narzędzie
**Co mówić:**
> "**Ćwiczenie 2.1 (20 min):**
> Dodaj narzędzie `usun_skarb(nazwa: str, ilosc: int)`:
> 
> ```python
> def usun_skarb(nazwa: str, ilosc: int) -> str:
>     '''Usuwa skarb ze skarbca (np. wydatek, strata).
>     
>     Args:
>         nazwa: Nazwa skarbu
>         ilosc: Ile usunąć
>     '''
>     # TODO: Twoja implementacja
> ```
> 
> Wskazówki:
> - Sprawdź czy skarb istnieje
> - Sprawdź czy mamy wystarczająco
> - Odejmij od SKARBY[nazwa]
> - Zwróć komunikat
> 
> Dodaj do `tools=[...]` i przetestuj!"

---

### Slajd 22: Ćwiczenie 2.2 - Walidacja
**Co mówić:**
> "**Ćwiczenie 2.2 (10 min):**
> Dodaj walidację do `dodaj_lup()`:
> - Nie pozwól na ujemne ilości
> - Nie pozwól na puste nazwy
> - Ogranicz max ilość (np. 10000)
> 
> Przetestuj:
> - 'Dodaj -50 dublonów' → błąd
> - 'Dodaj 999999 rubinów' → błąd"

---

### Slajd 23: Demo - Wieloetapowe Użycie
**Co mówić:**
> "Teraz magia! Zapytajcie agenta:
> 
> **'Dodaj 100 złotych dublonów, potem dodaj 50 rubinów, a na koniec oblicz całkowitą wartość skarbca.'**
> 
> Obserwujcie - agent użyje 3 narzędzi PO KOLEI! To pokazuje moc ADK."

**Akcja:** Live demo - pokaż jak agent chain-uje tools

---

### Slajd 24: Podsumowanie Module 02
**Co mówić:**
> "Brawo! Teraz Wasze agenty DZIAŁAJĄ, nie tylko gadają! 🛠️
> 
> **Czego się nauczyliście:**
> - ✅ Tools to funkcje Python
> - ✅ Docstring + type hints = MUST
> - ✅ Agent SAM decyduje kiedy użyć tool
> - ✅ Agent może chain-ować wiele tools
> 
> **Następny krok:** Wiele agentów współpracujących - Sequential Agent!"

---

## ☕ PRZERWA (11:45 - 12:00, 15 min)

---

# 3️⃣ MODULE 04: SEQUENTIAL AGENT (12:00 - 13:00, 60 min)

## Slajd 25: Rada Wojenna - Pipeline Agentów
**Co mówić:**
> "Do tej pory: 1 agent. Teraz: 3 agenci współpracujący!
> 
> **Scenariusz:** Rada Wojenna planuje atak:
> 1. **Zwiadowca** zbiera wywiad
> 2. **Strateg** planuje atak (używa wywiadu)
> 3. **Kapitan** podejmuje decyzję (używa wywiadu + planu)
> 
> To **SequentialAgent** - orkiestrator który uruchamia agentów PO KOLEI."

---

## TEORIA (15 min)

### Slajd 26: Czym jest SequentialAgent?
**Co mówić:**
> "SequentialAgent to workflow agent który:
> - Uruchamia sub-agentów po kolei
> - Przekazuje dane między nimi przez **state** (stan sesji)
> - Każdy agent widzi wyniki poprzednich
> 
> ```python
> pipeline = SequentialAgent(
>     name='rada_wojenna',
>     sub_agents=[zwiadowca, strateg, kapitan]  # Kolejność ma znaczenie!
> )
> ```"

---

### Slajd 27: Output Key - Zapisywanie Wyników
**Co mówić:**
> "Jak przekazać dane między agentami? **output_key**!
> 
> ```python
> zwiadowca = LlmAgent(
>     name='zwiadowca',
>     instruction='Zbierz wywiad...',
>     output_key='raport_wywiadu'  # ← Zapisz wynik do state
> )
> ```
> 
> Wynik zwiadowcy jest zapisywany w state jako `raport_wywiadu`."

---

### Slajd 28: Dostęp do State - Odczytywanie Wyników
**Co mówić:**
> "Jak odczytać? Użyj `{key_name}` w instruction:
> 
> ```python
> strateg = LlmAgent(
>     name='strateg',
>     instruction='''Na podstawie wywiadu: {raport_wywiadu}
>     
>     Zaplanuj atak...''',
>     output_key='plan_bitwy'
> )
> ```
> 
> ADK automatycznie podmienia `{raport_wywiadu}` na faktyczny wynik!"

---

## PRAKTYKA (45 min)

### Slajd 29: Hands-On - Rada Wojenna
**Co mówić:**
> "Otwórzcie `adk_training/module_04_sequential_agent/agent.py`
> 
> **Zadanie 4.1 (15 min):**
> 1. Przeczytaj kod - 3 agentów + SequentialAgent
> 2. Uruchom: `adk web`
> 3. Testuj: 'Zaplanuj atak na Fort Royal'
> 4. Obserwuj jak agenci działają PO KOLEI
> 
> Zwróć uwagę:
> - Zwiadowca odpowiada pierwszy
> - Strateg używa raportu zwiadowcy
> - Kapitan używa obu"

---

### Slajd 30: Ćwiczenie 4.1 - Dodaj 4. Agenta
**Co mówić:**
> "**Ćwiczenie 4.1 (20 min):**
> Dodaj 4. agenta: **Logistyk**
> 
> ```python
> logistyk = LlmAgent(
>     name='logistyk',
>     instruction='''Na podstawie planu: {plan_bitwy}
>     
>     Przygotuj listę potrzebnych zasobów:
>     - Amunicja
>     - Prowiant
>     - Ludzie
>     ''',
>     output_key='lista_zasobow'
> )
> ```
> 
> Dodaj do pipeline: `[zwiadowca, strateg, logistyk, kapitan]`"

---

### Slajd 31: Ćwiczenie 4.2 - Conditional Logic
**Co mówić:**
> "**Ćwiczenie 4.2 (10 min):**
> Zmodyfikuj Kapitana aby podejmował decyzję:
> - Jeśli ryzyko wysokie → WYCOFANIE
> - Jeśli ryzyko niskie → ATAK
> 
> Wskazówka: Dodaj do instruction:
> ```
> Oceń ryzyko na podstawie {raport_wywiadu}.
> Jeśli ryzyko > 70% → WYCOFANIE
> Jeśli ryzyko < 30% → ATAK
> Inaczej → CZEKAJ
> ```"

---

### Slajd 32: Podsumowanie Module 04
**Co mówić:**
> "Świetnie! Teraz macie pipeline agentów! 🔄
> 
> **Czego się nauczyliście:**
> - ✅ SequentialAgent orkiestruje sub-agentów
> - ✅ output_key zapisuje wyniki do state
> - ✅ {key_name} odczytuje ze state
> - ✅ Każdy agent buduje na poprzednich
> 
> **Następny krok:** Parallel Agent - agenci działający RÓWNOCZEŚNIE!"

---

## 🍽️ LUNCH (13:00 - 14:00, 60 min)

---

# 4️⃣ MODULE 07: PARALLEL AGENT (14:00 - 15:00, 60 min)

## Slajd 33: Flota Zwiadowców - Równoległość
**Co mówić:**
> "Po lunchu - nowa koncepcja! Sequential = po kolei. Parallel = RÓWNOCZEŚNIE!
> 
> **Scenariusz:** 3 zwiadowców badają 3 wyspy jednocześnie:
> - Zwiadowca Północ → Wyspa Północna
> - Zwiadowca Wschód → Wyspa Wschodnia  
> - Zwiadowca Południe → Wyspa Południowa
> 
> Wszyscy startują w tym samym momencie!"

---

## TEORIA (15 min)

### Slajd 34: Sequential vs Parallel
**Co mówić:**
> "Różnica:
> 
> **Sequential:**
> ```
> Agent 1 → (czeka) → Agent 2 → (czeka) → Agent 3
> Czas: 30s + 30s + 30s = 90s
> ```
> 
> **Parallel:**
> ```
> Agent 1 ↘
> Agent 2 → (wszyscy równocześnie)
> Agent 3 ↗
> Czas: max(30s, 30s, 30s) = 30s
> ```
> 
> 3x szybciej!"

---

### Slajd 35: Kiedy Używać Parallel?
**Co mówić:**
> "Używaj Parallel gdy:
> - ✅ Zadania są NIEZALEŻNE (nie potrzebują wyników innych)
> - ✅ Chcesz PRZYSPIESZYĆ (równoległe wykonanie)
> - ✅ Zbierasz dane z wielu źródeł
> 
> NIE używaj gdy:
> - ❌ Agent B potrzebuje wyniku Agenta A (użyj Sequential)
> - ❌ Kolejność ma znaczenie"

---

## PRAKTYKA (45 min)

### Slajd 36: Hands-On - Flota Zwiadowców
**Co mówić:**
> "Otwórzcie `adk_training/module_07_parallel_agent/agent.py`
> 
> **Zadanie 7.1 (15 min):**
> 1. Przeczytaj kod - 3 zwiadowców + ParallelAgent
> 2. Uruchom: `adk web`
> 3. Testuj: 'Zbadaj archipelag'
> 4. Obserwuj - wszyscy zwiadowcy odpowiadają JEDNOCZEŚNIE!
> 
> Porównaj czas z Sequential!"

---

### Slajd 37: Ćwiczenie 7.1 - Dodaj 4. Zwiadowcę
**Co mówić:**
> "**Ćwiczenie 7.1 (15 min):**
> Dodaj Zwiadowcę Zachód:
> 
> ```python
> zwiadowca_zachod = LlmAgent(
>     name='zwiadowca_zachod',
>     instruction='Zbadaj zachodnią wyspę...',
>     output_key='raport_zachod'
> )
> ```
> 
> Dodaj do ParallelAgent. Teraz 4 zwiadowców równocześnie!"

---

### Slajd 38: Ćwiczenie 7.2 - Agregator Raportów
**Co mówić:**
> "**Ćwiczenie 7.2 (15 min):**
> Dodaj agenta który agreguje wszystkie raporty:
> 
> ```python
> agregator = LlmAgent(
>     name='agregator',
>     instruction='''Podsumuj raporty:
>     
>     Północ: {raport_polnoc}
>     Wschód: {raport_wschod}
>     Południe: {raport_poludnie}
>     Zachód: {raport_zachod}
>     
>     Która wyspa jest najbardziej obiecująca?
>     '''
> )
> ```
> 
> Użyj SequentialAgent: `[parallel_scouts, agregator]`"

---

### Slajd 39: Podsumowanie Module 07
**Co mówić:**
> "Doskonale! Teraz macie równoległe wykonanie! ⚡
> 
> **Czego się nauczyliście:**
> - ✅ ParallelAgent uruchamia sub-agentów równocześnie
> - ✅ 3x szybciej niż Sequential (dla 3 agentów)
> - ✅ Używaj gdy zadania są niezależne
> - ✅ Można łączyć: Parallel + Sequential
> 
> **Następny krok:** Router Agent - inteligentny routing!"

---

## ☕ PRZERWA (15:00 - 15:15, 15 min)

---

# 5️⃣ MODULE 12: ROUTER AGENT (15:15 - 16:00, 45 min)

## Slajd 40: Admirał i Eksperci - Intelligent Routing
**Co mówić:**
> "Ostatni moduł Dnia 1! Router Agent to inteligentny dispatcher:
> 
> **Scenariusz:** Admirał kieruje pytania do ekspertów:
> - Pytanie o trasę → Navigator
> - Pytanie o działa → Gunner
> - Pytanie o jedzenie → Cook
> 
> Agent SAM wybiera odpowiedniego eksperta!"

---

## TEORIA (10 min)

### Slajd 41: Sequential vs Parallel vs Router
**Co mówić:**
> "Porównanie:
> 
> | Typ | Wykonanie | Use Case |
> |-----|-----------|----------|
> | Sequential | Wszyscy po kolei | Pipeline, workflow |
> | Parallel | Wszyscy równocześnie | Niezależne zadania |
> | **Router** | **Jeden wybrany** | **Specjalizacja** |
> 
> Router = tylko 1 agent odpowiada (ten najbardziej pasujący)!"

---

### Slajd 42: Jak Działa Routing?
**Co mówić:**
> "Router używa **description** sub-agentów:
> 
> ```python
> navigator = LlmAgent(
>     description='Ekspert od nawigacji, map, tras morskich'  # ← To czyta Router!
> )
> 
> gunner = LlmAgent(
>     description='Ekspert od dział, amunicji, taktyki bojowej'
> )
> 
> router = RouterAgent(
>     sub_agents=[navigator, gunner, cook]
> )
> ```
> 
> User: 'Jaka trasa do Tortuga?' → Router wybiera Navigator (bo description pasuje)"

---

## PRAKTYKA (35 min)

### Slajd 43: Hands-On - Admirał
**Co mówić:**
> "Otwórzcie `adk_training/module_12_router_agent/agent.py`
> 
> **Zadanie 12.1 (10 min):**
> 1. Przeczytaj kod - 3 ekspertów + RouterAgent
> 2. Uruchom: `adk web`
> 3. Testuj różne pytania:
>    - 'Jaka trasa do Karaibow?' → Navigator
>    - 'Ile mamy amunicji?' → Gunner
>    - 'Co na obiad?' → Cook
> 
> Obserwuj który ekspert odpowiada!"

---

### Slajd 44: Ćwiczenie 12.1 - Dodaj Eksperta
**Co mówić:**
> "**Ćwiczenie 12.1 (15 min):**
> Dodaj 4. eksperta: **Doktor** (medyk)
> 
> ```python
> doktor = LlmAgent(
>     name='doktor',
>     description='Ekspert od medycyny, ran, chorób, zdrowia załogi',
>     instruction='Jesteś doktorem okrętowym...'
> )
> ```
> 
> Dodaj do router. Testuj: 'Ktoś ma gorączkę, co robić?'"

---

### Slajd 45: Ćwiczenie 12.2 - Fallback Agent
**Co mówić:**
> "**Ćwiczenie 12.2 (10 min):**
> Co jeśli pytanie nie pasuje do żadnego eksperta?
> 
> Dodaj General Agent jako fallback:
> 
> ```python
> general = LlmAgent(
>     description='Ekspert ogólny - odpowiada gdy pytanie nie pasuje do specjalizacji'
> )
> 
> router = RouterAgent(
>     sub_agents=[navigator, gunner, cook, doktor, general]  # General na końcu!
> )
> ```"

---

### Slajd 46: Podsumowanie Module 12
**Co mówić:**
> "Brawo! Koniec Dnia 1! 🎉
> 
> **Czego się nauczyliście:**
> - ✅ RouterAgent wybiera jednego sub-agenta
> - ✅ Routing bazuje na description
> - ✅ Używaj dla specjalizacji/ekspertów
> - ✅ Dodaj fallback dla edge cases
> 
> **Jutro:** Zaawansowane techniki - callbacks, loops, databases, memory!"

---

## 📝 PODSUMOWANIE DNIA 1 (16:00 - 16:15, 15 min)

### Slajd 47: Recap Dnia 1
**Co mówić:**
> "Podsumujmy co zrobiliśmy:
> 
> 1. ✅ **Hello World** - pierwszy agent (Kapitan)
> 2. ✅ **Custom Tools** - narzędzia (Quartermaster)
> 3. ✅ **Sequential** - pipeline (Rada Wojenna)
> 4. ✅ **Parallel** - równoległość (Flota Zwiadowców)
> 5. ✅ **Router** - routing (Admirał)
> 
> Od rekruta do quartermastera! Jutro: od quartermastera do admirała!"

---

### Slajd 48: Q&A + Zadanie Domowe
**Co mówić:**
> "Pytania? [5 min Q&A]
> 
> **Zadanie domowe (opcjonalne):**
> Połącz wszystkie dzisiejsze moduły w jeden system:
> - Router kieruje do Sequential
> - Sequential używa Parallel
> - Wszystko z Custom Tools
> 
> Jutro pokażcie co stworzyliście!
> 
> Do zobaczenia jutro o 9:00! ⚓"

---

# 🌅 DZIEŃ 2: ZAAWANSOWANE WYPRAWY

---

# 🎬 POWITANIE DZIEŃ 2 (09:00 - 09:15, 15 min)

## Slajd 49: Witamy z Powrotem!
**Co mówić:**
> "Dzień dobry! Witamy w Dniu 2! Wczoraj nauczyliście się podstaw - dziś zaawansowane techniki.
>
> **Szybki recap Dnia 1:**
> - LlmAgent (Hello World)
> - Tools (Quartermaster)
> - Sequential (Rada Wojenna)
> - Parallel (Flota Zwiadowców)
> - Router (Admirał)
>
> Kto zrobił zadanie domowe? [pokaż 1-2 rozwiązania]"

---

## Slajd 50: Plan Dnia 2
**Co mówić:**
> "Dziś 5 zaawansowanych modułów:
>
> 6. **Human-in-Loop** - zatwierdzenia przez człowieka
> 7. **Loop Critique** - iteracyjne doskonalenie
> 8. **Database** - persistence i SQL
> 9. **Memory Bank** - pamięć długoterminowa
> 10. **RAG Agent** - wyszukiwanie w dokumentach
>
> Od quartermastera do admirała! 🏴‍☠️"

---

# 6️⃣ MODULE 05: HUMAN-IN-LOOP (09:15 - 10:15, 60 min)

## Slajd 51: Skarbnik - Zatwierdzenia Kapitana
**Co mówić:**
> "Nowy temat: **Human-in-the-Loop**. Agent pyta człowieka o zgodę przed akcją.
>
> **Scenariusz:** Skarbnik zarządza finansami, ale duże wydatki (>100 dublonów) wymagają zgody Kapitana.
>
> To kluczowe dla produkcji - nie chcesz aby agent robił wszystko automatycznie!"

---

## TEORIA (15 min)

### Slajd 52: Czym jest Human-in-Loop?
**Co mówić:**
> "Human-in-Loop = agent pyta człowieka przed wykonaniem akcji.
>
> **Przykłady:**
> - Wydaj 1000 zł → pytaj o zgodę
> - Wyślij email do CEO → pytaj o zgodę
> - Usuń dane → pytaj o zgodę
>
> W ADK: `require_confirmation=True`"

---

### Slajd 53: FunctionTool z Confirmation
**Co mówić:**
> "Implementacja:
>
> ```python
> from google.adk.tools import FunctionTool
>
> def wydaj_zloto(kwota: int, cel: str) -> str:
>     '''Wydaje złoto ze skarbca.'''
>     return f'Wydano {kwota} dublonów na {cel}'
>
> skarbnik = LlmAgent(
>     tools=[
>         FunctionTool(wydaj_zloto, require_confirmation=True)  # ← Wymaga zgody!
>     ]
> )
> ```
>
> Gdy agent chce użyć tool → UI pokazuje prompt → user klika TAK/NIE"

---

### Slajd 54: Callbacks - Zaawansowane
**Co mówić:**
> "Alternatywa: własne callbacks:
>
> ```python
> async def before_tool_callback(context):
>     if context.tool_name == 'wydaj_zloto':
>         kwota = context.parameters['kwota']
>         if kwota > 100:
>             # Pytaj użytkownika
>             return await ask_user_approval(context)
>
> agent = LlmAgent(
>     before_tool_callback=before_tool_callback
> )
> ```
>
> Więcej kontroli, ale bardziej skomplikowane."

---

## PRAKTYKA (45 min)

### Slajd 55: Hands-On - Skarbnik
**Co mówić:**
> "Otwórzcie `adk_training/module_05_human_in_loop/agent.py`
>
> **Zadanie 5.1 (15 min):**
> 1. Przeczytaj kod - FunctionTool z require_confirmation
> 2. Uruchom: `adk web`
> 3. Testuj:
>    - 'Wydaj 50 dublonów na prowiant' → automatycznie
>    - 'Wydaj 500 dublonów na nowy statek' → pytaj o zgodę
>
> Kliknij APPROVE lub REJECT w UI!"

---

### Slajd 56: Ćwiczenie 5.1 - Conditional Confirmation
**Co mówić:**
> "**Ćwiczenie 5.1 (20 min):**
> Zmodyfikuj aby confirmation zależał od kwoty:
>
> ```python
> def wydaj_zloto(kwota: int, cel: str) -> str:
>     if kwota > 100:
>         # Wymaga confirmation (jak?)
>         pass
>     else:
>         # Automatycznie
>         return f'Wydano {kwota}'
> ```
>
> Wskazówka: Użyj dwóch funkcji lub callback"

---

### Slajd 57: Ćwiczenie 5.2 - Approval Log
**Co mówić:**
> "**Ćwiczenie 5.2 (10 min):**
> Zapisuj wszystkie zatwierdzenia do logu:
>
> ```python
> APPROVAL_LOG = []
>
> async def after_approval_callback(context):
>     APPROVAL_LOG.append({
>         'action': context.tool_name,
>         'approved': context.approved,
>         'timestamp': datetime.now()
>     })
> ```
>
> Dodaj tool `pokaz_log()` aby wyświetlić historię"

---

### Slajd 58: Podsumowanie Module 05
**Co mówić:**
> "Świetnie! Teraz agenci pytają o zgodę! ✋
>
> **Czego się nauczyliście:**
> - ✅ Human-in-Loop = bezpieczeństwo
> - ✅ FunctionTool(require_confirmation=True)
> - ✅ Callbacks dla zaawansowanej logiki
> - ✅ Approval log dla audytu
>
> **Następny krok:** Loop Critique - iteracyjne doskonalenie!"

---

## ☕ PRZERWA (10:15 - 10:30, 15 min)

---

# 7️⃣ MODULE 08: LOOP CRITIQUE (10:30 - 11:15, 45 min)

## Slajd 59: Kartograf - Doskonalenie Mapy
**Co mówić:**
> "Nowa koncepcja: **LoopAgent** - iteracyjne doskonalenie.
>
> **Scenariusz:** Kartograf rysuje mapę, Krytyk ocenia, Kartograf poprawia... aż mapa jest idealna.
>
> To wzorzec 'critique and refine' - bardzo potężny!"

---

## TEORIA (10 min)

### Slajd 60: Czym jest LoopAgent?
**Co mówić:**
> "LoopAgent uruchamia sub-agentów w pętli:
>
> ```
> Iteracja 1: Kartograf → Krytyk → 'Brakuje skali'
> Iteracja 2: Kartograf (poprawia) → Krytyk → 'Brakuje legendy'
> Iteracja 3: Kartograf (poprawia) → Krytyk → 'OK!'
> STOP
> ```
>
> ```python
> loop = LoopAgent(
>     sub_agents=[kartograf, krytyk],
>     max_iterations=5  # Max 5 iteracji
> )
> ```"

---

### Slajd 61: Kiedy Używać Loop?
**Co mówić:**
> "Używaj Loop gdy:
> - ✅ Potrzebujesz iteracyjnego doskonalenia
> - ✅ Masz agenta 'twórcy' i agenta 'krytyka'
> - ✅ Jakość rośnie z iteracjami
>
> Przykłady:
> - Pisanie kodu → code review → poprawki
> - Generowanie tekstu → edycja → finalizacja
> - Projektowanie → feedback → redesign"

---

## PRAKTYKA (35 min)

### Slajd 62: Hands-On - Kartograf
**Co mówić:**
> "Otwórzcie `adk_training/module_08_loop_critique/agent.py`
>
> **Zadanie 8.1 (10 min):**
> 1. Przeczytaj kod - Kartograf + Krytyk + LoopAgent
> 2. Uruchom: `adk web`
> 3. Testuj: 'Narysuj mapę do Wyspy Skarbów'
> 4. Obserwuj iteracje - mapa się poprawia!
>
> Ile iteracji zajęło?"

---

### Slajd 63: Ćwiczenie 8.1 - Zmień Kryteria
**Co mówić:**
> "**Ćwiczenie 8.1 (15 min):**
> Zmodyfikuj Krytyka aby sprawdzał:
> - ✅ Współrzędne GPS
> - ✅ Punkty orientacyjne
> - ✅ Skala
> - ✅ Legenda
> - ✅ Róża wiatrów
>
> Jeśli wszystko OK → zatwierdź
> Jeśli brakuje → poproś o poprawki"

---

### Slajd 64: Ćwiczenie 8.2 - Quality Score
**Co mówić:**
> "**Ćwiczenie 8.2 (10 min):**
> Dodaj scoring system:
>
> ```python
> krytyk = LlmAgent(
>     instruction='''Oceń mapę w skali 1-10:
>
>     - Współrzędne: +2 pkt
>     - Punkty orientacyjne: +2 pkt
>     - Skala: +2 pkt
>     - Legenda: +2 pkt
>     - Róża wiatrów: +2 pkt
>
>     Jeśli score >= 8 → ZATWIERDŹ
>     Jeśli score < 8 → POPRAW
>     '''
> )
> ```"

---

### Slajd 65: Podsumowanie Module 08
**Co mówić:**
> "Doskonale! Iteracyjne doskonalenie działa! 🔄
>
> **Czego się nauczyliście:**
> - ✅ LoopAgent = iteracyjne doskonalenie
> - ✅ Wzorzec: Creator + Critic
> - ✅ max_iterations zapobiega nieskończonym pętlom
> - ✅ Jakość rośnie z każdą iteracją
>
> **Następny krok:** Database - zapisywanie danych!"

---

## ☕ PRZERWA (11:15 - 11:30, 15 min)

---

# 8️⃣ MODULE 09: DATABASE INTEGRATION (11:30 - 12:45, 75 min)

## Slajd 66: Kronikarz - Zapisywanie Wypraw
**Co mówić:**
> "Nowy temat: **Persistence**. Do tej pory wszystko w pamięci - po restarcie znika.
>
> **Scenariusz:** Kronikarz zapisuje wyprawy do bazy danych (SQLite). Dane przetrwają restart!
>
> To fundament aplikacji produkcyjnych."

---

## TEORIA (20 min)

### Slajd 67: Dlaczego Database?
**Co mówić:**
> "Bez database:
> - ❌ Dane znikają po restarcie
> - ❌ Nie można analizować historii
> - ❌ Nie można współdzielić danych
>
> Z database:
> - ✅ Persistence
> - ✅ Queries (SQL)
> - ✅ Analytics
> - ✅ Sharing"

---

### Slajd 68: SQLite - Prosty Start
**Co mówić:**
> "SQLite = baza danych w jednym pliku. Idealna na start:
>
> ```python
> import sqlite3
>
> # Połącz
> conn = sqlite3.connect('kronika.db')
> cursor = conn.cursor()
>
> # Stwórz tabelę
> cursor.execute('''
>     CREATE TABLE wyprawy (
>         id INTEGER PRIMARY KEY,
>         data TEXT,
>         cel TEXT,
>         lup TEXT,
>         straty INTEGER
>     )
> ''')
>
> # Zapisz
> cursor.execute('INSERT INTO wyprawy VALUES (?, ?, ?, ?, ?)',
>                (1, '2024-01-15', 'Tortuga', '1000 dublonów', 5))
> conn.commit()
> ```"

---

### Slajd 69: Database Tools dla Agenta
**Co mówić:**
> "Tworzymy tools które agent może używać:
>
> ```python
> def zapisz_wyprawe(data: str, cel: str, lup: str) -> str:
>     '''Zapisuje wyprawę do kroniki.'''
>     conn = sqlite3.connect('kronika.db')
>     cursor = conn.cursor()
>     cursor.execute('INSERT INTO wyprawy ...')
>     conn.commit()
>     return 'Zapisano!'
>
> def pokaz_historie() -> str:
>     '''Pokazuje ostatnie 10 wypraw.'''
>     conn = sqlite3.connect('kronika.db')
>     cursor = conn.cursor()
>     cursor.execute('SELECT * FROM wyprawy ORDER BY data DESC LIMIT 10')
>     return cursor.fetchall()
>
> kronikarz = LlmAgent(
>     tools=[zapisz_wyprawe, pokaz_historie]
> )
> ```"

---

## PRAKTYKA (55 min)

### Slajd 70: Hands-On - Kronikarz
**Co mówić:**
> "Otwórzcie `adk_training/module_09_database_simple/agent.py`
>
> **Zadanie 9.1 (20 min):**
> 1. Przeczytaj kod - database tools
> 2. Uruchom: `python init_database.py` (stwórz DB)
> 3. Uruchom: `adk web`
> 4. Testuj:
>    - 'Zapisz wyprawę do Tortuga, łup: 500 dublonów'
>    - 'Pokaż historię wypraw'
>    - 'Ile wypraw mamy w kronice?'
>
> Sprawdź plik `kronika.db` - dane są tam!"

---

### Slajd 71: Ćwiczenie 9.1 - Dodaj Queries
**Co mówić:**
> "**Ćwiczenie 9.1 (20 min):**
> Dodaj nowe queries:
>
> ```python
> def najlepsza_wyprawa() -> str:
>     '''Znajduje wyprawę z największym łupem.'''
>     # TODO: SELECT * FROM wyprawy ORDER BY lup DESC LIMIT 1
>
> def suma_lupow() -> str:
>     '''Oblicza całkowity łup ze wszystkich wypraw.'''
>     # TODO: SELECT SUM(lup) FROM wyprawy
>
> def wyprawy_do_celu(cel: str) -> str:
>     '''Znajduje wszystkie wyprawy do danego celu.'''
>     # TODO: SELECT * FROM wyprawy WHERE cel = ?
> ```
>
> Dodaj do tools i przetestuj!"

---

### Slajd 72: Ćwiczenie 9.2 - Postgres (Bonus)
**Co mówić:**
> "**Ćwiczenie 9.2 (15 min, opcjonalne):**
> Dla zaawansowanych - przełącz na Postgres:
>
> ```python
> import psycopg2
>
> conn = psycopg2.connect(
>     host='localhost',
>     database='pirate_db',
>     user='pirate',
>     password='arrr'
> )
> ```
>
> Zobacz `module_09_database_postgres/` dla przykładu"

---

### Slajd 73: Podsumowanie Module 09
**Co mówić:**
> "Brawo! Teraz dane przetrwają restart! 💾
>
> **Czego się nauczyliście:**
> - ✅ SQLite = prosty start
> - ✅ Database tools dla agenta
> - ✅ Persistence = dane przetrwają
> - ✅ SQL queries = analytics
>
> **Następny krok:** Memory Bank - pamięć między sesjami!"

---

## 🍽️ LUNCH (12:45 - 13:45, 60 min)

---

# 9️⃣ MODULE 11: MEMORY BANK (13:45 - 14:45, 60 min)

## Slajd 74: Pamiętnik Kapitana - Long-Term Memory
**Co mówić:**
> "Po lunchu - WOW moment! **Memory Bank** = agent pamięta między sesjami.
>
> **Scenariusz:**
> - Sesja 1 (poniedziałek): 'Lubię rum z limonką'
> - Sesja 2 (piątek): 'Przynieś mi drinka'
> - Agent: 'Oczywiście! Rum z limonką, jak lubisz! 🍹'
>
> Agent PAMIĘTA z poprzedniej sesji!"

---

## TEORIA (15 min)

### Slajd 75: Session vs Memory Bank
**Co mówić:**
> "Różnica:
>
> | Aspekt | Session | Memory Bank |
> |--------|---------|-------------|
> | Czas życia | Jedna rozmowa | Długoterminowo |
> | Zakres | Bieżąca sesja | Wszystkie sesje |
> | Storage | Tymczasowy | Vertex AI (cloud) |
> | Use case | Kontekst rozmowy | Preferencje, fakty |
>
> Session = pamięć krótkoterminowa
> Memory Bank = pamięć długoterminowa"

---

### Slajd 76: Vertex AI Memory Bank Service
**Co mówić:**
> "ADK integruje się z Vertex AI Memory Bank:
>
> ```python
> from google.adk.memory import VertexAiMemoryBankService
> from google.adk.tools.preload_memory_tool import PreloadMemoryTool
>
> memory_service = VertexAiMemoryBankService(
>     project=PROJECT_ID,
>     location=REGION,
>     agent_engine_id=ENGINE_ID
> )
>
> agent = LlmAgent(
>     tools=[PreloadMemoryTool()],  # Auto-load memories
>     after_agent_callback=auto_save_to_memory  # Auto-save
> )
> ```
>
> Automatyczne: load przed zapytaniem, save po odpowiedzi!"

---

### Slajd 77: Jak Działa Memory Bank?
**Co mówić:**
> "Flow:
>
> ```
> User: 'Lubię rum z limonką'
>     ↓
> Agent: Odpowiada
>     ↓
> Callback: Zapisuje sesję do Memory Bank
>     ↓
> Vertex AI: Przechowuje jako embedding
>
> ---
>
> User (nowa sesja): 'Przynieś drinka'
>     ↓
> PreloadMemoryTool: Wyszukuje relevantne memories
>     ↓
> Vertex AI: Zwraca 'User lubi rum z limonką'
>     ↓
> Agent: 'Rum z limonką, jak lubisz!'
> ```
>
> Similarity search na embeddingach!"

---

## PRAKTYKA (45 min)

### Slajd 78: Hands-On - Pamiętnik Kapitana
**Co mówić:**
> "Otwórzcie `adk_training/module_11_memory_bank/`
>
> **Zadanie 11.1 (20 min):**
> 1. Uruchom: `python create_agent_engine.py` (stwórz Agent Engine w Vertex AI)
> 2. Skopiuj `agent_engine_id` do `.env`
> 3. Uruchom: `python run_agent.py`
> 4. Testuj:
>    - Sesja 1: 'Lubię temperaturę 23°C'
>    - Sesja 2 (nowa): 'Jaka jest moja preferowana temperatura?'
>
> Agent PAMIĘTA!"

---

### Slajd 79: Ćwiczenie 11.1 - Wiele Preferencji
**Co mówić:**
> "**Ćwiczenie 11.1 (15 min):**
> Naucz agenta zapamiętywać:
> - Ulubiony kolor
> - Ulubione jedzenie
> - Hobby
> - Preferowana temperatura
>
> Testuj w różnych sesjach - agent powinien pamiętać wszystko!"

---

### Slajd 80: Ćwiczenie 11.2 - List Memories
**Co mówić:**
> "**Ćwiczenie 11.2 (10 min):**
> Dodaj tool do listowania wspomnień:
>
> ```python
> async def pokaz_wspomnienia(tool_context: ToolContext) -> str:
>     '''Pokazuje wszystkie zapisane wspomnienia.'''
>     memories = await memory_service.list_memories(user_id='user')
>     return '\\n'.join([m.content for m in memories])
> ```
>
> Testuj: 'Pokaż co o mnie pamiętasz'"

---

### Slajd 81: Podsumowanie Module 11
**Co mówić:**
> "WOW! Agent pamięta między sesjami! 🧠
>
> **Czego się nauczyliście:**
> - ✅ Memory Bank = long-term memory
> - ✅ Vertex AI Agent Engine
> - ✅ PreloadMemoryTool + auto-save callback
> - ✅ Similarity search na embeddingach
>
> **Następny krok:** RAG Agent - wyszukiwanie w dokumentach!"

---

## ☕ PRZERWA (14:45 - 15:00, 15 min)

---

# 🔟 MODULE 03: RAG AGENT (15:00 - 16:00, 60 min)

## Slajd 82: Biblioteka Nawigacyjna - RAG
**Co mówić:**
> "Ostatni moduł! **RAG** = Retrieval-Augmented Generation.
>
> **Scenariusz:** Bibliotekarz przeszukuje tysiące map i dokumentów nawigacyjnych, znajduje relevantne, i odpowiada z cytatami.
>
> To enterprise use case - integracja z korporacyjną wiedzą!"

---

## TEORIA (15 min)

### Slajd 83: Czym jest RAG?
**Co mówić:**
> "RAG = LLM + Wyszukiwanie w dokumentach
>
> **Bez RAG:**
> User: 'Jaka trasa do Tortuga?'
> Agent: 'Nie wiem' (brak wiedzy)
>
> **Z RAG:**
> User: 'Jaka trasa do Tortuga?'
> Agent: Przeszukuje dokumenty → Znajduje 'Mapa Karaibów 1720'
> Agent: 'Według Mapy Karaibów 1720: płyń na południe...'"

---

### Slajd 84: Vertex AI Search Tool
**Co mówić:**
> "ADK integruje się z Vertex AI Search:
>
> ```python
> from google.adk.tools import VertexAiSearchTool
>
> biblioteka = VertexAiSearchTool(
>     data_store_id='pirate_maps_and_charts',  # Data Store w Vertex AI
>     max_results=5  # Top 5 dokumentów
> )
>
> bibliotekarz = LlmAgent(
>     instruction='Przeszukuj dokumenty i cytuj źródła',
>     tools=[biblioteka]
> )
> ```"

---

### Slajd 85: Setup - Vertex AI Search
**Co mówić:**
> "Wymagania:
> 1. Vertex AI Search włączony w GCP
> 2. Data Store utworzony
> 3. Dokumenty zindeksowane
>
> To wymaga czasu (15-30 min indexing), więc przygotowałem demo data store.
>
> W produkcji: uploadujecie swoje dokumenty (PDF, HTML, TXT)"

---

## PRAKTYKA (45 min)

### Slajd 86: Demo - RAG w Akcji
**Co mówić:**
> "Pokażę live demo (10 min):
>
> 1. Data Store z mapami piratów (PDF)
> 2. Agent z VertexAiSearchTool
> 3. Pytania:
>    - 'Jaka trasa do Tortuga?'
>    - 'Gdzie są rafy koralowe?'
>    - 'Jakie porty są bezpieczne?'
>
> Obserwujcie - agent cytuje źródła!"

**Akcja:** Live demo z przygotowanym data store

---

### Slajd 87: Hands-On - Bibliotekarz (jeśli czas)
**Co mówić:**
> "Jeśli macie skonfigurowany Vertex AI Search:
>
> **Zadanie 3.1 (20 min):**
> 1. Stwórz Data Store w Vertex AI Search
> 2. Upload 2-3 dokumenty (PDF/TXT)
> 3. Poczekaj na indexing (15 min)
> 4. Skonfiguruj `data_store_id` w kodzie
> 5. Testuj agenta
>
> Jeśli nie - obserwujcie demo"

---

### Slajd 88: Ćwiczenie 3.1 - Multi-Source RAG
**Co mówić:**
> "**Ćwiczenie 3.1 (15 min):**
> Dodaj wiele źródeł:
>
> ```python
> mapy = VertexAiSearchTool(data_store_id='maps')
> dokumenty = VertexAiSearchTool(data_store_id='documents')
> rejestry = VertexAiSearchTool(data_store_id='registries')
>
> bibliotekarz = LlmAgent(
>     tools=[mapy, dokumenty, rejestry]  # 3 źródła!
> )
> ```
>
> Agent wybierze odpowiednie źródło!"

---

### Slajd 89: Podsumowanie Module 03
**Co mówić:**
> "Doskonale! RAG = enterprise AI! 📚
>
> **Czego się nauczyliście:**
> - ✅ RAG = LLM + Document Search
> - ✅ Vertex AI Search Tool
> - ✅ Cytowanie źródeł
> - ✅ Enterprise knowledge integration
>
> **To był ostatni moduł!** 🎉"

---

# 🎓 ZAKOŃCZENIE SZKOLENIA (16:00 - 16:30, 30 min)

## Slajd 90: Podsumowanie 2 Dni
**Co mówić:**
> "Gratulacje! Ukończyliście podróż przez Archipelag ADK! 🏴‍☠️
>
> **Dzień 1 - Fundamenty:**
> 1. Hello World - LlmAgent
> 2. Custom Tools - narzędzia
> 3. Sequential - pipeline
> 4. Parallel - równoległość
> 5. Router - routing
>
> **Dzień 2 - Zaawansowane:**
> 6. Human-in-Loop - zatwierdzenia
> 7. Loop Critique - iteracje
> 8. Database - persistence
> 9. Memory Bank - long-term memory
> 10. RAG - document search
>
> Od rekruta do admirała!"

---

## Slajd 91: Kluczowe Wnioski
**Co mówić:**
> "Najważniejsze lekcje:
>
> 1. **LlmAgent** to fundament - prosty ale potężny
> 2. **Tools** dają agentom ręce - mogą działać
> 3. **Multi-agent** (Sequential/Parallel/Router) = orkiestracja
> 4. **Callbacks** = kontrola i bezpieczeństwo
> 5. **Persistence** (DB/Memory) = produkcja
> 6. **RAG** = enterprise knowledge
>
> Macie teraz wszystkie narzędzia do budowania produkcyjnych agentów!"

---

## Slajd 92: Następne Kroki
**Co mówić:**
> "Co dalej?
>
> **1. Praktyka:**
> - Zbuduj własnego agenta dla swojego use case
> - Połącz wiele wzorców (Router + Sequential + Tools)
> - Wdróż na Cloud Run (Module 06)
>
> **2. Nauka:**
> - [ADK Docs](https://google.github.io/adk-docs/)
> - [Gemini API](https://ai.google.dev/gemini-api)
> - [Vertex AI](https://cloud.google.com/vertex-ai)
>
> **3. Community:**
> - GitHub: google/adk
> - Discord: [link]
> - Stack Overflow: tag `google-adk`"

---

## Slajd 93: Certyfikaty
**Co mówić:**
> "Każdy z Was otrzymuje certyfikat:
>
> **'Kapitan [Imię] ukończył podróż przez Archipelag ADK i jest gotów dowodzić własną flotą agentów AI!'**
>
> [Rozdaj certyfikaty]"

---

## Slajd 94: Q&A Finalne
**Co mówić:**
> "Ostatnie pytania? (15 min)
>
> [Odpowiadaj na pytania]
>
> Dziękuję za udział! Powodzenia w budowaniu agentów! ⚓🏴‍☠️
>
> Kontakt: [email/slack]"

---

## Slajd 95: Zdjęcie Grupowe
**Co mówić:**
> "Zdjęcie na pamiątkę! 📸
>
> Wszyscy z certyfikatami - uśmiech!
>
> Ahoj, Kapitanie! ⚓"

---

# 📚 DODATKI

## Materiały dla Uczestników
- 📖 Handbook piracki (PDF) - wszystkie przykłady
- 🗺️ Mapa Archipelagu ADK (diagram)
- 🏴‍☠️ Słownik terminologii
- 💾 Repozytorium GitHub
- 🎓 Certyfikat PDF

## Feedback Form
- Link do ankiety
- Ocena każdego modułu (1-5)
- Co było najlepsze?
- Co poprawić?
- Czy polecisz szkolenie?

---

**KONIEC PLANU PREZENTACJI** 🎉

