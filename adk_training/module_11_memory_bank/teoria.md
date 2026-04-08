# Module 11: Memory Bank - Teoria

## 🎯 Kluczowe Koncepcje

### MemoryBank - Pamięć Długoterminowa

**MemoryBank** przechowuje informacje **między sesjami** - agent pamięta wcześniejsze rozmowy.

```python
from google.adk.sessions.memory import MemoryBank

memory = MemoryBank()

agent = LlmAgent(
    memory=memory  # Agent ma dostęp do pamięci
)
```

### Różnica: Session State vs Memory Bank

| Aspekt | Session State | Memory Bank |
|--------|---------------|-------------|
| **Zasięg** | Jedna sesja | Wiele sesji |
| **Trwałość** | Tymczasowe | Persystentne |
| **Użycie** | Przepływ danych w pipeline | Długoterminowa wiedza |
| **Przykład** | Wynik agenta w SequentialAgent | Preferencje użytkownika |

### PreloadMemoryTool

**PreloadMemoryTool** automatycznie ładuje relevantne wspomnienia na początku każdej tury.

```python
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

preload = PreloadMemoryTool()

agent = LlmAgent(
    tools=[preload],  # Auto-ładuje wspomnienia
    memory=memory_bank
)
```

---

## 💼 Przypadki Użycia Biznesowego

### 1. Asystent Osobisty - Preferencje Użytkownika

```python
memory = MemoryBank()

personal_assistant = LlmAgent(
    instruction="""Jesteś osobistym asystentem.
    
    Zapamiętuj:
    - Preferencje użytkownika
    - Ważne daty (urodziny, spotkania)
    - Nawyki i rutyny
    - Cele długoterminowe
    """,
    memory=memory
)
```

**Przykład:**
```
Sesja 1:
User: "Lubię kawę bez cukru"
Agent: "Zapamiętam!"

Sesja 2 (następny dzień):
User: "Zamów mi kawę"
Agent: "Zamawiam kawę bez cukru, jak lubisz!"
```

### 2. Customer Support - Historia Klienta

```python
support_agent = LlmAgent(
    instruction="""Zapamiętuj historię interakcji z klientem:
    - Wcześniejsze problemy
    - Rozwiązania które zadziałały
    - Preferencje komunikacji
    """,
    memory=memory_bank
)
```

**Korzyści:** Personalizacja, brak powtarzania pytań, lepsza obsługa.

### 3. Sales - Relacje z Klientami

```python
sales_agent = LlmAgent(
    instruction="""Zapamiętuj:
    - Potrzeby biznesowe klienta
    - Budżet i timeline
    - Decydenci w firmie
    - Wcześniejsze oferty
    """,
    memory=memory_bank
)
```

---

## ✅ Najlepsze Praktyki

### 1. Co Zapamiętywać?

**✅ Zapamiętuj:**
- Preferencje użytkownika
- Ważne fakty i daty
- Decyzje i uzgodnienia
- Kontekst długoterminowy

**❌ NIE zapamiętuj:**
- Tymczasowych danych (użyj session state)
- Wrażliwych danych (hasła, karty kredytowe)
- Danych które się często zmieniają

### 2. Strukturyzacja Wspomnień

```python
# ❌ Źle - chaotyczne
memory.add("Użytkownik lubi kawę i ma spotkanie jutro")

# ✅ Dobrze - strukturalne
memory.add("[PREFERENCE] Kawa: bez cukru, z mlekiem")
memory.add("[EVENT] Spotkanie z klientem: 2024-03-15 14:00")
memory.add("[GOAL] Cel Q1: zwiększyć sprzedaż o 20%")
```

### 3. Kategoryzacja

```python
def save_categorized_memory(content: str, category: str):
    """
    Kategorie: work, personal, preferences, goals, events
    """
    tagged = f"[{category.upper()}] {content}"
    memory_bank.add(tagged)
```

### 4. Czyszczenie Starych Wspomnień

```python
# Regularnie usuwaj nieaktualne wspomnienia
def cleanup_old_memories(days_old: int = 90):
    """Usuń wspomnienia starsze niż X dni."""
    # Implementacja zależna od backend
    pass
```

---

## ⚠️ Typowe Pułapki

### 1. Przechowywanie Wrażliwych Danych

**Problem:** Hasła, dane karty w Memory Bank.

**Rozwiązanie:** NIGDY nie przechowuj wrażliwych danych. Użyj bezpiecznego storage.

### 2. Brak Kategoryzacji

**Problem:** Wszystkie wspomnienia w jednym worku → trudne wyszukiwanie.

**Rozwiązanie:** Taguj wspomnienia kategoriami.

### 3. Zbyt Dużo Wspomnień

**Problem:** Tysiące wspomnień → wolne wyszukiwanie, wysokie koszty.

**Rozwiązanie:** 
- Regularnie czyść stare wspomnienia
- Priorytetyzuj ważne wspomnienia
- Używaj semantic search (tylko relevantne)

### 4. Brak Walidacji

**Problem:** Agent zapamiętuje nieprawdziwe informacje.

**Rozwiązanie:** Waliduj przed zapisem:
```python
def save_memory(content: str, confidence: float):
    if confidence < 0.7:
        return "⚠️ Niska pewność - czy na pewno zapamiętać?"
    memory_bank.add(content)
```

---

## 🔗 Odniesienia ADK

- [Memory Bank Docs](https://google.github.io/adk-docs/sessions/memory/)
- [PreloadMemoryTool](https://google.github.io/adk-docs/tools/preload-memory/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **MemoryBank** | Pamięć między sesjami |
| **PreloadMemoryTool** | Auto-ładuje relevantne wspomnienia |
| **Kategoryzacja** | Taguj wspomnienia dla łatwiejszego wyszukiwania |
| **Bezpieczeństwo** | NIE przechowuj wrażliwych danych |
| **Czyszczenie** | Regularnie usuwaj stare wspomnienia |

**Następny krok:** Module 12 - Router Agent (routing do specjalistycznych agentów)

