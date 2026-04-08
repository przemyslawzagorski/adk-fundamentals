 규모: ~3000 słów
# Moduł 3: Customization - Dostosowanie GitHub Copilot do Twojego Projektu

## 🎯 Cele Szkolenia
Po ukończeniu tego modułu będziesz w stanie:
- Skonfigurować GitHub Copilot do przestrzegania specyficznych standardów kodowania i wytycznych projektowych za pomocą plików `.github/copilot-instructions.md`.
- Tworzyć i zarządzać niestandardowymi plikami promptów w katalogu `.copilot/prompts/` w celu automatyzacji powtarzalnych zadań i generowania złożonego kodu.
- Rozumieć i implementować zaawansowane konfiguracje, takie jak hooki agentów, w celu integracji Copilota z istniejącymi procesami deweloperskimi i narzędziami.
- Zastosować wiedzę o dostosowywaniu Copilota w praktycznych scenariuszach w projekcie `spring-petclinic`.
- Unikać typowych pułapek związanych z nadmierną konfiguracją lub nieprecyzyjnymi instrukcjami dla Copilota.

## 📚 Teoria

### 1. Instrukcje Niestandardowe (.github/copilot-instructions.md)
GitHub Copilot, choć potężny, często korzysta z ogólnych wzorców i najlepszych praktyk opartych na miliardach linii kodu. W realnych projektach zespoły deweloperskie posiadają jednak swoje unikalne konwencje, style kodowania, architekturę i specyficzne biblioteki. Aby Copilot mógł być naprawdę efektywnym asystentem, musi rozumieć i przestrzegać tych wewnętrznych wytycznych.

Plik `.github/copilot-instructions.md` (lub alternatywnie `.vscode/copilot-instructions.md` w kontekście VS Code) to kluczowe narzędzie do dostosowywania zachowania Copilota do specyficznych wymagań projektu. Jest to plik Markdown, który zawiera instrukcje, wytyczne, przykłady kodu, a nawet fragmenty dokumentacji, które Copilot powinien brać pod uwagę podczas generowania sugestii. Działa on jako dodatkowa baza wiedzy, która priorytetowo traktuje specyfikę Twojego projektu nad ogólnymi wzorcami.

#### Składnia Markdown dla instrukcji
Copilot interpretuje treści w pliku `copilot-instructions.md` podobnie jak każdy inny plik Markdown. Oznacza to, że możesz używać standardowej składni do strukturyzowania swoich instrukcji:
- **Nagłówki** (`#`, `##`, `###`) do organizacji sekcji i podsekcji, co ułatwia Copilotowi zrozumienie hierarchii i ważności reguł.
- **Listy** (numerowane i nienumerowane) do wyliczania zasad, wymagań lub kroków. Są idealne do prezentowania zbioru krótkich wytycznych.
- **Bloki kodu** (```java, ```python, etc.) są niezwykle ważne. Pozwalają na prezentowanie:
    - **Wzorców do naśladowania:** Przykłady kodu, które ilustrują preferowany styl, użycie bibliotek czy wzorców projektowych. Copilot będzie starał się naśladować ten styl.
    - **Kodu do unikania:** Przykłady anty-wzorców, które Copilot powinien identyfikować i pomagać w ich eliminowaniu lub sugerować alternatywne rozwiązania.
    - **Fragmentów konfiguracji:** Schematy konfiguracji, które powinny być stosowane.
- **Cytaty** (`>`) do wyróżniania ważnych uwag, ostrzeżeń lub kluczowych zasad, które wymagają szczególnej uwagi.
- **Linki** do zewnętrznej dokumentacji, wewnętrznych wiki, przewodników stylu kodu lub specyfikacji architektonicznych, dostarczając Copilotowi dodatkowego kontekstu zewnętrznego.

