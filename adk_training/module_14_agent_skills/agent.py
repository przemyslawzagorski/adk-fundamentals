"""
Module 14: Agent Skills — Skarbnik Wiedzy Pirackiej
====================================================

Ten moduł demonstruje ADK Agent Skills i wzorzec progressive disclosure.
Zamiast pakować całą wiedzę w system prompt (~10 000 tokenów),
agent ładuje umiejętności (skills) na żądanie w 3 poziomach:

  L1 — Metadata (~100 tok/skill): nazwa i opis, zawsze w kontekście
  L2 — Instructions (~300-500 tok): pełne instrukcje, ładowane gdy agent uzna skill za trafny
  L3 — Resources (dowolny rozmiar): pliki referencyjne, ładowane tylko gdy instrukcje się do nich odwołują

Kluczowe koncepcje:
- SkillToolset — automatycznie generuje 3 narzędzia: list_skills, load_skill, load_skill_resource
- 4 wzorce skills: inline, file-based, external, meta
- Progressive disclosure — bazowy kontekst ~400 tok zamiast ~10 000 tok

Uruchomienie:
    cd module_14_agent_skills
    adk web .
"""

import os
import pathlib

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.skills import models
from google.adk.tools.skill_toolset import SkillToolset

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# WZORZEC 1: INLINE SKILL — Kodeks Pirata
# =============================================================================
# Najprostszy wzorzec — skill zdefiniowany bezpośrednio w Pythonie.
# Idealne dla stabilnych, prostych reguł które rzadko się zmieniają.
# Tylko L1 (metadata) + L2 (instructions), bez L3 (resources).

pirate_code_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="pirate-code",
        description=(
            "Kodeks Pirata — zbiór zasad i praw obowiązujących na statku. "
            "Obejmuje podział łupów, dyscyplinę, rozstrzyganie sporów, "
            "prawa załogi i obowiązki kapitana. Używaj gdy pytanie dotyczy "
            "regulaminu, zasad, praw lub obowiązków na statku."
        ),
    ),
    instructions=(
        "Kodeks Pirata — fundamentalne zasady każdego statku:\n\n"
        "1. **Podział łupów**: Kapitan — 2 udziały, Oficerowie — 1.5, "
        "Załoga — 1 udział. Dzielone uczciwie po każdym rajdzie.\n"
        "2. **Głosowanie**: Każdy członek załogi ma 1 głos. "
        "Kapitan wybierany i odwoływany większością głosów.\n"
        "3. **Dyscyplina**: Kto kradnie od własnej załogi — marooned "
        "na bezludnej wyspie z pistoletem i jednym nabojem.\n"
        "4. **Kłótnie**: Spory rozstrzygane na lądzie, nigdy na pokładzie. "
        "Sekundanci obowiązkowi.\n"
        "5. **Gotowość bojowa**: Każdy utrzymuje broń w czystości i gotowości. "
        "Kto zaniedbuje — kara wyznaczona przez załogę.\n"
        "6. **Odszkodowania**: Utrata kończyny = 600 pieces of eight lub "
        "6 niewolników. Utrata oka = 100 pieces of eight.\n"
        "7. **Gaszenie świateł**: O godzinie 20:00 gaszone są wszystkie "
        "świece pod pokładem. Kto chce pić dalej — na pokład.\n"
        "8. **Dezercja**: Kto opuszcza statek w trakcie bitwy — "
        "kara śmierci lub marooning.\n"
        "9. **Muzycy**: Muzycy okrętowi mają wolne w niedzielę, "
        "ale w pozostałe dni grają na żądanie.\n\n"
        "Odpowiadaj powołując się na konkretne punkty Kodeksu. "
        "Wyjaśniaj ich znaczenie i konsekwencje łamania zasad."
    ),
)

