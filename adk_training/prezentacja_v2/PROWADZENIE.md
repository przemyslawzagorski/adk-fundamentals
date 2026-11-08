# Prowadzenie szkolenia – Google ADK 2 (2 dni)

Przewodnik prowadzącego do `Google_ADK_Architektura_Agentow_v2.pptx`. Numery slajdów
odnoszą się do tej wersji. Kod: branch `training_09_10_11`, katalog `adk_training/`.

## 0. Przed szkoleniem (checklista)

- [ ] **Model.** Wszystkie moduły czytają `ADK_MODEL` z `.env`; domyślnie `gemini-3.5-flash-lite`.
  Uczestnicy kopiują `.env.template` → `.env`. Lokalizacja to zawsze `GOOGLE_CLOUD_LOCATION=global`, bo modele 3.5 są dostępne tylko tam.
- [ ] **Wersja ADK.** `pip install --upgrade "google-adk>=2.13.0"`, potem `pip show google-adk`.
- [ ] **Indeksy RAG (D1.3).** Działający `SEARCH_ENGINE_ID`, np. `pirate-knowledge-search_…`, sprawdzony na lite.
- [ ] **OAuth (D2.4).** Uczestnicy dodani jako *test users* na consent screen.
  **Zrotuj `GOOGLE_CLIENT_SECRET`, który wyciekł na czacie poprzedniej edycji.**
- [ ] **Uprawnienia.** Rola do tworzenia bucketów i AI Applications (D1.4) oraz Agent Engine (D2.2).
- [ ] **Windows.** `$env:PYTHONUTF8 = '1'`, bo inaczej emoji w modułach dają `UnicodeEncodeError`.
  Flaga `--reload` w `adk web` nie działa na Windows; po zmianie kodu restartuj `adk web`.
- [ ] **Usługa demo.** Cloud Run `pirate-navigator` odpowiada (D1.12).

### Koszt: dlaczego flash-lite

| Model | Input $/1M | Output $/1M | 12 osób × 2 dni (szac.) |
|---|---|---|---|
| gemini-3.5-flash | 1.50 | 9.00 | ~32 $ |
| gemini-3.5-flash-lite | 0.30 | 2.50 | ~8 $ |

Ceny pochodzą ze źródła zewnętrznego; przed szkoleniem warto je zweryfikować w cenniku Vertex AI.

Flash-lite przetestowany na modułach:
- 01, 02, 03, 04w (z rozwiązaniem), 05, 07w, 08, 08w, 12 (z rozwiązaniem), 26, 33;
- pz_bonus 02c i 02d.

Lite jest słabszy w delegacji. W module 33 sub-agent zapętlał `transfer_to_agent`; naprawione blokadą transferu, a ćwiczenie 33.3 pokazuje ten problem na żywo. Gdy któryś moduł zachowuje się dziwnie, uczestnik może przełączyć `ADK_MODEL=gemini-3.5-flash` – **to też jest lekcja**: słabszy model wymaga mocniejszej architektury.

---

## 1. Harmonogram – Dzień 1 (fundamenty i orkiestracja)

| Czas | Slajdy | Co |
|---|---|---|
| 09:00–09:40 | 1–15 | Otwarcie, Blok 1: czym jest agent, architektura, rynek |
| 09:40–09:55 | 16–21 | Blok 2: typy agentów, setup, pierwszy agent w ADK 2, model i koszt |
| 09:55–10:20 | 22 | **D1.1** Hello Agent |
| 10:20–10:45 | 23–24 | **D1.2** Własne narzędzia (20) |
| 10:45–10:55 | | *Przerwa* |
| 10:55–11:05 | 25–28 | Blok 3: RAG |
| 11:05–11:25 | 29 | **D1.3** RAG z Vertex AI Search |
| 11:25–11:40 | 30 | **D1.4 cz. 1**: bucket → datastore → app, *start importu* |
| 11:40–11:50 | 31–34 | Blok 4: Runner, sesja, stan (indeks buduje się w tle) |
| 11:50–12:15 | 35 | **D1.5** Agent z Pythona (Gradio) |
| 12:15–12:30 | 30 | **D1.4 cz. 2**: zapytania do własnego indeksu |
| 12:30–13:10 | | *Obiad* |
| 13:10–13:25 | 36–38 | Blok 5: wzorce multi-agent, Workflow, v1 vs v2 |
| 13:25–13:50 | 39 | **D1.6** Sekwencja |
| 13:50–14:10 | 40 | **D1.7** Równoległość |
| 14:10–14:40 | 41–42 | Custom agent → router + **D1.8** Pętla krytyki (25) |
| 14:40–14:50 | | *Przerwa* |
| 14:50–15:15 | 43–45 | Blok 6: callbacki + **D1.9** HITL (20) |
| 15:15–15:55 | 46–47 | Blok 7: delegacja + **D1.10** (30) |
| 15:55–16:15 | 48–49 | Plannery + **D1.11** (15) |
| 16:15–16:25 | 50–53 | Blok 8: deploy + **D1.12** jako demo (10) |
| 16:25–16:30 | 54 | Podsumowanie dnia, pytania kontrolne |

