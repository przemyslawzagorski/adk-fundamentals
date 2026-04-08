# 🎯 Plan Funkcyjny: GitHub Copilot Masterclass

## 📚 MAPOWANIE FUNKCJI DO MODUŁÓW

### **Moduł 1: Komunikacja z AI i eksploracja kodu**
**Funkcje Copilota:**
- ✅ **Inline Suggestions** - podstawowe autouzupełnianie
- ✅ **Chat Mode** - zadawanie pytań
- ✅ **Agent Mode** - autonomiczne tworzenie projektu
- ✅ **@workspace** - kontekst całego projektu
- ✅ **#file** - kontekst konkretnego pliku
- ✅ **#terminal** - kontekst terminala (błędy, logi)
- ✅ **Copilot CLI** - pomoc w komendach shell

**Ćwiczenia:**
1. Inline: Napisz sygnaturę metody, pozwól Copilotowi dokończyć
2. Chat: Zapytaj "Jak uruchomić Spring Boot na innym porcie?"
3. Agent Mode: "Stwórz projekt Spring Boot z Lombok i Web"
4. @workspace: "Znajdź wszystkie kontrolery w projekcie"
5. #terminal: Wklej błąd portu, zapytaj o rozwiązanie
6. CLI: `gh copilot suggest "jak znaleźć proces na porcie 8080"`

---

### **Moduł 2: Nawigacja i Konteksty**
**Funkcje Copilota:**
- ✅ **@workspace** - analiza architektury
- ✅ **Next Edit Suggestions** - przewidywanie kolejnych zmian
- ✅ **Symbol Search** - znajdowanie definicji
- ✅ **#codebase** - kontekst całej bazy kodu
- ✅ **Go to Definition** - nawigacja z Copilotem

**Ćwiczenia:**
1. @workspace: "Pokaż wszystkie encje JPA"
2. Next Edit: Zmień nazwę kolumny w encji, obserwuj sugestie w repo/service
3. Symbol Search: Zapytaj "Gdzie używana jest klasa TreasureEntity?"
4. #codebase: "Jakie wzorce projektowe są użyte w tym projekcie?"

---

### **Moduł 3: Chirurgiczny Refaktoring (Copilot Edits)**
**Funkcje Copilota:**
- ✅ **Edit Mode** - edycja wielu plików jednocześnie
- ✅ **Working Set** - zarządzanie kontekstem edycji
- ✅ **Refactoring Commands** - Extract Method, Rename, etc.
- ✅ **Multi-file Edits** - zmiany w wielu plikach
- ✅ **Preview Changes** - podgląd przed zatwierdzeniem

**Ćwiczenia:**
1. Edit Mode: "Rozbij GodClassController na 3 serwisy"
2. Working Set: Dodaj pliki do Working Set przed refaktoringiem
3. Extract Method: Zaznacz kod, poproś o ekstrakcję
4. Multi-file: "Zmień nazwę metody getUserData we wszystkich plikach"
5. Preview: Sprawdź zmiany przed zatwierdzeniem

---

### **Moduł 4: Testowanie**
**Funkcje Copilota:**
- ✅ **@test** - generowanie testów
- ✅ **Test Generation** - automatyczne testy jednostkowe
- ✅ **Mock Generation** - tworzenie mocków
- ✅ **Test Coverage** - analiza pokrycia testami
- ✅ **Characterization Tests** - testy dla legacy code

**Ćwiczenia:**
1. @test: "Wygeneruj testy JUnit 5 dla TreasureService"
2. Mock Generation: "Zmockuj TreasureRepository używając Mockito"
3. Test Coverage: "Jakie metody nie mają testów?"
4. Characterization: "Napisz testy dla legacy kodu bez dokumentacji"

---

### **Moduł 5: Konfiguracja i Narzucanie Zasad**
**Funkcje Copilota:**
- ✅ **Custom Instructions** - `.github/copilot-instructions.md`
- ✅ **Repository-wide Rules** - zasady dla całego repo
- ✅ **Code Style Enforcement** - wymuszanie stylu
- ✅ **Pattern Enforcement** - wymuszanie wzorców (Builder, Record)
- ✅ **Lombok Integration** - automatyczne używanie Lomboka

**Ćwiczenia:**
1. Custom Instructions: Stwórz `.github/copilot-instructions.md`
2. Enforce Records: "Wszystkie DTOs jako Java Records"
3. Enforce Builder: "Klasy z >3 parametrami używają @Builder"
4. Lombok: "Używaj @Data zamiast getterów/setterów"

---

