# Architektura

## Topologia systemu

Analyst System to platforma wieloagentowa z centralnym routerem i dwoma pętlami przetwarzania.

```mermaid
graph TB
    subgraph ENTRY ["Punkt wejścia"]
        U["Użytkownik"] --> CAP["Analyst Captain"]
    end

    subgraph REALIZE ["Pętla realizacji"]
        AR["Analiza wymagań"]
        CE["Tworzenie epików"]
        GD["Generowanie dokumentów"]
        GT["Plany testów"]
        RD["Recenzja dokumentów"]
    end

    subgraph LEARN ["Pętla wiedzy"]
        GS["Tworzenie umiejętności"]
    end

    subgraph DATA ["Baza wiedzy"]
        CT["Kontrakt projektu"]
        SK["Repozytorium umiejętności"]
        TM["Szablony dokumentów"]
    end

    subgraph EXT ["Integracje"]
        MCP["Comarch MCP"]
        MCP --> JI["Jira"]
        MCP --> WI["Wiki"]
        MCP --> GL["GitLab"]
    end

    CAP --> AR
    CAP --> CE
    CAP --> GD
    CAP --> GT
    CAP --> RD
    CAP --> GS

    GD -.-> SK
    GD -.-> TM
    GS ==> SK

    AR -.-> CT
    CE -.-> CT
    GD -.-> CT

    CAP --> MCP

    style CAP fill:#1e293b,color:#f1f5f9,stroke:none
    style ENTRY fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155
    style REALIZE fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#334155
    style LEARN fill:#fefce8,stroke:#d97706,stroke-width:2px,color:#334155
    style DATA fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#334155
    style EXT fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155
    style MCP fill:#10b981,color:#fff,stroke:none
```

---

## Trzy filary

<div class="features-grid" markdown>

<div class="feature" markdown>

### Inteligentny routing

Centralny agent analizuje polecenie i kieruje je do odpowiedniego orkiestratora. Nie potrzeba ręcznych reguł — decyzję podejmuje model językowy.

</div>

<div class="feature" markdown>

### Pipeline krokowy

Każdy orkiestrator to sekwencja wyspecjalizowanych kroków — od zbierania kontekstu, przez przetwarzanie, po kontrolę jakości.

</div>

<div class="feature" markdown>

### Dwie pętle

**Pętla realizacji** wykonuje zadania. **Pętla wiedzy** buduje umiejętności. Razem tworzą system, który się doskonali.

</div>

</div>

---

<div class="nav-cards" markdown>

<div class="nav-card" markdown>

**System dwupętlowy**

Jak współpracują pętla realizacji i pętla wiedzy

[Dual-Loop :material-arrow-right:](dual-loop.md)

</div>

<div class="nav-card" markdown>

**Topologie agentów**

Wizualne pipeline'y każdego orkiestratora

[Topologie :material-arrow-right:](orchestrators.md)

</div>

</div>
