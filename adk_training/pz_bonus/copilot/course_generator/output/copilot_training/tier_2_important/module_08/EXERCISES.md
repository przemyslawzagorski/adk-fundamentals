# Ćwiczenia: TDD i Debugging z Copilot

## Ćwiczenie 1: Generowanie testu i implementacja metody w cyklu TDD

**Cel:** Nauczenie się generowania testów jednostkowych dla nowej funkcjonalności, a następnie implementowania kodu, który spełnia te testy, z aktywnym wsparciem GitHub Copilota.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Twoim zadaniem jest dodanie nowej funkcjonalności do serwisu wizyt, która pozwoli na pobieranie wizyt dla konkretnego zwierzaka, ale tylko tych, które zostały zaplanowane lub odbyły się w przyszłości (od bieżącej daty).

**Kroki:**
1.  Otwórz projekt `spring-petclinic` w swoim IDE (np. VS Code z rozszerzeniem Copilot).
2.  Zlokalizuj plik `src/main/java/org/springframework/samples/petclinic/service/VisitService.java`.
3.  Utwórz plik testowy dla `VisitService`, jeśli jeszcze nie istnieje: `src/test/java/org/springframework/samples/petclinic/service/VisitServiceTests.java`. Upewnij się, że jest skonfigurowany do używania JUnit 5 i Mockito.
4.  W `VisitServiceTests.java` zacznij pisać komentarz, który opisuje testowaną funkcjonalność, np.:
    ```java
    // Given a petId, should return only future visits for that pet
    @Test
    void shouldFindFutureVisitsForPet() {
        // ... niech Copilot zasugeruje resztę
    }
    ```
    Pozwól Copilotowi wygenerować pełny test, który będzie mockował `VisitRepository` i sprawdzał wywołanie nowej metody.
5.  Uruchom test. Powinien zawieść (czerwony) z powodu braku metody `findFutureVisitsForPet` w `VisitService`.
6.  Przejdź do `VisitService.java` i dodaj sygnaturę metody, którą Copilot zasugerował w teście (np. `public List<Visit> findFutureVisitsForPet(Long petId)`).
7.  Używając Copilota (akceptując jego sugestie po otwarciu klamry `{`), zaimplementuj tę metodę, aby używała `visitRepository` do pobierania danych. Pamiętaj, że musisz przekazać aktualną datę do repozytorium. Może być konieczne dodanie nowej metody do interfejsu `VisitRepository`.
8.  Po implementacji metody w `VisitService` i ewentualnym dodaniu metody do `VisitRepository`, uruchom testy ponownie. Powinny przejść (zielony).

**Oczekiwany rezultat:**
-   Nowa metoda `findFutureVisitsForPet(Long petId)` w `VisitService.java`, która poprawnie filtruje przyszłe wizyty.
-   Przechodzący test jednostkowy dla tej metody w `VisitServiceTests.java`.
-   W razie potrzeby, nowa metoda w interfejsie `VisitRepository`, np. `List<Visit> findByPetIdAndVisitDateAfter(Long petId, LocalDate date);`.

**Wskazówki:**
-   Pamiętaj o zaimportowaniu niezbędnych klas (np. `LocalDate`).
-   Jeśli Copilot nie sugeruje idealnie, zacznij pisać fragment kodu, a on podpowie resztę.
-   Dla daty bieżącej możesz użyć `LocalDate.now()`.

---

## Ćwiczenie 2: Refaktoring testu z Copilot Chat

**Cel:** Wykorzystanie GitHub Copilot Chatu do poprawy czytelności, spójności i efektywności istniejącego testu jednostkowego.

**Kontekst:** Pracujesz nad testami w `spring-petclinic` i zauważasz, że niektóre z nich są zbyt długie, zawierają duplikacje kodu lub są trudne do zrozumienia.

