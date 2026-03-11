"""
🔍 Web Search Tool (DEPRECATED - v1.4.2)

⚠️ DEPRECATED: Ten plik nie jest już używany!
Zamiast tego używamy natywnego `google.adk.tools.google_search` w `documentation_research_agent.py`.

Powód: Natywny tool z ADK jest stabilniejszy i lepiej zarządza rate limiting.
"""

import logging
import asyncio
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def web_search(query: str, max_results: int = 5) -> str:
    """
    Searches for GitHub Copilot documentation and examples.
    
    Prioritizes:
    - GitHub Docs (docs.github.com)
    - GitHub Blog (github.blog)
    - Microsoft Learn (learn.microsoft.com)
    - VS Code Docs (code.visualstudio.com)
    
    Args:
        query: Search query (e.g., "GitHub Copilot Agent Mode 2026")
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Formatted string with search results
    """
    # THROTTLING: Wymuszamy 2s przerwy między zapytaniami (unikamy 429 z Google)
    await asyncio.sleep(5)
    logger.info(f"🔍 Web search (throttled): {query}")

    try:
        # Try using googlesearch-python
        from googlesearch import search
        
        results = []
        priority_domains = [
            "docs.github.com",
            "github.blog",
            "learn.microsoft.com",
            "skills.github.com",
            "code.visualstudio.com"
        ]
        
        # Add priority domains to query
        domain_query = f"{query} site:docs.github.com OR site:github.blog OR site:learn.microsoft.com"
        
        for url in search(domain_query, num_results=max_results, lang="en"):
            results.append(url)
            if len(results) >= max_results:
                break
        
        if not results:
            # Fallback: generic search
            for url in search(query, num_results=max_results, lang="en"):
                results.append(url)
                if len(results) >= max_results:
                    break
        
        # Format results
        formatted = f"Search results for '{query}':\n\n"
        for i, url in enumerate(results, 1):
            formatted += f"{i}. {url}\n"
        
        return formatted
        
    except ImportError:
        logger.warning("googlesearch-python not installed, using fallback")
        return _fallback_search(query)
    except Exception as e:
        logger.error(f"Search error: {e}")
        return _fallback_search(query)


def _fallback_search(query: str) -> str:
    """Fallback when googlesearch-python is not available"""
    
    # Hardcoded high-quality links for GitHub Copilot
    fallback_links = {
        "agent mode": [
            "https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-agent-mode",
            "https://github.blog/changelog/2024-11-01-github-copilot-agent-mode-now-available",
        ],
        "mcp": [
            "https://modelcontextprotocol.io/introduction",
            "https://github.com/modelcontextprotocol/servers",
        ],
        "custom agents": [
            "https://docs.github.com/en/copilot/building-copilot-extensions",
            "https://code.visualstudio.com/docs/copilot/copilot-extensibility-overview",
        ],
        "@workspace": [
            "https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide",
            "https://code.visualstudio.com/docs/copilot/workspace-context",
        ],
        "edits": [
            "https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-code-review",
            "https://code.visualstudio.com/docs/copilot/copilot-edits",
        ]
    }
    
    # Find relevant links
    query_lower = query.lower()
    relevant_links = []
    
    for keyword, links in fallback_links.items():
        if keyword in query_lower:
            relevant_links.extend(links)
    
    # If no specific match, return all
    if not relevant_links:
        for links in fallback_links.values():
            relevant_links.extend(links[:1])  # One from each category
    
    # Format results
    formatted = f"Search results for '{query}' (fallback mode):\n\n"
    for i, url in enumerate(relevant_links[:5], 1):
        formatted += f"{i}. {url}\n"
    
    formatted += "\nNote: Install 'googlesearch-python' for real-time search.\n"
    
    return formatted

