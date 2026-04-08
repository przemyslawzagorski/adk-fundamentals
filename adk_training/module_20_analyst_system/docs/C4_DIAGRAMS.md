# Diagramy C4 — Analyst System

## 1. C4 Context (Level 1) — System w ekosystemie

```mermaid
C4Context
    title C4 Context Diagram — Analyst System

    Person(user, "Analityk / Developer", "Zadaje pytania i zleca zadania analityczne")

    System(analyst, "Analyst System", "Inteligentny system agentowy do automatyzacji zadań analitycznych, generowania dokumentacji i zarządzania wiedzą projektową")

    System_Ext(gemini, "Google Gemini API", "LLM backend: gemini-2.5-flash / gemini-2.5-pro")
    System_Ext(jira, "Jira", "Zarządzanie zadaniami i backlogiem")
    System_Ext(wiki, "Confluence Wiki", "Baza dokumentacji projektowej")
    System_Ext(gitlab, "GitLab", "Repozytorium kodu źródłowego")
    System_Ext(mcp, "Comarch MCP Server", "Model Context Protocol — broker integracji")

    Rel(user, analyst, "Zleca zadania w języku naturalnym", "ADK CLI / Web UI")
    Rel(analyst, gemini, "Wysyła prompty, odbiera odpowiedzi", "HTTPS / API Key")
    Rel(analyst, mcp, "Łączy się po narzędzia", "stdio / MCP Protocol")
    Rel(mcp, jira, "Odczyt ticketów, wyszukiwanie", "REST API")
    Rel(mcp, wiki, "Odczyt stron wiki", "REST API")
    Rel(mcp, gitlab, "Przeglądanie kodu", "REST API")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## 2. C4 Container (Level 2) — Kontenery wewnętrzne

```mermaid
C4Container
    title C4 Container Diagram — Analyst System

    Person(user, "Analityk / Developer", "Użytkownik systemu")

    System_Boundary(analyst, "Analyst System") {
        Container(captain, "Analyst Captain", "LlmAgent + AgentTool", "Root router — kieruje zapytania do odpowiedniego orkiestratora")

        Container(analyze_req, "analyze_requirement", "SequentialAgent + ParallelAgent", "Analiza wymagań: jasność, zakres, zależności, luki")
        Container(create_epic, "create_epic", "SequentialAgent", "Tworzenie epiców z user stories")
        Container(gen_doc, "generate_document", "SequentialAgent", "Generowanie dokumentacji HLD/LLD")
        Container(gen_test, "generate_test_plan", "SequentialAgent", "Tworzenie planów testów")
        Container(review_doc, "review_document", "SequentialAgent", "Recenzja dokumentów")
        Container(gen_skill, "generate_skill", "SequentialAgent (6 kroków)", "Knowledge Loop — generowanie nowych skill-i")

        ContainerDb(contract, "Project Contract", "JSON / Pydantic", "Kontrakt wiedzy projektowej — domena, konfiguracja")
        ContainerDb(skills, "Skills Repository", "agentskills.io", "Baza umiejętności: Diátaxis, style-guide, templates, requirement-analysis")
        ContainerDb(output, "Output Directory", "Filesystem", "Wygenerowane dokumenty, epiki, plany")

        Container(tools, "Tool Functions", "Python / FunctionTool", "file_tools, template_tools, skill_tools")
        Container(prompts, "Prompt Builder", "Python", "Budowanie instrukcji z kontekstem projektu i skill-ami")
    }

    System_Ext(gemini, "Google Gemini API", "LLM")
    System_Ext(mcp, "Comarch MCP", "Jira + Wiki + GitLab")

    Rel(user, captain, "Zapytanie w języku naturalnym")
    Rel(captain, analyze_req, "AgentTool routing")
    Rel(captain, create_epic, "AgentTool routing")
    Rel(captain, gen_doc, "AgentTool routing")
    Rel(captain, gen_test, "AgentTool routing")
    Rel(captain, review_doc, "AgentTool routing")
    Rel(captain, gen_skill, "AgentTool routing")

    Rel(analyze_req, tools, "Używa narzędzi")
    Rel(gen_doc, tools, "Używa narzędzi")
    Rel(gen_doc, skills, "Ładuje skill-e dynamicznie")
    Rel(gen_skill, skills, "Zapisuje nowe skill-e")
    Rel(create_epic, tools, "Używa szablonów")
    Rel(tools, contract, "Odczytuje kontrakt")
    Rel(tools, output, "Zapisuje dokumenty")
    Rel(prompts, contract, "Buduje instrukcje")
    Rel(prompts, skills, "Odkrywa skill-e")

    Rel(captain, gemini, "Prompty LLM", "HTTPS")
    Rel(captain, mcp, "Narzędzia MCP", "stdio")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## 3. C4 Component (Level 3) — Pipeline agentów i przepływ danych