**Przykład zaawansowanej struktury:**
```markdown
# Wytyczne dla GitHub Copilot w projekcie spring-petclinic

## 💡 Ogólne Zasady Kodowania
- Zawsze używaj formatowania zgodnego z Google Java Format. Jest to domyślny standard w naszym projekcie.
- Preferuj lambdy zamiast anonimowych klas wewnętrznych w Java 8+.
- Unikaj magicznych liczb; zamiast tego używaj nazwanych stałych z odpowiednimi modyfikatorami dostępu (`public static final`).

## 🛠️ Wytyczne dla Spring Framework
- Wstrzykiwanie zależności zawsze przez konstruktor. **NIGDY** nie używaj `@Autowired` nad polem.
- Używaj adnotacji `@Service`, `@Repository`, `@Controller` we właściwych miejscach, zgodnie z trójwarstwową architekturą.
- Dla konfiguracji właściwości używaj adnotacji `@Value` z domyślnymi wartościami SpEL, np. `@Value("${app.setting:defaultValue}")`.

### 🔒 Bezpieczeństwo
- Zawsze sanitizuj dane wejściowe użytkownika, aby zapobiec atakom XSS i SQL Injection. Preferuj wbudowane mechanizmy frameworka (np. Spring Security).
- Używaj `PasswordEncoder` do przechowywania haseł.

## 🧪 Testy Jednostkowe
- Stosuj JUnit 5 i Mockito dla wszystkich testów jednostkowych.
- Nazwy metod testowych powinny być w formacie `nazwaTestowanejMetody_scenariusz_oczekiwanyWynik()`.
- Upewnij się, że testy są izotopowe (nie zależą od kolejności wykonania).

```java
// PRZYKŁAD KODU DO NAŚLADOWANIA (JUnit 5 + Mockito)
@ExtendWith(MockitoExtension.class)
class OwnerServiceTest {

    @Mock
    OwnerRepository ownerRepository;

    @InjectMocks
    OwnerServiceImpl ownerService;

    @Test
    void findOwnerById_existingOwner_returnsOwner() {
        // ... test logic ...
    }
}
```
```

#### Zakres i dziedziczenie instrukcji
Instrukcje dla Copilota są hierarchiczne i kontekstowe, co pozwala na precyzyjne sterowanie jego zachowaniem w różnych częściach projektu:
1.  **Globalne instrukcje:** Domyślne zachowania Copilota, oparte na jego podstawowym modelu trenowanym na ogromnej ilości kodu.
2.  **Instrukcje użytkownika:** Konfiguracja Copilota w Twoim środowisku deweloperskim (np. `settings.json` w VS Code). Dotyczy to osobistych preferencji, które mogą nadpisywać globalne ustawienia.
3.  **Instrukcje repozytorium:** Plik `.github/copilot-instructions.md` umieszczony w głównym katalogu repozytorium (np. `spring-petclinic/.github/copilot-instructions.md`). Te instrukcje mają zastosowanie do całego projektu i służą do zdefiniowania ogólnych wytycznych dla wszystkich deweloperów pracujących nad tym repozytorium.
4.  **Instrukcje katalogu:** Możesz umieścić `copilot-instructions.md` w dowolnych podkatalogach. Instrukcje z podkatalogów dziedziczą zasady z katalogów nadrzędnych i mogą je nadpisywać. Zasady z najbliższego pliku `copilot-instructions.md` w hierarchii katalogów mają najwyższy priorytet. Na przykład:
    *   `src/main/java/org/springframework/samples/petclinic/owner/.github/copilot-instructions.md` będzie miał wpływ tylko na pliki w katalogu `owner` i jego podkatalogach.
    *   Zasady z tego lokalnego pliku będą miały priorytet nad tymi z `spring-petclinic/.github/copilot-instructions.md` dla plików w `owner`.

Copilot automatycznie identyfikuje najbliższe instrukcje i stosuje je do aktualnie edytowanego pliku. Ta granularność pozwala na precyzyjne dostosowanie zachowania Copilota do różnych części projektu (np. osobne instrukcje dla warstwy UI z użyciem Thymeleaf, logiki biznesowej opartej na Spring i dostępu do danych z JPA).

#### Definiowanie reguł kodowania i zachowania Copilota
Kluczem do skutecznego używania `copilot-instructions.md` jest precyzyjne, jasne i jednoznaczne zdefiniowanie, czego oczekujemy od Copilota. Oto co możesz osiągnąć:
-   **Wymuszanie stylu formatowania:** Określ precyzyjnie styl formatowania kodu (np. wcięcia, style nawiasów klamrowych, maksymalna długość linii, użycie spacji vs tabulatorów). Nawiąż do istniejących formatów (`Google Java Format`, `Black` dla Pythona) lub do firmowych wytycznych.
-   **Preferowane biblioteki/frameworki:** Wyraźnie wskaż, które biblioteki lub frameworki są preferowane, a które zakazane. Na przykład, `Lombok` zamiast ręcznego pisania getterów/setterów, `JUnit 5` zamiast `JUnit 4`, `Log4j2` zamiast `java.util.logging`.
-   **Wzorce architektoniczne i projektowe:** Poinstruuj Copilota, aby stosował określone wzorce (np. wzorzec Repozytorium, wzorzec Fabryki, wzorzec Obserwatora) i prezentował je poprzez konkretne fragmenty kodu.
-   **Konwencje nazewnictwa:** Ustal rygorystyczne konwencje dla klas, interfejsów, metod, zmiennych, stałych, pakietów i plików (np. `PascalCase` dla klas, `camelCase` dla metod i zmiennych, prefiksy/sufiksy dla interfejsów).
-   **Unikanie anty-wzorców i błędów:** Zidentyfikuj i opisz wzorce kodu, których Copilot powinien unikać (np. field injection, użycie surowych typów, brak obsługi wyjątków, podatności bezpieczeństwa). Pokaż przykłady złego kodu i zasugeruj poprawne alternatywy.
-   **Wspieranie testowania:** Poinstruuj Copilota, aby generował testy jednostkowe w określonym stylu, z użyciem konkretnych bibliotek mockujących i asercji. Określ, gdzie powinny znajdować się pliki testowe (np. w `src/test/java`).
-   **Wytyczne dotyczące komentarzy i dokumentacji:** Zdefiniuj, kiedy i jak należy dodawać komentarze, np. wymagając Javadoc dla wszystkich publicznych API.

