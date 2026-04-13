# Moduł 8: Agent Pętli z Krytyką - Iteracyjne Doskonalenie

## 📋 Przegląd

Naucz się implementować **iteracyjne doskonalenie** używając `LoopAgent`. Ten wzorzec jest niezbędny dla przepływów pracy skupionych na jakości, gdzie wynik musi spełniać określone kryteria przed uznaniem go za gotowy. Pętla powtarza się, dopóki krytyk nie zatwierdzi wyniku lub nie zostanie osiągnięty maksymalny limit iteracji.

## 🎯 Cele Edukacyjne

Po ukończeniu tego modułu będziesz:
- Rozumieć jak `LoopAgent` wielokrotnie iteruje przez pod-agentów (`sub_agents`).
- Używać `output_schema` do wymuszenia ustrukturyzowanych, przewidywalnych decyzji od LLM.
- Tworzyć niestandardowego agenta (`BaseAgent`) do kontroli logiki pętli.
- Używać zdarzenia `EventActions(escalate=True)`, aby bezpiecznie przerwać wykonywanie `LoopAgent`.

## 🗂️ Pliki

```text
module_08_loop_critique/
├── agent.py          # Pętla bazowa: Dziennik pokładowy
├── agent_solution.py # Rozwiązania zadań z różnymi wariantami ocen
├── teoria.md         # Omówienie wzorców
├── README.md         # Ten plik
├── requirements.txt  # Zależności
└── .env.template     # Szablon środowiska
```

## 🚀 Szybki Start

```bash
# 1. Skopiuj szablon środowiska
copy .env.template .env

# 2. Edytuj .env ze swoim projektem Google Cloud
notepad .env

# 3. Zainstaluj zależności
pip install -r requirements.txt

# 4. Uruchom z interfejsem webowym ADK
adk web
```

## 💡 Scenariusz Bazowy (`agent.py`)

Proces tworzenia dziennika okrętowego wymaga perfekcji:
1. **Pisarz** - Tworzy nową wersję wpisu.
2. **Pierwszy Oficer (Krytyk)** - Ocenia wersję roboczą i daje wskazówki.
3. **Kapitan (Decydent)** - Decyduje na podstawie wytycznych, czy wpis zostaje zatwierdzony (`is_approved`). Zwraca te dane jako ustrukturyzowany JSON.
4. **Kontroler Pętli (Python)** - Zagląda do decyzji Kapitana i jeśli wynosi ona `True`, wywołuje `escalate=True`, natychmiast kończąc pętlę.

## 🔑 Kluczowe Koncepcje

### 1. LoopAgent z Limitem
```python
root_agent = LoopAgent(
    name="petla_doskonalenia",
    max_iterations=5,  # Zabezpieczenie przed nieskończoną pętlą!
    sub_agents=[autor, krytyk, decydent, kontroler]
)
```

### 2. Wymuszanie Decyzji z `output_schema`
```python
from pydantic import BaseModel, Field

class DecyzjaWpisu(BaseModel):
    is_approved: bool = Field(description="Zwróć True, jeśli akceptujesz")
    feedback: str = Field(description="Wyjaśnienie / Sugestie poprawek")

captain = LlmAgent(
    output_key="entry_status",
    output_schema=DecyzjaWpisu  # Model LLM zwróci strukturę zgodną z tą klasą
)
```

### 3. Sterowanie Pętlą za pomocą Eventów (Kontroler)
W ADK v1.0+ do przerwania pętli stosujemy niestandardowego Agenta napisanego w Pythonie, który rzuca zdarzenie przerwania:
```python
class SprawdzStatusIEskaluj(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        # Pobieramy wynik z pamięci współdzielonej agentów (state)
        status = ctx.session.state.get("entry_status", {})
        should_stop = status.get("is_approved", False)
        
        # escalate=True przerywa pętlę
        yield Event(
            author=self.name,
            actions=EventActions(escalate=should_stop)
        )
```

## 💬 Przykładowe Zapytania do ADK Web

1. **„Napisz dzisiejszy wpis do dziennika operacyjnego z rejsu na północ”**
2. **„Udokumentuj potyczkę z kupieckim statkiem z dzisiejszego poranka”**
3. **„Zapisz szczegóły o buncie załogi i racjonowaniu rumu”**

Obserwuj logi, aby zobaczyć, jak Pisarz i Krytyk "kłócą się", dopóki Kapitan nie zaakceptuje wpisu!

## 🧪 Ćwiczenia (Sprawdź `agent_solution.py`)

Zaimplementuj i przeanalizuj warianty z pliku rozwiązania:
1. **Wdrożenie Agenta Zliczającego**: Zbuduj callback (funkcję pythonową w parametrze `before_agent_callback`), który zlicza aktualną iterację.
2. **Krytyk Punktowy**: Zamień ocenę opisową na punktację (1-10) i uzależnij pole `is_approved` od średniej, która przekracza ocenę 8.0.
3. **Wyspecjalizowani Krytycy**: Stwórz osobne pętle dla tworzenia *postów na Social Media*, tworzenia *maili* i pisania *artykułów na bloga*.