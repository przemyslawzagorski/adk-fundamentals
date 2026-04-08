# Zaawansowane Scenariusze: Inżynieria Kontekstu i Promptów

Ten dokument przedstawia bardziej złożone i realistyczne scenariusze wykorzystania GitHub Copilot w kontekście inżynierii kontekstu i promptów, które wymagają głębszego zrozumienia jego możliwości i ograniczeń.

## Scenariusz 1: Rozwiązywanie Problemu "Token Window" w Mikroserwisie

**Opis:** Pracujesz nad złożonym systemem mikroserwisów. Jeden z mikroserwisów, odpowiedzialny za przetwarzanie danych klientów, ma bardzo rozbudowaną logikę biznesową, wiele encji JPA, serwisów, DTO i kontrolerów, rozłożonych na kilkadziesiąt plików. Chcesz wprowadzić nową funkcjonalność, która wymaga modyfikacji kilku encji, dodania nowego serwisu i kontrolera, a także zaktualizowania logiki walidacji w istniejących klasach.

**Wyzwanie:** Użycie `@workspace` powoduje, że Copilot staje się "mniej precyzyjny" lub wręcz ignoruje ważne detale, ponieważ kontekst jest zbyt duży i przekracza "token window". Sugestie są ogólne i wymagają ciągłego poprawiania.

**Strategia rozwiązania z Copilotem:**
1.  **Mapowanie zależności:** Zidentyfikuj kluczowe pliki, które będą modyfikowane lub tworzone. Użyj Copilota do szybkiego zrozumienia zależności między nimi (np. pytając "Jakie serwisy używają tej encji?" wskazując na encję).
2.  **Podział na mniejsze zadania:** Zamiast prosić o całą funkcjonalność naraz, podziel ją na mniejsze, zarządzalne etapy (np. "Krok 1: Modyfikacja encji X. Krok 2: Utworzenie nowego serwisu Y. Krok 3: Dodanie kontrolera Z.").
3.  **Fokus na pliku (`#file`):** Dla każdej modyfikacji w istniejącym pliku, używaj `#file` lub zaznaczaj konkretny blok kodu. Np. dla zmiany w encji A, otwórz `A.java`, użyj `#file` i poproś o konkretne zmiany.
4.  **Jawne wskazywanie wielu plików (`@file:path`):** Gdy potrzebujesz kontekstu z kilku powiązanych plików (np. encja, jej DTO i serwis), jawnie wskaż je w prompcie Copilot Chat. Przykład: `/createController @file:MyEntity.java @file:MyDto.java @file:MyService.java`. To pozwala na "szyte na miarę" okno kontekstowe.
5.  **Generowanie "szkieletów":** Poproś Copilota o wygenerowanie szkieletów dla nowych klas (serwis, kontroler), a następnie iteracyjnie dodawaj implementację, fokusując się na konkretnych metodach.
6.  **Wykorzystanie `.copilotignore`:** Upewnij się, że pliki niezwiązane z logiką biznesową (np. pliki konfiguracyjne środowiska, logi, pliki generowane automatycznie) są wykluczone z kontekstu Copilota, aby maksymalnie zwiększyć dostępną przestrzeń na kod źródłowy.

## Scenariusz 2: Generowanie Skomplikowanych Zapytań SQL/JPQL z Optymalizacją

**Opis:** W projekcie `spring-petclinic`, chcesz stworzyć raport, który wymaga złożonego zapytania JPQL, łączącego dane z wielu encji (np. właściciele, zwierzęta, wizyty, weterynarze, specjalizacje). Zapytanie musi być zoptymalizowane pod kątem wydajności i obsługiwać parametryzację.

**Wyzwanie:** Ręczne pisanie takiego zapytania jest czasochłonne i podatne na błędy. Copilot może pomóc, ale potrzebuje precyzyjnych instrukcji.

**Strategia rozwiązania z Copilotem:**
1.  **Model danych jako kontekst:** Upewnij się, że Copilot ma dostęp do wszystkich encji, które mają być użyte w zapytaniu (np. `Owner.java`, `Pet.java`, `Visit.java`, `Vet.java`, `Specialty.java`). Możesz otworzyć te pliki lub jawnie je wskazać.
2.  **Opis biznesowy zapytania:** Sformułuj prompt w języku naturalnym, opisując, jakie dane chcesz uzyskać i jakie warunki muszą być spełnione.
    ```
    Jako programista JPA, napisz zapytanie JPQL, które zwróci właścicieli, którzy posiadają co najmniej jedno zwierzę, które miało wizytę w ciągu ostatnich 6 miesięcy u weterynarza specjalizującego się w kardiologii. Zapytanie powinno zwrócić Ownerów, posortowanych po nazwisku. Parametrami powinny być data początkowa i nazwa specjalizacji. Użyj aliasów dla czytelności.
    ```
