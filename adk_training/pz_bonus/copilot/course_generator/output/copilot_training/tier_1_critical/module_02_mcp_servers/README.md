# MCP Servers - Rozszerzanie Możliwości Copilot

## 🎯 Cele Szkolenia
- Zrozumienie roli i architektury MCP Servers w ekosystemie GitHub Copilot.
- Nabycie umiejętności instalacji, konfiguracji i debugowania istniejących serwerów MCP.
- Opanowanie tworzenia niestandardowych (custom) MCP Servers, integrujących Copilot z zewnętrznymi systemami i logiką biznesową.
- Identyfikacja i implementacja praktycznych zastosowań MCP dla złożonych projektów, takich jak spring-petclinic.
- Poznanie najlepszych praktyk i typowych pułapek związanych z rozwojem i utrzymaniem MCP Servers.

## 📚 Teoria

### Co to są MCP Servers i do czego służą?
GitHub Copilot Chat, będący zaawansowanym narzędziem wspomagającym programistów, opiera się na dużych modelach językowych (LLMs). Aby jednak LLMy mogły być użyteczne w kontekście specyficznych, wewnętrznych danych organizacji lub zintegrowane z niestandardowymi narzędziami, potrzebne jest mechanizm rozszerzający ich możliwości. Tutaj z pomocą przychodzą **Microsoft Copilot Providers (MCP Servers)**, które są zewnętrznymi usługami działającymi jako pomost między Copilot Chat a niestandardowymi źródłami danych, logiką biznesową lub systemami zewnętrznymi.

**Kluczowe zastosowania MCP Servers:**
1.  **Dostęp do wewnętrznych baz wiedzy:** Pozwalają Copilotowi odwoływać się do dokumentacji wewnętrznej, baz danych, FAQów specyficznych dla firmy.
2.  **Integracja z systemami biznesowymi:** Umożliwiają Copilotowi interakcję z systemami takimi jak Jira, ServiceNow, wewnętrzne narzędzia CI/CD, systemy zarządzania zasobami (ERP) itp.
3.  **Wykonywanie niestandardowej logiki:** Copilot może wywoływać specyficzne funkcje lub skrypty, które wykonują operacje, np. generowanie raportów, uruchamianie testów, modyfikowanie konfiguracji, czy analizowanie kodu w sposób zdefiniowany przez organizację.
4.  **Udostępnianie kontekstu aplikacyjnego:** MCP może dostarczyć Copilotowi dodatkowy kontekst z otwartego projektu (np. `spring-petclinic`), np. struktury klas, zależności, fragmenty kodu, co zwiększa trafność generowanych odpowiedzi.
5.  **Bezpieczne i kontrolowane rozszerzanie:** Pozwalają na rozszerzanie Copilota w sposób kontrolowany i zgodny z polityką bezpieczeństwa organizacji, ponieważ to MCP Server decyduje, jakie dane są udostępniane i jakie operacje są wykonywane.

### Architektura i zasady działania
Architektura MCP Servers opiera się na zasadzie komunikacji klient-serwer. Klientem jest tutaj GitHub Copilot Chat (lub inne komponenty Copilota w VS Code), a serwerem jest Twoja niestandardowa usługa MCP. Komunikacja odbywa się zazwyczaj poprzez protokół HTTP/HTTPS.

**Główne komponenty:**
*   **Copilot Chat Client (VS Code Extension):** Wysyła zapytania do Copilot Chat. Jeśli zapytanie wymaga dostępu do zasobów zewnętrznych lub niestandardowej logiki, Copilot może przekierować je do skonfigurowanego MCP Servera.
*   **Copilot Service (Backend Microsoft):** Agreguje zapytania, przetwarza je za pomocą LLMs, a w razie potrzeby, deleguje do MCP Servers.
*   **MCP Server (Twoja usługa):** Odbiera żądania od Copilot Service, przetwarza je, wykonuje niestandardowe operacje (np. zapytania do bazy danych, wywołania API zewnętrznych systemów) i zwraca odpowiedź do Copilot Service.

