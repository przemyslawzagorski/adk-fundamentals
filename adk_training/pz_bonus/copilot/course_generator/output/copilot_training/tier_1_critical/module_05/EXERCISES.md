# Ćwiczenia: Inżynieria Kontekstu i Skuteczne Prompty

Pracując z repozytorium `spring-petclinic` (`https://github.com/spring-projects/spring-petclinic`), wykonaj poniższe ćwiczenia, koncentrując się na efektywnym wykorzystaniu GitHub Copilot i świadomym zarządzaniu kontekstem.

## Ćwiczenie 1: Dokumentowanie Warstwy Serwisowej z `@workspace`

**Cel:** Zrozumienie, jak GitHub Copilot może generować holistyczną dokumentację, analizując cały obszar roboczy.

**Kontekst:** Repozytorium `spring-petclinic`. Skupimy się na warstwie `service`.

**Kroki:**
1.  Otwórz dowolny plik z warstwy `service` (np. `OwnerService.java` lub `VetService.java`) w swoim IDE.
2.  W Copilot Chat lub inline chat, użyj promptu podobnego do poniższego, aby poprosić o dokumentację dla całej warstwy serwisowej. Pamiętaj o użyciu `@workspace`.
    ```
    Jako analityk systemowy, przygotuj wysokopoziomowe podsumowanie architektury i działania warstwy serwisowej w projekcie spring-petclinic. Opisz, jakie są główne serwisy (np. OwnerService, PetService, VetService, VisitService), za co odpowiadają i jak ze sobą współpracują. Zwróć uwagę na zależności i przepływ danych między nimi. Użyj @workspace, aby Copilot miał dostęp do wszystkich plików projektu.
    ```
3.  Przeanalizuj wygenerowaną odpowiedź. Czy zawiera ona kompleksowy opis? Czy trafnie identyfikuje zależności?
4.  Spróbuj to samo bez `@workspace` (lub ograniczając kontekst do jednego pliku). Porównaj jakość i zakres wygenerowanej dokumentacji.

**Oczekiwany rezultat:** Szczegółowa dokumentacja tekstowa opisująca interakcje i odpowiedzialności poszczególnych serwisów, uwzględniająca zależności widoczne w całym projekcie. Dokumentacja bez `@workspace` będzie prawdopodobnie uboższa.

**Wskazówki:**
-   Zwróć uwagę na to, czy Copilot poprawnie zidentyfikował wszystkie serwisy i ich główne metody.
-   Sprawdź, czy opisuje zależności między serwisami, np. jak `VisitService` może polegać na `PetService`.

---

## Ćwiczenie 2: Precyzyjny Refaktoring Metody z `#file`

**Cel:** Zastosowanie ograniczonego kontekstu dla precyzyjnych i bezpiecznych zmian w pojedynczym pliku.

**Kontekst:** Repozytorium `spring-petclinic`, plik `VetService.java`.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/vet/VetService.java`.
2.  Zidentyfikuj metodę `findVets()`. Jej obecna implementacja po prostu zwraca `vetRepository.findAll()`.
3.  Użyj Copilot Chat lub inline chat, aby zrefaktoryzować tę metodę. Poproś Copilota o modyfikację metody `findVets()` tak, aby zwracała weterynarzy posortowanych alfabetycznie po nazwisku. Pamiętaj o użyciu `#file`.
    ```
    Zrefaktoryzuj metodę `findVets()` w tym pliku. Chcę, aby zwracała weterynarzy posortowanych alfabetycznie po nazwisku (lastname) przed zwróceniem kolekcji. Użyj Java Stream API do sortowania. Ogranicz kontekst tylko do tego pliku. #file
    ```
4.  Sprawdź wygenerowany kod. Czy Copilot poprawnie zaimportował `java.util.Comparator` i `java.util.stream.Collectors`? Czy metoda działa zgodnie z oczekiwaniami?

**Oczekiwany rezultat:** Metoda `findVets()` w `VetService.java` została zmodyfikowana, aby sortować weterynarzy po nazwisku za pomocą Stream API. Żadne inne pliki nie powinny zostać zmodyfikowane ani zasugerowane do modyfikacji.

