# System dwupętlowy

## Koncepcja

Analyst System łączy dwie komplementarne pętle — **realizacji** i **wiedzy** — tworząc system, który nie tylko wykonuje zadania, ale autonomicznie się doskonali.

```mermaid
graph TB
    subgraph AL ["Pętla realizacji"]
        direction LR
        Q["Polecenie"] --> ROT["Routing"]
        ROT --> P["Pipeline agentów"]
        P --> O["Wynik"]
    end

    subgraph KL ["Pętla wiedzy"]
        direction LR
        T["Polecenie"] --> KP["Pipeline 6-krokowy"]
        KP --> NS["Nowa umiejętność"]
    end

    NS -->|"Wzbogaca"| P
    O -->|"Zidentyfikowana luka"| T

    style AL fill:#ecfdf5,stroke:#10b981,stroke-width:2px,color:#334155
    style KL fill:#fefce8,stroke:#d97706,stroke-width:2px,color:#334155
```

---

## Pętla realizacji

Główna pętla systemu. Odpowiada za realizację zadań analitycznych — od analizy wymagań po generowanie dokumentów.

<div class="pipeline" markdown>

<div class="step">
<div class="step-circle">1</div>
<div class="step-label">Polecenie użytkownika</div>
</div>
<div class="arrow">→</div>

<div class="step">
<div class="step-circle">2</div>
<div class="step-label">Inteligentny routing</div>
</div>
<div class="arrow">→</div>

<div class="step">
<div class="step-circle">3</div>
<div class="step-label">Pipeline agentów</div>
</div>
<div class="arrow">→</div>

<div class="step">
<div class="step-circle">4</div>
<div class="step-label">Kontrola jakości</div>
</div>
<div class="arrow">→</div>

<div class="step">
<div class="step-circle">5</div>
<div class="step-label">Gotowy wynik</div>
</div>

</div>

### Pięć orkiestratorów

| Orkiestrator | Specjalność | Wyróżnik |
|-------------|-------------|-----------|
| **Analiza wymagań** | Wielowymiarowa analiza wymagań | Czterech analityków pracuje równolegle |
| **Tworzenie epików** | Epiki z user stories i kryteriami akceptacji | Kontekst projektu wbudowany automatycznie |
| **Generowanie dokumentów** | HLD, LLD, plany testów | Dynamiczne ładowanie umiejętności |
| **Plany testów** | Scenariusze testowe z edge cases | Uwzględnia specyfikę domeny |
| **Recenzja dokumentów** | Weryfikacja jakości i zgodności | Ocena wg Diátaxis i style guide |

---

## Pętla wiedzy

Unikalna cecha systemu. Pipeline 6-krokowy, który autonomicznie buduje nowe umiejętności z wiedzy rozproszonej po projekcie.

```mermaid
graph LR
    A["Zbieranie źródeł"] --> B["Ekstrakcja wiedzy"]
    B --> C["Sprawdzenie duplikatów"]
    C --> D["Projektowanie umiejętności"]
    D --> E["Kontrola jakości"]
    E --> F["Publikacja"]

    style A fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style B fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style C fill:#fefce8,stroke:#d97706,stroke-width:2px
    style D fill:#10b981,color:#fff,stroke:none
    style E fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style F fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

!!! success "Efekt kumulatywny"
    Każda nowa umiejętność trafia do repozytorium i jest automatycznie odkrywana przez przyszłe uruchomienia. System staje się lepszy z każdym użyciem — **bez zmian w kodzie**.

---

## Sprzężenie zwrotne

Obie pętle współpracują, tworząc cykl ciągłego doskonalenia:

```mermaid
graph TB
    AL["Pętla realizacji"]
    KL["Pętla wiedzy"]
    SR["Repozytorium umiejętności"]

    AL -->|"Identyfikuje luki"| KL
    KL -->|"Buduje umiejętności"| SR
    SR -->|"Wzbogaca jakość"| AL

    style AL fill:#1e293b,color:#f1f5f9,stroke:none
    style KL fill:#10b981,color:#fff,stroke:none
    style SR fill:#d97706,color:#fff,stroke:none
```

???+ example "Przykład"
    1. System generuje dokument API — recenzja wskazuje brak konwencji nazewnictwa
    2. Użytkownik uruchamia Pętlę Wiedzy: *„utwórz umiejętność o konwencjach GraphQL API”*
    3. Nowa umiejętność trafia do repozytorium
    4. Kolejne dokumenty API **automatycznie** korzystają z tej umiejętności
