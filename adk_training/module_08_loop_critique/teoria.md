# Module 08: Loop Critique - Teoria

## 🎯 Kluczowe Koncepcje

### LoopAgent - Iteracyjne Doskonalenie

**LoopAgent** powtarza wykonanie przypisanych mu agentów w pętli. Aby kontrolować moment wyjścia z pętli w najnowszym ADK, używamy strukturalnego wyjścia (Pydantic) oraz małego, niestandardowego agenta kontrolnego, który zgłasza akcję przerwania (`escalate=True`).

### Wzorzec: Creator-Critic (Twórca-Krytyk)

Ten wzorzec to serce iteracyjnego udoskonalania. Pętla zazwyczaj wygląda tak:
1. **Creator** → tworzy lub poprawia draft
2. **Critic** → ocenia treść i zwraca ocenę w formie ustrukturyzowanej (JSON)
3. **Controller** → odczytuje ocenę i jeśli jakość jest odpowiednia, przerywa pętlę.

```text
Iteracja 1: Creator → tworzy draft → Critic → ocenia na 5/10 → Controller → CONTINUE
Iteracja 2: Creator → poprawia draft → Critic → ocenia na 7/10 → Controller → CONTINUE
Iteracja 3: Creator → finalizuje → Critic → ocenia na 9/10 → Controller → STOP
```

---

## 💼 Jak zaimplementować pętlę (Najlepsze Praktyki ADK)

### 1. Definicja Schematu (Pydantic)
Agent-Krytyk musi zwracać konkretne dane, na których będzie można oprzeć logikę w Pythonie.

```python
from pydantic import BaseModel, Field

class DecyzjaKrytyka(BaseModel):
    is_approved: bool = Field(description="True jeśli jakość jest >= 8/10")
    feedback: str = Field(description="Co należy poprawić")
```

### 2. Definicja Kontrolera Pętli (BaseAgent)
Kontroler to niestandardowy agent. Zagląda on do stanu sesji i jeśli `is_approved` wynosi `True`, zgłasza przedwczesne wyjście z pętli za pomocą `EventActions(escalate=True)`.

```python
from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions

class LoopController(BaseAgent):
    async def _run_async_impl(self, ctx):
        ocena = ctx.session.state.get("critique", {})
        is_approved = ocena.get("is_approved", False)
        
        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_approved)  # Jeśli True, wychodzi z pętli
        )
```

### 3. Złożenie Całości

```python
writer = LlmAgent(
    instruction="Napisz/popraw treść bazując na feedbacku: {critique}",
    output_key="draft"
)

editor = LlmAgent(
    instruction="Oceń treść: {draft}. Zwróć ustrukturyzowaną decyzję.",
    output_key="critique",
    output_schema=DecyzjaKrytyka  # <- Wymusza zwrócenie JSONa
)

controller = LoopController(name="kontroler")

content_loop = LoopAgent(
    sub_agents=[writer, editor, controller],
    max_iterations=5  # <- Zawsze ustawiaj limit bezpieczeństwa!
)
```

---

## ✅ Najlepsze Praktyki i Optymalizacja

### 1. Ustaw Rozsądny `max_iterations`

| Typ Zadania | Zalecane max_iterations |
|-------------|-------------------------|
| Proste (email, post) | 3 |
| Średnie (artykuł, kod) | 5 |
| Złożone (raport, design) | 7-10 |

**Uwaga:** Każda iteracja to koszt wykonania modelu LLM! Nigdy nie zostawiaj nieskończonej pętli.

### 2. Feedback Musi Być Konstruktywny

**❌ Zły feedback:** "To jest złe. Popraw."
**✅ Dobry feedback:**
"Problemy:
1. Brak jasnego CTA - dodaj na końcu.
2. Zbyt długie zdania - skróć do max 20 słów.
   Zachowaj: dobry hook w pierwszym akapicie."

### 3. Trwałość Stanu
Pamiętaj, że wewnątrz `LoopAgent` wszyscy agenci współdzielą ten sam stan kontekstu (`state`). Oznacza to, że Creator ma dostęp do klucza zapisanego przez Krytyka (i na odwrót).

---

## ⚠️ Typowe Pułapki

### 1. Nieskończona Pętla (Brak max_iterations)
**Problem:** Zapomniałeś ustawić `max_iterations` (albo kontroler nie działa poprawnie) i pętla "zjada" tokeny bez końca.
**Rozwiązanie:** ZAWSZE ustaw `max_iterations`. Zabezpiecza to przed błędami logicznymi modelu.

### 2. Brak Postępu Między Iteracjami
**Problem:** Twórca (Creator) ignoruje feedback i w każdej iteracji generuje identyczny tekst.
**Rozwiązanie:** Napisz wprost w instrukcji Creatora: "MUSISZ uwzględnić feedback z poprzedniej iteracji: {critique}".

### 3. Zbyt Surowy Critic
**Problem:** Krytyk zawsze wymaga poprawek, przez co pętla zawsze dochodzi do limitu `max_iterations` bez akceptacji.
**Rozwiązanie:** Ustaw realistyczne progi (np. 7.5/10 zamiast wymagania 10/10) w instrukcjach dla modelu.

---

**Następny krok:** Module 09 - Database Simple (integracja z bazą danych)