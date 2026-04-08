# Ćwiczenia: Agent Skills - Rozbudowa Agentów

Niniejsze ćwiczenia mają na celu praktyczne zastosowanie wiedzy na temat umiejętności agenta (Agent Skills) w GitHub Copilot, z wykorzystaniem repozytorium `spring-petclinic`.

## Ćwiczenie 1: Analiza Wbudowanej Umiejętności Generowania Kodu

**Cel:** Zrozumienie, jak Copilot używa swoich wbudowanych umiejętności do generowania kodu.

**Kontekst:** Pracujesz z plikiem `VetController.java` w repozytorium `spring-petclinic`. Chcesz dodać nową metodę do kontrolera, ale potrzebujesz pomysłu na jej strukturę.

**Kroki:**
1.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/vet/VetController.java` w edytorze kodu.
2.  Przejdź na koniec klasy `VetController`.
3.  W Copilot Chat (lub Inline Chat) wpisz polecenie, np.: `Napisz mi metodę GET /vets/json, która zwraca listę weterynarzy w formacie JSON.`
4.  Przeanalizuj wygenerowany kod. Zadaj Copilotowi pytania, np.: `Dlaczego użyłeś adnotacji @ResponseBody?` lub `Czy możesz dodać obsługę paginacji?`

**Oczekiwany rezultat:** Copilot wygeneruje fragment kodu podobny do poniższego i będzie w stanie wyjaśnić swoje decyzje.
```java
// ... w VetController.java
    @GetMapping({ "/vets.json" })
    public @ResponseBody List<Vet> showResourcesVetList() {
        // Here we are also using @ResponseBody explicitly
        return new Vets().getVetList();
    }
