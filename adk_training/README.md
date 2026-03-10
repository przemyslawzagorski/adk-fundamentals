# ADK Training Materials

Materiały szkoleniowe do Google Agent Development Kit (ADK) z przykładami agentów AI.

## 🚀 Quick Start

### 1. Wymagania wstępne

- Python 3.12 lub nowszy
- Konto Google Cloud Platform (GCP)
- `gcloud` CLI zainstalowane i skonfigurowane

### 2. Instalacja

```bash
# Sklonuj repozytorium
git clone <your-repo-url>
cd adk_training

# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności
pip install google-adk
```

### 3. Konfiguracja GCP

```bash
# Zaloguj się do GCP
gcloud auth application-default login

# Ustaw domyślny projekt (opcjonalnie)
gcloud config set project YOUR_PROJECT_ID
```

### 4. Konfiguracja zmiennych środowiskowych

```bash
# Skopiuj przykładowy plik .env
cp .env.example .env

# Edytuj .env i wypełnij swoimi wartościami:
# - GOOGLE_CLOUD_PROJECT=twoj-projekt-id
# - GOOGLE_CLOUD_LOCATION=us-central1
```

## 📚 Moduły

### ✅ Gotowe do uruchomienia (bez dodatkowej konfiguracji)

- **Module 01**: Hello World - Podstawowy agent
- **Module 02**: Custom Tool - Agent z niestandardowymi narzędziami
- **Module 05**: Human-in-Loop - Agent z zatwierdzaniem przez człowieka
- **Module 11**: Memory Bank - Agent z pamięcią
- **Module 12**: Router Agent - Agent routujący zapytania

### ⚙️ Wymagają dodatkowej konfiguracji

- **Module 03**: RAG Agent - wymaga Vertex AI Search (SEARCH_ENGINE_ID)
- **Module 09**: Database - wymaga bazy danych (SQLite lub Postgres)
- **Module 15**: Gmail Integration - wymaga OAuth credentials (patrz niżej)

### 🚫 Pominięte w testach automatycznych

- **Module 06**: Cloud Run Deployment
- **Module 10**: Debugging
- **Module 13**: Agent Engine
- **Module 14**: BigQuery Observability
- **Module 16**: Resilience

## 🧪 Uruchamianie testów

### Wszystkie testy automatyczne

```bash
python adk_training/e2e_tests/run_all_tests.py
```

### Pojedynczy moduł

```bash
python adk_training/e2e_tests/test_module_01.py
```

### Wyniki testów

- ✅ **6/6 testów automatycznych** przechodzi pomyślnie
- ⚠️ **3 testy** mają znane ograniczenia (Module 04, 07, 08 - session state)
- 📝 **2 testy manualne** (Module 09 - bazy danych)

## 📧 Module 15: Gmail Integration - Konfiguracja OAuth

**WAŻNE**: Każdy użytkownik musi skonfigurować własne OAuth credentials!

### Dlaczego nie mogę użyć Twoich credentials?

OAuth 2.0 dla Gmail wymaga **interaktywnego logowania** przez przeglądarkę. Proces wygląda tak:

1. **Developer (Ty)** tworzy OAuth Client ID w swoim projekcie GCP
2. **User (kolega)** musi zalogować się przez przeglądarkę do **swojego** konta Gmail
3. Google generuje token dostępu dla **tego konkretnego użytkownika**

**Nie można** udostępnić tokenu, bo:
- Token jest przypisany do konkretnego konta Gmail
- Token wygasa i wymaga odświeżenia
- Naruszałoby to bezpieczeństwo (dostęp do cudzego Gmaila)

### Jak skonfigurować Gmail dla kolegi?

#### Opcja A: Kolega używa Twojego projektu GCP (ZALECANE)

1. **Ty (właściciel projektu GCP)**:
   - Dodaj kolegę jako użytkownika testowego w OAuth consent screen
   - Udostępnij mu Client ID i Client Secret (można przez .env)

2. **Kolega**:
   - Kopiuje Client ID i Client Secret do swojego `.env`
   - Uruchamia `adk web` i loguje się do **swojego** Gmaila
   - Google generuje token dla jego konta

#### Opcja B: Kolega tworzy własny projekt GCP

1. Kolega tworzy własny projekt GCP
2. Włącza Gmail API
3. Tworzy własny OAuth Client ID
4. Konfiguruje OAuth consent screen
5. Używa swoich credentials

### Instrukcje dla kolegi (Opcja A)

```bash
# 1. Skopiuj .env.example jako .env
cp .env.example .env

# 2. Wypełnij .env (dostaniesz ode mnie):
# GOOGLE_CLOUD_PROJECT=moj-projekt-id
# GMAIL_CLIENT_ID=twoj-client-id.apps.googleusercontent.com
# GMAIL_CLIENT_SECRET=twoj-client-secret

# 3. Uruchom ADK web interface
cd adk_training/module_15_gmail_integration
adk web

# 4. Otwórz przeglądarkę i zaloguj się do SWOJEGO Gmaila
# 5. Zatwierdź dostęp
# 6. Token zostanie zapisany lokalnie (NIE commituj go!)
```

## 📁 Struktura projektu

```
adk_training/
├── .env.example              # Przykładowa konfiguracja
├── .gitignore               # Ignorowane pliki
├── README.md                # Ten plik
├── module_01_hello_world/   # Moduły szkoleniowe
├── module_02_custom_tool/
├── ...
└── e2e_tests/               # Testy E2E
    ├── run_all_tests.py     # Uruchom wszystkie testy
    ├── test_module_01.py    # Testy poszczególnych modułów
    └── README.md            # Dokumentacja testów
```

## ⚠️ Bezpieczeństwo

**NIGDY NIE COMMITUJ:**
- ❌ `.env` - zawiera ID projektu i credentials
- ❌ `*-key.json` - service account keys
- ❌ `token.json` - OAuth tokens
- ❌ `credentials.json` - OAuth credentials
- ❌ `*.db` - bazy danych z danymi testowymi

Wszystkie te pliki są w `.gitignore`!

## 🆘 Troubleshooting

### "Permission denied" przy uruchamianiu testów

```bash
# Upewnij się że jesteś zalogowany do GCP
gcloud auth application-default login
```

### "Module not found: google.adk"

```bash
# Zainstaluj ADK
pip install google-adk
```

### "GOOGLE_CLOUD_PROJECT not set"

```bash
# Skopiuj .env.example jako .env i wypełnij wartości
cp .env.example .env
# Edytuj .env
```

### Gmail OAuth nie działa

- Sprawdź czy masz poprawny Client ID i Secret w `.env`
- Sprawdź czy jesteś dodany jako test user w OAuth consent screen
- Usuń stary `token.json` i zaloguj się ponownie

## 📞 Kontakt

Jeśli masz pytania lub problemy, skontaktuj się ze mną!

## 📄 Licencja

Materiały szkoleniowe - użytek wewnętrzny.

