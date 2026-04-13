# Moduł 7: Agent Równoległy - "Rada Załogi"

## 📚 Briefing Misji

Naucz się uruchamiać wielu agentów **jednocześnie** używając `ParallelAgent`. To jest kluczowe gdy potrzebujesz zbierać informacje z wielu źródeł naraz lub generować różnorodne perspektywy równolegle.

## 🎯 Cele Edukacyjne

Po ukończeniu tego modułu będziesz:
- Rozumieć jak `ParallelAgent` wykonuje agentów współbieżnie
- Wiedzieć że równoległy agenci działają w **izolowanych kontekstach**
- Znać wzorzec łączenia `ParallelAgent` z syntezatorem
- Agregować wyniki od wielu równoległych agentów

## 🗂️ Pliki

```
module_07_parallel_agent/
├── agent.py          # Równoległa misja rozpoznawcza
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

## 🎯 Scenariusz

Trzej zwiadowcy eksplorują różne kierunki jednocześnie:
- **Zwiadowca Północny** - Obserwuje ruchy wroga i pogodę
- **Zwiadowca Południowy** - Znajduje ukryte zatoczki i trasy kupieckie
- **Zwiadowca Wschodni** - Monitoruje porty i floty rybackie

**Szpiegmistrz** następnie syntetyzuje wszystkie raporty w zunifikowany briefing wywiadowczy.

## 🔑 Kluczowe Koncepcje

### ParallelAgent
```python
parallel_scouts = ParallelAgent(
    name="grupa_zwiadowcza",
    sub_agents=[north_scout, south_scout, east_scout]
)
```

- Wszystkie sub_agents działają **współbieżnie** (nie sekwencyjnie)
- Każdy agent działa w **izolowanym kontekście**
- Każdy agent zapisuje do własnego `output_key`
- Czas wykonania = najwolniejszy agent (nie suma wszystkich)

### Wzorzec Agregacji
```python
# Krok 1: Równoległe wykonanie
parallel_scouts = ParallelAgent(sub_agents=[...])

# Krok 2: Syntezator czyta wszystkie wyniki
spymaster = LlmAgent(
    instruction="Połącz: {raport_polnocny}, {raport_poludniowy}, {raport_wschodni}"
)

# Krok 3: Sekwencyjna otoczka
root_agent = SequentialAgent(
    sub_agents=[parallel_scouts, spymaster]
)
```

## 💬 Przykładowe Zapytania

Wypróbuj te w interfejsie webowym ADK:

1. **"Jakie okazje istnieją na rajd w tym tygodniu?"**
2. **"Znajdź najbezpieczniejszą trasę do Port Królewskiego"**
3. **"Gdzie powinniśmy się ukryć przed Marynarką?"**
4. **"Jaka jest prognoza pogody na najbliższe dni?"**

## ⚠️ Ważne Uwagi

1. **Izolowane Konteksty**: Równoległy agenci nie widzą pracy innych
2. **Brak Współdzielonego Stanu**: Każda równoległa gałąź ma własny stan sesji
3. **Wymagana Agregacja**: Użyj syntezatora aby połączyć wyniki
4. **Wydajność**: Świetne dla zadań I/O-bound, mniejsza korzyść dla CPU-bound

## 🧪 Ćwiczenia

### Ćwiczenie 1: Dodaj Czwartego Zwiadowcę
Dodaj `zwiadowca_zachodni` który monitoruje:
- Trasy ucieczki o zachodzie słońca
- Zachodnie wiatry handlowe
- Odległe łańcuchy wysp

Zaktualizuj instrukcję szpiegmistrza aby zawierała `{raport_zachodni}`.

### Ćwiczenie 2: Wyspecjalizowani Zwiadowcy
Stwórz zwiadowców ze specjalistyczną wiedzą:
- `ekspert_pogodowy` - Skupia się tylko na pogodzie
- `analityk_wojskowy` - Skupia się na ruchach marynarki
- `specjalista_handlowy` - Skupia się na okazjach kupieckich

### Ćwiczenie 3: Wzorzec Głosowania
Zamiast syntezy, zaimplementuj wzorzec głosowania gdzie każdy zwiadowca "głosuje" na najlepszą akcję, a szpiegmistrz liczy głosy.

## 🔗 Następne Kroki

- **Moduł 8**: Loop Agent - Iteracyjne udoskonalanie z krytyką
- **Zaawansowane**: Połącz wzorce równoległe + pętlowe

## 📚 Referencje

- [Dokumentacja ADK ParallelAgent](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agent/)
- [Wzorce Multi-Agent](https://google.github.io/adk-docs/agents/multi-agents/)