**Wskazówki:**
-   Upewnij się, że Copilot dodał niezbędne importy do pliku.
-   Zweryfikuj, czy sortowanie działa poprawnie (np. wizualnie, jeśli uruchomisz aplikację i przejrzysz listę weterynarzy).

---

## Ćwiczenie 3: Optymalizacja "Token Window" poprzez Selekcję Kontekstu

**Cel:** Zrozumienie, jak świadomie wybierać pliki do kontekstu, aby optymalizować "token window" i uzyskać lepsze sugestie.

**Kontekst:** Repozytorium `spring-petclinic`, klasy `PetController`, `OwnerController`, `VisitController`.

**Kroki:**
1.  Wyobraź sobie, że chcesz poprosić Copilota o zaproponowanie wspólnej klasy bazowej (np. abstrakcyjnej) dla DTO (Data Transfer Objects), które mogłyby być używane przez `PetController`, `OwnerController` i `VisitController`. Takie DTO miałyby zawierać wspólne pola, takie jak `id` czy `name`.
2.  Spróbuj najpierw użyć promptu bez jawnego wskazywania plików, zakładając, że masz otwarte te trzy kontrolery.
    ```
    Zaproponuj abstrakcyjną klasę bazową dla DTO, która mogłaby być używana przez PetController, OwnerController i VisitController. Powinna zawierać wspólne pola, takie jak ID i Name. Wygeneruj kod tej klasy.
    ```
3.  Następnie spróbuj z jawnie wskazanymi plikami (użyj ` @file:path/to/PetController.java @file:path/to/OwnerController.java @file:path/to/VisitController.java` w Copilot Chat lub jako komentarz w nowym pliku):
    ```
    Zaproponuj abstrakcyjną klasę bazową dla DTO, która mogłaby być używana przez PetController, OwnerController i VisitController. Powinna zawierać wspólne pola, takie jak ID i Name. Wygeneruj kod tej klasy. Kontekst:
    @file:src/main/java/org/springframework/samples/petclinic/pet/PetController.java
    @file:src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java
    @file:src/main/java/org/springframework/samples/petclinic/pet/VisitController.java
    ```
4.  Porównaj sugestie. Czy sugestia z jawnym wskazaniem plików jest bardziej precyzyjna, uwzględnia więcej specyficznych cech tych kontrolerów?

**Oczekiwany rezultat:** Sugestia z jawnym wskazaniem plików powinna być bardziej dopasowana do kontekstu `spring-petclinic` i potencjalnie lepiej uwzględniać struktury DTO używane w tych kontrolerach, niż ogólna sugestia.

**Wskazówki:**
-   Zauważ, że `VisitController` w `spring-petclinic` jest często zintegrowany z `PetController` lub `OwnerController`, nie zawsze występuje jako osobna klasa. Możesz wybrać inne kontrolery lub serwisy, jeśli to konieczne.
-   Copilot może zasugerować, że `NamedEntity` jest już taką klasą bazową, co jest dobrą obserwacją!

---

## Ćwiczenie 4: Generowanie Testów Integracyjnych dla `OwnerController`

**Cel:** Praktyczne zastosowanie zaawansowanych promptów do generowania kompleksowych testów integracyjnych z wykorzystaniem `MockMvc`.

**Kontekst:** Repozytorium `spring-petclinic`, `OwnerController.java`.

**Kroki:**
1.  Stwórz nowy plik testowy: `src/test/java/org/springframework/samples/petclinic/owner/OwnerControllerIntegrationTests.java`.
2.  Wklej do niego prompt (lub użyj Copilot Chat), prosząc o wygenerowanie testów integracyjnych dla `OwnerController`.
    ```
    Jako doświadczony inżynier testów, napisz kompleksową klasę testów integracyjnych dla `OwnerController.java` w projekcie `spring-petclinic`. Klasa powinna nazywać się `OwnerControllerIntegrationTests` i używać `Spring MockMvc` oraz `JUnit 5`. Obejmij testy dla następujących scenariuszy:
    - Pomyślne dodanie nowego właściciela (POST /owners/new) i weryfikacja przekierowania.
    - Dodanie właściciela z brakującymi lub niepoprawnymi danymi (POST /owners/new), weryfikacja błędów walidacji i powrotu do formularza.
    - Wyszukiwanie właścicieli po nazwisku, które nie istnieje (GET /owners), weryfikacja, że strona wyszukiwania jest ponownie renderowana z informacją o braku wyników.
    - Wyszukiwanie właścicieli po częściowym nazwisku, które zwraca tylko jeden wynik (GET /owners), weryfikacja przekierowania do strony szczegółów tego właściciela.
    - Wyszukiwanie właścicieli po częściowym nazwisku, które zwraca wiele wyników (GET /owners), weryfikacja, że wyświetlona jest lista właścicieli.
    Użyj `@MockBean` dla `OwnerRepository` i zasymuluj jego zachowanie za pomocą `BDDMockito.given()` w metodzie `@BeforeEach`.
    ```
