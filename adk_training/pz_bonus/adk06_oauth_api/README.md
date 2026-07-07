# Moduł ADK06: OAuth API Integration - Google People API

## 🎯 Czego się nauczysz?

W tym module poznasz:
- **OAuth 2.0** - bezpieczna autoryzacja użytkowników
- **OpenAPIToolset** - integracja z REST API przez OpenAPI spec
- **Google People API** - dostęp do danych użytkownika (profil, kontakty)
- **AuthCredential** - zarządzanie credentials w ADK
- **REST API Tools** - automatyczne generowanie narzędzi z OpenAPI

## 💼 Po co jest ten moduł? (Przypadki biznesowe)

### 1. HR Management System
**Scenariusz:** Agent HR zarządza danymi pracowników
- Agent pobiera dane z Google Workspace (email, telefon, stanowisko)
- Automatycznie aktualizuje bazę danych HR
- Odpowiada na pytania o pracowników

**Korzyści:** Synchronizacja danych, automatyzacja HR, self-service dla pracowników

### 2. CRM Integration
**Scenariusz:** Agent sprzedażowy z dostępem do kontaktów
- Pobiera dane kontaktów z Google Contacts
- Wzbogaca profile klientów
- Sugeruje follow-upy na podstawie historii

### 3. Personal Assistant
**Scenariusz:** Asystent osobisty z dostępem do profilu
- "What's my email address?"
- "Show my phone number"
- "Who are my contacts in the company?"

---

## 🏗️ Architektura i Flow

```
User: "What's my email?"
    ↓
Agent: Rozpoznaje potrzebę danych użytkownika
    ↓
Agent: Wywołuje people.get tool
    ↓
OpenAPIToolset: Wykonuje HTTP request do People API
    ↓
OAuth2: Autoryzuje request (access token)
    ↓
People API: Zwraca dane użytkownika
    ↓
Agent: Formatuje i prezentuje odpowiedź
    ↓
User: "Your email is john@company.com"
```

### OAuth 2.0 Flow

```
1. User: Uruchamia agenta
2. ADK: Przekierowuje do Google OAuth
3. User: Loguje się i zatwierdza uprawnienia
4. Google: Zwraca authorization code
5. ADK: Wymienia code na access token
6. Agent: Używa token do API calls
```

---

## 🔑 Kluczowe Koncepcje ADK

### 1. **OAuth 2.0 Authorization**

OAuth 2.0 to standard autoryzacji pozwalający aplikacji na dostęp do danych użytkownika bez udostępniania hasła.

```python
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows

auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes={
                "https://www.googleapis.com/auth/userinfo.email": "user email",
                "https://www.googleapis.com/auth/userinfo.profile": "user profile"
            }
        )
    )
)
```

### 2. **AuthCredential** - Credentials w ADK

```python
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
)
```

### 3. **OpenAPIToolset** - REST API jako Narzędzia

OpenAPIToolset automatycznie generuje narzędzia z OpenAPI specification:

```python
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

toolset = c(
    spec_str=openapi_schema,  # YAML/JSON spec
    spec_str_type="yaml",
    auth_credential=auth_credential,
    auth_scheme=auth_scheme
)

# Pobierz konkretne narzędzie
people_get_tool = toolset.get_tool("people.get")
```

### 4. **Google People API**

API do zarządzania kontaktami i danymi użytkownika:

**Endpoint:** `GET /v1/people/me`

**Zwraca:**
- Imię i nazwisko
- Email
- Telefon
- Zdjęcie profilowe
- Organizacja
- I więcej...

---

## 📋 Wymagania

### 1. Google Cloud Project

**Krok 1: Utwórz projekt**
```bash
gcloud projects create my-adk-project
gcloud config set project my-adk-project
```

**Krok 2: Włącz People API**
```bash
gcloud services enable people.googleapis.com
```

