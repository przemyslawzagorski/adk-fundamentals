# Model zagrożeń

Systematyczne spojrzenie na to, **kto może zaatakować system**, **jak** i **jak się bronimy**.

Podejście: **STRIDE** (Spoofing, Tampering, Repudiation, Information disclosure, DoS, Elevation of privilege).

## Granice zaufania

```mermaid
flowchart LR
    subgraph "Sieć publiczna (niezaufana)"
      I[Internet]
    end
    subgraph "Sieć korporacyjna (półzaufana)"
      P[Reverse proxy + TLS]
      U[Użytkownicy]
    end
    subgraph "Host aplikacji (zaufany)"
      A[Code Analyst<br/>kontener, user app]
      V[(Wolumen<br/>web_data, repo)]
    end
    subgraph "Zewnętrzne API (warunkowo zaufane)"
      M[LLM + Embeddings]
    end
    I -.x.-> A
    U --> P
    P --> A
    A --> V
    A --> M
```

Linie przerywane oznaczają **odcięcie** — bezpośredni dostęp z internetu jest zabroniony (reverse proxy + autoryzacja).

## Aktorzy

| Aktor | Dostęp | Motywacja | Mitigacja |
|-------|--------|-----------|-----------|
| **Uprawniony użytkownik** | API key, dostęp do UI | Analiza i modyfikacja kodu | Rate limit, audit trail |
| **Złośliwy insider** | API key, dostęp do UI | Eksfiltracja, sabotaż | Sekrety wykluczone, branche tylko feature, audit trail |
| **Zewnętrzny napastnik bez auth** | brak auth | Rekonesans, DoS | 401 na wszystkim poza `/health`/`/ready`/`/metrics` |
| **Złośliwy autor pliku w repo** | pośredni (przez zawartość pliku) | Prompt injection | System instruction: "plik = dane", separacja Parts |
| **Dostawca LLM/Embeddings** | fragmenty kodu | Leak (mało prawdopodobne) | Wybór dostawcy, DPA, alternatywa lokalna |

## STRIDE per-komponent

### Web layer (FastAPI)

| Zagrożenie | Opis | Obrona |
|------------|------|--------|
| **S**poofing | podszycie się pod użytkownika | API key header + HTTPS (reverse proxy) |
| **T**ampering | zmiana żądania w tranzycie | TLS via reverse proxy |
| **R**epudiation | użytkownik zaprzecza akcji | Request-ID w logach + `X-Request-ID` w response |
| **I**nfo disclosure | leak odpowiedzi | DOMPurify, autoescape Jinja2, `/metrics` wewnętrzny |
| **D**oS | zapychanie serwera | SlowAPI rate limit + lock per-repo |
| **E**levation | eskalacja uprawnień | Brak ról w aplikacji — prawa jak uruchomiony kontener |

### Narzędzia (file/git/build)

| Zagrożenie | Opis | Obrona |
|------------|------|--------|
| **T**ampering | zapis poza repo (path traversal) | `safe_resolve` z realpath |
| **T**ampering | commit na `main` | `validate_branch_name` + blacklist |
| **I**nfo disclosure | odczyt `.env` | `is_secret_file` blokuje read/write/list |
| **E**levation | wstrzyknięcie w shell (git/maven) | `shell=False`, walidacja `test_filter` |
| **D**oS | zawieszenie build toolem | Timeout + cap outputu 8 KB |

### RAG (LlamaIndex)

| Zagrożenie | Opis | Obrona |
|------------|------|--------|
| **T**ampering | stary indeks po zapisie | `mark_file_dirty()` w wrapperze `write_file` |
| **I**nfo disclosure | indeks sekretów | Skip w `_should_index_file` (`is_secret_file`) |
| **D**oS | nieograniczony crawl | `_SKIP_DIRS` + limity rozmiaru |

### Agent (ADK Runner)

| Zagrożenie | Opis | Obrona |
|------------|------|--------|
| **T**ampering | prompt injection z pliku | System instruction: "plik = dane", błąd narzędzia = stop |
| **T**ampering | prompt injection z inputu | `sanitize_user_input`, osobny `types.Part` |
| **I**nfo disclosure | agent ujawnia klucze | System instruction zabrania ujawniania `api_key`/sekretów |
| **D**oS | pętla nieskończona LLM | Budget kroków w ADK (domyślny limit) |
| **E**levation | agent tworzy plik sekretu | `is_secret_file` blokuje `write_project_file` |

## Znane ograniczenia (akceptowane ryzyko)

!!! warning "Brak ról w aplikacji"
    Model uprawnień jest binarny: masz API key albo nie. Nie ma ról (admin/viewer).
    Dla bardziej szczegółowej kontroli użyj reverse proxy z OAuth/OIDC i przepuszczaj tylko określone ścieżki.

!!! warning "Stan in-memory"
    Indeksy i Runnery są w pamięci procesu. Restart = utrata stanu sesji chat
    (indeks jest persistowany na dysk przy shutdown lifespan).
    Multi-node wymaga sticky session i wspólnego wolumenu.

!!! warning "Brak podpisów commitów"
    Agent commituje jako użytkownik repo (git config w repo). Bez GPG sign.
    Jeśli compliance wymaga sign — skonfiguruj git GPG w kontenerze.

## Następny krok

- [Autoryzacja krok po kroku](autoryzacja.md) — jak dokładnie działa API key flow.
- [Path traversal](path-traversal.md) — dlaczego `safe_resolve` jest tak ostrożny.
- [Prompt injection](prompt-injection.md) — strategia mitigacji.
- [Pełny audyt](audyt.md) — lista znalezisk z trzech faz + status fixów.
