# Moduł 2: Niestandardowe Narzędzie Python - Zarządzanie Inwentarzem

## 📚 Przegląd

W tym module nauczysz się wyposażać agenta w niestandardowe narzędzia - funkcje Python, które rozszerzają możliwości agenta poza zwykłą konwersację.

**Czas trwania:** 45 minut
**Poziom trudności:** Początkujący-Średniozaawansowany

## 🎯 Cele Edukacyjne

- Tworzenie funkcji Python służących jako narzędzia agenta
- Zrozumienie wymagań dla funkcji narzędziowych (docstringi, adnotacje typów)
- Przekazywanie narzędzi do LlmAgent przez parametr `tools`
- Obserwacja jak agenci decydują kiedy użyć konkretnych narzędzi

## 📁 Zawartość Modułu

```
module_02_custom_tool/
├── agent.py          # Agent z niestandardowymi funkcjami narzędziowymi
├── .env.template     # Konfiguracja środowiska
├── requirements.txt  # Zależności
└── README.md         # Ten plik
```

## 🚀 Szybki Start

```bash
cd adk_training/module_02_custom_tool
pip install -r requirements.txt
copy .env.template .env  # Edytuj i wpisz swój project ID
adk web
```

## 🔑 Kluczowe Koncepcje

### Wymagania dla Funkcji Narzędziowych

Każda funkcja narzędziowa MUSI mieć:

1. **Adnotacje typów** dla wszystkich parametrów i wartości zwracanej
2. **Docstring** opisujący co funkcja robi
3. **Jasne opisy parametrów** w docstringu

```python
def moje_narzedzie(param1: str, param2: int) -> str:
    """
    Krótki opis co to narzędzie robi.

    Args:
        param1: Opis pierwszego parametru
        param2: Opis drugiego parametru

    Returns:
        Opis tego co jest zwracane
    """
    # Implementacja
    return wynik
```

### Przekazywanie Narzędzi do Agenta

```python
root_agent = LlmAgent(
    name="nazwa_agenta",
    model="gemini-2.5-flash",
    instruction="...",
    tools=[funkcja_narzedzie_1, funkcja_narzedzie_2],  # Lista funkcji
)
```

### Jak Agenci Używają Narzędzi

1. Agent otrzymuje wiadomość użytkownika
2. Agent analizuje czy jakieś narzędzie pomoże w odpowiedzi
3. Jeśli tak, agent wywołuje narzędzie z odpowiednimi parametrami
4. Agent otrzymuje wynik narzędzia
5. Agent formułuje odpowiedź używając wyniku

## 🏋️ Ćwiczenia

### Ćwiczenie 2.1: Dodaj Nowe Narzędzie
Stwórz funkcję `remove_treasure()` która usuwa przedmioty z inwentarza.

### Ćwiczenie 2.2: Narzędzie z Walidacją
Dodaj walidację wejścia aby zapobiec ujemnym ilościom.

### Ćwiczenie 2.3: Wieloetapowe Użycie Narzędzi
Poproś agenta: "Dodaj 100 złotych dublonów a potem pokaż mi całkowitą wartość."
Obserwuj jak używa wielu narzędzi w sekwencji.

## 💡 Wskazówki

- **Docstringi są kluczowe** - Agent czyta je aby zrozumieć narzędzie
- **Trzymaj narzędzia skupione** - Jedno narzędzie, jeden cel
- **Zwracaj pomocne wiadomości** - Dołączaj kontekst w zwracanych wartościach
- **Obsługuj błędy elegancko** - Zwracaj komunikaty błędów, nie rzucaj wyjątków

## ❓ Częste Problemy

### Narzędzie Nie Jest Wywoływane
- Sprawdź czy docstring jasno opisuje kiedy użyć narzędzia
- Upewnij się że adnotacje typów są obecne
- Spróbuj być bardziej konkretny w swoim zapytaniu

### Przekazywane Są Złe Parametry
- Używaj opisowych nazw parametrów
- Dodaj przykłady w docstringu jeśli potrzeba

## 🎓 Co Dalej?

W **Module 3** nauczysz się o RAG (Retrieval-Augmented Generation) używając Vertex AI Search aby dać agentowi dostęp do ogromnych zasobów wiedzy!

---

*"Właściwe narzędzie do właściwej pracy ułatwia życie programisty."*