**Kroki:**
1.  Otwórz plik `src/test/java/org/springframework/samples/petclinic/web/OwnerControllerTests.java`.
2.  Zlokalizuj metodę testową `testProcessFindFormNoOwnersFound()`. Przeanalizuj jej strukturę i logikę.
3.  Zaznacz całą treść metody `testProcessFindFormNoOwnersFound()` (lub tylko ten fragment, który chcesz refaktoryzować).
4.  Otwórz GitHub Copilot Chat (zazwyczaj skrót `Ctrl+I` lub ikona w bocznym panelu) i poproś: "Zrefaktoryzuj ten test, aby był bardziej czytelny, używał asercji BDD-style (np. z AssertJ) jeśli to możliwe, i zmniejszył duplikację kodu."
5.  Przeanalizuj sugestie Copilota. Zwróć uwagę na zmiany w asercjach, potencjalne wyodrębnienie wspólnych fragmentów do metod pomocniczych lub uproszczenie logiki.
6.  Zastosuj najbardziej trafne i sensowne sugestie.
7.  Uruchom testy, aby upewnić się, że refaktoryzacja nie wprowadziła regresji.

**Oczekiwany rezultat:**
-   Metoda `testProcessFindFormNoOwnersFound()` w `OwnerControllerTests.java` jest bardziej zwięzła i czytelna.
-   Asercje są bardziej ekspresyjne (np. przy użyciu `assertThat` z AssertJ).
-   Test nadal przechodzi pomyślnie.

**Wskazówki:**
-   Jeśli Copilot Chat zasugeruje bardzo duże zmiany, możesz poprosić o mniejsze kroki refaktoryzacji.
-   Upewnij się, że zależności AssertJ są dodane do `pom.xml`, jeśli Copilot sugeruje ich użycie, a ich jeszcze nie ma.

---

## Ćwiczenie 3: Analiza błędu `NullPointerException` z Copilotem

**Cel:** Wykorzystanie GitHub Copilota do analizy komunikatu o błędzie (`NullPointerException`) i otrzymywania sugestii dotyczących potencjalnych przyczyn oraz poprawek.

**Kontekst:** W aplikacji `spring-petclinic` występuje błąd. Symulujesz sytuację, w której `Pet` w pewnym momencie jest `null`, co prowadzi do wyjątku.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/web/OwnerController.java`.
2.  W metodzie `processCreationForm` (lub innej, która operuje na obiekcie `Pet`), celowo wprowadź błąd, który spowoduje `NullPointerException`. Na przykład, znajdź fragment kodu, gdzie używany jest `Pet` i tymczasowo ustaw go na `null` przed użyciem, lub stwórz warunek, w którym `pet` mógłby być `null` gdy nie powinien.
    ```java
    // Przykład celowego błędu:
    Pet pet = new Pet(); // Załóżmy, że normalnie jest inicjalizowany
    // ...
    pet = null; // Celowe ustawienie na null przed użyciem
    String petName = pet.getName(); // To spowoduje NullPointerException
    ```
3.  Uruchom aplikację `spring-petclinic` (np. z poziomu IDE) i wykonaj akcję, która wywoła ten błąd (np. spróbuj dodać nowego właściciela lub zwierzaka, w zależności od miejsca wprowadzenia błędu).
4.  Gdy aplikacja się zawiesi lub wyświetli błąd w konsoli/logach, skopiuj pełen stack trace wyjątku.
5.  Wklej skopiowany stack trace do GitHub Copilot Chatu i zadaj pytanie: "Zanalizuj ten stack trace. Dlaczego wystąpił `NullPointerException` w `OwnerController.java` i jak mogę go naprawić?"
6.  Przeanalizuj odpowiedź Copilota. Powinien wskazać konkretną linię i przyczynę błędu, a także zaproponować rozwiązania (np. sprawdzenie `null`, inicjalizację obiektu).
7.  Zastosuj sugestie Copilota, aby poprawić błąd w `OwnerController.java`.
8.  Uruchom aplikację ponownie i upewnij się, że błąd został naprawiony.

**Oczekiwany rezultat:**
-   Zrozumienie, jak Copilot pomaga w diagnozowaniu `NullPointerException` na podstawie stack trace\'a.
-   Poprawiony kod w `OwnerController.java`, który poprawnie obsługuje potencjalne wartości `null`.

**Wskazówki:**
-   Możesz eksperymentować z różnymi miejscami wprowadzenia `NullPointerException`, aby zobaczyć, jak Copilot radzi sobie z różnymi scenariuszami.
-   Jeśli Copilot nie daje wystarczająco szczegółowych wskazówek, możesz doprecyzować pytanie, podając dodatkowy kontekst kodu.

---

## Ćwiczenie 4: Analiza kodu i stanu podczas debugowania z Copilotem

**Cel:** Wykorzystanie GitHub Copilota do zrozumienia wpływu zmian w kodzie i interpretacji stanu aplikacji w trakcie procesu debugowania, pomagając w szybkim identyfikacji problemów.

**Kontekst:** W `spring-petclinic` napotykasz problem z niepoprawnym filtrowaniem danych w repozytorium. Musisz zrozumieć, dlaczego metoda `findByLastName` w `OwnerRepository` nie zwraca oczekiwanych wyników.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/repository/OwnerRepository.java`.
2.  W metodzie `findByLastName`, celowo wprowadź mały błąd w zapytaniu (np. użyj nieistniejącej kolumny lub błędnego warunku `LIKE`). Na przykład, zamiast `findByLastNameContainingIgnoreCase`, zmień na `findByLastNameEqualsIgnoreCase` lub zmień `String lastName` na `String firstName` w sygnaturze metody zapytania, nie zmieniając jego użycia.
    ```java
    // Przykład celowego błędu w OwnerRepository.java
    // Oryginał: @Query("SELECT owner FROM Owner owner WHERE owner.lastName LIKE :lastName%")
    // Zmienione na:
    @Query("SELECT owner FROM Owner owner WHERE owner.lastName = :lastName") // Celowo zmienione na dokładne dopasowanie
    List<Owner> findByLastName(@Param("lastName") String lastName);
    ```
