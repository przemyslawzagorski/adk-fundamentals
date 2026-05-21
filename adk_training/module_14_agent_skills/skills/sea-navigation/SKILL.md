---
name: sea-navigation
description: >
  Nawigacja astronomiczna — wyznaczanie pozycji statku na morzu
  za pomocą obserwacji ciał niebieskich. Obejmuje: identyfikację gwiazd
  nawigacyjnych, pomiar wysokości sekstantem, obliczanie szerokości
  i długości geograficznej, tablice nautyczne, wyznaczanie kursu.
  Używaj gdy pytanie dotyczy nawigacji, pozycji, kursu, gwiazd,
  sekstantu lub map morskich.
---

# Nawigacja Astronomiczna

## Kiedy używać tego skilla
- Pytania o wyznaczanie pozycji na morzu
- Identyfikacja gwiazd nawigacyjnych
- Użycie sekstantu
- Obliczanie kursu i odległości
- Praca z mapami i tablicami nautycznymi

## Krok 1: Identyfikacja gwiazdy nawigacyjnej
Załaduj `references/star-charts.md` — tabela 15 najważniejszych gwiazd nawigacyjnych
z ich deklinacją, gwiazdozbiorem i porą roku widoczności.

Wybierz gwiazdę na podstawie:
- Pory roku (nie wszystkie gwiazdy widoczne cały rok)
- Półkuli (N/S)
- Warunków pogodowych (jasność gwiazdy)

## Krok 2: Pomiar sekstantem
1. Ustaw sekstant na linię horyzontu
2. Nakieruj na wybraną gwiazdę
3. Odczytaj kąt wysokości (altitude) z dokładnością do 0.1'
4. Zanotuj dokładny czas pomiaru (chronometr pokładowy)

## Krok 3: Obliczenie pozycji
1. **Szerokość geograficzna** (z Polaris — tylko półkula N):
   - Zmierz wysokość Polaris nad horyzontem
   - Szerokość ≈ Wysokość Polaris ± korekta (max ±1°)

2. **Długość geograficzna** (metoda lunarna lub chronometrowa):
   - Zanotuj czas lokalnego południa słonecznego
   - Porównaj z czasem Greenwich (chronometr)
   - Różnica × 15° = długość geograficzna

3. **Metoda dwóch gwiazd** (dokładniejsza):
   - Zmierz wysokość dwóch gwiazd w krótkim odstępie czasu
   - Oblicz linie pozycyjne (LOP) dla każdej
   - Przecięcie LOP = pozycja fix

## Krok 4: Wyznaczanie kursu
1. Na mapie zaznacz pozycję aktualną i docelową
2. Zmierz kąt kursu (bearing) od północy
3. Uwzględnij:
   - Deklinację magnetyczną (variation)
   - Dewiację kompasu (deviation)
   - Prądy morskie (drift)
4. Kurs rzeczywisty = Kurs kompasowy + Variation + Deviation

## Ważne formuły
- **Odległość** (w milach morskich): 1° szerokości = 60 Mm
- **Prędkość**: 1 węzeł = 1 Mm/h
- **ETA**: Odległość / Prędkość = Czas podróży
