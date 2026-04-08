# Refaktoryzacja: Ekstrakcja Logiki Biznesowej do Serwisu

**Instrukcja dla Copilota:**
Użytkownik zaznaczył fragment kodu lub wskazał metodę w kontrolerze (np. `OwnerController`). Twoim zadaniem jest zrefaktoryzowanie tego kodu poprzez ekstrakcję logiki biznesowej (np. zapisu do bazy danych, złożonych walidacji) do nowej lub istniejącej metody w warstwie serwisowej.

**Kroki, które należy wykonać:**
1.  **Identyfikacja logiki:** Określ, która część zaznaczonego kodu lub metody powinna zostać przeniesiona do serwisu.
2.  **Stworzenie/Modyfikacja Serwisu:** Jeśli nie istnieje odpowiednia klasa serwisowa dla danego kontekstu (np. `OwnerService`), utwórz ją w odpowiednim pakiecie. Jeśli istnieje, dodaj nową metodę (np. `saveOwner`, `processOwnerData`) lub zmodyfikuj istniejącą, aby zawierała przeniesioną logikę. Upewnij się, że serwis jest oznaczony adnotacją `@Service`.
3.  **Wstrzykiwanie Serwisu:** Wstrzyknij nowo utworzony/zmodyfikowany serwis do kontrolera (za pomocą `@Autowired` lub przez konstruktor).
4.  **Wywołanie Metody Serwisu:** Zastąp oryginalną logikę w kontrolerze wywołaniem odpowiedniej metody w serwisie.
5.  **Testy (opcjonalnie):** Zaproponuj wygenerowanie testów jednostkowych lub integracyjnych dla nowej/zmodyfikowanej metody w serwisie.
6.  **Potwierdzenie:** Po zakończeniu, potwierdź, że refaktoryzacja została wykonana i że kod jest funkcjonalny oraz zgodny z zasadami warstwowej architektury.

**Przykład użycia:**
Zaznacz metodę `processCreationForm` w `OwnerController.java` i użyj tego promptu, aby przenieść logikę zapisu właściciela do `OwnerService`.
