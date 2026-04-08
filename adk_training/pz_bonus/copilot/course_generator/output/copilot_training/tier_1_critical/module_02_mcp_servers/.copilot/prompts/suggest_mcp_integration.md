### Sugestie integracji MCP dla bieżącego kontekstu

**Opis:**
Copilot, w oparciu o aktualny plik (jeśli jest dostępny) lub ogólny kontekst projektu `spring-petclinic`, proszę zasugeruj możliwe integracje z Custom MCP Servers. Pomyśl o obszarach, w których zewnętrzna logika lub dane mogłyby usprawnić pracę dewelopera.

**Scenariusz użycia:**
Deweloper pracuje nad konkretnym modułem (np. `Owner`, `Vet`) i zastanawia się, jak mógłby wykorzystać MCP do automatyzacji zadań, dostępu do wewnętrznej wiedzy lub integracji z innymi systemami. Prompt jest wywoływany w celu uzyskania inspiracji.

**Oczekiwany rezultat:**
Lista 2-3 konkretnych pomysłów na MCP Servers, które byłyby przydatne w danym kontekście `spring-petclinic`. Każda sugestia powinna zawierać krótki opis, przykład zapytania do MCP oraz potencjalne korzyści. Przykłady mogą obejmować integrację z systemem zarządzania zadaniami (Jira), wewnętrznym linterem kodu, narzędziem do generowania schematów baz danych lub bazą wiedzy o regułach biznesowych.

**Przykład interakcji:**
**Użytkownik:** (w pliku `OwnerController.java`) `/prompt suggest_mcp_integration`
**Copilot:** `W kontekście OwnerController.java, rozważ integrację z MCP, który mógłby: 1. Sprawdzać zgodność kodu z wewnętrznymi standardami walidacji pól formularza. 2. Generować fragmenty kodu SQL do migracji danych.`