# Dodawanie Nowego Endpointu REST

**Instrukcja dla Copilota:**
Użytkownik chce dodać nowy endpoint REST do istniejącego kontrolera Spring (np. `VetController`, `OwnerController`). Twoim zadaniem jest zaimplementowanie tego endpointu, wliczając w to wszelkie niezbędne zmiany w warstwie serwisowej i repozytoryjnej.

**Kroki, które należy wykonać:**
1.  **Analiza Wymagań:** Zrozum, jaki zasób ma być obsługiwany (np. `Vet`, `Owner`), jaka operacja ma zostać wykonana (GET, POST, PUT, DELETE) oraz jakie parametry wejściowe i wyjściowe są wymagane.
2.  **Modyfikacja Repozytorium:** Jeśli nowa funkcjonalność wymaga pobrania/zapisu danych w sposób, którego nie obsługują istniejące metody w repozytorium (np. `VetRepository`), dodaj nową metodę (np. `findBySpecialtyName`).
3.  **Modyfikacja/Tworzenie Serwisu:** Jeśli istnieje warstwa serwisowa (np. `VetService`), dodaj do niej metodę orkiestrującą logikę biznesową. Jeśli warstwa serwisowa nie istnieje, zaproponuj jej utworzenie.
4.  **Implementacja w Kontrolerze:** Wskazanym kontrolerze dodaj nową metodę, która będzie obsługiwać endpoint REST.
    *   Użyj odpowiednich adnotacji (`@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`).
    *   Zdefiniuj ścieżkę (`@RequestMapping`, `@PathVariable`, `@RequestParam`).
    *   Obsłuż parametry wejściowe i wyjściowe (np. `ResponseEntity`, DTO).
    *   Upewnij się, że obsługiwane są błędy (np. zasób nie znaleziony) za pomocą odpowiednich statusów HTTP.
5.  **Generowanie Testów (opcjonalnie):** Zaproponuj wygenerowanie testu integracyjnego dla nowego endpointu, używając `MockMvc`.

**Przykład użycia:**
Poproś o dodanie endpointu GET `/vets/specialty/{specialtyName}` do `VetController.java`, który zwraca listę weterynarzy według specjalizacji.
