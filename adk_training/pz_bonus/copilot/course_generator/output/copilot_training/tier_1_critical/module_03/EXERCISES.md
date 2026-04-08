# Ćwiczenia: Customization - Dostosowanie GitHub Copilot do Twojego Projektu

## Ćwiczenie 1: Wymuszanie stylu formatowania kodu w spring-petclinic

**Cel:** Skonfiguruj GitHub Copilot, aby przestrzegał określonych zasad formatowania kodu Java w projekcie `spring-petclinic`.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Chcesz, aby wszystkie nowe klasy i modyfikacje były zgodne z konwencjami, które preferują użycie Lomboka dla boilerplate kodu i wstrzykiwanie zależności przez konstruktor.

**Kroki:**
1.  Otwórz projekt `spring-petclinic` w swoim IDE.
2.  Utwórz plik `.github/copilot-instructions.md` (jeśli jeszcze nie istnieje) w głównym katalogu projektu (`output/copilot_training/tier_1_critical/module_03/.github/copilot-instructions.md`).
3.  Dodaj do tego pliku instrukcje, które jasno określają:
    *   Preferencję dla adnotacji Lombok (`@Getter`, `@Setter`, `@NoArgsConstructor`, `@AllArgsConstructor`) do generowania standardowych metod.
    *   Wymóg wstrzykiwania zależności przez konstruktor dla komponentów Spring (np. w serwisach, kontrolerach).
    *   Przykłady kodu ilustrujące te zasady.
4.  Otwórz istniejącą klasę (np. `Owner.java` w `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`) i usuń istniejące gettery/settery. Następnie spróbuj wygenerować je ponownie za pomocą Copilota. Sprawdź, czy Copilot zasugeruje użycie adnotacji Lombok.
5.  Utwórz nową klasę serwisu (np. `NewService.java`) i poproś Copilota o dodanie zależności do istniejącego repozytorium (np. `OwnerRepository`). Zweryfikuj, czy wstrzykiwanie zależności odbywa się przez konstruktor.

**Oczekiwany rezultat:** Copilot powinien konsekwentnie sugerować użycie adnotacji Lombok i wstrzykiwanie zależności przez konstruktor w plikach `.java` w projekcie.

**Wskazówki:**
-   Pamiętaj, że instrukcje w `copilot-instructions.md` działają najlepiej, gdy są zwięzłe i zawierają konkretne przykłady kodu.
-   Wykorzystaj bloki kodu Markdown do przedstawienia pożądanych wzorców.

---

## Ćwiczenie 2: Niestandardowe instrukcje dla testów jednostkowych (JUnit 5 & Mockito)

**Cel:** Dostosuj Copilota, aby sugerował testy jednostkowe zgodne z określonymi standardami zespołu dla `spring-petclinic`, wykorzystując JUnit 5 i Mockito.

**Kontekst:** Twój zespół wymaga, aby wszystkie testy jednostkowe były pisane z użyciem JUnit 5 i Mockito, a nazwy metod testowych miały określoną konwencję (np. `nazwaMetody_scenariusz_oczekiwanyWynik()`).

**Kroki:**
1.  Edytuj plik `.github/copilot-instructions.md` z Ćwiczenia 1.
2.  Dodaj sekcję dotyczącą testów jednostkowych, precyzując:
    *   Preferencję dla JUnit 5 (`@ExtendWith`, `@BeforeEach`, `@Test`, `Assertions`).
    *   Preferencję dla Mockito (`@Mock`, `@InjectMocks`, `when().thenReturn()`, `verify()`).
    *   Wymaganą konwencję nazewnictwa dla metod testowych.
3.  Otwórz klasę `OwnerRepository.java` lub inną klasę repozytorium w `spring-petclinic`.
4.  Poproś Copilota o wygenerowanie testu jednostkowego dla tej klasy. Obserwuj, czy Copilot zastosuje się do Twoich instrukcji dotyczących JUnit 5, Mockito i nazewnictwa metod.

