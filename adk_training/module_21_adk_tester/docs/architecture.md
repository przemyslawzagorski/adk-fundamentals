# Architektura module_21_adk_tester

## Diagram architektury — Co mamy vs Co testowaliśmy

```mermaid
graph TB
    subgraph "Podejście A: Czysty Playwright (deterministyczny skrypt)"
        SCRIPT["_test_browser_m01_m02.py<br/><b>Deterministyczny skrypt</b><br/>hardcoded selektory, prompty"]
        PW_DIRECT["Playwright Browser<br/>page.click(), page.fill()"]
        SCRIPT -->|"page.goto(), click, fill, Enter"| PW_DIRECT
    end

    subgraph "Podejście B: Agent Computer Use (module_21_adk_tester)"
        CLI["cli.py<br/>CLI / Interactive"]
        ATS["AgentTesterSystem<br/>Runner + Session"]
        AGENT["LlmAgent<br/><b>adk_web_tester</b><br/>model: gemini-2.5-flash"]
        
        subgraph "Narzędzia agenta"
            CU["ComputerUseToolset<br/>click_at(x,y), type_text_at()"]
            FT1["get_test_plan()"]
            FT2["save_test_result()"]
            FT3["generate_report()"]
        end
        
        PC["PlaywrightComputer<br/>(BaseComputer)<br/>+ video recording"]
        PW_AGENT["Playwright Browser<br/>screenshots → Gemini<br/>Gemini → click/type"]

        CLI --> ATS
        ATS --> AGENT
        AGENT -->|"sam decyduje co kliknąć<br/>na podstawie screenshotów"| CU
        AGENT --> FT1
        AGENT --> FT2
        AGENT --> FT3
        CU --> PC
        PC --> PW_AGENT
    end

    subgraph "Cel testów"
        ADK_WEB["ADK Web Server<br/>localhost:8000"]
        
        subgraph "Testowane agenty"
            A01["module_01<br/>asystent_podstawowy"]
            A02["module_02<br/>zarzadca_skarbow"]
            A03["module_03<br/>asystent_rag"]
        end

        ADK_WEB --> A01
        ADK_WEB --> A02
        ADK_WEB --> A03
    end

    PW_DIRECT -->|"HTTP"| ADK_WEB
    PW_AGENT -->|"HTTP"| ADK_WEB

    style SCRIPT fill:#ff9800,color:#000
    style AGENT fill:#4caf50,color:#fff
    style ADK_WEB fill:#2196f3,color:#fff
    style PC fill:#9c27b0,color:#fff
```

## Flow agenta Computer Use — krok po kroku

```mermaid
sequenceDiagram
    participant U as Użytkownik / CLI
    participant A as LlmAgent (Gemini)
    participant CU as ComputerUseToolset
    participant PC as PlaywrightComputer
    participant B as Chromium Browser
    participant ADK as ADK Web (localhost:8000)
    participant FT as FunctionTools

    U->>A: "Przetestuj moduły 01, 02, 03"
    
    Note over A: Agent sam planuje strategię
    
    A->>FT: get_test_plan("01")
    FT-->>A: scenariusze, prompty, keywords
    
    A->>CU: open_web_browser()
    CU->>PC: initialize()
    PC->>B: launch chromium + video recording
    B->>ADK: GET localhost:8000
    PC-->>CU: screenshot (PNG)
    CU-->>A: screenshot → Gemini widzi UI

    Note over A: Gemini analizuje screenshot:<br/>"Widzę dropdown 'Select an agent'<br/>Muszę go kliknąć"

    A->>CU: click_at(200, 97)
    CU->>PC: mouse.click(200, 97)
    PC->>B: klik na dropdown
    B-->>PC: dropdown otwarty
    PC-->>CU: nowy screenshot
    CU-->>A: screenshot z listą agentów

    Note over A: "Widzę 'module_01_hello_world'<br/>w dropdown, klikam"

    A->>CU: click_at(200, 150)
    CU->>PC: mouse.click(200, 150)
    PC->>B: klik na agenta
    B->>ADK: session created
    PC-->>CU: screenshot z chatem
    CU-->>A: screenshot

    Note over A: "Widzę pole tekstowe na dole.<br/>Wpisuję prompt z planu testów"

    A->>CU: type_text_at(950, 743, "Kim jesteś?", enter=true)
    CU->>PC: click + type + Enter
    PC->>B: textarea.fill + Enter
    B->>ADK: POST /run (message)
    ADK-->>B: odpowiedź agenta
    PC-->>CU: screenshot z odpowiedzią
    CU-->>A: screenshot

    Note over A: Gemini CZYTA odpowiedź<br/>ze screenshota, ocenia:<br/>"Zawiera 'pomoc' ✓, >50 znaków ✓"

    A->>FT: save_test_result("m01_greeting", "PASS", response="...")
    FT-->>A: zapisano

    Note over A: Powtarza dla każdego scenariusza...
    
    A->>FT: generate_report("01")
    FT-->>A: raport Markdown wygenerowany

    A-->>U: "Moduł 01: 3/3 PASS. Raport zapisany."
    
    Note over PC, B: context.close() → video finalized (.webm)
```

## Porównanie podejść

| | **Czysty Playwright** | **Agent Computer Use** |
|---|---|---|
| **Kto decyduje co kliknąć?** | Skrypt — hardcoded selektory | **Gemini** — na podstawie screenshotów |
| **Skąd wie gdzie jest textarea?** | `page.locator("textarea[placeholder='...']")` | Widzi na screenshocie i klika `type_text_at(x, y)` |
| **Jak czyta odpowiedź?** | `page.query_selector(".bot-message")` | Gemini **czyta tekst ze screenshota** (OCR wizualny) |
| **Odporność na zmiany UI** | Łamie się gdy zmieni się selektor | Agent sam się adaptuje (widzi nowy layout) |
| **Koszt** | 0 (zero API calls) | ~$0.05-0.15 za moduł (Gemini API) |
| **Szybkość** | ~2min na 2 moduły | ~5-10min (screenshot → analiza → akcja w pętli) |
| **Plik** | `_test_browser_m01_m02.py` | `agent.py` + `cli.py` + `playwright_computer.py` |