**Gdy jesteś w niedoczasie** (kolejność cięć):
1. D1.7 – tylko 07w;
2. D1.11 – demo prowadzącego;
3. D1.12 – tylko URL usługi.

Nie tnij D1.6 ani D1.8, bo to rdzeń szkolenia (Workflow).

## 2. Harmonogram – Dzień 2 (produkcja i integracje)

| Czas | Slajdy | Co |
|---|---|---|
| 09:00–09:15 | 55 | Recap dnia 1 (pytania kontrolne ze slajdu 54) |
| 09:15–09:55 | 56–57 | Blok 9: artefakty + **D2.1** |
| 09:55–10:35 | 58–59 | Blok 10: pamięć + **D2.2** |
| 10:35–10:45 | | *Przerwa* |
| 10:45–11:10 | 60–63 | Blok 11: integracje – bazy, MCP, A2A, OAuth |
| 11:10–11:45 | 64 | **D2.3** Agent i baza danych |
| 11:45–12:30 | 65 | **D2.4 cz. 1**: MCP gotowy i własny |
| 12:30–13:10 | | *Obiad* |
| 13:10–13:40 | 65 | **D2.4 cz. 2**: OAuth |
| 13:40–14:20 | 66–67 | Blok 12: Skills + **D2.5** |
| 14:20–14:30 | | *Przerwa* |
| 14:30–15:20 | 68–69 | Blok 13: piramida testów + **D2.6** |
| 15:20–16:00 | 70–76 | Enterprise, roadmapa, checklista architekta |
| 16:00–16:30 | 77–79 | Q&A, ankieta; bufor na moduły zapasowe |

---

## 3. Ćwiczenia – Dzień 1

Format: **Pokazuję** (prowadzący, 2–5 min) → **Robią** → **Dodają** (szybsi) →
**Sprawdzenie** → **Pułapki** → **Wniosek** (wypowiedz go na głos na koniec).

### D1.1 Hello Agent – `module_01_hello_world` · 25 min · slajd 22 (dawne zad1)
- **Pokazuję:**
  - struktura modułu (`agent.py`, `__init__.py`, `.env`);
  - zakładki `adk web`: Chat / Events / Trace / State.
- **Robią:**
  1. `adk web --reload_agents` i rozmowa z agentem.
  2. Odkomentuj `google_search` i zapytaj o coś aktualnego.
  3. Ustaw `ADK_MODEL=gemini-9-flash` i przeczytaj błąd `404 NOT_FOUND`.
  4. Porównaj odpowiedzi lite z flash.
  5. `pip install --upgrade` i `pip show google-adk`.
- **Dodają:** tokeny w `usage_metadata`; persona i format odpowiedzi.
- **Pułapki:**
  - „Gdzie wpisać model?” – w `.env` (`ADK_MODEL`);
  - brak linków z wyszukiwania – pokaż grounding w Events.
  - Lista modeli: cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions
- **Wniosek:** model to konfiguracja, nie kod; koszt i jakość zmieniasz w `.env`.

### D1.2 Własne narzędzia – `module_02_custom_tool` · 20 min · slajd 24 (zad2)
- **Pokazuję:**
  - docstring i type hints jako kontrakt narzędzia;
  - co się dzieje przy złym docstringu.
- **Robią:**
  1. Dopisują nową funkcję-narzędzie i dodają ją do `tools`.
  2. Jednym promptem odpalają kilka narzędzi: „Dodaj 5 złotych monet, potem pokaż inwentarz i policz pozycje”.
  3. Śledzą w Events kolejność function call → response.
- **Dodają:** walidacja, która zwraca `{"status": "error"}`; zapis w `tool_context.state`.
- **Pułapki:** graf nie odświeża się bez restartu `adk web` (pytanie z poprzedniej grupy).
- **Wniosek:** narzędzie zwraca status, a błąd to dane, nie wyjątek; LLM sam łączy wywołania.

