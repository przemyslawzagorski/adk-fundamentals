# This MCP server was used for initial training. Since the [Comarch MCP Integration Tool](https://gitlab.czk.comarch/ai/mcp/mcp-integration-tool) is now available, we invite you to use the new one

# Jira, Wiki & GitLab MCP Integration

**Master branch:** Ready-to-use server ([jira-wiki-mcp-2.0.jar](server/jira-wiki-mcp-2.0.jar)) and client config ([mcp.json](client/mcp.json))  
**Develop branch:** Source code for extending functionality

---

## Quick Start

To use this MCP server:
1. Download [jira-wiki-mcp-2.0.jar](server/jira-wiki-mcp-2.0.jar) to your local machine.
2. Add [mcp.json](client/mcp.json) to your project or IDE.
3. Set the necessary parameters (if you need more info see below).
4. You're ready to go!

Step-by-step video guides are available below.

---

## Table of Contents


1. [General Info](#general-info)
2. [Available Tools](#available-tools)
3. [Environment Variables](#environment-variables)
4. [IDE Configuration](#ide-configuration)
5. [Implementation Details](#implementation-details)
6. [Contributing](#contributing)

---

## General Info


This project provides a set of tools delivered by the MCP (Model Context Protocol) server for integrating with Jira, Confluence Wiki, and GitLab systems.

If you're not familiar with MCP, check out this video: [MCP w 5 minut](https://youtu.be/rv9rxQ3F28o) *(PL - zostaw suba! Ziomeczek ogarnia)*

To run the MCP server, you only need Java 21. If you don't have it, you can download it in 30 seconds from:

To run the MCP server, you only need Java 21.  
If you don't have it, you can download it in 30 seconds from [Java 21](https://adoptium.net/temurin/releases/?version=21&os=any&arch=any).


---

## Available Tools


▶️ [Watch how it works](https://www.ibard.com/d/1c48228d480ae936708e2b22d56204f924517567)

### Jira Tools


| Tool                      | Description                                                        | Required Parameters                | Optional Parameters         |
|---------------------------|--------------------------------------------------------------------|------------------------------------|----------------------------|
| **jira_get_ticket**       | Get info about a Jira ticket by ID                                 | `ticketId` (e.g., `CLM6-11588`)    |                            |
| **jira_search**           | Search Jira tickets using JQL                                      | `jql` (Jira Query Language string) | `limit` (default: 10)      |
| **jira_my_open_tickets**  | Get unresolved tickets assigned to you, sorted by update           |                                    | `limit` (default: 10)      |
| **jira_create_ticket**    | Create a new Jira ticket <br>⚠️ Rate limited: 5/hr                |                                    |                            |
| **jira_add_comment**      | Add a comment to a Jira ticket <br>⚠️ Rate limited: 5/hr           |                                    |                            |


### Confluence Wiki Tools *(Optional)*
*Enable by setting `ENABLE_WIKI_INTEGRATION=true`*


| Tool                      | Description                                                    | Required Parameters                | Optional Parameters         |
|---------------------------|----------------------------------------------------------------|------------------------------------|----------------------------|
| **wiki_get_page**         | Get info about a Confluence Wiki page by ID                    | `pageId`                           |                            |
| **wiki_search**           | Search Wiki content using CQL                                  | `cql` (CQL string)                 | `limit` (default: 10)      |
| **wiki_get_page_by_url**  | Get Wiki page info by URL                                      | `url` (full Wiki page URL)         |                            |


### GitLab Tools *(Optional, set `ENABLE_GITLAB_INTEGRATION=true`)*

| Tool                      | Description                                                    |
|---------------------------|----------------------------------------------------------------|
| **gitlab_get_releases**   | Retrieve all releases from the configured GitLab project       |
| **gitlab_get_release**    | Get a specific release by tag name                             |
| **gitlab_get_wiki_page**  | Retrieve a GitLab wiki page by slug (e.g., for release notes)  |
| **gitlab_get_wiki_pages** | List all GitLab wiki pages                                     |

---

## Environment Variables


Set these in your IDE or in the `mcp.json` file.


### Jira Configuration *(always required)*


```
JIRA_BASE_URL="https://your-jira-instance.com/rest/api/2"
JIRA_BEARER_TOKEN="your-jira-token"
```


#### Optional defaults for ticket creation
```
JIRA_DEFAULT_PROJECT_KEY="CLM6"           # e.g., CLM6, PROJ
JIRA_DEFAULT_ISSUE_TYPE="Story"           # Story, Task, Bug, Epic
JIRA_DEFAULT_LABEL="CLM6_Polaris"         # e.g., CLM6_Polaris, team-name
```


### Wiki Integration *(optional)*
```
ENABLE_WIKI_INTEGRATION="true"
WIKI_BASE_URL="https://your-wiki-instance.com/rest/api"
WIKI_BEARER_TOKEN="your-wiki-token"
```


### GitLab Integration *(optional)*
```
ENABLE_GITLAB_INTEGRATION="true"
GITLAB_BASE_URL="https://your-gitlab-instance.com"
GITLAB_PROJECT_ID="your-project-id"  # e.g., bu130255/plc130254/clm-6/clm6-core
GITLAB_ACCESS_TOKEN="your-gitlab-token"
```

---

## IDE Configuration


▶️ [Watch the setup tutorial](https://www.ibard.com/d/3f9c8e073f97a0c51583ab501ef51afa5df669dc)


### Using Java (Java 21+ required)

#### VS Code
1. Copy [jira-wiki-mcp-2.0.jar](server/jira-wiki-mcp-2.0.jar) to your system.
2. Copy [mcp.json](client/mcp.json) to `.vscode/mcp.json`.
3. Set the path to the JAR file in your config.
4. Set environment parameters as above.

#### IntelliJ
1. Copy [jira-wiki-mcp-2.0.jar](server/jira-wiki-mcp-2.0.jar) to your system.
2. Copy [mcp.json](client/mcp.json) to `Settings` → `Languages & Frameworks` → `GitHub Copilot` → `Edit in mcp.json`.
3. Set the path to the JAR file in your config.
4. Set environment parameters as above.

> ⚠️ **JAVA**: If you have multiple Java versions or encounter issues, replace `"command": "java"` with the full path to your Java executable in [mcp.json](client/mcp.json), e.g.:
> - `"command": "/opt/jdk-21.0.2/bin/java"`
> - `"command": "C:/Program Files/Java/jdk-21.0.2/bin/java"`

### Using Docker
*TODO*

---

## Implementation Details


- Built with **Java 21** and MCP SDK **0.9.0**
- Integrates with:
  - [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v2/intro)
  - [Confluence Wiki REST API](https://developer.atlassian.com/cloud/confluence/rest/v1/intro)
  - [GitLab REST API](https://docs.gitlab.com/api/api_resources/)

---

## Contributing


This project currently contains only basic functionalities.

Feel free to add or change anything—contributions are welcome!

Source code is available on the `develop` branch.
