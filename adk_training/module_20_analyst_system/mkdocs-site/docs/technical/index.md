# Prezentacja techniczna

## Podsumowanie techniczne

Analyst System to wieloagentowa platforma zbudowana na Google ADK, wykorzystująca modele Gemini do automatyzacji zadań analitycznych.

---

## Architektura w liczbach

| Metryka | Wartość |
|---------|---------|
| Pliki implementacji | 36+ |
| Orkiestratory | 6 |
| Wyspecjalizowani agenci | 12 |
| Wbudowane skille | 4 |
| Szablony dokumentów | 4 |
| Testy E2E | 16 (wszystkie przechodzą) |
| Linie kodu | ~2 300 |

---

## Stack technologiczny

```mermaid
graph TB
    subgraph "Warstwa aplikacji"
        ADK["🤖 Google ADK<br/><small>Agent Development Kit</small>"]
        PY["🐍 Python 3.11+"]
        PD["📋 Pydantic v2<br/><small>Walidacja danych</small>"]
    end

    subgraph "Modele AI"
        GF["⚡ Gemini 2.5 Flash<br/><small>Domyślny — szybki</small>"]
        GP["🧠 Gemini 2.5 Pro<br/><small>Złożone zadania</small>"]
    end

    subgraph "Integracje"
        MCP["🔌 Comarch MCP<br/><small>Model Context Protocol</small>"]
        AS["📚 agentskills.io<br/><small>Agent Skills spec</small>"]
    end

    subgraph "Infrastruktura"
        JI["📋 Jira"]
        WI["📖 Confluence"]
        GL["🔀 GitLab"]
    end

    ADK --> GF
    ADK --> GP
    ADK --> MCP
    ADK --> AS
    MCP --> JI
    MCP --> WI
    MCP --> GL

    style ADK fill:#37474f,color:#fff,stroke:none
    style GF fill:#4caf50,color:#fff,stroke:none
    style GP fill:#00897b,color:#fff,stroke:none
    style MCP fill:#009688,color:#fff,stroke:none
```

---

<div class="grid-cards" markdown>

<div class="card" markdown>
[:octicons-arrow-right-24: **Stack technologiczny**](stack.md)

Pełna lista technologii i zależności
</div>

<div class="card" markdown>
[:octicons-arrow-right-24: **Konfiguracja i uruchomienie**](setup.md)

Jak skonfigurować i uruchomić system
</div>

</div>
