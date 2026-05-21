---
hide:
  - toc
  - navigation
---

<div class="hero" markdown>

# AI Analyst System

<p class="hero-subtitle">
Analityk, który się uczy.<br/>
Generuje dokumenty z kontekstem projektu,<br/>
analizuje wymagania w minuty — i z każdym użyciem<br/>
jest lepszy niż poprzednio.
</p>

<div class="hero-actions" markdown>

[Poznaj wartość](overview/why.md){ .md-button .md-button--primary }
[Architektura](architecture/index.md){ .md-button }

</div>

</div>

<div class="stats-bar" markdown>
<div class="stat">
<span class="stat-value">6</span>
<span class="stat-label">Orkiestratorów</span>
</div>
<div class="stat">
<span class="stat-value">2</span>
<span class="stat-label">Pętle systemu</span>
</div>
<div class="stat">
<span class="stat-value">∞</span>
<span class="stat-label">Self-extending skills</span>
</div>
<div class="stat">
<span class="stat-value">3</span>
<span class="stat-label">Integracje</span>
</div>
</div>

---

## Jedno polecenie — kompletny wynik

Opisz zadanie w języku naturalnym. System automatycznie zbiera kontekst projektu, angażuje wyspecjalizowanych agentów AI i dostarcza gotowy wynik — z wiedzą domenową, która rośnie z każdym użyciem.

```mermaid
graph LR
    U["Użytkownik"] --> C["Analyst Captain"]
    C --> AL["Pętla realizacji"]
    C --> KL["Pętla wiedzy"]

    AL --> D["Dokumenty"]
    AL --> R["Raporty"]
    AL --> E["Epiki"]

    KL --> S["Nowe umiejętności"]
    S -.->|wzbogaca| AL

    style C fill:#1e293b,color:#f1f5f9,stroke:none
    style AL fill:#ecfdf5,stroke:#10b981,stroke-width:2px
    style KL fill:#fefce8,stroke:#d97706,stroke-width:2px
    style D fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    style R fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    style E fill:#dcfce7,stroke:#22c55e,stroke-width:2px
    style S fill:#fefce8,stroke:#d97706,stroke-width:2px
```

---

<div class="features-grid" markdown>

<div class="feature" markdown>

### Dokumentacja

HLD, LLD, plany testów — generowane z pełnym kontekstem projektu, zgodne z Diátaxis i standardami wewnętrznymi

</div>

<div class="feature" markdown>

### Analiza wymagań

Czterech specjalistów AI bada równolegle jasność, zakres, zależności i luki w dokumentacji

</div>

<div class="feature" markdown>

### Meta Skills

System sam tworzy nowe umiejętności z wiedzy projektowej — i natychmiast z nich korzysta. [Compound knowledge effect →](architecture/meta-skills.md)

</div>

</div>

---

<div class="nav-cards" markdown>

<div class="nav-card" markdown>

**Dlaczego AI Analyst?**

Jakie problemy rozwiązuje i jaką wartość przynosi organizacji

[Poznaj wartość :material-arrow-right:](overview/why.md)

</div>

<div class="nav-card" markdown>

**Architektura systemu**

Dwupętlowy design z inteligentnymi topologiami agentów

[Zobacz architekturę :material-arrow-right:](architecture/index.md)

</div>

<div class="nav-card" markdown>

**Rezultaty**

Mierzalne efekty: czas, jakość, compound knowledge

[Zobacz rezultaty :material-arrow-right:](overview/results.md)

</div>

</div>
