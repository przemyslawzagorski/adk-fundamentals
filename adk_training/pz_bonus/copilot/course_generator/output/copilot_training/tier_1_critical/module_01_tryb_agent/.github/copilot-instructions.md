# Instrukcje Użycia GitHub Copilot w Repozytorium spring-petclinic

Ten dokument zawiera wskazówki dotyczące efektywnego wykorzystania GitHub Copilot (w tym Copilot Chat) podczas pracy z repozytorium `spring-petclinic`. Celem jest maksymalizacja produktywności i utrzymanie spójności kodu.

## 🎯 Ogólne Zasady

1.  **Kontekst jest Kluczowy**: Zawsze upewnij się, że Copilot ma wystarczający kontekst. Otwieraj pliki, które są związane z Twoim zadaniem, lub jawnie wskazuj je w zapytaniach.
2.  **Weryfikuj Generowany Kod**: Copilot to narzędzie wspomagające, a nie zastępujące dewelopera. Zawsze dokładnie przeglądaj, testuj i weryfikuj sugerowany kod przed jego akceptacją.
3.  **Używaj Prompty w Języku Polskim**: Preferujemy interakcje z Copilotem w języku polskim, aby utrzymać spójność komunikacji w zespole i dokumentacji.
4.  **Bądź Precyzyjny**: Im bardziej szczegółowe i jasne jest Twoje zapytanie, tym trafniejsza będzie odpowiedź Copilota.

## 🧑‍💻 Agenci Copilot - Kiedy i Jak Używać

Poniżej przedstawiamy scenariusze użycia dla poszczególnych agentów:

### `@workspace`
*   **Kiedy używać**: Do pytań o architekturę projektu, lokalizowanie plików, zrozumienie zależności, wyszukiwanie implementacji interfejsów w całym repozytorium.
*   **Przykłady**:
    *   `@workspace Jakie kontrolery Spring są zdefiniowane w tym projekcie?`
    *   `@workspace Gdzie jest zdefiniowany interfejs `OwnerRepository` i kto go używa?`
    *   `@workspace Jaka jest konfiguracja bazy danych dla profilu testowego?`

### `@vscode`
*   **Kiedy używać**: Do pytań i komend dotyczących samego Visual Studio Code, jego funkcji, skrótów klawiszowych, rozszerzeń czy konfiguracji.
*   **Przykłady**:
    *   `@vscode Jak mogę szybko przejść do definicji metody w VS Code?`
    *   `@vscode Skonfiguruj automatyczne formatowanie kodu Java przy zapisie pliku.`
    *   `@vscode Otwórz panel z problemami w projekcie.`

### `@terminal`
*   **Kiedy używać**: Do wykonywania komend CLI (Maven, Git, skrypty) w kontekście projektu. Pamiętaj, że zmiany wykonane przez `@terminal` są trwałe.
*   **Przykłady**:
    *   `@terminal Zbuduj projekt Maven i uruchom testy.`
    *   `@terminal Pokaż status Git dla bieżącego repozytorium.`
    *   `@terminal Uruchom aplikację Spring Boot w trybie deweloperskim.`

### `@search`
*   **Kiedy używać**: Gdy potrzebujesz informacji spoza kontekstu projektu – dokumentacji zewnętrznej, rozwiązań problemów, przykładów użycia bibliotek, najlepszych praktyk dla Springa czy Javy.
*   **Przykłady**:
    *   `@search Jakie są najlepsze praktyki dla zabezpieczania REST API w Spring Boot?`
    *   `@search Wyjaśnij wzorzec projektowy Builder w Javie.`
    *   `@search Jakie są różnice między Spring Data JPA a Hibernate?`

### `@agent` (lub domyślny Copilot)
*   **Kiedy używać**: Do generowania kodu, refaktoryzacji, pisania testów, dokumentowania, wyjaśniania złożonej logiki. Jest to "dyrygent", który może używać innych agentów.
*   **Przykłady**:
    *   `@agent Zrefaktoryzuj tę metodę, aby była bardziej czytelna.` (po zaznaczeniu metody)
    *   `@agent Napisz test jednostkowy dla klasy `OwnerController` używając MockMvc.`
    *   `@agent Wygeneruj dokumentację Javadoc dla tej klasy.` (po otwarciu klasy)

## ✍️ Wskazówki dotyczące Pisania Promptów

*   **Język Naturalny**: Pisz tak, jakbyś rozmawiał z innym deweloperem.
*   **Rola i Cel**: Jasno określ swoją rolę (np. "Jako deweloper chcę...") i cel (np. "...aby dodać nową funkcjonalność...").
*   **Kontekst**: Odwołuj się do konkretnych plików, metod, linii kodu.
*   **Format Wyniku**: Określ, jakiej formy oczekujesz (np. "pokaż mi kod", "wygeneruj tylko plan", "podsumuj w punktach").
*   **Iteracja**: Jeśli pierwsza odpowiedź nie jest satysfakcjonująca, popraw prompt lub poproś o modyfikacje (np. "To jest dobre, ale czy możesz to zrobić bez...").

## ⚠️ Co Należy Unikać

*   **Zbyt Ogólne Pytania**: Unikaj pytań typu "Co mam teraz zrobić?".
*   **Ślepe Kopiowanie**: Nigdy nie wklejaj kodu generowanego przez Copilota bez zrozumienia jego działania i konsekwencji.
*   **Nieweryfikowalne Zmiany**: Zawsze upewnij się, że generowane zmiany są przetestowane i nie wprowadzają regresji.

Wszelkie sugestie dotyczące ulepszenia tych instrukcji są mile widziane.
