# Dlaczego AI Analyst?

## Problem

W złożonych projektach IT — setki modułów, tysiące encji, rozproszone zespoły — analityka staje się wąskim gardłem.

<div class="comparison" markdown>

<div class="before" markdown>

### Bez AI Analyst

- Dokumentacja pisana ręcznie, każdy dokument od zera
- Analiza wymagań zależy od jednego eksperta
- Wiedza domenowa rozproszona między wiki, Jira i kodem
- Onboarding nowych osób trwa tygodniami
- Brak spójnych standardów dokumentacji

</div>

<div class="after" markdown>

### Z AI Analyst

- Dokumenty generowane automatycznie z kontekstem projektu
- Czterech analityków AI bada każde wymaganie równolegle
- Centralna baza wiedzy — kontrakt projektu + repozytorium umiejętności
- System rozumie projekt od pierwszej minuty
- Jeden standard: Diátaxis, style guide, szablony

</div>

</div>

---

## Wartość biznesowa

<div class="grid-cards" markdown>

<div class="card" markdown>
<div class="card-icon">⚡</div>
<div class="card-value">10x</div>
<div class="card-title">Szybciej</div>
<div class="card-desc">Dokumenty w minutach zamiast godzin pracy manualnej</div>
</div>

<div class="card" markdown>
<div class="card-icon">🎯</div>
<div class="card-value">100%</div>
<div class="card-title">Spójność</div>
<div class="card-desc">Centralny standard — każdy dokument wg tych samych reguł</div>
</div>

<div class="card" markdown>
<div class="card-icon">🔄</div>
<div class="card-value">∞</div>
<div class="card-title">Samouczenie</div>
<div class="card-desc">System buduje nowe umiejętności autonomicznie</div>
</div>

<div class="card" markdown>
<div class="card-icon">📈</div>
<div class="card-value">0</div>
<div class="card-title">Utrata wiedzy</div>
<div class="card-desc">Wiedza zakodowana w systemie — nie odchodzi z ludźmi</div>
</div>

</div>

---

## Jak to działa w praktyce?

### Generowanie dokumentacji

> *„Wygeneruj High-Level Design dla modułu zarządzania alertami sieciowymi”*

```mermaid
graph LR
    A["Polecenie"] --> B["Klasyfikacja"]
    B --> C["Zbieranie kontekstu"]
    C --> D["Ładowanie umiejętności"]
    D --> E["Generowanie treści"]
    E --> F["Kontrola jakości"]
    F --> G["Gotowy dokument"]

    style A fill:#f8fafc,stroke:#cbd5e1,stroke-width:2px
    style E fill:#1e293b,color:#f1f5f9,stroke:none
    style F fill:#10b981,color:#fff,stroke:none
    style G fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

### Analiza wymagań

> *„Przeanalizuj: system musi obsługiwać masową aktywację 10 000 kart SIM”*

```mermaid
graph LR
    A["Wymaganie"] --> B["Zbieranie kontekstu"]
    B --> P["Analiza równoległa"]

    P --> C1["Jasność"]
    P --> C2["Zakres"]
    P --> C3["Zależności"]
    P --> C4["Luki"]

    C1 --> S["Synteza"]
    C2 --> S
    C3 --> S
    C4 --> S
    S --> R["Raport analityczny"]

    style P fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style S fill:#1e293b,color:#f1f5f9,stroke:none
    style R fill:#dcfce7,stroke:#22c55e,stroke-width:2px
```

### Budowanie wiedzy

> *„Utwórz umiejętność dotyczącą konwencji nazewnictwa w GraphQL API”*

```mermaid
graph LR
    A["Polecenie"] --> B["Zbieranie źródeł"]
    B --> C["Ekstrakcja wiedzy"]
    C --> D["Sprawdzenie duplikatów"]
    D --> E["Projektowanie"]
    E --> F["Kontrola jakości"]
    F --> G["Nowa umiejętność"]

    style E fill:#10b981,color:#fff,stroke:none
    style G fill:#fefce8,stroke:#d97706,stroke-width:2px
```

---

## Kluczowe pytania

???+ question "Ile osób trzeba do analizy jednego wymagania?"
    **Bez AI:** 1–2 seniorów, wielokrotne spotkania, szukanie w wiki.

    **Z AI Analyst:** Jedno polecenie → cztery niezależne analizy równolegle → zsyntezowany raport z rekomendacjami.

???+ question "Co się dzieje, gdy odchodzi kluczowy pracownik?"
    Wiedza jest zakodowana w **kontrakcie projektu** i **repozytorium umiejętności**. Nowe umiejętności budowane są autonomicznie — wiedza rośnie, nie ginie.

???+ question "Czy dokumentacja jest spójna między projektami?"
    Centralne umiejętności (Diátaxis, style guide) i szablony wymuszają jeden standard. System automatycznie weryfikuje jakość każdego dokumentu.
