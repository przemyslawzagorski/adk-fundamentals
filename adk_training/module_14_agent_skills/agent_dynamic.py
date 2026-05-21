"""
Module 14: Dynamic External Skills — ładowanie z GitHub w locie
================================================================

Demonstracja dynamicznego pobierania skilli z repozytoriów GitHub
BEZ wcześniejszego klonowania — agent ładuje skille at runtime.

3 podejścia:
  1. GitHub Raw Content API → tempdir → load_skill_from_dir
  2. GCS (Google Cloud Storage) → load_skill_from_gcs_dir (natywne w ADK)
  3. Ręczny parsing SKILL.md → models.Skill (bez zapisu na dysk)

Uruchomienie:
    cd module_14_agent_skills
    # Zamień tymczasowo:
    copy agent.py agent_backup.py
    copy agent_dynamic.py agent.py
    adk web .
"""

import os
import pathlib
import tempfile
import logging

import httpx
import yaml
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

logger = logging.getLogger(__name__)

# =============================================================================
# HELPER: Pobierz skill z GitHub w locie
# =============================================================================

def load_skill_from_github(
    repo: str,
    skill_path: str,
    branch: str = "main",
    files: list[str] | None = None,
) -> models.Skill:
    """Pobierz skill z GitHub repo i załaduj jako models.Skill.

    Podejście 1: Pobieram SKILL.md + pliki z references/ via GitHub Raw API,
    zapisuję do tempdir, potem ładuję standardowym load_skill_from_dir.

    Args:
        repo: "owner/repo" (np. "ComposioHQ/awesome-claude-skills")
        skill_path: Ścieżka do katalogu skilla w repo (np. "changelog-generator")
        branch: Branch/tag (domyślnie "main")
        files: Lista plików do pobrania (oprócz SKILL.md).
               Jeśli None — pobieramy tylko SKILL.md (bez references/).

    Returns:
        models.Skill załadowany z pobranych plików.

    Example:
        >>> skill = load_skill_from_github(
        ...     repo="ComposioHQ/awesome-claude-skills",
        ...     skill_path="changelog-generator",
        ...     branch="master",
        ... )
    """
    base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{skill_path}"

    # Pobierz SKILL.md (wymagany)
    skill_md_url = f"{base_url}/SKILL.md"
    logger.info("Downloading: %s", skill_md_url)

    response = httpx.get(skill_md_url, timeout=15, follow_redirects=True)
    response.raise_for_status()
    skill_md_content = response.text

    # Parsuj frontmatter aby poznać name (potrzebne do nazwy katalogu)
    parts = skill_md_content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid SKILL.md format from {skill_md_url}")
    frontmatter = yaml.safe_load(parts[1])
    skill_name = frontmatter["name"]

    # Utwórz tempdir z poprawną strukturą: {skill_name}/SKILL.md
    temp_base = pathlib.Path(tempfile.mkdtemp(prefix="adk_skill_"))
    skill_dir = temp_base / skill_name
    skill_dir.mkdir()

    # Zapisz SKILL.md
    (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")
    logger.info("Saved: %s/SKILL.md", skill_dir)

    # Pobierz dodatkowe pliki (references/, assets/, scripts/)
    if files:
        for file_path in files:
            file_url = f"{base_url}/{file_path}"
            logger.info("Downloading: %s", file_url)

            try:
                resp = httpx.get(file_url, timeout=15, follow_redirects=True)
                resp.raise_for_status()
            except httpx.HTTPStatusError:
                logger.warning("Failed to download: %s (skipping)", file_url)
                continue

            local_path = skill_dir / file_path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(resp.text, encoding="utf-8")
            logger.info("Saved: %s", local_path)

    # Załaduj standardowym load_skill_from_dir
    return load_skill_from_dir(skill_dir)


def load_skill_from_github_raw(
    repo: str,
    skill_path: str,
    branch: str = "main",
) -> models.Skill:
    """Pobierz skill z GitHub — podejście 2: bez zapisu na dysk.

    Parsuje SKILL.md bezpośrednio do models.Skill w pamięci.
    Nie pobiera references/ (tylko L1+L2, bez L3).
    Szybsze, ale ograniczone.

    Args:
        repo: "owner/repo"
        skill_path: Ścieżka do SKILL.md w repo
        branch: Branch/tag

    Returns:
        models.Skill z frontmatter + instructions (bez resources).
    """
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{skill_path}/SKILL.md"
    logger.info("Downloading (raw): %s", url)

    response = httpx.get(url, timeout=15, follow_redirects=True)
    response.raise_for_status()

    content = response.text
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid SKILL.md format from {url}")

    frontmatter_data = yaml.safe_load(parts[1])
    instructions = parts[2].strip()

    return models.Skill(
        frontmatter=models.Frontmatter.model_validate(frontmatter_data),
        instructions=instructions,
    )


# =============================================================================
# ŁADOWANIE SKILLI
# =============================================================================

# --- Lokalne skille (szybkie, zawsze dostępne) ---
pirate_code_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="pirate-code",
        description=(
            "Kodeks Pirata — zbiór zasad i praw obowiązujących na statku. "
            "Obejmuje podział łupów, dyscyplinę, rozstrzyganie sporów, "
            "prawa załogi i obowiązki kapitana."
        ),
    ),
    instructions=(
        "Kodeks Pirata — fundamentalne zasady każdego statku:\n\n"
        "1. **Podział łupów**: Kapitan — 2 udziały, Oficerowie — 1.5, "
        "Załoga — 1 udział.\n"
        "2. **Głosowanie**: Każdy członek załogi ma 1 głos.\n"
        "3. **Dyscyplina**: Kto kradnie od załogi — marooned.\n"
        "4. **Kłótnie**: Rozstrzygane na lądzie, sekundanci obowiązkowi.\n"
        "5. **Gotowość bojowa**: Broń czysta i gotowa.\n"
        "6. **Odszkodowania**: Utrata kończyny = 600 PoE.\n"
        "7. **Gaszenie świateł**: 20:00, Kto pije — na pokład.\n"
        "8. **Dezercja w boju**: Kara śmierci.\n"
        "9. **Muzycy**: Wolne w niedzielę.\n"
    ),
)

