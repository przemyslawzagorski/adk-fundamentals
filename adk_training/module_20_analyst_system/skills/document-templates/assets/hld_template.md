# [TODO: Document Title] — High-Level Design

## Przegląd

### Kontekst biznesowy

[TODO: Why this feature/change is needed. Business drivers, user needs.]

### Cel

[TODO: What this design achieves. Expected outcomes.]

### Zakres

**W zakresie:**
- [TODO: List what's included]

**Poza zakresem:**
- [TODO: List what's explicitly excluded]

---

## Architektura

### Diagram komponentów

[TODO: Component diagram — Mermaid, PlantUML, or description]

### Kluczowe komponenty

| Komponent | Odpowiedzialność | Technologia |
|-----------|-----------------|-------------|
| [TODO: Name] | [TODO: What it does] | [TODO: Key tech choices] |

### Przepływ danych

[TODO: Describe the main data flow through the system]

---

## Integracje

| System | Protokół | Kierunek | Format danych | Obsługa błędów |
|--------|----------|----------|---------------|----------------|
| [TODO] | [TODO: REST/Kafka/gRPC] | [TODO: in/out/bidirectional] | [TODO: JSON/Protobuf] | [TODO: retry/DLQ/circuit breaker] |

---

## Wymagania niefunkcjonalne

| Wymaganie | Cel | Uwagi |
|-----------|-----|-------|
| Wydajność | [TODO: e.g., p99 < 200ms] | |
| Skalowalność | [TODO: e.g., 10k req/s] | |
| Dostępność | [TODO: e.g., 99.9%] | |
| Bezpieczeństwo | [TODO: AuthN/AuthZ approach] | |

---

## Ryzyka

| Ryzyko | Prawdopodobieństwo | Wpływ | Mitygacja |
|--------|-------------------|-------|-----------|
| [TODO] | [TODO: low/medium/high] | [TODO: low/medium/high] | [TODO: mitigation strategy] |

---

## Decyzje architektoniczne

### DR-1: [TODO: Decision Title]

**Status:** Proposed
**Kontekst:** [TODO: Why this decision was needed]
**Decyzja:** [TODO: What was decided]
**Konsekwencje:** [TODO: What follows from this decision]

---

## [CONDITIONAL: Plan migracji]

[TODO: Only if replacing existing system. Migration strategy, rollback plan, data migration.]

---

## Powiązane dokumenty

- [TODO: Links to related documents, Jira epics, existing documentation]