3.  Copilot powinien wygenerować całą strukturę klasy testowej wraz z metodami testowymi.
4.  Zweryfikuj, czy wygenerowane testy są poprawne i używają odpowiednich asercji `MockMvc`.

**Oczekiwany rezultat:** Pełna klasa testowa `OwnerControllerIntegrationTests` z pięcioma metodami testowymi, które weryfikują różne aspekty działania `OwnerController`.

**Wskazówki:**
-   Może być konieczne ręczne dodanie brakujących importów, jeśli Copilot ich nie uwzględnił.
-   Sprawdź, czy `BDDMockito` jest poprawnie skonfigurowane, aby mockować repozytorium.

---

## Ćwiczenie 5: Iteracyjne Udoskonalanie Promptu - Walidacja Wieku Zwierzęcia

**Cel:** Praktyka iteracyjnego udoskonalania promptów w celu uzyskania precyzyjnego i idiomatycznego dla frameworka rozwiązania.

**Kontekst:** Repozytorium `spring-petclinic`, pliki `Pet.java` i `PetController.java`. Chcemy dodać walidację wieku zwierzęcia (`age`) tak, aby było ono zawsze dodatnie.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/pet/Pet.java`.
2.  **Iteracja 1 (prosty prompt):** W Copilot Chat, wpisz: "W klasie Pet.java, dodaj walidację, aby pole age było dodatnie."
    *   Przeanalizuj odpowiedź. Czy wystarczy? Czy jest zgodna ze Spring Validation?
3.  **Iteracja 2 (ulepszony prompt - dodajemy szczegóły Spring Validation):** "W klasie `Pet.java`, upewnij się, że pole `age` jest wymagane (nie null) i jest większe od zera. Użyj adnotacji walidacyjnych `@NotNull` i `@Min(1)`. Zapewnij, że komunikaty błędów są opisowe, np. `Wiek jest wymagany` i `Wiek musi być dodatni`."
    *   Zastosuj zmiany w `Pet.java`. Przeanalizuj wygenerowane adnotacje i komunikaty.
4.  **Iteracja 3 (integracja z kontrolerem):** Teraz otwórz `src/main/java/org/springframework/samples/petclinic/pet/PetController.java`. W Copilot Chat, wpisz:
    ```
    Jako doświadczony programista Spring Boot, zaktualizuj metodę `processUpdateForm` w PetController.java. Po dodaniu adnotacji `@NotNull` i `@Min(1)` do pola `age` w `Pet.java`, upewnij się, że ta metoda poprawnie obsługuje błędy walidacji z `BindingResult`. W przypadku błędów walidacji, formularz `pets/createOrUpdatePetForm` powinien zostać ponownie renderowany, przekazując `pet` i `owner` do modelu. Upewnij się, że komunikaty walidacyjne z adnotacji są wyświetlane. Ogranicz kontekst do `PetController.java` i `Pet.java`.
    ```
    *   Zastosuj zmiany. Przetestuj, uruchamiając aplikację i próbując edytować zwierzę z wiekiem 0 lub ujemnym. Czy komunikaty walidacji są wyświetlane poprawnie?

**Oczekiwany rezultat:** Klasa `Pet.java` powinna mieć adnotacje `@NotNull` i `@Min(1)` na polu `age`. Metoda `processUpdateForm` w `PetController.java` powinna prawidłowo przetwarzać `BindingResult` i ponownie renderować formularz z komunikatami błędów walidacji, jeśli wiek jest niepoprawny.

**Wskazówki:**
-   Pamiętaj o dodaniu `@Valid` do argumentu `Pet` w metodach `processCreationForm` i `processUpdateForm` w `PetController`, jeśli jeszcze go tam nie ma.
-   Dla testów, możesz również dodać test jednostkowy w `PetTests.java` (jeśli istnieje) lub w `PetControllerIntegrationTests` (z Ćwiczenia 4), aby sprawdzić walidację.

---

## Ćwiczenie 6: Generowanie Adnotacji Swagger/OpenAPI dla Endpointów

**Cel:** Wykorzystanie Copilota do automatyzacji generowania dokumentacji API za pomocą adnotacji.

**Kontekst:** Repozytorium `spring-petclinic`, plik `OwnerController.java`.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`.
2.  Dodaj zależności Swagger/OpenAPI do `pom.xml` (jeśli nie ma). Możesz poprosić o to Copilota w osobnym prompcie.
3.  Dla wybranej metody (np. `showOwner` lub `processCreationForm`), poproś Copilota o dodanie adnotacji Swagger/OpenAPI, które opiszą endpoint, jego parametry, możliwe kody odpowiedzi HTTP (np. 200 OK, 400 Bad Request, 404 Not Found) i ich schematy.
    ```
    W metodzie `showOwner` w OwnerController.java, dodaj adnotacje Swagger/OpenAPI (@Operation, @ApiResponse itp.), które szczegółowo opiszą ten endpoint. Ogranicz kontekst do tego pliku. #file
    ```
