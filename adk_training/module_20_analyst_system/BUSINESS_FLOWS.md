# Analyst System — Business Flows E2E

> **Dla CTO/Product Ownera:** Dokładna mapa co system robi, jak przepływają dane, gdzie są quality gates.
> **Dla developera:** Kontrakt architektoniczny z testami — zmienisz coś i od razu wiesz co się rozbije.
> **Dla QA:** Pełna mapa scenariuszy z expected output i security boundary.

---

## Executive Summary

**Analyst System** to produkcyjny system multi-agentowy (Google ADK) który automatyzuje pracę analityka IT:
- **6 pipeline'ów** obsługujących pełen cykl życia dokumentacji
- **Dual-loop architecture**: Execution Loop (analiza/generacja) + Knowledge Loop (samorozwój)
- **35 agentów** skoordynowanych przez jednego routera
- **4 wbudowane skills** + framework do generowania nowych
- **Integracja z Jira/Confluence/GitLab** przez MCP (opcjonalna, graceful fallback)

### Kluczowe liczby

| Metryka | Wartość |
|---------|---------|
| Orkiestratory | 6 (analyze_requirement, create_epic, generate_document, generate_test_plan, review_document, generate_skill) |
| Agenty ogółem | 35 (unikalne nazwy) |
| Narzędzia | 10 (file_tools: 3, template_tools: 2, skill_tools: 5) + MCP |
| Quality gates | Każdy pipeline ma review_quality agent |
| Modele LLM | gemini-2.5-flash (standard) + gemini-2.5-pro (complex tasks) |
| Testy quality | 10 e2e (routing, security, pipeline structure, contracts, skills) |

---

## Architektura — Dual-Loop

```
  ┌─────────────────────────────────────────────────────────────────────────────────┐
  │                          ANALYST SYSTEM                                         │
  │                                                                                 │
  │  User Request ──► [Analyst Captain] ──► routing via AgentTool ──►               │
  │                        │                                                        │
  │        ┌───────────────┼───────────────────────────────────────┐                │
  │        │               │            EXECUTION LOOP              │                │
  │        │  ┌────────────┴──────────────────────────────────┐    │                │
  │        │  │ analyze_requirement                            │    │                │
  │        │  │ collect → [clarity|scope|cross_ref|gap]∥ → synth│    │                │
  │        │  ├────────────────────────────────────────────────┤    │                │
  │        │  │ create_epic                                    │    │                │
  │        │  │ collect → write(+template+skill) → review → save│   │                │
  │        │  ├────────────────────────────────────────────────┤    │                │
  │        │  │ generate_document                              │    │                │
  │        │  │ classify → collect → write(+skills) → review → save│ │               │
  │        │  ├────────────────────────────────────────────────┤    │                │
  │        │  │ generate_test_plan                             │    │                │
  │        │  │ collect → plan → review → save                  │    │                │
  │        │  ├────────────────────────────────────────────────┤    │                │
  │        │  │ review_document                                │    │                │
  │        │  │ read → analyze(+skills) → report               │    │                │
  │        │  └────────────────────────────────────────────────┘    │                │
  │        └───────────────────────────────────────────────────────┘                │
  │                                                                                 │
  │        ┌───────────────────────────────────────────────────────┐                │
  │        │                KNOWLEDGE LOOP                          │                │
  │        │  generate_skill                                        │                │
  │        │  collect → extract → dedup → architect → review → present │             │
  │        │                                        ↓                │                │
  │        │                              [USER APPROVAL]            │                │
  │        │                                        ↓                │                │
  │        │                              write_skill_draft → skills/ │               │
  │        └───────────────────────────────────────────────────────┘                │
  │                                                                                 │
  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                        │
  │  │   Contract    │   │    Skills    │   │   Templates  │                        │
  │  │ (JSON/Pydantic)│   │ (agentskills │   │ (HLD, LLD,  │                        │
  │  │ → context     │   │  .io spec)  │   │  epic, test) │                        │
  │  │   injection   │   │ → dynamic   │   │              │                        │
  │  └──────────────┘   │   loading   │   └──────────────┘                        │
  │                      └──────────────┘                                           │
  └─────────────────────────────────────────────────────────────────────────────────┘
          ↕ MCP (optional)              ↕ Gemini API
     Jira / Confluence / GitLab     gemini-2.5-flash / pro
```