**Oczekiwany rezultat:** Copilot generuje testy jednostkowe dla klas `spring-petclinic` zgodne z zasadami JUnit 5 i Mockito oraz z określoną konwencją nazewnictwa metod testowych.

**Wskazówki:**
-   Możesz podać fragmenty kodu testowego jako przykłady w `copilot-instructions.md`.
-   Użyj `Ctrl+I` (Cmd+I na Macu) w edytorze kodu, aby wywołać inline chat i poprosić o testy.

---

## Ćwiczenie 3: Enforcing Specific `@Value` Annotation Style

**Cel:** Upewnij się, że Copilot używa konkretnego stylu dla adnotacji `@Value` w aplikacjach Spring, np. z użyciem Spring Expression Language (SpEL) dla wartości domyślnych.

**Kontekst:** W projekcie `spring-petclinic` chcesz, aby konfiguracja była spójna, a adnotacje `@Value` zawsze zawierały wartość domyślną z SpEL.

**Kroki:**
1.  Dodaj do pliku `.github/copilot-instructions.md` instrukcje dotyczące preferowanego sposobu użycia `@Value` w Springu, w tym przykład użycia SpEL dla wartości domyślnych (np. `@Value("${some.property:someDefaultValue}")`).
2.  Utwórz nową klasę konfiguracyjną lub serwis w `spring-petclinic` i spróbuj poprosić Copilota o dodanie pola z adnotacją `@Value`. Sprawdź, czy Copilot przestrzega Twojej dyrektywy.

**Oczekiwany rezultat:** Copilot generuje adnotacje `@Value` z wartościami domyślnymi zgodnymi ze specyfikacją SpEL.

**Wskazówki:** Jasne i krótkie przykłady są kluczowe dla Copilota.

---

## Ćwiczenie 4: Reguły logowania (SLF4J) dla spring-petclinic

**Cel:** Skonfiguruj Copilota, aby preferował bibliotekę SLF4J do logowania i przestrzegał określonych praktyk logowania w `spring-petclinic`.

**Kontekst:** Twój projekt `spring-petclinic` używa SLF4J z Logback. Chcesz, aby Copilot sugerował odpowiednie instrukcje logowania, np. używając `LOGGER.info()`, `LOGGER.debug()` z formatowaniem parametrów.

**Kroki:**
1.  Zaktualizuj `.github/copilot-instructions.md`, dodając sekcję o logowaniu. Określ, że należy używać `org.slf4j.Logger` i `org.slf4j.LoggerFactory`, a także pokaż preferowany sposób logowania z placeholderami (np. `logger.info("Finding owner by id: {}", id);`).
2.  Otwórz klasę `OwnerServiceImpl.java` i dodaj nową metodę, która wymaga logowania. Poproś Copilota o dodanie instrukcji logowania. Sprawdź, czy używa SLF4J i poprawnych wzorców.

**Oczekiwany rezultat:** Copilot sugeruje instrukcje logowania zgodne z SLF4J i określonymi wzorcami.

**Wskazówki:** Pamiętaj o imporcie `org.slf4j.Logger` i statycznym inicjowaniu Loggera.

---

## Ćwiczenie 5: Niestandardowy prompt: Generowanie serwisu Spring Boot

**Cel:** Stwórz niestandardowy plik promptu, który umożliwi szybkie generowanie szkieletu nowej usługi Spring Boot wraz z interfejsem i implementacją w `spring-petclinic`.

**Kontekst:** Często musisz tworzyć nowe usługi w projekcie `spring-petclinic`. Chcesz zautomatyzować proces tworzenia podstawowych plików (interfejs serwisu, implementacja serwisu, interfejs repozytorium).