**Zasady działania:**
1.  **Zapytanie użytkownika:** Użytkownik zadaje pytanie w Copilot Chat, np. "Stwórz nowy task w Jira dotyczący błędu w OwnerController.java w spring-petclinic".
2.  **Analiza przez Copilot Service:** Copilot Service analizuje intencję użytkownika i identyfikuje, że pytanie wymaga interakcji z systemem Jira, co z kolei wymaga MCP Servera.
3.  **Wywołanie MCP Servera:** Copilot Service wysyła żądanie do skonfigurowanego MCP Servera, przekazując mu odpowiedni kontekst (np. fragment kodu, nazwę pliku, intencję). Żądanie to zazwyczaj ma specyficzny format (np. JSON), który MCP Server potrafi zinterpretować.
4.  **Przetwarzanie przez MCP Server:** MCP Server odbiera żądanie, uwierzytelnia je (jeśli wymagane), przetwarza (np. używa API Jira do stworzenia taska) i generuje odpowiedź.
5.  **Odpowiedź do Copilot Service:** MCP Server zwraca odpowiedź do Copilot Service, informując o wyniku operacji (np. "Task został utworzony: JIRA-123").
6.  **Wyświetlenie użytkownikowi:** Copilot Chat wyświetla użytkownikowi odpowiedź otrzymaną od MCP Servera.

### Scenariusze użycia w projektach
MCP Servers otwierają drzwi do niezliczonych możliwości integracji i automatyzacji w projektach deweloperskich. Oto kilka przykładów, z naciskiem na kontekst `spring-petclinic`:

*   **Analiza kodu i rekomendacje:** MCP może być zintegrowany z wewnętrznym narzędziem do statycznej analizy kodu. Gdy deweloper zapyta Copilota o poprawę wydajności w `OwnerController.java` ze `spring-petclinic`, MCP może wywołać to narzędzie, przeanalizować plik i zwrócić konkretne rekomendacje, np. "Zoptymalizuj zapytanie SQL w metodzie findOwners()."
*   **Zarządzanie zadaniami (Jira/Azure DevOps):** Jak w przykładzie powyżej, Copilot może tworzyć, aktualizować lub pobierać informacje o zadaniach deweloperskich bezpośrednio z chatu. Na przykład, "Pokaż mi otwarte błędy związane z modułem Vet w `spring-petclinic`" lub "Dodaj nowe zadanie 'Zaimplementuj walidację dla pola numer telefonu właściciela' w Jira, przypisz do mnie i ustaw priorytet na Wysoki".
*   **Dostęp do dokumentacji wewnętrznej:** Jeśli `spring-petclinic` ma specyficzną, wewnętrzną dokumentację projektową (np. diagramy architektury, specyfikacje API), MCP może umożliwić Copilotowi przeszukiwanie tej dokumentacji i odpowiadanie na pytania, np. "Jaka jest strategia obsługi błędów w warstwie REST API dla `spring-petclinic`?".
*   **Wywoływanie narzędzi CI/CD:** Copilot może wywoływać akcje w potokach CI/CD. "Uruchom testy jednostkowe dla OwnerService w `spring-petclinic`" lub "Wdróż najnowszą wersję `spring-petclinic` na środowisko testowe".
*   **Generowanie raportów i metryk:** MCP może integrować się z narzędziami do monitorowania i raportowania. Deweloper mógłby zapytać: "Pokaż mi raport ze zużycia pamięci przez instancję `spring-petclinic` na środowisku produkcyjnym z ostatniej godziny".
*   **Uczenie maszynowe i analiza danych:** MCP może służyć do wywoływania niestandardowych modeli ML, np. do przewidywania czasu potrzebnego na implementację nowej funkcji w `spring-petclinic` lub sugerowania optymalizacji kodu na podstawie historycznych danych. Np. "Przewidź złożoność implementacji asynchronicznego zapisu logów w `spring-petclinic`".

## 💡 Przykłady Użycia

### Przykład 1: Konfiguracja VS Code do połączenia z MCP
Aby Copilot mógł komunikować się z lokalnym lub zdalnym MCP Serverem, należy odpowiednio skonfigurować VS Code. Używamy do tego pliku `settings.json`.

Załóżmy, że uruchomiliśmy lokalny MCP Server pod adresem `http://localhost:3000`. Aby Copilot wiedział, gdzie szukać naszego serwera, dodajemy następującą konfigurację:

```json
{
  "github.copilot.advanced": {
    "debug.overrideCopilotProviderUrls": {
      "mcp": "http://localhost:3000"
    }
  },
  "github.copilot.internal.featureFlags": {
    "provider.mcp.enabled": true
  }
}
```

**Wyjaśnienie:**
*   `github.copilot.advanced.debug.overrideCopilotProviderUrls.mcp`: To jest klucz, który pozwala nadpisać domyślny URL dla providera `mcp`. Zamiast domyślnego serwisu Copilota, zapytania skierowane do `mcp` będą wysyłane na `http://localhost:3000`.
*   `github.copilot.internal.featureFlags.provider.mcp.enabled`: Upewnia się, że funkcja dostawcy MCP jest włączona.

Po dodaniu tych wpisów do `settings.json` (możesz edytować globalny `settings.json` lub plik `.vscode/settings.json` dla konkretnego projektu, np. `spring-petclinic`), zrestartuj VS Code, aby zmiany zostały załadowane. Teraz, gdy Copilot Chat otrzyma zapytanie wymagające interakcji z MCP, skieruje je pod skonfigurowany adres.

### Przykład 2: Prosty Custom MCP Server (Node.js)
Stwórzmy bardzo prosty MCP Server, który odpowiada na podstawowe zapytania. Ten przykład użyje Node.js z frameworkiem Express. Serwer będzie po prostu zwracał wiadomości na podstawie prostego promptu.

**Plik: `server.js`**
```javascript
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/v1/mcp/prompt', (req, res) => {
  console.log('Received Copilot MCP request:', JSON.stringify(req.body, null, 2));

  const prompt = req.body.messages && req.body.messages.length > 0 
               ? req.body.messages[req.body.messages.length - 1].content 
               : '';
  
  let responseContent = 'Witaj z Custom MCP! Nie rozumiem Twojego zapytania.';

  if (prompt.toLowerCase().includes('hello')) {
    responseContent = 'Hello from your custom MCP Server!';
  } else if (prompt.toLowerCase().includes('petclinic')) {
    responseContent = 'Repozytorium spring-petclinic to świetny przykład aplikacji Spring Boot!';
  } else if (prompt.toLowerCase().includes('time')) {
    responseContent = `Aktualny czas na serwerze to: ${new Date().toLocaleTimeString()}.`;
  }

  res.json({
    response: {
      choices: [
        {
          message: {
            content: responseContent,
            role: 'assistant',
          },
        },
      ],
    },
  });
});

app.listen(port, () => {
  console.log(`Custom MCP Server listening at http://localhost:${port}`);
});
```

**Plik: `package.json`**
```json
{
  "name": "simple-mcp-server",
  "version": "1.0.0",
  "description": "A simple custom MCP server for GitHub Copilot",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "body-parser": "^1.20.2"
  },
  "author": "Your Name",
  "license": "ISC"
}
```

**Jak uruchomić:**
1.  Zainstaluj Node.js i npm, jeśli jeszcze ich nie masz.
2.  W folderze z plikami `server.js` i `package.json` uruchom `npm install`.
3.  Następnie uruchom `npm start`.
4.  Skonfiguruj VS Code tak, jak w Przykładzie 1, wskazując `http://localhost:3000` jako URL MCP.

Teraz, gdy w Copilot Chat zapytasz "Hello MCP", "Tell me about petclinic" lub "What time is it?", Copilot powinien zwrócić odpowiedź z Twojego customowego serwera.

### Przykład 3: Integracja z wewnętrznymi narzędziami (koncept)
Wyobraź sobie, że chcesz, aby Copilot mógł automatycznie tworzyć nowe gałęzie Git dla nowych zadań. Możesz stworzyć MCP Server, który integruje się z Twoim repozytorium Git (np. przez API GitHub) i systemem zarządzania zadaniami (np. Jira).

**Scenariusz:** Użytkownik prosi: "Stwórz nową gałąź feature/implement-owner-validation dla zadania JIRA-456 w spring-petclinic".

