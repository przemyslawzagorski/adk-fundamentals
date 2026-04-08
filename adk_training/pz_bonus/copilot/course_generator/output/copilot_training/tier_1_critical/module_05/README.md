# Inżynieria Kontekstu i Skuteczne Prompty z GitHub Copilot

## 🎯 Cele Szkolenia
- Zrozumienie kluczowej roli kontekstu w generowaniu precyzyjnych i trafnych sugestii przez GitHub Copilot.
- Opanowanie metod zarządzania kontekstem w GitHub Copilot, w tym efektywne użycie `@workspace` i `#file`.
- Identyfikacja i optymalizacja problemów związanych z "token window" w dużych bazach kodu.
- Opracowanie umiejętności tworzenia precyzyjnych, jednoznacznych i iteracyjnie udoskonalanych promptów.
- Poznanie zaawansowanych technik promptowania dla maksymalizacji produktywności i jakości kodu generowanego przez Copilot.
- Wykorzystanie GitHub Copilot do generowania dokumentacji, refaktoringu, testów i implementacji wzorców projektowych w oparciu o kontekst projektu.

## 📚 Teoria

### Znaczenie Kontekstu dla Jakości Odpowiedzi
GitHub Copilot, podobnie jak inne duże modele językowe (LLMs), opiera swoje sugestie na analizie dostępnego kontekstu. Kontekst to nic innego jak fragmenty kodu, otwarte pliki, komentarze, nazwy zmiennych, a nawet historia edycji, które Copilot 'widzi' i na ich podstawie próbuje przewidzieć, co deweloper chce napisać. Im bardziej trafny i precyzyjny kontekst, tym lepsze i bardziej użyteczne są generowane sugestie.

Zrozumienie, jak Copilot interpretuje i wykorzystuje kontekst, jest fundamentalne dla efektywnego korzystania z tego narzędzia. Niewystarczający lub zbyt szeroki kontekst może prowadzić do nieprawidłowych, ogólnikowych lub niepasujących do projektu sugestii, co zamiast przyspieszać pracę, może ją spowalniać przez konieczność ręcznych poprawek. Pamiętaj, że Copilot nie 'rozumie' kodu w ludzki sposób; on identyfikuje wzorce i relacje statystyczne w ogromnych zbiorach danych, na których był trenowany, a następnie aplikuje je do Twojego kontekstu.

Kluczem jest to, że Copilot nie jest inteligentny w ludzkim sensie. Jest to zaawansowany system dopasowywania wzorców. Kiedy dostarczasz mu kontekst, tak naprawdę dajesz mu próbki kodu i danych, na podstawie których ma wygenerować kontynuację lub modyfikację. Jeśli kontekst jest niejasny, sprzeczny lub zbyt obszerny, wzorce stają się rozmyte, a wyniki mniej trafne. Z drugiej strony, precyzyjny kontekst pozwala Copilotowi na wybór najbardziej relewantnych wzorców z jego bazy wiedzy, co prowadzi do generowania kodu, który jest nie tylko poprawny składniowo, ale także sensowny logicznie w kontekście Twojego projektu.

### Metody Selekcji Kontekstu: `@workspace` i `#file`
GitHub Copilot oferuje specjalne mechanizmy do zarządzania zakresem kontekstu, które są kluczowe dla precyzyjnego generowania kodu. Są to `@workspace` i `#file`.

#### `@workspace`

`@workspace` to modyfikator, który informuje Copilota, aby uwzględnił cały otwarty obszar roboczy (projekt) jako kontekst dla generowanych sugestii. Jest to szczególnie przydatne, gdy potrzebujesz, aby Copilot 'widział' zależności między wieloma plikami, klasami czy modułami w Twoim projekcie. Pozwala to na generowanie kodu, który jest spójny z globalną architekturą i stylem projektu, ponieważ Copilot ma wgląd w szerszy obraz.

**Kiedy używać `@workspace`:**
-   **Generowanie kodu, który integruje się z wieloma komponentami:** Na przykład, gdy tworzysz nową funkcjonalność, która wymaga interakcji z istniejącymi serwisami, repozytoriami i kontrolerami. Copilot może wtedy zaproponować implementacje, które są zgodne z architekturą całego projektu. Jest to szczególnie przydatne przy tworzeniu nowych endpointów API, które muszą korzystać z wielu warstw aplikacji.
-   **Refaktoryzacja obejmująca wiele plików:** Jeśli planujesz zmienić interfejs API lub strukturę danych, co wpłynie na wiele miejsc w kodzie (np. zmianę nazwy metody używanej w dziesiątkach plików), `@workspace` pomoże Copilotowi zrozumieć te globalne zmiany i zaproponować spójne aktualizacje we wszystkich powiązanych plikach. To minimalizuje ryzyko wprowadzenia błędów integracyjnych.
-   **Generowanie dokumentacji projektowej:** Poproszenie Copilota o wygenerowanie ogólnej dokumentacji dla całej warstwy aplikacji (np. warstwy serwisowej) będzie wymagało dostępu do wszystkich plików w tej warstwie, aby zrozumieć zależności i przepływy danych. Copilot może wtedy stworzyć wysokopoziomowe opisy, jak i szczegółowe wyjaśnienia interakcji.
-   **Analiza zależności:** Gdy potrzebujesz zrozumieć, jak klasy są ze sobą powiązane, `@workspace` może pomóc Copilotowi w zasugerowaniu diagramów zależności (w formie tekstowej lub pseudokodu) lub szczegółowych opisów architektury systemu, wyciągając informacje z różnych źródeł w projekcie.
-   **Przeprowadzanie zmian konfiguracyjnych:** Na przykład, aktualizacja schematu bazy danych lub zmiana globalnych parametrów w plikach konfiguracyjnych (np. `application.properties`, `pom.xml`), gdzie Copilot może zasugerować powiązane zmiany w kodzie.

**Ograniczenia `@workspace`:**
-   **Problem "token window":** W dużych projektach, cały obszar roboczy może być zbyt obszerny, aby zmieścić się w oknie kontekstowym LLM-a. Może to prowadzić do ignorowania części kodu, co skutkuje niekompletnymi lub ogólnikowymi sugestiami. Copilot będzie musiał heurystycznie wybrać najważniejsze fragmenty, co nie zawsze jest optymalne dla Twojego zadania.
-   **Mniejsza precyzja:** Gdy kontekst jest zbyt szeroki, Copilot może mieć trudności z określeniem, które części kodu są najbardziej istotne dla danego zapytania, co może skutkować mniej precyzyjnymi lub nawet irrelewantnymi sugestiami. Może to prowadzić do generowania kodu, który jest poprawny, ale niekoniecznie optymalny dla specyficznej sytuacji.
-   **Wyższe zużycie zasobów:** Przetwarzanie większego kontekstu wymaga więcej mocy obliczeniowej i czasu, co może spowolnić generowanie sugestii.