// ...
```

**Wskazówki:**
-   Eksperymentuj z różnymi zapytaniami, aby zobaczyć, jak Copilot adaptuje generowany kod.
-   Zwróć uwagę, jak Copilot interpretuje kontekst klasy i projektu.

---

## Ćwiczenie 2: Implementacja Prostej Umiejętności Wyświetlania Informacji o Projekcie

**Cel:** Stworzenie i uruchomienie podstawowej, niestandardowej umiejętności Copilota.

**Kontekst:** Chcesz mieć szybki sposób na sprawdzenie aktualnej daty lub wersji Javy, używanej w projekcie `spring-petclinic`, bezpośrednio z Copilota.

**Kroki:**
1.  W głównym katalogu `spring-petclinic`, utwórz katalog `.copilot/skills`.
2.  W katalogu `.copilot/skills` utwórz plik `showInfo.js` z następującą zawartością (lub podobną, jeśli wolisz Pythona/Basha):
    ```javascript
    // .copilot/skills/showInfo.js
    const query = process.argv[2];

    if (query && query.toLowerCase().includes("date")) {
        console.log(`Aktualna data: ${new Date().toLocaleString()}`);
    } else if (query && query.toLowerCase().includes("java version")) {
        console.log("Wersja Javy projektu spring-petclinic: Java 17"); // Uproszczono
    } else {
        console.log("Dostępne informacje: data, java version.");
        console.log("Przykład użycia: 'Copilot, użyj showProjectInfo date' lub 'Copilot, użyj showProjectInfo java version'");
    }
    ```
3.  Zmodyfikuj plik `package.json` w głównym katalogu `spring-petclinic` (jeśli nie istnieje, utwórz go z podstawową strukturą) i dodaj sekcję `copilot` dla umiejętności:
    ```json
    {
      "name": "spring-petclinic",
      "version": "2.7.0",
      "private": true,
      "copilot": {
        "skills": [
          {
            "id": "showProjectInfo",
            "description": "Wyświetla aktualną datę lub wersję Javy projektu.",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/showInfo.js", "${query}"]
            }
          }
        ]
      }
    }
    ```
4.  W Copilot Chat, spróbuj wywołać swoją nową umiejętność:
    *   `Copilot, użyj umiejętności showProjectInfo date`
    *   `Copilot, użyj showProjectInfo java version`

**Oczekiwany rezultat:** Copilot poprawnie uruchomi skrypt `showInfo.js` i wyświetli odpowiednią informację w Copilot Chat.

**Wskazówki:**
-   Upewnij się, że masz zainstalowanego Node.js, jeśli używasz JavaScriptu.
-   Zwróć uwagę na ścieżki w `package.json` – muszą być poprawne względem głównego katalogu projektu.

---

## Ćwiczenie 3: Tworzenie Niestandardowej Umiejętności Generowania Boileplate Testu JUnit 5

**Cel:** Stworzenie zaawansowanej niestandardowej umiejętności, która generuje boilerplate testu dla istniejącej klasy Java.

**Kontekst:** Chcesz usprawnić proces tworzenia testów jednostkowych w `spring-petclinic`. Potrzebujesz umiejętności, która automatycznie wygeneruje plik testowy JUnit 5 dla dowolnej podanej klasy (np. `OwnerRepository`).

**Kroki:**
1.  W katalogu `.copilot/skills` (utworzonym w poprzednim ćwiczeniu) utwórz plik `generateTest.js` (lub `generateTest.py`, jeśli wolisz Python):
    ```javascript
    // .copilot/skills/generateTest.js
    const fs = require('fs');
    const path = require('path');
    const className = process.argv[2]; // Argument przekazany z package.json

    if (!className) {
        console.error("Błąd: Nie podano nazwy klasy. Użycie: generateTest <nazwa_klasy>");
        process.exit(1);
    }

    const packageName = "org.springframework.samples.petclinic.owner"; // Przykładowo, można by to inteligentniej parsować
    const testBoilerplate = `
package ${packageName};

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class ${className}Tests {

    private ${className} ${className.toLowerCase()};

    @BeforeEach
    void setup() {
        // W zależności od klasy, tutaj może być potrzebna mock implementacja lub Spring context
        // Np.: this.${className.toLowerCase()} = mock(${className}.class);
        System.out.println("Przygotowanie testu dla klasy: ${className}");
    }

    @Test
    void testExampleMethod() {
        // Implement test logic here
        assertThat(true).isTrue(); // Placeholder
        System.out.println("Wykonano test dla klasy: ${className}");
    }

}
`;
    const projectRoot = path.resolve(__dirname, '../../../'); // Zakładamy, że .copilot jest w root
    const outputDir = path.join(projectRoot, `src/test/java/${packageName.replace(/\./g, '/')}/`);
    const outputFilePath = path.join(outputDir, `${className}Tests.java`);

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
        console.log(`Utworzono katalog: ${outputDir}`);
    }

    fs.writeFileSync(outputFilePath, testBoilerplate);
    console.log(`✅ Wygenerowano boilerplate testu dla klasy ${className} w pliku ${outputFilePath}`);
    ```
2.  Dodaj definicję tej umiejętności do pliku `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "generateTestBoilerplate",
            "description": "Generuje boilerplate testu JUnit 5 dla podanej klasy Java (np. OwnerRepository).",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/generateTest.js", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Nazwa klasy Java (bez rozszerzenia), dla której ma być wygenerowany test."
              }
            }
          }
    ```
3.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/OwnerRepository.java`. Zaznacz tekst `OwnerRepository`.
4.  W Copilot Chat, wywołaj umiejętność: `Copilot, użyj umiejętności generateTestBoilerplate dla zaznaczonego tekstu.` (lub po prostu `Copilot, generateTestBoilerplate OwnerRepository`)

**Oczekiwany rezultat:** W katalogu `src/test/java/org/springframework/samples/petclinic/owner/` zostanie utworzony plik `OwnerRepositoryTests.java` z podstawowym kodem testu. Copilot powinien poinformować o pomyślnym utworzeniu pliku.

**Wskazówki:**
-   Upewnij się, że skrypt ma prawa do zapisu w katalogu testów.
-   Zauważ użycie `${selectedText}`. Możesz także użyć `${query}` i pozwolić Copilotowi wydobyć nazwę klasy z zapytania.

---

## Ćwiczenie 4: Integracja Linera (Checkstyle) jako Umiejętność Agenta

**Cel:** Stworzenie umiejętności, która integruje zewnętrzne narzędzie (Checkstyle) i raportuje jego wyniki.

**Kontekst:** Chcesz, aby Copilot mógł na żądanie uruchamiać Checkstyle na plikach Java w `spring-petclinic` i informować Cię o naruszeniach standardów kodowania.

**Kroki:**
1.  Pobierz JAR Checkstyle (np. wersję 8.45 lub nowszą) i umieść go w katalogu `lib` w głównym katalogu `spring-petclinic` (utwórz katalog `lib`, jeśli nie istnieje).
    *   Możesz pobrać np. stąd: `https://repo1.maven.org/maven2/com/puppycrawl/tools/checkstyle/8.45/checkstyle-8.45-all.jar`
