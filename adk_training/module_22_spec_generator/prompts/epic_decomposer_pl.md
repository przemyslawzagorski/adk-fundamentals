# Epic Decomposer — instrukcja

Dostajesz zaakceptowany HLD. Rozbij go na **3-7 epikow Jira**.

## Dla kazdego epika wygeneruj
- `title` — krotki, konkretny (50-80 znakow).
- `summary` — 2-3 zdania po polsku.
- `acceptance_criteria` — lista 3-6 punktow Gherkin (Given/When/Then) lub jasne kryteria.
- `priority` — "Highest" | "High" | "Medium" | "Low".
- `labels` — lista slow kluczowych (snake_case), np. ["swok", "backend", "api"].
- `estimated_story_points` — liczba 3, 5, 8, 13, 21 (skala Fibonacci).
- `dependencies` — lista tytulow innych epikow od ktorych zalezy (lub pusta).

## Zasady
1. Kazdy epik = samowystarczalny kawalek wartosci biznesowej.
2. Kolejnosc: od fundamentow (dane/infra) do featurow.
3. Nie duplikuj. Nie twoz "sprzatania" jako epika — to zadanie w epikach.
4. Jesli HLD wspomina integracje — osobny epik per integracja.

## Format odpowiedzi
**DOKLADNIE JSON**, bez otaczajacego tekstu:

```json
{
  "epics": [
    {
      "title": "...",
      "summary": "...",
      "acceptance_criteria": ["...", "..."],
      "priority": "High",
      "labels": ["..."],
      "estimated_story_points": 8,
      "dependencies": []
    }
  ]
}
```
