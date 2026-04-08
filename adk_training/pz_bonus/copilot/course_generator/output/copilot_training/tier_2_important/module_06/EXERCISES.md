# Ćwiczenia: Copilot Chat - Podstawy

## Ćwiczenie 1: Wyjaśnienie metody z repozytorium `spring-petclinic`

**Cel:** Użycie Copilot Chat do zrozumienia działania istniejącego kodu.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Chcesz szybko zrozumieć, jak działa metoda odpowiedzialna za wyszukiwanie właścicieli zwierząt.

**Kroki:**
1. Otwórz projekt `spring-petclinic` w VS Code.
2. Przejdź do pliku `OwnerRepository.java` (ścieżka: `src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java`).
3. Zlokalizuj metodę `findByLastName(String lastName)`.
4. Zaznacz całą sygnaturę i ciało metody `findByLastName`.
5. Otwórz panel Copilot Chat i wpisz komendę `/explain`.
6. Przeczytaj wyjaśnienie dostarczone przez Copilota.

**Oczekiwany rezultat:** Copilot Chat powinien dostarczyć zwięzłe i dokładne wyjaśnienie działania metody `findByLastName`, w tym jej celu (znajdowanie właścicieli po nazwisku), parametrów i zwracanego typu.

**Wskazówki:**
- Upewnij się, że masz aktywne połączenie z internetem i Copilot jest zalogowany.
- Jeśli wyjaśnienie jest zbyt ogólne, możesz spróbować dodać kontekst, np. "Wyjaśnij tę metodę, biorąc pod uwagę, że to jest interfejs Spring Data JPA."

---

## Ćwiczenie 2: Refaktoryzacja prostej metody

**Cel:** Wykorzystanie Copilot Chat do refaktoryzacji fragmentu kodu w celu poprawy jego czytelności lub wydajności.

**Kontekst:** Masz małą metodę pomocniczą, którą chciałbyś ulepszyć.

**Kroki:**
1. W projekcie `spring-petclinic`, utwórz nową, prostą metodę pomocniczą w pliku `PetService.java` (ścieżka: `src/main/java/org/springframework/samples/petclinic/pet/PetService.java`). Na przykład, metodę, która przyjmuje string z datą i parsuje go na `LocalDate` (bez obsługi błędów).
   ```java
   // Przykład prostej metody do refaktoryzacji
   public LocalDate parseDateString(String dateString) {
       return LocalDate.parse(dateString);
   }
   ```
2. Zaznacz nowo utworzoną metodę `parseDateString`.
3. W Copilot Chat wpisz komendę `/refactor Make this method more robust and add error handling.`.
4. Przejrzyj propozycje refaktoryzacji od Copilota. Zauważ, jak Copilot sugeruje dodanie `try-catch` lub użycie `DateTimeFormatter`.
5. Wybierz jedną z propozycji lub zmodyfikuj kod ręcznie, bazując na sugestiach.

**Oczekiwany rezultat:** Metoda `parseDateString` powinna zostać zmodyfikowana tak, aby była bardziej odporna na błędy (np. poprzez dodanie obsługi `DateTimeParseException`) i potencjalnie bardziej czytelna.

**Wskazówki:**
- Jeśli Copilot nie oferuje wystarczająco dobrych propozycji, spróbuj być bardziej precyzyjny w swoim promptcie, np. "Refaktoryzuj tę metodę, aby używała `DateTimeFormatter` i bezpiecznie obsługiwała błędy parsowania daty."

---

## Ćwiczenie 3: Generowanie komentarzy Javadoc

**Cel:** Użycie Copilot Chat do szybkiego generowania dokumentacji dla metody.

**Kontekst:** W projekcie `spring-petclinic` potrzebujesz dodać standardowe komentarze Javadoc do istniejącej metody kontrolera.

**Kroki:**
1. Otwórz plik `OwnerController.java` (ścieżka: `src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java`).
2. Zlokalizuj metodę `processNewOwnerForm(@Valid Owner owner, BindingResult result)`.
3. Zaznacz całą sygnaturę i ciało metody `processNewOwnerForm`.
4. Otwórz panel Copilot Chat i wpisz komendę `/doc`.
5. Przejrzyj wygenerowane komentarze Javadoc. Zwróć uwagę na to, czy poprawnie opisują parametry i zwracany typ.
6. Wstaw wygenerowane komentarze nad metodą.

**Oczekiwany rezultat:** Nad metodą `processNewOwnerForm` powinny pojawić się dobrze sformatowane komentarze Javadoc, opisujące cel metody, jej parametry (`owner`, `result`) i zwracany typ (`String`).

**Wskazówki:**
- Po wygenerowaniu komentarzy, zawsze sprawdź ich poprawność i upewnij się, że są zgodne z rzeczywistym działaniem metody. Czasem Copilot może wymagać drobnych poprawek.

---

## Ćwiczenie 4: Prośba o implementację wzorca projektowego

**Cel:** Wykorzystanie Copilot Chat do uzyskania pomocy w implementacji wzorca projektowego dla istniejącej klasy.

**Kontekst:** Chcesz zastosować wzorzec projektowy Builder do klasy `Pet` w `spring-petclinic`, aby ułatwić tworzenie nowych instancji `Pet` z wieloma opcjonalnymi atrybutami.

**Kroki:**
1. Otwórz plik `Pet.java` (ścieżka: `src/main/java/org/springframework/samples/petclinic/pet/Pet.java`).
2. Otwórz panel Copilot Chat.
3. Wpisz szczegółowy prompt: "W jaki sposób mogę zaimplementować wzorzec projektowy Builder dla klasy `Pet` z projektu `spring-petclinic` w Javie, aby ułatwić tworzenie nowych obiektów `Pet` z różnymi kombinacjami pól? Pokaż mi przykład użycia."
4. Przeanalizuj odpowiedź Copilota. Powinien zaproponować strukturę klasy `PetBuilder` z metodami do ustawiania poszczególnych pól i metodą `build()`.
5. Spróbuj zaimplementować wzorzec `Builder` w klasie `Pet` lub w nowej klasie testowej, korzystając z sugestii Copilota.

**Oczekiwany rezultat:** Otrzymasz propozycję kodu dla wzorca Builder dla klasy `Pet`, wraz z przykładem jego użycia. Będziesz w stanie zrozumieć, jak zastosować ten wzorzec do klasy `Pet`.

**Wskazówki:**
- Copilot może dostarczyć różne implementacje wzorca Builder (np. wewnętrzna klasa statyczna, zewnętrzna klasa). Wybierz tę, która najlepiej pasuje do Twojego stylu kodowania.
- Jeśli odpowiedź jest zbyt długa lub niejasna, poproś o uproszczenie lub skupienie się na konkretnych aspektach.