---

## Flow 1: Analiza wymagań (analyze_requirement)

### Trigger
> „Przeanalizuj wymaganie: system musi obsługiwać masową aktywację 10 000 kart SIM w partii"

### Pipeline

```
User Request
    │
    ▼
[Analyst Captain] ──routing──► analyze_requirement
    │
    ▼
┌─ source_collector ─────────────────────────┐
│  output_key: collected_sources              │
│  Tools: read_file, list_files, MCP(optional)│
│  Zbiera: Jira tickets, wiki pages, local docs│
└─────────────────┬──────────────────────────┘
                  ▼
┌─ ParallelAgent (4 analitycy równolegle) ───┐
│                                             │
│  ┌─ clarity_analyst ──┐  ┌─ scope_analyst ──┐
│  │ output_key:         │  │ output_key:      │
│  │ clarity_analysis    │  │ scope_analysis   │
│  │ Jasność, dwuznaczn-│  │ Zakres explicite/│
│  │ ości, brak definicji│  │ implicite/hidden │
│  └─────────────────────┘  └──────────────────┘
│  ┌─ cross_ref_analyst ┐  ┌─ docs_gap_analyst┐
│  │ output_key:         │  │ output_key:      │
│  │ cross_ref_analysis  │  │ docs_gap_analysis│
│  │ Powiązane tickety,  │  │ Brakujące docs,  │
│  │ zależności, konflikty│  │ nieaktualne info │
│  └─────────────────────┘  └──────────────────┘
│                                             │
└──────────────────┬──────────────────────────┘
                   ▼
┌─ synthesis_agent ──────────────────────────┐
│  output_key: requirement_analysis           │
│  Łączy 4 perspektywy w raport:             │
│  • Jasność i gaps                           │
│  • Warstwy zakresu                          │
│  • Zależności i ryzyka                      │
│  • Rekomendacja: Ready / Refinement / Spike │
└─────────────────────────────────────────────┘
```

### Output
Structured report z rekomendacją **Ready** (do implementacji) / **Refinement** (potrzebne doprecyzowanie) / **Spike** (potrzebne badanie techniczne).

### Wartość biznesowa
- **Przed**: Analityk spędza 2-4h na jednym wymaganiu, często pomija cross-references
- **Po**: 4 perspektywy w <2 min, zawsze sprawdza powiązania i luki

---

## Flow 2: Tworzenie epików (create_epic)

### Trigger
> „Utwórz epik dla implementacji eksportu CDR do formatu CSV"

### Pipeline

```
User Request
    │
    ▼
[Analyst Captain] ──routing──► create_epic
    │
    ▼
┌─ source_collector ─────────────────────────┐
│  output_key: collected_sources              │
│  Tools: read_file, list_files, MCP          │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ epic_writer ──────────────────────────────┐
│  output_key: epic_draft                     │
│  MODEL: gemini-2.5-flash                    │
│  Ładuje: epic_template + requirement-analysis│
│  Generuje:                                  │
│  • Tytuł i opis epiku                       │
│  • 3-8 user stories (Jako/chcę/aby)        │
│  • AC w formacie Given/When/Then            │
│  • Mapa zależności                          │
│  • Ryzyka i mitygacje                       │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ quality_reviewer ─────────────────────────┐
│  output_key: epic_reviewed                  │ ◄── QUALITY GATE
│  Waliduje:                                  │
│  • Niezależność user stories (INVEST)       │
│  • Kompletność AC (Given/When/Then)         │
│  • Brak TODO/placeholder                    │
│  • Spójność z kontraktem projektu           │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ template_writer ──────────────────────────┐
│  output_key: epic_result                    │
│  Tools: write_document                      │
│  Zapisuje: output/epics/nazwa-epiku.md     │
│  Format: kebab-case naming convention       │
└─────────────────────────────────────────────┘
```

