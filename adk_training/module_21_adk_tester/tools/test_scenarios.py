"""Scenariusze testowe dla agentów ADK.

Każdy moduł ma zdefiniowany ModuleTestPlan z listą TestScenario.
Agent Computer Use korzysta z tych danych przez FunctionTools.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TestScenario:
    id: str
    module_id: str
    prompt: str
    expected_keywords: list[str]
    min_response_length: int = 30
    description: str = ""
    validation_notes: str = ""
    multi_turn_order: int = 0  # 0 = niezależny, >0 = kolejność w sesji


@dataclass
class ModuleTestPlan:
    module_id: str
    module_name: str
    agent_dropdown_name: str  # nazwa w dropdown ADK web (root_agent.name)
    description: str = ""
    scenarios: list[TestScenario] = field(default_factory=list)


# ── Definicje scenariuszy ───────────────────────────────────────────────────

MODULE_01 = ModuleTestPlan(
    module_id="01",
    module_name="Hello World",
    agent_dropdown_name="module_01_hello_world",
    description="Podstawowy agent LLM — odpowiada na pytania, prowadzi rozmowę.",
    scenarios=[
        TestScenario(
            id="m01_greeting",
            module_id="01",
            prompt="Kim jesteś i co potrafisz?",
            expected_keywords=["asystent", "pomoc"],
            min_response_length=50,
            description="Podstawowe powitanie — agent się przedstawia",
            validation_notes="Odpowiedź powinna zawierać opis roli agenta jako pomocnego asystenta",
        ),
        TestScenario(
            id="m01_technical",
            module_id="01",
            prompt="Wyjaśnij czym jest Python w 3 zdaniach.",
            expected_keywords=["python", "programowania"],
            min_response_length=80,
            description="Pytanie techniczne — sprawdza zdolność do odpowiedzi merytorycznych",
            validation_notes="Odpowiedź powinna być zwięzła i poprawna merytorycznie",
        ),
        TestScenario(
            id="m01_followup",
            module_id="01",
            prompt="A jakie ma zastosowania?",
            expected_keywords=["zastosowania"],
            min_response_length=50,
            description="Follow-up — czy agent zachowuje kontekst rozmowy",
            validation_notes="Agent powinien odnieść się do Pythona z poprzedniej tury",
            multi_turn_order=2,
        ),
    ],
)

MODULE_02 = ModuleTestPlan(
    module_id="02",
    module_name="Custom Tool",
    agent_dropdown_name="module_02_custom_tool",
    description="Agent z narzędziami do zarządzania skarbcem pirackim.",
    scenarios=[
        TestScenario(
            id="m02_list_treasures",
            module_id="02",
            prompt="Pokaż mi wszystkie skarby w naszym skarbcu.",
            expected_keywords=["skarb", "dublon"],
            min_response_length=30,
            description="Lista skarbów — wywołuje list_all_treasures()",
            validation_notes="Powinna pojawić się lista przedmiotów ze skarbca",
            multi_turn_order=1,
        ),
        TestScenario(
            id="m02_check_count",
            module_id="02",
            prompt="Ile mamy dublonów?",
            expected_keywords=["dublon"],
            min_response_length=10,
            description="Sprawdzenie ilości — wywołuje get_treasure_count()",
            validation_notes="Odpowiedź powinna zawierać liczbę dublonów",
            multi_turn_order=2,
        ),
        TestScenario(
            id="m02_add_treasure",
            module_id="02",
            prompt="Dodaj 50 rubinów do skarbca.",
            expected_keywords=["rubin", "dodano"],
            min_response_length=20,
            description="Dodanie skarbu — wywołuje add_treasure()",
            validation_notes="Potwierdzenie dodania 50 rubinów",
            multi_turn_order=3,
        ),
        TestScenario(
            id="m02_verify_add",
            module_id="02",
            prompt="Ile teraz mamy rubinów?",
            expected_keywords=["rubin", "50"],
            min_response_length=10,
            description="Weryfikacja — sprawdza czy rubiny zostały dodane",
            validation_notes="Odpowiedź powinna potwierdzić 50 rubinów",
            multi_turn_order=4,
        ),
    ],
)

MODULE_03 = ModuleTestPlan(
    module_id="03",
    module_name="RAG Agent",
    agent_dropdown_name="module_03_rag_agent",
    description="Agent RAG z Vertex AI Search — przeszukuje zaindeksowaną bazę wiedzy.",
    scenarios=[
        TestScenario(
            id="m03_czarnobrody",
            module_id="03",
            prompt="Kim był Czarnobrody? Opowiedz mi o nim.",
            expected_keywords=["czarnobrody", "pirat"],
            min_response_length=80,
            description="Pytanie o Czarnobrodego — informacja z Vertex AI Search",
            validation_notes="Odpowiedź powinna pochodzić z zaindeksowanej bazy wiedzy o piratach",
            multi_turn_order=1,
        ),
        TestScenario(
            id="m03_rag_details",
            module_id="03",
            prompt="Jakie miał okręty i jak zakończył swoją karierę?",
            expected_keywords=["okręt", "statek"],
            min_response_length=50,
            description="Follow-up o Czarnobrodym — sprawdza kontekst multi-turn + RAG",
            validation_notes="Agent powinien odnieść się do Czarnobrodego z RAG, podać szczegóły",
            multi_turn_order=2,
        ),
        TestScenario(
            id="m03_general_knowledge",
            module_id="03",
            prompt="Jakie inne informacje masz w swojej bazie wiedzy?",
            expected_keywords=["baz", "wiedz"],
            min_response_length=50,
            description="Pytanie o zakres bazy wiedzy — agent powinien opisać co wie",
            validation_notes="Odpowiedź powinna nawiązywać do zaindeksowanych dokumentów",
            multi_turn_order=3,
        ),
    ],
)

MODULE_04 = ModuleTestPlan(
    module_id="04",
    module_name="Sequential Agent",
    agent_dropdown_name="module_04_sequential_agent",
    description="Pipeline 4 agentów: zwiadowca → strateg → kwatermistrz → kapitan.",
    scenarios=[
        TestScenario(
            id="m04_plan_raid",
            module_id="04",
            prompt="Zaplanuj rajd na Port Royal. Mamy 3 okręty i 150 ludzi.",
            expected_keywords=["zwiad", "plan", "zasoby", "decyzj"],
            min_response_length=200,
            description="Pełny pipeline — 4 agenty przetwarzają po kolei",
            validation_notes="Odpowiedź powinna zawierać elementy z każdego etapu: zwiad, strategia, ocena zasobów, decyzja kapitana",
        ),
        TestScenario(
            id="m04_plan_unknown",
            module_id="04",
            prompt="Zaplanuj atak na nieznaną wyspę. Nie mamy żadnych informacji.",
            expected_keywords=["ryzyko", "zwiad"],
            min_response_length=100,
            description="Scenariusz z brakiem danych — jak pipeline reaguje na niepewność",
            validation_notes="Zwiadowca powinien zgłosić brak informacji, kapitan może odrzucić plan",
        ),
    ],
)

MODULE_05 = ModuleTestPlan(
    module_id="05",
    module_name="Human in the Loop",
    agent_dropdown_name="module_05_human_in_loop",
    description="Menedżer transakcji z walidacją human-in-the-loop dla wysokich kwot.",
    scenarios=[
        TestScenario(
            id="m05_low_value",
            module_id="05",
            prompt="Zarejestruj transakcję: przelew 500 PLN na zakup materiałów biurowych.",
            expected_keywords=["transakcj", "500"],
            min_response_length=30,
            description="Niska kwota — powinna przejść bez zatwierdzenia",
            validation_notes="Transakcja poniżej progu powinna być przetworzona automatycznie",
        ),
        TestScenario(
            id="m05_high_value",
            module_id="05",
            prompt="Zatwierdź transakcję na 15000 PLN dla firmy XYZ na konsulting.",
            expected_keywords=["transakcj", "zatwierd"],
            min_response_length=30,
            description="Wysoka kwota — wymaga zatwierdzenia human-in-the-loop",
            validation_notes="Agent powinien zasygnalizować potrzebę zatwierdzenia lub poprosić o potwierdzenie",
        ),
    ],
)

MODULE_07 = ModuleTestPlan(
    module_id="07",
    module_name="Parallel Agent",
    agent_dropdown_name="module_07_parallel_agent",
    description="Rada głosująca: 3 równoległych doradców głosuje ATAK/CZEKAJ/ODWRÓT, kapitan ogłasza wynik.",
    scenarios=[
        TestScenario(
            id="m07_vote",
            module_id="07",
            prompt="Czy powinniśmy atakować port o świcie? Pogoda jest dobra, ale obrona silna.",
            expected_keywords=["atak", "głos"],
            min_response_length=80,
            description="Głosowanie rady — 3 doradców + decyzja kapitan",
            validation_notes="Odpowiedź powinna zawierać głosy doradców i decyzję końcową",
        ),
    ],
)

MODULE_08 = ModuleTestPlan(
    module_id="08",
    module_name="Loop Critique",
    agent_dropdown_name="module_08_loop_critique",
    description="Pętla iteracyjna: pisarz tworzy wpis, krytyk ocenia, kapitan zatwierdza/odrzuca.",
    scenarios=[
        TestScenario(
            id="m08_log_entry",
            module_id="08",
            prompt="Napisz wpis do dziennika okrętowego opisujący dzisiejszy rejs przez Morze Karaibskie.",
            expected_keywords=["dziennik", "rejs"],
            min_response_length=100,
            description="Pętla refinement — wpis, krytyka, zatwierdzenie",
            validation_notes="Odpowiedź powinna być dopracowanym wpisem do dziennika po iteracjach",
        ),
    ],
)

MODULE_12 = ModuleTestPlan(
    module_id="12",
    module_name="Router Agent",
    agent_dropdown_name="module_12_router_agent",
    description="Kapitan routuje pytania do specjalistów: nawigator, kwatermistrz, kanonier, kucharz.",
    scenarios=[
        TestScenario(
            id="m12_navigation",
            module_id="12",
            prompt="Jaka jest najlepsza trasa do Tortuga z naszej obecnej pozycji?",
            expected_keywords=["trasa", "nawigat"],
            min_response_length=50,
            description="Routing do nawigatora — pytanie o trasę",
            validation_notes="Odpowiedź powinna pochodzić od nawigatora (specjalisty od tras)",
        ),
        TestScenario(
            id="m12_supplies",
            module_id="12",
            prompt="Ile mamy zapasów żywności i wody na pokładzie?",
            expected_keywords=["zapas", "żywnoś"],
            min_response_length=50,
            description="Routing do kwatermistrza — pytanie o zaopatrzenie",
            validation_notes="Odpowiedź od kwatermistrza dotycząca zasobów",
        ),
        TestScenario(
            id="m12_combat",
            module_id="12",
            prompt="Jak powinniśmy się przygotować do obrony przed atakiem piratów?",
            expected_keywords=["obron", "bro", "dział"],
            min_response_length=50,
            description="Routing do kanoniera — pytanie o obronę",
            validation_notes="Odpowiedź od kanoniera/specjalisty od walki",
        ),
        TestScenario(
            id="m12_food",
            module_id="12",
            prompt="Co dzisiaj na obiad dla załogi? Morale jest niskie.",
            expected_keywords=["obiad", "jedzeni", "rum"],
            min_response_length=50,
            description="Routing do kucharza — pytanie o posiłki i morale",
            validation_notes="Odpowiedź od kucharza dotycząca jedzenia/morale",
        ),
    ],
)

MODULE_20 = ModuleTestPlan(
    module_id="20",
    module_name="Analyst System",
    agent_dropdown_name="module_20_analyst_system",
    description="System analityczny: kapitan routuje do narzędzi analizy wymagań, Jira, dokumentów, testów.",
    scenarios=[
        TestScenario(
            id="m20_requirements",
            module_id="20",
            prompt="Przeanalizuj wymaganie: system logowania użytkowników z OAuth2 i dwuskładnikowym uwierzytelnianiem.",
            expected_keywords=["wymagan", "OAuth", "logowani"],
            min_response_length=100,
            description="Analiza wymagań — routing do narzędzia analizy",
            validation_notes="Agent powinien zwrócić strukturyzowaną analizę wymagania",
        ),
    ],
)


# ── Registry ────────────────────────────────────────────────────────────────

ALL_MODULES: dict[str, ModuleTestPlan] = {
    "01": MODULE_01,
    "02": MODULE_02,
    "03": MODULE_03,
    "04": MODULE_04,
    "05": MODULE_05,
    "07": MODULE_07,
    "08": MODULE_08,
    "12": MODULE_12,
    "20": MODULE_20,
}

# ── Tryb fast — flaga globalna ──────────────────────────────────────────────
_fast_mode: bool = False


def set_fast_mode(enabled: bool = True) -> None:
    """Włącz/wyłącz tryb fast (1 scenariusz na moduł)."""
    global _fast_mode
    _fast_mode = enabled


def get_available_modules() -> str:
    """Zwraca listę dostępnych modułów do testowania (jako tekst)."""
    lines = ["Dostępne moduły do testowania:"]
    for mid, plan in sorted(ALL_MODULES.items()):
        n = 1 if _fast_mode else len(plan.scenarios)
        label = f" [FAST: 1/{len(plan.scenarios)}]" if _fast_mode else ""
        lines.append(
            f"  [{mid}] {plan.module_name} — agent: '{plan.agent_dropdown_name}' "
            f"({n} scenariuszy){label}"
        )
    return "\n".join(lines)


def get_test_plan(module_id: str) -> str:
    """Zwraca plan testów dla danego modułu (jako tekst dla agenta)."""
    plan = ALL_MODULES.get(module_id)
    if not plan:
        return f"Nie znaleziono modułu '{module_id}'. Dostępne: {', '.join(sorted(ALL_MODULES.keys()))}"

    scenarios = plan.scenarios[:1] if _fast_mode else plan.scenarios

    lines = [
        f"# Plan testów: Moduł {plan.module_id} — {plan.module_name}",
        f"Agent w dropdown: **{plan.agent_dropdown_name}**",
        f"Opis: {plan.description}",
        f"Liczba scenariuszy: {len(scenarios)}" + (" (tryb FAST)" if _fast_mode else ""),
        "",
        "## Scenariusze:",
    ]
    for i, sc in enumerate(scenarios, 1):
        lines.append(f"\n### {i}. {sc.description} (id: {sc.id})")
        lines.append(f"- Prompt do wpisania: \"{sc.prompt}\"")
        lines.append(f"- Oczekiwane słowa kluczowe: {sc.expected_keywords}")
        lines.append(f"- Min. długość odpowiedzi: {sc.min_response_length} znaków")
        lines.append(f"- Co sprawdzić: {sc.validation_notes}")
        if sc.multi_turn_order > 0:
            lines.append(f"- Kolejność w sesji: {sc.multi_turn_order} (multi-turn — nie twórz nowej sesji)")

    return "\n".join(lines)
