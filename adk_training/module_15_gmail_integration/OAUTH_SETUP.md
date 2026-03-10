# Gmail OAuth Setup - Instrukcje dla użytkowników

## 🔐 Dlaczego każdy user musi mieć własne OAuth credentials?

Gmail API używa **OAuth 2.0**, który wymaga:
1. **Interaktywnego logowania** przez przeglądarkę
2. **Zgody użytkownika** na dostęp do jego Gmaila
3. **Tokenu dostępu** przypisanego do konkretnego konta Gmail

**Nie można** udostępnić tokenu między użytkownikami, bo:
- Token jest przypisany do konkretnego konta Gmail (nie można go użyć dla innego konta)
- Token wygasa i wymaga odświeżenia
- Naruszałoby to bezpieczeństwo (dostęp do cudzego Gmaila)

## 🎯 Dwie opcje konfiguracji

### Opcja A: Użyj projektu GCP właściciela (ZALECANE dla zespołu)

**Właściciel projektu GCP** udostępnia swój projekt, ale **każdy user loguje się do swojego Gmaila**.

#### Kroki dla właściciela projektu:

1. **Utwórz OAuth Client ID** (jeśli jeszcze nie masz):
   - Przejdź do: https://console.cloud.google.com/apis/credentials
   - Wybierz swój projekt
   - Kliknij "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "ADK Gmail Integration"
   - Skopiuj Client ID i Client Secret

2. **Skonfiguruj OAuth Consent Screen**:
   - Przejdź do: https://console.cloud.google.com/apis/credentials/consent
   - User Type: "External" (lub "Internal" jeśli Google Workspace)
   - App name: "ADK Training"
   - User support email: twój email
   - Scopes: dodaj Gmail API scopes (gmail.readonly, gmail.send, etc.)
   - **Test users: DODAJ EMAILE WSZYSTKICH UŻYTKOWNIKÓW!**

3. **Udostępnij credentials użytkownikom**:
   - Wyślij im Client ID i Client Secret (np. przez bezpieczny kanał)
   - Lub dodaj do `.env.example` (ale NIE commituj prawdziwych wartości!)

#### Kroki dla użytkownika (kolegi):

1. **Otrzymaj credentials** od właściciela projektu

2. **Skonfiguruj .env**:
   ```bash
   # Edytuj adk_training/.env
   GOOGLE_CLOUD_PROJECT=projekt-wlasciciela
   GMAIL_CLIENT_ID=123456789.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=GOCSPX-abc123def456
   ```

3. **Uruchom OAuth flow**:
   ```bash
   cd adk_training/module_15_gmail_integration
   adk web
   ```

4. **Zaloguj się w przeglądarce**:
   - Otwórz URL który wyświetli `adk web`
   - Zaloguj się do **swojego** konta Gmail
   - Zatwierdź dostęp
   - Token zostanie zapisany lokalnie w `token.json`

5. **WAŻNE**: NIE commituj `token.json`! (jest w .gitignore)

---

### Opcja B: Każdy user tworzy własny projekt GCP

Jeśli nie chcesz udostępniać swojego projektu GCP, każdy user może stworzyć własny.

#### Kroki dla każdego użytkownika:

1. **Utwórz projekt GCP**: https://console.cloud.google.com/projectcreate

2. **Włącz Gmail API**: https://console.cloud.google.com/apis/library/gmail.googleapis.com

3. **Utwórz OAuth Client ID** (jak w Opcji A, krok 1)

4. **Skonfiguruj OAuth Consent Screen** (jak w Opcji A, krok 2)
   - Dodaj siebie jako test user

5. **Skonfiguruj .env** (jak w Opcji A, krok 2)

6. **Uruchom OAuth flow** (jak w Opcji A, kroki 3-5)

---

## 🧪 Testowanie

Po skonfigurowaniu OAuth:

```bash
# Uruchom agenta
cd adk_training/module_15_gmail_integration
adk web

# Przykładowe zapytania:
# - "Pokaż moje ostatnie emaile"
# - "Wyślij email do kolega@example.com"
# - "Szukaj emaili od szef@example.com"
```

## 🔒 Bezpieczeństwo

**NIGDY NIE COMMITUJ:**
- ❌ `token.json` - Twój osobisty token dostępu
- ❌ `credentials.json` - OAuth credentials (jeśli zapisane lokalnie)
- ❌ `.env` - zawiera Client Secret

**MOŻESZ udostępnić** (przez bezpieczny kanał):
- ✅ Client ID (nie jest tajny, ale lepiej nie publikować publicznie)
- ✅ Client Secret (TYLKO przez bezpieczny kanał, NIE przez Git!)

## ❓ FAQ

**Q: Czy mogę użyć tokenu kolegi?**  
A: NIE. Token jest przypisany do jego konta Gmail. Musisz wygenerować własny.

**Q: Czy mogę użyć Client ID/Secret kolegi?**  
A: TAK, jeśli kolega Cię dodał jako test user w OAuth consent screen.

**Q: Jak długo token jest ważny?**  
A: Token dostępu wygasa po ~1h, ale refresh token pozwala go odświeżyć automatycznie.

**Q: Co jeśli token wygaśnie?**  
A: ADK automatycznie odświeży token używając refresh token. Jeśli to nie zadziała, usuń `token.json` i zaloguj się ponownie.

**Q: Czy muszę płacić za Gmail API?**  
A: NIE. Gmail API ma darmowy limit (1 miliard quota units/dzień), co wystarcza na normalne użycie.

## 🆘 Troubleshooting

### "Access blocked: This app's request is invalid"
- Sprawdź czy jesteś dodany jako test user w OAuth consent screen
- Sprawdź czy Gmail API jest włączone w projekcie

### "invalid_client"
- Sprawdź czy Client ID i Client Secret są poprawne w `.env`
- Sprawdź czy używasz credentials z tego samego projektu GCP

### "Token has been expired or revoked"
```bash
# Usuń stary token i zaloguj się ponownie
rm token.json
adk web
```

### "redirect_uri_mismatch"
- Sprawdź czy redirect URI w OAuth Client ID zawiera `http://localhost:8080`
- Dodaj `http://localhost:8080/oauth2callback` jako authorized redirect URI