#### `#file`

`#file` to modyfikator, który ogranicza kontekst do konkretnego, wskazanego pliku. Jest to niezwykle przydatne, gdy chcesz, aby Copilot skupił się wyłącznie na treści jednego pliku i generował sugestie, które są w pełni zgodne z jego wewnętrzną logiką i strukturą, ignorując potencjalnie rozpraszający kod z innych części projektu. To podejście maksymalizuje precyzję w ramach pojedynczego pliku.

**Kiedy używać `#file`:**
-   **Precyzyjny refaktoring w obrębie pliku:** Jeśli refaktoryzujesz pojedynczą metodę, klasę lub fragment kodu i nie chcesz, aby Copilot był "rozpraszany" przez zależności zewnętrzne, `#file` zapewni, że sugestie będą dotyczyły tylko tego pliku. To idealne rozwiązanie do optymalizacji algorytmów, poprawy czytelności lub wprowadzenia lokalnych zmian w implementacji.
-   **Generowanie testów jednostkowych:** W przypadku testów jednostkowych, zazwyczaj skupiamy się na testowaniu pojedynczej klasy lub metody. Użycie `#file` pozwala Copilotowi na wygenerowanie testów, które są ściśle związane z wewnętrzną implementacją testowanego komponentu, bez wprowadzania zewnętrznych zależności, które mogłyby skomplikować test.
-   **Dodawanie adnotacji lub komentarzy do istniejącego kodu:** Gdy potrzebujesz dodać dokumentację Javadoc, komentarze wyjaśniające złożoną logikę w metodzie, `#file` zapewni, że Copilot skupi się na semantyce tego konkretnego pliku i stworzy dokumentację spójną z jego treścią.
-   **Tworzenie nowych funkcji w istniejącej klasie:** Jeśli dodajesz nową metodę do klasy i chcesz, aby była ona zgodna z konwencjami i logiką już istniejących metod w tym pliku, `#file` jest idealnym narzędziem. Copilot może naśladować styl i strukturę istniejącego kodu.
-   **Debugowanie i analiza pojedynczego pliku:** Gdy napotkasz problem w konkretnym pliku i potrzebujesz pomocy Copilota w jego analizie lub sugerowaniu poprawek, ograniczenie kontekstu do tego pliku pozwala na głębsze skupienie się na jego zawartości.

**Ograniczenia `#file`:**
-   **Brak zrozumienia zależności zewnętrznych:** Jeśli Twoje zadanie wymaga interakcji z innymi plikami (np. wywołania metod z innych serwisów, które nie są widoczne w kontekście `#file`), `#file` może doprowadzić do wygenerowania kodu, który nie kompiluje się, nie integruje się poprawnie z resztą systemu lub ignoruje ważne aspekty architektury.
-   **Konieczność manualnej integracji:** Po wygenerowaniu kodu z `#file`, może być konieczne ręczne dostosowanie go do reszty projektu, zwłaszcza jeśli wygenerowane sugestie mają wpływ na inne części systemu.
-   **Ryzyko redundancji:** Jeśli Copilot nie widzi globalnego kontekstu, może zasugerować implementacje, które duplikują już istniejącą logikę w innych plikach.

### Problem 'Token Window' i Jego Optymalizacja

Każdy model językowy, w tym ten używany przez GitHub Copilot, operuje w ramach ograniczonego "okna kontekstowego" (ang. token window). Oznacza to, że model może przetworzyć tylko określoną liczbę tokenów (słów, fragmentów kodu, znaków interpunkcyjnych) naraz. Jeśli podany kontekst (np. cały projekt z `@workspace`) przekroczy ten limit, Copilot będzie musiał go przyciąć, co może prowadzić do utraty kluczowych informacji i w rezultacie do mniej trafnych sugestii.

Tokeny są podstawowymi jednostkami przetwarzanymi przez model. Mogą to być całe słowa, części słów, znaki interpunkcyjne, a nawet spacje. Liczba tokenów w oknie kontekstowym jest zazwyczaj stała dla danego modelu i środowiska (np. 8k, 16k, 32k, 128k tokenów). Po przekroczeniu tego limitu, model musi zdecydować, które tokeny są najważniejsze, a które można odrzucić, aby zmieścić się w oknie. Proces ten, zwany "przycinaniem kontekstu", jest heurystyczny i nie zawsze prowadzi do zachowania najbardziej istotnych informacji dla Twojego zadania.

**Skutki przekroczenia token window:**
-   **Ignorowanie części kodu:** Najmniej istotne fragmenty (z perspektywy modelu) mogą zostać odrzucone, nawet jeśli są kluczowe dla Twojego zadania. Może to dotyczyć deklaracji klas, interfejsów, adnotacji czy ważnych fragmentów logiki biznesowej, które są niezbędne do prawidłowego zrozumienia problemu.
-   **Ogólnikowe sugestie:** Bez pełnego kontekstu, Copilot może generować bardziej generyczne, "bezpieczne" sugestie, które nie są specyficzne dla Twojego projektu. Zamiast dostosowanego rozwiązania, otrzymasz ogólny boilerplate, który wymaga znacznych modyfikacji.
-   **Błędy logiczne:** Jeśli Copilot nie "widzi" ważnych zależności (np. sygnatur metod w innym pliku, które miałyby być wywołane), może zasugerować kod, który wprowadza błędy logiczne, nie kompiluje się lub nie jest zgodny z innymi częściami systemu. To prowadzi do frustracji i dodatkowego czasu na debugowanie.
-   **Spadek wydajności:** Modele językowe są bardziej efektywne, gdy operują na spójnym i kompletnym kontekście. Fragmentaryczny kontekst może prowadzić do dłuższych czasów generowania odpowiedzi i niższej jakości sugestii.

