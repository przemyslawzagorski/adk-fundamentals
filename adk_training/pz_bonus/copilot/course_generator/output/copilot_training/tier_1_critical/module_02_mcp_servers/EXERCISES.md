# Ćwiczenia: MCP Servers - Rozszerzanie Copilot

## Ćwiczenie 1: Zrozumienie podstawowych interakcji z Copilot Chat

**Cel:** Zapoznanie się z możliwościami Copilot Chat w kontekście zadawania pytań ogólnych o strukturę projektu `spring-petclinic`, co stanowi punkt wyjścia do zrozumienia, jak MCP Servers mogą wzbogacić ten kontekst.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Chcesz zrozumieć, jak Copilot Chat radzi sobie z pytaniami dotyczącymi struktury kodu bez aktywnego MCP Servera.

**Kroki:**
1.  Otwórz repozytorium `spring-petclinic` w VS Code.
2.  Otwórz Copilot Chat (ikonka dymka w lewym panelu VS Code).
3.  Zadaj Copilotowi pytania, np.:
    *   `Jaka jest struktura katalogów w repozytorium spring-petclinic?`
    *   `W jakich plikach zdefiniowany jest OwnerController w spring-petclinic?`
    *   `Jakie są główne encje modelu danych w spring-petclinic?`

**Oczekiwany rezultat:**
Copilot Chat powinien odpowiedzieć na Twoje pytania, korzystając ze swojej wiedzy ogólnej oraz kontekstu otwartego projektu. Zwróć uwagę, jak ogólne lub szczegółowe są odpowiedzi, oraz czy Copilot potrafi wskazać konkretne pliki/linie kodu w `spring-petclinic`.

**Wskazówki:**
- Upewnij się, że rozszerzenie GitHub Copilot Chat jest zainstalowane i aktywne.
- Eksperymentuj z różnymi sformułowaniami pytań.

---

## Ćwiczenie 2: Identyfikacja potencjalnych zastosowań MCP dla spring-petclinic

**Cel:** Przemyślenie, w jaki sposób Custom MCP Servers mogłyby wzbogacić doświadczenie deweloperskie w projekcie `spring-petclinic`, wychodząc poza standardowe możliwości Copilota.

**Kontekst:** Mając świadomość architektury `spring-petclinic` i problemów, które mogą pojawić się podczas jego rozwoju, zastanów się, jakie specyficzne potrzeby mogłyby zostać zaspokojone przez niestandardowe rozszerzenia Copilota.

**Kroki:**
1.  Przejrzyj kod `spring-petclinic`, zwracając uwagę na moduły (Owner, Vet, Pet, Visit), warstwy (web, service, repository) i używane technologie (Spring, Hibernate, bazy danych).
2.  Zastanów się nad typowymi zadaniami deweloperskimi lub problemami, które napotykasz w tego typu projekcie (np. tworzenie nowych encji, refaktoryzacja, debugowanie, generowanie testów, zarządzanie dokumentacją).
3.  Zaproponuj 3-5 konkretnych scenariuszy, w których Custom MCP Server mógłby dostarczyć wartości dodanej dla `spring-petclinic`. Opisz krótko, co taki MCP by robił i jaką korzyść by przynosił.
    *Przykład: MCP do walidacji reguł biznesowych: Na podstawie konfiguracji lub adnotacji w kodzie, MCP mógłby informować, czy nowa implementacja OwnerService jest zgodna z wewnętrznymi regułami walidacji.* 

**Oczekiwany rezultat:**
Lista 3-5 pomysłów na MCP Servers, które bezpośrednio wspierałyby rozwój i utrzymanie `spring-petclinic`, z krótkim opisem ich funkcjonalności i uzasadnieniem.

**Wskazówki:**
- Pomyśl o integracjach z narzędziami wewnętrznymi, bazami danych wiedzy, systemami CI/CD, czy systemami do zarządzania zadaniami.
- Jakie powtarzalne zadania mógłby zautomatyzować Copilot, gdyby miał dostęp do Twojej logiki biznesowej?

