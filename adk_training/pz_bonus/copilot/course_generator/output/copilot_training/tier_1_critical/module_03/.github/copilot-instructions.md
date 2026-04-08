 규모: 2500-3500 słów
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

Plik `.github/copilot-instructions.md` (lub alternatywnie `.vscode/copilot-instructions.md` w kontekście VS Code) to kluczowe narzędzie do dostosowywania zachowania Copilota do specyficznych wymagań projektu. Jest to plik Markdown, który zawiera instrukcje, wytyczne, przykłady kodu, a nawet fragmenty dokumentacji, które Copilot powinien brać pod uwagę podczas generowania sugestii.

#### Składnia Markdown dla instrukcji
Copilot interpretuje treści w pliku `copilot-instructions.md` podobnie jak każdy inny plik Markdown. Oznacza to, że możesz używać standardowej składni do strukturyzowania swoich instrukcji:
- Nagłówki (`#`, `##`, `###`) do organizacji sekcji.
- Listy (numerowane i nienumerowane) do wyliczania zasad.
- Bloki kodu (` ````java ` ````) do prezentowania przykładów kodu, wzorców do naśladowania lub kodu do unikania.
- Cytaty (`>`) do wyróżniania ważnych uwag.
- Linki do zewnętrznej dokumentacji lub wewnętrznych wiki.

**Przykład struktury:**
```markdown
# Wytyczne dla GitHub Copilot w projekcie spring-petclinic

## 💡 Ogólne Zasady Kodowania
- Zawsze używaj formatowania zgodnego z Google Java Format.
- Preferuj lambdy zamiast anonimowych klas wewnętrznych.
- Unikaj magicznych liczb; zamiast tego używaj nazwanych stałych.

## 🛠️ Wytyczne dla Spring Framework
- Wstrzykiwanie zależności zawsze przez konstruktor.
- Używaj adnotacji `@Service`, `@Repository`, `@Controller` we właściwych miejscach.

## 🧪 Testy Jednostkowe
- Stosuj JUnit 5 i Mockito.
- Nazwy metod testowych powinny być w formacie `nazwaMetody_scenariusz_oczekiwanyWynik()`.
```

#### Zakres i dziedziczenie instrukcji
Instrukcje dla Copilota są hierarchiczne i kontekstowe:
1.  **Globalne instrukcje:** Domyślne zachowania Copilota.
2.  **Instrukcje użytkownika:** Konfiguracja Copilota w Twoim środowisku deweloperskim (np. `settings.json` w VS Code).
3.  **Instrukcje repozytorium:** Plik `.github/copilot-instructions.md` w głównym katalogu repozytorium. Te instrukcje mają zastosowanie do całego projektu.
4.  **Instrukcje katalogu:** Możesz umieścić `copilot-instructions.md` w podkatalogach. Instrukcje z podkatalogów dziedziczą i mogą nadpisywać instrukcje z katalogów nadrzędnych. Na przykład, plik w `src/main/java/com/example/.github/copilot-instructions.md` będzie miał wpływ tylko na pliki w tym katalogu i jego podkatalogach, a jego zasady będą miały priorytet nad zasadami z głównego `.github/copilot-instructions.md`.

Copilot automatycznie identyfikuje najbliższe instrukcje i stosuje je do aktualnie edytowanego pliku. Dzięki temu możesz precyzyjnie dostosować zachowanie Copilota do różnych części projektu (np. osobne instrukcje dla warstwy UI, logiki biznesowej i dostępu do danych).

