# Tryb Agent - Fundament Pracy z Copilot

## 🎯 Cele Szkolenia
Po ukończeniu tego modułu będziesz potrafił(a):
- Zrozumieć podstawowe koncepcje, architekturę i filozofię działania agentów GitHub Copilot.
- Efektywnie wykorzystywać wbudowanych agentów (@workspace, @vscode, @agent, @terminal, @search) do różnorodnych, złożonych zadań programistycznych, wykraczających poza proste autouzupełnianie.
- Planować, monitorować i iterować nad zadaniami wykonywanymi przez agentów, analizując ich plany działania i modyfikując je w celu optymalizacji.
- Świadomie zarządzać kontekstem i pamięcią agentów (krótkotrwałą i długotrwałą) w celu uzyskania maksymalnie spójnych, trafnych i precyzyjnych odpowiedzi.
- Stosować zaawansowane najlepsze praktyki w interakcji z agentami, minimalizując ryzyko typowych pułapek i nieporozumień.
- Integrować agentów Copilot w codzienne procesy deweloperskie, takie jak refaktoryzacja, generowanie testów, debugowanie i dokumentowanie, w celu znaczącego zwiększenia produktywności i jakości tworzonego oprogramowania.

## 📚 Teoria

### 💡 Co to jest Agent GitHub Copilot i Jak Działa?
Agent GitHub Copilot to innowacyjny system wspomagający programowanie, który wykracza poza tradycyjne funkcje autouzupełniania kodu. Jest to inteligentny asystent, osadzony bezpośrednio w Twoim środowisku deweloperskim (głównie VS Code), który wykorzystuje zaawansowane duże modele językowe (Large Language Models – LLMs) do rozumienia Twoich intencji wyrażonych w języku naturalnym, kontekstu Twojego kodu oraz całego projektu.

**Główna zasada działania:** Agenci Copilot działają na zasadzie "narzędzi" (tools) i "planowania" (planning). Kiedy zadajesz agentowi pytanie lub wydajesz polecenie, LLM interpretuje Twoje zapytanie. Następnie, na podstawie tej interpretacji, generuje plan działania, który składa się z sekwencji kroków. Każdy krok może obejmować użycie jednego z dostępnych narzędzi (np. odczytanie pliku, wykonanie komendy terminala, wyszukanie w internecie) lub bezpośrednią modyfikację kodu. To podejście pozwala agentom na wykonywanie złożonych zadań, które wymagają interakcji z różnymi aspektami środowiska deweloperskiego.

**Rola w IDE:** Agenci działają w tle, monitorując Twój kod, otwarte pliki i aktywne okna. Dzięki temu są w stanie dostarczyć kontekstowe sugestie i odpowiedzi. Ich celem jest nie tylko pisanie kodu za Ciebie, ale także edukowanie, wskazywanie lepszych praktyk i przyspieszanie procesu decyzyjnego, redukując tzw. "cognitive load".

### 🌐 Typy Agentów (Standardowe, Wbudowane i Niestandardowe)
GitHub Copilot oferuje bogaty zestaw predefiniowanych agentów, każdy z nich jest zoptymalizowany pod kątem specyficznych zadań i ma dostęp do określonych narzędzi i zakresu wiedzy.

*   **`@workspace`**:
    *   **Specjalizacja**: Rozumienie i nawigacja po całym Twoim projekcie.
    *   **Zdolności**: Przeszukiwanie plików, analiza struktury katalogów, zależności, plików konfiguracyjnych (np. `pom.xml`, `package.json`, `Dockerfile`), identyfikacja głównych komponentów i przepływów danych. Może odpowiadać na pytania dotyczące architektury, lokalizacji definicji klas, użycia zmiennych w całym projekcie.
    *   **Praktyczne zastosowania**: Szybkie zapoznawanie się z nowym projektem, rozwiązywanie problemów związanych z zależnościami, znajdowanie wszystkich miejsc, w których używana jest dana funkcja.
    *   **Przykład interakcji**: `@workspace Zidentyfikuj wszystkie klasy kontrolerów Spring w tym projekcie i podaj ich ścieżki.`

*   **`@vscode`**:
    *   **Specjalizacja**: Interakcja i pomoc w ramach środowiska Visual Studio Code.
    *   **Zdolności**: Odpowiadanie na pytania dotyczące funkcji VS Code, skrótów klawiszowych, konfiguracji, rozszerzeń, problemów z lintingiem, debugowaniem w VS Code. Może sugerować komendy VS Code do wykonania.
    *   **Praktyczne zastosowania**: Nauka i optymalizacja pracy z VS Code, rozwiązywanie problemów z konfiguracją edytora, odkrywanie nowych funkcji.
    *   **Przykład interakcji**: `@vscode Jak mogę skonfigurować automatyczne formatowanie kodu w VS Code dla plików Java?`

