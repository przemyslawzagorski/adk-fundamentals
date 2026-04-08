# Platforma

## Ekosystem narzędziowy

Analyst System integruje lokalne narzędzia, bazę wiedzy i systemy zewnętrzne w spójny ekosystem.

```mermaid
graph TB
    subgraph LOCAL ["Narzędzia lokalne"]
        FT["Operacje na plikach"]
        TT["Zarządzanie szablonami"]
        ST["Zarządzanie umiejętnościami"]
    end

    subgraph KNOWLEDGE ["Baza wiedzy"]
        CT["Kontrakt projektu"]
        SK["Repozytorium umiejętności"]
        TM["Szablony dokumentów"]
    end

    subgraph EXTERNAL ["Systemy zewnętrzne"]
        MCP["Comarch MCP"]
        MCP --> JI["Jira"]
        MCP --> WI["Wiki / Confluence"]
        MCP --> GL["GitLab"]
    end

    FT --> CT
    TT --> TM
    ST --> SK

    style LOCAL fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#334155
    style KNOWLEDGE fill:#fefce8,stroke:#d97706,stroke-width:2px,color:#334155
    style EXTERNAL fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#334155
    style MCP fill:#10b981,color:#fff,stroke:none
```

---

## Baza wiedzy

### Kontrakt projektu

Centralny dokument definiujący kontekst projektu — domeny biznesowe, konwencje techniczne, opis architektury. Każdy orkiestrator automatycznie ładuje kontrakt jako kontekst.

### Repozytorium umiejętności

Rosnąca baza umiejętności w formacie agentskills.io. Cztery umiejętności bazowe (Diátaxis, style guide, szablony, analiza wymagań) plus umiejętności generowane przez Pętlę Wiedzy.

### Szablony dokumentów

Predefiniowane struktury dla HLD, LLD, epików i planów testów — zapewniają spójność formatu we wszystkich generowanych dokumentach.

---

## Integracje

Comarch MCP (Model Context Protocol) łączy system z zewnętrznymi platformami:

| Platforma | Zastosowanie |
|-----------|-------------|
| **Jira** | Pobieranie wymagań, backlog, user stories |
| **Confluence** | Dokumentacja projektowa, wiki |
| **GitLab** | Kod źródłowy, schematy, konfiguracje |

!!! info "Model Context Protocol"
    MCP to standard komunikacji między agentami AI a zewnętrznymi systemami. Pozwala na bezpieczny, kontrolowany dostęp do danych bez konieczności budowania dedykowanych integracji.

---

## Technologia

| Komponent | Technologia |
|-----------|-------------|
| **Platforma agentowa** | Google ADK |
| **Modele AI** | Gemini 2.5 Flash / Pro |
| **Język** | Python 3.11+ |
| **Integracje** | Comarch MCP |
| **Format umiejętności** | agentskills.io |