### D1.3 RAG – `module_03_rag_agent` · 20 min · slajd 29 (zad3)
- **Robią:**
  1. Wpisują w `.env` jedno z: `SEARCH_ENGINE_ID` (preferowany) albo `SEARCH_DATASTORE_ID`.
  2. Pytają o treść dokumentów.
  3. Zmieniają `max_results` i instrukcję.
  4. Zadają pytanie spoza dokumentów.
- **Dodają:** „cytuj źródło / powiedz nie wiem”; porównanie engine i datastore.
- **Pułapki:**
  - ID zawsze z `locations/global`;
  - `404 DataStore not found` oznacza stare ID (poprzednia grupa: engine działał, datastore dawał 404);
  - `UnicodeEncodeError` naprawia `PYTHONUTF8=1`.
- **Wniosek:** jakość RAG zależy od indeksu, nie od promptu.

### D1.4 Własny indeks – konsola GCP + module_03 · 15 + 15 min · slajd 30 (zad4)
- **Część 1** (przed Blokiem 4):
  1. Bucket i własne PDF/MD.
  2. AI Applications: datastore z bucketa, potem app.
  3. **Start importu.**
- **Część 2** (12:15, po D1.5): podmiana ID w `.env` i pytania o *swoje* dokumenty.
- **Pułapki:**
  - „Unable to create your bucket” – ponów (u części osób działało za drugim razem);
  - brak wyników – indeks jeszcze się buduje.
- **Wniosek:** pipeline wiedzy (źródło → indeks → agent) aktualizujesz bez zmiany kodu.

### D1.5 Agent z Pythona – `pz_bonus/adk_services_01_session_gradio` · 25 min · slajd 35 (zad7)
- **Dlaczego wcześniej niż w poprzedniej edycji:** stan (`output_key`, `{klucz}`, prefiksy) jest fundamentem Workflow w D1.6.
- **Robią:**
  1. `cd adk_training\pz_bonus\adk_services_01_session_gradio`, potem `python ui.py`.
  2. Podgląd stanu w UI.
  3. Nowa sesja kontra kontynuacja.
- **Dodają:** prefiksy `user:` / `app:` / `temp:`; trwały SessionService.
- **Wniosek:** Runner i SessionService to runtime agenta; `adk web` to tylko jeden z klientów.

### D1.6 Sekwencja – module_04 → `module_04w_workflow_sequence` · 25 min · slajd 39 (zad5 + 5b)
- **Pokazuję:**
  - ten sam rajd w 04 (SequentialAgent, deprecated) i w 04w (`Workflow(edges=[...])`);
  - funkcja jako węzeł.
- **Robią:**
  1. 4W.2: agent `kwatermistrz` (`output_key="lista_zapasow"`) przed Kapitanem.
  2. Używają `{lista_zapasow}` w instrukcji Kapitana.
- **Dodają:** 4W.1, czyli funkcja `ocen_ryzyko(plan_bitwy: str)`. Parametr jest wstrzykiwany ze stanu po nazwie, a wynik idzie przez `yield Event(state=...)`.
- **Rozwiązanie:** `agent_solution.py` (przetestowane na lite). Włączenie: `from .agent_solution import root_agent` w pustym `__init__.py`, potem restart.
- **Pułapki:**
  - `{klucz}`, którego nie ma w stanie, rzuca błąd – użyj `{klucz?}`;
  - nowy węzeł pojawia się dopiero po restarcie.
- **Wniosek:** proces o znanej kolejności to graf w kodzie, nie decyzja LLM.

### D1.7 Równoległość – module_07 → `module_07w_workflow_parallel` · 20 min · slajd 40 (zad6 + 6b)
- **Robią:** „Zbadaj wyspę Skull Island”, kolejność zakończenia w Events, 7W.1 (czwarty zwiadowca, tylko `edges`).
- **Dodają:** 7W.2, czyli `podsumuj_zbiorke(node_input: dict)` po `JoinNode`. Klucze słownika to nazwy węzłów.
- **Pułapki:** `429 RESOURCE_EXHAUSTED`, gdy cała grupa startuje naraz.
- **Wniosek:** niezależne kroki równolegle skracają czas, a JoinNode zbiera wyniki.

### D1.8 Pętla krytyki – module_08 → `module_08w_workflow_loop` · 25 min · slajdy 41–42 (zad9 + 9b)
- **Pokazuję:**
  - slajd 41: custom `_run_async_impl` z ADK 1;
  - w ADK 2 to samo robi funkcja-router `yield Event(route=...)`.