*   **`@terminal`**:
    *   **Specjalizacja**: Wykonywanie komend w terminalu systemowym.
    *   **Zdolności**: Uruchamianie kompilacji (Maven, Gradle), wykonywanie testów, operacji Git (commit, push, pull, status), instalacja pakietów, uruchamianie aplikacji. Agent interpretuje Twoje polecenie i przekłada je na odpowiednią komendę CLI.
    *   **Praktyczne zastosowania**: Automatyzacja zadań deweloperskich, szybkie sprawdzanie stanu repozytorium, kompilowanie i testowanie projektu bez opuszczania czatu.
    *   **Przykład interakcji**: `@terminal sprawdź, czy w projekcie są jakieś niezaimplementowane zmiany w Git.`

*   **`@search`**:
    *   **Specjalizacja**: Pozyskiwanie informacji z internetu.
    *   **Zdolności**: Wyszukiwanie dokumentacji, artykułów technicznych, rozwiązań popularnych problemów, porównywanie technologii, wyjaśnianie błędów kompilacji, które mogą wynikać z bibliotek zewnętrznych.
    *   **Praktyczne zastosowania**: Szybkie rozwiązywanie problemów, nauka nowych technologii, pozyskiwanie "know-how" spoza kontekstu projektu.
    *   **Przykład interakcji**: `@search Jakie są najlepsze praktyki w zarządzaniu transakcjami w Spring Data JPA?`

*   **`@agent` (lub domyślny Copilot)**:
    *   **Specjalizacja**: Ogólne, złożone zadania programistyczne, często wymagające planowania i orkiestracji innych agentów.
    *   **Zdolności**: Refaktoryzacja kodu, generowanie nowych funkcji, pisanie testów jednostkowych i integracyjnych, debugowanie, optymalizacja algorytmów, tworzenie dokumentacji. Ten agent jest "mózgiem", który potrafi stworzyć spójny plan działania.
    *   **Praktyczne zastosowania**: Wszystkie operacje bezpośrednio związane z manipulacją kodem i złożonymi procesami deweloperskimi.
    *   **Przykład interakcji**: `@agent Zrefaktoryzuj ten fragment kodu tak, aby używał wzorca Factory Method.`

**Niestandardowe Agenty (Custom Agents)**: GitHub aktywnie pracuje nad rozszerzeniem możliwości Copilota o tworzenie niestandardowych agentów. W przyszłości umożliwi to programistom i organizacjom definiowanie własnych agentów, którzy będą mieli dostęp do specyficznych, wewnętrznych baz wiedzy (np. dokumentacja firmowa, wewnętrzne biblioteki) oraz niestandardowych narzędzi. To otworzy drogę do jeszcze głębszej integracji Copilota w specyficzne środowiska pracy.

### 🗣️ Podstawowe Interakcje z Agentami - Składnia i Kontekst
Interakcja z agentami Copilot jest zaprojektowana tak, aby była jak najbardziej zbliżona do naturalnej rozmowy. Odbywa się to głównie poprzez okno czatu Copilot w VS Code lub poprzez funkcję "inline chat" bezpośrednio w edytorze kodu.

1.  **Wywołanie Agenta**: Aby skierować swoje zapytanie do konkretnego agenta, użyj symbolu `@` następowanego przez jego nazwę.
    *   `@workspace Pokaż mi pliki konfiguracyjne.`
    *   `@agent Zoptymalizuj tę pętlę.` (po zaznaczeniu pętli)
    *   Jeśli nie określisz agenta, domyślnie używany jest agent `Copilot` (lub `@agent`), który podejmuje próbę zrozumienia i rozwiązania problemu ogólnie.

2.  **Formułowanie Zapytania/Polecenia**: Po wywołaniu agenta, opisz swoje zadanie lub pytanie w języku naturalnym. Agenci są elastyczni, ale precyzyjne i zwięzłe sformułowania zawsze dają lepsze rezultaty.

3.  **Zapewnianie Kontekstu**: Agenci automatycznie czerpią kontekst z Twojego aktualnego środowiska. To obejmuje:
    *   **Aktywny Plik**: Zawartość aktualnie otwartego pliku w edytorze.
    *   **Zaznaczony Kod**: Jeśli zaznaczysz fragment kodu, agent skupi się na nim.
    *   **Kontekst Czatowy**: Poprzednie wiadomości w bieżącej sesji czatu. Agent "pamięta" przebieg rozmowy.
    *   **Kontekst Projektu (@workspace)**: Agent `@workspace` może analizować całe repozytorium, pliki konfiguracyjne, zależności, co pozwala na zadawanie pytań o ogólną strukturę projektu.
    *   **Jawne Wskazanie Kontekstu**: Możesz również jawnie odwołać się do konkretnych plików lub linii kodu w swoim zapytaniu, np. `w pliku OwnerController.java, w metodzie saveOwner(...)`.

### ⚙️ Planowanie i Wykonanie Zadań przez Agentów - Proces i Kontrola