#### Definiowanie reguł kodowania i zachowania Copilota
Kluczem do skutecznego używania `copilot-instructions.md` jest precyzyjne i jasne zdefiniowanie, czego oczekujemy od Copilota. Oto co możesz osiągnąć:
-   **Wymuszanie stylu:** Określ styl formatowania (np. wcięcia, nawiasy klamrowe, nazewnictwo zmiennych).
-   **Preferowane biblioteki/frameworki:** Zleć Copilotowi preferowanie konkretnych bibliotek (np. `Lombok` zamiast ręcznego pisania getterów/setterów, `JUnit 5` zamiast `JUnit 4`).
-   **Wzorce architektoniczne:** Poinstruuj Copilota, aby stosował określone wzorce (np. wzorzec Repozytorium, wzorzec Fabryki).
-   **Konwencje nazewnictwa:** Ustal konwencje dla klas, metod, zmiennych, stałych.
-   **Unikanie anty-wzorców:** Zidentyfikuj i opisz wzorce kodu, których Copilot powinien unikać.
-   **Wspieranie testowania:** Poinstruuj Copilota, aby generował testy jednostkowe w określonym stylu, z użyciem konkretnych bibliotek mockujących.

**Wskazówka:** Im więcej kontekstu i przykładów podasz w pliku instrukcji, tym trafniejsze będą sugestie Copilota. Używaj rzeczywistych fragmentów kodu z Twojego projektu jako "wzorców do naśladowania".

### 2. Pliki Promptów (.copilot/prompts/)
Podczas gdy `copilot-instructions.md` koncentruje się na ogólnych zasadach i stylu, pliki promptów w katalogu `.copilot/prompts/` pozwalają na definiowanie konkretnych, powtarzalnych "zadań" dla Copilota. Są to specjalnie sformatowane pliki tekstowe (zazwyczaj z rozszerzeniem `.prompt` lub `.md`), które służą jako szablony dla złożonych zapytań do Copilota Chat lub funkcji generowania kodu.

#### Struktura plików promptów i ich organizacja
Katalog `.copilot/prompts/` powinien zawierać pliki z rozszerzeniem `.prompt` (lub `.md` w niektórych przypadkach). Każdy plik reprezentuje osobny prompt, który możesz wywołać w środowisku deweloperskim (np. w Copilot Chat w VS Code).

**Przykład struktury:**
```
.copilot/
└── prompts/
    ├── create_service.prompt
    ├── generate_tests.prompt
    ├── refactor_to_streams.prompt
    └── explain_code_block.prompt
```

Nazwa pliku promptu często staje się jego "nazwą wywoławczą". Możesz grupować prompty w podkatalogach w ramach `prompts/` dla lepszej organizacji (np. `prompts/java/`, `prompts/sql/`).

#### Definiowanie parametrów i użycie kontekstu z @workspace, #file
Pliki promptów mogą być dynamiczne i interaktywne. Możesz definiować w nich zmienne (parametry) i odwoływać się do kontekstu projektu.

**Parametry:** Użyj składni `{{variable_name}}` w pliku promptu, aby zdefiniować parametry. Gdy wywołasz taki prompt, Copilot Chat poprosi Cię o podanie wartości dla tych parametrów.

**Kontekst:** Copilot Chat pozwala na dostarczenie dodatkowego kontekstu do Twoich promptów:
-   `@workspace`: Włącza cały kontekst obszaru roboczego (wszystkie pliki w projekcie), co może być kosztowne obliczeniowo, ale bardzo przydatne dla ogólnych pytań o architekturę.
-   `#file`: Dodaje kontekst aktualnie otwartego pliku. Przydatne, gdy prompt ma działać na konkretnym pliku.
-   `#selection`: Dodaje kontekst aktualnie zaznaczonego fragmentu kodu.
-   `@file:path/to/file.java`: Pozwala na jawne wskazanie konkretnego pliku jako kontekstu.
-   `@symbol:ClassName`: Pozwala na wskazanie konkretnego symbolu (klasy, metody) jako kontekstu.

**Przykład pliku promptu (`create_service.prompt`):**
```markdown
Tworzę usługę Spring Boot. Wygeneruj interfejs i implementację dla usługi o nazwie `{{ServiceName}}`. Upewnij się, że używa adnotacji `@Service` i wstrzykuje `{{RepositoryName}}` przez konstruktor. Zapewnij podstawową implementację metody `findById(Long id)`. Klasy powinny znajdować się w pakiecie `com.example.springpetclinic.{{service_package}}`.

@workspace #file
```