- **Robią:**
  1. 08 i 08w z tym samym tematem.
  2. Zmiana kryteriów krytyka.
  3. Znalezienie `MAX_ITERACJI` i routera.
- **Dodają:** 8W.2 (kapitan jako funkcja, mniej wywołań LLM); 8W.1 (`RequestInput`).
- **Tip od uczestnika poprzedniej edycji:** w schemacie `reason` przed `decision`, bo model generuje token po tokenie (wdrożone w 05, 08, 08w).
- **Wniosek:** jakość przez iterację, a twardy limit pętli daje przewidywalny koszt.

### D1.9 HITL przez callbacki – `module_05_human_in_loop` · 20 min · slajdy 43–45 (zad8)
- **Robią:**
  1. „Potrzebuję 500 dublonów na naprawę żagli”.
  2. Sprawdzają `pending_approval` w State.
  3. Próbują „tak, zatwierdzam”: kwatermistrz odmawia, bo zatwierdza tylko Admirał.
  4. Śledzą callbacki.
- **Dodają:** zmiana progu kwoty; guardrail `before_model_callback` (słowa lub PII).
- **Pułapki:** „uparty” agent to zamierzone zabezpieczenie, nie błąd.
- **Wniosek:** callbacki to punkt kontroli (guardrails, zatwierdzenia) bez zmiany agenta. W grafie natywnie: `RequestInput` (Z2).

### D1.10 Delegacja – `module_12_router_agent` + `module_33_task_api` · 30 min · slajdy 46–47 (zad10 + nowe)
- **Robią:**
  1. 12: dodają specjalistę do `sub_agents` (transfer).
  2. AgentTool: `from .agent_solution import root_agent` w `__init__.py`, prompt „Mamy rannego marynarza i trzeba wyznaczyć kurs na Jamajkę”.
     - AgentTool woła `doctor` i `navigator` **naraz**, a kapitan zostaje w rozmowie;
     - przy transferze rozmowę przejmuje jeden specjalista.
  3. 33: „Przygotuj statek, płyniemy do Tortugi”, potem lista zapasów, potem „To wszystko”.
- **Dodają:** agent `skarbnik` (`mode="single_turn"`); porównanie z routingiem w kodzie (moduł 26).
- **Pułapka lite (do pokazania!):**
  - bez `disallow_transfer_to_parent/peers` sub-agent w trybie task zapętla `transfer_to_agent` zamiast wołać `finish_task`;
  - naprawione w module; ćwiczenie 33.3 każe zdjąć blokadę i zobaczyć pętlę.
- **Wniosek:** wybór delegacji to wybór, kto kontroluje rozmowę i ile wywołań LLM płacisz.

### D1.11 Plannery – `pz_bonus` 02c vs 02d · 15 min · slajdy 48–49 (zad11)
- `cd adk_training\pz_bonus`, potem `adk web .`; to samo pytanie w obu modułach.
- **Na lite:** `thinking_level=LOW` daje 0 thoughts; `HIGH` myśli. To nie błąd, tylko gotowy materiał do dyskusji o koszcie, bo thinking jest płatny jak output.
- **Wniosek:** jawny plan (ReAct) kontra thinking modelu, czyli koszt tokenów kontra jakość.

### D1.12 Deploy – `module_06_cloud_run` · 10 min demo · slajdy 50–53 (zad12)
- URL usługi: `pirate-navigator-28948426345.us-central1.run.app`; `pirate_navigator/agent.py` to ten sam kod co lokalnie.
- Chętni wdrażają wieczorem wg `DEPLOY_GCLOUD_GUIDE.md`.
- **Wniosek:** agent to usługa, a konfiguracja idzie przez zmienne środowiskowe.

---

## 4. Ćwiczenia – Dzień 2

### D2.1 Artefakty – `pz_bonus/a01_intro` · 30 min · slajd 57
- **Robią:**
  1. Generują obraz (zapisuje się jako artefakt).
  2. W **nowej sesji** proszą o opis poprzedniego obrazu.
  3. Edytują obraz, co tworzy nową wersję artefaktu.
- **Pułapki:**
  - przy całej grupie łatwo o 429, więc generujcie na zmianę;
  - model obrazów to `gemini-2.5-flash-image`.
- **Wniosek:** pliki trzymamy poza kontekstem LLM, a sesja przechowuje tylko referencje.