#### Jak Agenci Planują, Wykonują i Raportują Zadania
Złożone zadania dla agenta Copilot uruchamiają proces, który naśladuje podejście programisty do rozwiązywania problemów:

1.  **Interpretacja Intencji**: Na podstawie Twojego zapytania i dostępnego kontekstu, agent próbuje w pełni zrozumieć Twoją intencję. Czego dokładnie chcesz? Jaki jest ostateczny cel?
2.  **Generowanie Propozycji Planu (Thinking Phase)**: Agent w swojej "głowie" tworzy model problemu i generuje sekwencję logicznych kroków, które doprowadzą do rozwiązania. W tym momencie decyduje, których narzędzi użyć i w jakiej kolejności.
3.  **Prezentacja Planu Użytkownikowi**: Agent prezentuje Ci ten plan w oknie czatu. To Twoja szansa na weryfikację. Plan zazwyczaj zawiera:
    *   **Jasno określony cel** (Goal).
    *   **Listę kroków** (Steps), często z opisem, które narzędzie zostanie użyte (np. `Użyj @workspace, aby...`, `Wykonaj @terminal...`).
    *   Czasem także **oczekiwane rezultaty** każdego kroku.
4.  **Akceptacja/Modyfikacja/Odrzucenie Planu**: Masz pełną kontrolę nad planem. Możesz:
    *   **Akceptować** plan, pozwalając agentowi na automatyczne wykonanie kroków.
    *   **Modyfikować** plan, dodając lub usuwając kroki, zmieniając ich kolejność lub sugerując inne podejścia.
    *   **Odrzucić** plan i poprosić o nowe podejście lub po prostu zrezygnować z zadania.
5.  **Wykonanie Planu (Execution Phase)**: Po akceptacji, agent wykonuje kroki planu jeden po drugim. Możesz monitorować jego postępy w czasie rzeczywistym w oknie czatu, widząc, jakie narzędzia są aktywowane i jakie są ich wyniki.
6.  **Raportowanie Wyników i Iteracja**: Po zakończeniu planu, agent przedstawia rezultaty – może to być zmieniony kod, podsumowanie informacji, wyniki testów czy raport. Jeśli wynik nie jest satysfakcjonujący lub pojawiły się błędy, możesz kontynuować dialog, prosząc o poprawki, dodatkowe zmiany lub nowe podejście. Ten iteracyjny charakter jest kluczowy dla efektywnej pracy z agentami.

#### Struktura Planu (Kroki, Cel)
Plany agentów są zazwyczaj czytelne i logiczne. Na przykład, aby dodać nową funkcjonalność, agent może przedstawić plan składający się z:
-   **Cel:** Opis tego, co ma zostać osiągnięte.
-   **Krok 1: Analiza istniejącej struktury.** (`Użyj @workspace, aby zrozumieć, gdzie najlepiej umieścić nową klasę...`)
-   **Krok 2: Generowanie szkieletu kodu.** (`Utwórz nową klasę UserRegistrationService.java z podstawową strukturą.`)
-   **Krok 3: Implementacja logiki biznesowej.** (`Dodaj metodę registerUser(User user) uwzględniając walidację i zapis do bazy danych.`)
-   **Krok 4: Tworzenie testów.** (`Wygeneruj test jednostkowy dla UserRegistrationService.`)
-   **Krok 5: Aktualizacja API/kontrolera.** (`Zmodyfikuj UserController.java, aby używał nowej usługi.`)

#### Obsługa Błędów i Iteracje w Planie
Agenci Copilot są zaprojektowani tak, aby reagować na błędy i umożliwiać iteracyjne podejście:
-   **Detekcja Błędów**: Jeśli agent napotka błąd podczas kompilacji po zmianie kodu, niepowodzenie testu lub problem z wykonaniem komendy terminala, zgłosi to w czacie.
-   **Diagnoza i Sugestie**: W wielu przypadkach agent spróbuje zdiagnozować przyczynę błędu i zasugerować możliwe rozwiązania lub modyfikacje w planie.
-   **Kontynuacja Dialogu**: Możesz akceptować sugestie agenta, odrzucać je lub dostarczać własne wskazówki. Jest to ciągły proces uczenia się i dostosowywania, gdzie programista i agent wspólnie dążą do rozwiązania problemu. Nie bój się prosić agenta o "naprawienie tego błędu" lub "spróbuj ponownie z innym podejściem".

### 🧠 Pamięć Agentów - Zarządzanie Kontekstem

#### Krótkotrwała i Długotrwała Pamięć Agenta
Zrozumienie, jak agenci zarządzają informacjami, jest kluczowe dla efektywnej interakcji:

1.  **Pamięć Krótkotrwała (Kontekst Sesji Czatowej)**:
    *   **Charakterystyka**: To pamięć o bieżącej konwersacji. Agent "pamięta" wszystkie poprzednie wiadomości w aktywnej sesji czatu – Twoje pytania, jego odpowiedzi, fragmenty kodu, które zostały omówione.
    *   **Zastosowanie**: Umożliwia prowadzenie spójnych, wieloetapowych dialogów. Dzięki niej możesz odwoływać się do wcześniej omawianych kwestii bez konieczności ich powtarzania.
    *   **Ograniczenia**: Jest efemeryczna. Zazwyczaj resetuje się po zamknięciu okna czatu, po ponownym uruchomieniu VS Code, lub jeśli sesja jest zbyt długa i kontekst przekroczy wewnętrzny limit tokenów LLM.
    *   **Wpływ**: Im krótsza i bardziej skupiona rozmowa, tym lepsza jakość interakcji. Długie, rozbudowane sesje mogą prowadzić do "zgubienia wątku" przez agenta.

2.  **Pamięć Długotrwała (Wiedza Ogólna i Kontekst Projektu)**:
    *   **Charakterystyka**: To stała baza wiedzy agenta. Składa się z wiedzy, na której model LLM został wytrenowany (ogólne zasady programowania, składnia języków, popularne biblioteki, wzorce projektowe) oraz z dynamicznie pozyskiwanego kontekstu Twojego projektu (dostęp do plików poprzez `@workspace`).
    *   **Zastosowanie**: Jest zawsze dostępna i stanowi podstawę dla wszystkich interakcji. Agent może odwoływać się do niej niezależnie od bieżącej sesji czatu.
    *   **Wpływ**: Im lepiej zorganizowany projekt, tym łatwiej agentowi `@workspace` jest czerpać z tej pamięci, co przekłada się na trafniejsze sugestie.

#### Zarządzanie Kontekstem Konwersacji
Efektywne zarządzanie kontekstem to sztuka prowadzenia rozmowy z agentem tak, aby zawsze miał on dostęp do najbardziej relewantnych informacji.

*   **Bądź Precyzyjny i Kontekstowy**:
    *   Zamiast `popraw ten błąd`, powiedz `w pliku UserService.java, w metodzie createUser, występuje błąd NullPointerException. Znajdź przyczynę i zaproponuj poprawkę.`
    *   Jeśli pracujesz nad konkretnym fragmentem kodu, zaznacz go w edytorze przed zadaniem pytania.
*   **Segmentacja Zadań**: Dla bardzo złożonych problemów, rozważ dzielenie ich na mniejsze, logiczne etapy. Zakończ jeden etap, zweryfikuj wynik, a dopiero potem przejdź do następnego, rozpoczynając ewentualnie nową sesję czatu, jeśli stary kontekst stał się zbyt duży.
*   **"Świeży Start"**: Jeśli zauważysz, że odpowiedzi agenta stają się chaotyczne, nieprecyzyjne lub nieadekwatne, oznacza to, że kontekst sesji mógł zostać zanieczyszczony lub przekroczony. W takim przypadku warto rozpocząć nową sesję czatu, aby zapewnić agentowi "czystą kartę".
*   **Wskazówki Dotyczące Plików**: Jeśli Twoje pytanie dotyczy wielu plików, możesz jawnie wspomnieć o nich w zapytaniu, np. `W plikach OwnerController.java i OwnerRepository.java, jak mogę dodać nową walidację?`.

### 🛠️ Narzędzia dla Agentów - Rozszerzanie Zdolności Copilota

Agenci Copilot to coś więcej niż tylko interfejs do LLM; są to "inteligentni" operatorzy narzędzi. To właśnie dostęp do tych narzędzi pozwala im na wykonywanie konkretnych, operacyjnych zadań w Twoim środowisku deweloperskim.

#### Szczegółowe Możliwości i Przykłady Użycia Narzędzi

1.  **`workspace` Tool**:
    *   **Głębsza Analiza**: Pozwala agentowi na budowanie wewnętrznej reprezentacji struktury projektu, relacji między klasami, dziedziczenia, użycia interfejsów, konfiguracji Maven/Gradle. Może symulować "przeskakiwanie do definicji" lub "znajdowanie wszystkich referencji".
    *   **Przypadki Użycia Zaawansowane**: Analiza złożoności cyklometrycznej metody w całym projekcie, identyfikacja potencjalnych miejsc na refaktoryzację modułową, zrozumienie, jak dany serwis jest używany przez różne kontrolery.
    *   **Przykład**: `@workspace znajdź wszystkie miejsca, w których wywoływana jest metoda `save` z `OwnerRepository`, i pokaż, jakie parametry są tam przekazywane.`

2.  **`vscode` Tool**:
    *   **Kontrola IDE**: Agent może wykorzystać to narzędzie do manipulowania elementami UI VS Code, uruchamiania wbudowanych funkcji edytora (np. refaktoryzacja "Extract Method", "Rename Symbol"), otwierania paneli (problemy, debugowanie, terminal), a nawet instalowania rozszerzeń.
    *   **Przypadki Użycia Zaawansowane**: Automatyzacja powtarzalnych operacji w edytorze, pomoc w tworzeniu niestandardowych skrótów klawiszowych, rozwiązywanie problemów z konfiguracją debugera.
    *   **Przykład**: `@vscode otwórz panel Problems i podsumuj wszystkie błędy kompilacji w otwartych plikach.`

