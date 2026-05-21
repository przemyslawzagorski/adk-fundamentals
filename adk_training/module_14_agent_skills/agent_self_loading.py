"""
Module 14: Self-Loading Agent — sam szuka, instaluje i używa skilli w locie
============================================================================

DEMO FLOW (użytkownik pisze):
  1. "Jakie skille masz?"            → agent: 2 lokalne
  2. "Potrzebuję coś do changelog"   → agent szuka → znajduje → instaluje
  3. "Jakie skille masz teraz?"      → agent: 3 skille (nowy widoczny!)
  4. "Wygeneruj changelog"           → agent używa nowo zainstalowanego skilla

Kluczowy mechanizm: HOT-RELOAD
  - skill_toolset._skills to zwykły dict
  - install_skill() dorzuca nowy wpis
  - list_skills / load_skill natychmiast go widzą

Uruchomienie:
    cd module_14_agent_skills
    adk web .              # po podmianie: copy agent_self_loading.py agent.py
"""

import json
import logging
import os
import pathlib
import tempfile
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.skills import load_skill_from_dir, models
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURACJA REPOZYTORIUM SKILLI
# =============================================================================

SKILL_REPO = "ComposioHQ/awesome-claude-skills"
SKILL_BRANCH = "master"

# Katalog skilli w repo (cache z GitHub API, żeby nie odpytywać za każdym razem)
# W produkcji: pobieramy z API lub z pliku index.json w repo
_REMOTE_SKILL_CATALOG: dict[str, str] | None = None


def _fetch_skill_catalog() -> dict[str, str]:
    """Pobierz katalog dostępnych skilli z GitHub API (lub cache).

    Returns:
        Dict {skill_name: description} — opis z SKILL.md frontmatter.
    """
    global _REMOTE_SKILL_CATALOG
    if _REMOTE_SKILL_CATALOG is not None:
        return _REMOTE_SKILL_CATALOG

    api_url = f"https://api.github.com/repos/{SKILL_REPO}/contents/?ref={SKILL_BRANCH}"
    logger.info("📡 Fetching skill catalog from: %s", api_url)

    resp = httpx.get(api_url, timeout=15, follow_redirects=True)
    resp.raise_for_status()

    catalog = {}
    for item in resp.json():
        if item["type"] == "dir" and item["name"] not in ("composio-skills", "template-skill"):
            catalog[item["name"]] = ""  # opis uzupełnimy lazy

    _REMOTE_SKILL_CATALOG = catalog
    logger.info("📦 Found %d skills in remote catalog", len(catalog))
    return catalog


def _download_and_load_skill(skill_name: str) -> models.Skill:
    """Pobierz skill z GitHub i załaduj jako models.Skill."""
    base_url = (
        f"https://raw.githubusercontent.com/{SKILL_REPO}/{SKILL_BRANCH}/{skill_name}"
    )

    # 1. Pobierz SKILL.md
    skill_md_url = f"{base_url}/SKILL.md"
    logger.info("⬇️  Downloading: %s", skill_md_url)
    resp = httpx.get(skill_md_url, timeout=15, follow_redirects=True)
    resp.raise_for_status()
    skill_md_content = resp.text

    # 2. Parsuj frontmatter
    parts = skill_md_content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid SKILL.md from {skill_md_url}")
    frontmatter = yaml.safe_load(parts[1])
    actual_name = frontmatter.get("name", skill_name)

    # 3. Zapisz do tempdir (wymagane przez load_skill_from_dir)
    temp_base = pathlib.Path(tempfile.mkdtemp(prefix="adk_hotload_"))
    skill_dir = temp_base / actual_name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

    # 4. Spróbuj pobrać znane pliki referencyjne (GitHub Tree API)
    try:
        tree_url = (
            f"https://api.github.com/repos/{SKILL_REPO}"
            f"/git/trees/{SKILL_BRANCH}?recursive=1"
        )
        tree_resp = httpx.get(tree_url, timeout=15, follow_redirects=True)
        tree_resp.raise_for_status()

        prefix = f"{skill_name}/"
        for item in tree_resp.json().get("tree", []):
            path = item.get("path", "")
            if path.startswith(prefix) and path != f"{prefix}SKILL.md":
                rel = path[len(prefix):]
                if any(rel.startswith(d) for d in ("references/", "assets/", "scripts/")):
                    file_url = f"{base_url}/{rel}"
                    try:
                        fr = httpx.get(file_url, timeout=10, follow_redirects=True)
                        fr.raise_for_status()
                        local_path = skill_dir / rel
                        local_path.parent.mkdir(parents=True, exist_ok=True)
                        local_path.write_text(fr.text, encoding="utf-8")
                        logger.info("  📄 Downloaded: %s", rel)
                    except Exception:
                        pass
    except Exception as e:
        logger.warning("Could not fetch file tree: %s", e)

    # 5. Załaduj standardowo
    return load_skill_from_dir(skill_dir)


# =============================================================================
# GLOBALNE: SkillToolset + rejestr (ten dict mutujemy!)
# =============================================================================

# Startujemy z 2 lokalnymi skillami
_initial_skills = [
    load_skill_from_dir(SKILLS_DIR / "ship-maintenance"),
    load_skill_from_dir(SKILLS_DIR / "crew-training"),
]

skill_toolset = SkillToolset(skills=_initial_skills)


# =============================================================================
# NARZĘDZIA AGENTA: search + install (FunctionTool)
# =============================================================================

