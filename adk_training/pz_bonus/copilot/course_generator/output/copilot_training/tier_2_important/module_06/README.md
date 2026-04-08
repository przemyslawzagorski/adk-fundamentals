# Copilot Chat - Podstawy

## 🎯 Cele Szkolenia
Po ukończeniu tego modułu uczestnik będzie potrafił:
- Rozumieć i efektywnie korzystać z interfejsu Copilot Chat w VS Code.
- Używać podstawowych komend chata, takich jak `/explain`, `/refactor`, `/doc`.
- Skutecznie zadawać pytania Copilotowi i interpretować jego odpowiedzi.
- Tworzyć efektywne zapytania (prompty) w Copilot Chat w celu uzyskania precyzyjnych sugestii i pomocy.
- Zarządzać sugerowanymi zmianami kodu i historią konwersacji.

## 📚 Teoria

### Wprowadzenie do Copilot Chat
GitHub Copilot Chat to interaktywny interfejs konwersacyjny dostępny bezpośrednio w środowisku VS Code, który pozwala programistom komunikować się z Copilotem za pomocą języka naturalnego. Zamiast czekać na sugestie w edytorze, możesz aktywnie zadawać pytania, prosić o wyjaśnienia, generować kod, refaktoryzować istniejące fragmenty, czy tworzyć dokumentację. Działa to jak rozmowa z doświadczonym kolegą-programistą, który ma dostęp do całej Twojej bazy kodu i kontekstu projektu.

**Interfejs Copilot Chat w VS Code**
Copilot Chat jest dostępny jako panel boczny w VS Code, zazwyczaj poprzez ikonę dymku czatu lub skrót klawiaturowy. W panelu tym możesz wpisywać zapytania tekstowe i otrzymywać odpowiedzi. Interfejs jest zaprojektowany tak, aby płynnie integrować się z Twoim workflow, umożliwiając szybkie przełączanie się między pisaniem kodu a interakcją z AI.

### Podstawowe Komendy Chata
Copilot Chat rozpoznaje szereg wbudowanych komend, które pomagają ukierunkować jego działania. Oto kilka najczęściej używanych:

- **`/explain`**: Ta komenda prosi Copilota o wyjaśnienie zaznaczonego fragmentu kodu lub funkcji. Jest niezwykle użyteczna do szybkiego zrozumienia logiki, zwłaszcza w przypadku obcego lub skomplikowanego kodu.
  *Przykład:* Zaznacz metodę `findOwner` w `OwnerRepository.java` w projekcie `spring-petclinic` i wpisz `/explain`. Copilot wyjaśni jej cel i działanie.

- **`/refactor`**: Służy do prośby o refaktoryzację zaznaczonego kodu. Może to obejmować poprawę czytelności, wydajności, lub zastosowanie wzorców projektowych. Copilot często proponuje wiele alternatywnych rozwiązań.
  *Przykład:* Zaznacz fragment kodu w `PetService.java` i wpisz `/refactor`. Copilot zaproponuje ulepszenia.

- **`/doc`**: Używana do generowania dokumentacji dla zaznaczonego kodu, np. komentarzy Javadoc, Pydoc, czy innych formatów. Pomaga to w utrzymaniu aktualnej i kompletnej dokumentacji projektu.
  *Przykład:* Zaznacz metodę `addOwner` w `OwnerController.java` i wpisz `/doc`. Copilot wygeneruje odpowiednie komentarze.

- **`/fix`**: Pomaga w identyfikowaniu i proponowaniu rozwiązań dla błędów w kodzie.

- **`/test`**: Generuje testy jednostkowe lub integracyjne dla wskazanego kodu.

### Zadawanie Pytań i Otrzymywanie Odpowiedzi
Podstawą interakcji z Copilot Chat jest zadawanie pytań. Możesz pytać o dowolny aspekt związany z kodem, technologiami, wzorcami projektowymi czy ogólnymi problemami programistycznymi. Ważne jest, aby formułować pytania jasno i konkretnie, dostarczając wystarczający kontekst.