### Deliverable
Plik Markdown w `output/epics/` gotowy do importu do Jira.

### Wartość biznesowa
- **Przed**: PO pisze epik 1-2 dni, user stories niekompletne, AC brak lub generyczne
- **Po**: Kompletny epik z Given/When/Then AC w <5 min

---

## Flow 3: Generowanie dokumentacji (generate_document)

### Trigger
> „Wygeneruj HLD dla modułu zarządzania alertami sieciowymi"

### Pipeline

```
User Request
    │
    ▼
[Analyst Captain] ──routing──► generate_document
    │
    ▼
┌─ doc_type_classifier ─────────────────────┐
│  output_key: doc_classification             │
│  Identyfikuje: typ (HLD/LLD/tutorial/...)  │
│  + template + topic                         │
│  Decyduje o frameworku: Diátaxis vs custom  │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ source_collector ─────────────────────────┐
│  output_key: collected_sources              │
│  Zbiera materiały źródłowe                  │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ content_writer ───────────────────────────┐
│  output_key: doc_draft                      │
│  MODEL: gemini-2.5-pro (STRONG)             │  ◄── Mocniejszy model
│  Skills loading (DYNAMIC):                  │
│  • ALWAYS: style-guide                      │
│  • IF Diátaxis: diataxis-writing            │
│  • IF matching topic: domain-specific skill │
│  + ładuje template z template_tools          │
│  Generuje dokument z kontekstem projektu    │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ quality_reviewer ─────────────────────────┐
│  output_key: doc_reviewed                   │ ◄── QUALITY GATE
│  Sprawdza:                                  │
│  • Brak TODO/placeholder                    │
│  • Hierarchia nagłówków (H1>H2>H3)         │
│  • Terminologia zgodna z glossary kontraktu │
│  • Styl zgodny ze style-guide               │
│  • Konkretne przykłady (nie generyczne)     │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ doc_file_writer ──────────────────────────┐
│  output_key: doc_result                     │
│  Tools: write_document                      │
│  Zapisuje: output/{type}/ (hld/, lld/, etc.)│
└─────────────────────────────────────────────┘
```

### Dynamic Skill Loading — kluczowy mechanizm
```
Zapytanie: "Wygeneruj HLD dla billing"
                │
                ▼
        discover_relevant_skills("billing HLD")
                │
                ├── MATCH: style-guide (always)
                ├── MATCH: diataxis-writing (HLD = reference type)
                └── MATCH: domain-specific skill (if "billing" in skill description)
```

### Wartość biznesowa
- **Przed**: HLD zajmuje 3-5 dni, każdy członek zespołu pisze inaczej
- **Po**: HLD w <10 min, zawsze ten sam format, styl, terminologia

---

## Flow 4: Plan testów (generate_test_plan)

### Trigger
> „Przygotuj plan testów integracyjnych dla Census"

### Pipeline

```
source_collector → test_planner(+template+skill) → quality_reviewer → writer
       │                  │                              │              │
  collected_sources  test_plan_draft              test_plan_reviewed  test_plan_result
```

### Deliverable
Plan testów w `output/test-plans/` z scenariuszami pogrupowanymi:
- **Positive** — happy path
- **Negative** — błędne dane, brak uprawnień
- **Edge** — graniczne ilości, timeout, duże pliki
- **Integration** — interakcje między komponentami

Każdy scenariusz: preconditions + steps + expected results.

---

## Flow 5: Recenzja dokumentu (review_document)

### Trigger
> „Zrecenzuj ten dokument pod kątem Diátaxis"

### Pipeline

```
doc_reader → review_quality_analyst(+skills) → report
     │                    │                       │
  doc_content         doc_review             review_result
```

### Deliverable
Raport z:
- **Quality score** (1-10)
- **Critical issues** (numerowane, z lokalizacją)
- **Suggestions** (ulepszenia)
- **Positive observations** (co jest dobrze)