def search_skill_store(query: str) -> dict:
    """Przeszukaj zdalny sklep z umiejętnościami (GitHub repo).

    Szuka skilli, których nazwa zawiera frazę z query.
    Zwraca listę dostępnych do instalacji.

    Args:
        query: Fraza do wyszukania (np. "changelog", "resume", "testing").
    """
    try:
        catalog = _fetch_skill_catalog()
    except Exception as e:
        return {"error": f"Nie udało się pobrać katalogu: {e}"}

    query_lower = query.lower()
    matches = []
    already_installed = set(skill_toolset._skills.keys())

    for name in sorted(catalog.keys()):
        if query_lower in name.lower():
            status = "✅ zainstalowany" if name in already_installed else "📦 dostępny"
            matches.append({"name": name, "status": status})

    if not matches:
        # Zwróć wszystkie jako sugesię
        all_names = sorted(catalog.keys())
        return {
            "message": f"Brak wyników dla '{query}'. Dostępne skille:",
            "available": all_names[:15],
            "total": len(all_names),
        }

    return {
        "query": query,
        "results": matches,
        "hint": "Użyj install_skill(name) aby zainstalować wybrany skill.",
    }


def install_skill(name: str) -> dict:
    """Zainstaluj skill ze zdalnego repozytorium.

    Pobiera SKILL.md + references/ z GitHub i dodaje do aktywnych skilli.
    Po instalacji skill jest natychmiast dostępny przez list_skills i load_skill.

    Args:
        name: Nazwa skilla do zainstalowania (np. "changelog-generator").
    """
    # Sprawdź czy już zainstalowany
    if name in skill_toolset._skills:
        skill = skill_toolset._skills[name]
        return {
            "status": "already_installed",
            "message": f"Skill '{name}' jest już zainstalowany.",
            "description": skill.frontmatter.description,
        }

    # Sprawdź czy istnieje w katalogu
    try:
        catalog = _fetch_skill_catalog()
        if name not in catalog:
            return {
                "status": "not_found",
                "message": f"Skill '{name}' nie istnieje w repozytorium.",
                "hint": "Użyj search_skill_store() aby znaleźć dostępne skille.",
            }
    except Exception as e:
        return {"status": "error", "message": f"Katalog niedostępny: {e}"}

    # Pobierz i zaladuj
    try:
        skill = _download_and_load_skill(name)
    except Exception as e:
        return {
            "status": "download_error",
            "message": f"Błąd pobierania '{name}': {e}",
        }

    # === HOT-RELOAD: dodaj do SkillToolset._skills ===
    skill_toolset._skills[skill.frontmatter.name] = skill

    installed_count = len(skill_toolset._skills)
    has_refs = bool(skill.resources and skill.resources.references)
    ref_files = list(skill.resources.references.keys()) if has_refs else []

    logger.info(
        "🔥 HOT-RELOAD: skill '%s' zainstalowany! Łącznie: %d",
        name,
        installed_count,
    )

    return {
        "status": "installed",
        "message": f"✅ Skill '{skill.frontmatter.name}' zainstalowany i gotowy!",
        "description": skill.frontmatter.description,
        "references": ref_files,
        "total_skills": installed_count,
        "hint": (
            f"Teraz użyj load_skill(name='{skill.frontmatter.name}') "
            "aby przeczytać instrukcje i zacząć korzystać."
        ),
    }


def list_installed_skills() -> dict:
    """Pokaż wszystkie aktualnie zainstalowane skille (lokalne + pobrane).

    Zwraca listę z nazwami, opisami i źródłem (local/remote).
    """
    result = []
    for name, skill in skill_toolset._skills.items():
        result.append({
            "name": name,
            "description": skill.frontmatter.description[:120],
            "has_references": bool(
                skill.resources and skill.resources.references
            ),
        })
    return {
        "total": len(result),
        "skills": result,
    }


# =============================================================================
# AGENT
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name="self_loading_agent",
    description=(
        "Agent z dynamicznym ładowaniem skilli — sam szuka, "
        "instaluje i używa umiejętności z GitHub w locie."
    ),
    instruction="""\
Jesteś Agentem z dynamicznym ładowaniem umiejętności (skills).

## Twoje narzędzia:

### 🔍 Wyszukiwanie
- **search_skill_store(query)** — przeszukaj zdalny katalog skilli na GitHub
- **list_installed_skills()** — pokaż aktualnie zainstalowane skille

### 📥 Instalacja  
- **install_skill(name)** — pobierz skill z GitHub i zainstaluj w locie
  Po instalacji skill jest NATYCHMIAST dostępny!

### 📚 Korzystanie ze skilli (z SkillToolset)
- **list_skills()** — lista zainstalowanych skilli (ta sama co list_installed_skills)
- **load_skill(name)** — załaduj instrukcje skilla
- **load_skill_resource(skill_name, path)** — załaduj plik referencyjny

## Jak działasz:

1. Gdy user prosi o coś czego nie wiesz — **szukaj** w skill store
2. Gdy znajdziesz pasujący skill — **zainstaluj** go
3. Po instalacji — **załaduj** instrukcje i działaj według nich
4. Zawsze informuj usera co robisz: "Szukam...", "Instaluję...", "Gotowe!"

## Przykładowa rozmowa:
- User: "Pomóż mi z changelogiem"
- Ty: "Sprawdzam skill store..." → search_skill_store("changelog")
- Ty: "Znalazłem! Instaluję..." → install_skill("changelog-generator")
- Ty: "Zainstalowany! Ładuję instrukcje..." → load_skill("changelog-generator")
- Ty: [działasz według instrukcji skilla]

## Stan początkowy:
Masz 2 lokalne skille: ship-maintenance, crew-training.
Resztę możesz doinstalować w locie z GitHub!
""",
    tools=[
        skill_toolset,
        FunctionTool(search_skill_store),
        FunctionTool(install_skill),
        FunctionTool(list_installed_skills),
    ],
)