```mermaid
graph TB
    subgraph "Analyst Loop"
        direction TB
        AR["analyze_requirement<br/><i>Sequential + Parallel</i>"]
        CE["create_epic<br/><i>4-step Sequential</i>"]
        GD["generate_document<br/><i>5-step Sequential</i>"]
        GT["generate_test_plan<br/><i>4-step Sequential</i>"]
        RD["review_document<br/><i>3-step Sequential</i>"]
    end

    subgraph "Knowledge Loop"
        direction TB
        GS["generate_skill<br/><i>6-step Sequential</i>"]
    end

    subgraph "analyze_requirement Pipeline"
        direction LR
        SC1[source_collector] --> PA
        subgraph PA["ParallelAgent"]
            CA[clarity_analyst]
            SA[scope_analyst]
            CRA[cross_ref_analyst]
            DGA[docs_gap_analyst]
        end
        PA --> SYN[synthesis_agent]
    end

    subgraph "generate_skill Pipeline"
        direction LR
        SC2[source_collector] --> KE[knowledge_extractor]
        KE --> DC[dedup_checker]
        DC --> SKA[skill_architect]
        SKA --> QR[quality_reviewer]
        QR --> PR[presenter]
    end

    subgraph "Shared Resources"
        CONTRACT[(Project Contract)]
        SKILLS[(Skills Repository)]
        TOOLS[Tool Functions]
    end

    CAPTAIN["Analyst Captain<br/><i>LlmAgent Router</i>"]

    CAPTAIN -->|AgentTool| AR
    CAPTAIN -->|AgentTool| CE
    CAPTAIN -->|AgentTool| GD
    CAPTAIN -->|AgentTool| GT
    CAPTAIN -->|AgentTool| RD
    CAPTAIN -->|AgentTool| GS

    AR -.->|uses| TOOLS
    GD -.->|loads| SKILLS
    GS -.->|writes| SKILLS
    CE -.->|uses| TOOLS
    TOOLS -.->|reads| CONTRACT

    style CAPTAIN fill:#4CAF50,color:white
    style PA fill:#2196F3,color:white
    style CONTRACT fill:#FF9800,color:white
    style SKILLS fill:#FF9800,color:white
```

---

## 4. Przepływ stanu (output_key chain)

```mermaid
graph LR
    subgraph "generate_skill — 6 kroków"
        A["source_collector"] -->|collected_knowledge| B["knowledge_extractor"]
        B -->|extracted_knowledge| C["dedup_checker"]
        C -->|dedup_decision| D["skill_architect"]
        D -->|skill_draft| E["quality_reviewer"]
        E -->|skill_reviewed| F["presenter"]
        F -->|skill_result| OUT["Wynik"]
    end

    subgraph "analyze_requirement — 3 kroki"
        G["source_collector"] -->|collected_sources| H["ParallelAgent"]
        H -->|clarity + scope + cross_ref + docs_gap| I["synthesis_agent"]
        I -->|requirement_analysis| OUT2["Wynik"]
    end

    style A fill:#E3F2FD
    style G fill:#E3F2FD
    style OUT fill:#C8E6C9
    style OUT2 fill:#C8E6C9
```