2.  W głównym katalogu `spring-petclinic`, utwórz katalog `config` i w nim plik `checkstyle.xml` (przykładowa prosta konfiguracja):
    ```xml
    <?xml version="1.0"?>
    <!DOCTYPE module PUBLIC
        "-//Puppy Crawl//DTD Check Configuration 1.3//EN"
        "https://checkstyle.sourceforge.io/dtds/configuration_1_3.dtd">

    <module name="Checker">
        <property name="charset" value="UTF-8"/>
        <property name="fileExtensions" value="java, xml"/>
        <module name="TreeWalker">
            <module name="LocalVariableName"/>
            <module name="MethodLength"/>
            <module name="NeedBraces"/>
            <module name="EmptyBlock"/>
            <module name="ParenPad"/>
            <module name="WhitespaceAfter"/>
        </module>
    </module>
    ```
3.  W katalogu `.copilot/skills` utwórz skrypt `runCheckstyle.sh` (lub `runCheckstyle.cmd` dla Windows, lub skrypt Python, który wywołuje Java):
    ```bash
    #!/bin/bash
    FILE_TO_CHECK=$1

    if [ -z "$FILE_TO_CHECK" ]; then
        echo "Błąd: Nie podano pliku do sprawdzenia. Użycie: runCheckstyle <sciezka_do_pliku>"
        exit 1
    }

    echo "Uruchamiam Checkstyle dla pliku: $FILE_TO_CHECK"
    java -jar ./lib/checkstyle-8.45-all.jar -c ./config/checkstyle.xml "$FILE_TO_CHECK"
    ```
    *   Upewnij się, że skrypt ma uprawnienia do wykonywania (`chmod +x ./.copilot/skills/runCheckstyle.sh`).
4.  Dodaj definicję umiejętności `runCheckstyle` do pliku `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "runCheckstyle",
            "description": "Uruchamia Checkstyle na wskazanym pliku Java i raportuje naruszenia.",
            "execute": {
              "command": "bash",
              "args": ["./.copilot/skills/runCheckstyle.sh", "${file}"]
            },
            "args": {
              "file": {
                "type": "string",
                "description": "Ścieżka do pliku Java do sprawdzenia."
              }
            }
          }
    ```
5.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
6.  W Copilot Chat, wywołaj umiejętność: `Copilot, uruchom Checkstyle dla tego pliku.` (lub `Copilot, użyj runCheckstyle na Owner.java`)

**Oczekiwany rezultat:** Copilot uruchomi Checkstyle i zwróci raport z naruszeniami (lub informację o braku naruszeń) w Copilot Chat.

**Wskazówki:**
-   Dostosuj ścieżki do JAR Checkstyle i pliku konfiguracyjnego w skrypcie i definicji umiejętności.
-   Możesz stworzyć cel Maven lub Gradle w projekcie `spring-petclinic` do uruchamiania Checkstyle i wywoływać go zamiast bezpośrednio JAR-a.

---

## Ćwiczenie 5: Umiejętność Generowania Javadoc dla Metody

**Cel:** Stworzenie umiejętności, która generuje boilerplate Javadoc dla wybranej metody Java.

**Kontekst:** Chcesz szybko dodać dokumentację Javadoc do metod w `spring-petclinic`.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz plik `generateJavadoc.js`:
    ```javascript
    // .copilot/skills/generateJavadoc.js
    const methodSignature = process.argv[2];

    if (!methodSignature) {
        console.error("Błąd: Nie podano sygnatury metody.");
        process.exit(1);
    }

    const javadocBoilerplate = `/**
 * Opis działania metody: [Opis_tutaj]
 *
 * @param {string} param1 Opis parametru 1
 * @return {string} Opis zwracanej wartości
 * @throws {Exception} Opis wyjątku
 */
`;
    // W rzeczywistości, skrypt musiałby inteligentnie parsować methodSignature
    // i wyodrębniać parametry, zwracany typ itp.
    // Dla uproszczenia, tylko podstawowy boilerplate.
    console.log(javadocBoilerplate);
    ```
2.  Dodaj definicję umiejętności `generateJavadoc` do pliku `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "generateJavadoc",
            "description": "Generuje boilerplate Javadoc dla zaznaczonej sygnatury metody Java.",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/generateJavadoc.js", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Sygnatura metody Java, dla której ma być wygenerowany Javadoc."
              }
            }
          }
    ```