**Kroki:**
1.  Utwórz plik `create_service.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  Wypełnij plik promptu treścią, która instruuje Copilota, aby wygenerował:
    *   Interfejs serwisu z metodami takimi jak `findById(Long id)` i `save(Entity entity)`.
    *   Implementację serwisu adnotowaną `@Service`, wstrzykującą odpowiednie repozytorium przez konstruktor.
    *   Interfejs repozytorium rozszerzający `JpaRepository<Entity, Long>`.
    *   Użyj zmiennych `{{ServiceName}}`, `{{EntityName}}` i `{{service_package}}` dla dynamicznych nazw i pakietów.
    *   Dodaj kontekst `@workspace` i `#file`.
3.  Otwórz Copilot Chat w IDE i wywołaj swój prompt (np. `/create_service`). Podaj wymagane nazwy i pakiet (np. `VetService`, `Vet`, `vet`).

**Oczekiwany rezultat:** Copilot generuje trzy pliki (`VetService.java`, `VetServiceImpl.java`, `VetRepository.java`) z poprawnym boilerplate kodem dla nowej usługi, wstrzykiwaniem zależności i podstawowymi metodami.

**Wskazówki:** Testuj swój prompt iteracyjnie, dostosowując go, aż uzyskasz pożądane rezultaty.

---

## Ćwiczenie 6: Niestandardowy prompt: Generowanie testów jednostkowych dla klasy

**Cel:** Stwórz prompt, który szybko wygeneruje szablon testu jednostkowego dla dowolnej klasy w `spring-petclinic`, wykorzystując JUnit 5 i Mockito.

**Kontekst:** Potrzebujesz szybkiego sposobu na generowanie testów dla nowych lub istniejących klas. Chcesz, aby Copilot dostarczył podstawową strukturę testu, z mockami dla zależności i poprawnym nazewnictwem metod testowych.

**Kroki:**
1.  Utwórz plik `generate_tests.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  Wypełnij plik promptu treścią, która instruuje Copilota, aby wygenerował:
    *   Klasę testową z adnotacjami JUnit 5 (`@ExtendWith(MockitoExtension.class)`, `@InjectMocks`, `@Mock`).
    *   Wstrzyknięcie mocków dla zależności testowanej klasy.
    *   Przykładowe metody testowe z nazwą zgodną z konwencją `nazwaMetody_scenariusz_oczekiwanyWynik()`.
    *   Użyj zmiennych `{{ClassName}}` i `{{FilePath}}` dla dynamicznego kontekstu klasy.
    *   Dodaj kontekst `@workspace` i `@file:{{FilePath}}`.
3.  Otwórz klasę `VisitController.java` (`src/main/java/org/springframework/samples/petclinic/visit/VisitController.java`) w `spring-petclinic`.
4.  W Copilot Chat wywołaj swój prompt (np. `/generate_tests`). Podaj `ClassName` jako `VisitController` i `FilePath` jako pełną ścieżkę do pliku `VisitController.java`.

**Oczekiwany rezultat:** Copilot generuje szablon klasy testowej dla `VisitController` z mockami dla jej zależności (`VisitRepository`, `PetRepository`) i przykładowymi metodami testowymi.

**Wskazówki:** Upewnij się, że Twój prompt jest wystarczająco szczegółowy, aby Copilot zrozumiał, jakie zależności ma zamockować.

---

## Ćwiczenie 7: Niestandardowy prompt: Refaktoryzacja do Java Streams

**Cel:** Stwórz prompt, który pomoże Copilotowi refaktoryzować kod używający tradycyjnych pętli na Java Streams w `spring-petclinic`.

**Kontekst:** W projekcie istnieje kod, który można by uprościć i uczynić bardziej czytelnym, używając Java Streams API.

**Kroki:**
1.  Utwórz plik `refactor_to_streams.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  Prompt powinien instruować Copilota, aby wziął zaznaczony blok kodu i przepisał go na ekwiwalent z wykorzystaniem Java Streams, jeśli to możliwe.
3.  Otwórz plik `PetClinicServiceImpl.java` (`src/main/java/org/springframework/samples/petclinic/service/PetClinicServiceImpl.java`) lub inną klasę zawierającą pętle i kolekcje.
4.  Zaznacz fragment kodu (np. metodę `findOwnersByLastName`) i w Copilot Chat użyj swojego promptu. Oceniaj jakość refaktoryzacji.

