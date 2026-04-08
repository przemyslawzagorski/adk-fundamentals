# TDD i Debugging z Copilot

## 🎯 Cele Szkolenia
-   Zrozumienie, jak GitHub Copilot może wspierać proces Test-Driven Development (TDD).
-   Nabycie umiejętności wykorzystania Copilota do generowania testów jednostkowych i integracyjnych.
-   Poznanie technik pisania kodu spełniającego testy z aktywnym udziałem Copilota.
-   Opanowanie strategii refaktoringu istniejącego kodu i testów za pomocą Copilota.
-   Wykorzystanie Copilota jako narzędzia wspomagającego debugowanie i analizę błędów.
-   Umiejętność interpretacji komunikatów o błędach i generowania sugestii poprawek przez Copilota.
-   Zrozumienie, jak Copilot może pomagać w analizie kodu i stanu aplikacji podczas procesu debugowania.

## 📚 Teoria

### Wsparcie dla Test-Driven Development (TDD) z GitHub Copilot

Test-Driven Development (TDD) to metodyka programowania, w której testy jednostkowe są pisane przed kodem implementującym funkcjonalność (cykl Red-Green-Refactor). GitHub Copilot może znacznie przyspieszyć i ułatwić każdy z tych etapów.

#### Generowanie testów jednostkowych i integracyjnych
Copilot doskonale radzi sobie z generowaniem szablonów testów, a nawet całych scenariuszy testowych, bazując na nazwie metody, interfejsie lub komentarzu opisującym intencję.
**Przykład:** Wystarczy napisać komentarz `// Generate a unit test for 'saveOwner' method`, a Copilot zaproponuje strukturę testu wraz z mockami i asercjami. Jest to przydatne zarówno przy testach jednostkowych, jak i integracyjnych wymagających konfiguracji kontekstu.

#### Pisanie kodu pod testy z pomocą Copilota
Po stworzeniu nieprzechodzącego testu (RED), celem jest napisanie kodu, który go przejdzie (GREEN). Copilot, mając kontekst testu i definicji klas, może sugerować implementacje. Jeśli test jest dobrze napisany, Copilot może wygenerować trafne fragmenty kodu.
**Wskazówka:** Po dodaniu sygnatury metody, otwórz klamrę `{`, a Copilot zacznie sugerować implementację, bazując na nazwie metody, parametrach i dostępnych testach.

#### Refaktoring istniejącego kodu i testów
Faza refaktoryzacji jest kluczowa. Copilot Chat może być niezwykle pomocny. Możesz zaznaczyć fragment kodu lub test i poprosić Copilota o:
-   "Zrefaktoryzuj ten kod, aby był bardziej czytelny i efektywny."
-   "Upraszczaj ten test, usuwając duplikaty i poprawiając asercje."
Copilot może sugerować zmiany w strukturze, nazewnictwie czy optymalizację algorytmów, dbając o zachowanie funkcjonalności.

### Debugowanie z GitHub Copilot

Debugowanie to proces znajdowania i usuwania błędów. Copilot może dostarczyć cenne wsparcie, przyspieszając diagnostykę i proponując rozwiązania.

#### Analiza błędów i sugerowanie poprawek
Gdy napotkasz błąd (w logach, w trakcie działania), Copilot może pomóc go zrozumieć.
**Przykład:** Skopiuj cały stack trace `NullPointerException` do Copilot Chatu i poproś: "Zanalizuj ten stack trace i zaproponuj możliwe przyczyny oraz potencjalne rozwiązania." Copilot wskaże miejsca, gdzie błąd mógł wystąpić, i zasugeruje naprawy (np. dodanie sprawdzenia `null`, inicjalizację).

#### Interpretacja stack trace\'ów
Stack trace to zapis wywołań funkcji. Copilot może pomóc w interpretacji:
-   Wskazując konkretne linie kodu w Twoim projekcie.
-   Wyjaśniając, co oznaczają poszczególne ramki wywołań.
-   Proponując, od którego punktu zacząć analizę.
To pozwala szybko zlokalizować problematyczny fragment kodu.