**Wskazówka:** Im więcej kontekstu, konkretnych reguł, a zwłaszcza *przykładów kodu* podasz w pliku instrukcji, tym trafniejsze i bardziej zgodne z projektem będą sugestie Copilota. Używaj rzeczywistych, dobrze napisanych fragmentów kodu z Twojego projektu jako "wzorców do naśladowania", a także przykładów kodu, którego należy unikać.

### 2. Pliki Promptów (.copilot/prompts/)
Podczas gdy `copilot-instructions.md` koncentruje się na ogólnych zasadach i stylu kodowania, pliki promptów w katalogu `.copilot/prompts/` pozwalają na definiowanie konkretnych, powtarzalnych "zadań" dla Copilota. Są to specjalnie sformatowane pliki tekstowe (zazwyczaj z rozszerzeniem `.prompt` lub `.md`), które służą jako spersonalizowane szablony dla złożonych zapytań do Copilot Chat lub funkcji generowania kodu. Pozwalają one na kapsułkowanie złożonej logiki generowania i ponowne jej wykorzystywanie.

#### Struktura plików promptów i ich organizacja
Katalog `.copilot/prompts/` powinien zawierać pliki z rozszerzeniem `.prompt` (lub `.md`). Każdy plik reprezentuje osobny prompt, który możesz wywołać w środowisku deweloperskim (np. w Copilot Chat w VS Code, używając `/nazwa_promptu`).

**Przykład struktury katalogów:**
```
.copilot/
└── prompts/
    ├── create_service.prompt
    ├── generate_tests.prompt
    ├── refactor_to_streams.prompt
    ├── sql/
    │   └── generate_migration.prompt
    └── documentation/
        └── create_javadoc.prompt
```

Nazwa pliku promptu (bez rozszerzenia) często staje się jego "nazwą wywoławczą" w Copilot Chat (np. `create_service`). Możesz grupować prompty w podkatalogach w ramach `prompts/` dla lepszej organizacji (np. `prompts/java/`, `prompts/sql/`, `prompts/documentation/`), co pomaga w zarządzaniu większą liczbą promptów i kategoryzowaniu ich według celu.

#### Definiowanie parametrów i użycie kontekstu z @workspace, #file
Pliki promptów mogą być dynamiczne i interaktywne, pozwalając na wstrzykiwanie zmiennych i odwoływanie się do kontekstu projektu w czasie rzeczywistym. Dzięki temu jeden prompt może być używany w wielu różnych scenariuszach.

**Parametry:** Użyj składni `{{variable_name}}` w pliku promptu, aby zdefiniować dynamiczne parametry. Gdy wywołasz taki prompt w Copilot Chat, zostaniesz poproszony o podanie wartości dla tych parametrów. Pozwala to na stworzenie generycznych promptów, które są konfigurowalne przez użytkownika.