**Jak działałby MCP:**
1.  MCP Server odbiera zapytanie od Copilota.
2.  Analizuje prompt, wyodrębniając nazwę gałęzi (`feature/implement-owner-validation`) i ID zadania Jira (`JIRA-456`).
3.  Wywołuje API Git (np. GitHub API) w celu stworzenia nowej gałęzi w repozytorium `spring-petclinic`.
4.  Opcjonalnie: Wywołuje API Jira w celu zaktualizowania zadania JIRA-456 o informację, że nowa gałąź została utworzona.
5.  Zwraca potwierdzenie do Copilota: "Gałąź `feature/implement-owner-validation` została utworzona dla JIRA-456." 

Ten przykład wymagałby bardziej zaawansowanej logiki po stronie MCP Servera, obejmującej autoryzację, obsługę błędów i bardziej złożoną analizę promptów. Kluczowe jest to, że MCP działa jako warstwa pośrednicząca, tłumacząca intencje Copilota na konkretne akcje w Twoich wewnętrznych systemach.

## ✅ Best Practices

1.  **Zdefiniuj jasne API dla MCP:** Projektując Custom MCP, traktuj go jak każde inne API. Zdefiniuj jasne punkty końcowe, formaty żądań i odpowiedzi. Użyj schematów JSON do walidacji danych wejściowych.
2.  **Modułowa architektura:** Dziel logikę MCP na mniejsze, niezależne moduły. Ułatwia to testowanie, utrzymanie i skalowanie. Na przykład, oddziel logikę interakcji z Jira od logiki dostępu do baz danych.
3.  **Bezpieczeństwo i autoryzacja:** Implementuj solidne mechanizmy uwierzytelniania i autoryzacji dla swojego MCP Servera. Upewnij się, że MCP ma dostęp tylko do niezbędnych zasobów i działa w kontekście odpowiednich uprawnień. Rozważ użycie tokenów API, OAuth lub innych bezpiecznych metod.
4.  **Obsługa błędów i logowanie:** Każdy MCP Server powinien zawierać kompleksową obsługę błędów i mechanizmy logowania. Loguj wszystkie żądania, odpowiedzi i błędy, co jest kluczowe dla debugowania i monitorowania działania serwera. Zapewnij, że komunikaty o błędach zwracane do Copilota są czytelne i pomocne dla użytkownika.
5.  **Idempotencja operacji:** Jeśli Twój MCP wykonuje operacje zmieniające stan w zewnętrznych systemach, rozważ ich idempotencję. Oznacza to, że wielokrotne wywołanie tej samej operacji z tymi samymi parametrami powinno dawać ten sam wynik, nie powodując niepożądanych efektów ubocznych.
6.  **Walidacja wejścia:** Zawsze waliduj dane wejściowe otrzymane od Copilota. Nigdy nie ufaj danym pochodzącym od klienta. Zapobiega to atakom typu injection i nieoczekiwanym zachowaniom.
7.  **Optymalizacja wydajności:** MCP Servers powinny działać szybko, aby nie opóźniać odpowiedzi Copilota. Optymalizuj zapytania do baz danych, wywołania API i przetwarzanie logiki. Rozważ buforowanie (caching) dla często odpytywanych danych.
8.  **Wersjonowanie:** Wersjonuj swoje MCP Servers i ich API. Umożliwi to ewolucję serwera bez łamania kompatybilności wstecznej z istniejącymi integracjami Copilota.
9.  **Dokumentacja:** Twórz szczegółową dokumentację dla każdego Custom MCP Servera. Powinna ona zawierać instrukcje instalacji, konfiguracji, schematy API, przykłady użycia i informacje o sposobie interakcji z Copilotem.
10. **Testy jednostkowe i integracyjne:** Pisanie testów jest kluczowe dla zapewnienia niezawodności MCP Servera. Testy jednostkowe powinny pokrywać logikę biznesową, a testy integracyjne – interakcje z zewnętrznymi API i samym Copilotem.
11. **Minimalizacja kontekstu:** Przekazuj do MCP tylko niezbędny kontekst z Copilota. Zbyt duża ilość danych może spowolnić komunikację i zwiększyć złożoność parsowania po stronie serwera.
12. **Zarządzanie stanem:** Jeśli Twój MCP wymaga utrzymywania stanu, rozważ użycie zewnętrznych, skalowalnych rozwiązań do zarządzania stanem, takich jak bazy danych NoSQL lub serwisy cache'ujące.

## ⚠️ Common Pitfalls