**Strategie optymalizacji token window:**
1.  **Selektywne użycie `@workspace` i `#file`:** Zawsze zastanawiaj się, ile kontekstu Copilot naprawdę potrzebuje. Dla precyzyjnych zmian w jednym pliku użyj `#file`. Dla zadań obejmujących kilka ściśle powiązanych plików, możesz użyć `@workspace`, ale bądź świadomy jego limitów i monitoruj jakość generowanych odpowiedzi. Jeśli Copilot zaczyna generować dziwne lub niepowiązane sugestie, może to być znak zbyt szerokiego kontekstu.
2.  **Explicitne wskazywanie plików (tzw. "focused context"):** W niektórych narzędziach (np. Copilot Chat) możesz jawnie wskazać konkretne pliki, które mają być dodane do kontekstu, np. `/explain @file:src/main/java/org/springframework/samples/petclinic/owner/OwnerService.java`. To pozwala na ręczne sterowanie tym, co Copilot 'widzi', bez konieczności angażowania całego obszaru roboczego, co jest idealnym kompromisem między `#file` a `@workspace`.
3.  **Refaktoryzacja kodu:** Długie metody, duże klasy i skomplikowane zależności zwiększają objętość kontekstu. Refaktoryzacja kodu na mniejsze, bardziej spójne jednostki nie tylko poprawia czytelność i utrzymywalność, ale także ułatwia Copilotowi przetwarzanie kontekstu. Mniejsze, samodzielne komponenty są łatwiejsze do zrozumienia i przetwarzania przez LLM.
4.  **Komentowanie kodu:** Dobrze napisane komentarze (zwłaszcza Javadoc w Javie, docstrings w Pythonie) mogą w zwięzły sposób opisać logikę i przeznaczenie kodu, redukując potrzebę analizowania dużej ilości szczegółów przez Copilota. Pamiętaj jednak, aby komentarze były aktualne i precyzyjne, ponieważ nieaktualne komentarze mogą wprowadzać Copilota w błąd.
5.  **Czyszczenie nieużywanego kodu:** Usunięcie martwego kodu, nieużywanych zależności czy zakomentowanych fragmentów zmniejsza ogólną objętość projektu, co pośrednio wpływa na efektywność zarządzania kontekstem. Lżejszy projekt to szybsze i bardziej trafne sugestie.
6.  **Użycie `.copilotignore`:** Podobnie jak `.gitignore`, możesz stworzyć plik `.copilotignore`, aby wykluczyć z kontekstu Copilota folderów lub plików, które nie są istotne dla generowania kodu (np. `build/`, `node_modules/`, pliki logów, dokumentacja niekodowa). To pozwala na manualne zmniejszenie objętości kontekstu.

### Inżynieria Promptów dla Jakości i Precyzji

Inżynieria promptów (Prompt Engineering) to sztuka i nauka formułowania zapytań do modeli językowych w taki sposób, aby uzyskać od nich jak najbardziej trafne, precyzyjne i użyteczne odpowiedzi. Skuteczne prompty to podstawa efektywnego wykorzystania GitHub Copilot. Dobrze sformułowany prompt to połowa sukcesu w pracy z Copilotem, przekształcając go z prostego narzędzia do autouzupełniania w potężnego asystenta programistycznego.

#### Zasady Tworzenia Efektywnych Promptów

1.  **Bądź precyzyjny i jednoznaczny:** Unikaj ogólników. Zamiast "Napisz kod", powiedz "Napisz funkcję, która waliduje adres e-mail zgodnie ze standardem RFC 5322, zwracając `true` dla poprawnego i `false` dla niepoprawnego adresu". Określ konkretne wymagania, typy danych, wartości brzegowe.
2.  **Określ cel i zadanie:** Co dokładnie chcesz osiągnąć? Czy to generowanie kodu, refaktoryzacja, testy, dokumentacja, debugowanie, optymalizacja? Jasno to zakomunikuj na początku promptu. "Wygeneruj testy jednostkowe dla...", "Zrefaktoryzuj tę metodę, aby...", "Wyjaśnij działanie tego bloku kodu...".
3.  **Podaj kontekst (jeśli nie używasz `@workspace` / `#file`):** Jeśli to konieczne, wklej istotne fragmenty kodu bezpośrednio do promptu lub użyj odpowiednich modyfikatorów Copilota. Opisz tło zadania, problem, który próbujesz rozwiązać, i istniejące rozwiązania, które Copilot powinien wziąć pod uwagę.
4.  **Zdefiniuj format wyjściowy:** Czy oczekujesz kodu w Javie, Pythona? Czy ma to być klasa, metoda, fragment JSON, YAML, czy pełny plik? Czy ma zawierać komentarze, testy, adnotacje? "Zwróć wynik jako JSON zawierający pola `name` i `version`" lub "Wygeneruj pełny plik `.java` dla klasy `MyService` wraz z niezbędnymi importami".
5.  **Podaj przykłady (Few-shot prompting):** Jeśli masz specyficzny styl kodowania, potrzebujesz implementacji konkretnego wzorca projektowego lub chcesz, aby Copilot dostosował się do istniejących konwencji, podaj jeden lub dwa przykłady wejścia i oczekiwanego wyjścia w prompcie. Copilot często potrafi zaadaptować się do podanego stylu i wzorców.
6.  **Używaj języka naturalnego, ale technicznego:** Pisz w sposób konwersacyjny, ale z użyciem terminologii technicznej specyficznej dla języka programowania, frameworka lub domeny, która pomoże Copilotowi lepiej zrozumieć intencje. Unikaj slangu.
7.  **Zdefiniuj rolę (Persona):** Czasami przydaje się nadanie Copilotowi roli, np. "Jesteś doświadczonym programistą Java Spring Boot z 10-letnim doświadczeniem w bankowości..." lub "Działasz jako ekspert od bezpieczeństwa, sprawdź ten kod pod kątem podatności...". To pomaga Copilotowi przyjąć odpowiedni punkt widzenia i dostosować swoje sugestie.
8.  **Wskazówki i ograniczenia:** Określ, czego nie chcesz lub jakie ograniczenia muszą być spełnione. "Nie używaj pętli for, zastosuj Stream API". "Użyj adnotacji Lombok do generowania getterów i setterów". "Nie wprowadzaj nowych zależności do `pom.xml`". "Zapewnij, że rozwiązanie jest zgodne z Java 8".
9.  **Strukturyzuj prompty:** Używaj nagłówków, list punktowanych, bloków kodu i innych elementów formatowania, aby uczynić prompt czytelnym i łatwym do przetworzenia. Długie, jednolite bloki tekstu są trudniejsze do parsowania zarówno dla ludzi, jak i dla LLMów.

#### Iteracyjne Udoskonalanie Promptów

Tworzenie idealnego promptu rzadko udaje się za pierwszym razem. Skuteczne inżynierowanie promptów to proces iteracyjny, który wymaga eksperymentowania i analitycznego podejścia:

1.  **Start z prostym promptem:** Zacznij od ogólnego zapytania, aby zobaczyć, co Copilot potrafi wygenerować. To jest Twój punkt wyjścia do dalszych iteracji.
2.  **Analizuj odpowiedź:** Czy jest blisko celu? Co jest dobre, co złe, co brakuje? Czy kod jest kompletny, kompiluje się? Czy spełnia wymagania funkcjonalne i niefunkcjonalne? Zidentyfikuj luki i problemy.
3.  **Udoskonal prompt:** Dodaj precyzji, więcej kontekstu, ograniczenia, przykłady, poprawki formatu. Pamiętaj o zasadach tworzenia efektywnych promptów. Każda iteracja powinna wprowadzać konkretne zmiany mające na celu rozwiązanie zidentyfikowanych problemów.
4.  **Testuj ponownie:** Powtórz proces, aż uzyskasz satysfakcjonujący wynik. Może to wymagać wielu rund poprawek, ale każda z nich przybliża Cię do idealnego rozwiązania.

*Przykład iteracji dla walidacji wieku zwierzęcia w `PetController.java` (Spring Petclinic)*:

*   **Prompt 1 (ogólny):** "Dodaj walidację wieku zwierzęcia do PetController."
    *   *Wynik:* Może dodać podstawową walidację, ale bez komunikatów, bez adnotacji Spring. Może to być `if (pet.getAge() <= 0) { // obsługa błędu }`.
    *   *Problem:* Brak integracji ze Spring MVC, brak specyficznych komunikatów, brak użycia standardowych adnotacji walidacyjnych.
*   **Prompt 2 (poprawiony - dodano szczegóły walidacji i komunikat):** "W PetController.java, dodaj walidację wieku dla pola 'age' w obiekcie Pet. Wiek musi być dodatnią liczbą całkowitą. Użyj adnotacji `@Min(0)` i `@NotNull` na polu w klasie Pet. W metodzie `processUpdateForm`, jeśli walidacja się nie powiedzie, zwróć komunikat 'Wiek musi być dodatni' i ponownie wyrenderuj formularz."
    *   *Wynik:* Bardziej precyzyjna walidacja, ale może nadal nie być w pełni zgodna z konwencjami obsługi błędów Spring MVC (`BindingResult.rejectValue`).
    *   *Problem:* Brak wykorzystania `BindingResult` do precyzyjnego przypisania błędu do pola, co może prowadzić do nieprawidłowego wyświetlania błędów w formularzu.
*   **Prompt 3 (zaawansowany - pełna integracja ze Spring MVC):** "Jako doświadczony programista Spring Boot, zaktualizuj metodę `processUpdateForm` w PetController.java, aby dodać walidację dla pola 'age' obiektu Pet. Upewnij się, że 'age' jest większe od zera. Zastosuj wbudowane adnotacje walidacyjne Spring (`@Min`) na polu `age` w klasie `Pet` oraz Spring `BindingResult` do obsługi błędów walidacji. Jeśli walidacja pola `age` zawiedzie, dodaj błąd do `BindingResult` za pomocą `rejectValue` dla pola 'age' z komunikatem 'Wiek musi być dodatni'. Upewnij się, że strona formularza `pets/createOrUpdatePetForm` jest ponownie renderowana w przypadku błędu walidacji, przekazując obiekt `pet` i `owner` do modelu. Ogranicz kontekst do `PetController.java` i `Pet.java`. #file"
    *   *Wynik:* Pełne, zgodne ze Spring Boot rozwiązanie, uwzględniające obsługę błędów formularza w sposób idiomatyczny dla frameworka. Zapewnia prawidłowe wyświetlanie błędów walidacji na stronie.

#### Przykłady Zaawansowanych Technik Promptowania

1.  **Chain-of-Thought Prompting (CoT):** Technika, w której prosisz Copilota o "myślenie krok po kroku" lub o rozłożenie problemu na mniejsze, logiczne etapy przed przedstawieniem ostatecznego rozwiązania. Jest to szczególnie przydatne dla złożonych zadań, które wymagają wieloetapowego rozumowania. Np. "Zaproponuj plan implementacji systemu cache'owania dla tej aplikacji. Krok 1: Wybór technologii (Redis/Ehcache). Krok 2: Projekt interfejsu cache. Krok 3: Implementacja warstwy serwisu. Następnie, po planie, wygeneruj kod dla kroku 2."
2.  **Few-Shot Prompting z przykładami kodu:** Dostarcz Copilotowi kilka przykładów prawidłowego wejścia i wyjścia, aby nauczyć go konkretnego wzorca lub preferowanego stylu kodowania. To niezwykle efektywne przy adaptacji do istniejącego stylu kodowania lub niestandardowych formatów. Na przykład, jeśli masz niestandardową klasę exception i chcesz, aby Copilot generował podobne, podaj 2-3 przykłady.
3.  **Myślenie krok po kroku (Explicit "Let's think step by step")**: Włączenie tej frazy w prompt może skłonić Copilota do generowania bardziej ustrukturyzowanych i logicznych odpowiedzi, rozbijając proces rozwiązywania problemu na mniejsze, łatwiejsze do śledzenia kroki. Jest to ogólna zasada, która często poprawia jakość odpowiedzi w złożonych scenariuszach.
4.  **Wskazywanie na konkretne linie/bloki (Inline Chat/Context Selection):** Jeśli masz długi plik, możesz zaznaczyć konkretny blok kodu i poprosić Copilota o jego refaktoryzację, wyjaśnienie lub dodanie testów. To działa jak bardzo precyzyjne `#file` wewnątrz pliku, pozwalając na hiper-precyzyjne dostosowanie kontekstu do aktualnie edytowanego fragmentu kodu.
5.  **Negatywne wskazówki (Negative Constraints):** Poinformuj Copilota, czego **nie** chcesz, aby uniknąć niepożądanych sugestii. Np. "Nie używaj klas pomocniczych (utility classes), zaimplementuj to jako metodę w istniejącej klasie". "Unikaj stosowania rekurencji".
6.  **Określanie złożoności (Complexity constraints):** Poproś Copilota o generowanie kodu, który spełnia określone wymagania dotyczące złożoności obliczeniowej lub pamięciowej. Np. "Zaproponuj algorytm o złożoności czasowej O(n log n)".

## 💡 Przykłady Użycia

### Przykład 1: Dokumentacja warstwy serwisowej z `@workspace`

**Scenariusz:** Chcemy wygenerować ogólne podsumowanie działania warstwy serwisowej w `spring-petclinic`, aby lepiej zrozumieć jej architekturę i zależności. Jest to zadanie wysokopoziomowe, które wymaga zrozumienia całego podsystemu.

**Prompt:**
```
Jako architekt oprogramowania, przygotuj szczegółową dokumentację techniczną dla warstwy serwisowej w projekcie `spring-petclinic`. Opisz główne serwisy (OwnerService, VetService, PetService, VisitService), ich kluczowe metody, odpowiedzialności oraz wzajemne zależności. Zwróć uwagę na przepływ danych i interakcje między nimi. Dokumentacja powinna być zwięzła, ale kompleksowa. Użyj @workspace, aby uzyskać pełen kontekst.
```