**Kontekst:** Copilot Chat pozwala na dostarczenie dodatkowego kontekstu do Twoich promptów, co znacząco zwiększa trafność i jakość generowanych odpowiedzi:
-   `@workspace`: Włącza cały kontekst obszaru roboczego (wszystkie pliki w projekcie), co może być kosztowne obliczeniowo dla dużych projektów, ale jest bardzo przydatne dla ogólnych pytań o architekturę, zależności między modułami, czy globalne refaktoryzacje.
-   `#file`: Dodaje kontekst aktualnie otwartego pliku. Przydatne, gdy prompt ma działać na konkretnym pliku i potrzebuje jego treści do analizy lub modyfikacji.
-   `#selection`: Dodaje kontekst aktualnie zaznaczonego fragmentu kodu. Jest to idealne do refaktoryzacji małych fragmentów, generowania komentarzy do metody, czy optymalizacji pętli.
-   `@file:path/to/file.java`: Pozwala na jawne wskazanie konkretnego pliku (lub wielu plików) jako kontekstu, niezależnie od tego, który plik jest aktualnie otwarty. Umożliwia to tworzenie promptów, które pracują na zbiorze z góry określonych plików.
-   `@symbol:ClassName`: Pozwala na wskazanie konkretnego symbolu (klasy, interfejsu, metody, pola) jako kontekstu. Copilot skupi się na definicji i użyciach tego symbolu.

**Przykład pliku promptu (`create_service.prompt` z parametrami i kontekstem):**
```markdown
Tworzę usługę Spring Boot. Wygeneruj interfejs i implementację dla usługi o nazwie `{{ServiceName}}`. Upewnij się, że używa adnotacji `@Service` i wstrzykuje `{{RepositoryName}}` przez konstruktor. Zapewnij podstawową implementację metody `findById(Long id)`. Klasy powinny znajdować się w pakiecie `com.example.springpetclinic.{{service_package}}`.

@workspace #file
```

Gdy użyjesz tego promptu, Copilot Chat poprosi Cię o `ServiceName`, `RepositoryName` i `service_package`. `@workspace` i `#file` zapewnią Copilotowi kontekst całego projektu i aktualnie otwartego pliku, co pomoże w generowaniu kodu zgodnego z istniejącą strukturą, nazewnictwem i zależnościami.

#### Automatyzacja często powtarzających się zadań
Pliki promptów są idealne do automatyzacji wielu powtarzalnych, ale złożonych zadań programistycznych, co znacznie zwiększa efektywność dewelopera:
-   **Generowanie boilerplate kodu:** Szybkie tworzenie nowych klas (serwisów, kontrolerów, encji, DTO) na podstawie predefiniowanych szablonów zgodnych ze standardami projektu. Minimalizuje to ryzyko błędów i zapewnia spójność.
-   **Refaktoryzacja:** Pisanie promptów, które automatyzują złożone refaktoryzacje (np. migracja do nowej wersji API, zmiana wzorca projektowego, konwersja na Java Streams API, ekstrakcja interfejsów). Copilot może sugerować zmiany, które są zbyt duże na automatyczne uzupełnianie kodu.
-   **Generowanie testów:** Tworzenie szablonów promptów do szybkiego generowania testów jednostkowych lub integracyjnych dla istniejących klas. Możesz określić framework testowy, biblioteki mockujące, strategie testowania i konwencje nazewnictwa.
-   **Generowanie dokumentacji:** Tworzenie wstępnych fragmentów dokumentacji, komentarzy Javadoc, lub nawet notatek do `README.md` na podstawie kodu.
-   **Analiza kodu i rozwiązywanie problemów:** Pisanie promptów, które analizują zaznaczony kod pod kątem potencjalnych błędów, luk bezpieczeństwa, sugestii optymalizacyjnych, wyjaśniania złożonej logiki, czy proponowania poprawek.
-   **Generowanie zapytań SQL/schematów baz danych:** Automatyczne tworzenie skryptów DDL dla nowych encji, migracji schematów lub złożonych zapytań SQL na podstawie opisów tekstowych.

**Korzyści:** Zwiększona spójność kodu, skrócenie czasu na powtarzalne zadania (eliminacja "boilerplate code"), zmniejszenie ryzyka błędów ludzkich, szybsze wdrażanie nowych funkcjonalności.

### 3. Hooki Agentów (Agent Hooks)
Agent Hooki to zaawansowany mechanizm w GitHub Copilot, który pozwala na rozszerzanie i modyfikowanie zachowania Copilota poprzez podłączanie niestandardowej logiki do różnych etapów jego cyklu życia. Możesz myśleć o nich jak o "zdarzeniach" lub "punktach rozszerzeń", które uruchamiają niestandardowe skrypty lub funkcje w odpowiedzi na działania Copilota. Jest to potężne narzędzie do integracji Copilota z istniejącymi narzędziami, procesami CI/CD i firmowymi standardami.

