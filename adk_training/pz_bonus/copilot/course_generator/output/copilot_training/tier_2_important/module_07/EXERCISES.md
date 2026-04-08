wybór "Ask Copilot about this file").
3. Po wskazaniu pliku, zapytaj Copilota:
   ```
   Zaproponuj refaktoryzację tej klasy, aby poprawić jej czytelność i wydajność, np. poprzez użycie bardziej nowoczesnych konstrukcji Javy (jeśli to możliwe) lub ulepszenie metod dostępu do kolekcji. Przedstaw zmiany w formie bloku kodu.
   ```

**Oczekiwany rezultat:**
- Copilot powinien dostarczyć sugestie dotyczące refaktoryzacji dla klasy `Vet.java`, możliwe, że zaproponuje zmiany w zarządzaniu kolekcją `specialties` lub w strukturze klasy, aby była bardziej idiomatyczna.
- Otrzymasz blok kodu z proponowanymi zmianami.

**Wskazówki:**
- Upewnij się, że Copilot naprawdę skupił się na wskazanym pliku. Jeśli nie, spróbuj ponownie wskazać plik lub dokładniej sprecyzować pytanie.

---

## Ćwiczenie 3: Testowanie i Refaktoryzacja z Subagentami

**Cel:** Obserwacja, jak Copilot wykorzystuje subagentów do rozkładania złożonych zadań na mniejsze części (np. tworzenie testów i refaktoryzacja).

**Kontekst:** Chcesz dodać test jednostkowy do metody `findByLastName` w `OwnerRepository.java` i jednocześnie sprawdzić, czy można ją zrefaktoryzować, aby była bardziej efektywna lub zgodna z najlepszymi praktykami Spring Data JPA.

**Kroki:**
1. Otwórz panel Copilot Chat.
2. Zapytaj Copilota o złożone zadanie:
   ```
   Napisz test jednostkowy dla metody `findByLastName` w `OwnerRepository.java`. Następnie zrefaktoruj tę metodę, aby była bardziej idiomatyczna dla Spring Data JPA, jeśli to możliwe, i upewnij się, że testy nadal przechodzą. Przedstaw zmiany w formie bloku kodu.
   ```

**Oczekiwany rezultat:**
- Copilot powinien najpierw zaproponować kod testu jednostkowego dla metody `findByLastName`.
- Następnie, powinien zaproponować refaktoryzację samej metody `findByLastName` lub jej otoczenia.
- Zwróć uwagę na komunikaty w czacie Copilota – możesz zauważyć, że używa on `Test Agent` i `Refactor Agent` do realizacji zadania.
- Możesz poprosić Copilota o wyjaśnienie, dlaczego zaproponował konkretne zmiany.

**Wskazówki:**
- Metoda `findByLastName` w `OwnerRepository.java` w `spring-petclinic` używa adnotacji `@Query`. Zobacz, czy Copilot zaproponuje zmianę na dynamiczne zapytanie lub inną formę, jeśli uzna to za bardziej idiomatyczne.
- Po otrzymaniu propozycji, możesz dopytać: "Jakie byłyby konsekwencje tych zmian dla wydajności?"

---

## Ćwiczenie 4: Wyszukiwanie Informacji z Subagentem Search

**Cel:** Zrozumienie, jak Copilot wykorzystuje `Search Agent` do pozyskiwania informacji z zewnętrznych źródeł.

**Kontekst:** Potrzebujesz szybko dowiedzieć się o najnowszych trendach lub ważnych zmianach w ekosystemie Spring Boot.

**Kroki:**
1. Otwórz panel Copilot Chat.
2. Zapytaj Copilota o informacje, które wymagają przeszukania dokumentacji lub internetu:
   ```
   Jakie są najnowsze zalecenia dotyczące konfiguracji bezpieczeństwa w aplikacjach Spring Boot 3, zwłaszcza w kontekście uwierzytelniania JWT?
   ```

**Oczekiwany rezultat:**
- Copilot powinien przeszukać dostępne źródła (dokumentacja Spring, blogi, fora) i podsumować kluczowe zalecenia dotyczące bezpieczeństwa w Spring Boot 3 z JWT.
- Możesz zauważyć, że Copilot informuje o użyciu `Search Agent`.

**Wskazówki:**
- Spróbuj zadać inne pytanie wymagające wyszukiwania, np. "Jakie są różnice między Spring WebFlux a Spring MVC?"
- Zawsze weryfikuj źródła, jeśli Copilot je poda, aby upewnić się, że informacje są aktualne i wiarygodne.