### Wartość biznesowa
- Code review jest standardem, document review nie — ten flow to **document review as a service**

---

## Flow 6: Knowledge Loop — generowanie skill-i (generate_skill)

### Trigger
> „Utwórz nowy skill dotyczący konwencji nazewnictwa w API GraphQL"

### Pipeline (6 etapów)

```
User Request
    │
    ▼
┌─ source_collector ─────────────────────────┐
│  output_key: collected_knowledge            │
│  SOURCE ATTRIBUTION wymagane                │
│  Zbiera: Wiki, GitLab, Jira, lokalne docs   │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ knowledge_extractor ──────────────────────┐
│  output_key: extracted_knowledge            │
│  MODEL: gemini-2.5-pro (STRONG)             │
│  Klasyfikuje typ:                           │
│  • domain-concept                           │
│  • process-workflow                         │
│  • template-pattern                         │
│  • quality-standard                         │
│  • integration-guide                        │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ dedup_checker ────────────────────────────┐
│  output_key: dedup_decision                 │
│  Tools: list_skills, read_skill             │
│  Decyzja: CREATE / UPDATE / MERGE / SKIP    │
│  Porównuje z istniejącymi skills            │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ skill_architect ──────────────────────────┐
│  output_key: skill_draft                    │
│  MODEL: gemini-2.5-pro (STRONG)             │
│  Tworzy SKILL.md per agentskills.io spec:  │
│  • YAML frontmatter                         │
│  • Body ≤500 lines (target 100-300)         │
│  • ## When to use                           │
│  • Tabele, ✅/❌ patterns                   │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ quality_reviewer ─────────────────────────┐
│  output_key: skill_reviewed                 │ ◄── QUALITY GATE
│  MODEL: gemini-2.5-pro (STRONG)             │
│  Anthropic principle:                       │
│  "Czy agent POTRZEBUJE tej informacji?"     │
│  Waliduje: spec compliance, conciseness,    │
│  content quality                            │
└─────────────────┬──────────────────────────┘
                  ▼
┌─ presenter ────────────────────────────────┐
│  output_key: skill_result                   │
│  Pokazuje użytkownikowi:                    │
│  • Action (CREATE/UPDATE/MERGE/SKIP)        │
│  • Quality score                            │
│  • Warnings                                 │
│  • Full content preview                     │
│                                             │
│  ► USER APPROVAL ◄                          │ ◄── HUMAN-IN-THE-LOOP
│                                             │
│  write_skill_draft → skills/{name}/SKILL.md │
└─────────────────────────────────────────────┘
```

### Wartość biznesowa
- **Self-improving system**: każdy nowy skill podnosi jakość WSZYSTKICH przyszłych dokumentów
- **Knowledge capture**: wiedza zespołu nie ginie gdy ktoś odchodzi

---

## Mechanizmy przekrojowe

### Contract Injection — kontekstowość
```
contract/sample_contract.json
         │
         ▼
  ProjectKnowledgeContract (Pydantic v2)
         │
         ▼
  build_base_instruction(contract, agent_role)
         │
         ▼
  Każdy agent automatycznie wie:
  • Nazwa projektu, domena, bounded contexts
  • Słownik terminów (glossary)
  • Tech stack (Scala 2.13, Kafka, etc.)
  • Style notes, primary language
  • Konwencje zespołu
```

### Security Boundary
| Layer | Ochrona |
|-------|---------|
| **File read** | Blokuje `/etc/shadow`, `/etc/passwd`, `\windows\system32` |
| **File write** | Wymusza zapis w obrębie OUTPUT_DIR, blokuje `../` path traversal |
| **Skill names** | Regex `^[a-z][a-z0-9-]{0,62}[a-z0-9]$`, reserved names rejected |
| **Tool returns** | Zawsze `{status: "ok"|"error", ...}` — agent sprawdza status |
| **MCP** | Graceful fallback — system działa bez tokenów |

