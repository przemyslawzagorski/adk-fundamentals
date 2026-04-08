# GitHub Copilot Masterclass - Moduł 2: Nawigacja i Konteksty (Banking / Financial Services)

## Opis Modułu

Ten moduł koncentruje się na zaawansowanych funkcjonalnościach bankowych i finansowych, takich jak zarządzanie kontami, przetwarzanie transakcji, wykrywanie oszustw oraz ocena ryzyka. Służy jako praktyczne ćwiczenie w wykorzystaniu GitHub Copilot do nawigacji po złożonym kodzie, zrozumienia kontekstu biznesowego i implementacji zaawansowanych wzorców.

## Cel Nauki (dla uczestników Masterclass)

*   **Zrozumienie kontekstu biznesowego:** Jak GitHub Copilot może pomóc w szybkim zrozumieniu domen bankowych i finansowych.
*   **Nawigacja w złożonych systemach:** Efektywne używanie Copilota do poruszania się po architekturze mikroserwisowej i zależnościach.
*   **Zaawansowane refaktoryzacje:** Wykorzystanie Copilot Agent Mode do wielofajlowych operacji refaktoryzacyjnych.
*   **Self-correction loops:** Implementacja mechanizmów autokorekty z użyciem sugestii Copilota.
*   **@workspace context:** Optymalne wykorzystanie kontekstu całego projektu dla lepszych sugestii.

## Struktura Projektu (Spring Boot)

Projekt jest zbudowany w oparciu o Spring Boot i zawiera następujące kluczowe komponenty:

*   `AccountService.java`: Serwis odpowiedzialny za podstawowe operacje na kontach bankowych (tworzenie, depozyty, wypłaty).
*   `TransactionProcessor.java`: Obsługuje złożone transakcje finansowe, takie jak przelewy, zapewniając ich atomowość.
*   `FraudDetectionService.java`: Serwis do wykrywania potencjalnych oszustw w czasie rzeczywistym, wykorzystujący heurystyki i symulowane modele ML.
*   `RiskAssessmentEngine.java`: Silnik oceny ryzyka dla wniosków kredytowych i nowych produktów finansowych.
*   `BankingApplication.java`: Główna klasa startowa aplikacji Spring Boot.

## Jak korzystać z GitHub Copilot w tym module

Każdy plik zawiera komentarze `TODO:` specyficzne dla GitHub Copilot, które wskazują miejsca, gdzie można zastosować zaawansowane funkcje Copilota. Zachęcamy do:

1.  **Rozwiązywania TODO:** Używaj Copilota do implementacji brakujących fragmentów kodu.
2.  **Trybu Agenta (Agent Mode):** Eksperymentuj z trybem Agenta do zadań wymagających zmian w wielu plikach (np. refaktoryzacja bazy danych, dodawanie telemetrii).
3.  **Kontekstu @workspace:** Zwróć uwagę, jak sugestie Copilota zmieniają się po dodaniu lub edycji kodu w innych plikach, wykorzystując kontekst całego projektu.
4.  **Pętli autokorekty:** Świadomie wprowadzaj poprawki i obserwuj, jak Copilot adaptuje swoje sugestie, ucząc się z Twojego feedbacku.

## Uruchamianie Aplikacji

Projekt można uruchomić jako standardową aplikację Spring Boot. Wymaga Java 17+.

```bash
./mvnw spring-boot:run
```

---