Copilot Chat analizuje Twój bieżący plik, otwarte pliki, a czasem nawet całe repozytorium (w zależności od konfiguracji i dostępnych integracji), aby dostarczyć jak najbardziej trafne odpowiedzi. Odpowiedzi mogą obejmować fragmenty kodu, wyjaśnienia teoretyczne, linki do dokumentacji czy sugestie dotyczące dalszych działań.

### Tworzenie Efektywnych Zapytań (Promptów)
Jakość odpowiedzi Copilota w dużej mierze zależy od jakości zadawanego pytania (promptu). Oto kluczowe wskazówki:

1.  **Bądź konkretny:** Zamiast "Napisz kod", użyj "Napisz metodę do walidacji adresu email w Javie, która używa wyrażeń regularnych i zwraca boolean."
2.  **Dostarcz kontekst:** Wskaż, w jakim języku programujesz, jaka jest struktura projektu, czego oczekujesz od rezultatu.
3.  **Określ format:** Jeśli potrzebujesz kodu, poproś o "fragment kodu w Javie". Jeśli wyjaśnienie, poproś o "zwięzłe wyjaśnienie".
4.  **Używaj przykładów:** Jeśli masz konkretny przykład danych wejściowych i oczekiwanych danych wyjściowych, dołącz je do promptu.
5.  **Iteruj:** Jeśli pierwsza odpowiedź nie jest satysfakcjonująca, zmodyfikuj prompt i spróbuj ponownie. Copilot pamięta kontekst rozmowy.

*Przykład:* Zamiast "jak zaimplementować buildera?", lepiej "W jaki sposób mogę zaimplementować wzorzec projektowy Builder dla klasy `Pet` z projektu `spring-petclinic` w Javie, aby ułatwić tworzenie nowych obiektów `Pet` z różnymi kombinacjami pól?".

### Przeglądanie, Akceptowanie i Odrzucanie Sugerowanych Zmian
Kiedy Copilot proponuje zmiany w kodzie (np. po użyciu `/refactor` lub po wygenerowaniu kodu), zazwyczaj przedstawia je w formacie diff, który możesz przejrzeć bezpośrednio w interfejsie chata.
- **Akceptacja:** Często dostępny jest przycisk "Insert into new file" lub "Insert at Cursor" pozwalający na wstawienie kodu.
- **Odrzucenie:** Jeśli sugestia nie jest trafna, po prostu ją ignorujesz lub zadajesz kolejne pytanie, precyzując swoje oczekiwania.
- **Modyfikacja:** Możesz wstawić sugerowany kod i następnie samodzielnie go dostosować.

Pamiętaj, że Copilot to narzędzie wspomagające – ostateczna decyzja o włączeniu kodu do projektu zawsze należy do Ciebie.

### Zarządzanie Historią Konwersacji
Copilot Chat przechowuje historię Twoich rozmów. Możesz do niej wracać, aby przypomnieć sobie poprzednie pytania i odpowiedzi, co jest szczególnie przydatne, gdy pracujesz nad złożonym problemem i potrzebujesz odtworzyć tok myślenia. Historia jest często resetowana po zamknięciu sesji VS Code, ale możesz zapisywać interesujące fragmenty do swoich notatek.

## 💡 Kluczowe Przykłady

### Przykład 1: Wyjaśnianie złożonej metody
Załóżmy, że natrafiasz na metodę `initNewPet` w `PetController.java` w projekcie `spring-petclinic` i nie jesteś pewien wszystkich jej kroków.

1. Otwórz plik `PetController.java`.
2. Zaznacz całą metodę `initNewPet`.
3. Otwórz Copilot Chat i wpisz: `/explain`
Copilot odpowie szczegółowym opisem, co metoda robi, jakie ma parametry i jaki jest jej cel, np.:
```markdown
Metoda `initNewPet` jest używana do inicjalizacji nowego obiektu `Pet` przed jego dodaniem do formularza. Sprawdza, czy obiekt `Owner` został przekazany; jeśli tak, ustawia go dla nowego `Pet`. Dodatkowo, ładuje listę typów zwierząt domowych (PetType) i umieszcza ją w modelu, aby były dostępne w formularzu.
```

