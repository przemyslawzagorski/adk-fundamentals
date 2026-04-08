## Wskazówki dla GitHub Copilot w projekcie spring-petclinic

Ten plik zawiera ogólne instrukcje i kontekst dla GitHub Copilot, aby pomóc mu lepiej zrozumieć specyfikę projektu `spring-petclinic` i udzielać bardziej trafnych odpowiedzi.

### Ogólny kontekst projektu
`spring-petclinic` to przykładowa aplikacja Spring Boot demonstrująca najlepsze praktyki w tworzeniu aplikacji webowych z użyciem Spring Framework. Jest to aplikacja do zarządzania kliniką weterynaryjną, która obsługuje właścicieli zwierząt, weterynarzy i wizyty.

### Architektura i technologie
- **Backend:** Spring Boot, Spring Data JPA, Hibernate, Maven.
- **Baza danych:** H2 (domyślnie), PostgreSQL, MySQL.
- **Frontend:** Thymeleaf, Bootstrap, jQuery.
- **Struktura:** Warstwowa (kontrolery, serwisy, repozytoria, encje).

### Kluczowe moduły
- `Owner`: Zarządzanie właścicielami zwierząt i ich danymi.
- `Pet`: Zarządzanie zwierzętami, ich typami i danymi.
- `Vet`: Zarządzanie weterynarzami i ich specjalizacjami.
- `Visit`: Zarządzanie wizytami zwierząt.

### Oczekiwane zachowanie Copilota
1.  **Świadomość domenowa:** Copilot powinien być świadomy terminologii związanej z domeną weterynaryjną i modelem danych `spring-petclinic`.
2.  **Generowanie kodu:** Preferowane są idiomy Spring Boot i wzorce projektowe `spring-petclinic`.
3.  **Refaktoryzacja:** Sugestie refaktoryzacji powinny być zgodne z czystym kodem i zasadami SOLID.
4.  **Testy:** Generowanie testów jednostkowych i integracyjnych z użyciem JUnit 5 i Mockito.

### Wsparcie dla MCP Servers
Projekt `spring-petclinic` jest często wykorzystywany do eksperymentów z Custom MCP Servers. Jeśli korzystasz z MCP, pamiętaj o:
- **Kontekstualizacji zapytań:** MCP powinien uwzględniać bieżący plik i jego zawartość.
- **Integracji:** Wykorzystywaniu MCP do integracji z narzędziami analitycznymi, Jira, systemami CI/CD w kontekście `spring-petclinic`.

**Przykład użycia w Copilot Chat:**
`/ask Jakie są klasy modelu danych związane z właścicielami zwierząt w spring-petclinic?`

**Oczekiwana odpowiedź (przez Copilot lub MCP):**
`W kontekście spring-petclinic, kluczowe klasy związane z właścicielami zwierząt to: Owner, Pet, PetType, Visit.`
