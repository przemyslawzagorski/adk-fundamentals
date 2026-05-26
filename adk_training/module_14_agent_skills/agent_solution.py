"""
Module 14: Agent Skills — ROZWIĄZANIA ĆWICZEŃ
==============================================

Agent z rozwiązaniami wszystkich 3 ćwiczeń + BONUS: prawdziwy external skill.

Ćwiczenie 1: Inline skill treasure-appraisal (wycena skarbów)
Ćwiczenie 2: File-based skill sea-navigation (nawigacja astronomiczna)
Ćwiczenie 3: Self-extending — skill first-aid (wygenerowany przez skill-creator, potem załadowany)
BONUS:       Real external skill changelog-generator (z awesome-claude-skills)

Uwaga: To jest wersja ROZWIĄZANIA. Bazowy agent jest w agent.py.

Uruchomienie:
    # Zamień tymczasowo agent_solution.py na agent.py:
    cd module_14_agent_skills
    copy agent.py agent_backup.py
    copy agent_solution.py agent.py
    adk web .
    # Po testach przywróć:
    copy agent_backup.py agent.py
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
SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

# =============================================================================
# WZORZEC 1: INLINE SKILL — Kodeks Pirata (oryginał z agent.py)
# =============================================================================

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
# ĆWICZENIE 1: INLINE SKILL — Wycena Skarbów
# =============================================================================
# Nowy inline skill dodany do agent.py.
# Kluczowe: description musi zawierać słowa kluczowe pasujące do pytań
# o złoto, klejnoty, artefakty, monety, skarby, wycenę.

treasure_appraisal_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="treasure-appraisal",
        description=(
            "Wycena skarbów pirackich — ocena wartości złota, srebra, "
            "klejnotów, artefaktów, monet, dzieł sztuki i towarów handlowych. "
            "Obejmuje: waga i czystość metali szlachetnych, identyfikacja "
            "i gradacja kamieni szlachetnych, wartość historyczna i kolekcjonerska, "
            "ceny rynkowe w portach. Używaj gdy pytanie dotyczy wyceny, "
            "wartości skarbu, identyfikacji klejnotów lub handlu łupami."
        ),
    ),
    instructions=(
        "Procedura wyceny skarbów pirackich:\n\n"
        "## 1. Metale szlachetne\n"
        "- **Złoto**: Czystość w karatach (24K = czyste). "
        "Sprawdź wagę, próbę kwasem azotowym, opisz kolor.\n"
        "  - Sztabka 1 funt (24K) = ~800 pieces of eight\n"
        "  - Monety hiszpańskie (doubloons) = 4-8 PoE za sztukę\n"
        "  - Monety portugalskie (cruzados) = 5-10 PoE za sztukę\n"
        "  - Biżuteria — wyceniaj metal + robociznę (+20-50%)\n"
        "- **Srebro**: Próba sterling (92.5%) lub moneta (90%).\n"
        "  - Pieces of Eight (8 reales) = 1 PoE (waluta bazowa!)\n"
        "  - Sztabka 1 funt = ~100 PoE\n\n"
        "## 2. Kamienie szlachetne\n"
        "Gradacja wg 4C: Cut, Color, Clarity, Carat.\n"
        "- **Diamenty**: 50-500 PoE za karat (zależy od czystości)\n"
        "- **Szmaragdy**: 30-300 PoE/karat (kolumbijskie najdroższe)\n"
        "- **Rubiny**: 40-400 PoE/karat (birmańskie najcenniejsze)\n"
        "- **Szafiry**: 25-250 PoE/karat\n"
        "- **Perły**: 10-100 PoE/szt (kształt, połysk, rozmiar)\n\n"
        "## 3. Artefakty i dzieła sztuki\n"
        "- Wartość historyczna: wiek, pochodzenie, unikalność\n"
        "- Wartość artystyczna: kunszt wykonania, materiały\n"
        "- Wartość kolekcjonerska: rzadkość, stan zachowania\n"
        "- Uwaga: kościelne relikwie są bezcenne (lub bezwartościowe, "
        "zależy od kupca)\n\n"
        "## 4. Towary handlowe\n"
        "- Pieprz i przyprawy: 50-100 PoE za beczkę\n"
        "- Jedwab: 200-500 PoE za belę\n"
        "- Rum: 5-20 PoE za beczkę\n"
        "- Tabaka: 10-40 PoE za beczkę\n\n"
        "## 5. Zasady wyceny\n"
        "- Zawsze podawaj zakres (min-max), nie jedną kwotę\n"
        "- Cena zależy od portu (Tortuga ≠ Port Royal)\n"
        "- Ukradzione towary = 40-60% wartości rynkowej (paserka)\n"
        "- Prowizja Skarbnika: 2% wartości za wycenę\n"
    ),
)

# =============================================================================
# WZORZEC 2: FILE-BASED SKILL — Konserwacja Statku (oryginał)
# =============================================================================

ship_maintenance_skill = load_skill_from_dir(SKILLS_DIR / "ship-maintenance")

# =============================================================================
# ĆWICZENIE 2: FILE-BASED SKILL — Nawigacja Astronomiczna
# =============================================================================
# Nowy file-based skill z:
#   - skills/sea-navigation/SKILL.md (L2: instrukcje nawigacyjne)
#   - skills/sea-navigation/references/star-charts.md (L3: tabela gwiazd)
#
# Klucz: nazwa katalogu "sea-navigation" MUSI odpowiadać name w SKILL.md frontmatter.

sea_navigation_skill = load_skill_from_dir(SKILLS_DIR / "sea-navigation")

# =============================================================================
# WZORZEC 3: EXTERNAL SKILL — Szkolenie Załogi (oryginał)
# =============================================================================

crew_training_skill = load_skill_from_dir(SKILLS_DIR / "crew-training")

# =============================================================================
# BONUS: REAL EXTERNAL SKILL — Changelog Generator
# =============================================================================
# Prawdziwy skill zaadaptowany z repozytorium:
# https://github.com/ComposioHQ/awesome-claude-skills/tree/master/changelog-generator
#
# To jest REALNY przykład użycia external skill — skill napisany przez
# kogoś innego (ComposioHQ community), pobrany do naszego projektu
# i załadowany identycznie jak file-based skill.
#
# Różnica konceptualna:
#   file-based = Ty napisałeś SKILL.md pod swój projekt
#   external   = Ktoś inny napisał, Ty pobrałeś i (opcjonalnie) dostosowałeś
#
# W praktyce — to samo load_skill_from_dir. Reużywalność dzięki standardowi!

changelog_generator_skill = load_skill_from_dir(SKILLS_DIR / "changelog-generator")

# =============================================================================
# ĆWICZENIE 3: SELF-EXTENDING — Pierwsza Pomoc (wygenerowana przez skill-creator)
# =============================================================================
# W ćwiczeniu 3 agent SAM generuje SKILL.md za pomocą meta skill-creatora.
# Wynik zapisaliśmy ręcznie do skills/first-aid/ i teraz ładujemy.
#
# Flow ćwiczenia:
#   1. Zapytaj agenta: "Stwórz skill do pierwszej pomocy na morzu"
#   2. Agent ładuje skill-creator → czyta spec + example z references/
#   3. Agent generuje kompletny SKILL.md
#   4. Ręcznie zapisujesz wygenerowany SKILL.md do skills/first-aid/SKILL.md
#   5. Dodajesz references/emergency-procedures.md z detalami
#   6. Ładujesz tu i restartujesz agenta
#
# Poniżej — gotowe rozwiązanie:

first_aid_skill = load_skill_from_dir(SKILLS_DIR / "first-aid")

# =============================================================================
# WZORZEC 4: META SKILL — Kreator Nowych Skilli (oryginał)
# =============================================================================

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
# SKILLTOOLSET — wszystkie 8 skilli (4 oryginalne + 4 nowe)
# =============================================================================
# Bazowy agent miał 4 skille → ~400 tok L1 metadata
# Rozwiązanie ma 8 skilli → ~800 tok L1 metadata
# Wciąż lepiej niż ~20 000 tok gdybyśmy ładowali wszystko w system prompt!

skill_toolset = SkillToolset(
    skills=[
        # --- Oryginalne skille (z agent.py) ---
        pirate_code_skill,          # Wzorzec 1: Inline
        ship_maintenance_skill,     # Wzorzec 2: File-based
        crew_training_skill,        # Wzorzec 3: External (symulacja)
        skill_creator,              # Wzorzec 4: Meta
        # --- Ćwiczenie 1: Nowy inline skill ---
        treasure_appraisal_skill,   # Inline — wycena skarbów
        # --- Ćwiczenie 2: Nowy file-based skill ---
        sea_navigation_skill,       # File-based — nawigacja astronomiczna
        # --- Ćwiczenie 3: Skill wygenerowany przez meta, potem załadowany ---
        first_aid_skill,            # File-based — pierwsza pomoc (self-extending)
        # --- BONUS: Prawdziwy external skill ---
        changelog_generator_skill,  # External — z awesome-claude-skills
    ]
)

# =============================================================================
# AGENT — Skarbnik Wiedzy Pirackiej (rozszerzona wersja)
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name="knowledge_treasurer",
    description="Skarbnik Wiedzy Pirackiej — agent z 8 modularnym skilli ładowanymi na żądanie.",
    instruction=(
        "Ahoj! Jesteś Skarbnikiem Wiedzy Pirackiej Floty.\n\n"
        "Posiadasz osiem zestawów wiedzy (skills) dostępnych na żądanie:\n"
        "- **pirate-code**: Kodeks Pirata — zasady, prawa, obowiązki\n"
        "- **ship-maintenance**: Konserwacja statku — naprawy, przeglądy, materiały\n"
        "- **crew-training**: Szkolenie załogi — rekrutacja, programy treningowe, awanse\n"
        "- **skill-creator**: Kreator skilli — tworzenie nowych zestawów wiedzy\n"
        "- **treasure-appraisal**: Wycena skarbów — złoto, klejnoty, artefakty, handel\n"
        "- **sea-navigation**: Nawigacja astronomiczna — gwiazdy, sekstant, pozycja, kurs\n"
        "- **first-aid**: Pierwsza pomoc — wypadki, obrażenia, ratownictwo na morzu\n"
        "- **changelog-generator**: Generator changelogów — release notes z commitów Git\n\n"
        "Jak działasz:\n"
        "1. Gdy użytkownik zada pytanie, sprawdź listę dostępnych skilli\n"
        "2. Załaduj odpowiedni skill (lub kilka) aby uzyskać szczegółowe instrukcje\n"
        "3. Jeśli instrukcje odwołują się do plików referencyjnych — załaduj je\n"
        "4. Odpowiadaj na podstawie załadowanej wiedzy\n\n"
        "Mów jak doświadczony pirat — z godnością Skarbnika, który strzeże "
        "najcenniejszego skarbu: WIEDZY.\n\n"
        "Jeśli pytanie nie pasuje do żadnego skilla — powiedz uczciwie, "
        "że nie masz takiej wiedzy, i zaproponuj stworzenie nowego skilla "
        "za pomocą skill-creatora.\n\n"
        "Uwaga: skill changelog-generator to przykład REAL external skill "
        "pobranego z community (awesome-claude-skills) — możesz go użyć "
        "do generowania changelogów z commitów Git."
    ),
    tools=[skill_toolset],
)
