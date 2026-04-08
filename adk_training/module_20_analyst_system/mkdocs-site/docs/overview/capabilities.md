# Możliwości

## Sześć orkiestratorów, jedno polecenie

Każdy orkiestrator to wyspecjalizowany pipeline agentów AI. Wystarczy polecenie w języku naturalnym — system sam wybierze odpowiednią ścieżkę.

---

=== "Analiza wymagań"

    **Wielowymiarowa analiza z czterema specjalistami pracującymi równolegle**

    Czterech analityków AI bada jednocześnie różne aspekty wymagania: jasność, zakres, zależności i luki dokumentacyjne. Wyniki scala synteza w spójny raport.

    ```mermaid
    graph LR
        A["Wymaganie"] --> B["Kontekst"]
        B --> P["Analiza równoległa"]
        P --> C1["Jasność"]
        P --> C2["Zakres"]
        P --> C3["Zależności"]
        P --> C4["Luki"]
        C1 --> S["Synteza"]
        C2 --> S
        C3 --> S
        C4 --> S
        S --> R["Raport"]

        style P fill:#ecfdf5,stroke:#10b981,stroke-width:2px
        style S fill:#1e293b,color:#f1f5f9,stroke:none
        style R fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    ```

    > *„Przeanalizuj: system musi obsługiwać masową aktywację 10 000 kart SIM w jednej partii”*

=== "Generowanie dokumentów"

    **HLD, LLD, plany testów — z dynamicznymi umiejętnościami**

    System rozpoznaje typ dokumentu, dobiera umiejętności i generuje treść zgodną ze standardami.

    ```mermaid
    graph LR
        A["Klasyfikacja"] --> B["Źródła"]
        B --> C["Tworzenie treści"]
        C --> D["Kontrola jakości"]
        D --> E["Zapis"]

        SK["Umiejętności"]
        SK -.-> C

        style C fill:#1e293b,color:#f1f5f9,stroke:none
        style SK fill:#fefce8,stroke:#d97706,stroke-width:2px
        style E fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    ```

    > *„Wygeneruj HLD dla modułu zarządzania alertami sieciowymi”*

=== "Tworzenie epików"

    **Kompletne epiki z user stories, kryteriami akceptacji i podziałem zadań**

    System zbiera kontekst projektu i generuje strukturę epiku gotową do backlogu.

    ```mermaid
    graph LR
        A["Kontekst"] --> B["Tworzenie"]
        B --> C["Kontrola jakości"]
        C --> D["Zapis"]

        style B fill:#1e293b,color:#f1f5f9,stroke:none
        style D fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    ```

    > *„Utwórz epik dla eksportu CDR do CSV z podziałem na user stories”*

=== "Recenzja"

    **Weryfikacja jakości dokumentu wg Diátaxis i style guide**

    System wczytuje dokument, ocenia go pod kątem sprawśi i zgodności ze standardami, a następnie dostarcza raport z rekomendacjami.

    > *„Zrecenzuj ten dokument pod kątem kompletności i zgodności z Diátaxis”*

=== "Budowanie wiedzy"

    **Autonomiczne tworzenie nowych umiejętności z wiedzy projektowej**

    Pipeline 6-krokowy z deduplikacją — system zbiera wiedzę, wyodrębnia konwencje, sprawdza duplikaty i tworzy nową umiejętność.

    ```mermaid
    graph LR
        A["Źródła"] --> B["Ekstrakcja"]
        B --> C["Deduplikacja"]
        C --> D["Projektowanie"]
        D --> E["Recenzja"]
        E --> F["Publikacja"]

        style D fill:#10b981,color:#fff,stroke:none
        style F fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    ```

    > *„Utwórz umiejętność o konwencjach nazewnictwa w API GraphQL”*

---

## Przykłady efektów

| Polecenie | Wynik |
|-----------|-------|
| *„Przeanalizuj wymaganie o masowej aktywacji SIM”* | Wielowymiarowy raport: jasność, zakres, zależności, luki |
| *„Wygeneruj HLD dla modułu billing”* | Dokument HLD zgodny z Diátaxis, z kontekstem projektu |
| *„Utwórz epik dla eksportu CDR”* | Epik z user stories, kryteriami akceptacji, podziałem |
| *„Zrecenzuj ten dokument”* | Raport z oceną jakości i konkretnymi rekomendacjami |
| *„Utwórz skill o konwencjach GraphQL”* | Nowa umiejętność w repozytorium, automatycznie odkrywana |
