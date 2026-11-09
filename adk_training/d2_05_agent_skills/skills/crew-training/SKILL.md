---
name: crew-training
description: >
  Program szkoleniowy dla załogi pirackiej. Obejmuje rekrutację, trening bojowy,
  nawigację, etykietę morską i awanse. Używaj tego skilla gdy pytanie dotyczy
  szkolenia nowych członków załogi, programów treningowych lub rozwoju umiejętności.
---

# Program Szkoleniowy Załogi

Ten skill pochodzi z "biblioteki umiejętności pirackiej floty" — symuluje zewnętrzny
skill pobrany z repozytorium społeczności (wzorzec external skill).

## Gdy użytkownik pyta o szkolenie załogi:

### Faza 1: Ocena rekruta
Zbierz informacje o nowym członku załogi:
- Doświadczenie morskie (brak / podstawowe / zaawansowane)
- Specjalizacja (żeglarz / artylerysta / nawigator / kucharz / medyk)
- Kondycja fizyczna (zdolny / ograniczenia)

### Faza 2: Załaduj program treningowy
Użyj `load_skill_resource` aby pobrać `references/training-procedures.md` —
zawiera szczegółowe programy szkoleniowe dla każdej specjalizacji.

### Faza 3: Stwórz plan szkolenia
Na podstawie oceny i programu:
1. Dobierz odpowiedni track szkoleniowy
2. Ustal czas trwania (2-8 tygodni)
3. Wyznacz mentora z załogi
4. Określ kryteria egzaminu końcowego

### Faza 4: Monitorowanie postępów
Zaproponuj system oceny:
- **Tydzień 1-2**: Podstawy (węzły, terminologia, hierarchia)
- **Tydzień 3-4**: Specjalizacja (praktyka na stanowisku)
- **Tydzień 5-6**: Symulacje (ćwiczenia bojowe / nawigacyjne)
- **Tydzień 7-8**: Egzamin i certyfikacja

## Zasady awansów
- Rekrut → Marynarz: Po zdaniu egzaminu podstawowego
- Marynarz → Starszy Marynarz: 6 miesięcy bez wpadek + rekomendacja
- Starszy Marynarz → Oficer: Udowodniona inicjatywa + głosowanie załogi