Gdy użyjesz tego promptu, Copilot Chat poprosi Cię o `ServiceName`, `RepositoryName` i `service_package`. `@workspace` i `#file` zapewnią Copilotowi kontekst całego projektu i aktualnie otwartego pliku, co pomoże w generowaniu kodu zgodnego z istniejącą strukturą.

#### Automatyzacja często powtarzających się zadań
Pliki promptów są idealne do automatyzacji:
-   **Generowanie boilerplate:** Szybkie tworzenie nowych klas (serwisów, kontrolerów, encji) na podstawie predefiniowanych szablonów.
-   **Refaktoryzacja:** Pisanie promptów, które automatyzują złożone refaktoryzacje (np. migracja do nowej wersji API, zmiana wzorca projektowego).
-   **Generowanie testów:** Tworzenie szablonów promptów do szybkiego generowania testów jednostkowych lub integracyjnych dla istniejących klas.
-   **Dokumentacja:** Generowanie wstępnych fragmentów dokumentacji lub komentarzy Javadoc.
-   **Analiza kodu:** Pisanie promptów, które analizują zaznaczony kod pod kątem potencjalnych błędów, luk bezpieczeństwa lub sugestii optymalizacyjnych.

**Korzyści:** Zwiększona spójność kodu, skrócenie czasu na powtarzalne zadania, zmniejszenie ryzyka błędów ludzkich.

### 3. Hooki Agentów (Agent Hooks)
Agent Hooki to zaawansowany mechanizm w GitHub Copilot, który pozwala na rozszerzanie i modyfikowanie zachowania Copilota poprzez podłączanie niestandardowej logiki do różnych etapów jego cyklu życia. Możesz myśleć o nich jak o "zdarzeniach", które uruchamiają niestandardowe skrypty lub funkcje w odpowiedzi na działania Copilota.

#### Rodzaje hooków: pre-run, post-run, event hooki
Istnieją różne typy hooków, które uruchamiają się w zależności od fazy operacji Copilota:
-   **Pre-run hooks:** Uruchamiane *przed* wykonaniem głównej operacji Copilota (np. przed wygenerowaniem kodu lub odpowiedzią na prompt).
    -   **Zastosowanie:** Walidacja danych wejściowych, sprawdzenie warunków wstępnych, wstrzyknięcie dodatkowego kontekstu, modyfikacja promptu przed wysłaniem do modelu.
-   **Post-run hooks:** Uruchamiane *po* wykonaniu głównej operacji Copilota i otrzymaniu jego odpowiedzi.
    -   **Zastosowanie:** Formatowanie wygenerowanego kodu, uruchamianie linera, zapisywanie logów, powiadamianie użytkownika, modyfikowanie odpowiedzi przed jej prezentacją.
-   **Event hooks:** Uruchamiane w odpowiedzi na specyficzne zdarzenia, które nie są bezpośrednio związane z cyklem "zapytanie-odpowiedź" Copilota, ale dotyczą jego stanu lub interakcji z IDE (np. zmiana pliku, uruchomienie Copilota).
    -   **Zastosowanie:** Monitorowanie, zbieranie metryk, integracja z systemami CI/CD.

#### Automatyzacja zadań wokół cyklu życia agenta
Hooki agentów są potężnym narzędziem do automatyzacji procesów deweloperskich i integracji Copilota z istniejącymi narzędziami i przepływami pracy. Pozwalają na:
-   **Zwiększenie jakości kodu:** Automatyczne formatowanie, linting, sprawdzanie bezpieczeństwa po wygenerowaniu kodu.
-   **Wspieranie CI/CD:** Wyzwalanie procesów CI/CD, aktualizowanie statusu zadań w systemach zarządzania projektem.
-   **Personalizacja środowiska:** Dostosowywanie środowiska IDE na podstawie akcji Copilota.
-   **Optymalizacja produktywności:** Upraszczanie złożonych przepływów pracy, redukując liczbę ręcznych kroków.