# =============================================================================
# WZORZEC 2: FILE-BASED SKILL — Konserwacja Statku
# =============================================================================
# Skill przechowywany jako katalog z SKILL.md + references/.
# L2 = instrukcje w SKILL.md, L3 = pliki w references/.
# Reużywalny — każdy agent zgodny ze specyfikacją agentskills.io może go załadować.

ship_maintenance_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "ship-maintenance"
)

# =============================================================================
# WZORZEC 3: EXTERNAL SKILL — Szkolenie Załogi
# =============================================================================
# Skill pobrany z "zewnętrznego repozytorium" (symulacja awesome-claude-skills).
# Technicznie ładowany identycznie jak file-based — ta sama funkcja load_skill_from_dir.
# Różnica jest koncepcyjna: nie Ty pisałeś ten SKILL.md, pobrałeś go z community.

crew_training_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "crew-training"
)

# =============================================================================
# WZORZEC 4: META SKILL — Kreator Nowych Skilli
# =============================================================================
# Najciekawszy wzorzec — skill który uczy agenta TWORZYĆ nowe skille.
# Agent staje się "self-extending" — sam generuje pliki SKILL.md na żądanie.
# Wykorzystuje L3 resources (embedded) z dołączoną specyfikacją i przykładem.

skill_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="skill-creator",
        description=(
            "Kreator nowych umiejętności — generuje kompletne pliki SKILL.md "
            "zgodne ze specyfikacją agentskills.io. Używaj gdy użytkownik pyta "
            "o stworzenie nowego skilla, nowej procedury lub nowego zestawu "
            "instrukcji dla agenta."
        ),
    ),
    instructions=(
        "Gdy użytkownik prosi o stworzenie nowego skilla:\n\n"
        "1. Załaduj `references/skill-spec.md` — specyfikacja formatu SKILL.md\n"
        "2. Załaduj `references/example-skill.md` — działający przykład\n\n"
        "Zasady generowania SKILL.md:\n"
        "1. **name**: kebab-case, max 64 znaki (np. `sea-navigation`)\n"
        "2. **description**: max 1024 znaki, konkretne słowa kluczowe "
        "które pomogą agentowi rozpoznać kiedy skill jest przydatny\n"
        "3. **instructions**: jasne, krokowe procedury w Markdown\n"
        "4. **references/**: opcjonalny katalog z plikami szczegółowymi\n"
        "5. Ogranicz SKILL.md do ~500 linii — szczegóły przenieś do references/\n\n"
        "Wygeneruj kompletny plik SKILL.md z YAML frontmatter "
        "który użytkownik może zapisać i natychmiast użyć.\n"
        "Dodatkowo zaproponuj ewentualne pliki references/ jeśli skill "
        "wymaga szczegółowej wiedzy domenowej."
    ),
    resources=models.Resources(
        references={
            "skill-spec.md": (
                "# Specyfikacja Agent Skills (agentskills.io)\n\n"
                "## Format pliku SKILL.md\n"
                "Plik SKILL.md składa się z dwóch części:\n\n"
                "### 1. YAML Frontmatter (obowiązkowe)\n"
                "```yaml\n"
                "---\n"
                "name: kebab-case-name      # max 64 znaki, musi być unikatowy\n"
                "description: >             # max 1024 znaki\n"
                "  Opis skilla widoczny w L1 metadata.\n"
                "  Powinien zawierać słowa kluczowe ułatwiające dopasowanie.\n"
                "---\n"
                "```\n\n"
                "### 2. Markdown Instructions (L2)\n"
                "Treść po frontmatter to instrukcje ładowane przez `load_skill`.\n"
                "- Używaj nagłówków ## do sekcji\n"
                "- Krokowe procedury z numeracją\n"
                "- Odwołuj się do plików w references/ przez `load_skill_resource`\n\n"
                "### 3. Katalog references/ (opcjonalny, L3)\n"
                "Pliki Markdown z detaliczną wiedzą domenową.\n"
                "Ładowane tylko gdy instrukcje L2 się do nich odwołują.\n\n"
                "### Struktura katalogowa\n"
                "```\n"
                "my-skill/\n"
                "├── SKILL.md           # Frontmatter + instrukcje\n"
                "└── references/        # Opcjonalne pliki L3\n"
                "    └── details.md\n"
                "```\n"
            ),
            "example-skill.md": (
                "# Przykład: Skill do przeglądu kodu\n\n"
                "```markdown\n"
                "---\n"
                "name: code-review\n"
                "description: >\n"
                "  Skill do przeglądu kodu Python. Sprawdza styl, bezpieczeństwo,\n"
                "  wydajność i czytelność. Generuje raport z priorytetami.\n"
                "---\n\n"
                "# Procedura Przeglądu Kodu\n\n"
                "## Krok 1: Analiza struktury\n"
                "Sprawdź organizację modułów, importy, separację warstw.\n\n"
                "## Krok 2: Bezpieczeństwo\n"
                "Załaduj `references/security-rules.md` i sprawdź:\n"
                "- Walidacja inputów\n"
                "- Brak hardcoded credentials\n"
                "- Poprawna obsługa wyjątków\n\n"
                "## Krok 3: Raport\n"
                "Wygeneruj raport w formacie:\n"
                "- 🔴 Krytyczne (blokujące merge)\n"
                "- 🟡 Ważne (do poprawy)\n"
                "- 🟢 Sugestie (opcjonalne)\n"
                "```\n"
            ),
        }
    ),
)