**Oczekiwany rezultat (fragment):** Copilot powinien wygenerować opis, który łączy informacje z różnych plików serwisowych, pokazując, jak np. `VisitService` korzysta z `PetService` do pobierania informacji o zwierzętach, a `OwnerService` zarządza właścicielami i ich zwierzętami. Zamiast opisywać każdy serwis w izolacji, dokumentacja powinna przedstawić całościowy obraz, uwzględniając cykl życia danych i relacje między encjami obsługiwanymi przez serwisy.

```markdown
## Architektura Warstwy Serwisowej w Spring PetClinic

Warstwa serwisowa w aplikacji Spring PetClinic odpowiada za logikę biznesową, orkiestrację danych oraz abstrakcję nad warstwą dostępu do danych (repozytoriów). Stanowi ona kluczowe ogniwo między kontrolerami (warstwa prezentacji) a warstwą persystencji. Jej głównym celem jest zapewnienie spójności danych i enkapsulacja złożonych operacji biznesowych.

### Kluczowe Serwisy i Ich Odpowiedzialności:

1.  **`OwnerService` (lub `PetClinicService` w starszych wersjach):**
    *   **Odpowiedzialność:** Zarządzanie cyklem życia właścicieli (Owner) oraz ich zwierząt (Pet). Obejmuje tworzenie, odczytywanie, aktualizowanie i usuwanie (CRUD) danych właścicieli i zwierząt, a także wyszukiwanie właścicieli po nazwisku.
    *   **Kluczowe Metody:** `findOwners()`, `findOwnerById()`, `saveOwner()`, `findPetsByOwner()`, `savePet()`, `deleteOwner()`.
    *   **Interakcje:** Współpracuje bezpośrednio z `OwnerRepository` i `PetRepository` dla operacji bazodanowych. Może również pośredniczyć w tworzeniu wizyt, delegując zadania do `VisitService`.

2.  **`VetService`:**
    *   **Odpowiedzialność:** Zarządzanie danymi weterynarzy (Vet) i ich specjalności (Specialty). Udostępnia funkcjonalności do pobierania listy weterynarzy i zarządzania ich profilami.
    *   **Kluczowe Metody:** `findVets()`, `findVetById()`, `saveVet()`, `findSpecialties()`.
    *   **Interakcje:** Współpracuje z `VetRepository` i `SpecialtyRepository`.

3.  **`PetService` (często zintegrowane z `OwnerService` w prostszych architekturach):**
    *   **Odpowiedzialność:** Specyficzne operacje na obiektach zwierząt (Pet), takie jak walidacja typów, przypisywanie typów zwierząt. W bardziej rozbudowanych aplikacjach może mieć własne, niezależne operacje.
    *   **Kluczowe Metody:** `findPetTypes()`, `findPetById()`, `savePet()`, `deletePet()`.
    *   **Interakcje:** Silnie powiązane z `OwnerService` (zwierzęta należą do właścicieli), współpracuje z `PetRepository` i `PetTypeRepository`.

4.  **`VisitService`:**
    *   **Odpowiedzialność:** Zarządzanie wizytami (Visit) dla zwierząt. Odpowiada za planowanie, zapisywanie i pobieranie informacji o wizytach.
    *   **Kluczowe Metody:** `saveVisit()`, `findVisitsByPetId()`, `deleteVisit()`.
    *   **Interakcje:** Zazwyczaj wymaga obiektu `Pet`, więc często wchodzi w interakcje z `PetService` lub `OwnerService` w celu pobrania danych zwierzęcia przed utworzeniem wizyty. Współpracuje z `VisitRepository`.

### Przepływ Danych i Zależności:

Klient (np. kontroler HTTP) wywołuje metody w serwisach. Serwisy z kolei wykorzystują repozytoria do interakcji z bazą danych, stanowiąc warstwę abstrakcji nad persystencją. Oto przykładowy przepływ dla operacji dodawania wizyty:

1.  **Żądanie z kontrolera:** `VisitController` otrzymuje żądanie dodania nowej wizyty i wywołuje `VisitService.saveVisit(Visit visit)`. 
2.  **Walidacja i przygotowanie w serwisie:** `VisitService` może najpierw upewnić się, że obiekt `visit` jest poprawny, a zwierzę (`visit.getPet()`) istnieje w systemie (pobierając go z `PetService` lub `OwnerService` jeśli `pet` w `visit` jest niekompletne).
3.  **Persystencja:** Następnie `VisitService` używa `VisitRepository.save(visit)` do utrwalenia danych w bazie danych.
4.  **Odpowiedź do kontrolera:** Po pomyślnym zapisie, `VisitService` zwraca wynik do kontrolera, który następnie generuje odpowiednią odpowiedź dla użytkownika.

Ta struktura zapewnia separację odpowiedzialności, ułatwia testowanie jednostkowe i integracyjne poszczególnych warstw oraz promuje czystą architekturę, zgodną z zasadami SOLID.
```

### Przykład 2: Precyzyjny Refaktoring z `#file` w `VetService.java`

**Scenariusz:** Chcemy zrefaktoryzować metodę `findVets()` w `VetService.java`, aby korzystała z Java Stream API do sortowania weterynarzy alfabetycznie po nazwisku. Kluczowe jest, aby ta zmiana nie miała niezamierzonych konsekwencji w innych plikach, dlatego użyjemy `#file`.

**Prompt:**
```
Jako doświadczony programista Java, zrefaktoryzuj metodę `findVets()` w pliku `VetService.java` w projekcie `spring-petclinic`. Aktualnie metoda zwraca `Collection<Vet>`. Chcę, aby przed zwróceniem kolekcji, weterynarze byli sortowani alfabetycznie po nazwisku. Użyj Java Stream API do posortowania kolekcji. Zachowaj wszystkie importy i adnotacje. Ogranicz kontekst do tego pliku (`VetService.java`). #file
```

**Fragment oryginalnego `VetService.java` (przed zmianami):**
```java
package org.springframework.samples.petclinic.vet;

import java.util.Collection;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class VetService {

	private VetRepository vetRepository;

	@Autowired
	public VetService(VetRepository vetRepository) {
		this.vetRepository = vetRepository;
	}

	@Transactional(readOnly = true)
	public Collection<Vet> findVets() throws DataAccessException {
		return vetRepository.findAll();
	}

}
```

