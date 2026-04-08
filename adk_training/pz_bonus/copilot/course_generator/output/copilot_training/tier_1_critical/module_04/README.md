# Agent Skills - Rozbudowa Agentów

## 🎯 Cele Szkolenia
- Zrozumienie roli i działania umiejętności (Agent Skills) w GitHub Copilot.
- Umiejętność wykorzystania wbudowanych umiejętności Copilota w codziennej pracy programisty.
- Zdolność do projektowania, implementacji i integracji własnych, niestandardowych umiejętności Copilota.
- Optymalizacja przepływu pracy dzięki automatyzacji zadań za pomocą rozszerzonych możliwości agentów.
- Poznanie dobrych praktyk tworzenia niezawodnych i użytecznych umiejętności agenta.

## 📚 Teoria

### Wprowadzenie do Umiejętności Agenta (Agent Skills)
GitHub Copilot, będąc zaawansowanym asystentem AI, wykracza poza samo generowanie kodu. Dzięki koncepcji "Agent Skills", Copilot może wykonywać bardziej złożone zadania, działając jako agent. Umiejętności to w zasadzie małe programy lub skrypty, które Copilot może wywołać w odpowiedzi na zapytania użytkownika. Mogą one służyć do interakcji z systemem plików, narzędziami zewnętrznymi, API czy bazami danych, rozszerzając tym samym jego możliwości poza zwykłe pisanie kodu.

#### Jak działają Umiejętności Agenta?
1.  **Rozpoznawanie intencji:** Użytkownik zadaje pytanie lub wydaje polecenie w Copilot Chat.
2.  **Analiza:** Copilot analizuje zapytanie, aby zidentyfikować intencję i sprawdzić, czy istnieje dostępna umiejętność, która może pomóc w jego realizacji.
3.  **Wybór umiejętności:** Jeśli intencja pasuje do definicji umiejętności, Copilot wybiera najbardziej odpowiednią.
4.  **Wykonanie:** Copilot wywołuje wybraną umiejętność, przekazując jej niezbędne argumenty z kontekstu rozmowy lub kodu.
5.  **Prezentacja wyniku:** Wynik działania umiejętności jest zwracany do Copilota, który następnie prezentuje go użytkownikowi, często w formie podsumowania lub dalszych sugerowanych działań.

### Przegląd Wbudowanych Umiejętności
GitHub Copilot jest wyposażony w szereg wbudowanych umiejętności, które są od razu dostępne. Obejmują one m.in.:
-   **Generowanie kodu:** Klasyczna funkcja Copilota, ale traktowana jako umiejętność generowania fragmentów kodu na podstawie kontekstu.
-   **Wyjaśnianie kodu:** Zdolność do analizy i objaśniania złożonych fragmentów kodu.
-   **Refaktoryzacja:** Sugerowanie i wykonywanie prostych operacji refaktoryzacyjnych.
-   **Testowanie:** Generowanie testów jednostkowych lub pomoc w ich tworzeniu.
-   **Zarządzanie plikami:** Podstawowe operacje na plikach i katalogach w obszarze roboczym.
-   **Interakcja z dokumentacją:** Przeszukiwanie i streszczanie dokumentacji (np. języków programowania, frameworków).

Korzystanie z wbudowanych umiejętności często odbywa się w sposób naturalny poprzez zadawanie pytań w Copilot Chat, bez konieczności jawnego wywoływania konkretnej umiejętności.

### Integracja Umiejętności z Agentami
Umiejętności są integralną częścią architektury agentów. Agent to bardziej złożony byt, który może składać się z wielu umiejętności i logiki decyzyjnej. Integracja polega na udostępnianiu agentowi zestawu narzędzi (skills), z których może on korzystać do osiągnięcia celu. Kontekst jest kluczowy – agent musi wiedzieć, kiedy i jakiej umiejętności użyć.

### Tworzenie Niestandardowych Umiejętności