#### Wykorzystanie Copilota w analizie kodu i stanu podczas debugowania
Podczas debugowania często trzeba zrozumieć, dlaczego zmienna ma określoną wartość lub jak działa skomplikowana funkcja. Copilot może w tym pomóc:
-   **Analiza zmiennych:** Zaznacz fragment kodu z problematyczną zmienną i zapytaj Copilota: "Dlaczego zmienna X ma taką wartość w tym punkcie? Jakie operacje wpływają na jej stan?"
-   **Zrozumienie przepływu:** Poproś Copilota o wyjaśnienie logiki skomplikowanej funkcji, która jest wykonywana w trakcie debugowania.
-   **Wsparcie przy analizie zmian:** Copilot może pomóc zinterpretować różnice w kodzie (`git diff`) i ich potencjalny wpływ na błąd, zwłaszcza po cofnięciu zmian.

## 💡 Przykłady Użycia

### Przykład 1: Generowanie testu i implementacja metody TDD
Dodajemy funkcjonalność do `VisitService`, która zwraca listę wizyt dla zwierzaka w zakresie dat.
1.  **Stwórz test (RED):** W `VisitServiceTests.java` napisz komentarz `// Given a pet and a date range, should return all visits within that range` i pozwól Copilotowi wygenerować test (np. dla metody `findVisitsForPetInDateRange`). Test zawiedzie, bo metoda nie istnieje.
2.  **Zaimplementuj metodę (GREEN):** W `VisitService.java` dodaj sygnaturę metody i pozwól Copilotowi ją zaimplementować, używając `visitRepository`. Może być konieczne dodanie nowej metody do `VisitRepository`.
3.  **Refaktoryzacja:** Użyj Copilot Chatu, aby poprawić czytelność testu lub implementacji, jeśli potrzeba.

### Przykład 2: Debugowanie `NullPointerException` z Copilot Chat
Masz `NullPointerException` w logach, np. `java.lang.NullPointerException: Cannot invoke "org.springframework.samples.petclinic.model.Pet.getName()" because "pet" is null at OwnerController.java:180`.
1.  **Skopiuj Stack Trace:** Skopiuj cały stack trace.
2.  **Zapytaj Copilot Chat:** Wklej stack trace do Copilot Chatu i zadaj pytanie: "Zanalizuj ten stack trace. Jakie są możliwe przyczyny tego `NullPointerException` i jak mogę go naprawić w `OwnerController.java`?"
3.  **Przeanalizuj i zastosuj:** Copilot wskaże linię 180 i zasugeruje dodanie sprawdzenia `null` dla obiektu `pet` lub upewnienie się, że `pet` jest prawidłowo inicjalizowany. Zastosuj poprawkę.

## ✅ Best Practices
-   **Precyzyjne Prompty:** Formułuj jasne i konkretne pytania dla Copilota.
-   **Weryfikuj Sugestie:** Zawsze przeglądaj kod i testy generowane przez Copilota.
-   **Małe Krokami:** W TDD, generuj małe testy i odpowiadaj na nie minimalnym kodem.
-   **Kontekst dla Debugowania:** Dostarcz Copilotowi pełen kontekst błędu (stack trace, fragmenty kodu).
-   **Używaj Copilot Chat do Refaktoringu:** Jest efektywny do poprawy czytelności i struktury kodu.

## ⚠️ Common Pitfalls
-   **Ślepe Zaufanie:** Akceptowanie sugestii bez zrozumienia.
-   **Generowanie Zbyt Skomplikowanych Testów:** Copilot może generować złożone testy; dąż do prostoty.
-   **Brak Kontekstu:** Prośby bez odpowiedniego kontekstu mogą skutkować ogólnikowymi odpowiedziami.
-   **Przeciążenie Copilota:** Próba rozwiązania dużego problemu za jednym razem jest mniej efektywna.

## 🔗 Dodatkowe Zasoby
-   [Oficjalna dokumentacja GitHub Copilot](https://docs.github.com/en/copilot/overview)
-   [Wprowadzenie do Test-Driven Development](https://martinfowler.com/bliki/UnitTest.html)
-   [Dokumentacja Spring Petclinic](https://github.com/spring-projects/spring-petclinic)
