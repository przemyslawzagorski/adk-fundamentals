# 📊 Vertex AI Quota Limits & Optimization

## 🚨 PROBLEM: 429 RESOURCE_EXHAUSTED

System działa poprawnie, ale przekracza limity API Vertex AI.

---

## 📈 AKTUALNE LIMITY (Vertex AI - Paid Tier)

### Gemini Models - Standard PayGo

| Model | RPM (Requests/Min) | TPM (Tokens/Min) | Notatki |
|-------|-------------------|------------------|---------|
| **gemini-2.5-pro** | ~10-15 | ~32,000 | Wolniejszy, droższy |
| **gemini-2.5-flash** | ~60 | ~1,000,000 | Szybszy, tańszy |

**Źródło:** https://cloud.google.com/vertex-ai/generative-ai/docs/quotas

---

## 🔧 JAK PODNIEŚĆ LIMITY?

### Opcja 1: **Request Quota Increase** (Zalecane)

1. Przejdź do Google Cloud Console:
   ```
   https://console.cloud.google.com/iam-admin/quotas
   ```

2. Filtruj po:
   ```
   Service: Vertex AI API
   Quota: Online prediction requests per base model per minute per region per base_model
   ```

3. Wybierz model (np. `gemini-2.5-flash`)

4. Kliknij **EDIT QUOTAS** → **REQUEST INCREASE**

5. Uzasadnienie (przykład):
   ```
   We are building an AI-powered workspace generator for GitHub Copilot training.
   The system uses LoopAgent pattern (Writer->Critic->Controller) which requires
   multiple sequential requests per module. We need higher quota to generate
   8 training modules efficiently.
   
   Requested quota: 120 RPM for gemini-2.5-flash
   ```

6. **Czas oczekiwania:** 1-3 dni robocze

---

### Opcja 2: **Provisioned Throughput** (Dla produkcji)

Gwarantowana przepustowość bez limitów RPM.

**Koszt:** ~$0.50-2.00 per 1000 tokens (zależy od modelu)

**Dokumentacja:** https://cloud.google.com/vertex-ai/generative-ai/docs/provisioned-throughput

---

### Opcja 3: **Użyj Gemini API** zamiast Vertex AI

Gemini API (ai.google.dev) ma **wyższe limity** dla płatnych kont:

| Model | Free Tier RPM | Paid Tier RPM |
|-------|---------------|---------------|
| gemini-2.5-flash | 15 | **2,000** |
| gemini-2.5-pro | 2 | **1,000** |

**Jak zmienić:**

1. Pobierz API key z: https://aistudio.google.com/app/apikey

2. Zmień w `.env`:
   ```bash
   GOOGLE_API_KEY=your-gemini-api-key
   # Usuń GOOGLE_CLOUD_PROJECT i GOOGLE_CLOUD_LOCATION
   ```

3. ADK automatycznie użyje Gemini API zamiast Vertex AI

---

## 🎯 OPTYMALIZACJE W KODZIE

### ✅ Już zaimplementowane:

1. **Sekwencyjne wykonanie modułów** (zamiast równoległego)
   - Było: 3 moduły równolegle = 3x więcej requestów/min
   - Jest: 1 moduł na raz = stabilne RPM

2. **Request counter** - logowanie co 5 requestów:
   ```
   📊 API Requests: 15 total (12.5 RPM) | {'unknown': 15}
   ```

3. **Planning phase** - tylko 2 równoległe agenty (Research + Structure)

---

### 🔄 Możliwe dalsze optymalizacje:

1. **Exponential Backoff** - automatyczne retry z opóźnieniem
2. **Rate Limiting** - ograniczenie do 10 RPM w kodzie
3. **Batch Processing** - grupowanie requestów
4. **Caching** - cache dla powtarzających się promptów

---

## 📊 MONITORING

System automatycznie loguje:

```
📊 API Requests: 20 total (15.3 RPM) | {'gemini-2.5-pro': 8, 'gemini-2.5-flash': 12}
```

Po zakończeniu:

```
📊 FINAL API STATS:
   Total requests: 45
   Duration: 180.5s
   Average RPM: 15.0
   By model: {'gemini-2.5-pro': 18, 'gemini-2.5-flash': 27}
```

---

## 🚀 REKOMENDACJE

### Dla testów (teraz):
1. **Poczekaj 2-5 minut** między uruchomieniami
2. Lub **zmniejsz zakres** do 2-3 modułów (edytuj `main.py`)

### Dla produkcji:
1. **Request quota increase** dla `gemini-2.5-flash` do 120 RPM
2. Lub **użyj Gemini API** (2000 RPM dla Flash)
3. Rozważ **Provisioned Throughput** dla stabilnej wydajności

---

## 📞 SUPPORT

- **Quota increase:** https://console.cloud.google.com/iam-admin/quotas
- **Vertex AI docs:** https://cloud.google.com/vertex-ai/generative-ai/docs/quotas
- **Gemini API limits:** https://ai.google.dev/gemini-api/docs/rate-limits