---

## Ćwiczenie 3: Instalacja przykładowego MCP Servera (Symulacja)

**Cel:** Zrozumienie ogólnych kroków instalacji i uruchomienia prostego MCP Servera, nawet jeśli nie będziesz go faktycznie instalować w tym momencie.

**Kontekst:** W poprzednim `README.md` przedstawiono przykład prostego MCP Servera w Node.js. To ćwiczenie ma na celu symulację procesu jego uruchomienia.

**Kroki:**
1.  Przygotuj środowisko: Upewnij się, że masz zainstalowane Node.js i npm (lub inny menedżer pakietów dla wybranego języka).
2.  Utwórz nowy katalog np. `my-first-mcp`.
3.  Stwórz plik `package.json` z zależnościami (np. `express`, `body-parser`) i plik `server.js` z kodem serwera, tak jak w przykładzie z `README.md`.
4.  W terminalu, będąc w katalogu `my-first-mcp`, wykonaj komendę `npm install` (lub odpowiednik dla Twojego języka/ekosystemu).
5.  Następnie uruchom serwer komendą `npm start`.
6.  Zaobserwuj komunikat o uruchomieniu serwera (np. `Custom MCP Server listening at http://localhost:3000`).

**Oczekiwany rezultat:**
Serwer MCP powinien uruchomić się poprawnie, wyświetlając komunikat o nasłuchiwaniu na określonym porcie. Nie ma potrzeby interakcji z Copilotem na tym etapie, celem jest poprawne uruchomienie serwera.

**Wskazówki:**
- Zwróć uwagę na komunikaty błędów podczas instalacji zależności, jeśli takie wystąpią.
- Upewnij się, że port 3000 (lub inny wybrany) nie jest zajęty przez inną aplikację.

---

## Ćwiczenie 4: Konfiguracja VS Code do połączenia z MCP

**Cel:** Skonfigurowanie VS Code, aby Copilot Chat mógł komunikować się z Twoim lokalnie uruchomionym MCP Serverem.

**Kontekst:** Uruchomiłeś prosty MCP Server, który nasłuchuje na porcie 3000. Teraz musisz powiedzieć VS Code, gdzie szukać tego serwera.

**Kroki:**
1.  Otwórz `settings.json` w VS Code. Możesz to zrobić poprzez `File > Preferences > Settings` (lub `Code > Preferences > Settings` na macOS), następnie wyszukaj `settings.json` i wybierz `Edit in settings.json`.
2.  Dodaj lub zmodyfikuj następujące wpisy w pliku `settings.json`:
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
3.  Zapisz `settings.json`.
4.  Zrestartuj VS Code, aby upewnić się, że zmiany zostały zastosowane.

**Oczekiwany rezultat:**
VS Code powinien zostać zrestartowany, a Copilot Chat powinien być teraz skonfigurowany do używania Twojego lokalnego MCP Servera. Nie będzie widocznych zmian w interfejsie, ale wewnętrznie Copilot będzie próbował kierować zapytania do Twojego serwera.

**Wskazówki:**
- Upewnij się, że składnia JSON jest poprawna. Mały błąd może uniemożliwić załadowanie ustawień.
- Jeśli masz plik `.vscode/settings.json` w katalogu `spring-petclinic`, możesz dodać te ustawienia tam, aby były specyficzne dla projektu.

---

## Ćwiczenie 5: Testowanie połączenia z lokalnym MCP

**Cel:** Weryfikacja, czy Copilot Chat poprawnie komunikuje się z Twoim lokalnym MCP Serverem.

**Kontekst:** Po skonfigurowaniu VS Code, teraz możesz sprawdzić, czy prosty MCP Server odpowiada na zapytania, które wcześniej zdefiniowałeś.

