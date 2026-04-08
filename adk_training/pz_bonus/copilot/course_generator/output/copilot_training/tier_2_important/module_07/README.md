napisanie testów i refaktoryzację kodu może zostać podzielona na zadanie 'napisz test' i 'refaktoryzuj'.
- **Specjalizacja:** Każdy subagent jest wyszkolony do wykonywania określonego rodzaju operacji, co zwiększa skuteczność i precyzję odpowiedzi Copilota.

**Jak Copilot automatycznie wykorzystuje subagentów do złożonych zapytań?**
Kiedy zadajesz pytanie Copilotowi, jego wewnętrzny mechanizm ocenia złożoność i naturę zapytania. Jeśli stwierdzi, że zadanie wymaga więcej niż jednej operacji lub dostępu do różnych źródeł danych/funkcji, automatycznie aktywuje odpowiednich subagentów. Dzieje się to w tle i często jest wizualizowane w oknie czatu jako „Myślę…” lub „Używam agenta X…”.

**Przykłady wbudowanych subagentów:**
Chociaż ich dokładna lista i nazewnictwo mogą ewoluować, typowe subagenci to:
- **`Search Agent`**: Używany do przeszukiwania dokumentacji, internetu lub bazy wiedzy w celu znalezienia informacji niezbędnych do odpowiedzi na pytanie.
- **`Refactor Agent`**: Specjalizuje się w przepisywaniu kodu w celu poprawy jego struktury, czytelności lub wydajności, bez zmiany jego zewnętrznego zachowania.
- **`Test Agent`**: Skoncentrowany na generowaniu testów jednostkowych, integracyjnych lub end-to-end dla danego kodu.
- **`Explain Agent`**: Wyjaśnia działanie kodu lub koncepty programistyczne.
- **`Fix Agent`**: Pomaga w identyfikowaniu i poprawianiu błędów w kodzie.
- **`Commit Agent`**: Generuje sugestie wiadomości commitów na podstawie zmian w kodzie.

## 💡 Przykłady Użycia

### Przykład 1: Analiza architektury projektu z `@workspace`
**Pytanie:** "Korzystając z kontekstu `@workspace`, opisz ogólną architekturę projektu spring-petclinic, ze szczególnym uwzględnieniem warstw i technologii." 

**Wyjaśnienie:** Copilot przeskanuje cały projekt `spring-petclinic`, analizując jego strukturę katalogów, pliki konfiguracyjne (np. `pom.xml`, `.properties`), nazewnictwo klas i pakietów. Na podstawie zebranych informacji dostarczy podsumowanie architektoniczne, wskazując na przykład na warstwę prezentacji (Spring MVC/Thymeleaf), warstwę biznesową (serwisy), warstwę dostępu do danych (Spring Data JPA), a także technologie takie jak Spring Boot, Hibernate, H2 Database itp.

### Przykład 2: Refaktoryzacja klasy za pomocą `#file`
**Pytanie:** "Używając `#file src/main/java/org/springframework/samples/petclinic/owner/Owner.java`, zaproponuj refaktoryzację tej klasy, aby była bardziej zgodna z zasadami czystego kodu i wykorzystywała nowe funkcje Javy, jeśli to możliwe (np. rekordy)." 

**Wyjaśnienie:** Copilot skupi się wyłącznie na pliku `Owner.java`. Przeanalizuje jego zawartość, metody, pola i relacje. Następnie zaproponuje zmiany, takie jak:
- Zastąpienie getterów i setterów przez rekord Javy, jeśli klasa jest prostym holderem danych.
- Ulepszenie logiki w metodach.
- Sugestie dotyczące walidacji danych.
- Zoptymalizowanie importów lub struktury wewnętrznej klasy.

```java
// Oryginalny fragment Owner.java
public class Owner extends Person {

    @Column(name = "address")
    private String address;

    @Column(name = "city")
    private String city;

    @Column(name = "telephone")
    private String telephone;

    // ... gettery i settery ...
}

// Możliwa propozycja refaktoryzacji na Record (uproszczony przykład)
// Wymagałoby to szerszej analizy ORM i innych zależności
// record OwnerDetails(String address, String city, String telephone) {}
```

