# Module 07: Parallel Agent - Teoria

## 🎯 Kluczowe Koncepcje

### ParallelAgent - Równoległe Wykonanie

**ParallelAgent** uruchamia wszystkich sub-agentów **jednocześnie** (równolegle).

```python
parallel = ParallelAgent(
    name="team",
    sub_agents=[agent1, agent2, agent3]  # Wszyscy startują razem!
)
```

### Sequential vs Parallel

| Aspekt | Sequential | Parallel |
|--------|-----------|----------|
| **Wykonanie** | Po kolei (A→B→C) | Równocześnie (A+B+C) |
| **Czas** | Suma czasów | Max z czasów |
| **Zależności** | B czeka na A | Niezależni |
| **Użycie** | Pipeline, workflow | Niezależne zadania |

### Kiedy Używać Parallel?

✅ **Używaj gdy:**
- Zadania są **niezależne** (nie potrzebują wyników innych)
- Chcesz **zaoszczędzić czas** (równoległość)
- Potrzebujesz **wielu perspektyw** na ten sam problem

❌ **NIE używaj gdy:**
- Agent B potrzebuje wyniku Agenta A (użyj Sequential)
- Zadania muszą być w określonej kolejności

---

## 💼 Przypadki Użycia Biznesowego

### 1. Analiza Dokumentów: Wiele Perspektyw

```python
legal_analyst = LlmAgent(
    instruction="Oceń dokument pod kątem prawnym",
    output_key="legal_review"
)

financial_analyst = LlmAgent(
    instruction="Oceń dokument pod kątem finansowym",
    output_key="financial_review"
)

compliance_analyst = LlmAgent(
    instruction="Oceń dokument pod kątem compliance",
    output_key="compliance_review"
)

parallel_review = ParallelAgent(
    sub_agents=[legal_analyst, financial_analyst, compliance_analyst]
)
```

**Korzyści:** 3x szybciej niż sekwencyjnie, różne perspektywy, kompleksowa analiza.

### 2. Badanie Rynku: Konkurencja

```python
competitor_a_analyst = LlmAgent(
    instruction="Przeanalizuj Competitor A",
    output_key="competitor_a"
)

competitor_b_analyst = LlmAgent(
    instruction="Przeanalizuj Competitor B",
    output_key="competitor_b"
)

market_trends_analyst = LlmAgent(
    instruction="Przeanalizuj trendy rynkowe",
    output_key="market_trends"
)

market_research = ParallelAgent(
    sub_agents=[competitor_a_analyst, competitor_b_analyst, market_trends_analyst]
)
```

### 3. Due Diligence: Ocena Startupu

```python
tech_dd = LlmAgent(instruction="Oceń technologię", output_key="tech")
business_dd = LlmAgent(instruction="Oceń model biznesowy", output_key="business")
team_dd = LlmAgent(instruction="Oceń zespół", output_key="team")
market_dd = LlmAgent(instruction="Oceń rynek", output_key="market")

due_diligence = ParallelAgent(
    sub_agents=[tech_dd, business_dd, team_dd, market_dd]
)
```

---

## ✅ Najlepsze Praktyki

### 1. Parallel + Sequential = Potęga

```python
# Krok 1: Parallel - zbierz dane
parallel_data_collection = ParallelAgent(
    sub_agents=[source1, source2, source3]
)

# Krok 2: Sequential - agreguj
aggregator = LlmAgent(
    instruction="Podsumuj: {source1} {source2} {source3}",
    output_key="summary"
)

# Połącz
pipeline = SequentialAgent(
    sub_agents=[parallel_data_collection, aggregator]
)
```

### 2. Obsługa Konfliktów

```python
conflict_resolver = LlmAgent(
    instruction="""Rozwiąż konflikty między raportami:
    
    {report1}
    {report2}
    {report3}
    
    Jeśli sprzeczne rekomendacje:
    1. Zidentyfikuj konflikt
    2. Oceń wiarygodność każdego źródła
    3. Podaj ostateczną rekomendację z uzasadnieniem
    """,
    output_key="final_decision"
)
```

### 3. Wagi i Priorytety

```python
decision_maker = LlmAgent(
    instruction="""Oceń raporty z wagami:
    
    Security (waga: 40%): {security_report}
    Performance (waga: 30%): {performance_report}
    Cost (waga: 20%): {cost_report}
    UX (waga: 10%): {ux_report}
    
    Oblicz ważoną ocenę i podaj rekomendację.
    """
)
```

### 4. Timeout dla Wolnych Agentów

W produkcji: ustaw timeout aby jeden wolny agent nie blokował całości.

```python
# Koncepcyjnie (wymaga custom implementacji):
parallel = ParallelAgent(
    sub_agents=[fast_agent, slow_agent],
    timeout=60  # Maksymalnie 60s na wszystkich
)
```

---

## ⚠️ Typowe Pułapki

### 1. Zależności Między Agentami

**Problem:** Agent B potrzebuje wyniku Agenta A, ale są w Parallel.

**Rozwiązanie:** Użyj Sequential lub podziel na etapy:
```python
# ❌ ŹLE - B potrzebuje A
ParallelAgent(sub_agents=[agent_a, agent_b])

# ✅ DOBRZE
SequentialAgent(sub_agents=[agent_a, agent_b])
```

### 2. Zbyt Wiele Agentów Równolegle

**Problem:** 20 agentów równolegle → wysokie koszty, rate limits.

**Rozwiązanie:** Ogranicz do 3-5 agentów równolegle.

### 3. Brak Agregacji Wyników

**Problem:** 4 agentów zwraca 4 różne raporty → użytkownik musi sam agregować.

**Rozwiązanie:** Dodaj agenta agregującego:
```python
SequentialAgent(sub_agents=[
    ParallelAgent(sub_agents=[a1, a2, a3]),
    aggregator  # Agreguje wyniki
])
```

### 4. Ignorowanie Konfliktów

**Problem:** Agent1 mówi "GO", Agent2 mówi "NO-GO" → co teraz?

**Rozwiązanie:** Dodaj conflict resolver (patrz najlepsze praktyki).

---

## 🔗 Odniesienia ADK

- [ParallelAgent Docs](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agent/)
- [Workflow Patterns](https://google.github.io/adk-docs/patterns/workflows/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **ParallelAgent** | Uruchamia agentów równocześnie |
| **Szybkość** | Max(czas agentów) zamiast Sum(czas) |
| **Niezależność** | Agenci nie mogą zależeć od siebie |
| **Agregacja** | Dodaj agenta agregującego wyniki |
| **Konflikty** | Dodaj conflict resolver |
| **Limit** | 3-5 agentów równolegle (optymalne) |

**Następny krok:** Module 08 - Loop Critique (iteracyjne doskonalenie)

