# D2.4b: REST API jako narzędzia — OpenAPIToolset + OAuth 2.0 (Google People API)

## Czego się nauczysz?

- **OpenAPIToolset** – każda operacja ze specyfikacji OpenAPI staje się narzędziem agenta.
- **OAuth 2.0 (authorization code)** w ADK – `AuthScheme` + `AuthCredential`.
- Jak ADK **pauzuje** wywołanie narzędzia (`adk_request_credential`), czeka na logowanie
  użytkownika i **wznawia** je z tokenem.
- **Least privilege** – tylko te scope'y, których faktycznie potrzebuje endpoint.

## Przypadki biznesowe

- **Self-service HR** – „Jaki mam e-mail służbowy?”, „Jak się nazywam w systemie?”.
- **CRM** – agent działający na danych zalogowanego handlowca (jego kontakty, kalendarz).
- **Każde wewnętrzne REST API** ze specyfikacją OpenAPI – zero ręcznego pisania wrapperów.

## Jak to działa

```
User: "Jaki mam e-mail?"
  → LLM wybiera narzędzie people_get
  → ADK: brak tokenu → event adk_request_credential (run się zatrzymuje)
  → adk web: popup Google (consent) → redirect na /dev-ui/ z ?code=...
  → ADK wymienia code na access token, zapisuje credential w sesji
  → people_get: GET https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses
  → LLM formułuje odpowiedź na podstawie wyniku
```

Kluczowe fragmenty z [agent.py](agent.py):

```python
auth_scheme = OAuth2(flows=OAuthFlows(authorizationCode=OAuthFlowAuthorizationCode(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes=SCOPES,                      # openid, userinfo.email, userinfo.profile
)))
auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET),
)
people_toolset = OpenAPIToolset(
    spec_str=openapi_schema, spec_str_type="yaml",
    auth_scheme=auth_scheme, auth_credential=auth_credential,
    tool_filter=["people_get"],         # operationId "people.get" → nazwa narzędzia "people_get"
)
root_agent = Agent(..., tools=[people_toolset])   # toolset przekazujemy wprost
```

Specyfikacja OpenAPI jest w [schemas.py](schemas.py). Ścieżka zawiera na sztywno
`?personFields=names,emailAddresses` – to uproszczenie dydaktyczne (patrz Ćwiczenie 1).

## Konfiguracja (jednorazowo)

1. Włącz People API w projekcie:
   ```bash
   gcloud services enable people.googleapis.com --project=<PROJECT_ID>
   ```
2. Google Cloud Console → **APIs & Services → OAuth consent screen** – skonfiguruj
   (typ *Internal* dla Workspace lub *External* + dodaj siebie jako test usera).
3. **Credentials → Create credentials → OAuth client ID**:
   - Application type: **Web application**
   - Authorized redirect URIs: **`http://localhost:8000/dev-ui/`**
     (oraz `http://127.0.0.1:8000/dev-ui/`, jeśli otwierasz UI pod tym adresem)
4. Client ID i Secret wpisz do `d2_04b_oauth_openapi/.env` (albo `adk_training/.env`) (wzór: [.env.template](.env.template)).
   **Nie commituj sekretów.**

> `adk web` w ADK 2.x używa jako redirect URI `window.location.origin + "/dev-ui/"`.
> Adres w przeglądarce musi zgadzać się 1:1 z zarejestrowanym URI (host i port).

## Uruchomienie

```powershell
cd adk_training
adk web
```

Otwórz http://localhost:8000, wybierz `d2_04b_oauth_openapi` i zapytaj:

- „What's my email address?” / „Jak się nazywam?”
- Pierwsze wywołanie pokaże przycisk logowania Google → zaloguj się → agent dokończy odpowiedź.

**Co pokazać w zakładce Events/Trace:** event `adk_request_credential`, następnie
ponowne wywołanie `people_get` już z tokenem.

## Ćwiczenia

1. **Więcej pól** – zmień ścieżkę w `schemas.py` na
   `personFields=names,emailAddresses,phoneNumbers,organizations,photos`.
   Czy potrzebne są dodatkowe scope'y? (Podpowiedź: telefon → `user.phonenumbers.read`).
   Lepsza wersja: usuń query z path i zdefiniuj `personFields` jako parametr – niech LLM sam
   wybiera pola.
2. **Kalendarz** – dodaj drugi `OpenAPIToolset` dla Calendar API
   (`GET /calendar/v3/users/me/calendarList`, scope `calendar.readonly`) i zapytaj
   „Jakie mam kalendarze?”.
3. **Obsługa błędów** – dodaj `after_tool_callback`, który zamienia odpowiedzi 401/403/429
   na przyjazne komunikaty dla użytkownika.

## Troubleshooting

| Problem | Przyczyna / rozwiązanie |
|---|---|
| `redirect_uri_mismatch` | Zarejestruj dokładnie `http://localhost:8000/dev-ui/` (ze slashem na końcu) i otwieraj UI pod tym samym hostem. |
| `invalid_client` | Zły Client ID/Secret albo klient typu *Desktop* zamiast *Web application*. |
| `access_denied` / brak zgody | Consent screen w trybie testowym – dodaj swoje konto jako test usera. |
| 403 `PERMISSION_DENIED` z People API | API nie jest włączone w projekcie klienta OAuth. |
| Log `GOOGLE_CLIENT_ID ... not set` | Brak zmiennych w `.env` w katalogu, z którego uruchamiasz `adk web`. |

## Odnośniki

- [ADK – Authenticating with tools](https://google.github.io/adk-docs/tools/authentication/)
- [ADK – OpenAPI tools](https://google.github.io/adk-docs/tools/openapi-tools/)
- [Google People API – people.get](https://developers.google.com/people/api/rest/v1/people/get)
