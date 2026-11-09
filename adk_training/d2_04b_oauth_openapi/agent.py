"""
Bonus ADK06: REST API as tools - OpenAPIToolset + OAuth 2.0 (Google People + Calendar API)
==========================================================================================

``OpenAPIToolset`` turns every operation of an OpenAPI spec into a tool.
When a tool needs user credentials, ADK pauses the run with the
``adk_request_credential`` function call; ``adk web`` opens the Google consent
popup, exchanges the code for tokens and resumes the tool call.

Two toolsets share ONE auth scheme + credential, so the user signs in once
and the token is reused for People API and Calendar API.

Setup: OAuth client of type "Web application" with the authorized redirect URI
``http://localhost:8000/dev-ui/`` (see README).

Run (from ``adk_training``):
    adk web
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi.openapi.models import OAuth2, OAuthFlowAuthorizationCode, OAuthFlows
from google.adk import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.auth import AuthCredential, AuthCredentialTypes, OAuth2Auth
from google.adk.tools import BaseTool, ToolContext
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import (
    OpenAPIToolset,
)

from .schemas import calendar_openapi_schema, openapi_schema

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
TIMEZONE = os.getenv("AGENT_TIMEZONE", "Europe/Warsaw")

if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
    logger.warning("GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set - OAuth will fail.")

# Least privilege: profile for people_get + events (not full calendar admin).
SCOPES = {
    "openid": "OpenID Connect",
    "https://www.googleapis.com/auth/userinfo.email": "View your email address",
    "https://www.googleapis.com/auth/userinfo.profile": "See your basic profile",
    "https://www.googleapis.com/auth/calendar.events": "View and edit calendar events",
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

calendar_toolset = OpenAPIToolset(
    spec_str=calendar_openapi_schema,
    spec_str_type="yaml",
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
    tool_filter=[
        "calendar_events_list",
        "calendar_events_insert",
        "calendar_events_delete",
    ],
)


def fill_calendar_defaults(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> None:
    """Deterministic API plumbing the LLM should not have to remember."""
    if not tool.name.startswith("calendar_"):
        return None
    args.setdefault("calendar_id", "primary")
    if tool.name == "calendar_events_list":
        args.setdefault("single_events", True)
        args.setdefault("order_by", "startTime")
    if tool.name == "calendar_events_insert":
        args.setdefault("send_updates", "all")
        create_request = (args.get("conference_data") or {}).get("createRequest")
        if create_request is not None:
            create_request.setdefault("requestId", uuid.uuid4().hex)
            create_request.setdefault("conferenceSolutionKey", {"type": "hangoutsMeet"})
            args["conference_data_version"] = 1
    return None


def build_instruction(_: ReadonlyContext) -> str:
    now = datetime.now(ZoneInfo(TIMEZONE))
    return f"""You are a personal office assistant.

Current date and time: {now.strftime("%A, %Y-%m-%d %H:%M")} ({TIMEZONE}, UTC offset {now.strftime("%z")}).
Resolve relative dates ("tomorrow", "next Thursday") from this value.

Tools:
- `people_get` - the signed-in user's Google profile (name, email).
- `calendar_events_list` - agenda for a time range. Always pass time_min and time_max
  as RFC3339 with offset (e.g. 2026-11-12T00:00:00+01:00).
- `calendar_events_insert` - create a meeting. Use start/end with dateTime + timeZone "{TIMEZONE}".
  Default duration 30 minutes. If the user wants a video call / Meet / online meeting,
  pass conference_data={{"createRequest": {{"conferenceSolutionKey": {{"type": "hangoutsMeet"}}}}}}.
- `calendar_events_delete` - delete an event by id (find it first with calendar_events_list).

Rules:
- The first tool call asks the user to sign in with Google; this is expected.
- Before creating or deleting an event, check for conflicts with calendar_events_list,
  show a short summary (title, date, time, attendees, Meet yes/no) and ask for confirmation.
- After creating an event, return its htmlLink and hangoutLink (if present).
- Answer only with data returned by tools; never invent personal data.
- Reply in the user's language."""


root_agent = Agent(
    model=MODEL,
    name="office_assistant",
    description="Assistant that reads the user's Google profile and manages Google Calendar events.",
    instruction=build_instruction,
    tools=[people_toolset, calendar_toolset],
    before_tool_callback=fill_calendar_defaults,
)
