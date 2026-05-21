# Dla decydentów

Strona dla product ownerów, security leadów i engineering managerów, którzy
muszą zdecydować, czy AuditOps należy do firmowego toolchainu. **Bez wymaganego kodu.**

## Pitch w jednym akapicie

AuditOps daje inżynierowi security możliwość powiedzenia _"przetestuj nową
stronę logowania na `staging.acme.test` pod kątem OWASP Top 10"_ zwykłym
językiem i otrzymania w odpowiedzi reprodukowalnego, audytowalnego raportu
Markdown z exit-code zrozumiałym dla CI. Każdy run zasila wiki pamięci
instytucjonalnej — drugi run na tym samym targecie korzysta z wiedzy
z pierwszego, bez ręcznego copy-paste findingów do Confluence.

## Czym AuditOps **nie jest**

| Czym nie jest | Dlaczego |
|---|---|
| Zastępstwem człowieka-pentestera | Kreatywność adwersarska nie jest w scope. |
| Skanerem, który uruchomisz na losowych URL | Wymuszona allowlista. |
| Bazą podatności | Findingi linkują do OWASP, nie do CVE. |
| WAF-em lub narzędziem runtime defence | Generuje raporty, nie blokuje ruchu. |

## Wartość Day-1

- **Regresyjne testy security w CI**: Tak samo jak unit testy łapią
  zepsuty kod, AuditOps łapie moment, gdy ktoś usuwa nagłówek CSP
  z deployu. Flaga `--fail-on high` łamie build przy regresjach.
- **Udokumentowane dowody**: Każdy run produkuje raport Markdown + JSON,
  który można dołączyć do ticketów Jira i PR review.
- **Mniej zamieszania "czy już to testowaliśmy?"**: Per-target wiki
  pokazuje każdy poprzedni run, każde finding i częstotliwość wystąpień.

## Wartość Day-30

- **Kumulujący się wgląd**: Po kilku tygodniach wiki audytów posiada
  bojowy katalog tego, jak aplikacja *faktycznie* zawodzi — bardziej
  wartościowe niż generyczna checklista OWASP.
- **LLM staje się mądrzejszy per-target, nie ogólnie**: Nie trenujemy
  żadnego modelu. Skill "audit-history" (V3) to po prostu wiki
  streszczone do prompta plannera. Pamięć żyje na dysku w markdown —
  można ją backupować, audytować, diffować, a nawet przejrzeć
  przez człowieka przed ponownym użyciem (HITL).

## Ryzyka i mitygacje

| Ryzyko | Mitygacja |
|---|---|
| LLM testuje target poza scope | Allowlista domen wymuszona przez `safety.runtime_guard`. |
| LLM odpływa od planu z destrukcyjnymi payloadami | DSL pozwala tylko na wybrane akcje (zob. `dsl.ALLOWED_ACTIONS`). |
| Operator zapomina, że odpala aktywny skan | Wymagane potwierdzenie disclaimer per-user, persystowane w sqlite. |
| Wiki rozjeżdża się / korupcja | Wiki pisze Python (nie LLM). `auditops wiki-lint` w CI. |
| LLM halucynuje findingi | Findingi powstają tylko z asercji Playwright w DSL; LLM tłumaczy tylko *plan*. |
| Koszt wymyka się spod kontroli | Rate-limiter ogranicza runy per-user per-godzina. |

## Co obiecujemy

1. LLM nigdy nie edytuje plików raportu, indeksu wiki, logu ani stron findingów.
2. Artefakty runa (`runs/<id>.md`, `report.md`, `report.json`) są
   niezmienialne.
3. Aktualizacje wiki są idempotentne — przepuszczenie ukończonego audytu
   przez recorder dwukrotnie nie duplikuje wystąpień.
4. CLI zwraca non-zero przy osiągnięciu skonfigurowanego progu severity,
   co Twój pipeline CI już rozumie.

## Czego **nie** obiecujemy

1. Pokrycia kategorii OWASP poza A01, A02, A03 i A05 (pozostałe opierają się
   na recon-only heurystykach).
2. Autentykowanych skanów dla dowolnych flow auth poza cookie + header
   injection (OAuth, OIDC, SAML wymagają dodatkowej obróbki).
3. Porównywalnego zachowania między wersjami Playwright/przeglądarki.

## Notki compliance

- Każdy run wymaga jawnego `DisclaimerAck` zapisującego user id, URL targetu,
  timestamp i wolnotekstowe oświadczenie. Store ack-ów to plik sqlite —
  audytorzy mogą go grepować.
- Raporty to pliki lokalne; domyślnie nic nigdzie nie jest uploadowane.
- Wywołanie LLM trafia do providera, na który skonfigurowany jest
  `module_23_auggie_integration` (domyślnie: Anthropic). Wyłącz egress
  w CI, jeśli wymagasz pracy air-gapped.
