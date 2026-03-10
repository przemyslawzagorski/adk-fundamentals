# Module 15: Message in a Bottle - Gmail Integration 📧

## Overview

The **Ship's Messenger** demonstrates Gmail integration using the `GmailToolset`. Send and receive emails, search your inbox, and manage drafts - all through natural language!

## Learning Objectives

- ✅ Configure OAuth credentials for Google APIs
- ✅ Use `GmailToolset` for email operations
- ✅ Handle authentication flows in agents
- ✅ Integrate external services with ADK

## Architecture

```
┌──────────────────────────────────────────────┐
│           Ship's Messenger Agent             │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │         GmailToolset                  │   │
│  │  - gmail_read_message                 │   │
│  │  - gmail_send_message                 │   │
│  │  - gmail_search                       │   │
│  │  - gmail_list_messages                │   │
│  └──────────────────┬───────────────────┘    │
└─────────────────────┼────────────────────────┘
                      │ OAuth 2.0
                      ▼
              ┌───────────────┐
              │   Gmail API   │
              └───────────────┘
```

## Key Concepts

### GmailToolset

```python
from google.adk.tools.google_api_tool import GmailToolset

gmail_toolset = GmailToolset(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET
)

root_agent = LlmAgent(
    name="messenger",
    model="gemini-2.5-flash",
    tools=[gmail_toolset]
)
```

## Setup

### 1. Configure OAuth in GCP Console

1. Go to **APIs & Services** → **Credentials**
2. Create **OAuth 2.0 Client ID** (Web application)
3. Add authorized redirect URIs
4. Download client ID and secret

### 2. Environment Setup

```bash
cp .env.template .env
```

Edit `.env`:
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLIENT_ID=your-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-oauth-client-secret
```

### 3. Enable Gmail API

```bash
gcloud services enable gmail.googleapis.com
```

## Running

```bash
cd module_15_gmail_integration
adk web
```

On first use, you'll be redirected to authenticate with Google.

## Available Tools

| Tool | Description |
|------|-------------|
| `gmail_list_messages` | List recent emails |
| `gmail_read_message` | Read a specific email |
| `gmail_send_message` | Send an email |
| `gmail_search` | Search emails |
| `gmail_create_draft` | Create a draft |

## Example Conversations

```
User: "Check my inbox"
Agent: "Aye! Here be yer recent messages..."

User: "Send a message to crew@ship.com saying 'Meeting at noon'"
Agent: "Message sent to crew@ship.com!"

User: "Search for emails about treasure maps"
Agent: "Found 3 messages mentionin' treasure maps..."
```

## Exercises

1. **Read Emails**: Ask the agent to summarize your inbox
2. **Send Email**: Compose and send a test message
3. **Search**: Find emails with specific keywords

## Security Notes

- Never commit OAuth credentials to git
- Use `.env` files for local development
- Rotate credentials regularly
- Request minimal OAuth scopes

## Pirate Theme 🏴‍☠️

The Ship's Messenger carries messages across the seven seas of the internet! Every email is a bottle cast into the digital ocean!