4.  Przeanalizuj wygenerowane adnotacje. Czy są poprawne i kompleksowe?

**Oczekiwany rezultat:** Metoda `showOwner` (lub inna wybrana) w `OwnerController.java` powinna być wzbogacona o adnotacje Javadoc i Swagger/OpenAPI, które dokładnie dokumentują jej działanie.

**Wskazówki:**
-   Możesz potrzebować specyficznych importów dla adnotacji Swagger, np. z `io.swagger.v3.oas.annotations.*`.
-   Zwróć uwagę, czy Copilot prawidłowo inferuje typy parametrów i odpowiedzi HTTP.

---

## Ćwiczenie 7: Implementacja Wzorca DTO dla Encji `Owner`

**Cel:** Użycie Copilota do tworzenia warstw abstrakcji (DTO) i mapowania danych.

**Kontekst:** Repozytorium `spring-petclinic`, encja `Owner.java`.

**Kroki:**
1.  Stwórz nowy plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerDto.java`.
2.  W Copilot Chat, poproś o wygenerowanie klasy `OwnerDto` na podstawie encji `Owner.java`. Klasa `OwnerDto` powinna zawierać tylko pola, które są prezentowane w interfejsie użytkownika (np. `id`, `firstName`, `lastName`, `address`, `city`, `telephone`), bez kolekcji zwierząt.
    ```
    Jako programista Spring, wygeneruj klasę `OwnerDto` w języku Java, która będzie Data Transfer Object dla encji `Owner.java` z projektu spring-petclinic. `OwnerDto` powinien zawierać pola `id`, `firstName`, `lastName`, `address`, `city`, `telephone`. Dodaj również metody statyczne `fromEntity(Owner owner)` i `toEntity(OwnerDto ownerDto, Owner owner)` do mapowania między `Owner` a `OwnerDto`. Kontekst: @file:src/main/java/org/springframework/samples/petclinic/owner/Owner.java
    ```
3.  Przeanalizuj wygenerowaną klasę DTO i metody mapujące. Czy są poprawne?
4.  (Opcjonalnie) Zmodyfikuj `OwnerController`, aby używał `OwnerDto` w metodach tworzenia i edycji właścicieli.

**Oczekiwany rezultat:** Nowa klasa `OwnerDto.java` z odpowiednimi polami i dwiema metodami statycznymi do konwersji między `Owner` a `OwnerDto`.

**Wskazówki:**
-   Zwróć uwagę, czy Copilot poprawnie zignorował kolekcję `pets` z encji `Owner`.
-   Metoda `toEntity` powinna aktualizować istniejący obiekt `Owner`, a nie tworzyć nowy, aby zachować ciągłość encji zarządzanej przez JPA.

---

## Ćwiczenie 8: Refaktoryzacja Metod Pomocniczych do Osobnej Klasy

**Cel:** Wykorzystanie Copilota do poprawy organizacji kodu poprzez ekstrakcję logiki.

**Kontekst:** Repozytorium `spring-petclinic`, klasa `OwnerService.java`.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerService.java`.
2.  Wyobraź sobie, że w `OwnerService` dodajesz skomplikowaną logikę walidacji adresu, która może być używana w wielu miejscach. Chcesz przenieść ją do osobnej klasy pomocniczej.
3.  Poproś Copilota o stworzenie nowej klasy pomocniczej `AddressValidator.java` w tym samym pakiecie, która będzie zawierała metodę `isValidAddress(String address, String city)`. Zaimplementuj w niej prostą logikę walidacji (np. adres nie może być pusty, miasto musi być na liście predefiniowanych miast).
    ```
    Jako programista Java Spring, stwórz nową klasę publiczną `AddressValidator` w tym pakiecie. Powinna zawierać publiczną statyczną metodę `boolean isValidAddress(String address, String city)`. Zaimplementuj prostą logikę: adres i miasto nie mogą być puste, a miasto musi być jednym z: "Madison", "Sun Prairie", "Denver". Użyj #file. Następnie w OwnerService.java, zaktualizuj metodę `saveOwner`, aby używała tej nowej klasy do walidacji adresu przed zapisem właściciela. Jeśli adres jest niepoprawny, rzuć `IllegalArgumentException`. #file
    ```
