# Przepływ danych — State Passing

## Mechanizm output_key

Agenci w pipeline komunikują się przez mechanizm **output_key** — kluczowy wzorzec Google ADK. Każdy agent produkuje wynik, który jest automatycznie wstrzykiwany w sesję i dostępny dla kolejnych kroków.

```mermaid
graph LR
    A["Agent 1<br/><small>output_key = 'result_a'</small>"]
    B["Agent 2<br/><small>output_key = 'result_b'<br/>Instrukcja: użyj {result_a}</small>"]
    C["Agent 3<br/><small>Instrukcja: użyj<br/>{result_a} i {result_b}</small>"]

    A -->|"session.state\n['result_a']"| B
    B -->|"session.state\n['result_b']"| C

    style A fill:#eceff1,stroke:#546e7a
    style B fill:#eceff1,stroke:#546e7a
    style C fill:#37474f,color:#fff,stroke:none
```

!!! info "Jak to działa technicznie?"
    1. Agent kończy pracę →  wynik zapisywany pod `session.state[output_key]`
    2. ADK automatycznie podmienia `{output_key}` w instrukcjach kolejnych agentów
    3. Każdy agent widzi tylko to, co jest mu potrzebne

---

## Łańcuchy output_key per orkiestrator

### analyze_requirement

```mermaid
graph LR
    A["req_source_collector<br/><small>→ collected_sources</small>"]
    B["parallel_requirement_analysts<br/><small>→ clarity_analysis<br/>→ scope_analysis<br/>→ cross_ref_analysis<br/>→ docs_gap_analysis</small>"]
    C["req_synthesis<br/><small>→ requirement_analysis</small>"]

    A --> B --> C

    style B fill:#eceff1,stroke:#546e7a,stroke-width:2px
    style C fill:#37474f,color:#fff,stroke:none
```

### generate_document

| Krok | Agent | output_key | Dostęp do stanu |
|------|-------|-----------|-----------------|
| 1 | doc_type_classifier | `doc_type` | — |
| 2 | doc_source_collector | `doc_sources` | `{doc_type}` |
| 3 | doc_content_writer | `doc_content` | `{doc_type}`, `{doc_sources}` + skille |
| 4 | doc_quality_reviewer | `doc_review` | `{doc_content}` |
| 5 | doc_file_writer | `doc_result` | `{doc_content}`, `{doc_review}` |

### generate_skill (Knowledge Loop)

| Krok | Agent | output_key | Dostęp do stanu |
|------|-------|-----------|-----------------|
| 1 | skill_source_collector | `collected_knowledge` | — |
| 2 | skill_knowledge_extractor | `extracted_knowledge` | `{collected_knowledge}` |
| 3 | skill_dedup_checker | `dedup_decision` | `{extracted_knowledge}` |
| 4 | skill_architect | `skill_draft` | `{extracted_knowledge}`, `{dedup_decision}` |
| 5 | skill_quality_reviewer | `skill_reviewed` | `{skill_draft}` |
| 6 | skill_presenter | `skill_result` | `{skill_draft}`, `{skill_reviewed}` |

---

## Kontrakt wiedzy projektowej

Centralnym elementem kontekstu jest **Project Knowledge Contract** — plik JSON walidowany Pydantic.

```mermaid
graph TB
    subgraph CT ["📑 Project Knowledge Contract"]
        PN["project_name<br/><small>'IoT Connect'</small>"]
        PD["project_description<br/><small>Opis projektu</small>"]
        DC["domain: DomainContext<br/><small>Konteksty domenowe<br/>(10 bounded contexts)</small>"]
        DOC["documentation<br/><small>Diátaxis, PL</small>"]
        JI["jira<br/><small>URL, project key</small>"]
        WK["wiki<br/><small>Confluence URL</small>"]
        TS["tech_stack<br/><small>['Scala', 'Kafka', ...]</small>"]
        TC["team_conventions<br/><small>Konwencje zespołu</small>"]
    end

    PB["Prompt Builder<br/><small>agent_instructions.py</small>"]
    SK["Skill Discovery<br/><small>discover_relevant_skills()</small>"]

    CT --> PB
    PB --> INS["📝 Instruction<br/><small>Bazowa instrukcja<br/>+ kontekst projektu<br/>+ treść skilli</small>"]
    SK --> INS

    INS --> AG["🤖 Agent<br/><small>Instrukcja wstrzyknięta</small>"]

    style CT fill:#fff3e0,stroke:#ff9800,stroke-width:2px,color:#333
    style INS fill:#37474f,color:#fff,stroke:none
```

### Struktura kontraktu

```json
{
  "project_name": "IoT Connect",
  "project_description": "Enterprise IoT Connectivity Management Platform",
  "domain": {
    "contexts": [
      {
        "name": "Census",
        "description": "Zarządzanie klientami, partnerami",
        "entities": ["BusinessPartner", "Account", "Agreement"],
        "glossary": {
          "BP": "Business Partner",
          "Party": "Strona umowy"
        }
      }
    ]
  },
  "documentation": {
    "framework": "diataxis",
    "language": "pl",
    "style_notes": "Microsoft Writing Style Guide"
  },
  "jira": {
    "url": "https://jira.comarch/",
    "project_key": "IOTC"
  },
  "tech_stack": ["Scala 2.13", "Cats Effect 3", "Kafka", "PostgreSQL", "Elasticsearch"],
  "team_conventions": ["F-first signatures", "Resource lifecycle", "Domain ADTs"]
}
```

!!! tip "Rozszerzalność"
    Dodanie nowego modułu/domeny do systemu to **dodanie nowego wpisu w kontrakcie**. Nie wymaga zmian w kodzie ani konfiguracji agentów.

---

## Diagram przepływu — pełny cykl

```mermaid
sequenceDiagram
    participant U as 👤 Użytkownik
    participant C as 🧠 Captain
    participant O as 📋 Orkiestrator
    participant S as 📚 Skills
    participant T as 🔧 Tools
    participant G as 🤖 Gemini

    U->>C: "Wygeneruj HLD dla modułu billing"
    C->>G: Analiza zapytania → wybór orkiestratora
    G-->>C: generate_document
    C->>O: AgentTool → generate_document

    rect rgb(232, 234, 246)
        Note over O: Pipeline 5 kroków
        O->>G: Krok 1: Klasyfikacja typu → HLD
        O->>T: Krok 2: Załaduj kontrakt + szablony
        O->>S: discover_relevant_skills("HLD")
        S-->>O: [diataxis-writing, style-guide, document-templates]
        O->>G: Krok 3: Generuj treść (z kontekstem + skillami)
        O->>G: Krok 4: Quality review
        O->>T: Krok 5: Zapisz plik
    end

    O-->>C: doc_result
    C-->>U: 📄 Gotowy HLD
```
