"""
Moduł ADK06: OAuth API Integration - ROZWIĄZANIA ĆWICZEŃ
========================================================
Ćwiczenia:
1. Dodaj więcej pól z People API (telefon, organizacja, zdjęcie)
2. Dodaj Google Calendar API integration
3. Dodaj error handling dla OAuth i API errors
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.genai import types
from google.adk.tools.openapi_tool.openapi_spec_parser import rest_api_tool, OperationEndpoint
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

load_dotenv()

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = 'hr_manager_solution'

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# =============================================================================
# ĆWICZENIE 1: ROZSZERZONA SPECYFIKACJA PEOPLE API
# =============================================================================

# Rozszerzona OpenAPI spec z dodatkowymi polami
extended_people_api_schema = """
openapi: 3.0.3
info:
  title: Google People API - Extended
  version: v1
  description: Extended People API with phone, organization, and photos
servers:
  - url: https://people.googleapis.com

components:
  securitySchemes:
    google_oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://accounts.google.com/o/oauth2/v2/auth
          tokenUrl: https://oauth2.googleapis.com/token
          scopes:
            https://www.googleapis.com/auth/userinfo.email: View email
            https://www.googleapis.com/auth/userinfo.profile: View profile
            https://www.googleapis.com/auth/user.phonenumbers.read: View phone numbers
            https://www.googleapis.com/auth/user.organization.read: View organization

security:
  - google_oauth2:
      - https://www.googleapis.com/auth/userinfo.email
      - https://www.googleapis.com/auth/userinfo.profile

paths:
  /v1/people/me?personFields=names,emailAddresses,phoneNumbers,organizations,photos:
    get:
      summary: Get extended person info
      description: Get user profile with phone, organization, and photo
      operationId: people.get.extended
      responses:
        '200':
          description: Success
        '401':
          description: Unauthorized
        '403':
          description: Forbidden
      security:
        - google_oauth2:
            - https://www.googleapis.com/auth/userinfo.email
            - https://www.googleapis.com/auth/userinfo.profile
            - https://www.googleapis.com/auth/user.phonenumbers.read
            - https://www.googleapis.com/auth/user.organization.read
"""

# =============================================================================
# ĆWICZENIE 2: GOOGLE CALENDAR API INTEGRATION
# =============================================================================

calendar_api_schema = """
openapi: 3.0.3
info:
  title: Google Calendar API - Events List
  version: v3
  description: Access to user's calendar events
servers:
  - url: https://www.googleapis.com/calendar/v3

components:
  securitySchemes:
    google_oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://accounts.google.com/o/oauth2/v2/auth
          tokenUrl: https://oauth2.googleapis.com/token
          scopes:
            https://www.googleapis.com/auth/calendar.readonly: Read calendar

security:
  - google_oauth2:
      - https://www.googleapis.com/auth/calendar.readonly

paths:
  /calendars/primary/events:
    get:
      summary: List calendar events
      description: Get upcoming events from primary calendar
      operationId: calendar.events.list
      parameters:
        - name: maxResults
          in: query
          schema:
            type: integer
            default: 10
        - name: orderBy
          in: query
          schema:
            type: string
            default: startTime
        - name: singleEvents
          in: query
          schema:
            type: boolean
            default: true
        - name: timeMin
          in: query
          schema:
            type: string
            format: date-time
      responses:
        '200':
          description: Success
        '401':
          description: Unauthorized
"""

# =============================================================================
# AUTH CONFIGURATION
# =============================================================================

# Auth scheme z rozszerzonymi scopes
auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes={
                "openid": "openid",
                "https://www.googleapis.com/auth/cloud-platform": "cloud platform",
                "https://www.googleapis.com/auth/userinfo.email": "user email",
                "https://www.googleapis.com/auth/userinfo.profile": "user profile",
                "https://www.googleapis.com/auth/user.phonenumbers.read": "phone numbers",
                "https://www.googleapis.com/auth/user.organization.read": "organization",
                "https://www.googleapis.com/auth/calendar.readonly": "calendar read"
            },
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    ),
)

# =============================================================================
# TOOLSETS
# =============================================================================

# People API toolset (rozszerzony)
people_toolset = OpenAPIToolset(
    spec_str=extended_people_api_schema,
    spec_str_type="yaml",
    auth_credential=auth_credential,
    auth_scheme=auth_scheme
)

# Calendar API toolset
calendar_toolset = OpenAPIToolset(
    spec_str=calendar_api_schema,
    spec_str_type="yaml",
    auth_credential=auth_credential,
    auth_scheme=auth_scheme
)

# =============================================================================
# AGENT Z ROZSZERZONYMI MOŻLIWOŚCIAMI
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name=AGENT_APP_NAME,
    description="Advanced HR Manager with People API and Calendar access",
    instruction="""You are an advanced HR assistant with access to:

1. PEOPLE API (Extended):
   - Names and emails
   - Phone numbers
   - Organization and job title
   - Profile photos

2. CALENDAR API:
   - Upcoming events
   - Meeting schedules
   - Availability

CAPABILITIES:
- Answer questions about user profile
- Show contact information
- Display organization details
- Check calendar and availability

ERROR HANDLING:
- If API call fails, explain the error clearly
- If permissions are missing, guide user to grant them
- If data is not available, suggest alternatives

Be professional and helpful!
""",
    tools=[
        people_toolset.get_tool("people.get.extended"),
        calendar_toolset.get_tool("calendar.events.list")
    ]
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Ćwiczenie 1 - Rozszerzone dane:
   "What's my email?"
   "Show my phone number"
   "What's my job title?"
   "Show my organization"
   "Display my profile photo"

2. Ćwiczenie 2 - Calendar:
   "What are my upcoming meetings?"
   "Show my calendar for today"
   "Am I free this afternoon?"
   "List my next 5 events"

3. Ćwiczenie 3 - Error handling:
   (Testuj bez autoryzacji)
   (Testuj z wygasłym tokenem)
   (Testuj z brakującymi scopes)

4. Kompleksowy scenariusz:
   "Show my full profile"
   "What meetings do I have today?"
   "Am I available for a call at 3pm?"

KONFIGURACJA:

1. Google Cloud Console:
   - Włącz People API
   - Włącz Calendar API
   - Dodaj scopes do OAuth consent screen

2. .env:
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-secret

3. Uruchomienie:
   adk web

4. Autoryzacja:
   - Kliknij "Authorize"
   - Zaloguj się do Google
   - Zatwierdź wszystkie uprawnienia

UWAGA:
Przy pierwszym uruchomieniu Google poprosi o zatwierdzenie
wszystkich scopes (email, profile, phone, organization, calendar).
"""