Większą moc Copilota uzyskujemy poprzez tworzenie własnych, niestandardowych umiejętności. Pozwalają one na rozszerzenie funkcjonalności Copilota o specyficzne dla naszego projektu, zespołu lub firmy narzędzia i procesy.

#### Definiowanie Umiejętności w `package.json`
Niestandardowe umiejętności Copilota są definiowane w pliku `package.json` (lub w innych, podobnych plikach konfiguracyjnych w zależności od ekosystemu).
Sekcja `copilot.skills` w `package.json` służy do deklarowania umiejętności. Każda umiejętność ma swój unikalny identyfikator, opis, oraz wskazuje na plik wykonywalny (skrypt) i opcjonalnie schemat argumentów.

```json
{
  "name": "my-project-skills",
  "version": "1.0.0",
  "copilot": {
    "skills": [
      {
        "id": "generateTestBoilerplate",
        "description": "Generuje boilerplate testu JUnit 5 dla podanej klasy Java.",
        "execute": {
          "command": "node",
          "args": ["./.copilot/skills/generateTest.js", "${fileBasenameNoExtension}"]
        },
        "args": {
          "fileBasenameNoExtension": {
            "type": "string",
            "description": "Nazwa pliku klasy Java (bez rozszerzenia), dla której ma być wygenerowany test."
          }
        }
      },
      {
        "id": "runCheckstyle",
        "description": "Uruchamia Checkstyle na plikach Java i raportuje naruszenia.",
        "execute": {
          "command": "java",
          "args": [
            "-jar",
            "./lib/checkstyle-8.45-all.jar",
            "-c",
            "./config/checkstyle.xml",
            "${file}"
          ]
        },
        "args": {
          "file": {
            "type": "string",
            "description": "Ścieżka do pliku Java do sprawdzenia."
          }
        }
      }
    ]
  }
}
```
W powyższym przykładzie zdefiniowano dwie umiejętności: `generateTestBoilerplate` i `runCheckstyle`. Każda z nich ma `id`, `description` i sekcję `execute` definiującą sposób jej uruchomienia. Sekcja `args` opisuje argumenty, jakich oczekuje umiejętność.

#### Wywoływanie Zewnętrznych Skryptów lub Kodu
Sekcja `execute` w definicji umiejętności jest kluczowa. Określa ona, jaki program ma zostać uruchomiony i z jakimi argumentami. Może to być dowolny skrypt (Node.js, Python, Bash) lub plik wykonywalny.
-   `command`: Program do uruchomienia (np. `node`, `python`, `bash`, `java`).
-   `args`: Lista argumentów przekazywanych do programu. Copilot może automatycznie wstrzykiwać zmienne kontekstowe, takie jak `${file}`, `${selection}`, `${fileBasenameNoExtension}`.

Przykład skryptu `generateTest.js`:
```javascript
// .copilot/skills/generateTest.js
const fs = require('fs');
const className = process.argv[2]; // Argument przekazany z package.json

if (!className) {
    console.error("Błąd: Nie podano nazwy klasy.");
    process.exit(1);
}

const testBoilerplate = `
package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class ${className}Tests {

    private ${className} ${className.toLowerCase()};

    @BeforeEach
    void setup() {
        // Implement test logic here
        this.${className.toLowerCase()} = new ${className}();
    }

    @Test
    void testExampleMethod() {
        // Implement test logic here
        assertThat(true).isTrue(); // Placeholder
    }

}
`;

const outputDir = './src/test/java/org/springframework/samples/petclinic/owner/';
const outputFilePath = `${outputDir}${className}Tests.java`;

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

fs.writeFileSync(outputFilePath, testBoilerplate);
console.log(`Wygenerowano boilerplate testu dla klasy ${className} w pliku ${outputFilePath}`);
```