3.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
4.  Zaznacz sygnaturę metody, np.: `public String getFirstName() {`.
5.  W Copilot Chat, wywołaj: `Copilot, użyj umiejętności generateJavadoc dla zaznaczonej metody.`

**Oczekiwany rezultat:** Copilot wklei boilerplate Javadoc nad zaznaczoną metodą (lub zwróci go w chatcie do wklejenia).

---

## Ćwiczenie 6: Umiejętność Wyszukiwania Użycia Klasy/Metody (Gradle/Maven)

**Cel:** Stworzenie umiejętności, która używa narzędzi budowania do znalezienia referencji do klasy lub metody.

**Kontekst:** Chcesz szybko znaleźć, gdzie dana klasa (`Owner`) lub metoda jest używana w projekcie `spring-petclinic`.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz skrypt `findUsage.sh`:
    ```bash
    #!/bin/bash
    SEARCH_TERM=$1

    if [ -z "$SEARCH_TERM" ]; then
        echo "Błąd: Nie podano terminu wyszukiwania."
        exit 1
    }

    echo "Szukam użycia '$SEARCH_TERM' w projekcie..."
    # Możesz użyć 'grep' lub bardziej zaawansowanych narzędzi.
    # W przypadku Javy, lepsze byłoby parsowanie AST lub użycie narzędzi IDE.
    # Tutaj proste wyszukiwanie grep.
    grep -r "$SEARCH_TERM" src/main/java src/test/java || echo "Nie znaleziono użycia dla '$SEARCH_TERM'."
    ```
2.  Dodaj definicję umiejętności `findCodeUsage` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "findCodeUsage",
            "description": "Wyszukuje użycie klasy lub metody w projekcie spring-petclinic.",
            "execute": {
              "command": "bash",
              "args": ["./.copilot/skills/findUsage.sh", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Nazwa klasy lub metody do wyszukania."
              }
            }
          }
    ```
3.  Otwórz dowolny plik Java, np. `Owner.java`. Zaznacz `Owner` lub `getFirstName`.
4.  W Copilot Chat, wywołaj: `Copilot, znajdź użycie tego tekstu.` (lub `Copilot, użyj findCodeUsage Owner`).

**Oczekiwany rezultat:** Copilot zwróci listę plików i linii, w których znaleziono wyszukiwany termin.

---

## Ćwiczenie 7: Rozszerzenie Umiejętności `showProjectInfo` o Informacje o Systemie Operacyjnym

**Cel:** Modyfikacja istniejącej umiejętności w celu dodania nowej funkcjonalności.

**Kontekst:** Chcesz, aby umiejętność `showProjectInfo` mogła również wyświetlać podstawowe informacje o systemie operacyjnym.

**Kroki:**
1.  Zmodyfikuj plik `.copilot/skills/showInfo.js` (lub odpowiednik Pythona/Basha) dodając obsługę "os info":
    ```javascript
    // .copilot/skills/showInfo.js (zmieniony fragment)
    const query = process.argv[2];
    const os = require('os'); // Dodaj to na początku pliku JS

    if (query && query.toLowerCase().includes("date")) {
        console.log(`Aktualna data: ${new Date().toLocaleString()}`);
    } else if (query && query.toLowerCase().includes("java version")) {
        console.log("Wersja Javy projektu spring-petclinic: Java 17");
    } else if (query && query.toLowerCase().includes("os info")) {
        console.log(`System operacyjny: ${os.platform()} ${os.arch()} - ${os.release()}`);
        console.log(`Całkowita pamięć: ${(os.totalmem() / (1024 ** 3)).toFixed(2)} GB`);
    } else {
        console.log("Dostępne informacje: data, java version, os info.");
        console.log("Przykład użycia: 'Copilot, użyj showProjectInfo os info'");
    }
    ```
2.  Wywołaj umiejętność: `Copilot, użyj showProjectInfo os info`.

**Oczekiwany rezultat:** Copilot wyświetli podstawowe informacje o systemie operacyjnym.

---

## Ćwiczenie 8: Umiejętność Uruchamiania Testów Jednostkowych dla Konkretnej Klasy (Maven/Gradle)

**Cel:** Stworzenie umiejętności, która uruchamia testy jednostkowe dla pojedynczej klasy testowej przy użyciu Maven lub Gradle.

**Kontekst:** Chcesz szybko uruchomić testy dla konkretnego pliku testowego w `spring-petclinic`, np. po wprowadzeniu zmian.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz skrypt `runTests.sh`:
    ```bash
    #!/bin/bash
    TEST_CLASS=$1

    if [ -z "$TEST_CLASS" ]; then
        echo "Błąd: Nie podano nazwy klasy testowej."
        exit 1
    }

    echo "Uruchamiam testy dla klasy: $TEST_CLASS"
    # Użycie Maven do uruchomienia konkretnego testu
    ./mvnw test -Dtest=$TEST_CLASS
    # Alternatywnie dla Gradle:
    # ./gradlew test --tests "*$TEST_CLASS*"
    ```
2.  Dodaj definicję umiejętności `runSingleTest` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "runSingleTest",
            "description": "Uruchamia testy jednostkowe dla podanej klasy testowej (np. OwnerRepositoryTests).",
            "execute": {
              "command": "bash",
              "args": ["./.copilot/skills/runTests.sh", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Nazwa klasy testowej do uruchomienia (np. OwnerRepositoryTests)."
              }
            }
          }
    ```
