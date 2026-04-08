# Module 05: Human-in-the-Loop - Teoria

## 🎯 Kluczowe Koncepcje

### HumanInputTool - Zatwierdzanie przez Człowieka

**HumanInputTool** wstrzymuje wykonanie agenta i czeka na input od użytkownika.

```python
from google.adk.tools import HumanInputTool

human_tool = HumanInputTool()
response = human_tool.get_input("Czy zatwierdzasz transakcję?")
```

### Kiedy Używać Human-in-the-Loop?

| Scenariusz | Przykład |
|------------|----------|
| **Wysokie ryzyko** | Transakcje >10k PLN |
| **Compliance** | Operacje wymagające audytu |
| **Niejednoznaczność** | Agent nie jest pewien (confidence <70%) |
| **Krytyczne decyzje** | Usunięcie danych, deployment produkcyjny |

---

## 💼 Przypadki Użycia Biznesowego

### 1. Finanse: Zatwierdzanie Płatności

```python
def approve_payment(amount: float, vendor: str) -> str:
    if amount > 10000:
        human = HumanInputTool()
        response = human.get_input(
            f"Zatwierdź płatność {amount} PLN dla {vendor}?"
        )
        return "APPROVED" if "tak" in response.lower() else "REJECTED"
    return "AUTO_APPROVED"
```

**Korzyści:** Kontrola nad wysokimi wydatkami, audit trail, redukcja ryzyka.

### 2. HR: Rekrutacja - Screening CV

```python
def screen_candidate(cv_text: str) -> str:
    # AI ocenia CV
    score = ai_evaluate_cv(cv_text)
    
    if score > 80:
        return "AUTO_ACCEPT"
    elif score < 40:
        return "AUTO_REJECT"
    else:
        # Niejednoznaczne - poproś człowieka
        human = HumanInputTool()
        return human.get_input(
            f"CV score: {score}/100. Zaproś na rozmowę?\n{cv_text}"
        )
```

**Korzyści:** AI filtruje oczywiste przypadki, człowiek decyduje w trudnych.

### 3. Content Moderation: Flagowanie Treści

```python
def moderate_content(content: str) -> str:
    toxicity = ai_check_toxicity(content)
    
    if toxicity > 0.9:
        return "AUTO_REMOVE"
    elif toxicity > 0.5:
        human = HumanInputTool()
        return human.get_input(
            f"Toxicity: {toxicity}. Usuń treść?\n{content}"
        )
    return "APPROVED"
```

---

## ✅ Najlepsze Praktyki

### 1. Jasne Prompty dla Człowieka

**❌ Źle:**
```python
response = human.get_input("OK?")
```

**✅ Dobrze:**
```python
response = human.get_input("""
🔔 ZATWIERDZENIE WYMAGANE

Transakcja: 15,000 PLN
Odbiorca: Acme Corp
Kategoria: Consulting

Czy zatwierdzasz? (tak/nie)
""")
```

### 2. Walidacja Odpowiedzi

```python
response = human.get_input("Zatwierdź? (tak/nie)")

# Waliduj odpowiedź
if "tak" in response.lower() or "yes" in response.lower():
    return "APPROVED"
elif "nie" in response.lower() or "no" in response.lower():
    return "REJECTED"
else:
    # Niejednoznaczna odpowiedź - poproś ponownie
    return human.get_input("Proszę odpowiedz 'tak' lub 'nie'")
```

### 3. Kontekst dla Decyzji

Podaj człowiekowi **wszystkie** informacje potrzebne do decyzji:

```python
prompt = f"""
📊 ZATWIERDZENIE TRANSAKCJI

Kwota: {amount} PLN
Odbiorca: {vendor}
Kategoria: {category}
Budżet pozostały: {remaining_budget} PLN
Historia dostawcy: {vendor_history}

⚠️ Uwagi:
- Przekracza limit dzienny
- Nowy dostawca (brak historii)

Czy zatwierdzasz?
"""
```

### 4. Wieloetapowe Zatwierdzenia

```python
# Krok 1: Manager
manager_approval = human.get_input("Manager: Zatwierdź budżet?")
if "nie" in manager_approval.lower():
    return "REJECTED_BY_MANAGER"

# Krok 2: Finance
finance_approval = human.get_input("Finance: Zatwierdź płatność?")
if "nie" in finance_approval.lower():
    return "REJECTED_BY_FINANCE"

return "FULLY_APPROVED"
```

---

## ⚠️ Typowe Pułapki

### 1. Brak Timeoutów

**Problem:** Agent czeka w nieskończoność na odpowiedź.

**Rozwiązanie:** Ustaw timeout i domyślną akcję:
```python
# Koncepcyjnie (wymaga async):
try:
    response = await asyncio.wait_for(
        human.get_input("Zatwierdź?"),
        timeout=300  # 5 minut
    )
except asyncio.TimeoutError:
    return "AUTO_REJECTED (timeout)"
```

### 2. Zbyt Częste Prośby o Zatwierdzenie

**Problem:** Każda mała operacja wymaga zatwierdzenia → frustracja użytkownika.

**Rozwiązanie:** Ustal progi:
```python
if amount < 1000:
    return "AUTO_APPROVED"  # Małe kwoty
elif amount < 10000:
    # Tylko powiadomienie, bez zatwierdzenia
    log_transaction(amount, vendor)
    return "AUTO_APPROVED"
else:
    # Tylko wysokie kwoty wymagają zatwierdzenia
    return human.get_input(...)
```

### 3. Brak Logowania Decyzji

**Problem:** Nie wiadomo kto i kiedy zatwierdził.

**Rozwiązanie:** Loguj wszystkie decyzje:
```python
response = human.get_input(prompt)
log_approval_decision(
    user=current_user,
    timestamp=datetime.now(),
    decision=response,
    context={"amount": amount, "vendor": vendor}
)
```

### 4. Niejednoznaczne Odpowiedzi

**Problem:** Użytkownik pisze "może" zamiast "tak/nie".

**Rozwiązanie:** Wymuszaj format:
```python
while True:
    response = human.get_input("Zatwierdź? (wpisz TAK lub NIE)")
    if response.upper() in ["TAK", "NIE", "YES", "NO"]:
        break
    # Poproś ponownie
```

---

## 🔗 Odniesienia ADK

- [HumanInputTool Docs](https://google.github.io/adk-docs/tools/human-input/)
- [Human-in-the-Loop Patterns](https://google.github.io/adk-docs/patterns/human-in-loop/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **HumanInputTool** | Wstrzymuje agenta, czeka na input |
| **Kiedy używać** | Wysokie ryzyko, compliance, niejednoznaczność |
| **Jasne prompty** | Podaj pełny kontekst dla decyzji |
| **Walidacja** | Sprawdzaj format odpowiedzi |
| **Timeout** | Ustaw domyślną akcję po czasie |
| **Logowanie** | Audit trail wszystkich decyzji |

**Następny krok:** Module 07 - Parallel Agent (równoległe wykonanie)

