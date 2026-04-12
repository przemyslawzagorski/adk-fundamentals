# Moduł 4: Sekwencyjny Pipeline Wieloagentowy

## 🎯 Cele Edukacyjne

Po ukończeniu tego modułu będziesz rozumieć:
- Jak `SequentialAgent` orkiestruje wielu agentów
- Wzorzec `output_key` do przekazywania danych między agentami
- Jak uzyskać dostęp do wyników poprzednich agentów używając składni `{key_name}`
- Budowanie wieloetapowych przepływów pracy z automatycznym przepływem danych

## 💡 Koncepcja: Pipeline Planowania

```
Zapytanie → [Zwiadowca] → [Strateg] → [Kapitan] → Finalna Decyzja
                ↓              ↓            ↓
           raport_wywiadu  plan_bitwy  decyzja_kapitana
              (stan)         (stan)        (stan)
```

## 🔑 Kluczowe Wzorce

### 1. Output Key - Przechowywanie Wyników Agenta
```python
zwiadowca = LlmAgent(
    name="zwiadowca",
    instruction="Zbierz wywiad...",
    output_key="raport_wywiadu"  # Wynik przechowywany w stanie sesji
)
```

### 2. Dostęp do Stanu - Odczytywanie Poprzednich Wyników
```python
strateg = LlmAgent(
    name="strateg",
    instruction="Na podstawie tego wywiadu: {raport_wywiadu}",  # Odczyt ze stanu
    output_key="plan_bitwy"
)
```

### 3. Orkiestracja Sekwencyjna
```python
pipeline = SequentialAgent(
    name="pipeline_planowania",
    sub_agents=[zwiadowca, strateg, kapitan]  # Uruchamiane po kolei
)
```

## 🚀 Konfiguracja

1. **Skopiuj szablon środowiska:**
   ```bash
   cp .env.template .env
   ```

2. **Edytuj `.env` ze swoim projektem GCP:**
   ```
   GOOGLE_CLOUD_PROJECT=twoj-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

3. **Uwierzytelnij się:**
   ```bash
   gcloud auth application-default login
   ```

## ▶️ Uruchomienie Agenta

```bash
cd adk_training/module_04_sequential_agent
adk web
```

Następnie otwórz http://localhost:8000 i wypróbuj:
- "Zaplanuj operację w lokalizacji X"
- "Wykryliśmy nowy cel - oceń i zaplanuj"
- "Potrzebujemy strategii dla projektu Y"

## 🔄 Jak To Działa

1. **Agent Zwiadowca** otrzymuje zapytanie, zbiera "wywiad"
2. Wynik Zwiadowcy jest przechowywany w stanie jako `raport_wywiadu`
3. **Agent Strateg** odczytuje `{raport_wywiadu}` i tworzy plan
4. Wynik Stratega jest przechowywany jako `plan_bitwy`
5. **Agent Kapitan** odczytuje oba i podejmuje finalną decyzję
6. Wszystkie trzy odpowiedzi są widoczne w konwersacji

## 🏋️ Ćwiczenia

### Ćwiczenie 1: Dodaj Czwartego Agenta
Dodaj agenta "Kwatermistrz" między Strategiem a Kapitanem, który:
- Odczytuje plan_bitwy
- Ocenia potrzeby zasobowe i sprzętowe
- Przechowuje wynik jako "ocena_zasobow"
- Kapitan powinien również przejrzeć tę ocenę

### Ćwiczenie 2: Modyfikacja Przepływu Danych
Zmień Kapitana aby również uwzględniał:
- Morale zespołu (dodaj do obowiązków Zwiadowcy)
- Warunki środowiskowe (dodaj do wywiadu Zwiadowcy)

### Ćwiczenie 3: Obsługa Błędów
Co się stanie jeśli Zwiadowca dostarczy wywiad o niskiej pewności (ocena < 5)?
Zmodyfikuj instrukcje Kapitana aby automatycznie odrzucał plany o niskiej pewności.

## ❓ Częste Problemy

**Problem:** Agent nie widzi poprzedniego wyniku
**Rozwiązanie:** Sprawdź czy `output_key` dokładnie pasuje do `{key_name}`

**Problem:** Widoczna tylko odpowiedź ostatniego agenta
**Rozwiązanie:** To oczekiwane zachowanie - sprawdź stan sesji dla wyników pośrednich

## 📝 Kluczowe Wnioski

1. `SequentialAgent` uruchamia agentów po kolei automatycznie
2. `output_key` przechowuje wynik agenta w stanie sesji
3. Użyj `{key_name}` w instrukcjach aby odczytać ze stanu
4. Każdy agent widzi wszystkie poprzednie wyniki przez stan
5. Świetne do: badanie→analiza→podsumowanie pipeline'ów