3.  Uruchom aplikację w trybie debugowania.
4.  Ustaw breakpointy w metodzie `findByLastName` w `OwnerRepository.java` oraz w kontrolerze (np. `OwnerController.java`) tam, gdzie ta metoda jest wywoływana (np. w `processFindForm`).
5.  Przejdź do interfejsu użytkownika aplikacji i spróbuj wyszukać właściciela (np. wpisz "mi" w pole wyszukiwania, aby znaleźć "Smith").
6.  Gdy debugger zatrzyma się na breakpointach, obserwuj wartości zmiennych. Zauważ, że metoda `findByLastName` może zwrócić pustą listę lub niepoprawne wyniki.
7.  Zaznacz kod metody `findByLastName` w `OwnerRepository.java`.
8.  Otwórz GitHub Copilot Chat i zapytaj: "Analizuję metodę `findByLastName`, która nie zwraca oczekiwanych wyników. Patrząc na ten kod, dlaczego `OwnerRepository` może nie zwracać wszystkich właścicieli dla częściowego dopasowania nazwiska?"
9.  Copilot powinien wskazać, że zmiana operatora `LIKE` na `=` spowodowała, że zapytanie szuka dokładnego dopasowania, a nie częściowego.
10. Bazując na sugestiach Copilota, popraw zapytanie w `OwnerRepository.java`, przywracając oryginalne zachowanie lub implementując oczekiwane.
11. Kontynuuj debugowanie lub uruchom testy, aby potwierdzić, że problem został rozwiązany.

**Oczekiwany rezultat:**
-   Zrozumienie, jak Copilot pomaga w analizie zapytań i logiki repozytorium podczas debugowania.
-   Naprawiona metoda `findByLastName` w `OwnerRepository.java`, która poprawnie filtruje właścicieli.

**Wskazówki:**
-   Możesz poprosić Copilota o wyjaśnienie składni zapytań JPQL/SQL, jeśli masz wątpliwości.
-   Zacznij od małych, kontrolowanych błędów, aby łatwiej było śledzić proces debugowania.