### Przykład 3: Złożone zadanie z subagentami (Testy i Refaktoryzacja)
**Pytanie:** "Napisz test jednostkowy dla metody `findByLastName` w `OwnerRepository.java`. Następnie zrefaktoruj tę metodę, aby była bardziej idiomatyczna dla Spring Data JPA, jeśli to możliwe, i upewnij się, że testy nadal przechodzą." 

**Wyjaśnienie:** Copilot rozpozna, że to zapytanie wymaga dwóch odrębnych operacji: pisania testów i refaktoryzacji. Prawdopodobnie aktywuje `Test Agent` do wygenerowania testów dla `findByLastName`, a następnie `Refactor Agent` do zaproponowania zmian w implementacji metody `findByLastName`. Możesz zaobserwować komunikaty w Copilot Chat, wskazujące na użycie tych subagentów. Na końcu, Copilot może zasugerować uruchomienie testów w celu weryfikacji. 

```java
// Fragment OwnerRepository.java
public interface OwnerRepository extends Repository<Owner, Integer> {

    // ... inne metody ...

    /**
     * Retrieve {@link Owner}s from the data store by last name, returning all owners
     * whose last name starts with the given name.
     * @param lastName Value to search for
     * @return a Collection of matching {@link Owner}s (or an empty Collection if none
     *         found)
     */
    @Query("SELECT DISTINCT owner FROM Owner owner left join fetch owner.pets WHERE owner.lastName LIKE :lastName%")
    Collection<Owner> findByLastName(@Param("lastName") String lastName);

}

// Przykład wygenerowanego testu (fragment)
@DataJpaTest
class OwnerRepositoryTests {

    @Autowired
    OwnerRepository owners;

    @Test
    void findByLastName() {
        Collection<Owner> owners = this.owners.findByLastName("Franklin");
        assertThat(owners).hasSize(1);
        // ... dalsze asercje ...
    }
}
```

## ✅ Best Practices
- **Bądź konkretny i zwięzły:** Im jaśniejsze jest Twoje zapytanie, tym lepszą odpowiedź otrzymasz. Unikaj dwuznaczności.
- **Używaj `@workspace` z umiarem:** Chociaż jest potężne, nie zawsze jest potrzebne. Używaj go, gdy naprawdę potrzebujesz szerokiego kontekstu projektu.
- **Weryfikuj odpowiedzi:** Zawsze sprawdzaj kod i sugestie dostarczone przez Copilota. Traktuj je jako punkt wyjścia, a nie ostateczne rozwiązanie.
- **Eksperymentuj z różnymi sformułowaniami:** Jeśli Copilot nie zrozumie Twojego zapytania za pierwszym razem, spróbuj sformułować je inaczej. 
- **Obserwuj działanie subagentów:** Zwracaj uwagę na komunikaty Copilota informujące o użyciu subagentów – pomoże Ci to zrozumieć, jak działa i jak możesz lepiej formułować złożone zapytania.

## ⚠️ Common Pitfalls
- **Nadmierne dostarczanie kontekstu:** Przeciążenie Copilota zbyt dużą ilością nieistotnego kontekstu może prowadzić do gorszych odpowiedzi i wolniejszego działania.
- **Brak weryfikacji:** Bez sprawdzenia, możesz wprowadzić błędy lub nieoptymalny kod do swojego projektu.
- **Oczekiwanie zbyt wielu kroków w jednym zapytaniu:** Chociaż subagenci pomagają w złożonych zadaniach, zbyt rozbudowane polecenie może być nadal zbyt trudne dla Copilota do przetworzenia w jednym kroku. Lepiej podzielić je na mniejsze części.
- **Ignorowanie ograniczeń okna kontekstowego:** Pamiętaj, że nawet z `file` i `@workspace`, istnieje limit tego, ile Copilot może aktywnie przetworzyć w danej chwili. Jeśli widzisz, że Copilot „zapomina” o czymś, spróbuj zawęzić kontekst.

## 🔗 Dodatkowe Zasoby
- [Dokumentacja GitHub Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat/using-github-copilot-chat)
- [Przewodnik po subagentach w Copilocie](https://docs.github.com/en/copilot/github-copilot-chat/sub-agents-in-github-copilot-chat) (upewnij się, że link jest aktualny, nazewnictwo i dostępność mogą się zmieniać).