3.  Otwórz plik `src/test/java/org/springframework/samples/petclinic/owner/OwnerRepositoryTests.java` (jeśli został wygenerowany w Ćwiczeniu 3, lub inny plik testowy).
4.  Zaznacz nazwę klasy testowej, np. `OwnerRepositoryTests`.
5.  W Copilot Chat, wywołaj: `Copilot, uruchom testy dla tej klasy.` (lub `Copilot, użyj runSingleTest OwnerRepositoryTests`)

**Oczekiwany rezultat:** Copilot uruchomi proces budowania Maven (lub Gradle), który wykona testy dla wskazanej klasy, a wynik zostanie wyświetlony w chatcie.

---

## Ćwiczenie 9: Umiejętność Generowania Zapytań SQL dla Encji

**Cel:** Stworzenie umiejętności, która na podstawie nazwy encji (klasy modelu) generuje proste zapytania SQL (SELECT, INSERT).

**Kontekst:** Często potrzebujesz szybko wygenerować podstawowe zapytania SQL dla encji w bazie danych `spring-petclinic`.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz plik `generateSql.js`:
    ```javascript
    // .copilot/skills/generateSql.js
    const entityName = process.argv[2];

    if (!entityName) {
        console.error("Błąd: Nie podano nazwy encji.");
        process.exit(1);
    }

    const tableName = entityName.toLowerCase() + "s"; // Proste mapowanie np. Owner -> owners

    const selectQuery = `SELECT * FROM ${tableName};`;
    const insertQuery = `INSERT INTO ${tableName} (id, name) VALUES (1, 'Test${entityName}');`; // Uproszczono

    console.log(`--- Zapytania SQL dla encji ${entityName} ---`);
    console.log(`SELECT: ${selectQuery}`);
    console.log(`INSERT: ${insertQuery}`);
    console.log(`--------------------------------------`);
    ```