3.  **Wskazówki optymalizacyjne:** W prompcie możesz dodać wskazówki dotyczące wydajności, np. "Zapewnij, że zapytanie jest zoptymalizowane, unikając n+1 problemu" (choć w JPQL to mniej problematyczne niż w HQL, nadal warto wspomnieć).
4.  **Iteracja i weryfikacja:** Po wygenerowaniu zapytania, przeanalizuj je. Jeśli coś jest nie tak, poproś Copilota o poprawki, precyzując, co jest nieprawidłowe (np. "Warunek daty jest błędny, powinien być większy lub równy od daty początkowej").
5.  **Dodanie do repozytorium:** Po uzyskaniu poprawnego zapytania, poproś Copilota o dodanie metody do odpowiedniego interfejsu repozytorium (np. `OwnerRepository`) z adnotacją `@Query`.

## Scenariusz 3: Dynamiczne Generowanie DTO i Mapperów

**Opis:** Masz istniejącą encję (`Owner.java`) i potrzebujesz kilku różnych wersji DTO dla różnych scenariuszy (np. `OwnerListDto` tylko z imieniem i nazwiskiem, `OwnerDetailsDto` ze wszystkimi danymi, `OwnerWithPetsDto` z danymi zwierząt). Potrzebujesz również mapperów do konwersji między encją a tymi DTO.

**Wyzwanie:** Ręczne tworzenie wielu DTO i mapperów jest monotonne i podatne na błędy. Chcesz, aby Copilot automatyzował ten proces.

**Strategia rozwiązania z Copilotem:**
1.  **Definicja DTO:** Dla każdego DTO stwórz nowy plik (np. `OwnerListDto.java`). W środku pliku, opisz, jakie pola ma zawierać to DTO i do jakiego scenariusza służy. Wskaż encję `Owner.java` jako kontekst.
    ```
    Jako programista Spring, wygeneruj klasę `OwnerListDto.java` w języku Java, która będzie Data Transfer Object dla encji `Owner.java`. `OwnerListDto` powinien zawierać tylko pola `id`, `firstName`, `lastName`. Dodaj również konstruktor oraz gettery. Kontekst: @file:src/main/java/org/springframework/samples/petclinic/owner/Owner.java
    ```
2.  **Generowanie mappera:** Po utworzeniu wszystkich DTO, poproś o stworzenie klasy mapperów (np. `OwnerMapper.java`) z metodami do konwersji między `Owner` a każdym z DTO.
    ```
    Jako programista Java, stwórz klasę `OwnerMapper.java` w pakiecie `org.springframework.samples.petclinic.owner.mapper`. Klasa powinna zawierać statyczne metody do mapowania: `Owner` -> `OwnerListDto`, `Owner` -> `OwnerDetailsDto`, `OwnerListDto` -> `Owner`. Użyj kontekstu `Owner.java`, `OwnerListDto.java`, `OwnerDetailsDto.java` (jeśli stworzono). Preferuj MapStruct jeśli jest na classpathie, w przeciwnym razie manualne mapowanie.
    ```
3.  **Iteracyjna weryfikacja:** Sprawdź, czy wygenerowane mappery poprawnie obsługują wszystkie pola i czy konwersje są dwukierunkowe, jeśli tego potrzebujesz.

## Scenariusz 4: Implementacja Niestandardowej Adnotacji Walidacyjnej

**Opis:** Chcesz zaimplementować niestandardową adnotację walidacyjną w Spring Boot, np. `ValidTelephoneNumber`, która sprawdzi, czy numer telefonu jest zgodny z polskim formatem (+48 XXX XXX XXX lub XXX XXX XXX).

**Wyzwanie:** Tworzenie niestandardowych adnotacji walidacyjnych wymaga kilku kroków: definicji adnotacji, implementacji walidatora i powiązania ich ze sobą. Copilot może pomóc w stworzeniu całej struktury.