**Oczekiwany rezultat (fragment zrefaktoryzowanego `VetService.java`):** Copilot powinien zaktualizować tylko metodę `findVets`, dodając logikę sortowania za pomocą Stream API, nie modyfikując niczego poza tym plikiem. Ważne jest, aby dodał niezbędne importy (`java.util.Comparator`, `java.util.stream.Collectors`).

```java
package org.springframework.samples.petclinic.vet;

import java.util.Collection;
import java.util.Comparator;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DataAccessException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class VetService {

	private VetRepository vetRepository;

	@Autowired
	public VetService(VetRepository vetRepository) {
		this.vetRepository = vetRepository;
	}

	@Transactional(readOnly = true)
	public Collection<Vet> findVets() throws DataAccessException {
		// Zrefaktoryzowana metoda z użyciem Stream API do sortowania
		return vetRepository.findAll().stream()
			.sorted(Comparator.comparing(Vet::getLastName))
			.collect(Collectors.toList());
	}

}
```

### Przykład 3: Generowanie Testów Integracyjnych dla `OwnerController.java`

**Scenariusz:** Potrzebujemy kompleksowych testów integracyjnych dla `OwnerController`, które weryfikują zachowanie aplikacji w różnych scenariuszach interakcji użytkownika z formularzami, takich jak dodawanie nowego właściciela, wyszukiwanie i obsługa błędów walidacji.

**Prompt:**
```
Jako programista testów automatycznych, napisz pełne testy integracyjne dla OwnerController.java w `spring-petclinic`. Stwórz nową klasę testową o nazwie `OwnerControllerIntegrationTests`. Obejmij następujące scenariusze:
1.  Test pomyślnego dodania nowego właściciela z poprawnymi danymi (POST `/owners/new`) i weryfikacja przekierowania do strony szczegółów właściciela.
2.  Test próby dodania właściciela z brakującymi lub niepoprawnymi danymi (np. puste pola `firstName`, `lastName` lub nieprawidłowy format `telephone`) i weryfikacja błędu walidacji (status OK, błędy w modelu, powrót do formularza).
3.  Test wyszukiwania właścicieli po nazwisku, które nie istnieje w bazie danych i weryfikacja, że strona wyszukiwania jest ponownie renderowana.
4.  Test wyszukiwania właścicieli po częściowym nazwisku, które zwraca tylko jeden wynik i weryfikacja przekierowania do strony szczegółów tego właściciela.
5.  Test wyszukiwania właścicieli po częściowym nazwisku, które zwraca wiele wyników i weryfikacja, że wyświetlona jest lista właścicieli.

Użyj Spring MockMvc i JUnit 5. Zapewnij, że testy są niezależne i czyszczą stan po sobie, jeśli to konieczne. Skorzystaj z `@MockBean` dla `OwnerRepository` i zasymuluj jego zachowanie za pomocą `BDDMockito.given()`.
```

**Oczekiwany rezultat (fragment `OwnerControllerIntegrationTests.java`):** Copilot powinien wygenerować klasę testową, która używa `MockMvc` do symulowania żądań HTTP i weryfikowania odpowiedzi. `BDDMockito` będzie używane do mockowania zachowań `OwnerRepository`.

```java
package org.springframework.samples.petclinic.owner;

import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.model;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.view;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Arrays;
import java.util.Collections;

/**
 * Testy integracyjne dla OwnerController z wykorzystaniem MockMvc i JUnit 5.
 */
@WebMvcTest(OwnerController.class)
class OwnerControllerIntegrationTests {

	@Autowired
	private MockMvc mockMvc;

	@MockBean
	private OwnerRepository owners; // Mockowanie repozytorium

	private Owner george;
	private Owner betty;

	@BeforeEach
	void setup() {
		// Inicjalizacja danych dla testów
		george = new Owner();
		george.setId(1);
		george.setFirstName("George");
		george.setLastName("Franklin");
		george.setAddress("110 W. Liberty St.");
		george.setCity("Madison");	
		george.setTelephone("6085551023");

		betty = new Owner();
		betty.setId(2);
		betty.setFirstName("Betty");
		betty.setLastName("Davis");
		betty.setAddress("638 Cardinal Ave.");
		betty.setCity("Sun Prairie");
		betty.setTelephone("6085551749");

		// Konfiguracja zachowania mocka OwnerRepository
		given(this.owners.findByLastName("Franklin")).willReturn(Arrays.asList(george));
		given(this.owners.findAll()).willReturn(Arrays.asList(george, betty));
		// Konfiguracja dla wyszukiwania wielu wyników
		given(this.owners.findByLastName("a")).willReturn(Arrays.asList(george, betty));
		// Konfiguracja dla pojedynczego wyniku po częściowym nazwisku
		given(this.owners.findByLastName("Fra")).willReturn(Arrays.asList(george));
	}

	@Test
	void testProcessCreationFormSuccess() throws Exception {
		mockMvc.perform(post("/owners/new")
			.param("firstName", "James")
			.param("lastName", "Bond")
			.param("address", "123 Secret St")
			.param("city", "London")
			.param("telephone", "007007007"))
			.andExpect(status().is3xxRedirection())
			.andExpect(view().name("redirect:/owners/{ownerId}"));
	}

	@Test
	void testProcessCreationFormHasErrors() throws Exception {
		mockMvc.perform(post("/owners/new")
			.param("firstName", "") // Puste imię - błąd walidacji
			.param("lastName", "Bond")
			.param("address", "123 Secret St")
			.param("city", "London")
			.param("telephone", "007007007"))
			.andExpect(status().isOk())
			.andExpect(model().attributeHasErrors("owner"))
			.andExpect(model().attributeHasFieldErrors("owner", "firstName"))
			.andExpect(view().name("owners/createOrUpdateOwnerForm"));
	}

	@Test
	void testFindOwnersNotFound() throws Exception {
		given(this.owners.findByLastName("NonExistent")).willReturn(Collections.emptyList());

		mockMvc.perform(get("/owners")
			.param("lastName", "NonExistent"))
			.andExpect(status().isOk())
			.andExpect(model().attributeHasErrors("owner")) // Oczekujemy błędu (np. Not found) lub pustej listy
			.andExpect(view().name("owners/findOwners")); // Powrót do formularza wyszukiwania
	}

	@Test
	void testFindOwnersOneResult() throws Exception {
		mockMvc.perform(get("/owners")
			.param("lastName", "Franklin"))
			.andExpect(status().is3xxRedirection())
			.andExpect(view().name("redirect:/owners/1")); // Przekierowanie do George'a
	}

	@Test
	void testFindOwnersMultipleResults() throws Exception {
		mockMvc.perform(get("/owners")
			.param("lastName", "a")) // Wyszukaj wszystkich, którzy mają 'a' w nazwisku
			.andExpect(status().isOk())
			.andExpect(view().name("owners/ownersList"))
			.andExpect(model().attribute("selections", hasSize(2))); // Oczekujemy 2 wyników
	}
}
```