**Oczekiwany rezultat:** Copilot efektywnie refaktoryzuje zaznaczony kod, transformując pętle na operacje strumieniowe, poprawiając czytelność i zwięzłość kodu.

**Wskazówki:** Zaznaczenie odpowiedniego fragmentu kodu jest kluczowe dla precyzyjnych sugestii.

---

## Ćwiczenie 8: Generowanie Javadoc za pomocą promptu

**Cel:** Stwórz prompt do szybkiego generowania komentarzy Javadoc dla metod i klas w projekcie `spring-petclinic`.

**Kontekst:** Chcesz, aby dokumentacja kodu była spójna i kompletna. Prompt pomoże szybko dodawać standardowe bloki Javadoc.

**Kroki:**
1.  Utwórz plik `generate_javadoc.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  Prompt powinien instruować Copilota, aby wygenerował Javadoc dla zaznaczonej metody lub klasy, uwzględniając parametry, typ zwracany i wyjątki.
3.  Otwórz dowolną klasę lub metodę w `spring-petclinic` bez Javadoc (np. w `VetController.java`). Zaznacz ją.
4.  W Copilot Chat wywołaj prompt i oceń wygenerowany Javadoc.

**Oczekiwany rezultat:** Copilot generuje poprawny i kompletny Javadoc dla zaznaczonych elementów kodu.

**Wskazówki:** Użyj `@selection` jako kontekstu w prompcie.

---

## Ćwiczenie 9: Pre-run hook: Walidacja istnienia pliku licencji

**Cel:** Skonfiguruj pre-run hook, który uniemożliwi wykonanie promptów Copilota, jeśli w projekcie `spring-petclinic` brakuje pliku `LICENSE`.

**Kontekst:** Wymagane jest, aby każdy projekt miał jasno zdefiniowaną licencję. Chcesz zautomatyzować sprawdzanie tej polityki.

**Kroki:**
1.  Utwórz prosty skrypt w Pythonie (np. `scripts/validate_license.py`) w katalogu `output/copilot_training/tier_1_critical/module_03/scripts/` (najpierw utwórz ten katalog), który sprawdzi, czy w katalogu głównym projektu istnieje plik `LICENSE`.
    *   Skrypt powinien zwracać kod wyjścia `0` (sukces), jeśli plik istnieje, i `1` (błąd), jeśli nie.
    *   Możesz symulować `project_root` lub przekazać go jako argument.
2.  Zmodyfikuj plik `output/copilot_training/tier_1_critical/module_03/config/settings.json`, dodając konfigurację `agentHooks` dla `onPromptRun`, która wywołuje Twój skrypt Pythona.
3.  Upewnij się, że plik `LICENSE` *nie* istnieje w głównym katalogu `spring-petclinic` (lub symuluj jego brak).
4.  Spróbuj uruchomić dowolny prompt Copilota Chat (np. `/help`). Obserwuj, czy hook zablokuje wykonanie promptu i wyświetli odpowiedni komunikat.
5.  Utwórz pusty plik `LICENSE` w głównym katalogu projektu i spróbuj ponownie uruchomić prompt.

**Oczekiwany rezultat:** Gdy plik `LICENSE` nie istnieje, uruchomienie promptu Copilota powinno zostać zablokowane. Po utworzeniu pliku `LICENSE`, prompty powinny działać normalnie.

**Wskazówki:** Pamiętaj, aby skrypt Pythona był wykonywalny i dostępny w ścieżce systemowej lub użyj pełnej ścieżki do niego w `settings.json`.

---

## Ćwiczenie 10: Post-run hook: Automatyczne formatowanie wygenerowanego kodu

**Cel:** Skonfiguruj post-run hook, który automatycznie formatuje każdy kod wygenerowany przez Copilota w projekcie `spring-petclinic`, używając narzędzia do formatowania (np. fikcyjnego `npm run format-code`).

**Kontekst:** Chcesz utrzymać spójny styl kodu, nawet dla kodu generowanego automatycznie. Automatyczne formatowanie zapobiega konieczności ręcznych poprawek.

**Kroki:**
1.  Zaktualizuj (lub utwórz) plik `output/copilot_training/tier_1_critical/module_03/config/package.json` (jeśli go nie ma, utwórz go z podstawową strukturą `{"name": "...", "scripts": {}}`).
2.  Dodaj do sekcji `scripts` polecenie `format-code`, które będzie symulować formatowanie kodu (np. `"format-code": "echo Formatting {{file_path}}..."`).
3.  Zmodyfikuj plik `output/copilot_training/tier_1_critical/module_03/config/settings.json`, dodając konfigurację `agentHooks` dla `onCodeGenerated`, która wywołuje Twoje polecenie `npm run format-code`.
4.  Poproś Copilota o wygenerowanie jakiegoś fragmentu kodu (np. prostej metody) w dowolnym pliku `.java` w `spring-petclinic`.
5.  Obserwuj terminal lub wyjście IDE, aby sprawdzić, czy polecenie formatowania zostało uruchomione po wygenerowaniu kodu.

**Oczekiwany rezultat:** Po każdym wygenerowaniu kodu przez Copilota, automatycznie uruchamia się zdefiniowane polecenie formatowania, a komunikat o formatowaniu jest widoczny.

**Wskazówki:** W rzeczywistym scenariuszu `npm run format-code` uruchomiłby narzędzie takie jak Prettier, Spotless lub inne formatujące kod Java.

---

## Ćwiczenie 11: Agent hook: Powiadomienie o sukcesie generowania kodu

**Cel:** Skonfiguruj agent hook, który wyświetli krótkie powiadomienie po pomyślnym wygenerowaniu kodu przez Copilota.

**Kontekst:** Chcesz mieć natychmiastową informację zwrotną o tym, że Copilot zakończył generowanie kodu, bez konieczności sprawdzania konsoli.

**Kroki:**
1.  Otwórz plik `output/copilot_training/tier_1_critical/module_03/config/settings.json`.
2.  Dodaj do `agentHooks` nowy wpis dla `onCodeGeneratedSuccess` (lub podobny hook, jeśli Copilot API oferuje bardziej szczegółowy stan), który uruchomi proste polecenie wyświetlające powiadomienie (np. `"echo 'Code generated successfully by Copilot!'"` w systemach Linux/macOS, lub skomplikowaną komendę uruchamiającą narzędzie do powiadomień systemowych).
3.  Poproś Copilota o wygenerowanie dowolnego fragmentu kodu w `spring-petclinic`.
4.  Sprawdź, czy powiadomienie zostało wyświetlone (w konsoli, jako powiadomienie systemowe, lub w logach IDE).

**Oczekiwany rezultat:** Po pomyślnym wygenerowaniu kodu przez Copilota, system wyświetla komunikat potwierdzający sukces.

**Wskazówki:** W środowisku VS Code można zintegrować się z API powiadomień VS Code za pomocą rozszerzeń.

---

## Ćwiczenie 12: Niestandardowy prompt: Generowanie SQL schema migration

**Cel:** Stwórz prompt, który generuje podstawowy skrypt migracji bazy danych SQL dla nowej encji w `spring-petclinic`.

**Kontekst:** Wprowadzasz nową encję do projektu `spring-petclinic` i potrzebujesz wygenerować odpowiadający jej skrypt migracji bazy danych (np. Flyway lub Liquibase format).

**Kroki:**
1.  Utwórz plik `generate_sql_migration.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  W prompcie poproś Copilota o wygenerowanie skryptu `CREATE TABLE` dla nowej encji o nazwie `{{NewEntityName}}` z kilkoma przykładowymi kolumnami (np. `id`, `name`, `description`).
    *   Określ, że skrypt powinien być w formacie SQL dla bazy danych H2 (używanej w `spring-petclinic`).
    *   Dodaj kontekst `#file` lub `@workspace`, aby Copilot mógł nawiązać do ogólnej struktury projektu.