4.  Copilot powinien najpierw wygenerować `AddressValidator.java`, a następnie zasugerować zmiany w `OwnerService.java`.
5.  Przeanalizuj wygenerowany kod i zastosuj zmiany.

**Oczekiwany rezultat:** Nowa klasa `AddressValidator.java` z metodą walidacji adresu oraz zaktualizowana metoda `saveOwner` w `OwnerService.java`, która korzysta z tej walidacji.

**Wskazówki:**
-   Zwróć uwagę, czy Copilot poprawnie obsługuje błąd walidacji w `OwnerService` (np. przez rzucenie wyjątku).
-   Pamiętaj o dodaniu niezbędnych importów.

---

## Ćwiczenie 9: Generowanie Zapytań JPA/Hibernate z Opisów

**Cel:** Tworzenie złożonych zapytań bazodanowych przy pomocy Copilota na podstawie naturalnego języka.

**Kontekst:** Repozytorium `spring-petclinic`, interfejs `OwnerRepository.java`.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java`.
2.  Poproś Copilota o dodanie do tego interfejsu nowej metody, która będzie wyszukiwać właścicieli spełniających określone kryteria.
    ```
    W OwnerRepository.java, dodaj nową metodę, która znajdzie wszystkich właścicieli (Owner) posiadających zwierzęta (Pet) o określonym typie (PetType). Metoda powinna przyjmować jako argument nazwę typu zwierzęcia (String petTypeName) i zwracać kolekcję Ownerów. Wykorzystaj Named Query lub Query Method w Spring Data JPA. #file
    ```
3.  Copilot powinien zasugerować deklarację metody w interfejsie `OwnerRepository` z odpowiednim zapytaniem (np. `@Query` lub nazwą metody zgodną z konwencją Spring Data JPA).
4.  Zweryfikuj poprawność wygenerowanego zapytania.

**Oczekiwany rezultat:** Nowa metoda w `OwnerRepository.java` z adnotacją `@Query` lub odpowiednią nazwą metody, która realizuje wyszukiwanie właścicieli po typie zwierzęcia.

**Wskazówki:**
-   Spring Data JPA pozwala na tworzenie zapytań na podstawie nazw metod. Copilot powinien być w stanie to wykorzystać.
-   Upewnij się, że zapytanie poprawnie łączy encje `Owner` i `Pet` oraz `PetType`.

---

## Ćwiczenie 10: Analiza i Sugestie Dotyczące Wydajności Kodu

**Cel:** Wykorzystanie Copilota do identyfikacji potencjalnych problemów z wydajnością i uzyskania sugestii optymalizacyjnych.

**Kontekst:** Repozytorium `spring-petclinic`, metoda `VetService.findVets()` lub `OwnerRepository.findByLastName()` (lub inna wybrana, która może być intensywna).

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/vet/VetService.java`.
2.  Zidentyfikuj metodę `findVets()`. Załóżmy, że repozytorium `vetRepository.findAll()` zwraca bardzo dużą kolekcję weterynarzy.
3.  Poproś Copilota o przeanalizowanie tej metody pod kątem potencjalnych problemów z wydajnością i zaproponowanie optymalizacji. Możesz użyć promptu w Copilot Chat:
    ```
    Przeanalizuj metodę `findVets()` w pliku `VetService.java` pod kątem potencjalnych problemów z wydajnością, zakładając, że `vetRepository.findAll()` może zwracać bardzo dużą liczbę rekordów. Zaproponuj optymalizacje, które mogą poprawić wydajność, np. stronicowanie, lazy loading, czy indeksowanie. Ogranicz kontekst do tego pliku. #file
    ```