### Przykład 4: Optymalizacja Promptu do Walidacji Wieku w `PetController.java`

**Scenariusz:** Chcemy dodać walidację wieku zwierzęcia (Pet) w formularzu edycji (`processUpdateForm`), upewniając się, że wiek jest dodatni. Pokażemy, jak iteracyjnie udoskonalić prompt, aby uzyskać dokładne i zgodne ze Spring Boot rozwiązanie, które prawidłowo integruje się z mechanizmem walidacji Spring MVC.

**Początkowy fragment `PetController.java` (metoda `processUpdateForm`):**
```java
package org.springframework.samples.petclinic.pet;

import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.Collection;

@Controller
@RequestMapping("/owners/{ownerId}")
class PetController {

    // ... inne metody i pola

    @PostMapping("/pets/{petId}/edit")
    public String processUpdateForm(@Valid Pet pet, BindingResult result, Owner owner, ModelMap model) {
        if (result.hasErrors()) {
            pet.setOwner(owner);
            model.addAttribute("pet", pet);
            return "pets/createOrUpdatePetForm";
        }
        owner.addPet(pet);
        this.petService.savePet(pet);
        return "redirect:/owners/{ownerId}";
    }
    // ...
}
```
**Oraz fragment `Pet.java` (klasa, do której należą pola `age`):**
```java
package org.springframework.samples.petclinic.pet;

import org.springframework.samples.petclinic.model.NamedEntity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;
import javax.validation.constraints.NotEmpty;
import javax.validation.constraints.Min;

@Entity
@Table(name = "pets")
public class Pet extends NamedEntity {

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Column(name = "age")
    private Integer age; // To pole chcemy walidować

    // ... Gettery i Settery
}
```

**Prompt 1 (podstawowy - skupienie na samej walidacji):**
```
Jako programista Java, chcę dodać walidację do pola `age` w obiekcie `Pet` w `PetController.java`. Upewnij się, że wiek jest dodatnią liczbą całkowitą. Zwróć mi tylko kod implementujący tę walidację.
```
*   *Wynik Copilota (prawdopodobny):* Może zasugerować dodanie adnotacji `@Min(1)` do pola `age` w klasie `Pet.java` lub prosty `if (pet.getAge() == null || pet.getAge() <= 0) { // obsługa błędu }` w kontrolerze.
*   *Problem:* Brak integracji ze Spring MVC `BindingResult`, brak specyficznych komunikatów, może nie uwzględniać nulli w wieku, jeśli pole jest opcjonalne. Sugestia może dotyczyć klasy `Pet`, ale nie wskazuje, jak to obsłużyć w `PetController`.

**Prompt 2 (ulepszony - włączenie Spring Validation i komunikatów):**
```
Jako programista Spring, zaktualizuj metodę `processUpdateForm` w PetController.java. Dodaj walidację, aby upewnić się, że pole `age` w obiekcie `Pet` jest większe od zera. Jeśli `age` nie jest dodatnie, dodaj błąd do `BindingResult` za pomocą `rejectValue` dla pola 'age' z komunikatem 'Wiek musi być dodatni'. W przypadku błędów walidacji, formularz `pets/createOrUpdatePetForm` powinien zostać ponownie renderowany, przekazując `pet` i `owner` do modelu. Ogranicz kontekst do `PetController.java`.
```
*   *Wynik Copilota (prawdopodobny):* Bardziej kompletne rozwiązanie, które może wyglądać tak:

```java
    @PostMapping("/pets/{petId}/edit")
    public String processUpdateForm(@Valid Pet pet, BindingResult result, Owner owner, ModelMap model) {
        if (pet.getAge() == null || pet.getAge() <= 0) {
            result.rejectValue("age", "invalid", "Wiek musi być dodatni");
        }
        if (result.hasErrors()) {
            pet.setOwner(owner);
            model.addAttribute("pet", pet);
            model.addAttribute("owner", owner);
            return "pets/createOrUpdatePetForm";
        }
        owner.addPet(pet);
        this.petService.savePet(pet);
        return "redirect:/owners/{ownerId}";
    }
```
*   *Problem:* Nadal nie używa adnotacji `@Min` w klasie `Pet`, co jest bardziej idiomatyczne dla walidacji w Spring. Ręczne sprawdzenie `if (pet.getAge() == null || pet.getAge() <= 0)` jest redundantne, gdy można użyć standardowych mechanizmów. Pole `age` w `Pet` powinno być też oznaczone adnotacją `@NotNull`.

**Prompt 3 (zaawansowany - pełna integracja ze Spring Validation Adnotacjami):**
```
Jako doświadczony programista Spring Boot, zaktualizuj klasę `Pet.java` i metodę `processUpdateForm` w `PetController.java`. W `Pet.java`, upewnij się, że pole `age` jest wymagane (nie null) i jest większe od zera, używając adnotacji walidacyjnych `@NotNull` i `@Min(1)`. Następnie, w `PetController.java`, upewnij się, że metoda `processUpdateForm` poprawnie obsługuje błędy walidacji z `BindingResult`. W przypadku błędów walidacji, formularz `pets/createOrUpdatePetForm` powinien zostać ponownie renderowany, przekazując `pet` i `owner` do modelu. Zapewnij, że `BindingResult` jest prawidłowo przetwarzany, aby komunikaty walidacyjne z adnotacji były wyświetlane. Ogranicz kontekst do `PetController.java` i `Pet.java`. #file
```
*   *Wynik Copilota:* Pełne, zgodne ze Spring Boot rozwiązanie, które modyfikuje `Pet.java` i `PetController.java`. Copilot powinien dodać adnotacje do `Pet.java` i zapewnić, że `processUpdateForm` w `PetController` używa `@Valid` i prawidłowo obsługuje `BindingResult`.

**Fragment zrefaktoryzowanego `Pet.java` (dodane adnotacje):**
```java
package org.springframework.samples.petclinic.pet;

import org.springframework.samples.petclinic.model.NamedEntity;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Table;
import javax.validation.constraints.Min;
import javax.validation.constraints.NotNull; // Dodane
import java.time.LocalDate;

@Entity
@Table(name = "pets")
public class Pet extends NamedEntity {

    @Column(name = "birth_date")
    private LocalDate birthDate;

    @Column(name = "age")
    @NotNull(message = "Wiek jest wymagany") // Dodane
    @Min(value = 1, message = "Wiek musi być dodatni") // Zaktualizowane
    private Integer age;

    // ... Gettery i Settery
}
```

