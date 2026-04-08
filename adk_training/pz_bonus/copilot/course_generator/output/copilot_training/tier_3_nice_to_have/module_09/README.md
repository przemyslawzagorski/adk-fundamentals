# Inline Chat i Sugestie Kodu (GitHub Copilot)

## 🎯 Cele Szkolenia
- Zrozumienie, jak efektywnie wykorzystywać Inline Chat do szybkich zmian w kodzie.
- Poznanie możliwości sugestii kodu w locie (inline suggestions) oferowanych przez GitHub Copilot.
- Opanowanie skrótu `Ctrl+I` do wywoływania Inline Chat.

## 📚 Wprowadzenie do Inline Chat i Sugestii

GitHub Copilot to potężne narzędzie wspierające programistów w pisaniu kodu. Jednymi z jego najbardziej intuicyjnych funkcji są **Inline Chat** oraz **Sugestie Kodu (Inline Suggestions)**. Pozwalają one na interakcję z Copilotem bezpośrednio w edytorze kodu, minimalizując przełączanie kontekstu i zwiększając produktywność.

**Inline Chat** to szybki sposób na zadawanie pytań, refaktoryzację fragmentów kodu, generowanie testów czy dodawanie komentarzy bez opuszczania bieżącej linii kodu. Aktywujesz go prostym skrótem `Ctrl+I` (lub `Cmd+I` na macOS). Po jego wywołaniu, Copilot otwiera małe okno czatu, w którym możesz opisać, co chcesz zrobić z zaznaczonym kodem lub w bieżącym kontekście. Jest to idealne rozwiązanie do szybkich, lokalnych modyfikacji i zapytań.

**Sugestie Kodu** (często nazywane po prostu "inline suggestions" lub "ghost text") to podpowiedzi generowane przez Copilota w czasie rzeczywistym, gdy piszesz kod. Pojawiają się one jako półprzezroczysty tekst, sugerując całe linie, fragmenty kodu, nazwy zmiennych, a nawet całe funkcje. Możesz je zaakceptować, naciskając klawisz `Tab`, lub zignorować. Są one niezwykle przydatne do przyspieszania procesu kodowania i odkrywania nowych sposobów implementacji.

Razem, te dwie funkcje tworzą spójne i efektywne środowisko pracy, które pozwala na płynne kodowanie i natychmiastowe wsparcie AI.

## 💡 Przykłady Użycia i Ćwiczenia

Poniższe ćwiczenia pomogą Ci zrozumieć i zastosować Inline Chat oraz Sugestie Kodu w praktyce, wykorzystując repozytorium `spring-petclinic`.

### Ćwiczenie 1: Refaktoryzacja z Inline Chat (`Ctrl+I`)

**Cel:** Użycie Inline Chat do szybkiej refaktoryzacji istniejącego bloku kodu.

**Kontekst:** Pracujesz z repozytorium `spring-petclinic`. Chcesz poprawić czytelność krótkiej pętli lub bloku kodu w pliku `PetService.java`.

**Kroki:**
1. Otwórz projekt `spring-petclinic` w VS Code.
2. Przejdź do pliku `src/main/java/org/springframework/samples/petclinic/service/PetService.java`.
3. Zlokalizuj dowolną krótką pętlę `for` lub `while` albo fragment kodu, który wydaje Ci się, że można by uprościć lub uczytelnić.
4. Zaznacz ten fragment kodu.
5. Naciśnij `Ctrl+I` (lub `Cmd+I` na macOS), aby wywołać Inline Chat.
6. W oknie czatu wpisz polecenie, np. "Refactor this code to be more concise" (Zrefaktoryzuj ten kod, aby był bardziej zwięzły) lub "Add comments explaining this block" (Dodaj komentarze wyjaśniające ten blok).
7. Przejrzyj sugestie Copilota i zastosuj wybraną zmianę.

**Oczekiwany rezultat:** Zaznaczony kod zostanie zrefaktoryzowany lub uzupełniony zgodnie z Twoim poleceniem, co poprawi jego jakość lub czytelność.

---

### Ćwiczenie 2: Wykorzystanie Inline Suggestions

**Cel:** Przetestowanie automatycznych sugestii kodu podczas pisania nowej metody.

**Kontekst:** W `spring-petclinic` chcesz dodać nową funkcjonalność walidacji daty wizyty.

**Kroki:**
1. Otwórz plik `src/main/java/org/springframework/samples/petclinic/service/VisitService.java`.
2. Znajdź istniejącą metodę lub miejsce, w którym logiczne byłoby dodanie nowej metody walidującej daty wizyt (np. czy data wizyty nie jest w przeszłości).
3. Zacznij pisać sygnaturę nowej metody, np. `public void validateVisitDate(Visit visit) {`.
4. Obserwuj, jak Copilot generuje sugestie kodu w postaci półprzezroczystego tekstu.
5. Akceptuj sugestie, naciskając `Tab`, lub kontynuuj pisanie, aby zobaczyć inne propozycje.
6. Spróbuj doprowadzić do sytuacji, w której Copilot zasugeruje całą logikę walidacji daty (np. porównanie z bieżącą datą).

**Oczekiwany rezultat:** Copilot w czasie rzeczywistym podpowie i zasugeruje fragmenty kodu, które pomogą Ci szybko zaimplementować logikę walidacji daty wizyty, demonstrując moc inline suggestions.

## 🔗 Dodatkowe Zasoby
- [Oficjalna dokumentacja GitHub Copilot](https://docs.github.com/en/copilot)
- [Korzystanie z czatu w VS Code](https://code.visualstudio.com/docs/editor/github-copilot#_chat-with-github-copilot-in-the-editor)