### D2.2 Memory Bank – `module_11_memory_bank` · 30 min · slajd 59
- **Robią:**
  1. `python create_agent_engine.py`.
  2. `adk web --memory_service_uri=agentengine://projects/<P>/locations/us-central1/reasoningEngines/<ID>`
  3. Podają fakty o sobie.
  4. W nowej sesji agent je pamięta.
- **Pułapka:** krótki `agentengine://<ID>` użyje lokalizacji `global` i nie znajdzie banku, więc **zawsze podawaj pełny URI z regionem**.
- **Wniosek:** stan `user:` to pamięć ustrukturyzowana; Memory Bank to wspomnienia wyszukiwane semantycznie.

### D2.3 Baza danych – `module_09_database_postgres` / `_simple` · 35 min · slajd 64
- Postgres (Neon) przez MCP Toolbox, `sslmode=require`; plan B to `module_09_database_simple`.
- **Pułapka:** Toolbox na Windows działa najpewniej pod WSL2.
- **Wniosek:** dane udostępniamy przez wąskie narzędzia (read-only, limity), nie przez surowy SQL.

### D2.4 MCP + OAuth – `module_16`, `module_06` (MCP), `pz_bonus/adk06_oauth_api` · 45 + 30 min · slajd 65
- **Przed obiadem:** gotowy serwer MCP, potem własny serwer MCP (STDIO).
- **Po obiedzie:** OAuth (consent screen, redirect URI, People API).
- **Pułapki:**
  - `403` – brak test usera albo wyłączone API;
  - w PowerShell testuj przez here-string, nie `echo |`;
  - **sekretów nie wklejamy na czat**.
- **Wniosek:** MCP to standard; własny serwer daje narzędzia reużywalne przez wielu agentów.

### D2.5 Skills – `module_14_agent_skills` · 30 min · slajd 67
- Uruchamiamy **z katalogu modułu** (`adk web .`); kolejność: `agent.py` → `agent_dynamic.py` → `agent_self_loading.py`.
- **Wniosek:** wiedza doładowana na żądanie daje mniejszy prompt i niższy koszt. Porównaj ze slajdem o instructions / skills / MCP.

### D2.6 Testy i ewaluacja – `module_21_adk_tester` + `module_31_evaluation` · 40 min · slajd 69
- **Robią:**
  1. `python -m playwright install chromium`.
  2. Scenariusz dla własnego agenta z dnia 1.
  3. Raport testera.
  4. W module 31: dataset i kryteria.
- **Pułapki:**
  - `COMPUTER_USE_MODEL` to preview, sprawdź dostępność;
  - porty 8000/8001;
  - raport mailowy może trafić do spamu.
- **Uwaga:** API ewaluacji (moduł 31) nie zostało przetestowane na lite; przećwicz przed szkoleniem.
- **Wniosek:** agent bez testów to prototyp. Kolejność: testy narzędzi, potem E2E, potem ewaluacja trajektorii.

---

## 5. Moduły zapasowe (dla zaawansowanej grupy)

| # | Moduł | Kiedy | Wartość |
|---|---|---|---|
| Z1 | `module_26_graph_routes` | po D1.10 | routing deterministyczny `Event(route=)` vs router LLM |
| Z2 | `module_28_human_input` | po D1.9 | HITL natywnie w Workflow (`RequestInput`) |
| Z3 | `module_31_evaluation` | w D2.6 | ewaluacja zamiast ręcznego testu |
| Z4 | `module_27_data_handling` | po D1.6 | przepływ danych w grafie |
| Z5 | guardrail `before_model_callback` w module 05 | po D1.9 | bezpieczeństwo, 10 min |
| Z6 | `module_32_a2a` | dzień 2, blok 11 | agent przez granicę procesu (uvicorn :8001) |
| Z7 | `module_29_collaboration` / `30_dynamic` | tylko pokaz | `@node`, `ctx.run_node`, dynamiczne grafy |

Moduły 25–32 nie mają README; omawiaj je bezpośrednio z kodu.

## 6. Tricki z poprzedniej edycji

- `adk web --reload_agents`; na Windows `--reload` jest wymuszone na `--no-reload`, więc restartuj ręcznie.
- `$env:PYTHONUTF8 = '1'` usuwa całą klasę błędów `UnicodeEncodeError`.
- Moduły `pz_bonus` uruchamiamy z katalogu `pz_bonus` (`adk web .`).
- W schematach strukturalnych najpierw `reason`, potem `decision`.
- Region Cloud Run (us-central1) to co innego niż lokalizacja modelu (global).
- Nowy agent albo węzeł jest widoczny w grafie dopiero po restarcie `adk web`.