**Fragment zrefaktoryzowanego `PetController.java` (użycie `@Valid` i obsługa `BindingResult`):**
```java
package org.springframework.samples.petclinic.pet;

import org.springframework.samples.petclinic.owner.Owner;
import org.springframework.samples.petclinic.owner.OwnerService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

import javax.validation.Valid;
import java.util.Collection;

@Controller
@RequestMapping("/owners/{ownerId}")
class PetController {

    private final PetService petService;
    private final OwnerService ownerService;

    public PetController(PetService petService, OwnerService ownerService) {
        this.petService = petService;
        this.ownerService = ownerService;
    }

    // ... Inne metody

    @PostMapping("/pets/{petId}/edit")
    public String processUpdateForm(@Valid Pet pet, BindingResult result, @PathVariable("ownerId") int ownerId, ModelMap model) {
        if (result.hasErrors()) {
            // Jeśli są błędy walidacji z Pet, upewniamy się, że obiekt owner jest w modelu
            Owner owner = this.ownerService.findOwnerById(ownerId);
            pet.setOwner(owner); // Musimy ustawić ownera, bo @Valid działa na pet
            model.addAttribute("pet", pet);
            model.addAttribute("owner", owner);
            model.addAttribute("types", petService.findPetTypes()); // Potrzebne do renderowania formularza
            return "pets/createOrUpdatePetForm";
        }
        
        // Jeśli walidacja przeszła, aktualizujemy zwierzę i przekierowujemy
        // W PetClinic, Pet jest dodawane do listy w Owner, więc musimy pobrać Ownera
        // i zaktualizować jego listę zwierząt, zanim zapiszemy Pet.
        Owner owner = this.ownerService.findOwnerById(ownerId);
        pet.setOwner(owner);
        owner.addPet(pet); // Upewnij się, że zaktualizowane Pet jest w liście ownera
        this.petService.savePet(pet);
        return "redirect:/owners/{ownerId}";
    }
    // ...
}
```

## ✅ Best Practices
-   **Zawsze zaczynaj od jasnego celu:** Przed napisaniem promptu, dokładnie sprecyzuj, co chcesz osiągnąć. Im precyzyjniej zdefiniujesz zadanie, tym lepsze będą sugestie Copilota.
-   **Używaj `@workspace` ostrożnie:** W dużych projektach, używaj `@workspace` tylko wtedy, gdy zadanie faktycznie wymaga globalnego kontekstu (np. generowanie architektury, refaktoring między modułami). W przeciwnym razie, skup się na mniejszym zakresie.
-   **`#file` dla precyzji:** Kiedy pracujesz nad konkretnym plikiem lub fragmentem kodu, użyj `#file` lub zaznacz zakres, aby ograniczyć kontekst. Zwiększa to trafność sugestii i redukuje szumy.
-   **Zdefiniuj rolę i format wyjściowy:** Poinformuj Copilota, kim "jesteś" (np. "Jako programista Java Spring") i w jakim formacie oczekujesz odpowiedzi (np. "Generuj kod w Java 8", "Zwróć jako JSON").
-   **Iteruj i testuj prompty:** Traktuj inżynierię promptów jako proces rozwojowy. Rzadko idealny prompt powstaje za pierwszym razem. Analizuj wyniki i systematycznie udoskonalaj swoje zapytania.
-   **Segmentuj złożone zadania:** Dziel duże problemy na mniejsze, łatwiejsze do zarządzania podzadania. Każde podzadanie może mieć swój własny, zoptymalizowany prompt.
-   **Używaj komentarzy w kodzie jako mini-promptów:** Krótkie, precyzyjne komentarze przed fragmentami kodu, które chcesz wygenerować lub zmodyfikować, mogą działać jak wyzwalacze dla Copilota, kierując jego sugestie.
-   **Utrzymuj kod czystym i zorganizowanym:** Czysty kod z wyraźnymi nazwami i logiką jest łatwiejszy do zrozumienia dla Copilota, co przekłada się na lepsze sugestie. Regularny refaktoring to nie tylko dobra praktyka programistyczna, ale także forma optymalizacji kontekstu dla AI.

## ⚠️ Common Pitfalls
-   **Zbyt ogólne prompty:** "Napisz kod dla mnie" jest bezużyteczne. Brak precyzji prowadzi do ogólnych, często niepoprawnych lub niepasujących sugestii, które wymagają dużo pracy ręcznej.
-   **Ignorowanie limitu tokenów:** Przeciążanie Copilota zbyt dużym kontekstem prowadzi do ignorowania istotnych fragmentów kodu i obniżenia jakości odpowiedzi. Zawsze miej na uwadze "token window".
-   **Brak precyzji w wymaganiach:** Nieokreślenie typów danych, wartości brzegowych, zależności czy formatów wyjściowych spowoduje, że Copilot będzie "zgadywał", często w nieprawidłowy sposób.
-   **Niejasny format wyjściowy:** Jeśli oczekujesz JSON, YAML, konkretnej struktury kodu, a tego nie określisz, możesz otrzymać nieprzetwarzalny lub nieużyteczny wynik.
-   **Brak testowania promptów:** Niezakładanie, że pierwszy prompt jest idealny. Pomijanie iteracyjnego procesu i akceptowanie pierwszej sugestii Copilota bez krytycznej oceny może prowadzić do wprowadzenia błędów lub nieoptymalnego kodu.
-   **Zbytnie zaufanie do Copilota:** Copilot jest narzędziem wspomagającym, a nie zastępującym programistę. Zawsze weryfikuj generowany kod, zwłaszcza pod kątem poprawności, bezpieczeństwa i wydajności. Możliwe są "halucynacje" lub generowanie kodu, który wygląda poprawnie, ale zawiera subtelne błędy.
-   **Brak aktualizacji kontekstu:** Jeśli zmienisz kod, ale nie zmienisz promptu, Copilot będzie nadal opierał się na starym kontekście, co może prowadzić do nieaktualnych lub błędnych sugestii.

## 🔗 Dodatkowe Zasoby
-   [Oficjalna dokumentacja GitHub Copilot](https://docs.github.com/en/copilot)
-   [Przewodnik po Inżynierii Promptów dla Copilota](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat/getting-started-with-github-copilot-chat#prompting-github-copilot-for-better-results)
-   [Blog OpenAI o inżynierii promptów](https://openai.com/blog/prompt-engineering)
-   [Repozytorium spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic)

---

*Ten dokument został wygenerowany automatycznie w ramach szkolenia z GitHub Copilot. Treść może wymagać weryfikacji i dostosowania.*