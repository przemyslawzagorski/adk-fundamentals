# Best Practices i Security z GitHub Copilot

## 🎯 Cele Szkolenia
- Zrozumienie ogólnych wskazówek dotyczących efektywnego wykorzystania GitHub Copilot.
- Zapoznanie się z aspektami prywatności i bezpieczeństwa danych w kontekście używania Copilota.
- Umiejętność konfiguracji ustawień prywatności Copilota w VS Code.

## 📚 Wprowadzenie i Kluczowe Aspekty
GitHub Copilot to potężne narzędzie, które może znacznie przyspieszyć proces kodowania. Jednak jego efektywne i bezpieczne wykorzystanie wymaga znajomości najlepszych praktyk oraz świadomości potencjalnych ryzyk. Ten moduł skupia się na tym, jak maksymalizować korzyści płynące z Copilota, jednocześnie minimalizując zagrożenia związane z prywatnością i bezpieczeństwem generowanego kodu. Ważne jest, aby zawsze traktować sugestie Copilota jako punkt wyjścia, a nie ostateczne rozwiązanie, i poddawać je dokładnej weryfikacji.

### ✅ Kluczowe Wskazówki
- **Weryfikacja kodu:** Zawsze przeglądaj i testuj kod wygenerowany przez Copilota. Może on zawierać błędy, luki bezpieczeństwa lub być niezoptymalizowany.
- **Prywatność danych:** Bądź świadomy, jakie dane są udostępniane firmie GitHub podczas korzystania z Copilota. Konfiguruj ustawienia prywatności zgodnie z polityką firmy.
- **Kontekst:** Copilot najlepiej działa, gdy ma odpowiedni kontekst. Staraj się pisać klarowny kod i komentarze, aby Copilot mógł generować bardziej trafne sugestie.

## 💡 Przykłady i Ćwiczenia

### Ćwiczenie 1: Weryfikacja Kodu Generowanego przez AI

**Cel:** Zrozumienie potrzeby weryfikacji i modyfikacji kodu sugerowanego przez Copilota, w kontekście repozytorium `spring-petclinic`.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Copilot może zasugerować kod, który nie zawsze jest optymalny lub bezpieczny. Poniższe ćwiczenie pomoże Ci rozwinąć krytyczne myślenie wobec automatycznie generowanego kodu.

**Kroki:**
1. Otwórz plik `Owner.java` znajdujący się w katalogu `src/main/java/org/springframework/samples/petclinic/owner` w projekcie `spring-petclinic`.
2. W pliku `Owner.java`, wewnątrz klasy `Owner`, spróbuj dodać nową metodę publiczną, np. `isValid()`, która będzie walidować, czy dane właściciela (np. `firstName`, `lastName`) nie są puste. Użyj Copilota do jej wygenerowania, wpisując np. komentarz `// Generate a method to validate owner's first and last name`. 
3. Dokładnie przeanalizuj zasugerowany kod pod kątem poprawności logiki, potencjalnych błędów null pointer, a także zgodności z przyjętymi konwencjami kodowania w `spring-petclinic`.
4. Wprowadź niezbędne modyfikacje, aby upewnić się, że kod jest zgodny z najlepszymi praktykami, jest czytelny i bezpieczny.

**Oczekiwany rezultat:** Metoda `isValid()` zostanie dodana do `Owner.java`, a Ty zyskasz doświadczenie w krytycznej ocenie i poprawianiu kodu generowanego przez AI.

---

### Ćwiczenie 2: Konfiguracja Prywatności Copilota w VS Code

**Cel:** Zapoznanie się z ustawieniami prywatności Copilota w VS Code i ich świadoma konfiguracja.

**Kontekst:** Dbanie o prywatność danych i kodu źródłowego jest kluczowe, szczególnie w środowisku korporacyjnym. W tym ćwiczeniu skonfigurujesz ustawienia Copilota, aby lepiej zarządzać udostępnianiem danych.

**Kroki:**
1. Otwórz ustawienia VS Code. Możesz to zrobić, naciskając `Ctrl + ,` (Comma) lub przechodząc do `File > Preferences > Settings`.
2. W polu wyszukiwania ustawień wpisz 