4.  Copilot powinien zasugerować zmiany w kodzie lub ogólne rekomendacje.
5.  Przeanalizuj sugestie. Czy są one sensowne w kontekście JPA i Spring Data?

**Oczekiwany rezultat:** Sugestie optymalizacyjne, takie jak wprowadzenie stronicowania (`Pageable`), dodanie adnotacji `@EntityGraph` dla eager loading konkretnych zależności lub rozważenie lazy loading tam, gdzie to możliwe, oraz wskazanie na optymalizacje bazodanowe (indeksy).

**Wskazówki:**
-   Copilot może zasugerować zmiany w `VetRepository`, takie jak metody zwracające `Page<Vet>` zamiast `Collection<Vet>`.
-   Pamiętaj, że implementacja sugerowanych zmian może wymagać modyfikacji również w kontrolerach.

---

## Ćwiczenie 11: Zastosowanie Wzorca Factory Method dla Tworzenia Zwierząt

**Cel:** Implementacja wzorców projektowych z pomocą Copilota.

**Kontekst:** Repozytorium `spring-petclinic`, tworzenie obiektów `Pet`.

**Kroki:**
1.  Wyobraź sobie, że chcesz wprowadzić bardziej elastyczny sposób tworzenia obiektów `Pet`, w zależności od ich typu. Chcesz zastosować wzorzec Factory Method.
2.  Poproś Copilota o wygenerowanie interfejsu `PetFactory` oraz kilku implementacji, np. `DogFactory`, `CatFactory`, `HamsterFactory`, które będą tworzyć odpowiednie obiekty `Pet`.
    ```
    Jako projektant oprogramowania, zaimplementuj wzorzec Factory Method w projekcie spring-petclinic dla tworzenia obiektów Pet. Stwórz interfejs `PetFactory` z metodą `createPet()`. Następnie zaimplementuj trzy konkretne fabryki: `DogFactory`, `CatFactory` i `HamsterFactory`. Każda fabryka powinna tworzyć instancję `Pet` z odpowiednim `PetType` (np. 'dog', 'cat', 'hamster') i ustawiać domyślne wartości, np. datę urodzenia na dzisiaj. Umieść to w nowym pakiecie `org.springframework.samples.petclinic.factory`. #workspace
    ```
3.  Copilot powinien wygenerować interfejs `PetFactory` i trzy klasy implementujące.
4.  Przeanalizuj wygenerowany kod. Czy poprawnie implementuje wzorzec Factory Method? Czy `PetType` jest poprawnie ustawiany?

**Oczekiwany rezultat:** Nowy pakiet `org.springframework.samples.petclinic.factory` zawierający interfejs `PetFactory` oraz klasy `DogFactory`, `CatFactory`, `HamsterFactory`, każda z metodą `createPet()`.

**Wskazówki:**
-   Zwróć uwagę, że `PetType` jest encją. Copilot powinien uwzględnić sposób, w jaki `PetType` jest zarządzany w `spring-petclinic` (np. przez `PetService.findPetTypeByName()`).
-   Możesz poprosić o dodanie metody `getPetType()` do `PetService` jeśli taka nie istnieje.

---