3.  **`search` Tool**:
    *   **Dynamiczne Pozyskiwanie Wiedzy**: Gdy wewnętrzna wiedza LLM jest niewystarczająca lub przestarzała, to narzędzie staje się nieocenione. Agent sam decyduje, kiedy potrzebuje "poszukać w Google" i potrafi skutecznie filtrować i syntezować informacje z wyników.
    *   **Przypadki Użycia Zaawansowane**: Badanie nowych wersji bibliotek (np. Spring Boot 3.2 vs 3.1), szukanie alternatywnych rozwiązań dla danego problemu (np. wzorce cache'owania w Javie), porównywanie wydajności różnych implementacji.
    *   **Przykład**: `@search porównaj wydajność HashMap i ConcurrentHashMap w scenariuszach wielowątkowych w Javie i kiedy powinno się używać której.`

4.  **`terminal` Tool**:
    *   **Interakcja z Systemem Operacyjnym**: Umożliwia agentowi na uruchamianie wszelkich komend dostępnych w CLI. To kluczowe do zadań takich jak: budowanie projektu, uruchamianie testów, operacje Git, interakcja z Dockerem, zarządzanie zależnościami (npm, pip).
    *   **Przypadki Użycia Zaawansowane**: Automatyzacja procesu CI/CD (lokalnie), generowanie raportów pokrycia kodu (Jacoco), migracje baz danych, uruchamianie skryptów diagnostycznych.
    *   **Przykład**: `@terminal użyj narzędzia Maven do wygenerowania raportu pokrycia kodu dla całego projektu spring-petclinic. Gdzie będzie znajdował się ten raport?`

#### Wpływ Dostępnych Narzędzi na Możliwości Agenta
Synergia między LLM a narzędziami jest tym, co czyni agentów Copilot tak potężnymi:
-   **Zdolność do Działania**: Bez narzędzi, agenci byliby tylko generatorami tekstu. Narzędzia nadają im zdolność do _działania_ w Twoim środowisku.
-   **Podstawa dla Planowania**: Decyzje agenta dotyczące planowania zadań są bezpośrednio uzależnione od dostępnych narzędzi. Agent wie, co potrafi zrobić, bo wie, jakie narzędzia ma do dyspozycji.
-   **Kontekst Dynamiczny**: Narzędzia, takie jak `workspace` i `terminal`, pozwalają agentowi na dynamiczne pozyskiwanie świeżego kontekstu z Twojego projektu i systemu, co jest kluczowe dla trafnych i aktualnych odpowiedzi.
-   **Weryfikacja i Iteracja**: Możliwość uruchamiania testów (`@terminal`) lub przeglądania plików (`@workspace`) pozwala agentowi na samodzielną weryfikację poprawności swoich zmian i iterację nad rozwiązaniami, co prowadzi do lepszych rezultatów końcowych.

## 💡 Przykłady Użycia

### Przykład 1: Zaawansowana Analiza Zależności Projektu z `@workspace`
**Cel:** Zrozumienie, które moduły w `spring-petclinic` zależą od `OwnerRepository.java` i jak są one ze sobą powiązane.

**Interakcja:**
```
@workspace Pokaż mi drzewo zależności dla `OwnerRepository.java` w projekcie spring-petclinic. Chodzi mi o to, które klasy bezpośrednio używają tego repozytorium i jak one są powiązane z innymi komponentami.
```

**Oczekiwana odpowiedź (fragment):**
```
**Analiza zależności dla `OwnerRepository.java`:**

Głównymi konsumentami `OwnerRepository.java` są:

1.  **`OwnerController.java`**:
    *   Używa `OwnerRepository` do zapisu (metoda `save`) i pobierania (metody `findById`, `findByLastName`) danych właścicieli.
    *   `OwnerController` jest komponentem warstwy prezentacji (Spring MVC), odpowiedzialnym za obsługę żądań HTTP związanych z właścicielami.
    *   Jest powiązany z `Owner` (model), `BindingResult` (walidacja), `ModelAndView` (widoki).

2.  **`OwnerService.java` (jeśli istnieje warstwa serwisowa, w PetClinic logika jest często w kontrolerach dla uproszczenia)**:
    *   Jeśli projekt byłby bardziej rozbudowany, istniałaby tu warstwa serwisowa, która orkiestrowałaby operacje na danych, np. `OwnerService` używałby `OwnerRepository` do logiki biznesowej.
    *   `OwnerService` byłby używany przez `OwnerController` (wstrzykiwanie zależności).

**Podsumowanie powiązań:**
`OwnerController` -> `OwnerRepository`
(Potencjalnie) `OwnerController` -> `OwnerService` -> `OwnerRepository`

Drzewo zależności dla `OwnerRepository.java` jest więc dość płaskie, głównie kontroler bezpośrednio wstrzykuje i używa repozytorium.
```
**Wyjaśnienie:** Agent `@workspace` dogłębnie analizuje importy, wstrzykiwanie zależności i użycia w całym projekcie, aby zmapować relacje między komponentami.

### Przykład 2: Generowanie Testów Integracyjnych dla Nowego Endpointu z `@agent`
**Cel:** Dodać nowy endpoint REST do `VetController.java` zwracający listę weterynarzy według specjalizacji, a następnie wygenerować dla niego test integracyjny.

**Interakcja (krok 1 - dodanie endpointu):**
1.  Otwórz plik `VetController.java`.
2.  W czacie Copilot wpisz:
    ```
    @agent Dodaj nowy endpoint GET `/vets/specialty/{specialtyName}` do VetController.java, który zwróci listę weterynarzy posiadających daną specjalizację. Użyj @RequestParam dla nazwy specjalizacji. Zapewnij, że obsługa błędów (np. brak specjalizacji) jest właściwa.
    ```
    (Agent zaproponuje plan, zaimplementuje endpoint w kontrolerze i być może w serwisie/repozytorium, zastosuj zmiany).

**Interakcja (krok 2 - generowanie testu):**
1.  Po zastosowaniu zmian w `VetController.java`.
2.  W czacie Copilot wpisz:
    ```
    @agent Wygeneruj test integracyjny dla nowego endpointu `/vets/specialty/{specialtyName}` w VetController.java. Test powinien sprawdzić, czy endpoint zwraca poprawną listę weterynarzy dla istniejącej specjalizacji oraz pustą listę dla nieistniejącej. Użyj MockMvc.
    ```

**Oczekiwana odpowiedź (fragment planu i kodu testu):**
```
**Cel:** Wygenerować test integracyjny dla endpointu `/vets/specialty/{specialtyName}` w `VetController.java`.

**Plan:**
1.  **Analiza istniejących testów:** Użyj @workspace, aby znaleźć istniejące testy integracyjne dla `VetController` i zrozumieć ich strukturę.
2.  **Tworzenie nowego pliku testowego:** Jeśli to konieczne, utwórz `VetControllerIntegrationTests.java` w odpowiednim pakiecie testowym.
3.  **Konfiguracja MockMvc:** Upewnij się, że test używa `@WebMvcTest` lub konfiguruje `MockMvc`.
4.  **Implementacja testu dla istniejącej specjalizacji:**
    *   Wstrzyknij `VetRepository` i `SpecialtyRepository` (lub mokuj je).
    *   Dodaj przykładowe dane (weterynarzy i specjalizacje).
    *   Wykonaj zapytanie GET do `/vets/specialty/radiology`.
    *   Zweryfikuj status HTTP (200 OK) i zawartość JSON.
5.  **Implementacja testu dla nieistniejącej specjalizacji:**
    *   Wykonaj zapytanie GET do `/vets/specialty/nonexistent`.
    *   Zweryfikuj status HTTP i czy zwracana jest pusta lista.
6.  **Prezentacja kodu testowego.**
```

**Oczekiwany kod testu (fragment):**
```java
// W src/test/java/org/springframework/samples/petclinic/vet/VetControllerIntegrationTests.java
package org.springframework.samples.petclinic.vet;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(VetController.class)
class VetControllerIntegrationTests {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private VetRepository vets;

    private Vet james;
    private Specialty radiology;
    private Specialty surgery;

    @BeforeEach
    void setup() {
        radiology = new Specialty();
        radiology.setId(1);
        radiology.setName("radiology");

        surgery = new Specialty();
        surgery.setId(2);
        surgery.setName("surgery");

        james = new Vet();
        james.setId(1);
        james.setFirstName("James");
        james.setLastName("Carter");
        james.addSpecialty(radiology);

        given(this.vets.findBySpecialtyName(radiology.getName())).willReturn(Arrays.asList(james));
        given(this.vets.findBySpecialtyName(surgery.getName())).willReturn(Collections.emptyList()); // dla nieistniejącej
        given(this.vets.findBySpecialtyName(anyString())).willReturn(Collections.emptyList()); // ogólny przypadek
    }

    @Test
    void testShowVetsBySpecialtyExisting() throws Exception {
        mockMvc.perform(get("/vets/specialty/{specialtyName}", "radiology")
            .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].firstName").value("James"));
    }

    @Test
    void testShowVetsBySpecialtyNotExisting() throws Exception {
        mockMvc.perform(get("/vets/specialty/{specialtyName}", "nonexistent")
            .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$").isEmpty());
    }
}
```
**Wyjaśnienie:** Agent nie tylko generuje test, ale także potrafi poprawnie skonfigurować `MockMvc`, użyć Mockito do mokowania zależności i stworzyć asercje, które weryfikują zarówno pozytywne, jak i negatywne scenariusze.

### Przykład 3: Szukanie Rozwiązań Błędów Kompilacji z `@search`
**Cel:** Rozwiązanie błędu kompilacji, który pojawia się po aktualizacji wersji Spring Boot i dotyczy problemu z migracją baz danych Flyway.

**Interakcja:**
```
@search Otrzymuję błąd "No qualifying bean of type 'org.flywaydb.core.Flyway' available" po aktualizacji Spring Boot do wersji 3.x. Jak to naprawić?
```

**Oczekiwana odpowiedź (fragment):**
```
**Rozwiązanie błędu "No qualifying bean of type 'org.flywaydb.core.Flyway' available" po aktualizacji Spring Boot 3.x:**

Ten błąd często występuje, ponieważ w Spring Boot 3.x (który wymaga Spring Framework 6 i Jakarta EE 9+), Flyway zaktualizował swoje pakiety. Starsze wersje Flyway używały pakietów `javax.*`, podczas gdy nowe wymagają `jakarta.*`.

**Możliwe rozwiązania:**

1.  **Zaktualizuj wersję Flyway**: Upewnij się, że używasz wersji Flyway, która jest kompatybilna ze Spring Boot 3.x i Jakarta EE. Zazwyczaj jest to Flyway w wersji 8.x lub nowszej (sprawdź oficjalną dokumentację Spring Boot dla rekomendowanej wersji).
    *   W pliku `pom.xml` (Maven):
        ```xml
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
            <version>9.16.0</version> <!-- Sprawdź najnowszą kompatybilną wersję -->
        </dependency>
        ```
    *   W pliku `build.gradle` (Gradle):
        ```groovy
        dependencies {
            implementation 'org.flywaydb:flyway-core:9.16.0' // Sprawdź najnowszą kompatybilną wersję
        }
        ```
2.  **Sprawdź konfigurację bazy danych**: Upewnij się, że Spring Boot może poprawnie skonfigurować źródło danych dla Flyway.
    *   W `application.properties`:
        ```properties
        spring.flyway.enabled=true
        spring.datasource.url=jdbc:postgresql://localhost:5432/petclinic
        spring.datasource.username=petclinic
        spring.datasource.password=petclinic
        ```
3.  **Dodatkowa konfiguracja (rzadziej)**: W niektórych przypadkach może być konieczne jawne zdefiniowanie beana `Flyway` lub dostosowanie jego konfiguracji.

**Wskazówki:**
*   Zawsze sprawdź `Migracja do Spring Boot 3.0` w oficjalnej dokumentacji Spring Boot.
*   Upewnij się, że wszystkie zależności są zaktualizowane i kompatybilne z nową wersją Spring Boot.
```
**Wyjaśnienie:** Agent `@search` przeszukuje fora deweloperskie i dokumentację, aby zidentyfikować typowe przyczyny i rozwiązania dla konkretnych błędów, oferując kontekstowe porady i fragmenty kodu.

### Przykład 4: Uruchamianie Debugera z `@vscode`
**Cel:** Szybkie uruchomienie aplikacji `spring-petclinic` w trybie debugowania i ustawienie breakpointu.

**Interakcja:**
```
@vscode Uruchom aplikację `spring-petclinic` w trybie debugowania. Następnie ustaw breakpoint w metodzie `processUpdateOwnerForm` w `OwnerController.java` na pierwszej linii logiki biznesowej.
```

**Oczekiwana odpowiedź:**
```
**Plan debugowania aplikacji:**

1.  **Uruchomienie debugera:** Użyję wbudowanej konfiguracji debugowania VS Code dla Spring Boot, aby uruchomić aplikację `spring-petclinic` w trybie debugowania.
2.  **Ustawienie breakpointu:** Po uruchomieniu aplikacji, otworzę plik `OwnerController.java` i ustawię breakpoint w metodzie `processUpdateOwnerForm` na linii zawierającej `if (result.hasErrors()) {`.

**Status:** Aplikacja została uruchomiona w trybie debugowania. Breakpoint został ustawiony. Możesz teraz wywołać ten endpoint w przeglądarce, aby trafić w breakpoint.
```
**Wyjaśnienie:** Agent `@vscode` potrafi wykonywać złożone operacje w środowisku VS Code, symulując interakcje użytkownika z UI, co jest szczególnie przydatne do automatyzacji zadań związanych z debugowaniem i konfiguracją środowiska.

## ✅ Best Practices
-   **Zawsze Weryfikuj Wygenerowany Kod**: Traktuj Copilota jako zaawansowanego partnera, a nie autorytet. Generowany kod może zawierać błędy, nie być optymalny, czy nie spełniać wszystkich Twoich wymagań. Krytyczna ocena i testowanie są niezbędne.
-   **Formułuj Zapytania Metodą "Zasady 5W"**: Who, What, When, Where, Why. Kto ma być dotknięty zmianą? Co dokładnie ma się zmienić? Kiedy ma się to wydarzyć (np. po wciśnięciu przycisku)? Gdzie (w jakim pliku, metodzie)? Dlaczego to robimy (jaki problem rozwiązujemy)?
-   **Podziel Złożone Zadania na Mniejsze, Logiczne Kroki**: Zamiast prosić o "utworzenie całej aplikacji", zacznij od "utwórz szkielet klasy User", następnie "dodaj metodę registerUser", potem "napisz test dla registerUser" itd. Pozwala to na większą kontrolę i łatwiejsze poprawki.
-   **Wykorzystaj Potencjał `inline chat`**: Do szybkich modyfikacji w obrębie jednego pliku, `inline chat` jest często bardziej efektywny niż główne okno czatu, ponieważ kontekst jest naturalnie ograniczony do zaznaczonego fragmentu kodu.
-   **Zarządzaj Kontekstem Aktywnie**: Jeśli rozmowa staje się zbyt długa lub agent zaczyna generować nieistotne odpowiedzi, rozważ rozpoczęcie nowej sesji czatu. Możesz również aktywnie kierować kontekst, odwołując się do konkretnych plików lub fragmentów kodu.
-   **Poznaj Granice Każdego Agenta**: Rozumienie, do czego służy `@workspace`, a do czego `@search`, pozwoli Ci na wybranie najodpowiedniejszego narzędzia do danego zadania i uniknięcie frustracji.
-   **Eksperymentuj i Ucz się**: Najlepszym sposobem na opanowanie Copilota jest praktyka. Regularnie próbuj używać go do różnych zadań, obserwuj jego zachowanie i dostosowuj swoje podejście.
-   **Dokumentuj Swoje Prompty**: Dla powtarzalnych zadań, takich jak generowanie boilerplate'u, refaktoryzacja, czy tworzenie testów, warto zapisywać skuteczne prompty. Możesz je później wykorzystać ponownie lub udostępnić zespołowi.

## ⚠️ Common Pitfalls
-   **Zbyt Szerokie lub Niejasne Zapytania**: Generują generyczne lub błędne odpowiedzi. Przykład: "Popraw mój kod" zamiast "Zrefaktoryzuj metodę `calculatePrice` w `OrderService.java` tak, aby była bardziej wydajna dla dużych zestawów danych".
-   **Brak Weryfikacji Bezpieczeństwa**: Kod generowany przez Copilota może nie zawsze spełniać wymogi bezpieczeństwa (np. SQL Injection, XSS). Zawsze przeprowadzaj analizę bezpieczeństwa i stosuj narzędzia SCA/SAST.
-   **Zależność bez Zrozumienia**: Ślepe poleganie na Copilocie może prowadzić do zmniejszenia własnych umiejętności programistycznych i trudności w debugowaniu lub modyfikowaniu kodu, którego się nie rozumie.
-   **Przeciążenie Kontekstu Czatowego**: Zbyt długie sesje czatu mogą powodować, że agent "zapomni" wcześniejsze instrukcje lub kontekst, prowadząc do niespójnych odpowiedzi.
-   **Błędy Interpretacyjne Agenta**: Agenci czasami źle interpretują intencje lub niuanse języka naturalnego, zwłaszcza w złożonych domenach biznesowych. Wymaga to cierpliwości i precyzyjnego doprecyzowania.
-   **Nieadekwatne Użycie Narzędzi**: Próba użycia `@search` do zlokalizowania pliku w projekcie zamiast `@workspace`, co prowadzi do nieefektywnych lub błędnych wyników.
-   **Przestarzała Wiedza Ogólna LLM**: Modele językowe są trenowane na danych do określonej daty. Mogą nie znać najnowszych wersji bibliotek, frameworków czy najlepszych praktyk, które pojawiły się po tej dacie. W takich przypadkach `@search` jest kluczowe.
-   **Problemy z Zachowaniem Stanu**: W bardziej złożonych scenariuszach, gdzie wymagane jest utrzymywanie stanu między wieloma interakcjami, agenci mogą mieć trudności, co wymaga ręcznej interwencji.

## 🔗 Dodatkowe Zasoby
-   [Oficjalna dokumentacja GitHub Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat)
-   [Co to jest GitHub Copilot Chat? (Video)](https://www.youtube.com/watch?v=F07g8qA3hQY)
-   [Blog GitHub Copilot - Najnowsze aktualizacje i funkcje](https://github.blog/topics/copilot/)
-   [Ścieżki Szkoleniowe Microsoft Learn dla Copilota](https://learn.microsoft.com/en-us/training/paths/get-started-github-copilot/)
-   [Repozytorium Spring PetClinic na GitHubie - doskonałe do ćwiczeń](https://github.com/spring-projects/spring-petclinic)