#### Rodzaje hooków: pre-run, post-run, event hooki
Istnieją różne typy hooków, które uruchamiają się w zależności od fazy operacji Copilota:
-   **Pre-run hooks:** Uruchamiane *przed* wykonaniem głównej operacji Copilota (np. przed wygenerowaniem kodu, odpowiedzią na prompt, czy uruchomieniem akcji agenta).
    -   **Zastosowanie:** Walidacja danych wejściowych lub środowiska (np. czy wszystkie zależności są zainstalowane, czy plik licencji istnieje), sprawdzenie warunków wstępnych, wstrzyknięcie dodatkowego kontekstu (np. z zewnętrznej bazy danych wiedzy), modyfikacja promptu przed wysłaniem do modelu w celu zwiększenia precyzji.
-   **Post-run hooks:** Uruchamiane *po* wykonaniu głównej operacji Copilota i otrzymaniu jego odpowiedzi lub wygenerowanego kodu.
    -   **Zastosowanie:** Automatyczne formatowanie wygenerowanego kodu (np. za pomocą Prettier, Spotless), uruchamianie linera (ESLint, Checkstyle), przeprowadzanie podstawowych testów, zapisywanie logów audytowych, powiadamianie użytkownika o zakończeniu operacji, modyfikowanie odpowiedzi przed jej prezentacją (np. filtrowanie wrażliwych informacji), integracja z systemami kontroli jakości kodu.
-   **Event hooks:** Uruchamiane w odpowiedzi na specyficzne zdarzenia, które nie są bezpośrednio związane z cyklem "zapytanie-odpowiedź" Copilota, ale dotyczą jego stanu lub interakcji z IDE (np. zmiana pliku, uruchomienie Copilota, błąd w działaniu agenta, uruchomienie debuggera).
    -   **Zastosowanie:** Monitorowanie użycia Copilota, zbieranie metryk produktywności, integracja z systemami śledzenia zadań (Jira, GitHub Issues) w celu aktualizacji statusów, wyzwalanie alertów w przypadku nieoczekiwanych zachowań Copilota.

#### Automatyzacja zadań wokół cyklu życia agenta
Hooki agentów są potężnym narzędziem do automatyzacji procesów deweloperskich i integracji Copilota z istniejącymi narzędziami i przepływami pracy. Pozwalają na:
-   **Zwiększenie jakości kodu:** Automatyczne uruchamianie narzędzi do formatowania, lintingu, statycznej analizy kodu (np. SonarQube), czy nawet skanowania bezpieczeństwa po wygenerowaniu kodu, zapewniając, że kod spełnia wszystkie standardy zespołu od samego początku.
-   **Wspieranie CI/CD i DevOps:** Wyzwalanie procesów CI/CD (np. uruchamianie Jenkinsa, GitHub Actions), aktualizowanie statusu zadań w systemach zarządzania projektem, generowanie raportów o wygenerowanym kodzie.
-   **Personalizacja środowiska deweloperskiego:** Dostosowywanie środowiska IDE na podstawie akcji Copilota, np. otwieranie konkretnych paneli, wyświetlanie powiadomień, modyfikowanie ustawień edytora.
-   **Optymalizacja produktywności:** Upraszczanie złożonych przepływów pracy, redukując liczbę ręcznych kroków i interwencji dewelopera, pozwalając mu skupić się na bardziej kreatywnych aspektach programowania.
-   **Zbieranie danych:** Anonimowe zbieranie danych o sposobie używania Copilota i skuteczności instrukcji/promptów, co pozwala na dalszą optymalizację konfiguracji.

#### Implementacja prostych hooków w kontekście projektu
Implementacja hooków agentów często odbywa się poprzez pliki konfiguracyjne specyficzne dla IDE (np. `settings.json` w VS Code) lub poprzez zewnętrzne skrypty/rozszerzenia, które mogą być napisane w dowolnym języku (Bash, Python, Node.js). Kluczowe jest, aby skrypty te były wykonywalne i dostępne w środowisku deweloperskim.

**Przykład konfiguracji `settings.json` dla VS Code (częściowo hipotetyczny, bazujący na koncepcjach Copilot Agent SDK):**
```json
{
  "github.copilot.advanced": {
    "agentHooks": {
      "onCodeGenerated": {
        "command": "npm run format-code -- --file {{file_path}}",
        "description": "Formatuje wygenerowany kod przy użyciu Spotless lub Prettier."
      },
      "onPromptRun": {
        "command": "python ${workspaceFolder}/scripts/validate_license.py",
        "args": ["${workspaceFolder}"],
        "description": "Sprawdza obecność pliku licencji przed uruchomieniem promptu Copilota."
      },
      "onAgentError": {
        "command": "node ${workspaceFolder}/scripts/notify_on_error.js",
        "args": ["{{error_message}}", "{{agent_id}}"],
        "description": "Powiadamia zespół o błędzie agenta Copilota."
      }
    }
  }
}
```