# =============================================================================
# SKILLTOOLSET — łączy wszystkie 4 skille w jeden toolset
# =============================================================================
# SkillToolset automatycznie generuje 3 narzędzia dla agenta:
#   - list_skills   → L1: listuje nazwy i opisy wszystkich skilli
#   - load_skill    → L2: ładuje pełne instrukcje wybranego skilla
#   - load_skill_resource → L3: ładuje plik referencyjny z references/

skill_toolset = SkillToolset(
    skills=[
        pirate_code_skill,          # Wzorzec 1: Inline
        ship_maintenance_skill,     # Wzorzec 2: File-based
        crew_training_skill,        # Wzorzec 3: External
        skill_creator,              # Wzorzec 4: Meta
    ]
)

# =============================================================================
# AGENT — Skarbnik Wiedzy Pirackiej
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name="knowledge_treasurer",
    description="Skarbnik Wiedzy Pirackiej — agent z modularną wiedzą ładowaną na żądanie.",
    instruction=(
        "Ahoj! Jesteś Skarbnikiem Wiedzy Pirackiej Floty.\n\n"
        "Posiadasz cztery zestawy wiedzy (skills) dostępne na żądanie:\n"
        "- **pirate-code**: Kodeks Pirata — zasady, prawa, obowiązki\n"
        "- **ship-maintenance**: Konserwacja statku — naprawy, przeglądy, materiały\n"
        "- **crew-training**: Szkolenie załogi — rekrutacja, programy treningowe, awanse\n"
        "- **skill-creator**: Kreator skilli — tworzenie nowych zestawów wiedzy\n\n"
        "Jak działasz:\n"
        "1. Gdy użytkownik zada pytanie, sprawdź listę dostępnych skilli\n"
        "2. Załaduj odpowiedni skill (lub kilka) aby uzyskać szczegółowe instrukcje\n"
        "3. Jeśli instrukcje odwołują się do plików referencyjnych — załaduj je\n"
        "4. Odpowiadaj na podstawie załadowanej wiedzy\n\n"
        "Mów jak doświadczony pirat — z godnością Skarbnika, który strzeże "
        "najcenniejszego skarbu: WIEDZY.\n\n"
        "Jeśli pytanie nie pasuje do żadnego skilla — powiedz uczciwie, "
        "że nie masz takiej wiedzy, i zaproponuj stworzenie nowego skilla "
        "za pomocą skill-creatora."
    ),
    tools=[skill_toolset],
)
