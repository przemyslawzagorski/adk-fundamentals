# Business value

> Pitch dla decydenta w 60 sekund + KPI w 5 minut.

## Problem

Programiści tracą czas na powtarzalne zadania (testy, review, exploracja kodu)
i jednocześnie korzystają z drogich modeli LLM **do wszystkiego** — nawet gdy
proste pytanie wystarczy.

## Rozwiązanie

**Two-tier orchestration**: tani model dispatchuje, drogi specjalista wykonuje.
Cache i circuit breaker eliminują zbędne wywołania. Cost tracker pokazuje USD
per tool w czasie rzeczywistym.

## ROI (przykładowy zespół 10 dev)

| Metryka | Bez Concierge | Z Concierge | Zysk |
|---|---|---|---|
| Średni koszt LLM / dev / dzień | $4–$8 | $1–$3 | **~60%** |
| Czas na PR review (manual) | 30 min | 5 min (AI draft) | **~80%** |
| Pokrycie testami nowych modułów | inkonsystentne | `WRITE_TESTS` w 1 kliknięciu | **+30%** pokrycia |
| MTTR błędów po deploy | high | mid (AI exploration kodu) | **-40%** |

Liczby orientacyjne — `cost_tracker` pokaże twoje rzeczywiste.

## KPI do dashboardu

Pull z `/api/cost` + `/api/telemetry`:

- `total_usd_24h` — koszt dzienny
- `cache_hit_rate` — efektywność cache (cel: > 30%)
- `avg_latency_p50_ms` per tool
- `breaker_open_count_24h` — niezawodność (cel: 0)
- `tools_run_24h` — adopcja

## Use cases

| Use case | Tool | Frekwencja typowa |
|---|---|---|
| Generowanie testów | `WRITE_TESTS` | 5–10 / dev / dzień |
| AI review PR | `REVIEW_PR` (CI) | każdy PR |
| Eksploracja nieznanego kodu | `EXPLAIN_CODE` | 3–5 / dev / dzień |
| Refactor sugestie | `REFACTOR` | tygodniowo |
| Audyt OWASP staging | AuditOps | przed releasem |

## Risks & mitigation

| Risk | Mitigation |
|---|---|
| Nieprzewidywalny koszt | Cost tracker + alerts (możesz dodać webhook na > $X / h) |
| Zła rekomendacja AI w PR | `ci_review` zawsze tylko *komentuje* — human approves |
| Lock-in na Claude | `auggie_factory` ma `DEFAULT_MODEL` — łatwo przełączyć |
| Lokalne dane do LLM | `auth.py` redaktuje sekrety; allowlista hostów dla AuditOps |

## Następne kroki dla pilota

1. Wdrożenie w jednym repo (1 dzień).
2. CI review na PR-ach (1 dzień).
3. Pomiar KPI przez 2 tygodnie.
4. Decyzja: rollout na więcej repo / dodanie własnych tools.
