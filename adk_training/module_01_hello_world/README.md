# ModuĹ‚ 1: Hello World Agent - Podstawowy Agent

## đź“š PrzeglÄ…d

Witaj! To Twoja pierwsza podrĂłĹĽ w Ĺ›wiat agentĂłw ADK. W tym module stworzysz prostego, ale funkcjonalnego agenta AI - podstawowego asystenta.

**Czas trwania:** 45 minut
**Poziom trudnoĹ›ci:** PoczÄ…tkujÄ…cy (nie wymaga wczeĹ›niejszego doĹ›wiadczenia z ADK)

## đźŽŻ Cele Edukacyjne

Po ukoĹ„czeniu tego moduĹ‚u bÄ™dziesz potrafiĹ‚:
- ZrozumieÄ‡ podstawowÄ… strukturÄ™ `LlmAgent`
- SkonfigurowaÄ‡ parametry: nazwÄ™ agenta, model i instrukcje
- UruchomiÄ‡ agenta za pomocÄ… komendy `adk web`
- WchodziÄ‡ w interakcjÄ™ z agentem przez interfejs webowy

## đź“ ZawartoĹ›Ä‡ ModuĹ‚u

```
module_01_hello_world/
â”śâ”€â”€ agent.py          # GĹ‚Ăłwny kod agenta
â”śâ”€â”€ .env.template     # Szablon konfiguracji Ĺ›rodowiska
â”śâ”€â”€ requirements.txt  # ZaleĹĽnoĹ›ci Python
â””â”€â”€ README.md         # Ten plik
```

## đźš€ Szybki Start

### Krok 1: Konfiguracja Ĺšrodowiska

```bash

# StwĂłrz Ĺ›rodowisko wirtualne (opcjonalne, ale zalecane)
python -m venv .venv

#aktywuj je
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# PrzejdĹş do tego moduĹ‚u
cd adk_training/module_01_hello_world

# Zainstaluj zaleĹĽnoĹ›ci
pip install -r requirements.txt

# Skopiuj szablon Ĺ›rodowiska
copy .env.template .env  # Windows
# cp .env.template .env  # macOS/Linux

# Edytuj .env i wpisz swĂłj GCP project ID (GOOGLE_CLOUD_LOCATION=global)
```

### Krok 2: Konfiguracja Uwierzytelniania GCP

```bash
# Zaloguj siÄ™ do Google Cloud
gcloud auth application-default login

# Ustaw swĂłj projekt
gcloud config set project TWOJ_PROJECT_ID

# Ustaw projekt rozliczeniowy dla ADC (usuwa ostrzeĹĽenie "without a quota project")
gcloud auth application-default set-quota-project TWOJ_PROJECT_ID
```

### Krok 3: Uruchomienie Agenta

```bash
# Uruchom interfejs webowy ADK
adk web
```

### Krok 4: Testowanie Agenta

1. OtwĂłrz URL pokazany w terminalu (zazwyczaj http://localhost:8000)
2. Wybierz "asystent_podstawowy" z listy rozwijanej agentĂłw
3. WyprĂłbuj te przykĹ‚adowe pytania:
   - "CzeĹ›Ä‡! Kim jesteĹ›?"
   - "Opowiedz mi o Pythonie"
   - "Co sprawia, ĹĽe agent AI jest dobry?"

## đź”‘ Kluczowe Koncepcje

### Klasa LlmAgent

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="nazwa_agenta",         # Unikalny identyfikator
    model="gemini-3.5-flash",    # Model LLM do uĹĽycia
    instruction="...",           # Prompt systemowy
    description="...",           # Dla systemĂłw wieloagentowych
)
```

### WaĹĽne Parametry

| Parametr | Opis | Wymagany |
|----------|------|----------|
| `name` | Unikalny identyfikator agenta | Tak |
| `model` | Model LLM (gemini-3.5-flash, itp.) | Tak |
| `instruction` | Prompt systemowy definiujÄ…cy zachowanie | Tak |
| `description` | Opis celu dla innych agentĂłw | Nie |

> **ADK 2:** `from google.adk import Agent` to ta sama klasa co `LlmAgent`
> (`Agent is LlmAgent == True`). Nowe przykĹ‚ady i dokumentacja uĹĽywajÄ… krĂłtszej nazwy `Agent`.

## đźŹ‹ď¸Ź Ä†wiczenia

### Ä†wiczenie 1.1: Modyfikacja OsobowoĹ›ci
ZmieĹ„ instrukcjÄ™, aby agent byĹ‚ bardziej formalny lub bardziej swobodny.

### Ä†wiczenie 1.2: WyprĂłbuj RĂłĹĽne Modele
DomyĹ›lnie moduĹ‚y uĹĽywajÄ… `gemini-3.5-flash-lite` (najtaĹ„szy). Ustaw w `.env`
`ADK_MODEL=gemini-3.5-flash` (lub `gemini-3.8-flash`) i porĂłwnaj czas, styl i
liczbÄ™ tokenĂłw (Events â†’ `usage_metadata`). Wpisz teĹĽ nieistniejÄ…cy model
(np. `gemini-9-flash`) i przeczytaj bĹ‚Ä…d `404 NOT_FOUND`.

### Ä†wiczenie 1.3: Dodaj Kontekst
Dodaj specyficznÄ… wiedzÄ™ do instrukcji (np. historiÄ™ firmy, nazwy produktĂłw).

## âť“ CzÄ™ste Problemy

### BĹ‚Ä…d "Could not authenticate"
```bash
# Ponownie uwierzytelnij siÄ™ z GCP
gcloud auth application-default login
```

### "Vertex AI API not enabled"
```bash
# WĹ‚Ä…cz API
gcloud services enable aiplatform.googleapis.com
```

### Agent Nie Pojawia SiÄ™ w Interfejsie Web
- Upewnij siÄ™, ĹĽe zmienna nazywa siÄ™ `root_agent` (ADK szuka tej nazwy)
- SprawdĹş, czy jesteĹ› we wĹ‚aĹ›ciwym katalogu

## đźŽ“ Co Dalej?

W **Module 2** nauczysz siÄ™ dawaÄ‡ agentowi niestandardowe narzÄ™dzia - specjalne zdolnoĹ›ci do interakcji ze Ĺ›wiatem poza zwykĹ‚Ä… konwersacjÄ…!

---

*"PodrĂłĹĽ tysiÄ…ca linii kodu zaczyna siÄ™ od jednego agenta."*