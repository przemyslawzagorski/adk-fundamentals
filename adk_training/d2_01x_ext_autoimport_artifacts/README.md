# EXT (po D2.1): Automatyczny import plików do Artifact Service — `SaveFilesAsArtifactsPlugin`

## Czego się nauczysz?

- Czym są **pluginy** w ADK i czym różnią się od callbacków agenta
  (plugin rejestrujemy raz na **`App`** – działa globalnie dla wszystkich agentów i narzędzi).
- Jak wbudowany **`SaveFilesAsArtifactsPlugin`** zamienia pliki wrzucone przez użytkownika
  na **artefakty**, zamiast trzymać ich bajty w historii rozmowy.
- Jak agent „ogląda” plik dopiero wtedy, gdy potrzebuje – narzędzie **`load_artifacts`**.

## Po co to?

Bez pluginu każdy wrzucony PDF/obraz siedzi w historii sesji i jest wysyłany do modelu
**w każdej kolejnej turze** (koszt tokenów, limity kontekstu). Z pluginem:

```
User wrzuca raport.pdf
  → plugin (on_user_message_callback): save_artifact("raport.pdf")      → v0
  → wiadomość w historii: [Uploaded Artifact: "raport.pdf"]             (tekst zamiast bajtów)
  → agent wywołuje load_artifacts tylko gdy pyta o treść pliku
```

Przypadki biznesowe: analiza faktur/umów, porównywanie wersji dokumentów, asystent HR
czytający CV, support z zrzutami ekranu.

## Kod ([agent.py](agent.py))

```python
root_agent = Agent(name="file_assistant", model=MODEL, instruction=..., tools=[load_artifacts])

app = App(
    name="d2_01x_ext_autoimport_artifacts",
    root_agent=root_agent,
    plugins=[SaveFilesAsArtifactsPlugin()],
)
```

`adk web` znajduje zmienną `app` (ma pierwszeństwo przed `root_agent`), więc plugin działa
automatycznie.

Szczegóły pluginu (ADK 2.x):

| Zachowanie | Wartość |
|---|---|
| Nazwa artefaktu | `display_name` pliku, a gdy brak – `artifact_<invocation_id>_<i>` |
| Zakres | artefakt **sesyjny** (bez prefiksu `user:`) |
| Limit | plik > 20 MB nie jest zapisywany – model dostaje tekst `[Upload Error: ...]` |
| Co trafia do modelu | `[Uploaded Artifact: "<nazwa>"]` (+ `file_data`, jeśli URI to `gs://` / `http(s)://`) |

## Uruchomienie

```powershell
cd adk_training
adk web
```

Wybierz `d2_01x_ext_autoimport_artifacts`, wrzuć spinaczem obrazek lub PDF i zapytaj
„Co jest w tym pliku?”.

**Co pokazać w UI:** zakładka **Artifacts** (plik pojawia się od razu po wysłaniu),
w Events wiadomość użytkownika zawiera tylko placeholder tekstowy, a model woła `load_artifacts`.

## Ćwiczenia

Rozwiązania: [agent_solution.py](agent_solution.py). Aby uruchomić rozwiązanie w `adk web`,
zmień [\_\_init\_\_.py](__init__.py) na `from .agent_solution import app`.

1. **Lista plików z metadanymi** – narzędzie `list_files`, które zwraca nazwę, wersję,
   typ MIME i datę (przez `tool_context.get_artifact_version`), **bez** ładowania bajtów.
2. **Filtrowanie** – parametr `kind: Literal["image", "pdf", "text", "all"]`.
   Zauważ, jak `Literal` zamienia się w `enum` w schemacie narzędzia.
3. **Automatyczna analiza** – po każdym uploadzie agent sam wywołuje `analyze_file`,
   które wysyła plik do Gemini i zapisuje streszczenie jako nowy artefakt
   `<nazwa>.summary.md` (`text/markdown`, z `custom_metadata`).
4. *(dodatkowe)* Napisz **własny plugin** (`BasePlugin`), który loguje nazwę i rozmiar każdego
   wrzuconego pliku w `on_user_message_callback` i odrzuca pliki inne niż PDF/obrazy.

## Troubleshooting

| Problem | Rozwiązanie |
|---|---|
| Plugin nie działa | Plugin musi być na `App`, a moduł musi eksportować `app` (sprawdź `__init__.py`). |
| Ostrzeżenie o niezgodnej nazwie aplikacji | `App(name=...)` powinno być równe nazwie folderu. |
| Model „nie widzi” pliku | Instrukcja musi kazać użyć `load_artifacts`; sam placeholder nie zawiera treści. |

## Odnośniki

- [ADK – Plugins](https://google.github.io/adk-docs/plugins/)
- [ADK – Artifacts](https://google.github.io/adk-docs/artifacts/)
