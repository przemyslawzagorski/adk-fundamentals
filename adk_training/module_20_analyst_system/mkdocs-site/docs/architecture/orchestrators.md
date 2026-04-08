# Topologie agentów

## Trzy wzorce

System wykorzystuje trzy wzorce organizacji agentów — tworząc elastyczne pipeline'y dopasowane do zadania.

```mermaid
graph TB
    subgraph T1 ["Sekwencyjny"]
        direction LR
        S1["Krok 1"] --> S2["Krok 2"] --> S3["Krok 3"]
    end

    subgraph T2 ["Równoległy"]
        direction LR
        PI["Wejście"] --> PA["Specjalista A"]
        PI --> PB["Specjalista B"]
        PI --> PC["Specjalista C"]
        PA --> PM["Scalenie"]
        PB --> PM
        PC --> PM
    end

    subgraph T3 ["Router"]
        direction LR
        R["Router AI"] --> RA["Pipeline X"]
        R --> RB["Pipeline Y"]
        R --> RC["Pipeline Z"]
    end

    style T1 fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#334155
    style T2 fill:#fefce8,stroke:#d97706,stroke-width:2px,color:#334155
    style T3 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px,color:#334155
```

---

## Analyst Captain — router

Centralny agent analizuje polecenie użytkownika i kieruje je do odpowiedniego orkiestratora. Decyzję podejmuje model językowy na podstawie opisu zadań.

```mermaid
graph LR
    U["Polecenie użytkownika"] --> CAP["Analyst Captain"]

    CAP --> AR["Analiza wymagań"]
    CAP --> CE["Tworzenie epików"]
    CAP --> GD["Generowanie dokumentów"]
    CAP --> GT["Plany testów"]
    CAP --> RD["Recenzja"]
    CAP --> GS["Tworzenie umiejętności"]

    style CAP fill:#1e293b,color:#f1f5f9,stroke:none
    style AR fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style CE fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style GD fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style GT fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style RD fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style GS fill:#fefce8,stroke:#d97706,stroke-width:2px
```

---

## Analiza wymagań

Jedyny orkiestrator łączący wzorzec sekwencyjny z równoległym. Czterech specjalistów bada wymaganie jednocześnie, a synteza scala ich wnioski.

```mermaid
graph TD
    subgraph COLLECT ["Zbieranie kontekstu"]
        SC["Zbieranie"]
    end

    subgraph PARALLEL ["Analiza równoległa"]
        direction LR
        CA["Jasność"]
        SA["Zakres"]
        CRA["Zależności"]
        DGA["Luki"]
    end

    subgraph MERGE ["Synteza wyników"]
        SYN["Scalenie"]
    end

    SC --> CA
    SC --> SA
    SC --> CRA
    SC --> DGA

    CA --> SYN
    SA --> SYN
    CRA --> SYN
    DGA --> SYN

    style COLLECT fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155
    style PARALLEL fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#334155
    style MERGE fill:#f8fafc,stroke:#cbd5e1,stroke-width:1px,color:#334155
    style SYN fill:#1e293b,color:#f1f5f9,stroke:none
```

!!! tip "Dlaczego analiza równoległa?"
    Cztery aspekty wymagania — jasność, zakres, zależności, luki — są niezależne. Równoległość oszczędza czas i zapewnia różnorodność perspektyw.

---

## Generowanie dokumentów

Najbardziej rozbudowany pipeline — pięć kroków z dynamicznym ładowaniem umiejętności dopasowanych do typu dokumentu.

```mermaid
graph LR
    A["Klasyfikacja"] --> B["Zbieranie źródeł"]
    B --> C["Tworzenie treści"]
    C --> D["Kontrola jakości"]
    D --> E["Zapis dokumentu"]

    SK["Umiejętności"]
    SK -.->|"Automatycznie dobrane"| C

    style C fill:#1e293b,color:#f1f5f9,stroke:none
    style D fill:#10b981,color:#fff,stroke:none
    style SK fill:#fefce8,stroke:#d97706,stroke-width:2px
    style E fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

---

## Tworzenie umiejętności

Pipeline 6-krokowy z wbudowaną deduplikacją — bezpieczne wytwarzanie nowych umiejętności.

```mermaid
graph LR
    A["Źródła"] --> B["Ekstrakcja"]
    B --> C["Deduplikacja"]
    C --> D["Architektura"]
    D --> E["Recenzja"]
    E --> F["Publikacja"]

    style A fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style B fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style C fill:#fefce8,stroke:#d97706,stroke-width:2px
    style D fill:#10b981,color:#fff,stroke:none
    style E fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style F fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

---

## Tworzenie epików

Pipeline 4-krokowy — od kontekstu projektu po kompletny epik z user stories.

```mermaid
graph LR
    A["Zbieranie kontekstu"] --> B["Tworzenie epiku"]
    B --> C["Kontrola jakości"]
    C --> D["Zapis"]

    style B fill:#1e293b,color:#f1f5f9,stroke:none
    style D fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

---

## Recenzja dokumentów

Najprostszy pipeline — trzy kroki weryfikacji dokumentu względem standardów.

```mermaid
graph LR
    A["Wczytanie dokumentu"] --> B["Analiza jakości"]
    B --> C["Raport z rekomendacjami"]

    style B fill:#1e293b,color:#f1f5f9,stroke:none
    style C fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```