2.  Dodaj definicję umiejętności `generateSqlQueries` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "generateSqlQueries",
            "description": "Generuje podstawowe zapytania SQL (SELECT, INSERT) dla podanej nazwy encji.",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/generateSql.js", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Nazwa encji (klasy modelu) dla której mają być wygenerowane zapytania SQL."
              }
            }
          }
    ```
3.  Otwórz plik `src/main/java/org/springframework/samples/petclinic/owner/Owner.java`.
4.  Zaznacz nazwę klasy `Owner`.
5.  W Copilot Chat, wywołaj: `Copilot, wygeneruj zapytania SQL dla Owner.` (lub `Copilot, użyj generateSqlQueries Owner`)

**Oczekiwany rezultat:** Copilot wyświetli proste zapytania SQL dla encji `Owner`.

---

## Ćwiczenie 10: Debugowanie Umiejętności Agenta

**Cel:** Zrozumienie, jak debugować niestandardowe umiejętności Copilota.

**Kontekst:** Podczas tworzenia umiejętności często pojawiają się błędy. Musisz wiedzieć, jak je zdiagnozować.

**Kroki:**
1.  Celowo wprowadź błąd do jednego ze skryptów umiejętności, np. do `generateTest.js` zmień `fs.writeFileSync` na `fs.writeFilleSync`.
2.  Wywołaj umiejętność, która używa tego błędnego skryptu (np. `generateTestBoilerplate`).
3.  Obserwuj komunikaty zwrotne z Copilota. Zwróć uwagę na wszelkie błędy.
4.  Sprawdź logi wyjściowe Copilota (często dostępne w panelu Output w VS Code, w zakładce "GitHub Copilot Chat").
5.  Popraw błąd w skrypcie i ponownie wywołaj umiejętność, aby sprawdzić, czy działa poprawnie.

**Oczekiwany rezultat:** Zidentyfikujesz błąd, zrozumiesz, jak Copilot sygnalizuje problemy w umiejętnościach i będziesz w stanie go naprawić.

**Wskazówki:**
-   Używaj `console.log()` (lub odpowiednika w Python/Bash) w swoich skryptach, aby wyświetlać wartości zmiennych i śledzić przepływ wykonania.
-   Sprawdź, czy skrypt działa poprawnie, uruchamiając go bezpośrednio z terminala, zanim wywołasz go przez Copilota.

---

## Ćwiczenie 11: Zwiększenie Interaktywności - Umiejętność z Potwierdzeniem

**Cel:** Stworzenie umiejętności, która wymaga potwierdzenia od użytkownika przed wykonaniem potencjalnie destrukcyjnej operacji.

**Kontekst:** Chcesz, aby umiejętność np. czyszczenia logów wymagała dodatkowego potwierdzenia.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz plik `clearLogs.js`:
    ```javascript
    // .copilot/skills/clearLogs.js
    const fs = require('fs');
    const path = require('path');
    const confirmation = process.argv[2]; // Oczekujemy "tak" lub "yes"

    if (!confirmation || !(confirmation.toLowerCase() === 'tak' || confirmation.toLowerCase() === 'yes')) {
        console.log("Potwierdź, że chcesz usunąć logi, dodając 'tak' lub 'yes' do zapytania. Np.: 'Copilot, wyczyść logi tak'");
        process.exit(0);
    }

    const logDir = path.resolve(__dirname, '../../../log'); // Zakładamy, że logi są w katalogu 'log' w root
    if (fs.existsSync(logDir)) {
        fs.rmSync(logDir, { recursive: true, force: true });
        console.log(`✅ Katalog logów (${logDir}) został wyczyszczony.`);
    } else {
        console.log(`Katalog logów (${logDir}) nie istnieje.`);
    }
    ```
2.  Dodaj definicję umiejętności `clearLogs` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "clearLogs",
            "description": "Czyści katalog z logami po potwierdzeniu.",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/clearLogs.js", "${query}"]
            },
            "args": {
              "query": {
                "type": "string",
                "description": "Potwierdź operację, wpisując 'tak' lub 'yes'."
              }
            }
          }
    ```
3.  Spróbuj wywołać:
    *   `Copilot, wyczyść logi` (powinno poprosić o potwierdzenie)
    *   `Copilot, wyczyść logi tak` (powinno usunąć logi)

**Oczekiwany rezultat:** Umiejętność będzie wymagała potwierdzenia przed wykonaniem operacji.

---

## Ćwiczenie 12: Umiejętność Generowania Endpointów REST na Podstawie Encji

**Cel:** Stworzenie umiejętności, która generuje boilerplate dla podstawowych endpointów REST (CRUD) dla danej encji.

**Kontekst:** Chcesz szybko tworzyć podstawowe kontrolery RESTful w `spring-petclinic` dla nowych encji.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz plik `generateRestController.js`:
    ```javascript
    // .copilot/skills/generateRestController.js
    const fs = require('fs');
    const path = require('path');
    const entityName = process.argv[2];

    if (!entityName) {
        console.error("Błąd: Nie podano nazwy encji.");
        process.exit(1);
    }

    const lowerCaseEntityName = entityName.toLowerCase();
    const packageName = "org.springframework.samples.petclinic.rest"; // Przykładowy pakiet dla REST
    const controllerBoilerplate = `
package ${packageName};

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Collection;

@RestController
@RequestMapping("/api/${lowerCaseEntityName}s") // Przykład: /api/owners
class ${entityName}RestController {

    // Tutaj należałoby wstrzyknąć serwis/repozytorium dla ${entityName}
    // private final ${entityName}Service ${lowerCaseEntityName}Service;

    // public ${entityName}RestController(${entityName}Service ${lowerCaseEntityName}Service) {
    //     this.${lowerCaseEntityName}Service = ${lowerCaseEntityName}Service;
    // }

