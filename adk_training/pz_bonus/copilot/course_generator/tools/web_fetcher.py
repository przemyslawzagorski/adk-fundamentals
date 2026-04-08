"""
🌐 Web Fetcher Tool
Narzędzie do pobierania i parsowania dokumentacji z URL-i
"""

import logging
import requests
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


def fetch_and_parse_url(url: str, timeout: int = 30) -> dict:
    """
    Fetches and parses content from a URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds (default: 30)
    
    Returns:
        Dictionary with:
        - url: Original URL
        - title: Page title
        - content: Extracted text content
        - headings: List of headings (h1, h2, h3)
        - code_blocks: Number of code blocks found
        - error: Error message if failed
    """
    try:
        logger.info(f"Fetching URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Extract main content (VS Code docs usually in main or article tags)
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not main_content:
            return {
                "url": url,
                "title": title_text,
                "content": "",
                "headings": [],
                "code_blocks": 0,
                "error": "No main content found"
            }
        
        # Extract headings
        headings = []
        for heading in main_content.find_all(['h1', 'h2', 'h3']):
            headings.append({
                "level": heading.name,
                "text": heading.get_text().strip()
            })
        
        # Count code blocks
        code_blocks = len(main_content.find_all(['pre', 'code']))
        
        # Extract text content (remove scripts, styles)
        for script in main_content(["script", "style", "nav", "footer"]):
            script.decompose()
        
        content = main_content.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        
        logger.info(f"✅ Successfully fetched: {url} ({len(content)} chars, {len(headings)} headings)")
        
        return {
            "url": url,
            "title": title_text,
            "content": content,
            "headings": headings,
            "code_blocks": code_blocks,
            "error": None
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching {url}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "headings": [],
            "code_blocks": 0,
            "error": f"Timeout after {timeout}s"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "headings": [],
            "code_blocks": 0,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "headings": [],
            "code_blocks": 0,
            "error": str(e)
        }


def fetch_multiple_urls(urls: list, delay: float = 1.0) -> dict:
    """
    Fetches multiple URLs with delay between requests.
    
    Args:
        urls: List of URLs to fetch
        delay: Delay between requests in seconds (default: 1.0)
    
    Returns:
        Dictionary mapping URL to parsed content
    """
    results = {}
    
    for i, url in enumerate(urls):
        logger.info(f"Fetching {i+1}/{len(urls)}: {url}")
        results[url] = fetch_and_parse_url(url)
        
        # Delay between requests (except for last one)
        if i < len(urls) - 1:
            time.sleep(delay)
    
    return results