#### Przekazywanie Argumentów i Obsługa Wyników
Copilot automatycznie parsuje argumenty z zapytania użytkownika i przekazuje je do umiejętności zgodnie ze zdefiniowanym schematem `args`. Wyniki działania umiejętności są zazwyczaj zwracane na standardowe wyjście (stdout). Copilot przechwytuje to wyjście i prezentuje je użytkownikowi. Ważne jest, aby skrypty generowały czytelne komunikaty.

## 💡 Przykłady Użycia

### Przykład 1: Użycie wbudowanej umiejętności do wyjaśniania kodu
Wyobraź sobie, że pracujesz nad plikiem `OwnerController.java` w projekcie `spring-petclinic` i natrafiasz na metodę, której działanie jest dla Ciebie niejasne.

**Kontekst:** Plik `OwnerController.java`, metoda `processCreationForm`.

```java
// src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java
// ...
    @PostMapping("/owners/new")
    public String processCreationForm(@Valid Owner owner, BindingResult result) {
        if (result.hasErrors()) {
            return "owners/createOrUpdateOwnerForm";
        }

        this.owners.save(owner);
        return "redirect:/owners/" + owner.getId();
    }
// ...
```

**Twoje pytanie do Copilota:** `Wyjaśnij mi, co robi metoda processCreationForm w tym OwnerController.`

**Oczekiwany rezultat:** Copilot wykorzysta wbudowaną umiejętność wyjaśniania kodu i dostarczy szczegółowy opis działania metody, w tym:
-   Adnotację `@PostMapping("/owners/new")` i jej znaczenie (obsługa żądań POST na ścieżce `/owners/new`).
-   Parametry `Owner owner` i `BindingResult result` oraz ich rolę w walidacji.
-   Logikę obsługi błędów walidacji (`result.hasErrors()`).
-   Zapisywanie nowego obiektu `Owner` do bazy danych (`this.owners.save(owner)`).
-   Przekierowanie po pomyślnym zapisie (`"redirect:/owners/" + owner.getId()`).

### Przykład 2: Implementacja prostej niestandardowej umiejętności (data/wersja Javy)
Stworzymy umiejętność, która po prostu wyświetli aktualną datę lub wersję Javy w projekcie.

