---
name: ship-maintenance
description: >
  Procedury konserwacji i naprawy statku pirackiego. Obejmuje inspekcję kadłuba,
  masztów, żagli, lin, dziobownicy i ładowni. Używaj tego skilla gdy pytanie dotyczy
  stanu technicznego statku, napraw, drewna, smoły lub harmonogramu przeglądów.
---

# Procedury Konserwacji Statku

Gdy użytkownik pyta o konserwację lub naprawę statku, postępuj według kroków:

## Krok 1: Identyfikacja obszaru
Określ, którego elementu statku dotyczy pytanie:
- **Kadłub** — podwodna część, uszczelnienia, barnacle (małże)
- **Pokład** — deski pokładowe, luki, reling
- **Maszty i żagle** — takielunek, liny, płótno żagli
- **Ładownia** — szczelność, wentylacja, ochrona ładunku

## Krok 2: Załaduj szczegółową checklistę
Użyj `load_skill_resource` aby pobrać `references/maintenance-checklist.md` —
zawiera szczegółowe procedury inspekcji dla każdego elementu.

## Krok 3: Diagnoza i rekomendacja
Na podstawie opisu problemu:
1. Zidentyfikuj możliwą przyczynę
2. Określ pilność (krytyczna / ważna / rutynowa)
3. Zaproponuj konkretne kroki naprawy
4. Oszacuj potrzebne materiały (deski, smoła, liny, płótno)

## Krok 4: Harmonogram
Zaproponuj harmonogram przeglądów:
- **Codziennie**: Sprawdzenie lin i takielunku
- **Co tydzień**: Inspekcja pokładu i ładowni
- **Co miesiąc**: Pełna inspekcja kadłuba (w porcie)
- **Co pół roku**: Karenowanie (wyciągnięcie na brzeg, czyszczenie dna)