1.  **Błędna konfiguracja endpointu MCP w VS Code:** Często zdarza się, że URL w `settings.json` jest nieprawidłowy, zawiera literówkę lub nie wskazuje na poprawny port, na którym działa MCP Server. Skutkuje to brakiem komunikacji między Copilotem a MCP.
2.  **Problemy z autoryzacją:** Brak prawidłowych uprawnień lub niepoprawne przekazanie tokenów API do zewnętrznych systemów (np. Jira, GitHub) przez MCP Server. Copilot może próbować wywołać akcję, ale MCP nie będzie miał autoryzacji do jej wykonania.
3.  **Nadmierne opóźnienia MCP Servera:** Jeśli MCP Server wykonuje złożone operacje, które trwają zbyt długo, Copilot może timeout'ować, zanim otrzyma odpowiedź. Może to prowadzić do frustracji użytkowników i postrzegania Copilota jako "wolnego". Optymalizuj logikę i rozważ asynchroniczne operacje dla długotrwałych zadań.
4.  **Niewystarczająca walidacja wejścia:** Przyjmowanie dowolnego tekstu z promptu Copilota bez odpowiedniej walidacji po stronie MCP Servera. Może to prowadzić do błędów, nieoczekiwanych zachowań lub nawet luk bezpieczeństwa (np. SQL Injection, Code Injection, jeśli MCP bezpośrednio wykonuje fragmenty kodu).
5.  **Brak obsługi błędów w MCP:** Niespójne lub brakujące mechanizmy obsługi błędów w logice MCP Servera. Gdy wystąpi błąd w zewnętrznym API lub w wewnętrznej logice, MCP zwraca ogólny błąd lub nic, zamiast informować Copilota o problemie w czytelny sposób.
6.  **Zbyt złożona logika w MCP:** Próba umieszczenia całej logiki biznesowej bezpośrednio w MCP Serverze, zamiast delegowania jej do istniejących mikroserwisów lub bibliotek. MCP powinien być lekką warstwą integracyjną, a nie monolitowym rozwiązaniem.
7.  **Problemy z kontekstem:** Niewłaściwe przekazywanie lub interpretowanie kontekstu z Copilota (np. aktualnie otwartego pliku, fragmentu kodu). Może to prowadzić do odpowiedzi niezwiązanych z intencją użytkownika.
8.  **Zależności i środowisko uruchomieniowe:** Problemy z zależnościami bibliotek, wersjami języka programowania lub środowiskiem uruchomieniowym MCP Servera. Należy zadbać o spójne i dobrze zdefiniowane środowisko (np. Docker).
9.  **Skalowalność:** Brak przewidywania skalowalności MCP Servera. Jeśli wielu użytkowników będzie jednocześnie korzystać z Copilota i wywoływać Twój MCP, serwer musi być w stanie obsłużyć ten ruch.
10. **Brak odpowiedniego logowania/monitorowania:** Trudności w diagnozowaniu problemów z MCP Serverem z powodu braku szczegółowych logów lub narzędzi do monitorowania. Warto zintegrować MCP z centralnym systemem logowania i monitorowania.
11. **Brak idempotencji:** Wykonywanie operacji zmieniających stan, które nie są idempotentne. Powtórne wywołanie przez Copilota (np. z powodu opóźnienia sieci) może spowodować wielokrotne utworzenie zasobu (np. kilku zadań Jira).
12. **Błędy w parsowaniu żądań Copilota:** Format żądań wysyłanych przez Copilota może być złożony. Błędy w parsowaniu struktury JSON (np. odwoływanie się do nieistniejących pól) mogą uniemożliwić MCP przetworzenie zapytania.

## 🔗 Dodatkowe Zasoby
- [Oficjalna dokumentacja GitHub Copilot Providers](https://docs.github.com/en/copilot/github-copilot-chat/creating-custom-providers-for-github-copilot-chat) (język angielski)
- [Przykładowy projekt GitHub Copilot Provider (repozytorium)](https://github.com/microsoft/vscode-copilot-sample-provider) (język angielski)
- [Artykuł: Extend GitHub Copilot with Custom Logic](https://devblogs.microsoft.com/visualstudio/extend-github-copilot-with-custom-logic/) (język angielski)
- Repozytorium `spring-petclinic`: `https://github.com/spring-projects/spring-petclinic`
