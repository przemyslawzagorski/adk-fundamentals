# Prezentacja v2 – Google ADK: Architektura Agentów AI

Wynikowa prezentacja: `Google_ADK_Architektura_Agentow_v2.pptx` (79 slajdów, 16:9).
Przewodnik prowadzącego (harmonogram, ćwiczenia, pułapki): [PROWADZENIE.md](./PROWADZENIE.md).

## Zasada układu

Każdy blok to **teoria → ćwiczenie**, bez skakania między tematami. Każde ćwiczenie ma
jeden slajd o stałym układzie:

- **Robią (wszyscy)** – kroki obowiązkowe;
- **Dodają (dla szybszych)** – rozszerzenia;
- **Sprawdzenie ✓** – po czym poznać, że działa;
- **Pułapki / fixy** – znane błędy z poprzednich edycji;
- **Wniosek architektoniczny** – jedno zdanie, które ma zostać w głowie.

W notatkach prelegenta jest mapowanie na dawne numery „zad” z czatu.

## Mapa slajdów

| Slajdy | Blok | Ćwiczenia |
|---|---|---|
| 1–4 | Otwarcie, agenda, separator dnia 1 | – |
| 5–15 | **Blok 1** – czym są agenci, architektura, rynek | – |
| 16–24 | **Blok 2** – typy agentów, setup labu, pierwszy agent w ADK 2, model i koszt | D1.1 (22), D1.2 (24) |
| 25–30 | **Blok 3** – RAG i Vertex AI Search | D1.3 (29), D1.4 (30) |
| 31–35 | **Blok 4** – runtime: Runner, sesja, stan | D1.5 (35) |
| 36–42 | **Blok 5** – wzorce multi-agent, Workflow, v1 vs v2, custom agent | D1.6 (39), D1.7 (40), D1.8 (42) |
| 43–45 | **Blok 6** – callbacki, human-in-the-loop | D1.9 (45) |
| 46–49 | **Blok 7** – delegacja (transfer / AgentTool / Task), plannery | D1.10 (47), D1.11 (49) |
| 50–54 | **Blok 8** – deploy, podsumowanie dnia 1 | D1.12 (53) |
| 55–57 | Separator dnia 2, **Blok 9** – artefakty | D2.1 (57) |
| 58–59 | **Blok 10** – pamięć długoterminowa | D2.2 (59) |
| 60–65 | **Blok 11** – integracje: bazy, MCP, A2A, OAuth | D2.3 (64), D2.4 (65) |
| 66–67 | **Blok 12** – Skills | D2.5 (67) |
| 68–69 | **Blok 13** – testowanie i ewaluacja | D2.6 (69) |
| 70–76 | Enterprise, roadmapa, checklista architekta | – |
| 77–79 | Linki, Q&A, zakończenie | – |

## Co zmieniono względem oryginału

- **Nowe slajdy (ok. 30):**
  - agenda dwudniowa i separatory dni;
  - setup labu;
  - kod pierwszego agenta w ADK 2;
  - model i koszt (flash vs flash-lite);
  - graf Workflow;
  - porównanie kodu v1 i v2;
  - delegacja i plannery;
  - piramida testów;
  - podsumowanie dnia 1;
  - 18 slajdów ćwiczeń.
- **Naklejki „ADK 2”** na slajdach o Sequential/Parallel/Loop i o własnym `_run_async_impl`. Te API są w ADK 2 deprecated, a zamiennik to `Workflow`.
- **Usunięte slajdy oryginału:**
  - 42 i 49 – nieaktualny kod (`gemini-2.0`) i literówki;
  - 50 – pusty placeholder „adk2”.
- **Zmieniona kolejność:**
  - blok enterprise i roadmapa przeniesione na koniec dnia 2;
  - teoria stanu (blok 4) stoi przed Workflow, bo `output_key` i `{klucz}` są potrzebne w D1.6.

## Mapowanie ćwiczeń (dawne „zad” → nowe)

| Nowe | Dawne | Moduł |
|---|---|---|
| D1.1 | zad1 | module_01_hello_world |
| D1.2 | zad2 | module_02_custom_tool |
| D1.3 | zad3 | module_03_rag_agent |
| D1.4 | zad4 | konsola GCP + module_03 |
| D1.5 | **zad7** (przesunięte wcześniej) | pz_bonus/adk_services_01_session_gradio |
| D1.6 | zad5 + 5b | module_04 → module_04w_workflow_sequence |
| D1.7 | zad6 + 6b | module_07 → module_07w_workflow_parallel |
| D1.8 | **zad9** + 9b (przed HITL) | module_08 → module_08w_workflow_loop |
| D1.9 | **zad8** | module_05_human_in_loop |
| D1.10 | zad10 + nowe | module_12_router_agent + module_33_task_api |
| D1.11 | zad11 | pz_bonus 02c vs 02d |
| D1.12 | zad12 | module_06_cloud_run |
| D2.1–D2.6 | dzień 2, zad1–zad6 | a01, 11, 09, 16/06/adk06, 14, 21 + 31 |

## Regeneracja

Slajdy budowane są skryptem `build_deck.py` (python-pptx). Plik `.pptx` nie jest w gicie
(`.gitignore`) – generujesz go lokalnie. Źródłem jest oryginalna prezentacja
`Architektura Agentów AI (1).pptx` (leży w głównym checkoutcie repo, `adk-fundamentals\adk_training\`).
Skrypt potrzebuje jej kopii pod ścieżką bez spacji i nawiasów:

```powershell
cd adk_training\prezentacja_v2
New-Item -ItemType Directory _work -Force | Out-Null
Copy-Item "<ścieżka>\Architektura Agentów AI (1).pptx" _work\source.pptx
$env:PYTHONUTF8 = '1'
python build_deck.py _work\source.pptx Google_ADK_Architektura_Agentow_v2.pptx
Remove-Item _work -Recurse -Force
```

Treść ćwiczeń zmieniasz w słowniku `EX` (sekcja „EX = {}”). Wnioski architektoniczne są
w słowniku `GOALS`, a kolejność slajdów w liście `order` na końcu skryptu.