### Przykład 2: Refaktoryzacja małego fragmentu kodu
Masz prostą metodę, która formatuje datę i chcesz sprawdzić, czy Copilot może ją ulepszyć.

1. Znajdź w projekcie `spring-petclinic` jakąś prostą metodę pomocniczą, np. w `org.springframework.samples.petclinic.util.EntityUtils`. Możesz stworzyć nową, jeśli nie ma odpowiedniej. Np. prostą metodę do konwersji `String` na `LocalDate`.
2. Zaznacz tę metodę.
3. W Copilot Chat wpisz: `/refactor Make this more readable and robust.`
Copilot może zaproponować np. użycie `DateTimeFormatter` z predefiniowanymi wzorcami lub dodanie obsługi wyjątków.

### Przykład 3: Generowanie komentarzy Javadoc
Potrzebujesz szybko udokumentować nową metodę.

1. Otwórz `OwnerController.java`.
2. Zaznacz metodę `processUpdateOwnerForm`.
3. W Copilot Chat wpisz: `/doc`
Copilot wygeneruje Javadoc podobny do poniższego:
```java
/**
 * Processes the form for updating an existing owner.
 *
 * @param owner   the {@link Owner} object populated from the form
 * @param result  the {@link BindingResult} object for validation errors
 * @param ownerId the ID of the owner to update
 * @return the view name to redirect to, either "owners/createOrUpdateOwnerForm" on error or "redirect:/owners/{ownerId}" on success
 */
@PostMapping("/owners/{ownerId}/edit")
public String processUpdateOwnerForm(@Valid Owner owner, BindingResult result, @PathVariable("ownerId") int ownerId) {
    // ... code ...
}
```

## ✅ Best Practices
- **Zawsze weryfikuj:** Kod generowany przez AI może zawierać błędy, nieefektywności lub luki bezpieczeństwa. Zawsze dokładnie przeglądaj i testuj sugestie.
- **Używaj kontekstu:** Im więcej kontekstu dostarczysz (zaznaczony kod, otwarte pliki, opis problemu), tym lepsze będą odpowiedzi.
- **Bądź precyzyjny:** Unikaj ogólnych pytań. Im bardziej szczegółowe zapytanie, tym bardziej trafna odpowiedź.
- **Iteruj i udoskonalaj:** Traktuj interakcję z Copilotem jako proces iteracyjny. Jeśli pierwsza odpowiedź nie jest idealna, zadaj pytanie ponownie, dodając więcej szczegółów.
- **Łącz z innymi narzędziami:** Copilot Chat działa najlepiej, gdy jest używany w połączeniu z innymi narzędziami deweloperskimi i Twoją własną wiedzą.

## ⚠️ Common Pitfalls
- **Zbyt ogólne zapytania:** Pytania typu "Napisz mi aplikację" nie przyniosą użytecznych rezultatów.
- **Nadmierne zaufanie:** Nie wklejaj kodu Copilota bez zrozumienia go. Może to prowadzić do wprowadzenia błędów lub długu technicznego.
- **Pomijanie dokumentacji:** Copilot jest świetny, ale nie zastępuje zrozumienia podstawowych koncepcji i oficjalnej dokumentacji.
- **Brak kontekstu:** Jeśli Copilot nie ma wystarczającego kontekstu, jego sugestie mogą być nietrafne lub ogólnikowe. Upewnij się, że odpowiednie pliki są otwarte lub kod jest zaznaczony.
- **Nieaktualne informacje:** Modele AI są trenowane na danych do pewnego punktu w czasie. Mogą nie znać najnowszych wersji bibliotek, frameworków lub najlepszych praktyk.

## 🔗 Dodatkowe Zasoby
- [Oficjalna dokumentacja GitHub Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat)
- [Przewodnik po efektywnych promptach dla Copilota](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat#try-prompts-to-start-a-conversation)