3.  Otwórz Copilot Chat i wywołaj prompt, podając `NewEntityName` (np. `ClinicOwner`).

**Oczekiwany rezultat:** Copilot generuje podstawowy skrypt SQL `CREATE TABLE` z odpowiednimi typami danych i kluczem głównym dla określonej encji.

**Wskazówki:** Możesz określić dodatkowe ograniczenia, takie jak klucze obce, indeksy, jeśli są potrzebne.

---

## Ćwiczenie 13: Konwencje nazewnictwa dla metod

**Cel:** Skonfiguruj Copilota, aby sugerował nazwy metod zgodne z przyjętymi konwencjami w projekcie `spring-petclinic` (np. `verbNoun` dla akcji, `getNoun` dla getterów).

**Kontekst:** Chcesz zapewnić spójność w nazewnictwie metod w całym projekcie.

**Kroki:**
1.  Zaktualizuj `.github/copilot-instructions.md`, dodając sekcję o konwencjach nazewnictwa metod, podając przykłady dla różnych typów metod (np. `saveOwner`, `getOwnerById`, `deletePet`).
2.  Otwórz dowolną klasę serwisu lub repozytorium w `spring-petclinic` i zacznij pisać nową metodę. Sprawdź, czy Copilot sugeruje nazwy zgodne z Twoimi instrukcjami.

