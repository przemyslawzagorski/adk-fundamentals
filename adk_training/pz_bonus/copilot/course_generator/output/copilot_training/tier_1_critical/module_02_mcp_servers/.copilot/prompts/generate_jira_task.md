### Utwórz zadanie Jira

**Opis:**
Copilot, używając skonfigurowanego MCP Servera Jira, proszę utwórz nowe zadanie w Jira. Użyj następującego formatu:

`Stwórz zadanie Jira dla błędu: [opis błędu] w module [moduł spring-petclinic], priorytet [Niski/Średni/Wysoki], przypisz do [imię i nazwisko].`

**Scenariusz użycia:**
Deweloper identyfikuje błąd lub potrzebę implementacji podczas pracy i chce szybko utworzyć zadanie w Jira bez opuszczania VS Code. MCP Server interpretuje ten prompt i wykonuje wywołanie do API Jira.

**Oczekiwany rezultat:**
Potwierdzenie utworzenia zadania Jira wraz z jego identyfikatorem (np. `JIRA-XXXX`) i linkiem, jeśli MCP to wspiera. W przypadku błędu (np. brakujące parametry, problem z autoryzacją), odpowiedni komunikat o błędzie z instrukcjami dla użytkownika.

**Przykład interakcji:**
**Użytkownik:** `/prompt generate_jira_task Stwórz zadanie Jira dla błędu: Brak walidacji adresu email w formularzu Owner w module Owner, priorytet Wysoki, przypisz do Jan Kowalski.`
**Copilot:** `✅ Zadanie JIRA-456 zostało utworzone: Brak walidacji adresu email. Link: [http://jira.firma.com/browse/JIRA-456](http://jira.firma.com/browse/JIRA-456)`