W tym przykładzie:
-   `onCodeGenerated` to hook post-run, który uruchamia skrypt `format-code` (zdefiniowany w `package.json`) po wygenerowaniu kodu. Parametr `{{file_path}}` zostanie automatycznie uzupełniony ścieżką do wygenerowanego pliku.
-   `onPromptRun` to hook pre-run, który uruchamia skrypt Pythona w celu walidacji licencji. Użycie zmiennej środowiskowej `${workspaceFolder}` pozwala na odwołanie się do katalogu głównego projektu, a `args` przekazuje go jako argument do skryptu.
-   `onAgentError` to hook zdarzenia, który uruchamia skrypt Node.js w przypadku błędu agenta, przekazując wiadomość o błędzie i identyfikator agenta.

Agent hooki mogą być zaimplementowane w różnych językach skryptowych (Bash, Python, Node.js) i wywoływać dowolne narzędzia dostępne w środowisku deweloperskim (np. CLI, lintery, formatery, kompilatory, narzędzia do testowania). Ważne jest, aby skrypty te były wykonywalne, dostępne w `PATH` lub by ich ścieżki były jawnie zdefiniowane. Użycie zmiennych środowiskowych IDE (takich jak `${workspaceFolder}`) jest kluczowe dla przenośności konfiguracji.

## 💡 Przykłady Użycia

### Przykład 1: Wymuszenie stylu kodowania z `.github/copilot-instructions.md`
Chcemy, aby Copilot zawsze generował gettery i settery w `spring-petclinic` z użyciem `Lombok` i aby preferował wstrzykiwanie zależności przez konstruktor, a także aby stosował adnotację `@Transactional` dla metod modyfikujących dane.

Utwórz plik `output/copilot_training/tier_1_critical/module_03/.github/copilot-instructions.md`:

```markdown
# Wytyczne dla GitHub Copilot w projekcie spring-petclinic

## 🛠️ Java Best Practices

### Lombok
Zawsze używaj adnotacji Lombok do generowania boilerplate code, takich jak gettery, settery, konstruktory, metody `equals()`/`hashCode()` i `toString()`. Nigdy nie generuj tych metod ręcznie.

**Przykład użycia Lomboka:**
```java
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ExampleEntity {
    private Long id;
    private String name;
}
```

### Wstrzykiwanie Zależności (Spring)
Preferuj wstrzykiwanie zależności przez konstruktor. Unikaj wstrzykiwania pól (`@Autowired` nad polem) i metod set-get, ponieważ utrudniają testowanie i naruszają zasadę niezmienności.

**Przykład prawidłowego wstrzykiwania zależności:**
```java
import org.springframework.stereotype.Service;

@Service
public class ExampleService {

    private final ExampleRepository exampleRepository;

    public ExampleService(ExampleRepository exampleRepository) {
        this.exampleRepository = exampleRepository;
    }

    // ... metody serwisu
}
```

### Transakcyjność
Metody w serwisach, które modyfikują stan bazy danych, zawsze powinny być oznaczone adnotacją `@Transactional` z `org.springframework.transaction.annotation.Transactional`.

**Przykład:**
```java
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ExampleService {

    // ... konstruktor ...

    @Transactional
    public void saveData(Data data) {
        // ... logika zapisu danych ...
    }
}
```
```

Teraz, gdy będziesz edytować lub tworzyć nowe klasy w projekcie `spring-petclinic` i poprosisz Copilota o wygenerowanie getterów/setterów, nowej usługi lub metody modyfikującej dane, powinien on stosować się do tych wytycznych, sugerując odpowiednie adnotacje i wzorce.

### Przykład 2: Automatyczne generowanie usług Spring Boot za pomocą promptu
Chcemy szybko generować szkielety nowych usług Spring Boot wraz z odpowiadającymi im interfejsami i prostymi interfejsami repozytoriów Spring Data JPA.

Utwórz plik `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/create_service.prompt` (zawartość już została utworzona w poprzednim kroku):

```markdown
Jako doświadczony deweloper Spring Boot, wygeneruj kompletny kod dla nowej usługi Java wraz z odpowiadającym jej interfejsem i prostym interfejsem repozytorium Spring Data JPA.

Nazwa usługi: `{{ServiceName}}`
Nazwa encji: `{{EntityName}}`
Pakiet bazowy: `com.example.springpetclinic.{{base_package}}`

Interfejs usługi powinien znajdować się w pakiecie `{{base_package}}.service` i zawierać metody `findById({{EntityName}} id)` i `save({{EntityName}} entity)`.
Implementacja usługi powinna być adnotowana `@Service`, wstrzykiwać `{{EntityName}}Repository` przez konstruktor i implementować metody z interfejsu.
Interfejs repozytorium powinien znajdować się w pakiecie `{{base_package}}.repository` i rozszerzać `JpaRepository<{{EntityName}}, Long>`.

@workspace #file
```

