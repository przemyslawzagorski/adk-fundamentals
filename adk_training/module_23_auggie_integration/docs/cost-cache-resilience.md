# Cache · cost · resilience

Trzy guardrails które robią różnicę między *demo* a *production*.

## LRU + TTL cache

`caching.py` — `Cache(max_size=1024, ttl_seconds=3600)`.

```python
from adk_training.module_23_auggie_integration.caching import get_cache

cache = get_cache()
key = cache.make_key(prompt=p, model=m, opts=o)    # SHA256
hit = cache.get(key)
if hit is None:
    result = expensive_call()
    cache.set(key, result)
```

Skip rules (nie cache'ujemy):
- prompt zawiera `success_criteria` (agentic loops — randomized).
- prompt zawiera `functions` (tool-call traces).

Endpoint: `POST /api/cache/clear`.

## Cost tracker

`cost_tracker.py` — `RATES_USD_PER_SEC` per model + per-tool aggregation.

```python
from adk_training.module_23_auggie_integration.cost_tracker import tracker
tracker.record(model="claude-sonnet-4.5", seconds=4.2, tool="WRITE_TESTS")
print(tracker.snapshot())   # {"total_usd": 0.00063, "by_tool": {...}, "by_model": {...}}
```

Endpoint: `GET /api/cost`. Frontend pokazuje *Cost panel* na żywo.

| Model | USD / sek (przykład) |
|---|---|
| `gemini-2.5-flash` | ~0.000007 |
| `claude-sonnet-4.5` | ~0.000150 |

Aktualizuj wartości w `cost_tracker.py` per pricing change.

## Resilience: retry + circuit breaker

`resilience.py`.

```python
from adk_training.module_23_auggie_integration.resilience import resilient

@resilient(max_retries=4, breaker_key="auggie")
def call_auggie(prompt: str) -> str:
    ...
```

| Parametr | Domyślna wartość |
|---|---|
| Retry backoff | 1 s, 2 s, 4 s, 8 s (exponential) |
| Circuit threshold | 5 błędów / 60 s |
| Open duration | 120 s (po tym half-open) |

Stan breakera w `/api/health` → pole `breaker`.

## Anti-patterns

- ❌ **Cache'owanie agentic loops** — fałszywe wyniki przy zmianie kontekstu.
- ❌ **Brak max-size w cache** — pamięć rośnie bez końca.
- ❌ **Retry bez jitter na rzeczywistym ruchu** — thundering herd. Tu mamy fixed backoff,
  bo workload jest interaktywny (1 użytkownik); rozważ jitter dla CI.
- ❌ **Breaker bez metryki** — bez `/api/health` nie wiesz że jesteś *open*.
