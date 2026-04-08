# Generowanie Testów Jednostkowych

**Instrukcja dla Copilota:**
Użytkownik zaznaczył klasę lub metodę, dla której chce wygenerować testy jednostkowe. Twoim zadaniem jest stworzenie nowego pliku testowego, zawierającego testy jednostkowe dla wskazanej klasy/metody.

**Kroki, które należy wykonać:**
1.  **Analiza Kontekstu:** Zrozumieć funkcjonalność testowanej klasy/metody.
2.  **Struktura Testu:** Utwórz nowy plik testowy w odpowiednim katalogu (`src/test/java/...`), nazwany zgodnie z konwencją (np. `[NazwaKlasy]Tests.java`).
3.  **Wybór Frameworku:** Użyj JUnit 5 w połączeniu z Mockito do mokowania zależności. Jeśli klasa jest kontrolerem Spring, użyj `@WebMvcTest` i `MockMvc`.
4.  **Generowanie Scenariuszy Testowych:**
    *   Dla każdej publicznej metody (lub kluczowych prywatnych metod, jeśli są testowalne poprzez publiczne API), wygeneruj co najmniej jeden test pozytywny i jeden test negatywny (jeśli ma zastosowanie).
    *   Uwzględnij testy dla przypadków brzegowych i walidacji.
5.  **Mockowanie Zależności:** Poprawnie zamokuj wszystkie zależności, aby testować tylko logikę danej klasy.
6.  **Asercje:** Użyj asercji JUnit (np. `assertEquals`, `assertTrue`, `assertThrows`) do weryfikacji oczekiwanych zachowań.
7.  **Zapewnij Czytelność:** Kod testowy powinien być czytelny i dobrze zorganizowany (np. używając `@BeforeEach`).

**Przykład użycia:**
Zaznacz klasę `OwnerController` i użyj tego promptu, aby wygenerować testy dla jej metod.