Po zapisaniu tego pliku, możesz otworzyć Copilot Chat (zazwyczaj skrót `Ctrl+Shift+I` lub `Cmd+Shift+I`) i wpisać np. `/create_service`. Copilot poprosi Cię o podanie `ServiceName`, `EntityName` i `base_package`, a następnie wygeneruje odpowiednie klasy w aktualnym kontekście, uwzględniając kontekst `@workspace` i `#file`, aby dopasować się do istniejącej struktury projektu `spring-petclinic`.

### Przykład 3: Walidacja istnienia pliku licencji przed uruchomieniem promptu (Pre-run Hook)
Zapewnij, że żaden prompt Copilota nie zostanie uruchomiony, jeśli w katalogu głównym projektu `spring-petclinic` nie istnieje plik `LICENSE`. Jest to krytyczny wymóg w wielu projektach open-source i komercyjnych.

**1. Stwórz skrypt walidacyjny (`output/copilot_training/tier_1_critical/module_03/scripts/validate_license.py`):**
Najpierw utwórz katalog `scripts`:
```python
import os
import sys

def validate_license(project_root):
    license_path = os.path.join(project_root, "LICENSE")
    if not os.path.exists(license_path):
        print(f"BŁĄD: Plik LICENCJI nie został znaleziony w katalogu głównym projektu: {project_root}", file=sys.stderr)
        print("Operacja Copilota została zablokowana. Utwórz plik LICENSE, aby kontynuować.", file=sys.stderr)
        sys.exit(1) # Zakończ z kodem błędu, aby zasygnalizować niepowodzenie hooka
    print(f"INFO: Plik LICENCJI znaleziony pod adresem: {license_path}")
    sys.exit(0) # Zakończ z kodem sukcesu

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python validate_license.py <project_root>", file=sys.stderr)
        sys.exit(1)
    project_root = sys.argv[1]
    validate_license(project_root)
```

**2. Skonfiguruj `settings.json` dla VS Code:**
Zmodyfikuj plik `output/copilot_training/tier_1_critical/module_03/config/settings.json`, aby aktywować ten pre-run hook:
```json
{
  "github.copilot.advanced": {
    "agentHooks": {
      "onPromptRun": {
        "command": "python",
        "args": [
          "${workspaceFolder}/scripts/validate_license.py",
          "${workspaceFolder}"
        ],
        "description": "Sprawdza obecność pliku licencji przed uruchomieniem dowolnego promptu Copilota."
      }
    }
  }
}
```

**Testowanie:**
1.  Upewnij się, że plik `LICENSE` *nie* istnieje w głównym katalogu Twojego projektu `spring-petclinic`.
2.  Spróbuj uruchomić dowolny prompt Copilota Chat (np. `/help`). Powinieneś zobaczyć komunikat o błędzie z Twojego skryptu i operacja Copilota zostanie zablokowana.
3.  Utwórz pusty plik `LICENSE` w głównym katalogu `spring-petclinic`.
4.  Spróbuj ponownie uruchomić prompt. Tym razem powinien on działać bez problemów.

