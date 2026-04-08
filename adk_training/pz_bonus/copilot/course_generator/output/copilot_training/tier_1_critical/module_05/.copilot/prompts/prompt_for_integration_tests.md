Jako doświadczony inżynier testów, napisz kompleksową klasę testów integracyjnych dla `OwnerController.java` w projekcie `spring-petclinic`. Klasa powinna nazywać się `OwnerControllerIntegrationTests` i używać `Spring MockMvc` oraz `JUnit 5`. Obejmij testy dla następujących scenariuszy:
1.  Pomyślne dodanie nowego właściciela (POST /owners/new) i weryfikacja przekierowania.
2.  Dodanie właściciela z brakującymi lub niepoprawnymi danymi (POST /owners/new), weryfikacja błędów walidacji i powrotu do formularza.
3.  Wyszukiwanie właścicieli po nazwisku, które nie istnieje (GET /owners), weryfikacja, że strona wyszukiwania jest ponownie renderowana.
4.  Wyszukiwanie właścicieli po częściowym nazwisku, które zwraca tylko jeden wynik (GET /owners), weryfikacja przekierowania do strony szczegółów tego właściciela.
5.  Wyszukiwanie właścicieli po częściowym nazwisku, które zwraca wiele wyników (GET /owners), weryfikacja, że wyświetlona jest lista właścicieli.
Użyj `@MockBean` dla `OwnerRepository` i zasymuluj jego zachowanie za pomocą `BDDMockito.given()` w metodzie `@BeforeEach`.
Zwróć tylko kod źródłowy klasy testowej w Javie.