## Ćwiczenie 12: Generowanie Przykładów Użycia dla Nowej Funkcji

**Cel:** Szybkie tworzenie przykładów kodu dla nowych lub istniejących funkcji.

**Kontekst:** Repozytorium `spring-petclinic`, klasa `VisitService.java`.

**Kroki:**
1.  Wyobraź sobie, że dodajesz nową metodę do `VisitService.java`, np. `scheduleFutureVisit(Pet pet, LocalDate date, String description)`. Dodaj tę metodę (może być pusta implementacja) do `VisitService`.
2.  W pliku testowym (np. nowym `VisitServiceTests.java` lub istniejącym `VisitServiceTests` jeśli istnieje), poproś Copilota o wygenerowanie trzech przykładów użycia dla tej metody.
    ```
    Jako programista Java, napisz trzy różne przykłady użycia dla metody `scheduleFutureVisit(Pet pet, LocalDate date, String description)` w `VisitService.java`. Pokaż, jak można zaplanować wizytę w różnych scenariuszach, np. dla różnych zwierząt, z różnymi datami i opisami. Wygeneruj fragmenty kodu, które można wkleić do metody testowej. Kontekst: @file:src/main/java/org/springframework/samples/petclinic/visit/VisitService.java
    ```
3.  Copilot powinien wygenerować fragmenty kodu demonstrujące użycie metody.
4.  Przeanalizuj wygenerowane przykłady. Czy są zrozumiałe i pokazują różnorodność użycia?

**Oczekiwany rezultat:** Trzy fragmenty kodu w Javie, które demonstrują, jak wywołać metodę `scheduleFutureVisit` z różnymi argumentami.

**Wskazówki:**
-   Copilot może zasugerować użycie `LocalDate.of()` i tworzenie przykładowych obiektów `Pet`.
-   Pamiętaj, aby dodać niezbędne importy, jeśli generowane przykłady ich wymagają.

---

## Ćwiczenie 13: Refaktoryzacja `PetType` do Enuma dla Prostoty

**Cel:** Wykorzystanie Copilota do zmiany struktury danych i refaktoryzacji kodu, jeśli kontekst na to pozwala.

**Kontekst:** Repozytorium `spring-petclinic`, klasa `PetType.java` (która jest encją).

**Kroki:**
1.  Zauważ, że `PetType` jest encją z tylko dwoma polami (`id` i `name`). W wielu aplikacjach, jeśli typy są stałe i niezmienne, lepiej jest użyć enuma.
2.  Poproś Copilota o refaktoryzację `PetType.java` z klasy encji na `enum`. Zapewnij, że wszystkie miejsca, które odwołują się do `PetType` (np. w `Pet.java`, `PetService.java`, `PetRepository.java`), zostaną zaktualizowane.
    ```
    Jako doświadczony programista Java, zrefaktoryzuj encję `PetType.java` w projekcie spring-petclinic na typ wyliczeniowy (enum). Załóż, że typy zwierząt są stałe (cat, dog, hamster, lizard, snake, bird). Następnie zaktualizuj wszystkie miejsca w kodzie, które odwołują się do `PetType`, w szczególności `Pet.java`, `PetService.java` i `PetRepository.java`, aby korzystały z nowego enuma. Użyj @workspace, aby zapewnić kompleksową refaktoryzację. 
    ```
3.  Copilot powinien zasugerować zmiany w `PetType.java`, a następnie w innych plikach.
4.  **UWAGA:** To ćwiczenie jest trudne i może wymagać wielu iteracji oraz manualnych poprawek, ponieważ zmiana encji na enum jest dużą modyfikacją wpływającą na wiele warstw. Copilot może potrzebować pomocy w zarządzaniu zależnościami JPA.

**Oczekiwany rezultat:** Klasa `PetType.java` zostaje zastąpiona przez `enum PetType`. Wszystkie odwołania do niej są zaktualizowane do używania nowej struktury.

**Wskazówki:**
-   Zwróć szczególną uwagę na to, jak Copilot radzi sobie z mapowaniem JPA (`@Enumerated` może być potrzebny).
-   To ćwiczenie może być dobrym przykładem, kiedy Copilot jest pomocny, ale wymaga aktywnego nadzoru i korekty ze strony programisty.

