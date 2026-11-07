# Bonus A01: Image Studio — narzędzia, ToolContext i wersjonowane artefakty

## Czego się nauczysz?

- Jak pisać **narzędzia (function tools)** z typowanymi parametrami (`Literal`, `Optional`) –
  ADK generuje z nich schemat dla LLM.
- Jak narzędzie korzysta z **`ToolContext`** do zapisu i odczytu **artefaktów**
  (`save_artifact`, `load_artifact`, `get_artifact_version`).
- **Wersjonowanie artefaktów** – każdy zapis pod tą samą nazwą tworzy nową wersję (v0, v1, ...).
- **Zakres artefaktów**: prefiks `user:` = plik widoczny we wszystkich sesjach użytkownika.
- Wbudowane narzędzie **`load_artifacts`** – pozwala modelowi *zobaczyć* zapisany obraz.

## Przypadki biznesowe

- **Marketing** – szybkie warianty grafik do kampanii („wersja na Instagram 9:16”, „to samo, ale nocą”).
- **E-commerce** – zdjęcia produktowe w różnych aranżacjach z historią zmian.
- **Prototypowanie UI / storyboard** – iteracyjne poprawki z możliwością powrotu do wcześniejszej wersji.

## Architektura

```
User ──► image_studio (gemini-3.5-flash)
            │
            ├─ generate_image(prompt, filename, aspect_ratio) ──► gemini-2.5-flash-image
            │        └─ tool_context.save_artifact("user:logo.png")         → v0
            ├─ edit_image(instruction, filename, source_version?)
            │        ├─ tool_context.load_artifact("user:logo.png", version) → obraz źródłowy
            │        └─ tool_context.save_artifact(...)                      → v1, v2, ...
            ├─ list_images() ── list_artifacts() + get_artifact_version()  (tylko metadane)
            └─ load_artifacts  (wbudowane – model ogląda obraz)
```

> **Dlaczego nie Imagen?** Modele Imagen 3/4 nie są dostępne na endpoincie `global`
> (używanym w szkoleniu z `gemini-3.5-flash`). Model obrazowy Gemini („Nano Banana”)
> jest dostępny i dodatkowo umie **edytować** istniejący obraz – stąd `edit_image`.
> Model zmienisz zmienną `IMAGE_MODEL` w `.env`.

## Kluczowy kod ([agent.py](agent.py))

```python
response = await _genai_client().aio.models.generate_content(
    model=IMAGE_MODEL,
    contents=[prompt],                         # przy edycji: [obraz_źródłowy, instrukcja]
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
    ),
)
version = await tool_context.save_artifact("user:logo.png", image_part)
```

- Klient `genai.Client` ma **retry z backoffem** (`HttpRetryOptions`) – model obrazowy ma
  niską quotę i potrafi zwrócić `429`.
- Narzędzia zwracają `{"status": "error", ...}` zamiast rzucać wyjątek – LLM może wtedy
  wyjaśnić użytkownikowi, co poszło nie tak.

## Uruchomienie

```powershell
cd adk_training\pz_bonus
adk web .
```

Wybierz `a01_intro`. Scenariusz demo:

1. „Wygeneruj minimalistyczne logo robota czytającego książkę, kwadrat” → `user:robot_logo.png` v0
2. „Zrób robota niebieskiego” → v1
3. „Wróć do oryginału (v0) i dodaj czerwoną czapkę” → v2 (źródło: v0)
4. „Pokaż moje obrazy” → lista z wersjami
5. „Co jest na tym obrazku?” → model używa `load_artifacts`

**Co pokazać w UI:** zakładka **Artifacts** (przełączanie wersji), w Events – `artifact_delta`
przy wywołaniach narzędzi. Nowa sesja tego samego użytkownika nadal widzi obrazy (`user:`).

## Ćwiczenia

1. **Zakres sesji vs użytkownika** – usuń prefiks `user:` w `_artifact_name`. Utwórz nową
   sesję i sprawdź, czy obrazy nadal są widoczne. Kiedy który zakres ma sens?
2. **Guardrail na prompt** – dodaj `before_tool_callback`, który blokuje `generate_image`,
   gdy prompt zawiera słowa z czarnej listy (zwróć `dict` z błędem zamiast wywołania modelu).
3. **Metadane** – przekaż `custom_metadata={"prompt": prompt}` do `save_artifact` i pokaż
   prompt w wyniku `list_images` (`get_artifact_version(...).custom_metadata`).
4. **Trwałość** – uruchom `adk web . --artifact_service_uri=gs://<bucket>` i sprawdź, że
   artefakty przeżywają restart serwera.

## Troubleshooting

| Problem | Rozwiązanie |
|---|---|
| `404 ... model not found` | Model obrazowy niedostępny w regionie/projekcie – ustaw `IMAGE_MODEL` na dostępny (np. `gemini-2.5-flash-image`). |
| `429 RESOURCE_EXHAUSTED` | Quota modelu obrazowego. Retry jest wbudowany; na szkoleniu z wieloma uczestnikami poproś o zwiększenie quoty albo generujcie na zmianę. |
| Obraz nie pojawia się w Artifacts | Sprawdź, czy narzędzie zwróciło `status: success`; odśwież widok sesji. |

## Odnośniki

- [ADK – Artifacts](https://google.github.io/adk-docs/artifacts/)
- [ADK – Function tools / ToolContext](https://google.github.io/adk-docs/tools-custom/function-tools/)
- [Gemini – image generation](https://ai.google.dev/gemini-api/docs/image-generation)