**Kroki:**
1.  Upewnij się, że Twój prosty MCP Server (z Ćwiczenia 3) jest uruchomiony i nasłuchuje na porcie 3000.
2.  Otwórz Copilot Chat w VS Code.
3.  Zadaj Copilotowi pytania, które powinny być obsłużone przez Twój MCP:
    *   `Hello MCP`
    *   `Tell me about petclinic` (jeśli Twój MCP zawiera logikę dla tego promptu)
    *   `What time is it?` (jeśli Twój MCP zawiera logikę dla tego promptu)

**Oczekiwany rezultat:**
Copilot Chat powinien wyświetlić odpowiedzi wygenerowane przez Twój Custom MCP Server, np. `Hello from your custom MCP Server!` lub `Repozytorium spring-petclinic to świetny przykład aplikacji Spring Boot!`. Powinieneś także zobaczyć logi żądań na konsoli, w której uruchomiony jest Twój MCP Server.

**Wskazówki:**
- Jeśli Copilot nie odpowiada zgodnie z oczekiwaniami, sprawdź logi MCP Servera, aby zobaczyć, czy żądanie w ogóle dotarło.
- Sprawdź również okno Output w VS Code (sekcja GitHub Copilot), tam mogą pojawić się komunikaty o błędach komunikacji.

---

## Ćwiczenie 6: Debugowanie problemów z połączeniem MCP

**Cel:** Nauka identyfikacji i rozwiązywania typowych problemów związanych z komunikacją między Copilotem a MCP Serverem.

**Kontekst:** Czasem połączenie nie działa idealnie. To ćwiczenie symuluje błąd i uczy, jak go zdiagnozować.

**Kroki:**
1.  **Zatrzymaj MCP Server:** Zamknij terminal, w którym uruchomiony jest Twój MCP Server.
2.  W Copilot Chat zadaj jedno z pytań z Ćwiczenia 5 (np. `Hello MCP`).
3.  Zaobserwuj odpowiedź Copilota (lub jej brak). Powinien on nie być w stanie połączyć się z serwerem, lub zwrócić generyczną odpowiedź, że nie rozumie zapytania.
4.  **Zmień port w `settings.json`:** Zmień adres URL w `settings.json` na nieprawidłowy, np. `"mcp": "http://localhost:3001"`.
5.  Zrestartuj VS Code i ponownie zadaj pytanie w Copilot Chat.
6.  **Analiza logów:** Otwórz panel `Output` w VS Code (`View > Output`) i wybierz `GitHub Copilot` oraz `GitHub Copilot Chat` z rozwijanej listy. Szukaj komunikatów o błędach połączenia, timeoutach lub problemach z dostawcami.
7.  Napraw błędy: Przywróć poprawny port w `settings.json` i uruchom ponownie MCP Server.

**Oczekiwany rezultat:**
Powinieneś być w stanie wywołać błędy komunikacji, zdiagnozować je za pomocą logów w VS Code i terminalu MCP Servera, a następnie poprawnie przywrócić działające połączenie.

**Wskazówki:**
- Zawsze sprawdzaj zarówno logi VS Code, jak i logi samego MCP Servera.
- Upewnij się, że firewalle nie blokują komunikacji na używanym porcie.

---

## Ćwiczenie 7: Szkielet prostego Custom MCP Servera (Python)

**Cel:** Stworzenie podstawowego MCP Servera w Pythonie, który potrafi odbierać żądania od Copilota i zwracać prostą odpowiedź.

**Kontekst:** Chcesz rozszerzyć Copilot o własną logikę napisaną w Pythonie. To ćwiczenie stworzy minimalistyczny serwer.

