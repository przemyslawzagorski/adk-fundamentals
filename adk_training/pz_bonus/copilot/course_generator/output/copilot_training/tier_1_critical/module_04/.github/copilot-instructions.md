# Instrukcje dla GitHub Copilot w Module "Agent Skills - Rozbudowa Agentów"

Witamy w module poświęconym rozbudowie Agent Skills w GitHub Copilot! Poniższe instrukcje pomogą Ci efektywnie korzystać z Copilota podczas pracy z tymi materiałami.

## 💡 Ogólne Wskazówki
-   **Zawsze dawaj kontekst:** Kiedy zadajesz pytania Copilotowi, staraj się wskazać, nad jakim fragmentem kodu lub plikiem pracujesz.
-   **Bądź precyzyjny:** Im dokładniejsze i jaśniejsze jest Twoje zapytanie, tym lepsze i bardziej trafne będą odpowiedzi Copilota.
-   **Eksperymentuj:** Nie bój się próbować różnych sformułowań pytań i poleceń.
-   **Wykorzystaj Copilot Chat:** Jest to główne narzędzie do interakcji z Agent Skills.

## 🤖 Korzystanie z Niestandardowych Umiejętności (Custom Skills)
W tym module będziesz tworzyć i używać niestandardowych umiejętności agenta.
Aby Copilot mógł wykryć i używać tych umiejętności, upewnij się, że:
1.  Plik `package.json` (zawierający definicje umiejętności w sekcji `copilot.skills`) znajduje się w głównym katalogu projektu `spring-petclinic` lub w innym miejscu, które Copilot monitoruje.
2.  Skrypty umiejętności (np. `.copilot/skills/generateTest.js`, `.copilot/skills/runCheckstyle.sh`) są dostępne w ścieżkach zdefiniowanych w `package.json` i mają odpowiednie uprawnienia do wykonywania (szczególnie skrypty bash).

### Przykładowe sposoby wywoływania umiejętności:
-   `Copilot, użyj umiejętności <skill_id> [argumenty]`
-   `Copilot, <description_of_skill>` (Copilot spróbuje sam dopasować intencję)
-   `Copilot, run <skill_id> <argumenty>`

### Przykład z tego modułu:
-   Aby wywołać umiejętność `generateTestBoilerplate` dla klasy `OwnerRepository`:
    *   Zaznacz tekst `OwnerRepository` w edytorze.
    *   W Copilot Chat wpisz: `Copilot, użyj generateTestBoilerplate dla zaznaczonego tekstu.`
    *   Alternatywnie: `Copilot, wygeneruj test JUnit dla klasy OwnerRepository.` (Copilot może sam dopasować).

## ⚠️ Rozwiązywanie Problemów
-   **Umiejętność nie działa:**
    1.  Sprawdź konsolę Output w VS Code (zakładka "GitHub Copilot Chat") pod kątem błędów.
    2.  Upewnij się, że ścieżki w `package.json` są poprawne.
    3.  Sprawdź uprawnienia do plików skryptów (np. `chmod +x`).
    4.  Uruchom skrypt umiejętności bezpośrednio z terminala, aby zobaczyć, czy działa niezależnie od Copilota.
-   **Brak detekcji umiejętności:**
    1.  Sprawdź składnię pliku `package.json` – musi być prawidłowym JSON-em.
    2.  Upewnij się, że sekcja `copilot.skills` jest poprawnie sformatowana.

Pamiętaj, że Copilot to narzędzie eksperymentalne, a jego zachowanie może się różnić. Cierpliwość i precyzja w komunikacji są kluczowe. Powodzenia w rozbudowie agentów!
