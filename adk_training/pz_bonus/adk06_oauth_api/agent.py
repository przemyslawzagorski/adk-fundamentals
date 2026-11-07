"""
Bonus ADK06: REST API as tools - OpenAPIToolset + OAuth 2.0 (Google People API)
================================================================================

``OpenAPIToolset`` turns every operation of an OpenAPI spec into a tool.
When a tool needs user credentials, ADK pauses the run with the
``adk_request_credential`` function call; ``adk web`` opens the Google consent
popup, exchanges the code for tokens and resumes the tool call.

Setup: OAuth client of type "Web application" with the authorized redirect URI
``http://localhost:8000/dev-ui/`` (see README).

Run (from ``adk_training/pz_bonus``):
    adk web .
"""

import logging
import os

from dotenv import load_dotenv
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk import Agent
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import (
    OpenAPIToolset,
)

from .schemas import openapi_schema

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = os.getenv("MODEL", "gemini-3.5-flash")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
    logger.warning("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set - OAuth will fail.")

# Least privilege: only what `people/me?personFields=names,emailAddresses` needs.
SCOPES = {
    "openid": "OpenID Connect",
    "https://www.googleapis.com/auth/userinfo.email": "View your email address",
    "https://www.googleapis.com/auth/userinfo.profile": "See your basic profile",
}

auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            scopes=SCOPES,
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OAUTH2,
    oauth2=OAuth2Auth(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET),
)

# operationId "people.get" becomes the tool name "people_get".
people_toolset = OpenAPIToolset(
    spec_str=openapi_schema,
    spec_str_type="yaml",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
    tool_filter=["people_get"],
)

root_agent = Agent(
    model=MODEL,
    name="hr_assistant",
    description="HR assistant that reads the signed-in user's Google profile.",
    instruction="""You are an HR assistant.

When the user asks about themselves ("me", "my", "mój", "moje"), call
`people_get` - it returns the signed-in user's Google profile (names, emails).
The first call asks the user to sign in with Google; this is expected.
Answer only with data returned by the tool; never invent personal data.
Reply in the user's language.""",
    tools=[people_toolset],
)