#### Implementacja prostych hooków w kontekście projektu
Implementacja hooków agentów często odbywa się poprzez pliki konfiguracyjne specyficzne dla IDE (np. `settings.json` w VS Code) lub poprzez zewnętrzne skrypty/rozszerzenia. Typowo, definiujesz, który hook ma być uruchomiony (np. `onCodeGenerated`) i jaki skrypt lub komenda ma zostać wykonana.

**Przykład konfiguracji `settings.json` dla VS Code (częściowo hipotetyczny, bazujący na koncepcjach):**
```json
{
  "github.copilot.advanced": {
    "agentHooks": {
      "onCodeGenerated": {
        "command": "npm run format-code -- --file {{file_path}}",
        "description": "Formatuje wygenerowany kod przy użyciu Spotless."
      },
      "onPromptRun": {
        "command": "python ./scripts/validate_license.py {{project_root}}",
        "description": "Sprawdza obecność pliku licencji przed uruchomieniem promptu."
      }
    }
  }
}
```

W tym przykładzie:
-   `onCodeGenerated` to hook post-run, który uruchamia skrypt `format-code` po wygenerowaniu kodu.
-   `onPromptRun` to hook pre-run, który uruchamia skrypt Pythona w celu walidacji licencji.

Agent hooki mogą być zaimplementowane w różnych językach skryptowych (Bash, Python, Node.js) i wywoływać dowolne narzędzia dostępne w środowisku deweloperskim. Ważne jest, aby skrypty te były dostępne w `PATH` lub by ich ścieżki były jawnie zdefiniowane.

## 💡 Przykłady Użycia

### Przykład 1: Wymuszenie stylu kodowania z `copilot-instructions.md`
Chcemy, aby Copilot zawsze generował gettery i settery w `spring-petclinic` z użyciem `Lombok` i aby preferował wstrzykiwanie zależności przez konstruktor.

Utwórz plik `output/copilot_training/tier_1_critical/module_03/.github/copilot-instructions.md`:

```markdown
# Wytyczne dla GitHub Copilot w projekcie spring-petclinic

## 🛠️ Java Best Practices

### Lombok
Zawsze używaj adnotacji Lombok do generowania boilerplate code, takich jak gettery, settery, konstruktory, metody `equals()`, `hashCode()` i `toString()`.

**Przykład:**
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
Preferuj wstrzykiwanie zależności przez konstruktor. Unikaj wstrzykiwania pól (`@Autowired` nad polem) i metod set-get.

**Przykład:**
```java
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class ExampleService {

    private final ExampleRepository exampleRepository;

    @Autowired // Adnotacja opcjonalna od Spring 4.3 jeśli jest tylko jeden konstruktor
    public ExampleService(ExampleRepository exampleRepository) {
        this.exampleRepository = exampleRepository;
    }

    // ... metody serwisu
}
```
```

Teraz, gdy będziesz edytować lub tworzyć nowe klasy w projekcie `spring-petclinic` i poprosisz Copilota o wygenerowanie getterów/setterów lub nowej usługi, powinien on stosować się do tych wytycznych.

### Przykład 2: Automatyczne generowanie usług Spring Boot za pomocą promptu
Chcemy szybko generować szkielety nowych usług Spring Boot z repozytoriami.

Utwórz plik `output/copilot_training/tier_1_critical/module_03/.copilot/prompts/create_service_with_repo.prompt`:

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

Po zapisaniu tego pliku, możesz otworzyć Copilot Chat i wpisać np. `/create_service_with_repo`. Copilot poprosi Cię o podanie `ServiceName`, `EntityName` i `base_package`, a następnie wygeneruje odpowiednie klasy w aktualnym kontekście.

### Przykład 3: Walidacja licencji przed uruchomieniem promptu za pomocą pre-run hooka
Zapewnij, że żaden prompt Copilota nie zostanie uruchomiony, jeśli w katalogu głównym projektu nie istnieje plik `LICENSE`.

**1. Stwórz skrypt walidacyjny (np. `scripts/validate_license.py`):**
```python
import os
import sys

def validate_license(project_root):
    license_path = os.path.join(project_root, 