---

## Ćwiczenie 14: Optymalizacja Importów i Usunięcie Niewykorzystanych Zależności

**Cel:** Wykorzystanie Copilota do utrzymywania czystości i optymalizacji kodu, również w zakresie zależności.

**Kontekst:** Dowolny plik Java w `spring-petclinic` zawierający potencjalnie nieużywane importy lub `pom.xml` z nieużywanymi zależnościami.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
2.  Ręcznie dodaj kilka nieużywanych importów do tego pliku (np. `import java.util.LinkedList;`, `import java.sql.Date;`).
3.  Poproś Copilota o optymalizację importów w tym pliku.
    ```
    Zoptymalizuj importy w tym pliku Java, usuwając wszystkie nieużywane. #file
    ```
4.  Copilot powinien usunąć zbędne importy.
5.  Otwórz `pom.xml`. Wyobraź sobie, że usunąłeś jakąś funkcjonalność i pewna zależność (np. `spring-boot-starter-validation`, jeśli wcześniej nie była używana) stała się zbędna. Poproś Copilota o zidentyfikowanie i usunięcie nieużywanych zależności z `pom.xml`.
    ```
    Jako ekspert Maven, przeanalizuj ten plik pom.xml i zidentyfikuj oraz usuń wszystkie deklarowane zależności, które nie są używane w projekcie. Zwróć tylko zaktualizowany plik pom.xml. #file
    ```
6.  Przeanalizuj sugestie. Czy Copilot poprawnie zidentyfikował nieużywane zależności?

**Oczekiwany rezultat:** Zoptymalizowane importy w pliku Java oraz zaktualizowany `pom.xml` z usuniętymi nieużywanymi zależnościami (o ile Copilot był w stanie je zidentyfikować na podstawie heurystyk).

**Wskazówki:**
-   Copilot jest bardzo dobry w optymalizacji importów w pojedynczym pliku. Identyfikacja nieużywanych zależności w `pom.xml` jest trudniejsza, ponieważ wymaga analizy całego projektu.
-   Dla `pom.xml`, Copilot może potrzebować więcej kontekstu lub bardziej precyzyjnego promptu, jeśli nie jest w stanie sam określić, czy zależność jest używana.

---

## Ćwiczenie 15: Generowanie Query Methods w Repozytorium

**Cel:** Szybkie tworzenie metod zapytań w Spring Data JPA na podstawie konwencji nazewnictwa.

**Kontekst:** Repozytorium `spring-petclinic`, interfejs `PetRepository.java`.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/pet/PetRepository.java`.
2.  W interfejsie `PetRepository`, zacznij pisać komentarz Javadoc dla nowej metody, która będzie wyszukiwać zwierzęta.
    ```java
    /**
     * Znajduje wszystkie zwierzęta (Pet) należące do danego właściciela (Owner), których wiek jest większy niż podana wartość.
     * Sortuje wyniki po imieniu zwierzęcia.
     *
     * @param ownerId ID właściciela
     * @param minAge minimalny wiek
     * @return Kolekcja zwierząt spełniających kryteria
     */
    // public Collection<Pet> findByOwnerIdAndAgeGreaterThanOrderBy... (kontynuuj z Copilotem)
    ```
3.  Po napisaniu komentarza i części nazwy metody, pozwól Copilotowi zasugerować pełną deklarację metody zgodnie z konwencją Query Methods w Spring Data JPA.
4.  Copilot powinien wygenerować coś podobnego do:
    ```java
    Collection<Pet> findByOwnerIdAndAgeGreaterThanOrderByName(Integer ownerId, Integer minAge);
    ```
5.  Zweryfikuj poprawność wygenerowanej metody.

**Oczekiwany rezultat:** Nowa metoda w `PetRepository.java`, której nazwa automatycznie tworzy zapytanie SQL, zgodnie z intencją wyrażoną w komentarzu Javadoc.

**Wskazówki:**
-   To ćwiczenie pokazuje, jak Copilot potrafi "rozumieć" intencje z komentarzy i przekształcać je w kod zgodny z frameworkiem.
-   Pamiętaj o dodaniu niezbędnych importów, jeśli Copilot ich nie uwzględnił.

---