**Kroki:**
1.  Dodaj definicję umiejętności w `package.json` w głównym katalogu `spring-petclinic`.
    ```json
    // package.json (w głównym katalogu spring-petclinic)
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
2.  Stwórz skrypt `./.copilot/skills/showInfo.js`:
    ```javascript
    // .copilot/skills/showInfo.js
    const query = process.argv[2];

    if (query && query.toLowerCase().includes("date")) {
        console.log(`Aktualna data: ${new Date().toLocaleString()}`);
    } else if (query && query.toLowerCase().includes("java version")) {
        // W rzeczywistości to wymagałoby parsowania `java -version`
        // Dla uproszczenia:
        console.log("Wersja Javy używana przez spring-petclinic: Java 17");
    } else {
        console.log("Dostępne informacje: data, java version.");
    }
    ```

**Twoje pytanie do Copilota:** `Copilot, użyj umiejętności showProjectInfo, żeby pokazać aktualną datę.`
**Oczekiwany rezultat:** Copilot uruchomi skrypt i zwróci aktualną datę.

### Przykład 3: Generowanie boilerplate testu JUnit 5
Wykorzystamy umiejętność `generateTestBoilerplate` zdefiniowaną w teorii.

**Kontekst:** Chcesz stworzyć test jednostkowy dla klasy `OwnerRepository` w `spring-petclinic`.
**Twoje pytanie do Copilota:** `Copilot, użyj umiejętności generateTestBoilerplate dla OwnerRepository.`

**Oczekiwany rezultat:** Copilot wywoła skrypt `generateTest.js`, który utworzy plik `OwnerRepositoryTests.java` w odpowiednim katalogu testowym z podstawowym kodem testu JUnit 5.

```java
// Przykładowy wygenerowany plik: src/test/java/org/springframework/samples/petclinic/owner/OwnerRepositoryTests.java
package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class OwnerRepositoryTests {

    private OwnerRepository ownerrepository;

    @BeforeEach
    void setup() {
        // Prawdopodobnie tutaj potrzebna będzie mock implementacja lub Spring context
        // this.ownerrepository = new OwnerRepository(); // To nie zadziała bezpośrednio
    }

    @Test
    void testFindById() {
        // Implement test logic here, e.g., using a mocked repository
        assertThat(true).isTrue(); // Placeholder
    }

}
```

## ✅ Best Practices
-   **Modułowość i Reużywalność:** Projektuj umiejętności tak, aby były małe, skupione na jednym zadaniu i potencjalnie reużywalne.
-   **Jasne Opisy:** Zapewnij czytelne `description` dla każdej umiejętności, aby Copilot mógł lepiej zrozumieć, kiedy jej użyć.
-   **Walidacja Argumentów:** W skryptach umiejętności zawsze waliduj przekazywane argumenty, aby zapobiec nieoczekiwanym błędom.
-   **Obsługa Błędów:** Implementuj mechanizmy obsługi błędów i zwracaj meaningful komunikaty w przypadku niepowodzenia.
-   **Bezpieczeństwo:** Ostrożnie z uprawnieniami i dostępem, które dajesz umiejętnościom. Unikaj wykonywania niezaufanego kodu.
-   **Dokumentacja:** Dokumentuj swoje niestandardowe umiejętności, aby inni członkowie zespołu mogli z nich korzystać i je rozwijać.
-   **Zależności:** Zarządzaj zależnościami skryptów umiejętności. Upewnij się, że wszystkie potrzebne narzędzia są dostępne w środowisku wykonania.
-   **Testowanie Umiejętności:** Testuj swoje umiejętności tak, jak testujesz zwykły kod.

## ⚠️ Common Pitfalls
-   **Niejasne Zapytania:** Użytkownicy mogą formułować zapytania w sposób, który nie pozwala Copilotowi na prawidłowe mapowanie do umiejętności. Wymaga to iteracji i dopracowania `description` umiejętności.
-   **Błędy w `package.json`:** Literówki lub nieprawidłowa składnia w definicji umiejętności w `package.json` mogą sprawić, że umiejętność nie będzie wykrywana.
-   **Problemy ze Ścieżkami:** Nieprawidłowe ścieżki do skryptów lub narzędzi w sekcji `execute` prowadzące do błędów "file not found".
-   **Brak Obsługi Kontekstu:** Umiejętności, które nie potrafią efektywnie wykorzystać kontekstu kodu lub rozmowy, mogą być mniej użyteczne.
-   **Zbyt Złożone Skrypty:** Skrypty wykonujące zbyt wiele zadań mogą być trudne w debugowaniu i utrzymaniu. Lepiej dzielić je na mniejsze, atomowe umiejętności.
-   **Błędy Środowiskowe:** Skrypt umiejętności może działać lokalnie, ale zawieść w środowisku Copilota z powodu brakujących zależności lub nieprawidłowej konfiguracji PATH.
-   **Brak Informacji Zwrotnej:** Umiejętność, która nie zwraca żadnego komunikatu na stdout, może sprawić wrażenie, że nic się nie stało.
-   **Bezpieczeństwo:** Uruchamianie dowolnego kodu, zwłaszcza z internetu, może prowadzić do luk bezpieczeństwa. Zawsze weryfikuj źródła.

## 🔗 Dodatkowe Zasoby
-   [Oficjalna dokumentacja GitHub Copilot Agent Skills](https://docs.github.com/en/copilot/github-copilot-enterprise/managing-github-copilot-in-your-organization/about-github-copilot-agent-skills) (Pamiętaj, że linki mogą ulegać zmianom)
-   [Artykuły na blogu GitHub dotyczące Copilot Agents](https://github.blog/tag/copilot/)
-   [Repozytorium spring-petclinic](https://github.com/spring-projects/spring-petclinic) - kontekst do ćwiczeń.
