# Module 01: Hello World Agent - Teoria i Koncepcje

## 📚 Spis Treści
1. [Wprowadzenie do LlmAgent](#wprowadzenie-do-llmagent)
2. [Architektura ADK](#architektura-adk)
3. [Kluczowe Koncepcje](#kluczowe-koncepcje)
4. [Przypadki Użycia Biznesowego](#przypadki-użycia-biznesowego)
5. [Najlepsze Praktyki](#najlepsze-praktyki)
6. [Typowe Pułapki](#typowe-pułapki)

---

## 🎯 Wprowadzenie do LlmAgent

### Czym jest LlmAgent?

**LlmAgent** to podstawowy building block w Google ADK (Agent Development Kit). Jest to wrapper wokół modelu LLM (Large Language Model), który:

- 🤖 Enkapsuluje model AI (np. Gemini)
- 💬 Zarządza konwersacją i kontekstem
- 🔧 Integruje narzędzia (tools)
- 📊 Śledzi stan sesji (state management)
- 🔄 Obsługuje callbacks i eventy

### Podstawowa Struktura

```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="nazwa_agenta",           # Unikalny identyfikator
    model="gemini-2.5-flash",      # Model LLM
    instruction="...",             # System prompt
    description="...",             # Opis dla innych agentów
    tools=[],                      # Lista narzędzi (opcjonalne)
)
```

---

## 🏗️ Architektura ADK

### Hierarchia Komponentów

```
┌─────────────────────────────────────────┐
│         ADK Framework                   │
│  ┌───────────────────────────────────┐  │
│  │      LlmAgent (Twój Agent)        │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   Gemini Model (LLM)        │  │  │
│  │  └─────────────────────────────┘  │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   Tools (Narzędzia)         │  │  │
│  │  └─────────────────────────────┘  │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   Session State (Stan)      │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Przepływ Danych

```
User Input → LlmAgent → Model (Gemini) → Response → User
                ↓
         Session State
         (pamięć konwersacji)
```

---

## 🔑 Kluczowe Koncepcje

### 1. **System Prompt (Instruction)**

**Instruction** to najważniejszy parametr - definiuje "osobowość" i zachowanie agenta.

**Dobre praktyki:**
- ✅ Jasno określ rolę agenta ("Jesteś ekspertem w...")
- ✅ Wymień konkretne zadania i obowiązki
- ✅ Podaj zasady komunikacji (ton, styl, język)
- ✅ Dodaj przykłady oczekiwanych zachowań
- ✅ Określ granice (czego agent NIE powinien robić)

**Przykład:**
```python
instruction="""Jesteś ekspertem ds. obsługi klienta w firmie technologicznej.

Twoje zadania:
1. Odpowiadanie na pytania o produkty
2. Rozwiązywanie problemów technicznych
3. Eskalacja skomplikowanych spraw do działu wsparcia

Zasady:
- Używaj przyjaznego, profesjonalnego tonu
- Zawsze pytaj o szczegóły przed udzieleniem odpowiedzi
- Jeśli czegoś nie wiesz, przyznaj się i zaproponuj alternatywę
"""
```

### 2. **Wybór Modelu**

ADK wspiera różne modele Gemini:

| Model | Szybkość | Koszt | Jakość | Użycie |
|-------|----------|-------|--------|--------|
| `gemini-2.5-flash` | ⚡⚡⚡ | 💰 | ⭐⭐⭐ | Codzienne zadania, chatboty |
| `gemini-2.0-flash` | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ | Stabilna wersja produkcyjna |
| `gemini-2.0-pro` | ⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ | Złożone analizy, kreatywność |

**Kiedy używać którego?**
- **Flash** - 90% przypadków użycia (szybki, tani, wystarczająco dobry)
- **Pro** - Gdy potrzebujesz najwyższej jakości (analiza prawna, medyczna, kreatywne pisanie)

### 3. **Name vs Description**

- **`name`**: Techniczny identyfikator (używany w logach, routingu)
  - Konwencja: `snake_case`, bez spacji
  - Przykład: `"asystent_obslugi_klienta"`

- **`description`**: Opis dla ludzi i innych agentów
  - Używany w systemach multi-agent do routingu
  - Przykład: `"Asystent obsługi klienta specjalizujący się w produktach technicznych"`

---

## 💼 Przypadki Użycia Biznesowego

### 1. **Obsługa Klienta (Customer Support)**

**Scenariusz:** Firma e-commerce potrzebuje chatbota do obsługi zapytań 24/7.

**Implementacja:**
```python
support_agent = LlmAgent(
    name="support_bot",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem obsługi klienta sklepu TechShop.

    Pomagasz klientom w:
    - Sprawdzaniu statusu zamówień
    - Zwrotach i reklamacjach
    - Pytaniach o produkty
    - Problemach technicznych

    Zawsze bądź uprzejmy i pomocny. Jeśli nie możesz pomóc,
    przekieruj do działu wsparcia: support@techshop.pl
    """
)
```

**Korzyści biznesowe:**
- ⏱️ Oszczędność czasu HR o 40% (automatyczne odpowiedzi na FAQ)
- 📧 Mniej emaili do działu HR
- 🎯 Lepsze doświadczenie kandydatów (szybkie odpowiedzi)
- 📊 Wstępny screening przed rozmową z rekruterem

### 3. **Asystent Sprzedaży (Sales Assistant)**

**Scenariusz:** Zespół sprzedaży potrzebuje wsparcia w generowaniu ofert i odpowiadaniu na pytania techniczne.

**Implementacja:**
```python
sales_agent = LlmAgent(
    name="sales_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem sprzedaży dla CloudMaster Pro.

    Produkt: CloudMaster Pro
    - Cena: od 499 PLN/miesiąc
    - Funkcje: zarządzanie chmurą, monitoring, automatyzacja
    - Plany: Starter, Business, Enterprise

    Twoje zadania:
    - Odpowiadanie na pytania o funkcje produktu
    - Porównywanie planów cenowych
    - Generowanie wstępnych ofert
    - Zbieranie wymagań klienta

    Zawsze podkreślaj wartość biznesową i ROI!
    """
)
```

**Korzyści biznesowe:**
- 🚀 Szybsze generowanie ofert (minuty zamiast godzin)
- 📈 Więcej leadów obsłużonych przez zespół
- 💡 Konsystentne informacje o produkcie
- 🎯 Lepsza kwalifikacja leadów

---

## ✅ Najlepsze Praktyki

### 1. **Projektowanie System Prompt**

**DO:**
- ✅ Używaj jasnego, strukturalnego języka
- ✅ Podawaj konkretne przykłady
- ✅ Definiuj granice odpowiedzialności
- ✅ Testuj różne wersje promptu
- ✅ Iteruj na podstawie feedbacku użytkowników

**NIE:**
- ❌ Nie pisz zbyt długich promptów (>2000 słów)
- ❌ Nie używaj niejasnych instrukcji
- ❌ Nie zakładaj że model "wie" kontekst Twojej firmy
- ❌ Nie mieszaj wielu ról w jednym agencie

### 2. **Wybór Nazwy Agenta**

**Dobre nazwy:**
- `asystent_obslugi_klienta`
- `hr_recruiter_bot`
- `sales_assistant_pl`

**Złe nazwy:**
- `agent1` (nieopisowe)
- `Asystent Obsługi` (spacje, polskie znaki)
- `super-mega-bot-2024` (zbyt długie)

### 3. **Testowanie Agenta**

**Proces testowania:**
1. **Testy jednostkowe** - pojedyncze pytania
2. **Testy scenariuszowe** - pełne konwersacje
3. **Testy brzegowe** - nietypowe zapytania
4. **Testy obciążeniowe** - wiele równoczesnych użytkowników

**Przykładowe pytania testowe:**
```python
test_cases = [
    "Cześć, kim jesteś?",                    # Podstawowe
    "Jakie są godziny otwarcia?",            # Informacyjne
    "Chcę złożyć reklamację",                # Akcja
    "asdfghjkl",                             # Nonsens
    "Czy możesz zhakować system?",           # Bezpieczeństwo
]
```

### 4. **Monitorowanie i Optymalizacja**

**Metryki do śledzenia:**
- 📊 Średni czas odpowiedzi
- 💰 Koszt na zapytanie (tokeny)
- 😊 Satysfakcja użytkowników (feedback)
- 🔄 Liczba eskalacji do człowieka
- ⚠️ Liczba błędnych odpowiedzi

---

## ⚠️ Typowe Pułapki

### 1. **Zbyt Ogólny System Prompt**

**Źle:**
```python
instruction="Jesteś pomocnym asystentem."
```

**Dobrze:**
```python
instruction="""Jesteś asystentem obsługi klienta w firmie TechShop.
Specjalizujesz się w produktach elektronicznych.
Odpowiadasz tylko na pytania związane z naszymi produktami i usługami.
Jeśli pytanie dotyczy innych tematów, grzecznie przekieruj do odpowiedniego działu."""
```

### 2. **Brak Walidacji Wejścia**

**Problem:** Agent odpowiada na wszystko, nawet na niewłaściwe pytania.

**Rozwiązanie:**
```python
instruction="""...
WAŻNE: Jeśli pytanie nie dotyczy naszych produktów lub usług,
odpowiedz: "Przepraszam, mogę pomóc tylko w sprawach związanych z produktami TechShop.
Czy masz pytanie o nasze produkty?"
"""
```

### 3. **Ignorowanie Kosztów**

**Problem:** Używanie `gemini-2.0-pro` do prostych zadań.

**Rozwiązanie:**
- Używaj `gemini-2.5-flash` dla 90% przypadków
- Rezerwuj `pro` dla złożonych analiz
- Monitoruj koszty w Google Cloud Console

### 4. **Brak Obsługi Błędów**

**Problem:** Agent nie wie co zrobić gdy nie zna odpowiedzi.

**Rozwiązanie:**
```python
instruction="""...
Jeśli nie znasz odpowiedzi:
1. Przyznaj się uczciwie: "Nie mam pewności co do tej informacji"
2. Zaproponuj alternatywę: "Mogę przekierować Cię do działu wsparcia"
3. Nigdy nie wymyślaj informacji!
"""
```

### 5. **Brak Testowania w Kontekście Biznesowym**

**Problem:** Agent działa w testach, ale zawodzi w produkcji.

**Rozwiązanie:**
- Testuj z prawdziwymi danymi klientów (zanonimizowanymi)
- Przeprowadź testy A/B z małą grupą użytkowników
- Zbieraj feedback i iteruj

---

## 🔗 Odniesienia do Dokumentacji ADK

### Oficjalna Dokumentacja
- [ADK Overview](https://google.github.io/adk-docs/)
- [LlmAgent API Reference](https://google.github.io/adk-docs/agents/llm-agent/)
- [Gemini Models](https://ai.google.dev/gemini-api/docs/models)

### Przykłady i Tutoriale
- [ADK Quickstart](https://google.github.io/adk-docs/quickstart/)
- [Building Your First Agent](https://google.github.io/adk-docs/tutorials/first-agent/)

---

## 📝 Podsumowanie

**Kluczowe wnioski z Module 01:**

1. **LlmAgent** to fundament ADK - prosty ale potężny
2. **System Prompt** to najważniejszy parametr - inwestuj czas w jego optymalizację
3. **Wybór modelu** ma znaczenie - balansuj koszt vs jakość
4. **Testowanie** jest kluczowe - nie wdrażaj bez testów
5. **Iteracja** to klucz do sukcesu - zbieraj feedback i ulepszaj

**Następne kroki:**
- Module 02: Dodawanie niestandardowych narzędzi (tools)
- Module 03: RAG - integracja z bazami wiedzy
- Module 04: Multi-agent systems - orkiestracja wielu agentów

---

*"Każda wielka podróż zaczyna się od pierwszego agenta!"* 🚀
**Korzyści biznesowe:**
- 📉 Redukcja kosztów wsparcia o 60-80%
- ⏰ Dostępność 24/7 bez dodatkowych kosztów
- 📈 Szybsze czasy odpowiedzi (sekundy vs minuty)
- 😊 Lepsza satysfakcja klientów

### 2. **Asystent HR (Rekrutacja)**

**Scenariusz:** Dział HR potrzebuje pomocy w screeningu CV i odpowiadaniu na pytania kandydatów.

**Implementacja:**
```python
hr_agent = LlmAgent(
    name="hr_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem HR w firmie TechCorp.

    Pomagasz w:
    - Odpowiadaniu na pytania o proces rekrutacji
    - Informowaniu o benefitach i kulturze firmy
    - Zbieraniu podstawowych informacji od kandydatów

    Benefity TechCorp:
    - Praca zdalna/hybrydowa
    - Prywatna opieka medyczna
    - Budżet szkoleniowy 5000 PLN/rok
    - 26 dni urlopu
    """
)
```