**Krok 3: Utwórz OAuth 2.0 Credentials**
1. Przejdź do [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Credentials
3. Create Credentials → OAuth 2.0 Client ID
4. Application type: Web application
5. Authorized redirect URIs: `http://localhost:8080/oauth2callback`
6. Pobierz Client ID i Client Secret

### 2. Zmienne środowiskowe (.env)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
ADK_MODEL=gemini-2.5-flash

# OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Instalacja
```bash
pip install google-adk python-dotenv fastapi
```

---

## 🚀 Quick Start

### Krok 1: Skonfiguruj credentials
Upewnij się że masz `GOOGLE_CLIENT_ID` i `GOOGLE_CLIENT_SECRET` w `.env`

### Krok 2: Uruchom agenta
```bash
cd adk_training/adk06_oauth_api
adk web
```

### Krok 3: Autoryzuj
1. Otwórz http://127.0.0.1:8000
2. Kliknij "Authorize" (jeśli pojawi się prompt)
3. Zaloguj się do Google
4. Zatwierdź uprawnienia

### Krok 4: Testuj
**Przykładowe zapytania:**
- "What's my email address?"
- "Show my profile information"
- "What's my name?"
- "Tell me about myself"

---

## 🧪 Ćwiczenia

### Ćwiczenie 1: Dodaj więcej pól z People API
**Cel:** Pobierz dodatkowe dane (telefon, organizacja, zdjęcie)

**Zadanie:**
1. Zmodyfikuj `personFields` w OpenAPI spec
2. Dodaj: `phoneNumbers`, `organizations`, `photos`
3. Agent powinien móc odpowiedzieć na "What's my phone number?"

**Wskazówka:**
```yaml
paths:
  /v1/people/me?personFields=names,emailAddresses,phoneNumbers,organizations:
```

### Ćwiczenie 2: Dodaj Google Calendar API
**Cel:** Agent może sprawdzać kalendarz użytkownika

**Zadanie:**
1. Włącz Calendar API w GCP
2. Dodaj scope: `https://www.googleapis.com/auth/calendar.readonly`
3. Stwórz OpenAPI spec dla Calendar API
4. Dodaj toolset do agenta

### Ćwiczenie 3: Dodaj error handling
**Cel:** Obsługa błędów OAuth i API

**Zadanie:**
1. Obsłuż przypadek gdy token wygasł
2. Obsłuż brak uprawnień (403)
3. Obsłuż rate limiting (429)
4. Zwróć przyjazne komunikaty użytkownikowi

---

## 🔧 Troubleshooting

### Problem 1: "OAuth error: invalid_client"
**Przyczyna:** Nieprawidłowy Client ID lub Secret

**Rozwiązanie:**
- Sprawdź czy credentials w `.env` są poprawne
- Upewnij się że skopiowałeś pełny Client ID (kończy się na `.apps.googleusercontent.com`)

### Problem 2: "redirect_uri_mismatch"
**Przyczyna:** Redirect URI nie jest autoryzowany

**Rozwiązanie:**
1. Przejdź do Google Cloud Console → Credentials
2. Edytuj OAuth 2.0 Client
3. Dodaj: `http://localhost:8080/oauth2callback`
4. Zapisz i spróbuj ponownie

### Problem 3: "insufficient_permissions"
**Przyczyna:** Brak wymaganych scopes

**Rozwiązanie:**
- Sprawdź czy scopes w `auth_scheme` zawierają wymagane uprawnienia
- Wyloguj się i zaloguj ponownie (aby odświeżyć scopes)

### Problem 4: "People API not enabled"
**Rozwiązanie:**
```bash
gcloud services enable people.googleapis.com --project=YOUR_PROJECT
```

---

## 📚 Odniesienia

- [Google People API](https://developers.google.com/people)
- [OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [OpenAPI Specification](https://swagger.io/specification/)
- [ADK OpenAPIToolset](https://google.github.io/adk-docs/tools/openapi/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **OAuth 2.0** | Bezpieczna autoryzacja bez udostępniania hasła |
| **OpenAPIToolset** | Auto-generowanie narzędzi z OpenAPI spec |
| **AuthCredential** | Zarządzanie credentials w ADK |
| **People API** | Dostęp do danych użytkownika i kontaktów |
| **Scopes** | Uprawnienia określające dostęp do danych |

**Poprzedni moduł:** A03 - Autoimport Files  
**Następny moduł:** ADK Services 04 - Memory Bank