**Kroki:**
1.  Utwórz nowy katalog, np. `python-mcp`.
2.  Stwórz plik `server.py` z następującym kodem:
    ```python
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import json

    class SimpleMCPHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path == '/v1/mcp/prompt':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_body = json.loads(post_data.decode('utf-8'))
                
                print(f"Received Copilot MCP request: {json.dumps(request_body, indent=2)}")

                prompt_content = ""
                if 'messages' in request_body and len(request_body['messages']) > 0:
                    last_message = request_body['messages'][-1]
                    if 'content' in last_message:
                        prompt_content = last_message['content']
                
                response_content = 'Witaj z Custom MCP (Python)! Nie rozumiem Twojego zapytania.'
                if 'hello' in prompt_content.lower():
                    response_content = 'Hello from your Python MCP Server!'
                elif 'petclinic' in prompt_content.lower():
                    response_content = 'Python MCP wie o spring-petclinic!'
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                response_payload = {
                    'response': {
                        'choices': [
                            {
                                'message': {
                                    'content': response_content,
                                    'role': 'assistant'
                                }
                            }
                        ]
                    }
                }
                self.wfile.write(json.dumps(response_payload).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')

    def run(server_class=HTTPServer, handler_class=SimpleMCPHandler, port=3000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print(f'Starting Python MCP Server on port {port}...')
        httpd.serve_forever()

    if __name__ == '__main__':
        run()
    ```
3.  Uruchom serwer w terminalu: `python server.py`.
4.  Skonfiguruj VS Code tak, jak w Ćwiczeniu 4, aby wskazywał na `http://localhost:3000`.
5.  Przetestuj połączenie w Copilot Chat, zadając pytania `Hello MCP` lub `Tell me about petclinic`.

**Oczekiwany rezultat:**
Twój Pythonowy MCP Server powinien poprawnie odbierać żądania i odpowiadać na nie, a Copilot Chat powinien wyświetlać te odpowiedzi. Zobaczysz logi żądań w terminalu Pythona.

**Wskazówki:**
- Upewnij się, że nie masz innego serwera działającego na porcie 3000.
- Ten prosty serwer nie ma zależności zewnętrznych poza standardową biblioteką Pythona.

---

## Ćwiczenie 8: Rozbudowa Custom MCP o podstawową logikę (Kontekst Pliku)

**Cel:** Zaimplementowanie w Custom MCP Serverze (Node.js lub Python) logiki, która reaguje na kontekst aktualnie otwartego pliku w `spring-petclinic`.

**Kontekst:** Chcesz, aby Copilot mógł odpowiadać na pytania dotyczące konkretnych klas w `spring-petclinic`, np. w kontekście `OwnerController.java`.

**Kroki:**
1.  Uruchom repozytorium `spring-petclinic` w VS Code.
2.  Modyfikuj swój Custom MCP Server (np. Node.js z `server.js`):
    *   Żądania od Copilota zawierają `currentFile` w `editor` obiekcie, który dostarcza ścieżkę do aktywnego pliku.
    *   Dodaj logikę do swojego serwera, która sprawdza, czy nazwa pliku zawiera `OwnerController.java`.
    *   Jeśli tak, a prompt zawiera frazę `Owner`, zwróć specyficzną odpowiedź, np. `W kontekście OwnerController.java, klasa Owner jest kluczowa dla zarządzania danymi właścicieli.`
    *   W przeciwnym razie, zwróć ogólną odpowiedź.
    *Przykład rozszerzenia logiki w Node.js:
    ```javascript
    // ... w funkcji app.post('/v1/mcp/prompt', ...) ...
    const editorContext = req.body.editor;
    const currentFilePath = editorContext && editorContext.currentFile ? editorContext.currentFile : null;

    // ... istniejąca logika parsowania promptu ...

    if (currentFilePath && currentFilePath.includes('OwnerController.java') && prompt.toLowerCase().includes('owner')) {
      responseContent = 'W kontekście OwnerController.java, klasa Owner jest kluczowa dla zarządzania danymi właścicieli i ich zwierząt.';
    } else if (prompt.toLowerCase().includes('vet')) {
      responseContent = 'Skupiam się na weterynarzach i ich specjalnościach.';
    }
    // ... reszta logiki ...
    ```

3.  Zrestartuj swój MCP Server.
4.  Otwórz plik `OwnerController.java` w `spring-petclinic`.
5.  W Copilot Chat zadaj pytanie, np. `Powiedz mi o owner w tym pliku.`
6.  Otwórz inny plik (np. `VetController.java`) i zadaj podobne pytanie, obserwując zmianę odpowiedzi.

