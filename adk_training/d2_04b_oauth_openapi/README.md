# D2.4b: REST API jako narzędzia — OpenAPIToolset + OAuth 2.0 (Google People + Calendar API)

## Czego się nauczysz?

- **OpenAPIToolset** – każda operacja ze specyfikacji OpenAPI staje się narzędziem agenta.
- **OAuth 2.0 (authorization code)** w ADK – `AuthScheme` + `AuthCredential`.
- Jak ADK **pauzuje** wywołanie narzędzia (`adk_request_credential`), czeka na logowanie
  użytkownika i **wznawia** je z tokenem.
- **Least privilege** – tylko te scope'y, których faktycznie potrzebuje endpoint.
- **Dwa toolsety, jedno logowanie** – People API i Calendar API współdzielą ten sam
  `auth_scheme` + `auth_credential`, więc token jest używany ponownie.
- **`before_tool_callback`** – deterministyczne uzupełnianie parametrów API
  (`calendar_id="primary"`, `requestId` dla Meet), których LLM nie musi pamiętać.

## Przypadki biznesowe

- **Self-service HR** – „Jaki mam e-mail służbowy?”, „Jak się nazywam w systemie?”.
- **CRM** – agent działający na danych zalogowanego handlowca (jego kontakty, kalendarz).
- **Asystent biurowy** – „Co mam jutro?”, „Umów spotkanie w czwartek o 10 z Janem, z linkiem Meet”.
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
root_agent = Agent(..., tools=[people_toolset, calendar_toolset])   # toolsety przekazujemy wprost
```

Drugi toolset – **Google Calendar** (spec `calendar_openapi_schema` w [schemas.py](schemas.py),
ręcznie napisany podzbiór Calendar API v3, bo Google publikuje Discovery, a nie OpenAPI):

| Narzędzie | Endpoint |
|---|---|
| `calendar_events_list` | `GET /calendars/{calendarId}/events` |
| `calendar_events_insert` | `POST /calendars/{calendarId}/events` (+ opcjonalnie link Google Meet) |
| `calendar_events_delete` | `DELETE /calendars/{calendarId}/events/{eventId}` |

Instrukcja agenta jest funkcją (`InstructionProvider`), która wstrzykuje bieżącą datę –
bez tego LLM nie wie, kiedy jest „jutro”.

Specyfikacja People API jest w [schemas.py](schemas.py). Ścieżka zawiera na sztywno
`?personFields=names,emailAddresses` – to uproszczenie dydaktyczne (patrz Ćwiczenie 1).

## Konfiguracja (jednorazowo)

1. Włącz People API i Calendar API w projekcie:
   ```bash
   gcloud services enable people.googleapis.com calendar-json.googleapis.com --project=<PROJECT_ID>
   ```
2. Google Cloud Console → **APIs & Services → OAuth consent screen** – skonfiguruj
   (typ *Internal* dla Workspace lub *External* + dodaj siebie jako test usera).
   W **Data access / Scopes** dodaj `.../auth/calendar.events` (scope „sensitive” – w trybie
   testowym nie wymaga weryfikacji Google).
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

### Demo: kalendarz (efekt „wow”)

Miej otwarty obok https://calendar.google.com i zapytaj:

1. „Co mam jutro w kalendarzu?” → `calendar_events_list`
2. „Umów mi jutro o 10:00 spotkanie »Demo ADK« na 30 minut z jan@example.com, z linkiem Meet.”
   → agent sprawdza konflikty, pokazuje podsumowanie i prosi o potwierdzenie
3. „Tak” → `calendar_events_insert` → wydarzenie z linkiem Meet pojawia się w kalendarzu,
   a uczestnik dostaje zaproszenie mailem (`sendUpdates=all`)
4. „Usuń to spotkanie” → `calendar_events_delete`

> Na szkoleniu używaj adresów uczestników albo własnych – zaproszenia są wysyłane naprawdę.

**Co pokazać w zakładce Events/Trace:** event `adk_request_credential`, następnie
ponowne wywołanie `people_get` już z tokenem. Przy kalendarzu: argumenty `calendar_events_insert`
po `before_tool_callback` (dopisane `calendar_id`, `requestId`, `conference_data_version`).

## Ćwiczenia

1. **Więcej pól** – zmień ścieżkę w `schemas.py` na
   `personFields=names,emailAddresses,phoneNumbers,organizations,photos`.
   Czy potrzebne są dodatkowe scope'y? (Podpowiedź: telefon → `user.phonenumbers.read`).
   Lepsza wersja: usuń query z path i zdefiniuj `personFields` jako parametr – niech LLM sam
   wybiera pola.
2. **Kalendarz – edycja** – dodaj do `calendar_openapi_schema` operację
   `PATCH /calendars/{calendarId}/events/{eventId}` (`calendar.events.patch`), dopisz ją do
   `tool_filter` i poproś „Przesuń to spotkanie na 11:00”.
3. **Obsługa błędów** – dodaj `after_tool_callback`, który zamienia odpowiedzi 401/403/429
   na przyjazne komunikaty dla użytkownika.

## Troubleshooting

| Problem | Przyczyna / rozwiązanie |
|---|---|
| `redirect_uri_mismatch` | Zarejestruj dokładnie `http://localhost:8000/dev-ui/` (ze slashem na końcu) i otwieraj UI pod tym samym hostem. |
| `invalid_client` | Zły Client ID/Secret albo klient typu *Desktop* zamiast *Web application*. |
| `access_denied` / brak zgody | Consent screen w trybie testowym – dodaj swoje konto jako test usera. |
| 403 `PERMISSION_DENIED` z People API | API nie jest włączone w projekcie klienta OAuth. |
| 403 `insufficientPermissions` z Calendar API | Token sprzed dodania scope'u kalendarza – zacznij nową sesję w `adk web` i zaloguj się ponownie; sprawdź, czy scope `calendar.events` jest na consent screen. |
| 403 `accessNotConfigured` z Calendar API | `gcloud services enable calendar-json.googleapis.com`. |
| Złe godziny wydarzeń | Ustaw `AGENT_TIMEZONE` w `.env` (domyślnie `Europe/Warsaw`). |
| Log `GOOGLE_CLIENT_ID ... not set` | Brak zmiennych w `.env` w katalogu, z którego uruchamiasz `adk web`. |

## Odnośniki

- [ADK – Authenticating with tools](https://google.github.io/adk-docs/tools/authentication/)
- [ADK – OpenAPI tools](https://google.github.io/adk-docs/tools/openapi-tools/)
- [Google People API – people.get](https://developers.google.com/people/api/rest/v1/people/get)
- [Google Calendar API – events](https://developers.google.com/calendar/api/v3/reference/events)