**Strategia rozwiązania z Copilotem:**
1.  **Definicja adnotacji:** Poproś Copilota o stworzenie pliku `ValidTelephoneNumber.java` dla niestandardowej adnotacji.
    ```
    Jako programista Spring Boot, wygeneruj niestandardową adnotację walidacyjną `@ValidTelephoneNumber` w języku Java. Powinna mieć pole `message` z wartością domyślną "Niepoprawny format numeru telefonu". Powinna być używalna na polach typu `String`. Kontekst: standardowe adnotacje walidacyjne Spring (np. @Pattern).
    ```
2.  **Implementacja walidatora:** Następnie poproś o stworzenie implementacji walidatora dla tej adnotacji, która użyje wyrażenia regularnego dla polskiego formatu numeru telefonu.
    ```
    Jako programista Spring Boot, zaimplementuj walidator dla adnotacji `@ValidTelephoneNumber`. Klasa powinna nazywać się `TelephoneNumberValidator` i implementować `ConstraintValidator<ValidTelephoneNumber, String>`. Użyj wyrażenia regularnego `^(\+48)? ?\d{3} ?\d{3} ?\d{3}$` do walidacji numeru telefonu. Zwróć tylko kod klasy `TelephoneNumberValidator`.
    ```
3.  **Integracja:** Poproś o zastosowanie tej adnotacji w encji `Owner.java` na polu `telephone`.
    ```
    W Owner.java, dodaj adnotację `@ValidTelephoneNumber` do pola `telephone`. Upewnij się, że są wszystkie wymagane importy.
    ```
4.  **Testowanie:** Wygeneruj test jednostkowy dla walidatora.
    ```
    Napisz test jednostkowy dla klasy `TelephoneNumberValidator`, używając JUnit 5. Sprawdź poprawne i niepoprawne numery telefonów zgodne z regexem `^(\+48)? ?\d{3} ?\d{3} ?\d{3}$`.
    ```

## Scenariusz 5: Refaktoryzacja z Użyciem Funkcji Javy 17+

**Opis:** Projekt `spring-petclinic` używa starszej wersji Javy (np. Java 8 lub 11), a Ty chcesz zaktualizować go do Javy 17+ i skorzystać z nowych funkcji języka, takich jak Records, Pattern Matching for instanceof czy Switch Expressions.

**Wyzwanie:** Ręczne przepisywanie klas na Records lub dostosowywanie kodu do nowych funkcji jest czasochłonne.

**Strategia rozwiązania z Copilotem:**
1.  **Konwersja na Record:** Zidentyfikuj proste klasy DTO lub niemutowalne klasy (np. `PetType` jeśli byłby niemutowalny) i poproś Copilota o konwersję na Record.
    ```
    Jako programista Java 17, przekształć tę klasę `MyDto.java` w Java Record. Zwróć tylko kod klasy Record. #file
    ```
2.  **Pattern Matching for instanceof:** Zidentyfikuj miejsca, gdzie występuje `instanceof` i rzutowanie. Poproś Copilota o refaktoryzację z użyciem Pattern Matching.
    ```
    Refaktoryzuj ten fragment kodu, aby używał Pattern Matching for instanceof (Java 17+). #file
    ```
    *Oryginał:* 
    ```java
    if (obj instanceof MyClass) {
        MyClass myClass = (MyClass) obj;
        myClass.doSomething();
    }
    ```
    *Prompt:* `Refactor this code snippet to use Pattern Matching for instanceof (Java 17+). #file`
    *Sugestia Copilota:* 
    ```java
    if (obj instanceof MyClass myClass) {
        myClass.doSomething();
    }
    ```
3.  **Switch Expressions:** Zidentyfikuj skomplikowane konstrukcje `switch` z wieloma `case` i `break`. Poproś o konwersję na Switch Expression.
    ```
    Refaktoryzuj tę instrukcję switch na Switch Expression (Java 17+). #file
    ```

**Oczekiwany rezultat:** Kod zgodny z nowymi funkcjami Javy 17+, bardziej zwięzły i czytelny.

**Wskazówki:**
-   Upewnij się, że projekt jest skonfigurowany do używania odpowiedniej wersji Javy (np. w `pom.xml`).
-   Copilot jest bardzo dobry w prostych konwersjach i refaktoryzacjach na nowe funkcje języka. Złożone scenariusze mogą wymagać dalszych poprawek.