**Oczekiwany rezultat:**
MCP Server powinien zwracać odpowiedzi, które są kontekstowe względem aktualnie otwartego pliku w VS Code, demonstrując jego zdolność do reagowania na kontekst projektu.

**Wskazówki:**
- Sprawdź dokładnie strukturę obiektu `request_body`, aby poprawnie odczytać `editor.currentFile`.
- Pamiętaj o uwzględnieniu ścieżek bezwzględnych lub względnych w `currentFile` w zależności od środowiska.

---

## Ćwiczenie 9: Integracja MCP z API (Mock Jira)

**Cel:** Stworzenie Custom MCP Servera, który symuluje integrację z zewnętrznym API (w tym przypadku Jira) do tworzenia zadań.

**Kontekst:** Chcesz, aby deweloperzy mogli tworzyć zadania w Jira bezpośrednio z Copilot Chat, np. zgłaszając błędy w `spring-petclinic`. Użyjesz prostego mocka zamiast prawdziwego API Jira.

**Kroki:**
1.  Modyfikuj swój Custom MCP Server (Node.js lub Python).
2.  Dodaj logikę, która rozpozna prompty typu: `Stwórz zadanie Jira dla błędu: [opis błędu] w module [moduł] w spring-petclinic, przypisz do [imię]`. Przykład: `Stwórz zadanie Jira dla błędu: Brak walidacji formularza właściciela w module Owner w spring-petclinic, przypisz do Jan Kowalski`.
3.  Wewnątrz MCP, parsowanie promptu w celu wyodrębnienia opisu błędu, modułu i przypisania.
4.  Zamiast faktycznego wywołania API Jira, loguj te informacje do konsoli i symuluj utworzenie zadania, zwracając do Copilota komunikat, np. `Zadanie JIRA-123 zostało utworzone: Brak walidacji formularza właściciela. Przypisano do Jan Kowalski.`

**Oczekiwany rezultat:**
Copilot Chat powinien wyświetlać potwierdzenia utworzenia zadań Jira z informacjami pobranymi z Twojego Custom MCP Servera, demonstrując zdolność do interakcji z mockowanym API.

**Wskazówki:**
- Skup się na precyzyjnym parsowaniu promptu. Możesz użyć prostych wyrażeń regularnych lub metod stringowych.
- Pamiętaj, aby symulować unikalny ID zadania (np. `JIRA-123`, `JIRA-124`).

---

## Ćwiczenie 10: Walidacja wejścia w Custom MCP

**Cel:** Wdrożenie podstawowej walidacji danych wejściowych w Custom MCP Serverze, aby zapewnić, że otrzymuje on kompletne i poprawne informacje przed przetworzeniem żądania.

**Kontekst:** W poprzednim ćwiczeniu tworzyłeś zadania Jira. Co się stanie, jeśli użytkownik nie poda wszystkich wymaganych informacji, np. opisu błędu?

**Kroki:**
1.  Modyfikuj logikę parsowania promptu z Ćwiczenia 9.
2.  Przed próbą "utworzenia" zadania Jira, sprawdź, czy wszystkie niezbędne elementy (opis błędu, moduł, przypisanie) zostały poprawnie wyodrębnione z promptu.
3.  Jeśli brakuje któregoś elementu, zwróć do Copilota błąd, np. `Błąd: Nie mogę utworzyć zadania Jira. Brakuje opisu błędu lub informacji o module. Proszę uzupełnij.`
4.  Przetestuj to, zadając Copilotowi niekompletne prompt, np. `Stwórz zadanie Jira dla błędu: w module Owner.`

**Oczekiwany rezultat:**
Twój MCP Server powinien poprawnie identyfikować brakujące informacje w prompty i zwracać odpowiednie komunikaty o błędach do Copilot Chat.

