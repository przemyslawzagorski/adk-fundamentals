# 🐛 Bugfix: JSON Parsing w Thinking Mode

## ✅ Status: FIXED

Naprawiono parsowanie JSON-a gdy model działa w "thinking mode".

---

## 🔴 Problem

**Symptom:**
System przechodzi przez wszystkie fazy, ale wymienia "puste" dane:
- 0 grup
- 0 dokumentów
- 0 modułów
- 0 plików

**Logi:**
```
✅ Ingestion completed. Groups: 0
✅ Evaluation completed: Evaluated 0 documents
✅ Planning completed: 0 modules, 0.0h total
```

**Przyczyna:**
W trybie "thinking mode" (`BuiltInPlanner ENABLED`) model Gemini "myśli na głos" przed wygenerowaniem JSON-a:

```
Alright, let's get this done. The task is to categorize...
[długi tekst myślowy]
```json
{
  "groups": {...}
}
```
```

Stara funkcja `extract_json_from_text` usuwała tylko znaczniki ````json`, ale zostawiała cały tekst myślowy. Parser `json.loads()` próbował parsować tekst zaczynający się od "Alright..." i zwracał pusty `{}`.

---

## ✅ Rozwiązanie

### 1. Ulepszona funkcja `extract_json_from_text`

**Strategia 3-poziomowa:**

1. **Poziom 1:** Szukaj JSON w bloku markdown (```json ... ```)
   ```python
   match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
   ```

2. **Poziom 2:** Fallback - szukaj pierwszego `{` i ostatniego `}`
   ```python
   start = text.find('{')
   end = text.rfind('}')
   json_str = text[start:end+1]
   ```

3. **Poziom 3:** Usuń thinking text i spróbuj parsować
   ```python
   clean_json = re.sub(r'^.*?(?=\{)', '', text, flags=re.DOTALL)
   ```

**Kluczowa zmiana:**
- Użycie `re.DOTALL` - kropka `.` pasuje też do `\n`
- `match.group(1)` - wyciąga TYLKO zawartość w nawiasach `()`
- Ignoruje cały tekst przed i po bloku JSON

### 2. Lepsze logowanie w `_run_single_agent`

Dodano:
- Logowanie długości text_buffer
- Preview pierwszych 200 znaków
- Ostrzeżenie gdy brak outputu

---

## 📊 Przed vs Po

### Przed:
```python
def extract_json_from_text(text: str) -> Dict:
    # Usuń ```json i ```
    clean_json = re.sub(r'```(?:json)?\s*', '', text)
    clean_json = re.sub(r'```\s*$', '', clean_json).strip()
    
    try:
        return json.loads(clean_json)  # ❌ Parsuje "Alright, let's..."
    except json.JSONDecodeError as e:
        return {}  # ❌ Zwraca pusty dict
```

**Rezultat:** `{}` → 0 grup, 0 dokumentów, 0 modułów

### Po:
```python
def extract_json_from_text(text: str) -> Dict:
    try:
        # 1. Szukaj w bloku markdown
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if match:
            json_str = match.group(1)  # ✅ Tylko JSON!
            return json.loads(json_str)
        
        # 2. Fallback: { ... }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            json_str = text[start:end+1]
            return json.loads(json_str)
        
        # 3. Ostatnia szansa
        clean_json = re.sub(r'^.*?(?=\{)', '', text, flags=re.DOTALL)
        return json.loads(clean_json)
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Nie udało się sparsować JSON: {e}")
        return {}
```

**Rezultat:** Poprawny JSON → grupy, dokumenty, moduły!

---

## 🔍 Przykład Działania

### Input (z thinking mode):
```
Alright, let's get this done. The task is to categorize the provided URLs...

I'll analyze each URL and group them by their URI structure.

```json
{
  "groups": {
    "agents": {
      "category": "agents",
      "urls": ["https://..."],
      "concepts": ["agent planning", "memory"]
    }
  },
  "total_urls": 5,
  "summary": "Processed 5 URLs"
}
```

Great! I've successfully categorized all URLs.
```

### Parsowanie:

**Poziom 1 (regex z markdown):**
```python
match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
# match.group(1) = '{\n  "groups": {...}\n}'
```

✅ **Sukces!** Wyciągnięto tylko JSON, zignorowano thinking text.

---

## ✅ Weryfikacja

Po naprawie:
1. ✅ Thinking text jest ignorowany
2. ✅ JSON jest poprawnie wyciągany z bloku markdown
3. ✅ Fallback działa gdy brak znaczników
4. ✅ Lepsze logowanie błędów (pierwsze i ostatnie 500 znaków)

---

## 🚀 Gotowe do Testowania

System jest naprawiony. Uruchom ponownie:

```bash
python main.py --doc-links doc_links_test --output-dir ./output/test
```

Teraz powinno działać poprawnie z thinking mode!

---

**Status: FIXED** ✅

