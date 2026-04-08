"""
🔍 GitHub Search Tool
Narzędzie do wyszukiwania repozytoriów na GitHub
"""

import logging
import requests
import os

logger = logging.getLogger(__name__)


def search_github(
    query: str,
    language: str = "Java",
    min_stars: int = 100,
    max_results: int = 10,
    sort: str = "stars"
) -> dict:
    """
    Searches GitHub repositories.
    
    Args:
        query: Search query (e.g., "spring boot sample")
        language: Programming language filter (default: "Java")
        min_stars: Minimum number of stars (default: 100)
        max_results: Maximum number of results (default: 10)
        sort: Sort by (stars, forks, updated) (default: "stars")
    
    Returns:
        Dictionary with:
        - repositories: List of repository info
        - total_count: Total number of results
        - error: Error message if failed
    """
    try:
        # GitHub API endpoint
        url = "https://api.github.com/search/repositories"
        
        # Build query
        full_query = f"{query} language:{language} stars:>={min_stars}"
        
        params = {
            "q": full_query,
            "sort": sort,
            "order": "desc",
            "per_page": max_results
        }
        
        # Headers (optional: add GitHub token for higher rate limits)
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Add token if available
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            headers["Authorization"] = f"token {github_token}"
            logger.info("Using GitHub token for authentication")
        else:
            logger.warning("No GITHUB_TOKEN found - rate limits will be lower")
        
        logger.info(f"Searching GitHub: {full_query}")
        
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        repositories = []
        for item in data.get("items", []):
            repo_info = {
                "name": item.get("name"),
                "full_name": item.get("full_name"),
                "url": item.get("html_url"),
                "clone_url": item.get("clone_url"),
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language", ""),
                "topics": item.get("topics", []),
                "license": item.get("license", {}).get("name", "No license") if item.get("license") else "No license",
                "updated_at": item.get("updated_at", ""),
                "size": item.get("size", 0)
            }
            repositories.append(repo_info)
        
        logger.info(f"✅ Found {len(repositories)} repositories")
        
        return {
            "repositories": repositories,
            "total_count": data.get("total_count", 0),
            "error": None
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching GitHub: {e}")
        return {
            "repositories": [],
            "total_count": 0,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error searching GitHub: {e}")
        return {
            "repositories": [],
            "total_count": 0,
            "error": str(e)
        }


def find_best_java_repository(
    concepts: list,
    min_stars: int = 500,
    max_results: int = 20
) -> dict:
    """
    Finds the best Java repository for training purposes.
    
    Args:
        concepts: List of concepts to cover (e.g., ["spring", "testing", "rest"])
        min_stars: Minimum stars (default: 500)
        max_results: Max results to analyze (default: 20)
    
    Returns:
        Best repository info or None
    """
    # Build query from concepts
    query = " ".join(concepts[:3])  # Use first 3 concepts
    
    result = search_github(
        query=query,
        language="Java",
        min_stars=min_stars,
        max_results=max_results
    )
    
    if result["error"] or not result["repositories"]:
        logger.warning("No repositories found")
        return {
            "error": "No repositories found",
            "name": "spring-petclinic",
            "full_name": "spring-projects/spring-petclinic",
            "url": "https://github.com/spring-projects/spring-petclinic",
            "clone_url": "https://github.com/spring-projects/spring-petclinic.git",
            "description": "Sample Spring Boot application (fallback)",
            "stars": 7500,
            "language": "Java",
            "topics": ["spring", "boot", "java"],
            "license": "Apache-2.0"
        }
    
    # Score repositories based on criteria
    scored_repos = []
    for repo in result["repositories"]:
        score = 0
        
        # Stars (normalized to 0-10)
        score += min(repo["stars"] / 1000, 10)
        
        # Has license (+5)
        if repo["license"] != "No license":
            score += 5
        
        # Has topics (+2 per relevant topic, max 10)
        relevant_topics = ["spring", "boot", "java", "rest", "testing", "sample", "demo"]
        topic_score = sum(2 for topic in repo["topics"] if topic in relevant_topics)
        score += min(topic_score, 10)
        
        # Size (prefer medium-sized repos: 1000-10000 KB)
        size_kb = repo["size"]
        if 1000 <= size_kb <= 10000:
            score += 5
        elif size_kb < 1000:
            score += 2  # Too small
        
        scored_repos.append((score, repo))
    
    # Sort by score
    scored_repos.sort(key=lambda x: x[0], reverse=True)
    
    if scored_repos:
        best_score, best_repo = scored_repos[0]
        logger.info(f"✅ Best repository: {best_repo['full_name']} (score: {best_score:.1f})")
        return best_repo

    # Fallback: spring-petclinic
    return {
        "error": "No repositories scored",
        "name": "spring-petclinic",
        "full_name": "spring-projects/spring-petclinic",
        "url": "https://github.com/spring-projects/spring-petclinic",
        "clone_url": "https://github.com/spring-projects/spring-petclinic.git",
        "description": "Sample Spring Boot application (fallback)",
        "stars": 7500,
        "language": "Java",
        "topics": ["spring", "boot", "java"],
        "license": "Apache-2.0"
    }