**Oczekiwany rezultat:** Copilot przestrzega określonych konwencji nazewnictwa metod, oferując sugestie zgodne z wytycznymi.

**Wskazówki:** Konkretne przykłady są zawsze bardziej efektywne niż ogólne zasady.

---

## Ćwiczenie 14: Unikanie anty-wzorców: Field Injection

**Cel:** Poinstruuj Copilota, aby unikał wstrzykiwania zależności przez pola (`@Autowired` na polu) i zamiast tego preferował wstrzykiwanie przez konstruktor.

**Kontekst:** W projekcie `spring-petclinic` wstrzykiwanie zależności przez pola jest uznawane za anty-wzorzec.

**Kroki:**
1.  W pliku `.github/copilot-instructions.md` dodaj sekcję, która wyraźnie odradza używanie field injection i podaje przykład kodu, którego należy unikać, oraz przykład kodu, który jest preferowany (constructor injection).
2.  Otwórz klasę serwisu lub kontrolera w `spring-petclinic`. Usuń istniejące wstrzykiwanie przez konstruktor i spróbuj poprosić Copilota o dodanie zależności. Sprawdź, czy nie sugeruje field injection.

**Oczekiwany rezultat:** Copilot unika sugerowania field injection i aktywnie promuje wstrzykiwanie przez konstruktor.

**Wskazówki:** Czasami Copilot potrzebuje jasnych negatywnych przykładów ("UNIKAJ TEGO:") oprócz pozytywnych.

---

## Ćwiczenie 15: Niestandardowy prompt: Generowanie opisu klasy/metody (plain text)

**Cel:** Stwórz prosty prompt do generowania zwięzłego, tekstowego opisu klasy lub metody.

**Kontekst:** Czasami potrzebujesz szybkiego, ludzkiego opisu fragmentu kodu, który możesz wkleić do dokumentacji lub zgłoszenia.

**Kroki:**
1.  Utwórz plik `describe_code.prompt` w katalogu `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/`.
2.  W prompcie poproś Copilota o krótkie, zwięzłe streszczenie funkcjonalności zaznaczonego kodu (klasy, metody) w języku polskim.
3.  Zaznacz dowolną klasę lub metodę w `spring-petclinic` i wywołaj prompt.

**Oczekiwany rezultat:** Copilot zwraca krótki, zrozumiały opis zaznaczonego kodu.

**Wskazówki:** Użyj `@selection` jako kontekstu i wyraźnie poproś o "zwięzły, tekstowy opis".