    @GetMapping
    public ResponseEntity<Collection<${entityName}>> get${entityName}s() {
        // Implementacja pobierania wszystkich ${entityName}
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @GetMapping("/${${lowerCaseEntityName}Id}")
    public ResponseEntity<${entityName}> get${entityName}(@PathVariable("entityId") int ${lowerCaseEntityName}Id) {
        // Implementacja pobierania pojedynczego ${entityName}
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @PostMapping
    public ResponseEntity<${entityName}> create${entityName}(@RequestBody @Valid ${entityName} ${lowerCaseEntityName}) {
        // Implementacja tworzenia nowego ${entityName}
        return new ResponseEntity<>(HttpStatus.CREATED);
    }

    @PutMapping("/${${lowerCaseEntityName}Id}")
    public ResponseEntity<${entityName}> update${entityName}(@PathVariable("entityId") int ${lowerCaseEntityName}Id, @RequestBody @Valid ${entityName} ${lowerCaseEntityName}) {
        // Implementacja aktualizacji ${entityName}
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }

    @DeleteMapping("/${${lowerCaseEntityName}Id}")
    public ResponseEntity<Void> delete${entityName}(@PathVariable("entityId") int ${lowerCaseEntityName}Id) {
        // Implementacja usuwania ${entityName}
        return new ResponseEntity<>(HttpStatus.NO_CONTENT);
    }
}
`;
    const projectRoot = path.resolve(__dirname, '../../../');
    const outputDir = path.join(projectRoot, `src/main/java/${packageName.replace(/\./g, '/')}/`);
    const outputFilePath = path.join(outputDir, `${entityName}RestController.java`);

    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
        console.log(`Utworzono katalog: ${outputDir}`);
    }

    fs.writeFileSync(outputFilePath, controllerBoilerplate);
    console.log(`✅ Wygenerowano RestController dla encji ${entityName} w pliku ${outputFilePath}`);
    ```
2.  Dodaj definicję umiejętności `generateRestController` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.json
          {
            "id": "generateRestController",
            "description": "Generuje boilerplate dla podstawowego RestController (CRUD) dla podanej nazwy encji.",
            "execute": {
              "command": "node",
              "args": ["./.copilot/skills/generateRestController.js", "${selectedText}"]
            },
            "args": {
              "selectedText": {
                "type": "string",
                "description": "Nazwa encji (klasy modelu) dla której ma być wygenerowany RestController."
              }
            }
          }
    ```
3.  W Copilot Chat, wywołaj: `Copilot, wygeneruj RestController dla encji Pet.` (lub `Copilot, użyj generateRestController Pet`).

**Oczekiwany rezultat:** W odpowiednim katalogu zostanie utworzony plik `PetRestController.java` z podstawowymi endpointami CRUD.

---

## Ćwiczenie 13: Umiejętność Skanowania Projektu pod Kątem Użycia Deprecated API

**Cel:** Stworzenie umiejętności, która pomaga zidentyfikować użycie przestarzałych (deprecated) API w projekcie.

**Kontekst:** Chcesz regularnie sprawdzać `spring-petclinic` pod kątem użycia przestarzałych metod i klas, aby ułatwić refaktoryzację.

**Kroki:**
1.  W katalogu `.copilot/skills` utwórz plik `findDeprecated.sh`:
    ```bash
    #!/bin/bash
    echo "Skanuję projekt pod kątem użycia przestarzałych API..."
    # Proste wyszukiwanie słowa 'Deprecated' w kodzie Javy
    grep -r "@Deprecated" src/main/java src/test/java | grep -v "public @interface Deprecated" || echo "Nie znaleziono użycia @Deprecated API."
    ```
2.  Dodaj definicję umiejętności `findDeprecatedApi` do `package.json`:
    ```json
    // ... w sekcji "copilot"."skills" w package.box]
          {
            "id": "findDeprecatedApi",
            "description": "Skanuje projekt pod kątem użycia przestarzałych (deprecated) API w kodzie Java.",
            "execute": {
              "command": "bash",
              "args": ["./.copilot/skills/findDeprecated.sh"]
            }
          }
    ```
3.  W Copilot Chat, wywołaj: `Copilot, znajdź deprecated API w projekcie.` (lub `Copilot, użyj findDeprecatedApi`).

**Oczekiwany rezultat:** Copilot wyświetli listę miejsc, gdzie znaleziono adnotację `@Deprecated` (lub jej użycie).

---