**Wskazówki:**
- Możesz użyć prostych warunków `if/else` lub słowników do przechowywania wymaganych parametrów.
- Dobre komunikaty o błędach są kluczowe dla użyteczności MCP.

---

## Ćwiczenie 11: Zwracanie bogatszych odpowiedzi z MCP

**Cel:** Naucz się, jak zwracać do Copilot Chat bardziej strukturalne i użyteczne odpowiedzi, które mogą zawierać np. linki, formatowanie Markdown.

**Kontekst:** Wcześniejsze odpowiedzi były prostymi stringami. Teraz chcesz, aby Twój MCP mógł zwracać np. link do utworzonego zadania Jira lub formatowany kod.

**Kroki:**
1.  Modyfikuj logikę zwracania odpowiedzi dla "utworzonego" zadania Jira z Ćwiczenia 9.
2.  Zamiast prostego tekstu, zwróć odpowiedź w formacie Markdown, która zawiera link do mockowego zadania Jira:
    ```markdown
    Zadanie JIRA-123 zostało utworzone: Brak walidacji formularza właściciela.
    Przypisano do: Jan Kowalski.
    [Link do zadania](http://mock-jira.com/browse/JIRA-123)
    ```
3.  Możesz także przetestować zwracanie fragmentów kodu, np. jeśli użytkownik zapyta `Pokaż mi jak wygląda klasa Owner w spring-petclinic` (założenie, że MCP ma dostęp do kodu).
    ```markdown
    ```java
    public class Owner extends Person {
        // ... pola i metody ...
    }
    ```
    ```

**Oczekiwany rezultat:**
Copilot Chat powinien renderować odpowiedzi z Twojego MCP z prawidłowo sformatowanymi linkami i blokami kodu Markdown, co znacznie zwiększy czytelność i użyteczność.

**Wskazówki:**
- Upewnij się, że Twoja odpowiedź JSON jest prawidłowo sformatowana, a pole `content` zawiera odpowiedni Markdown.
- W rzeczywistym scenariuszu, link do Jira byłby dynamicznie generowany.

---

## Ćwiczenie 12: Dokumentacja i Best Practices dla Custom MCP

**Cel:** Podsumowanie najlepszych praktyk i tworzenie prostej dokumentacji dla swojego Custom MCP Servera.

**Kontekst:** Stworzyłeś już kilka wersji MCP. Teraz ważne jest, aby dokumentować swoją pracę i stosować się do najlepszych praktyk, aby ułatwić sobie i innym przyszłą rozbudowę.

**Kroki:**
1.  Stwórz nowy plik `README.md` w katalogu swojego Custom MCP Servera (np. `python-mcp/README.md` lub `my-first-mcp/README.md`).
2.  W tym pliku zawrzyj następujące informacje:
    *   Krótki opis, do czego służy Twój MCP Server (np. `Ten MCP Server integruje Copilot z mockowym API Jira i reaguje na kontekst plików spring-petclinic`).
    *   Instrukcje instalacji i uruchomienia (zależności, komendy).
    *   Przykładowe prompty, które MCP potrafi obsłużyć (np. `Hello MCP`, `Stwórz zadanie Jira dla błędu...`).
    *   Krótki opis, jak konfiguruje się VS Code, aby korzystać z Twojego MCP.
3.  Przejrzyj sekcję Best Practices z głównego `README.md` modułu `module_02_mcp_servers` i zastanów się, które z nich zastosowałeś w swoich ćwiczeniach, a które mógłbyś jeszcze poprawić (np. dodanie logowania, bardziej zaawansowana walidacja).

**Oczekiwany rezultat:**
Posiadanie jasnej i zwięzłej dokumentacji dla Twojego Custom MCP Servera oraz zrozumienie, jak stosować najlepsze praktyki w rozwoju takich rozszerzeń.

**Wskazówki:**
- Dobra dokumentacja jest tak samo ważna, jak dobrze napisany kod.
- Pomyśl o przyszłych użytkownikach Twojego MCP – co musieliby wiedzieć, aby go uruchomić i używać?
