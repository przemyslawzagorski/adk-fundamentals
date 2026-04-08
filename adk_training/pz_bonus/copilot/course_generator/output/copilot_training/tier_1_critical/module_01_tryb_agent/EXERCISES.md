# Ćwiczenia: Tryb Agent - Fundament Pracy z Copilot

Wszystkie ćwiczenia są zaprojektowane do wykonania w środowisku Visual Studio Code z zainstalowanym rozszerzeniem GitHub Copilot Chat i w oparciu o sklonowane repozytorium `spring-petclinic` (https://github.com/spring-projects/spring-petclinic).

---

## Ćwiczenie 1: Analiza Technicznego Stosu Projektu z `@workspace`

**Cel:** Zrozumienie, jak agent `@workspace` może pomóc w szybkim zapoznaniu się z architekturą nieznanego projektu, identyfikując kluczowe technologie i zależności.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Jesteś nowym członkiem zespołu i chcesz szybko zrozumieć, jakie technologie są używane i jak projekt jest zbudowany.

**Kroki:**
1.  Otwórz projekt `spring-petclinic` w Visual Studio Code.
2.  W oknie czatu Copilot wpisz:
    ```
    @workspace Jaka jest główna architektura tego projektu? Jakie technologie backendowe i frontendowe są używane? Jakie są główne zależności budowania (np. Maven/Gradle, Spring Boot)?
    ```
3.  Przeanalizuj odpowiedź agenta. Zwróć uwagę na wymienione frameworki, bazy danych, narzędzia do budowania i silniki szablonów.
4.  Zadaj dodatkowe pytanie, np.:
    ```
    @workspace Gdzie w projekcie znajdują się pliki konfiguracyjne bazy danych i jak wygląda jej konfiguracja dla profilu `dev`?
    ```

**Oczekiwany rezultat:**
Otrzymasz zwięzłe podsumowanie technicznego stosu projektu, jego architektury (np. MVC), oraz informacji o konfiguracji bazy danych, wskazujące na konkretne pliki (`pom.xml`, `application.properties`, etc.). Powinieneś być w stanie zidentyfikować, że projekt używa Spring Boot, Spring Data JPA, H2/PostgreSQL, Thymeleaf i Maven/Gradle.

**Wskazówki:**
-   Upewnij się, że masz otwarty cały folder `spring-petclinic` w VS Code, aby agent miał pełny kontekst `workspace`.
-   Zwróć uwagę na to, jak agent identyfikuje i podsumowuje informacje z różnych plików konfiguracyjnych.

---

## Ćwiczenie 2: Znajdowanie Dokumentacji VS Code z `@vscode`

**Cel:** Wykorzystanie agenta `@vscode` do szybkiego wyszukiwania informacji i dokumentacji dotyczącej funkcji Visual Studio Code.

**Kontekst:** Chcesz poprawić swoje nawyki w używaniu VS Code i szukasz informacji o skrótach klawiszowych lub konkretnych funkcjach edytora.

**Kroki:**
1.  W oknie czatu Copilot wpisz:
    ```
    @vscode Jakie są najczęściej używane skróty klawiszowe w VS Code do nawigacji po kodzie i edycji?
    ```
2.  Zapoznaj się z listą skrótów. Wybierz jeden, którego nie znasz, i spróbuj go użyć.
3.  Zadaj kolejne pytanie:
    ```
    @vscode Wyjaśnij mi, czym jest funkcja "Peek Definition" w VS Code i jak jej użyć.
    ```

**Oczekiwany rezultat:**
Agent dostarczy listę skrótów klawiszowych i szczegółowy opis funkcji "Peek Definition" wraz z instrukcją użycia. Będziesz w stanie szybko uzyskać pomoc dotyczącą środowiska VS Code.

**Wskazówki:**
-   Pamiętaj, że `@vscode` jest Twoim przewodnikiem po samym edytorze, nie po kodzie projektu.

---

## Ćwiczenie 3: Refaktoryzacja `OwnerController.java` i Analiza Planu z `@agent`

**Cel:** Przeprowadzenie prostej refaktoryzacji metody z pomocą agenta `@agent` oraz analiza wygenerowanego przez niego planu działania.

**Kontekst:** W pliku `OwnerController.java` metoda `processFindForm` zawiera pewną duplikację kodu lub można ją uprościć. Chcesz, aby agent zaproponował refaktoryzację.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`.
2.  Przejdź do metody `processFindForm` (linia około 128).
3.  Zaznacz całą metodę `processFindForm`.
4.  W inline chat (Ctrl+I na zaznaczonym kodzie) lub w głównym czacie Copilot wpisz:
    ```
    @agent Zrefaktoryzuj tę metodę, aby była bardziej czytelna i używała Stream API Javy 8+, jeśli to możliwe, do filtrowania właścicieli. Najpierw pokaż mi swój plan.
    ```
5.  Przeanalizuj plan przedstawiony przez agenta. Oceń, czy ma sens i czy spełnia Twoje oczekiwania.
6.  Akceptuj plan, aby agent wykonał refaktoryzację.

**Oczekiwany rezultat:**
Agent przedstawi plan refaktoryzacji, który powinien zawierać kroki takie jak analiza kodu, identyfikacja miejsc do zmian, propozycja użycia Stream API. Po akceptacji planu, metoda `processFindForm` zostanie zmodyfikowana, stając się bardziej zwięzła i wykorzystująca nowoczesne konstrukcje Javy.

**Wskazówki:**
-   Zwróć uwagę na sekcję "Plan" w odpowiedzi agenta. To kluczowe, aby zrozumieć, co Copilot zamierza zrobić.
-   Jeśli plan nie jest idealny, możesz poprosić o jego modyfikację lub spróbować z innym poleceniem.

---

## Ćwiczenie 4: Dodawanie Nowego Endpointu REST do `VetController.java` (Planowanie)

**Cel:** Zaplanowanie z agentem `@agent` dodania nowego endpointu REST do istniejącego kontrolera.

**Kontekst:** Chcesz dodać do `spring-petclinic` nową funkcjonalność: endpoint REST, który zwróci listę weterynarzy pogrupowanych według ich specjalizacji. Zamiast od razu pisać kod, chcesz najpierw stworzyć szczegółowy plan.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/vet/VetController.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent Chcę dodać nowy endpoint REST do VetController.java pod adresem `/api/vets/bySpecialty/{specialtyName}`. Powinien on zwracać listę obiektów Vet, które posiadają daną specjalizację. Najpierw przedstaw mi szczegółowy plan implementacji, wliczając zmiany w repozytorium i serwisie (jeśli potrzebne). Nie generuj jeszcze kodu.
    ```
3.  Dokładnie przeanalizuj plan. Sprawdź, czy uwzględnia wszystkie aspekty (zmiana modelu, repozytorium, serwisu, kontrolera, ewentualne testy).
4.  Poproś agenta o doprecyzowanie wybranego kroku, np.:
    ```
    @agent W kroku dotyczącym modyfikacji repozytorium, jaka dokładnie metoda powinna zostać dodana do VetRepository?
    ```

**Oczekiwany rezultat:**
Agent przedstawi kompleksowy plan, który będzie zawierał kroki takie jak: modyfikacja `VetRepository` (dodanie metody `findBySpecialtyName`), ewentualne stworzenie `VetService`, dodanie endpointu w `VetController` z odpowiednimi adnotacjami (`@GetMapping`, `@PathVariable`) i obsługą odpowiedzi JSON. Powinien również wspomnieć o obsłudze przypadków, gdy specjalizacja nie istnieje.

**Wskazówki:**
-   Zwróć uwagę, że prośba "Nie generuj jeszcze kodu" jest kluczowa dla tego ćwiczenia, aby skupić się na planowaniu.
-   Ten scenariusz jest również dobrą okazją, aby agent stworzył DTO (Data Transfer Object) dla `Vet` w odpowiedzi JSON, aby uniknąć problemów z serializacją encji.

---

## Ćwiczenie 5: Śledzenie Pamięci Agenta w `Pet.java`

**Cel:** Zrozumienie, jak agent `@agent` utrzymuje kontekst i pamięć krótkotrwałą w trakcie konwersacji.

**Kontekst:** Chcesz wprowadzić kilka zmian w klasie `Pet.java` i obserwować, jak agent "pamięta" poprzednie modyfikacje i pytania.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/pet/Pet.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent W klasie Pet.java, dodaj nowe pole `chipId` typu String. Upewnij się, że jest ono walidowane (np. niepuste i unikalne).
    ```
    (Akceptuj sugerowane zmiany).
3.  Po dodaniu pola, zadaj kolejne pytanie dotyczące tej samej klasy, ale bez ponownego wskazywania pliku:
    ```
    @agent Teraz, dodaj metodę `getAgeInYears()` do klasy Pet, która oblicza wiek zwierzęcia na podstawie daty urodzenia i bieżącej daty.
    ```
    (Akceptuj sugerowane zmiany).
4.  Na koniec, zadaj pytanie odnoszące się do obu zmian:
    ```
    @agent Zaimplementuj metodę `toString()` dla klasy Pet, która będzie zawierać wszystkie pola, w tym `chipId` i wynik metody `getAgeInYears()`.
    ```

**Oczekiwany rezultat:**
Agent będzie w stanie bez problemu śledzić zmiany w klasie `Pet.java` i odwoływać się do wcześniej dodanych pól (`chipId`) i metod (`getAgeInYears()`), co świadczy o utrzymaniu kontekstu konwersacji.

**Wskazówki:**
-   Monitoruj, czy agent nie "gubi wątku" między kolejnymi pytaniami. Jeśli tak się stanie, być może kontekst stał się zbyt duży.
-   Zauważ, że w ostatnim pytaniu nie musiałeś przypominać agentowi o `chipId` ani `getAgeInYears()`.

---

## Ćwiczenie 6: Testowanie Odporności Pamięci Agenta na Sprzeczne Informacje

**Cel:** Sprawdzenie, jak agent `@agent` reaguje na wprowadzenie sprzecznych informacji w różnych etapach rozmowy.

**Kontekst:** Symulujesz scenariusz, w którym wymagania ewoluują lub są niejasne, i chcesz zobaczyć, jak Copilot radzi sobie z korektą lub rozbieżnościami.

**Kroki:**
1.  W nowej sesji czatu Copilot (lub po zresetowaniu poprzedniej) poproś:
    ```
    @agent Wygeneruj prosty interfejs `PaymentGateway` z metodą `processPayment(double amount)`.
    ```
    (Akceptuj wygenerowany kod).
2.  Następnie wprowadź sprzeczne wymaganie:
    ```
    @agent Zmień interfejs `PaymentGateway` tak, aby metoda nazywała się `authorizePayment(BigDecimal amount, String currency)` i zwracała `boolean`.
    ```
3.  Po wprowadzeniu drugiej zmiany, zapytaj:
    ```
    @agent Jak obecnie wygląda metoda do przetwarzania płatności w interfejsie PaymentGateway?
    ```

**Oczekiwany rezultat:**
Agent powinien poprawnie zinterpretować drugie polecenie jako modyfikację pierwszego i zaprezentować zaktualizowaną sygnaturę metody. Pamięć krótkotrwała agenta powinna nadpisać poprzednie informacje nowymi.

**Wskazówki:**
-   To ćwiczenie podkreśla, że najnowsze instrukcje mają priorytet w kontekście bieżącej konwersacji.
-   Zwróć uwagę, czy agent zadaje pytania o rozbieżności, czy po prostu przyjmuje nową instrukcję.

---

## Ćwiczenie 7: Wyszukiwanie Best Practices dla Spring Data JPA i Implementacja z `@search` i `@agent`

**Cel:** Wykorzystanie `@search` do pozyskania wiedzy, a następnie `@agent` do zastosowania jej w kodzie `spring-petclinic`.

**Kontekst:** Chcesz upewnić się, że `OwnerRepository.java` w `spring-petclinic` używa najlepszych praktyk Spring Data JPA, szczególnie w kontekście obsługi transakcji i zapytań niestandardowych.

**Kroki:**
1.  W oknie czatu Copilot wpisz:
    ```
    @search Jakie są najlepsze praktyki użycia adnotacji `@Transactional` w Spring Data JPA? Kiedy powinno się jej używać na poziomie serwisu, a kiedy na poziomie repozytorium?
    ```
2.  Przeanalizuj odpowiedź, zwracając uwagę na zalecenia dotyczące warstwy serwisu.
3.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java` oraz (jeśli by istniał) `OwnerService.java` (w `spring-petclinic` często logika jest w kontrolerze, więc skupimy się na adnotacjach tam, gdzie to możliwe, lub zasymulujemy warstwę serwisu).
4.  Poproś agenta o analizę i zasugerowanie zmian:
    ```
    @agent Bazując na zdobytej wiedzy o `@Transactional`, przeanalizuj OwnerRepository.java (i OwnerController.java, jeśli brakuje warstwy serwisu). Zaproponuj, gdzie najlepiej umieścić `@Transactional` w celu zapewnienia spójności danych.
    ```
5.  Akceptuj lub modyfikuj zaproponowane zmiany.

**Oczekiwany rezultat:**
Agent powinien znaleźć i podsumować najlepsze praktyki dotyczące `@Transactional`, wskazując, że zazwyczaj powinno się ją stosować na warstwie serwisu. Następnie, zaproponuje dodanie `@Transactional` do metod w `OwnerController.java` (w przypadku braku serwisu), które modyfikują dane, takie jak `saveOwner` lub `processUpdateOwnerForm`, a także zasugeruje, jak poprawić te metody.

**Wskazówki:**
-   To ćwiczenie pokazuje, jak możesz łączyć możliwości różnych agentów, aby najpierw pozyskać wiedzę, a następnie ją zastosować.
-   Zwróć uwagę, czy agent poprawnie identyfikuje transakcyjne metody.

---

## Ćwiczenie 8: Generowanie Raportu Pokrycia Testami z `@agent` i `@terminal`

**Cel:** Użycie agenta do wygenerowania raportu pokrycia kodu testami dla całego projektu `spring-petclinic` za pomocą narzędzia budującego (Maven).

**Kontekst:** Chcesz sprawdzić, które części kodu są pokryte testami, aby zidentyfikować obszary wymagające uwagi.

**Kroki:**
1.  W oknie czatu Copilot wpisz:
    ```
    @agent Wygeneruj raport pokrycia kodu testami dla projektu spring-petclinic. Użyj narzędzia Maven i pluginu JaCoCo. Gdzie znajdę wygenerowany raport? Pokaż mi polecenie Mavena do tego celu.
    ```
2.  Agent powinien przedstawić plan i odpowiednie polecenie Maven. Przeanalizuj je.
3.  Akceptuj wykonanie polecenia.
    ```
    @terminal mvn clean verify jacoco:report
    ```
4.  Po zakończeniu procesu, zapytaj agenta o lokalizację raportu:
    ```
    @agent Gdzie jest plik `index.html` z raportem JaCoCo?
    ```

**Oczekiwany rezultat:**
Agent powinien wskazać, że raport JaCoCo zostanie wygenerowany w katalogu `target/site/jacoco/index.html` (lub podobnym, zależnym od konfiguracji). Po uruchomieniu polecenia Maven, będziesz mógł otworzyć ten plik w przeglądarce i zobaczyć szczegółowy raport pokrycia testami.

**Wskazówki:**
-   Upewnij się, że masz zainstalowanego Mavena i poprawnie skonfigurowane zmienne środowiskowe, aby `@terminal` mógł go wywołać.
-   Zwróć uwagę na to, jak agent łączy wiedzę o narzędziach (JaCoCo, Maven) z umiejętnością interakcji z terminalem.

---

## Ćwiczenie 9: Debugowanie Błędu w Spring PetClinic z `@agent` i Narzędziami

**Cel:** Wykorzystanie agenta do pomocy w identyfikacji i rozwiązaniu prostego błędu logicznego lub środowiskowego w `spring-petclinic`.

**Kontekst:** Aplikacja `spring-petclinic` nie uruchamia się prawidłowo lub działa nieoczekiwanie w pewnym scenariuszu. Chcesz, aby Copilot pomógł w debugowaniu.

**Sytuacja Problemowa (zasymuluj błąd):**
1.  Celowo wprowadź błąd do projektu: Otwórz `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
2.  Zmień adnotację `@NotEmpty` przy polu `firstName` na `@Size(min = 100)` lub celowo zepsuj nazwę metody w repozytorium, np. w `OwnerRepository.java` zmień `findByLastName` na `findOwnersByLastNameeeee`.
3.  Spróbuj uruchomić aplikację. Prawdopodobnie otrzymasz błąd podczas startu lub NullPointerException/błąd walidacji.

**Kroki:**
1.  Skopiuj pełny stos wywołania błędu (stack trace) z konsoli lub panelu "Problems" w VS Code.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent Występuje następujący błąd podczas uruchamiania aplikacji spring-petclinic. Proszę o pomoc w zdiagnozowaniu przyczyny i zaproponowanie rozwiązania.
    ```
    (Wklej stos wywołania błędu po zapytaniu).
3.  Jeśli agent poprosi o więcej kontekstu, wskaż mu pliki, które zmodyfikowałeś.
4.  Jeśli błąd jest trudniejszy do zdiagnozowania, poproś agenta o plan debugowania:
    ```
    @agent Stwórz plan debugowania tego problemu. Czy mogę użyć debugera w VS Code?
    ```

**Oczekiwany rezultat:**
Agent powinien przeanalizować stos wywołania błędu i/lub plan debugowania. Powinien wskazać na miejsce, gdzie błąd najprawdopodobniej występuje (np. w konfiguracji walidacji `Owner` lub błędnej nazwie metody w repozytorium). Otrzymasz sugestie naprawy lub plan, który pomoże Ci samodzielnie znaleźć i rozwiązać problem.

**Wskazówki:**
-   Kluczem jest dostarczenie agentowi pełnego stosu wywołania błędu.
-   Ćwiczenie to pokazuje, jak agenci mogą pomóc w interpretacji komunikatów o błędach i w nawigowaniu po problemach.

---

## Ćwiczenie 10: Generowanie Testów Jednostkowych dla `OwnerController`

**Cel:** Wykorzystanie agenta `@agent` do wygenerowania podstawowych testów jednostkowych dla istniejącego kontrolera.

**Kontekst:** Masz istniejący kontroler `OwnerController.java` i chcesz szybko stworzyć dla niego zestaw testów jednostkowych, aby zapewnić jego poprawność.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent Wygeneruj testy jednostkowe dla klasy `OwnerController`, używając MockMvc. Skup się na testowaniu metod `initCreationForm`, `processCreationForm` i `showOwner`.
    ```
3.  Przeanalizuj plan agenta i wygenerowany kod testowy.

**Oczekiwany rezultat:**
Agent wygeneruje nowy plik testowy (`OwnerControllerTests.java`) z podstawowymi testami dla wskazanych metod. Testy będą używać `MockMvc` do symulacji żądań HTTP i weryfikacji odpowiedzi, a także `Mockito` do mokowania zależności (np. `OwnerRepository`).

**Wskazówki:**
-   Możesz poprosić agenta o bardziej szczegółowe testy, np. testowanie walidacji lub różnych scenariuszy (pozytywnych/negatywnych).
-   To ćwiczenie pokazuje siłę agenta w automatyzacji tworzenia boilerplate'u testowego.

---

## Ćwiczenie 11: Implementacja Nowej Walidacji dla `Pet` z `@agent`

**Cel:** Dodanie niestandardowej walidacji do encji `Pet` za pomocą agenta `@agent`.

**Kontekst:** W `spring-petclinic` chcesz wprowadzić niestandardową walidację, która zapewni, że data urodzenia zwierzęcia (`birthDate`) nie jest w przyszłości.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/pet/Pet.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent Dodaj niestandardową walidację do klasy `Pet`, która zapewni, że pole `birthDate` nie może być datą z przyszłości. Zaimplementuj adnotację walidacyjną i walidator.
    ```
3.  Przeanalizuj plan i kod wygenerowany przez agenta. Akceptuj zmiany.
4.  Sprawdź, czy walidator i adnotacja zostały poprawnie zintegrowane z klasą `Pet` oraz czy agent zaproponował użycie ich w kontrolerze (np. `PetController`).

**Oczekiwany rezultat:**
Agent powinien wygenerować adnotację walidacyjną (`@PastOrPresentDate` lub podobną) oraz klasę walidatora, która sprawdza datę urodzenia. Zintegruje tę adnotację z polem `birthDate` w `Pet.java`.

**Wskazówki:**
-   Pamiętaj, że walidacja będzie wymagała również dodania adnotacji `@Valid` w kontrolerach, które przyjmują obiekt `Pet` (np. `PetController.processCreationForm`). Agent powinien o tym wspomnieć lub zaoferować zmianę.

---

## Ćwiczenie 12: Optymalizacja Zapytania SQL (Analiza) z `@workspace` i `@agent`

**Cel:** Zidentyfikowanie potencjalnych wąskich gardeł w bazie danych na podstawie zapytań JPA i sugestia optymalizacji.

**Kontekst:** Podejrzewasz, że niektóre operacje pobierania danych w `spring-petclinic` mogą być nieefektywne, zwłaszcza te, które łączą wiele tabel.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @workspace W OwnerRepository.java, przeanalizuj zapytania JPA/HQL, zwłaszcza te, które potencjalnie mogą generować problem N+1. Zaproponuj, jak można je zoptymalizować (np. użycie `FETCH JOIN`).
    ```
3.  Agent powinien wskazać metody, które mogą generować problem N+1 (np. pobieranie właściciela z jego zwierzętami i ich wizytami) i zaproponować modyfikację zapytań (np. `SELECT owner FROM Owner owner LEFT JOIN FETCH owner.pets`).
4.  Poproś agenta o konkretną modyfikację jednej z tych metod:
    ```
    @agent Zmodyfikuj metodę `findById` w `OwnerRepository` tak, aby od razu pobierała wszystkie zwierzęta i wizyty właściciela, aby uniknąć problemu N+1.
    ```

**Oczekiwany rezultat:**
Agent powinien zidentyfikować metody, które mogą być problematyczne. Po drugiej interakcji, zmodyfikuje metodę `findById` w `OwnerRepository` dodając `LEFT JOIN FETCH` lub podobną konstrukcję, co poprawi wydajność pobierania danych.

**Wskazówki:**
-   To zaawansowane ćwiczenie pokazuje, jak agenci mogą pomagać w optymalizacji wydajności na poziomie bazy danych.
-   Zwróć uwagę, czy agent poprawnie tworzy złożone zapytania JPQL/HQL.

---

## Ćwiczenie 13: Dodawanie Nowej Logiki Biznesowej do `PetService` z `@agent`

**Cel:** Implementacja nowej logiki biznesowej w warstwie serwisowej z pomocą agenta.

**Kontekst:** Chcesz dodać funkcjonalność, która pozwala na śledzenie historycznych zmian statusu zwierzęcia (np. "zdrowy", "chory", "wyleczony"). Wymaga to nowej encji `PetStatusChange` i metody w serwisie.

**Kroki:**
1.  Poproś agenta o stworzenie nowej encji `PetStatusChange` z polami `pet`, `timestamp`, `oldStatus`, `newStatus`.
    ```
    @agent Stwórz nową encję JPA `PetStatusChange` w pakiecie `org.springframework.samples.petclinic.pet`. Powinna mieć pola `id`, `pet` (relacja ManyToOne do Pet), `timestamp` (LocalDateTime), `oldStatus` (String), `newStatus` (String).
    ```
    (Akceptuj zmiany).
2.  Poproś agenta o dodanie nowego serwisu `PetService` (jeśli nie istnieje) lub rozszerzenie istniejącego, o metodę `updatePetStatus(Pet pet, String newStatus)`.
    ```
    @agent Stwórz nową klasę `PetService` w pakiecie `org.springframework.samples.petclinic.pet.service`. Dodaj do niej metodę `updatePetStatus(Pet pet, String newStatus)` która będzie tworzyć i zapisywać nowy obiekt `PetStatusChange`.
    ```
    (Akceptuj zmiany).

**Oczekiwany rezultat:**
Agent stworzy encję `PetStatusChange`, repozytorium dla niej oraz klasę `PetService` z metodą `updatePetStatus`, która poprawnie zapisuje zmiany statusu zwierzęcia.

**Wskazówki:**
-   Zwróć uwagę na to, jak agent radzi sobie z tworzeniem nowych klas i zarządzaniem zależnościami między nimi.
-   Ten proces można rozszerzyć o automatyczne generowanie testów dla nowej logiki.

---

## Ćwiczenie 14: Generowanie Dokumentacji Javadoc dla Kluczowej Klasy z `@agent`

**Cel:** Wykorzystanie agenta do automatycznego generowania i aktualizowania dokumentacji Javadoc dla klasy i jej metod.

**Kontekst:** Chcesz, aby kluczowe klasy w `spring-petclinic` miały pełną i aktualną dokumentację Javadoc, aby ułatwić zrozumienie kodu.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
2.  W oknie czatu Copilot wpisz:
    ```
    @agent Dodaj pełną i zwięzłą dokumentację Javadoc dla klasy `Owner` i wszystkich jej pól oraz publicznych metod.
    ```
3.  Przeanalizuj wygenerowaną dokumentację. Czy jest kompletna? Czy jest dokładna?.
4.  Poproś agenta o poprawkę, jeśli coś jest nie tak, np.:
    ```
    @agent Upewnij się, że dokumentacja metody `getPet()` wyjaśnia relację jeden-do-wielu z klasą `Pet`.
    ```

**Oczekiwany rezultat:**
Agent doda standardowe bloki Javadoc dla klasy `Owner`, jej konstruktorów, pól i metod (getters/setters, `addPet`, `getPet`). Dokumentacja powinna być zgodna z konwencjami Javadoc.

**Wskazówki:**
-   Jest to doskonały przykład automatyzacji powtarzalnych, ale ważnych zadań.
-   Zawsze weryfikuj generowaną dokumentację pod kątem precyzji i kompletności.

---

## Ćwiczenie 15: Tworzenie Niestandardowego Promptu dla Refaktoryzacji z `.copilot/prompts/*.md`

**Cel:** Zrozumienie idei niestandardowych promptów i przygotowanie jednego dla specyficznego scenariusza refaktoryzacji.

**Kontekst:** W Twoim zespole często powtarza się pewien typ refaktoryzacji (np. ekstrakcja logiki biznesowej do warstwy serwisowej). Chcesz stworzyć niestandardowy prompt, który ułatwi agentowi `@agent` wykonywanie tego zadania.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`.
2.  Zidentyfikuj metodę w `OwnerController.java` (np. `processCreationForm` lub `processUpdateOwnerForm`), która zawiera logikę biznesową, którą można przenieść do serwisu.
3.  Stwórz nowy plik: `output/copilot_training/tier_1_critical/module_01_tryb_agent/.copilot/prompts/extract_to_service.md`
4.  W tym pliku umieść następujący prompt (możesz go dostosować):
    ```markdown
    # Refaktoryzacja: Ekstrakcja Logiki Biznesowej do Serwisu

    **Instrukcja dla Copilota:**
    Użytkownik zaznaczył fragment kodu lub wskazał metodę w kontrolerze. Twoim zadaniem jest zrefaktoryzowanie tego kodu poprzez ekstrakcję logiki biznesowej do nowej lub istniejącej metody w warstwie serwisowej.

    **Kroki, które należy wykonać:**
    1.  **Identyfikacja logiki:** Określ, która część zaznaczonego kodu lub metody powinna zostać przeniesiona do serwisu.
    2.  **Stworzenie/Modyfikacja Serwisu:** Jeśli nie istnieje odpowiednia klasa serwisowa dla danego kontekstu, utwórz ją (np. `OwnerService`). Jeśli istnieje, dodaj nową metodę lub zmodyfikuj istniejącą, aby zawierała przeniesioną logikę. Upewnij się, że serwis jest oznaczony jako `@Service`.
    3.  **Wstrzykiwanie Serwisu:** Wstrzyknij nowo utworzony/zmodyfikowany serwis do kontrolera.
    4.  **Wywołanie Metody Serwisu:** Zastąp oryginalną logikę w kontrolerze wywołaniem odpowiedniej metody w serwisie.
    5.  **Testy (opcjonalnie):** Zaproponuj wygenerowanie testów jednostkowych dla nowej metody w serwisie.
    6.  **Potwierdzenie:** Po zakończeniu, potwierdź, że refaktoryzacja została wykonana i że kod jest funkcjonalny.

    **Przykład zastosowania w OwnerController.java, metoda `processCreationForm`:**
    Kod odpowiedzialny za `owners.save(owner)` i przekierowanie powinien zostać przeniesiony do `OwnerService`.
    ```
5.  Zapisz plik. Następnie, wróć do `OwnerController.java`, zaznacz metodę `processCreationForm` i w inline chat spróbuj użyć tego promptu (składnia może się różnić w zależności od wersji Copilota, często to `@prompt extract_to_service`).

**Oczekiwany rezultat:**
Agent powinien zrozumieć intencję promptu i zaproponować plan refaktoryzacji, który obejmuje stworzenie `OwnerService`, przeniesienie logiki `save` do serwisu i zaktualizowanie kontrolera.

**Wskazówki:**
-   To ćwiczenie pokazuje, jak możesz programować Copilota, aby wykonywał specyficzne dla Twojego zespołu zadania.
-   Niestandardowe prompty są potężnym narzędziem do standaryzacji procesów deweloperskich.
