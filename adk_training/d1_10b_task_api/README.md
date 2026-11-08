# D1.10b: Task API – Zespół agentów z trybami pracy (ADK 2)

## 📚 Przegląd

Kapitan Portu przygotowuje statek do rejsu i deleguje zadania podwładnym.
Nowość ADK 2: sub-agent dostaje **tryb pracy** (`mode`), który określa, czy
rozmawia z użytkownikiem i jak oddaje wynik koordynatorowi.

**Czas trwania:** 40 minut
**Wymaga:** `d1_10a_router_transfer` (router / sub_agents)

## 🎯 Cele Edukacyjne

- Rozumieć tryby `chat`, `task`, `single_turn`
- Zbierać dane od użytkownika w sub-agencie i automatycznie wracać z wynikiem (`finish_task`)
- Zwracać ustrukturyzowany wynik przez `output_schema`

## 🚀 Szybki Start

```bash
cd adk_training
adk web
```

Wybierz `d1_10b_task_api` i przeprowadź rozmowę:
1. "Przygotuj statek, płyniemy do Nassau"
2. (Kwatermistrz zapyta o zapasy) "10 beczek rumu, 20 sucharów, 30 wody, 5 prochu"
3. "To wszystko"

## 🔑 Kluczowe Koncepcje

| mode | Rozmowa z użytkownikiem | Powrót do koordynatora |
|---|---|---|
| `chat` (domyślny) | pełna | ręcznie (`transfer_to_agent`) |
| `task` | tylko pytania doprecyzowujące | **automatycznie** po `finish_task` |
| `single_turn` | brak | **automatycznie**, z wynikiem; może działać równolegle |

```python
kwatermistrz = Agent(name="kwatermistrz", mode="task", output_schema=ListaZapasow, ...)
nawigator    = Agent(name="nawigator", mode="single_turn", tools=[sprawdz_pogode], ...)

root_agent = Agent(
    name="kapitan_portu",                  # root BEZ mode
    sub_agents=[kwatermistrz, nawigator],  # ADK dodaje narzędzia: kwatermistrz(), nawigator()
    tools=[zaladuj_statek],
)
```

Przebieg w **Events**:
`kapitan_portu → nawigator (single_turn, wraca od razu) → kwatermistrz (task, pyta usera) → finish_task → kapitan_portu → zaladuj_statek`

**Ograniczenia:** agent w trybie `task` musi być liściem (bez własnych `sub_agents`);
root agent nie ustawia `mode`.

**Pułapka (flash-lite):** bez `disallow_transfer_to_parent=True` /
`disallow_transfer_to_peers=True` lżejszy model potrafi zapętlić się na
`transfer_to_agent` zamiast wywołać `finish_task`. Dlatego kwatermistrz ma
transfer zablokowany, a instrukcja wprost nazywa `finish_task`.

### Porównanie z `d1_10a` (router)

W `d1_10a` sub-agent przejmował rozmowę i trzeba było pilnować, kiedy odda
kontrolę. W trybie `task` powrót jest automatyczny i niesie ustrukturyzowany wynik.

## 🏋️ Ćwiczenia

- **33.1** – `skarbnik` (`single_turn`) z narzędziem `wycen_zapasy`, koszt przed załadunkiem.
- **33.2** – obserwacja trybów w Events; zmień nawigatorowi `mode` na `"task"` i porównaj.
- **33.3** – usuń blokadę transferu z kwatermistrza, uruchom na lite i zobacz pętlę `transfer_to_agent`.

## 📖 Dokumentacja

- https://adk.dev/workflows/collaboration/