### Quality Gates — co waliduje reviewer w każdym pipeline
| Check | Dotyczy |
|-------|---------|
| Brak TODO/placeholder | Wszystkie pipeline'y |
| Heading hierarchy (H1>H2>H3) | generate_document, create_epic |
| Terminologia z glossary kontraktu | Wszystkie |
| Given/When/Then w AC | create_epic |
| INVEST criteria | create_epic |
| Diátaxis compliance | generate_document (if applicable) |
| Style guide compliance | Wszystkie generujące tekst |
| Source attribution | generate_skill |
| agentskills.io spec | generate_skill |

---

## Test Coverage — Mapa quality testów

### Istniejące testy (test_module_20.py + test_module_20_quality.py)

| # | Test | Co waliduje | Failure = |
|---|------|------------|-----------|
| S1-S6 | Structural tests | Importy, routing, pipeline count | Broken deployment |
| Q1 | Routing table ↔ tool names | Captain wie o wszystkich orchestratorach | Wrong routing → user gets error |
| Q2 | output_key → instruction refs | Pipeline data flow | Agent nie widzi danych z poprzedniego kroku |
| Q3 | Agent name uniqueness (35 names) | Brak state collision | State pollution między agentami |
| Q4 | Path traversal security | read_file blocks dangerous paths | Data exfiltration |
| Q5 | write_document containment | Output stays in OUTPUT_DIR | Arbitrary file write |
| Q6 | create_epic pipeline: 4 steps | collect→write→review→save chain | Broken epic generation |
| Q7 | generate_test_plan: 4 steps | collect→plan→review→save chain | Broken test plan generation |
| Q8 | review_document: 3 steps | read→analyze→report chain | Broken review |
| Q9 | Contract enrichment fields | All 6 fields injected | Agents lose project context |
| Q10 | Skill discovery precision | Correct skills matched for topic | Wrong skills loaded → bad output |

### Pokrycie per komponent

| Komponent | Testy | Status |
|-----------|:-----:|--------|
| Routing (Captain → orchestrators) | Q1 | ✅ |
| Pipeline structure (6 orchestrators) | Q6, Q7, Q8 | ✅ (3/6 orkiestratorów) |
| Data flow (output_key chain) | Q2 | ✅ |
| Security (path traversal, containment) | Q4, Q5 | ✅ |
| Agent identity (35 unique names) | Q3 | ✅ |
| Contract system | Q9 | ✅ |
| Skills system | Q10 | ✅ |
| MCP integration | — | ⚠️ Wymaga tokenów |
| analyze_requirement (parallel pattern) | — | 🔲 Do dodania |
| generate_document (dynamic skill loading) | — | 🔲 Do dodania |
| generate_skill (Knowledge Loop / 6 steps) | — | 🔲 Do dodania |

---

## Deployment

```bash
# Wymagane
export GOOGLE_API_KEY=...

# Opcjonalne
export ADK_MODEL=gemini-2.5-flash          # default
export ADK_MODEL_STRONG=gemini-2.5-pro      # for complex tasks
export OUTPUT_DIR=./output
export SKILLS_DIR=./skills

# MCP (opcjonalne — system działa bez)
export JIRA_BEARER_TOKEN=...
export WIKI_BEARER_TOKEN=...
export GITLAB_TOKEN=...

# Start
cd module_20_analyst_system
adk web .
```

---

## Roadmap jakościowy

| Priorytet | Cel | Impact |
|:---------:|-----|--------|
| **P0** | Testy pipeline: analyze_requirement (parallel pattern) | Jedyny parallel — bez testu może się rozsypać |
| **P0** | Testy pipeline: generate_skill (6-step Knowledge Loop) | Najdłuższy pipeline — highest failure risk |
| **P1** | Testy pipeline: generate_document (dynamic skill loading) | Kluczowy flow, dynamiczne ładowanie skill-i |
| **P1** | MCP graceful fallback test | Verify system works without tokens |
| **P2** | Contract validation edge cases | Empty glossary, missing fields |
| **P2** | Skill deduplication logic | CREATE vs UPDATE vs MERGE vs SKIP |