ship_maintenance_skill = load_skill_from_dir(SKILLS_DIR / "ship-maintenance")
crew_training_skill = load_skill_from_dir(SKILLS_DIR / "crew-training")

# --- Dynamiczne skille z GitHub (pobierane w locie!) ---
# UWAGA: Wymaga dostępu do internetu. Jeśli offline — używamy fallbacku.

GITHUB_SKILLS: list[models.Skill] = []

# Skill 1: changelog-generator z awesome-claude-skills (ComposioHQ)
# Podejście 1: pełne pobieranie z references/
try:
    changelog_skill = load_skill_from_github(
        repo="ComposioHQ/awesome-claude-skills",
        skill_path="changelog-generator",
        branch="master",
        # Nie znamy listy plików w references/ z góry,
        # więc podajemy None (tylko SKILL.md) lub znane pliki
    )
    GITHUB_SKILLS.append(changelog_skill)
    logger.info("✅ changelog-generator loaded from GitHub")
except Exception as e:
    logger.warning("⚠️ GitHub download failed for changelog-generator: %s", e)
    # Fallback: załaduj lokalną kopię
    try:
        changelog_skill = load_skill_from_dir(SKILLS_DIR / "changelog-generator")
        GITHUB_SKILLS.append(changelog_skill)
        logger.info("📁 changelog-generator loaded from local fallback")
    except Exception:
        logger.warning("❌ changelog-generator not available")

# Skill 2: content-research-writer (podejście 2: tylko L1+L2, bez dysku)
try:
    writer_skill = load_skill_from_github_raw(
        repo="ComposioHQ/awesome-claude-skills",
        skill_path="content-research-writer",
        branch="master",
    )
    GITHUB_SKILLS.append(writer_skill)
    logger.info("✅ content-research-writer loaded from GitHub (raw)")
except Exception as e:
    logger.warning("⚠️ GitHub download failed for content-research-writer: %s", e)

# --- Meta skill (kreator) ---
skill_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="skill-creator",
        description=(
            "Kreator nowych umiejętności — generuje kompletne pliki SKILL.md "
            "zgodne ze specyfikacją agentskills.io."
        ),
    ),
    instructions=(
        "Wygeneruj plik SKILL.md z:\n"
        "1. YAML frontmatter: name (kebab-case), description (max 1024 znaków)\n"
        "2. Markdown instructions: krokowe procedury\n"
        "3. Opcjonalnie: propozycja plików references/"
    ),
)


# =============================================================================
# SKILLTOOLSET
# =============================================================================

all_skills = [
    pirate_code_skill,
    ship_maintenance_skill,
    crew_training_skill,
    skill_creator,
    *GITHUB_SKILLS,  # Dynamicznie pobrane!
]

skill_toolset = SkillToolset(skills=all_skills)


# =============================================================================
# AGENT
# =============================================================================

loaded_names = [s.frontmatter.name for s in all_skills]
skills_list = "\n".join(f"- **{name}**" for name in loaded_names)

root_agent = Agent(
    model=MODEL,
    name="knowledge_treasurer",
    description="Skarbnik Wiedzy — agent z lokalnymi i dynamicznie pobranymi skilli.",
    instruction=(
        "Ahoj! Jesteś Skarbnikiem Wiedzy.\n\n"
        f"Dostępne skille ({len(all_skills)}):\n{skills_list}\n\n"
        "Niektóre skille zostały pobrane dynamicznie z GitHub w momencie startu.\n"
        "Jak działasz:\n"
        "1. Sprawdź listę skilli\n"
        "2. Załaduj odpowiedni skill\n"
        "3. Jeśli instrukcje wskazują na references/ — załaduj je\n"
        "4. Odpowiadaj na podstawie załadowanej wiedzy\n\n"
        "Jeśli pytanie nie pasuje — zaproponuj stworzenie nowego skilla."
    ),
    tools=[skill_toolset],
)