### **Moduł 6: Model Context Protocol (MCP)**
**Funkcje Copilota:**
- ✅ **MCP Servers** - integracja z zewnętrznymi systemami
- ✅ **Database Schema Analysis** - analiza schematu bazy
- ✅ **Migration Generation** - generowanie migracji
- ✅ **External Tools** - integracja z Flyway/Liquibase
- ✅ **Custom MCP Server** - tworzenie własnego serwera

**Ćwiczenia:**
1. MCP: Podłącz SQLite przez MCP
2. Schema Analysis: "Pokaż schemat tabeli treasures"
3. Migration: "Wygeneruj migrację Flyway dla nowej kolumny"
4. Custom Server: Stwórz MCP server dla API zewnętrznego

---

### **Moduł 7: Wielkie Migracje i Custom Agents**
**Funkcje Copilota:**
- ✅ **Language Translation** - translacja Java → Python
- ✅ **Custom Agents** - tworzenie `@Reviewer`, `@Architect`
- ✅ **Subagents** - delegowanie zadań do sub-agentów
- ✅ **Plan Mode** - planowanie złożonych zmian
- ✅ **Self-Correction** - auto-korekta błędów

**Ćwiczenia:**
1. Translation: "Przetłumacz DiscountCalculator.java na Python"
2. Custom Agent: Stwórz `@Reviewer` do code review
3. Subagents: "Użyj @Architect do zaprojektowania architektury"
4. Plan Mode: "Zaplanuj migrację z Java 11 do Java 17"

---

### **Moduł 8: Grand Finale (React Frontend)**
**Funkcje Copilota:**
- ✅ **Polyglot Support** - Java + TypeScript
- ✅ **Component Generation** - generowanie komponentów React
- ✅ **API Integration** - podłączanie do Spring Boot API
- ✅ **Type Generation** - generowanie typów TS z Java
- ✅ **Full-Stack Context** - @workspace dla backend + frontend

**Ćwiczenia:**
1. Component: "Wygeneruj komponent TreasureList w React"
2. API Integration: "Podłącz axios do /api/treasures"
3. Type Generation: "Wygeneruj typy TS z TreasureDTO.java"
4. Full-Stack: "@workspace Stwórz dashboard dla API"

---

## 🚀 MODUŁY DODATKOWE (Advanced Features)

### **Moduł 9: Copilot w Terminalu**
- Copilot CLI (`gh copilot suggest`, `gh copilot explain`)
- Shell command generation
- Git commit messages
- Docker commands

### **Moduł 10: Copilot dla DevOps**
- GitHub Actions generation
- CI/CD pipeline creation
- Dockerfile optimization
- Kubernetes manifests

### **Moduł 11: Copilot dla Dokumentacji**
- @doc - generowanie dokumentacji
- README generation
- API documentation (Swagger/OpenAPI)
- Javadoc/JSDoc generation

### **Moduł 12: Advanced Agent Mode**
- Multi-step workflows
- Autonomous debugging
- Performance optimization
- Security scanning

---

## 📊 FUNKCJE COPILOTA (Pełna lista)

### **Tryby pracy:**
1. **Inline Suggestions** - autouzupełnianie w edytorze
2. **Chat Mode** - konwersacja z AI
3. **Edit Mode** - edycja wielu plików
4. **Agent Mode** - autonomiczne działanie

### **Slash commands (konteksty):**
- `@workspace` - cały projekt
- `@doc` - dokumentacja
- `@test` - testy
- `@terminal` - terminal/błędy
- `#file` - konkretny plik
- `#codebase` - cała baza kodu

### **Custom Instructions:**
- `.github/copilot-instructions.md` - zasady repo
- Path-specific instructions - zasady dla katalogów
- Language-specific rules - zasady dla języków

### **Advanced Features:**
- **Next Edit Suggestions** - przewidywanie zmian
- **MCP Servers** - integracja zewnętrzna
- **Custom Agents** - własne agenty (@Reviewer, @Architect)
- **Subagents** - delegowanie zadań
- **Plan Mode** - planowanie złożonych zmian
- **Self-Correction** - auto-korekta

### **Copilot CLI:**
- `gh copilot suggest` - sugestie komend
- `gh copilot explain` - wyjaśnianie komend

---

## 🎯 ZASADY GENEROWANIA ĆWICZEŃ:

1. ✅ **Nie generujemy przykładowych odpowiedzi** - student sam ćwiczy!
2. ✅ **Konkretne zadania** - "Zrób X używając funkcji Y"
3. ✅ **Małe przykłady** - focus na funkcji, nie na całym projekcie
4. ✅ **Wartość szkoleniowa** - każde ćwiczenie uczy konkretnej funkcji
5. ✅ **Common sense** - nie dublujemy, nie piszemy oczywistości

