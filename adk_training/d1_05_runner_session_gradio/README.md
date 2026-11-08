# D1.5: Stan sesji we własnym UI (Gradio + ADK Runner)

## Czego się nauczysz?

- Jak uruchomić agenta **bez `adk web`**: ręcznie skonfigurowany `Runner` + `SessionService`.
- **Sesja per użytkownik i per karta przeglądarki** (`gr.State`) zamiast jednej globalnej sesji.
- **Zakresy stanu** (prefiks klucza decyduje, gdzie ADK go trzyma):

| Klucz | Zakres | Kto ustawia |
|---|---|---|
| `user:profile` | wszystkie sesje danego `user_id` | UI przy `create_session(state=...)` |
| `user:preferences` | wszystkie sesje danego `user_id` | narzędzie `remember_preference` (`tool_context.state`) |
| `now` | bieżąca sesja | `before_agent_callback` przed każdą turą |
| `app:...` / `temp:...` | cała aplikacja / tylko bieżące wywołanie | (ćwiczenie) |

- **Szablony instrukcji**: `{user:profile}`, `{now}`, `{user:preferences?}` są podstawiane
  ze stanu w każdej turze; `?` oznacza zmienną opcjonalną (bez `?` brak klucza = błąd).

## Pliki

- [agent.py](agent.py) – agent `personal_assistant`, callback `refresh_context`,
  narzędzie `remember_preference`. Działa też w `adk web` (bez UI dostaje profil `Guest`).
- [ui.py](ui.py) – Gradio: wybór użytkownika, czat, przycisk **New session**,
  podgląd `session.state` na żywo. Dane użytkowników są **fikcyjne**.

## Uruchomienie

```powershell
cd adk_training\d1_05_runner_session_gradio
python ui.py
```

Otwórz http://127.0.0.1:7860 (wymaga `gradio` w venv i `.env` w katalogu modułu albo w `adk_training/`).

Agent bez własnego UI: `cd adk_training; adk web` → `d1_05_runner_session_gradio`.

## Scenariusz demo

1. Użytkownik **anna** → „Co o mnie wiesz?” → agent zna profil z `user:profile`.
2. „Zapamiętaj, że wolę krótkie odpowiedzi w punktach.” → w panelu stanu pojawia się
   `user:preferences`.
3. **New session** → nowa sesja ma pusty czat, ale `user:preferences` nadal jest w stanie
   (zakres `user:`), a agent odpowiada w punktach.
4. Przełącz na **john** → zupełnie inny profil, brak preferencji Anny.
5. „Która godzina?” → wartość z `now`, odświeżana callbackiem przy każdej turze.

## Ćwiczenia

1. **Trwałość** – zamień `InMemorySessionService` na
   `DatabaseSessionService(db_url="sqlite+aiosqlite:///./sessions.db")`, zrestartuj UI
   i sprawdź, że preferencje przetrwały.
2. **Licznik tur** – w `refresh_context` zwiększaj `state["turn_count"]`
   (zakres sesji) oraz `state["app:total_turns"]` (zakres aplikacji). Obserwuj różnicę między
   użytkownikami.
3. **Lista sesji** – dodaj dropdown z `session_service.list_sessions(app_name=..., user_id=...)`,
   który pozwala wrócić do starej rozmowy.
4. **Streaming** – wyświetlaj częściowe odpowiedzi (`RunConfig(streaming_mode=StreamingMode.SSE)`
   + generator w Gradio).

## Dobre praktyki pokazane w module

- `runner.run_async` (asynchronicznie) zamiast `runner.run` – synchroniczna wersja jest
  przeznaczona do lokalnych testów.
- Zmiany stanu tylko przez `callback_context.state` / `tool_context.state` (ADK zapisuje je
  jako `state_delta` w evencie) – nie modyfikuj `session.state` bezpośrednio.
- Żadnych prawdziwych danych osobowych w kodzie szkoleniowym.

## Odnośniki

- [ADK – Session state](https://google.github.io/adk-docs/sessions/state/)
- [ADK – Runtime / Runner](https://google.github.io/adk-docs/runtime/)