## ✅ Best Practices
-   **Zwięzłość i Precyzja Instrukcji:** Twoje `copilot-instructions.md` powinny być jasne, zwięzłe i jednoznaczne. Unikaj dwuznaczności, która może prowadzić do niechcianych sugestii. Każda zasada powinna być łatwa do zrozumienia i zastosowania. Długie, złożone instrukcje mogą być mniej efektywne.
-   **Wersjonowanie Konfiguracji:** Traktuj wszystkie pliki konfiguracyjne Copilota (`copilot-instructions.md`, `.copilot/prompts/`, `settings.json`, `package.json` dla hooków) jak kod źródłowy. Wersjonuj je w swoim repozytorium Git, aby zapewnić spójność, możliwość śledzenia zmian i współpracę w zespole. Umożliwia to również łatwe odtworzenie środowiska.
-   **Iteracyjne Testowanie i Dostosowywanie:** Zmiany w instrukcjach i promptach Copilota wymagają testów. Generuj kod i proś o sugestie w różnych scenariuszach, aby upewnić się, że Copilot zachowuje się zgodnie z oczekiwaniami. Proces ten powinien być iteracyjny, ciągle udoskonalając konfigurację.
-   **Modularyzacja Promptów:** Dla złożonych zadań rozważ dzielenie dużych promptów na mniejsze, bardziej specyficzne i reużywalne fragmenty. Chociaż Copilot może nie obsługiwać wprost kompozycji promptów z różnych plików, utrzymanie promptów w małych, celowych jednostkach ułatwia zarządzanie i testowanie.
-   **Uważne Zarządzanie Kontekstem:** Używaj `@workspace` z rozwagą, szczególnie w bardzo dużych projektach, ponieważ może to prowadzić do wolniejszych odpowiedzi i mniej trafnych sugestii z powodu przeładowania kontekstem. Preferuj bardziej szczegółowe konteksty, takie jak `#file`, `#selection`, `@file:path` lub `@symbol:name`, aby dostarczyć Copilotowi najbardziej relewantnych informacji.
-   **Bezpieczeństwo przy Hookach:** Bądź niezwykle ostrożny przy implementowaniu hooków, które wykonują zewnętrzne skrypty. Upewnij się, że skrypty są bezpieczne, przetestowane i pochodzą z zaufanych źródeł, ponieważ mają one uprawnienia do uruchamiania poleceń w Twoim systemie. Unikaj przekazywania wrażliwych danych do skryptów.
-   **Dokumentacja Wewnętrzna:** Oprócz `copilot-instructions.md`, twórz wewnętrzną dokumentację dla zespołu, wyjaśniającą, jak efektywnie korzystać z niestandardowych promptów i jak działają agent hooki. Pomoże to w adopcji i maksymalizacji korzyści.

## ⚠️ Common Pitfalls
-   **Niejasne lub Sprzeczne Instrukcje:** Jeśli Twoje `copilot-instructions.md` zawierają niejasne, ogólnikowe lub sprzeczne zasady, Copilot może generować nieprzewidywalne lub niechciane sugestie. Zawsze dąż do precyzji i spójności.
-   **Przeładowany Kontekst w Promptach:** Używanie `@workspace` bez potrzeby, szczególnie w dużych repozytoriach, może prowadzić do wolniejszych odpowiedzi i obniżonej jakości sugestii, ponieważ Copilot ma zbyt wiele informacji do przetworzenia. Może to również generować wyższe koszty zasobów.
-   **Ignorowanie Hierarchii Dziedziczenia Instrukcji:** Niezrozumienie, jak instrukcje z lokalnych `.github/copilot-instructions.md` nadpisują te globalne, może prowadzić do nieoczekiwanych zachowań Copilota. Zawsze sprawdzaj, która instrukcja ma najwyższy priorytet dla danego pliku.
-   **Brak Wersjonowania Plików Konfiguracyjnych:** Nieumieszczenie konfiguracji Copilota w systemie kontroli wersji prowadzi do utraty historii zmian, trudności w reprodukcji środowisk, problemów ze współpracą w zespole i ogólnego braku zarządzania konfiguracją.
-   **Zależności Zewnętrzne w Hookach:** Skrypty wykonywane przez agent hooki mogą mieć zależności zewnętrzne (np. Python, Node.js, konkretne biblioteki). Jeśli te zależności nie są prawidłowo zarządzane lub nie są dostępne w środowisku dewelopera, hooki mogą zawieść, przerywając przepływ pracy.
-   **Nadmierna Konfiguracja:** Stworzenie zbyt wielu instrukcji lub promptów, które są redundantne lub zbyt granularne, może skomplikować zarządzanie i zmniejszyć rzeczywistą wartość Copilota. Dąż do równowagi między kontrolą a elastycznością.
-   **Brak Testów dla Konfiguracji:** Tak jak kod, konfiguracja Copilota powinna być testowana. Brak weryfikacji, czy instrukcje i prompty działają zgodnie z oczekiwaniami, może prowadzić do generowania błędnego kodu lub nieefektywnego użycia narzędzia.

## 🔗 Dodatkowe Zasoby
-   [Oficjalna Dokumentacja GitHub Copilot](https://docs.github.com/en/copilot)
-   [Zrozumienie Plików Prompts dla GitHub Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat/using-prompts-in-github-copilot-chat)
-   [Blog GitHub Engineering - Deep Dive into Copilot Customization](https://github.blog/)
-   [Dokumentacja Spring PetClinic](https://spring-petclinic.github.io/)

Ten moduł dostarcza kompleksowego przeglądu i praktycznych przykładów, jak skutecznie dostosować GitHub Copilot do specyficznych potrzeb Twojego projektu, zwiększając produktywność i jakość kodu w `spring-petclinic` i poza nim.