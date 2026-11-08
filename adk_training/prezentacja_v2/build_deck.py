"""Build the reworked training deck from source.pptx.

Usage: python build_deck.py <source.pptx> <output.pptx>
Keeps original (image) slides, drops outdated ones, adds native slides
(agenda, lab setup, ADK 2 code, Workflow API, costs, exercises, summaries)
and reorders everything into theory -> practice blocks.
"""
import re
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

SRC, OUT = sys.argv[1], sys.argv[2]

BG = RGBColor(0xF5, 0xF7, 0xFB)
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
BLUE = RGBColor(0x1A, 0x73, 0xE8)
TEAL = RGBColor(0x0F, 0x9D, 0x8A)
ORANGE = RGBColor(0xF2, 0x8C, 0x28)
PURPLE = RGBColor(0x7E, 0x57, 0xC2)
GREEN = RGBColor(0x34, 0xA8, 0x53)
RED = RGBColor(0xD9, 0x30, 0x25)
GREY = RGBColor(0x5F, 0x6B, 0x7A)
LIGHT = RGBColor(0xE8, 0xEE, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CODE_BG = RGBColor(0x1E, 0x24, 0x33)
FONT = "Segoe UI"
MONO = "Consolas"

prs = Presentation(SRC)
BLANK = prs.slide_layouts[0]
N_SRC = len(prs.slides)


# ----------------------------------------------------------------------------- helpers
def _font(run, size, color=NAVY, bold=False, mono=False, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = MONO if mono else FONT


def rich(par, text, size, color=NAVY, mono=False):
    """Append text to a paragraph; **bold** and `code` segments are styled."""
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        r = par.add_run()
        if part.startswith("**"):
            r.text = part[2:-2]
            _font(r, size, color, bold=True, mono=mono)
        elif part.startswith("`"):
            r.text = part[1:-1]
            _font(r, size - 1, RGBColor(0x0B, 0x50, 0xA8), mono=True)
        else:
            r.text = part
            _font(r, size, color, mono=mono)


def textbox(slide, x, y, w, h, lines, size=16, color=NAVY, bullet=None, align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.TOP, spacing=4, numbered=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    if isinstance(lines, str):
        lines = [lines]
    num = 0
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(spacing)
        sub = line.startswith("  ")
        if numbered and not sub:
            num += 1
        prefix = f"{num}. " if numbered else (f"{bullet} " if bullet else "")
        if sub:
            prefix = "– "
        if prefix:
            r = p.add_run()
            r.text = ("    " if sub else "") + prefix
            _font(r, size - (2 if sub else 0), ORANGE if numbered else BLUE, bold=True)
        rich(p, line.strip(), size - (2 if sub else 0), color)
    return tb


def rect(slide, x, y, w, h, fill, line=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s


def label(slide, x, y, w, h, text, fill, color=WHITE, size=12, bold=True, mono=False,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    s = rect(slide, x, y, w, h, fill, shape=shape, radius=0.5)
    tf = s.text_frame
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = Inches(0.0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    _font(r, size, color, bold=bold, mono=mono)
    return s


def card(slide, x, y, w, h, header, lines, color=BLUE, size=14, numbered=False, bullet="•"):
    rect(slide, x, y, w, h, WHITE, line=RGBColor(0xD5, 0xDD, 0xEA), radius=0.03)
    rect(slide, x, y + 0.12, 0.07, h - 0.24, color, shape=MSO_SHAPE.RECTANGLE)
    textbox(slide, x + 0.22, y + 0.1, w - 0.35, 0.4, header, size=size + 1, color=color)
    slide.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
    textbox(slide, x + 0.22, y + 0.52, w - 0.35, h - 0.6, lines, size=size,
            bullet=None if numbered else bullet, numbered=numbered, spacing=3)


KW = r"\b(?:from|import|def|return|yield|async|await|class|for|in|if|else|None|True|False)\b"


def code(slide, x, y, w, h, src, size=12, title=None):
    rect(slide, x, y, w, h, CODE_BG, radius=0.04)
    top = y + 0.12
    if title:
        textbox(slide, x + 0.2, y + 0.08, w - 0.4, 0.35, title, size=11,
                color=RGBColor(0x9A, 0xA7, 0xBD))
        top = y + 0.42
    tb = slide.shapes.add_textbox(Inches(x + 0.2), Inches(top), Inches(w - 0.4), Inches(h - (top - y) - 0.1))
    tf = tb.text_frame
    tf.word_wrap = False
    for i, line in enumerate(src.strip("\n").split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(0)
        p.line_spacing = 1.05
        code_part, _, comment = line.partition("#") if not re.search(r"[\"'][^\"']*#", line) else (line, "", "")
        for tok in re.split(r"(\"[^\"]*\"|'[^']*'|" + KW + r")", code_part):
            if not tok:
                continue
            r = p.add_run()
            r.text = tok
            if tok[0] in "\"'":
                c = RGBColor(0xF6, 0xC1, 0x77)
            elif re.fullmatch(KW, tok):
                c = RGBColor(0x82, 0xAA, 0xFF)
            else:
                c = RGBColor(0xE6, 0xE9, 0xEF)
            _font(r, size, c, mono=True)
        if _ or comment:
            r = p.add_run()
            r.text = "#" + comment
            _font(r, size, RGBColor(0x7F, 0xD1, 0x8B), mono=True, italic=True)
    return tb


def notes(slide, text):
    tf = slide.notes_slide.notes_text_frame
    tf.text = (tf.text + "\n\n" if tf.text.strip() else "") + text.strip()


def base(title, crumb, subtitle=None, accent=BLUE):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    textbox(s, 0.6, 0.32, 12.1, 0.7, title, size=30, color=NAVY)
    s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
    rect(s, 0.62, 1.02, 1.3, 0.07, accent, shape=MSO_SHAPE.RECTANGLE)
    if subtitle:
        textbox(s, 2.1, 0.9, 10.6, 0.35, subtitle, size=14, color=GREY)
    textbox(s, 0.6, 7.05, 6, 0.3, "Google ADK · Tworzenie Agentów AI · Comarch", size=10, color=GREY)
    textbox(s, 6.7, 7.05, 6.0, 0.3, crumb, size=10, color=GREY, align=PP_ALIGN.RIGHT)
    return s


def sticker(slide, text, x=9.0, y=0.25, w=4.1, h=0.75):
    s = rect(slide, x, y, w, h, ORANGE, radius=0.2)
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.12)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    rich(p, text, 12, WHITE)
    for r in p.runs:
        r.font.color.rgb = WHITE


GOALS = {
    "D1.1": ["Model to parametr konfiguracji, nie kodu – koszt i jakość zmieniasz w `.env`",
             "Wbudowane narzędzia (grounding) vs własne – kiedy które"],
    "D1.2": ["Docstring + typy = kontrakt narzędzia; LLM sam łączy wywołania",
             "Narzędzie zwraca `status` – błąd to dane, nie wyjątek"],
    "D1.3": ["RAG = narzędzie retrieval; jakość odpowiedzi zależy od indeksu, nie od promptu"],
    "D1.4": ["Pipeline wiedzy: źródło → indeks → agent; aktualizacja bez zmiany kodu"],
    "D1.5": ["Runner + SessionService = runtime agenta poza adk web",
             "Stan sesji to pamięć krótkoterminowa i kontrakt między krokami"],
    "D1.6": ["Proces o znanej kolejności → graf w kodzie, nie decyzja LLM"],
    "D1.7": ["Niezależne kroki równolegle = krótszy czas; JoinNode zbiera wyniki"],
    "D1.8": ["Jakość przez iterację: krytyk + twardy limit pętli = przewidywalny koszt"],
    "D1.9": ["Callbacki = punkt kontroli (guardrails, zatwierdzenia) bez zmiany agenta"],
    "D1.10": ["Wybór delegacji = wybór kto kontroluje rozmowę i ile wywołań LLM płacisz"],
    "D1.11": ["Planowanie: jawny plan (ReAct) vs thinking modelu – koszt tokenów vs jakość"],
    "D1.12": ["Agent to usługa: ten sam kod lokalnie i na Cloud Run, konfiguracja przez env"],
    "D2.1": ["Artefakty = pliki binarne poza kontekstem LLM; sesja trzyma referencje"],
    "D2.2": ["Pamięć długoterminowa: co zapisać, kiedy przywołać – to decyzja projektowa"],
    "D2.3": ["Dostęp do danych przez wąskie narzędzia (read-only, limity), nie surowy SQL"],
    "D2.4": ["MCP = standard integracji; własny serwer = reużywalne narzędzia dla wielu agentów"],
    "D2.5": ["Skills: wiedza doładowana na żądanie = mniejszy prompt i koszt"],
    "D2.6": ["Agent bez testów to prototyp: testy narzędzi → E2E → ewaluacja trajektorii"],
}


def exercise(code_id, title, crumb, module, minutes, steps, stretch, check, pitfalls, note):
    s = base(title, crumb, accent=ORANGE)
    # move title right of badge
    s.shapes[0].left = Inches(2.75)
    s.shapes[1].left = Inches(2.77)
    label(s, 0.6, 0.42, 2.0, 0.5, f"ĆWICZENIE {code_id}", ORANGE, size=14)
    label(s, 0.6, 1.3, 5.6, 0.42, module, LIGHT, color=RGBColor(0x0B, 0x50, 0xA8),
          size=13 if len(module) <= 48 else 10, bold=False, mono=True)
    label(s, 6.35, 1.3, 1.7, 0.42, f"⏱ {minutes} min", NAVY, size=12)
    card(s, 0.6, 1.95, 6.45, 3.45, "Robią (wszyscy)", steps, color=ORANGE, size=14, numbered=True)
    card(s, 0.6, 5.5, 6.45, 1.4, "Wniosek architektoniczny", GOALS[code_id], color=BLUE, size=12)
    card(s, 7.25, 1.95, 5.5, 1.55, "Dodają (dla szybszych)", stretch, color=PURPLE, size=12)
    card(s, 7.25, 3.6, 5.5, 1.45, "Sprawdzenie ✓", check, color=GREEN, size=12)
    card(s, 7.25, 5.15, 5.5, 1.75, "Pułapki / fixy", pitfalls, color=RED, size=12)
    notes(s, note)
    return s


def flow(slide, x, y, names, color=BLUE, w=1.35, h=0.48, gap=0.32, size=11):
    shapes = []
    for i, n in enumerate(names):
        sx = x + i * (w + gap)
        shapes.append(label(slide, sx, y, w, h, n, WHITE if n != "START" else NAVY,
                            color=color if n != "START" else WHITE, size=size,
                            mono=n not in ("START",)))
        shapes[-1].line.color.rgb = color
        shapes[-1].line.width = Pt(1.5)
        if i:
            arrow(slide, sx - gap, y + h / 2, sx, y + h / 2, color)
    return shapes


def arrow(slide, x1, y1, x2, y2, color=GREY, text=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(1.75)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn("a:tailEnd"), {"type": "triangle"})
    ln.append(tail)
    if text:
        textbox(slide, min(x1, x2) + 0.05, min(y1, y2) - 0.3, abs(x2 - x1) + 0.8, 0.3, text, size=10, color=color)
    return c


def section(title, sub, items, crumb):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY
    textbox(s, 0.8, 1.3, 11.5, 1.2, title, size=48, color=WHITE)
    s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
    rect(s, 0.82, 2.55, 1.6, 0.09, ORANGE, shape=MSO_SHAPE.RECTANGLE)
    textbox(s, 0.8, 2.8, 11.5, 0.6, sub, size=20, color=RGBColor(0xB8, 0xC7, 0xE0))
    textbox(s, 0.8, 3.7, 11.5, 3.2, items, size=17, color=WHITE, bullet="▸", spacing=6)
    for p in s.shapes[-1].text_frame.paragraphs:
        for r in p.runs:
            if r.font.color.rgb == NAVY:
                r.font.color.rgb = WHITE
    textbox(s, 6.7, 7.05, 6.0, 0.3, crumb, size=10, color=RGBColor(0xB8, 0xC7, 0xE0), align=PP_ALIGN.RIGHT)
    return s


NEW = {}

# ============================================================================= NEW SLIDES
# --- Agenda
s = base("Plan dwóch dni: teoria → praktyka, blok po bloku", "Agenda",
         subtitle="Każdy blok: krótka teoria (slajdy) → ćwiczenie w module → omówienie")
d1 = [
    ("1", "Po co agenci? Architektura i rynek", "—"),
    ("2", "Pierwszy agent, model, narzędzia", "D1.1–D1.2 · d1_01, d1_02"),
    ("3", "Grounding i RAG (Vertex AI Search)", "D1.3–D1.4 · d1_03"),
    ("4", "Runtime: Runner, sesja, stan", "D1.5 · d1_05"),
    ("5", "Multi-agent → Workflow (ADK 2)", "D1.6–D1.8 · d1_06 – d1_08"),
    ("6", "Callbacki i human-in-the-loop", "D1.9 · d1_09"),
    ("7", "Delegacja i planowanie", "D1.10–D1.11 · d1_10, d1_11"),
    ("8", "Deploy (Cloud Run)", "D1.12 · d1_12"),
]
d2 = [
    ("9", "Artefakty i multimodalność", "D2.1 · d2_01"),
    ("10", "Pamięć długoterminowa (Memory Bank)", "D2.2 · d2_02"),
    ("11", "Integracje: MCP, A2A, bazy danych", "D2.3–D2.4 · d2_03, d2_04"),
    ("12", "Skills i narzędzia deweloperskie", "D2.5 · d2_05"),
    ("13", "Jakość: testy i ewaluacja", "D2.6 · d2_06"),
    ("14", "Enterprise, rejestr agentów, roadmapa", "podsumowanie"),
]
for col, (hdr, rows, color) in enumerate([("DZIEŃ 1 · fundamenty i orkiestracja", d1, BLUE),
                                          ("DZIEŃ 2 · integracje i produkcja", d2, TEAL)]):
    x = 0.6 + col * 6.2
    label(s, x, 1.5, 5.95, 0.45, hdr, color, size=14)
    for i, (n, name, ex) in enumerate(rows):
        y = 2.1 + i * 0.6
        label(s, x, y, 0.45, 0.45, n, WHITE, color=color, size=12, shape=MSO_SHAPE.OVAL).line.color.rgb = color
        textbox(s, x + 0.55, y - 0.02, 3.4, 0.5, name, size=13, anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, x + 3.85, y + 0.06, 2.1, 0.4, ex, size=10, color=GREY, align=PP_ALIGN.RIGHT)
textbox(s, 6.8, 5.85, 5.95, 0.9,
        ["**18 ćwiczeń** w gotowych modułach repo `training_09_10_11`",
         "Każde: Robią → Dodają (dla szybszych) → Sprawdzenie"], size=12, bullet="▸")
notes(s, """Agenda (2 min). Zasada szkolenia: krótka teoria i od razu ćwiczenie w tym samym temacie – bez skakania.
Numeracja ćwiczeń D1.x / D2.x odpowiada slajdom 'ĆWICZENIE' i dokumentowi prowadzenia.
Dzień 1 = fundamenty i orkiestracja (w tym nowy Workflow API z ADK 2). Dzień 2 = integracje i droga do produkcji.""")
NEW["agenda"] = s

# --- Lab setup
s = base("Setup labu (15 min, przed pierwszym ćwiczeniem)", "Dzień 1 · Start",
         subtitle="Jedno środowisko dla wszystkich modułów")
code(s, 0.6, 1.5, 6.9, 3.15, """git clone -b training_09_10_11 <repo>
cd adk-fundamentals
py -3.12 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install --upgrade "google-adk>=2.13.0"
gcloud auth application-default login
gcloud auth application-default set-quota-project adk-training-pz
$env:PYTHONUTF8 = "1"
cd adk_training ; adk web --reload_agents""", size=12, title="PowerShell")
code(s, 0.6, 4.8, 6.9, 2.0, """GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=adk-training-pz
GOOGLE_CLOUD_LOCATION=global   # modele 3.5 tylko na global
ADK_MODEL=gemini-3.5-flash-lite  # domyślny model szkolenia""", size=12, title=".env (adk_training/ lub katalog modułu)")
card(s, 7.75, 1.5, 5.0, 5.3, "Znane problemy → fix", [
    "`Fatal error in launcher` → venv skopiowany z innej ścieżki; odtwórz venv lub `python -m google.adk.cli web`",
    "`UnicodeEncodeError ... charmap` → `$env:PYTHONUTF8=\"1\"`",
    "`--reload` nie działa na Windows → używamy `--reload_agents`",
    "Nowy folder agenta / zmiana grafu → restart `adk web`",
    "Ostrzeżenia `SequentialAgent ... deprecated` – oczekiwane (temat bloku 5)",
    "`adk web` zawsze z `adk_training/` (wyjątek: D1.5 – `python ui.py`)",
], color=RED, size=12)
notes(s, """Setup robimy razem, zanim ktokolwiek zacznie ćwiczenie 1. Sprawdź u każdego: `adk web` otwiera się na http://localhost:8000 i widać listę modułów.
Najczęstsze problemy z poprzedniej edycji są po prawej – miej je pod ręką.
Model: domyślnie gemini-3.5-flash-lite (koszt) – szczegóły na slajdzie o modelach.""")
NEW["setup"] = s

# --- First agent in ADK 2 (replaces outdated code slides)
s = base("Pierwszy agent w ADK 2: kod > prompty", "Dzień 1 · Blok 2: Pierwszy agent",
         subtitle="Agent = model + instrukcja + narzędzia. Funkcja Pythona = narzędzie.")
code(s, 0.6, 1.5, 7.2, 5.3, """import os
from google.adk import Agent

def policz_lup(skrzynie: int, monet_w_skrzyni: int) -> dict:
    \"\"\"Liczy łup: liczba skrzyń x monety w skrzyni.\"\"\"
    return {"status": "ok", "suma": skrzynie * monet_w_skrzyni}

root_agent = Agent(
    name="kwatermistrz",
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash-lite"),
    description="Liczy łupy załogi.",
    instruction="Odpowiadaj zwięźle. Licz narzędziem.",
    tools=[policz_lup],
)""", size=13, title="d1_NN_temat/agent.py")
card(s, 8.05, 1.5, 4.7, 2.55, "Co robi ADK", [
    "Docstring + type hints → schemat narzędzia dla LLM",
    "`root_agent` w `agent.py` → `adk web` sam znajdzie moduł",
    "Pętla: model → function call → wynik → odpowiedź",
], color=BLUE, size=12)
card(s, 8.05, 4.2, 4.7, 2.6, "Dobre praktyki", [
    "Narzędzie zwraca `dict` ze `status` (błąd ≠ wyjątek)",
    "Model z `.env` (`ADK_MODEL`), nie na sztywno",
    "Import z `google.adk` (ADK 2), nie `google_adk`",
    "Mały, nazwany agent = mikroserwis",
], color=GREEN, size=12)
notes(s, """Zamiast starych slajdów z kodem (gemini-2.0-flash, literówki LinAgent/google_adk).
Pokaż na żywo d1_01 i d1_02: struktura folderu (__init__.py, agent.py, root_agent), adk web: Chat / Events / Trace / State.
Podkreśl: opis narzędzia (docstring) to prompt dla modelu – zła nazwa/opis = złe wywołania.""")
NEW["code_first"] = s

# --- Model & cost
s = base("Model i koszt: dlaczego flash-lite na szkoleniu", "Dzień 1 · Blok 2: Pierwszy agent",
         subtitle="Ceny listowe Gemini API / Vertex, USD za 1M tokenów (XI 2026) – sprawdź aktualny cennik")
rows = [("Model", "Input", "Output", "Kiedy"),
        ("gemini-3.5-flash-lite", "$0.30", "$2.50", "domyślny: tools, routing, workflow"),
        ("gemini-3.1-flash-lite", "$0.25", "$1.50", "najtańszy, wycofanie 05.2027"),
        ("gemini-3.5-flash", "$1.50", "$9.00", "trudniejsze rozumowanie, długie odp."),
        ("gemini-3.8-flash", "$0.75", "$3.75", "nowszy flash (cena promo do 12.2026)")]
tbl = s.shapes.add_table(len(rows), 4, Inches(0.6), Inches(1.5), Inches(7.6), Inches(2.6)).table
for c, wdt in enumerate([2.6, 0.9, 0.9, 3.2]):
    tbl.columns[c].width = Inches(wdt)
for r, row in enumerate(rows):
    for c, val in enumerate(row):
        cell = tbl.cell(r, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY if r == 0 else (LIGHT if r == 1 else WHITE)
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = val
        _font(run, 12, WHITE if r == 0 else NAVY, bold=(r <= 1), mono=(c == 0 and r > 0))
card(s, 0.6, 4.3, 7.6, 2.5, "Szacunek: 12 osób × 2 dni", [
    "~300 wywołań/os., ~3k tokenów in + 0,5k out → ~11M in / ~1,8M out",
    "3.5-flash ≈ **$32**  vs  3.5-flash-lite ≈ **$8** (≈4× taniej)",
    "Uwaga: tokeny thinking liczone są jak output",
    "Workflow z funkcjami zamiast agentów = mniej wywołań LLM",
], color=TEAL, size=12)
card(s, 8.45, 1.5, 4.3, 5.3, "Zmierzone na naszym projekcie", [
    "Lite: tool calling, sekwencje i pętle działają (d1_01–d1_08b, d1_10a, d1_10b)",
    "`thinking_level=LOW` na lite → **0 tokenów thinking** – odpowiedź bywa niejednoznaczna",
    "`HIGH` na lite → myśli i odpowiada poprawnie",
    "Zmiana modelu = jedna linia w `.env`: `ADK_MODEL=gemini-3.5-flash`",
    "Modele 3.5 tylko na `GOOGLE_CLOUD_LOCATION=global`",
    "d1_10b na lite: pętla `transfer_to_agent` zamiast `finish_task` → fix: `disallow_transfer_to_parent=True`",
    "Słabszy model = więcej pracy po stronie architektury (jasne narzędzia, routing w kodzie)",
], color=ORANGE, size=12)
notes(s, """Dlaczego flash-lite: ~5x taniej na wejściu i ~3,6x na wyjściu niż 3.5-flash, a dla zadań szkoleniowych (tools, routing, proste workflow) jakość wystarcza – przetestowane na modułach.
Liczby szacunkowe – pokaż, jak samemu policzyć: Events → usage_metadata (prompt/candidates/thoughts tokens).
Ćwiczenie D1.1 zawiera porównanie lite vs flash. Ciekawostka do d1_11b: lite na LOW nie myśli wcale.""")
NEW["cost"] = s

# --- Workflow API (concept)
s = base("ADK 2: Workflow = graf węzłów", "Dzień 1 · Blok 5: Multi-agent → Workflow",
         subtitle="Zamiast SequentialAgent / ParallelAgent / LoopAgent (deprecated w v2)")
textbox(s, 0.6, 1.45, 6, 0.35, "Sekwencja  ·  d1_06b", size=14, color=BLUE)
s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
flow(s, 0.6, 1.9, ["START", "przyjmij", "zwiadowca", "strateg", "kapitan"], BLUE, w=1.2, gap=0.25)
textbox(s, 0.6, 2.65, 6, 0.35, "Fan-out / fan-in  ·  d1_07b", size=14, color=TEAL)
s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
st = label(s, 0.6, 3.6, 1.1, 0.48, "START", NAVY, size=11)
for i, n in enumerate(["zwiad_N", "zwiad_S", "zwiad_E"]):
    yy = 3.05 + i * 0.6
    b = label(s, 2.1, yy, 1.4, 0.45, n, WHITE, color=TEAL, size=11, mono=True)
    b.line.color.rgb = TEAL
    arrow(s, 1.7, 3.84, 2.1, yy + 0.22, TEAL)
    arrow(s, 3.5, yy + 0.22, 3.95, 3.84, TEAL)
j = label(s, 3.95, 3.6, 1.35, 0.48, "JoinNode", TEAL, size=11, mono=True)
k = label(s, 5.65, 3.6, 1.6, 0.48, "szpiegmistrz", WHITE, color=TEAL, size=11, mono=True)
k.line.color.rgb = TEAL
arrow(s, 5.3, 3.84, 5.65, 3.84, TEAL)
textbox(s, 0.6, 4.95, 6, 0.35, "Pętla przez routing  ·  d1_08b", size=14, color=PURPLE)
s.shapes[-1].text_frame.paragraphs[0].runs[0].font.bold = True
flow(s, 0.6, 5.5, ["pisarz", "krytyk", "kapitan", "decyzja"], PURPLE, w=1.15, gap=0.25)
z = label(s, 6.45, 5.5, 1.1, 0.48, "zapisz", WHITE, color=PURPLE, size=11, mono=True)
z.line.color.rgb = PURPLE
arrow(s, 5.95, 5.74, 6.45, 5.74, PURPLE)
textbox(s, 5.85, 5.15, 0.8, 0.3, "gotowe", size=10, color=PURPLE)
for xx in (5.375, 1.175):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(xx), Inches(5.98), Inches(xx), Inches(6.25))
    ln.line.color.rgb = PURPLE
    ln.line.width = Pt(1.75)
arrow(s, 5.375, 6.25, 1.175, 6.25, PURPLE)
textbox(s, 2.3, 6.27, 2.5, 0.3, "popraw (route)", size=10, color=PURPLE)
card(s, 8.0, 1.45, 4.75, 5.35, "Reguły", [
    "Węzeł = `Agent` | funkcja Pythona | `@node`",
    "Krotka w `edges` = sekwencja; krotka w krotce = równolegle",
    "Funkcja zapisuje stan: `yield Event(state={...})`",
    "Router: `yield Event(route=\"popraw\")` + mapa `{trasa: węzeł}`",
    "Parametr funkcji = klucz stanu (wstrzykiwany po nazwie)",
    "Agent: `output_key` zapisuje, `{klucz}` czyta",
    "Człowiek w pętli: `RequestInput` (d1_09x)",
], color=NAVY, size=12)
notes(s, """Najważniejszy slajd techniczny dnia 1. ADK 2 wprowadza jeden prymityw orkiestracji: graf.
Sekwencja, równoległość i pętla to tylko różne krawędzie. Deterministyczne kroki (walidacja, parsowanie, licznik) robimy funkcją – bez LLM, bez kosztu.
Źródło wzorców: google/adk-python@v2/contributing/workflow_samples. Następny slajd: ten sam kod v1 vs v2.""")
NEW["workflow"] = s

# --- v1 vs v2 code
s = base("Ten sam rajd: ADK 1 vs ADK 2", "Dzień 1 · Blok 5: Multi-agent → Workflow",
         subtitle="d1_06a_sequence_adk1_legacy  →  d1_06b_workflow_sequence")
code(s, 0.6, 1.5, 5.9, 3.6, """from google.adk.agents import SequentialAgent

root_agent = SequentialAgent(  # deprecated w v2
    name="pipeline_rajdu",
    sub_agents=[zwiadowca, strateg, kapitan],
)
# kod między agentami? -> własny BaseAgent
# i _run_async_impl (dużo boilerplate)""", size=13, title="ADK 1 (d1_06a)")
code(s, 6.75, 1.5, 6.0, 3.6, """from google.adk import Agent, Event, Workflow

def przyjmij_rozkaz(node_input: str):
    yield Event(state={"cel": node_input})

root_agent = Workflow(
    name="pipeline_rajdu_v2",
    edges=[("START", przyjmij_rozkaz,
            zwiadowca, strateg, kapitan)],
)""", size=13, title="ADK 2 (d1_06b)")
card(s, 0.6, 5.3, 12.15, 1.5, "Co zyskujemy", [
    "Kod deterministyczny jako pełnoprawny węzeł (walidacja, parsowanie, liczniki) – bez LLM i bez własnego BaseAgent",
    "Jawny graf: łatwiej czytać, testować i debugować w adk web (Events / Trace)",
], color=GREEN, size=13)
notes(s, """Pokaż oba moduły w adk web jeden po drugim. W Events porównaj kolejność węzłów.
Pytanie do grupy: gdzie w waszych procesach jest krok, który NIE powinien być LLM-em? (walidacja, mapowanie, reguły biznesowe).""")
NEW["v1v2"] = s

# --- Delegation
s = base("Delegacja: kto przejmuje rozmowę?", "Dzień 1 · Blok 7: Delegacja i planowanie",
         subtitle="Cztery sposoby łączenia agentów – różna kontrola i koszt")
items = [
    ("sub_agents + transfer", BLUE, ["LLM wybiera specjalistę", "Specjalista **przejmuje** rozmowę", "d1_10a · agent.py"]),
    ("AgentTool", TEAL, ["Agent wołany jak funkcja", "Wynik **wraca** do rodzica", "d1_10a · agent_solution.py"]),
    ("Task API (mode)", PURPLE, ["`mode=\"task\"`: dopytuje usera, potem wraca", "`single_turn`: w tle, bez rozmowy", "d1_10b"]),
    ("Workflow route", ORANGE, ["Routing **w kodzie**, nie przez LLM", "Deterministyczny i tani", "d1_10x · d1_08b"]),
]
for i, (hdr, lines, ) in enumerate([(h, l) for h, _, l in items]):
    color = items[i][1]
    card(s, 0.6 + i * 3.08, 1.5, 2.93, 2.6, hdr, lines, color=color, size=13)
card(s, 0.6, 4.3, 12.15, 2.5, "Jak wybrać", [
    "Rozmowa ma się przenieść do eksperta → `sub_agents` · Potrzebuję wyniku i kontroli w rodzicu → `AgentTool`",
    "Ustrukturyzowane zbieranie danych z auto-powrotem → Task API · Reguła jest znana → Workflow route (bez LLM)",
    "Koszt: każdy transfer / AgentTool to dodatkowe wywołania LLM; route w kodzie = 0 tokenów",
    "Lżejszy model + transfer = ryzyko pętli → blokuj `disallow_transfer_to_parent/peers` tam, gdzie powrót jest automatyczny",
], color=NAVY, size=13)
notes(s, """Przed ćwiczeniem D1.10. Pokaż w Events różnicę: transfer_to_agent (zmienia się autor kolejnych odpowiedzi) vs AgentTool (function_call/function_response w rodzicu).
Task API (ADK 2): mode='task' + output_schema – sub-agent zbiera dane od usera i sam wraca przez finish_task.""")
NEW["delegation"] = s

# --- Planners
s = base("Plannery: plan w tekście czy w głowie modelu?", "Dzień 1 · Blok 7: Delegacja i planowanie",
         subtitle="d1_11a_react_planner  vs  d1_11b_builtin_planner")
card(s, 0.6, 1.5, 5.95, 3.0, "PlanReActPlanner (d1_11a)", [
    "Plan jako tekst z tagami (PLANNING / REASONING / ACTION)",
    "Działa z każdym modelem, także bez thinkingu",
    "Widoczny i audytowalny, ale zużywa tokeny odpowiedzi",
    "Kiedy: słabszy model, wymagany ślad decyzji (audyt)",
], color=BLUE, size=13)
card(s, 6.8, 1.5, 5.95, 3.0, "BuiltInPlanner (d1_11b)", [
    "Natywny thinking modelu: `ThinkingConfig(thinking_level=...)`",
    "`include_thoughts=True` → thoughts widoczne w adk web",
    "Często równoległe wywołania narzędzi",
    "Kiedy: złożone zadania wieloetapowe, model z thinkingiem",
], color=PURPLE, size=13)
card(s, 0.6, 4.7, 12.15, 2.1, "Obserwacja z testów (flash-lite)", [
    "`thinking_level=LOW` → lite **nie myśli wcale** (0 thoughts); `HIGH` → myśli i odpowiada poprawnie",
    "3.5-flash myśli już na `LOW` → kompromis: tańszy model + wyższy poziom vs droższy model + niższy",
    "Mierz: `thoughts_token_count` w Events (płacisz jak za output)",
], color=ORANGE, size=13)
notes(s, """To samo pytanie w obu modułach, porównać Events: czas, liczba kroków, THOUGHT.
Zadanie: zmienić thinking_level na LOW w d1_11b i zobaczyć, że na lite thoughts znikają.""")
NEW["planners"] = s

# --- Day 1 summary
s = base("Podsumowanie dnia 1", "Dzień 1 · Koniec",
         subtitle="Co powinien umieć każdy uczestnik")
card(s, 0.6, 1.5, 6.0, 5.3, "Umiem…", [
    "zbudować agenta z narzędziami i wybrać model (koszt!)",
    "podpiąć RAG z Vertex AI Search (engine / datastore)",
    "uruchomić agenta z Pythona (Runner + SessionService)",
    "zbudować sekwencję, równoległość i pętlę jako Workflow",
    "zatrzymać agenta callbackiem (HITL)",
    "wybrać: sub_agents / AgentTool / Task API / route",
    "wdrożyć agenta na Cloud Run",
    "policzyć koszt: tokeny w Events, flash vs flash-lite",
    "uzasadnić: co jest LLM-em, a co zwykłym kodem",
], color=GREEN, size=15, bullet="✓")
card(s, 6.85, 1.5, 5.9, 2.6, "Pytania kontrolne", [
    "Kiedy funkcja zamiast agenta w Workflow?",
    "Czym różni się `state` z prefiksem `user:` od `temp:`?",
    "Dlaczego `reason` przed `decision` w schemacie?",
    "Transfer vs AgentTool – kto odpowiada userowi?",
], color=BLUE, size=13)
card(s, 6.85, 4.3, 5.9, 2.5, "Jutro", [
    "Artefakty, pamięć długoterminowa, MCP / A2A, bazy",
    "OAuth, skills, testy i ewaluacja agentów",
    "Przynieście pomysł na agenta z własnego projektu",
], color=TEAL, size=13)
notes(s, """5 minut. Szybka runda: każdy mówi jedną rzecz, którą wdroży u siebie. Zbierz pytania na rano.""")
NEW["sum1"] = s

# --- Day 2 opener
NEW["day2"] = section("Dzień 2", "Integracje i droga do produkcji",
                      ["Recap dnia 1 (10 min): Workflow, stan, callbacki, delegacja",
                       "Artefakty i pamięć długoterminowa",
                       "MCP, A2A, bazy danych, OAuth",
                       "Skills, testy i ewaluacja agentów",
                       "Enterprise: rejestr agentów, Agent Garden, roadmapa"],
                      "Dzień 2")
notes(NEW["day2"], """Recap: poproś 2–3 osoby o narysowanie na tablicy grafu z wczoraj (sekwencja + pętla). Potem od razu ćwiczenie D2.1.""")
NEW["day1"] = section("Dzień 1", "Fundamenty i orkiestracja agentów",
                      ["Po co agenci i jak o nich myśleć architektonicznie",
                       "Pierwszy agent, narzędzia, model i koszt",
                       "Grounding i RAG",
                       "Runtime i stan · Workflow (ADK 2) · Callbacki",
                       "Delegacja, planowanie i deploy"],
                      "Dzień 1")
notes(NEW["day1"], "Start dnia 1. Po bloku 1 (teoria, ~30 min) przechodzimy do setupu i pierwszego ćwiczenia.")

# --- Testing pyramid
s = base("Jakość agentów: od testu narzędzia do ewaluacji", "Dzień 2 · Blok 13: Jakość",
         subtitle="Agent jest niedeterministyczny – testujemy warstwami")
levels = [("Monitoring: Trace / Cloud Trace, koszty tokenów", GREY, 4.2),
          ("E2E: ADK Tester (d2_06b) – scenariusze w przeglądarce", ORANGE, 6.0),
          ("Ewaluacja: AgentEvaluator (d2_06a) – trajektoria + odpowiedź", PURPLE, 7.8),
          ("Unit: narzędzia i funkcje-węzły (pytest, bez LLM)", GREEN, 9.6)]
for i, (txt, color, wdt) in enumerate(levels):
    x = 0.6 + (9.6 - wdt) / 2
    label(s, x, 1.6 + i * 1.0, wdt, 0.8, txt, color, size=13)
card(s, 10.45, 1.6, 2.3, 3.8, "Zasada", [
    "Im niżej, tym taniej i szybciej",
    "Funkcje w Workflow testujesz jak zwykły kod",
], color=NAVY, size=12)
card(s, 0.6, 5.7, 12.15, 1.1, "Do zapamiętania", [
    "Ewaluacja ocenia też **trajektorię** (jakie narzędzia, w jakiej kolejności) – nie tylko tekst odpowiedzi",
], color=TEAL, size=13)
notes(s, """Przed ćwiczeniem D2.6. Pokaż, że deterministyczne węzły Workflow (np. ocen_ryzyko) mają zwykłe testy jednostkowe.
d2_06a: dataset + kryteria (tool_trajectory, response match). d2_06b: tester E2E z raportem.""")
NEW["testing"] = s

# --- Architect checklist
s = base("Checklista architekta agentów", "Podsumowanie",
         subtitle="Decyzje, które podejmujesz w każdym projekcie")
pairs = [
    ("Orkiestracja", "Reguła znana → Workflow (funkcja/route). Decyzja wymaga języka → Agent.", BLUE),
    ("Delegacja", "Rozmowa do eksperta → sub_agents · wynik do rodzica → AgentTool · formularz → Task API.", TEAL),
    ("Pamięć", "Sesja/stan (rozmowa) · `user:` (użytkownik) · Memory Bank (fakty długoterminowe) · Artefakty (pliki).", PURPLE),
    ("Integracje", "Narzędzie lokalne → funkcja · system zewnętrzny → MCP · inny agent/zespół → A2A.", ORANGE),
    ("Kontrola", "Walidacja → callback · akceptacja człowieka → RequestInput · schemat: `reason` przed `decision`.", RED),
    ("Koszt i jakość", "Najtańszy model, który przechodzi ewaluację · thinking tylko tam, gdzie trzeba · testy warstwowe.", GREEN),
]
for i, (hdr, txt, color) in enumerate(pairs):
    col, row = i % 2, i // 2
    card(s, 0.6 + col * 6.15, 1.5 + row * 1.8, 6.0, 1.65, hdr, [txt], color=color, size=13, bullet="")
notes(s, """Ostatni slajd merytoryczny. Przejdź tabelę z grupą – każda decyzja była ćwiczona w konkretnym module.
Potem: linki (e-profesor + ankieta) i Q&A.""")
NEW["checklist"] = s

# ============================================================================= EXERCISES
EX = {}
EX["D1.1"] = exercise("D1.1", "Hello Agent: model, google_search, wersja ADK", "Dzień 1 · Blok 2",
    "adk_training/d1_01_hello_agent", 25,
    ["Uruchom `adk web --reload_agents`, wybierz moduł, porozmawiaj",
     "Odkomentuj `google_search` (import + `tools=[...]`), zapytaj o coś aktualnego",
     "Ustaw nieistniejący model (`ADK_MODEL=gemini-9-flash`) i przeczytaj błąd",
     "Porównaj `gemini-3.5-flash-lite` (domyślny) z `gemini-3.5-flash`",
     "`pip install --upgrade \"google-adk>=2.13.0\"` i `pip show google-adk`"],
    ["Porównaj tokeny w Events → `usage_metadata`", "Zmień instrukcję: persona + format odpowiedzi"],
    ["Events: wywołanie `google_search` / grounding", "Zły model → `404 NOT_FOUND`"],
    ["Model wpisujemy w `.env` (`ADK_MODEL`) albo w `agent.py`", "Brak linków z wyszukiwania – zależy od odpowiedzi; pokaż grounding w Events"],
    "Pokazuję strukturę modułu i zakładki adk web (Chat/Events/Trace/State). Lista modeli: cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions")
EX["D1.2"] = exercise("D1.2", "Własne narzędzia i łańcuch wywołań", "Dzień 1 · Blok 2",
    "adk_training/d1_02_custom_tools", 20,
    ["Przeczytaj istniejące narzędzia (docstring + type hints)",
     "Dopisz własną metodę-narzędzie i dodaj ją do `tools`",
     "Jednym promptem odpal kilka narzędzi po kolei:",
     "  „Dodaj 5 złotych monet, potem pokaż inwentarz i policz pozycje”",
     "Prześledź w Events kolejność function call → response"],
    ["Walidacja argumentów → `{\"status\": \"error\", ...}`", "Zapis w `tool_context.state` między wywołaniami"],
    ["Events: `add_treasure` → `list_all_treasures`", "Odpowiedź korzysta z wyników narzędzi"],
    ["Graf nie odświeża się → odśwież stronę / restart `adk web`", "Nowe narzędzie niewidoczne → brak w `tools=[...]`"],
    "Dla zaawansowanych: dobry opis narzędzia = mniej pomyłek modelu; pokaż, co się stanie przy złym docstringu.")
EX["D1.3"] = exercise("D1.3", "RAG: podpięcie Vertex AI Search", "Dzień 1 · Blok 3",
    "adk_training/d1_03_rag_vertex_search", 20,
    ["Wpisz w `.env` **jedno** z: `SEARCH_ENGINE_ID` (preferowany) lub `SEARCH_DATASTORE_ID`",
     "Zadaj pytanie o treść dokumentów z indeksu",
     "Zmień `max_results` i instrukcję – porównaj odpowiedzi",
     "Zadaj pytanie spoza dokumentów – co robi agent?"],
    ["Instrukcja: „cytuj źródło”, „nie wiem, jeśli brak w dokumentach”", "Porównaj engine vs datastore"],
    ["Events: wywołanie `VertexAiSearchTool` z wynikami", "Odpowiedź oparta na dokumentach"],
    ["ID zawsze z `locations/global`", "`404 DataStore not found` → stare/usunięte ID", "`400 Invalid location us-central1` → zła lokalizacja w ID"],
    "ID engine/datastore podaję na czacie. Format: projects/adk-training-pz/locations/global/collections/default_collection/engines/<id>.")
EX["D1.4"] = exercise("D1.4", "Własny indeks: bucket → datastore → app", "Dzień 1 · Blok 3",
    "Konsola GCP + d1_03_rag_vertex_search", "15 + 15",
    ["Utwórz bucket i wgraj kilka własnych dokumentów (PDF/MD)",
     "AI Applications: datastore z bucketa → app (search engine)",
     "**Start indeksowania → robimy D1.5 → wracamy** (indeks buduje się kilka–kilkanaście minut)",
     "Podmień ID w `.env` na swój engine i zapytaj o treść **swoich** dokumentów"],
    ["Pytanie wymagające połączenia 2 dokumentów", "Porównaj chunking / parsowanie w ustawieniach datastore"],
    ["Agent cytuje treść waszych dokumentów", "W konsoli: status importu = zakończony"],
    ["„Unable to create your bucket” → ponów", "Brak wyników → indeks jeszcze się buduje"],
    "Część 1 (15 min): bucket + datastore + app, start importu. Potem Blok 4 i D1.5. Część 2 (15 min, przed obiadem): zapytania do własnego indeksu.")
EX["D1.5"] = exercise("D1.5", "Agent z Pythona: Runner, sesja i stan", "Dzień 1 · Blok 4",
    "d1_05_runner_session_gradio → python ui.py", 25,
    ["`cd adk_training\\d1_05_runner_session_gradio`",
     "`python ui.py` – rozmowa w UI Gradio (bez adk web)",
     "Podejrzyj stan sesji w UI",
     "Nowa sesja vs kontynuacja – co agent pamięta?"],
    ["Prefiksy stanu: `user:` / `app:` / `temp:` – co przeżywa nową sesję?", "Podmień `InMemorySessionService` na trwały"],
    ["Stan rośnie w trakcie rozmowy", "`user:` widoczne w nowej sesji, zwykły klucz – nie"],
    ["Port zajęty → zamknij poprzednie UI", "`UnicodeEncodeError` → `PYTHONUTF8=1`"],
    "Przeniesione przed multi-agent, bo stan (output_key, {klucz}) jest podstawą Workflow.")
EX["D1.6"] = exercise("D1.6", "Sekwencja: od SequentialAgent do Workflow", "Dzień 1 · Blok 5",
    "d1_06a_sequence_adk1_legacy → d1_06b_workflow_sequence", 25,
    ["Pokaz prowadzącego – d1_06a: „Zaatakuj fort na wyspie Tortuga”",
     "Uruchom d1_06b z tym samym promptem – porównaj Events i State",
     "4W.2: dodaj agenta `kwatermistrz` (`output_key=\"lista_zapasow\"`) przed Kapitanem",
     "Użyj `{lista_zapasow}` w instrukcji Kapitana"],
    ["4W.1: funkcja `ocen_ryzyko(plan_bitwy: str)` między strategiem a kapitanem", "`yield Event(state={\"poziom_ryzyka\": ...})`"],
    ["Events: przyjmij_rozkaz → zwiadowca → strateg → (kwatermistrz) → kapitan", "State: klucze z `output_key`"],
    ["`{klucz}` nie istnieje → użyj `{klucz?}`", "Nowy węzeł niewidoczny → restart `adk web`"],
    "Kluczowy moment szkolenia: funkcja jako węzeł (parametr wstrzykiwany ze stanu po nazwie). Rozwiązanie: agent_solution.py – włączenie: `from .agent_solution import root_agent` w __init__.py.")
EX["D1.7"] = exercise("D1.7", "Równoległość: fan-out i JoinNode", "Dzień 1 · Blok 5",
    "d1_07a_parallel_adk1_legacy → d1_07b_workflow_parallel", 20,
    ["d1_07a (pokaz) i d1_07b: „Zbadaj wyspę Skull Island”",
     "Zobacz w Events, że zwiadowcy kończą w różnej kolejności",
     "7W.1: dodaj czwartego zwiadowcę (tylko `edges` + instrukcja)"],
    ["7W.2: `podsumuj_zbiorke(node_input: dict)` po `JoinNode`", "Klucze słownika = nazwy węzłów"],
    ["Równoległe gałęzie w Trace", "Szpiegmistrz dostaje wszystkie raporty"],
    ["`429 RESOURCE_EXHAUSTED` → odczekaj / mniej gałęzi", "Cała grupa naraz → rozłóż w czasie"],
    "")
EX["D1.8"] = exercise("D1.8", "Pętla krytyki: generator ↔ krytyk", "Dzień 1 · Blok 5",
    "d1_08a_loop_adk1_legacy → d1_08b_workflow_loop", 25,
    ["d1_08a (pokaz: LoopAgent + escalate) i d1_08b (route) – ten sam temat",
     "Zmień kryteria krytyka i obserwuj liczbę iteracji",
     "Znajdź w d1_08b `MAX_ITERACJI` i router `decyzja`"],
    ["8W.2: zastąp agenta `kapitan` funkcją (mniej wywołań LLM)", "8W.1: akceptacja człowieka przez `RequestInput`"],
    ["Events: `route=popraw` / `gotowe`", "Licznik `iteracja` w State"],
    ["Pętla się nie kończy → `MAX_ITERACJI`, dokładny tekst kryterium", "Schemat: `reason` **przed** `decision` (Literal)"],
    "Tip z poprzedniej grupy: model generuje token po tokenie, więc najpierw uzasadnienie, potem decyzja – wdrożone w d1_09, d1_08a, d1_08b.")
EX["D1.9"] = exercise("D1.9", "Human-in-the-loop przez callbacki", "Dzień 1 · Blok 6",
    "adk_training/d1_09_hitl_callbacks", 20,
    ["Prompt: „Potrzebuję 500 dublonów na naprawę żagli”",
     "Zobacz `pending_approval` w State",
     "Spróbuj „tak, zatwierdzam” – kwatermistrz odmawia (tylko Admirał może)",
     "Prześledź callbacki: before_agent → before_tool → after_tool"],
    ["Zmień próg kwoty / dodaj regułę w `before_tool_callback`", "Guardrail: `before_model_callback` blokujący słowa/PII"],
    ["Events: decyzja Admirała (`AdmiralDecision`)", "Zablokowane narzędzie nie wykonuje się"],
    ["„Uparty” agent – to zamierzone zabezpieczenie", "Natywnie w Workflow: `RequestInput` (d1_09x)"],
    "Most do Workflow: ten sam problem w grafie rozwiązuje RequestInput (zapas Z2).")
EX["D1.10"] = exercise("D1.10", "Router, agent-as-a-tool i Task API", "Dzień 1 · Blok 7",
    "d1_10a_router_transfer  +  d1_10b_task_api", 30,
    ["d1_10a: dodaj specjalistę (np. `doctor`) do `sub_agents`, przetestuj routing",
     "AgentTool (po pull rozwiązania): `from .agent_solution import root_agent` w `__init__.py`",
     "  „Ranny marynarz i kurs na Jamajkę” – porównaj Events z wersją transfer",
     "d1_10b: „Przygotuj statek, płyniemy do Tortugi”",
     "  potem: „10 beczek rumu, 20 sucharów, 30 wody, 5 prochu” → „To wszystko”"],
    ["d1_10b: agent `skarbnik` (`mode=\"single_turn\"`) z narzędziem wyceny", "Porównaj z routingiem w kodzie (d1_10x)"],
    ["transfer: zmienia się autor odpowiedzi", "AgentTool: 2 wywołania naraz, kapitan zostaje", "Task: `finish_task` i powrót"],
    ["Nowy agent widoczny po restarcie `adk web`", "Lite: pętla `transfer_to_agent` → `disallow_transfer_to_parent` (ćw. 33.3)"],
    "Na flash-lite kwatermistrz bez blokady transferu zapętlał transfer_to_agent zamiast finish_task – naprawione w module (disallow_transfer_to_parent/peers); ćwiczenie 33.3 pokazuje problem na żywo. README d1_10a: agent nazywa się captain_router.")
EX["D1.11"] = exercise("D1.11", "Plannery: ReAct vs BuiltIn (thinking)", "Dzień 1 · Blok 7",
    "d1_11a_react_planner  vs  d1_11b_builtin_planner", 15,
    ["`cd adk_training ; adk web --reload_agents`",
     "To samo pytanie w d1_11a i d1_11b (np. kampania usługi chmurowej w UE)",
     "Porównaj Events: THOUGHT, liczbę kroków, czas"],
    ["d1_11b: `thinking_level` LOW vs HIGH na flash-lite", "`include_thoughts=False` – co się zmienia?"],
    ["d1_11a: tagi planu w tekście", "d1_11b: thoughts + często równoległe narzędzia"],
    ["Lite na LOW → 0 thoughts (to nie błąd)", "Oba moduły są w jednym dropdownie `adk web`"],
    "Wniosek kosztowy: thinking płatny jak output.")
EX["D1.12"] = exercise("D1.12", "Deploy na Cloud Run", "Dzień 1 · Blok 8",
    "adk_training/d1_12_deploy_cloud_run", "10 demo",
    ["Wywołaj wdrożonego agenta: pirate-navigator-28948426345.us-central1.run.app",
     "Przeczytaj `pirate_navigator/agent.py` – to ten sam kod co lokalnie",
     "Chętni: własny deploy wg `DEPLOY_GCLOUD_GUIDE.md` (PowerShell)"],
    ["`adk deploy cloud_run` vs Dockerfile – porównaj", "Zmienne środowiskowe (`ADK_MODEL`) w usłudze"],
    ["Odpowiedź z URL usługi", "Logi w Cloud Run"],
    ["Region Cloud Run (us-central1) ≠ lokalizacja modelu (global)", "Skrypty `.sh` → Git Bash / WSL"],
    "")
EX["D2.1"] = exercise("D2.1", "Obrazy i artefakty (Nano Banana)", "Dzień 2 · Blok 9",
    "d2_01_artifacts", 30,
    ["Wygeneruj obraz – zapisze się jako artefakt",
     "W **nowej sesji** poproś o opis poprzedniego obrazu",
     "Edytuj istniejący obraz → nowa wersja artefaktu",
     "Sprawdź listę wersji w zakładce Artifacts"],
    ["Proporcje i styl w prompcie", "Własne narzędzie: lista artefaktów użytkownika"],
    ["Artifacts: kolejne wersje pliku", "Nowa sesja zna obraz (stan `user:`)"],
    ["429 quota przy całej grupie → generujcie na zmianę", "Model obrazów: `gemini-2.5-flash-image` (nie Imagen na global)"],
    "Zamiast 'zmień ilość zdjęć' – edycja i wersjonowanie artefaktów.")
EX["D2.2"] = exercise("D2.2", "Memory Bank: pamięć między sesjami", "Dzień 2 · Blok 10",
    "adk_training/d2_02_memory_bank", 30,
    ["`python create_agent_engine.py` → zapisz ID",
     "`adk web --memory_service_uri=agentengine://projects/<P>/locations/us-central1/reasoningEngines/<ID>`",
     "Powiedz fakty o sobie („podróżuję do Gdańska”)",
     "Nowa sesja → agent pamięta; sprawdź wspomnienia w konsoli GCP"],
    ["Instrukcja: kiedy agent ma zapisywać wspomnienia", "Porównaj: stan `user:` vs Memory Bank"],
    ["Nowa sesja przywołuje fakt", "Konsola: wpisy pamięci"],
    ["Krótki `agentengine://ID` użyje `global` → podaj pełny URI z regionem", "Zapis asynchroniczny → odczekaj chwilę"],
    "")
EX["D2.3"] = exercise("D2.3", "Agent i baza danych", "Dzień 2 · Blok 11",
    "d2_03a_database_sqlite  →  d2_03b_database_postgres_mcp (chętni)", 35,
    ["d2_03a: `python init_database.py`, potem zapytanie w języku naturalnym",
     "Dodaj własne narzędzie do `database_tools.py` (read-only, z limitem)",
     "Chętni – d2_03b: Postgres (Neon) przez MCP Toolbox, `sslmode=require`",
     "Dodaj / zmień narzędzie SQL w `toolbox.yaml`"],
    ["Narzędzie zapisujące (INSERT) z potwierdzeniem", "Logowanie zapytań (`query_logger`)"],
    ["Agent zwraca dane z bazy", "Nowe narzędzie widoczne w Events"],
    ["Toolbox na Windows → najprościej WSL2", "Emoji w skryptach d2_03a → `PYTHONUTF8=1`"],
    "Toolbox to serwer MCP dla baz – dobry most do kolejnego ćwiczenia.")
EX["D2.4"] = exercise("D2.4", "MCP: gotowy serwer, własny serwer, OAuth", "Dzień 2 · Blok 11",
    "d2_04a_mcp_servers · d2_04b_oauth_openapi", "45 + 30",
    ["Podepnij piracki serwer MCP i wywołaj jego narzędzia",
     "Napisz własny serwer MCP (STDIO) z 1–2 narzędziami",
     "Po obiedzie – OAuth: consent screen, redirect URI, People API",
     "Zaloguj się w adk web i pobierz dane użytkownika"],
    ["Własny MCP jako zdalny (HTTP)", "Porównaj MCP vs zwykła funkcja-narzędzie"],
    ["Narzędzia MCP w Events", "OAuth: dane z People API"],
    ["403 → brak test usera na consent screen / wyłączone API", "Test MCP w PowerShell: here-string zamiast `echo |`", "Sekrety OAuth nie na czacie"],
    "Uczestników dodać wcześniej jako test users. GOOGLE_CLIENT_SECRET z poprzedniej edycji zrotować.")
EX["D2.5"] = exercise("D2.5", "Skills: wiedza ładowana na żądanie", "Dzień 2 · Blok 12",
    "adk_training/d2_05_agent_skills", 30,
    ["`adk web` z `adk_training/` → `d2_05_agent_skills`",
     "Przejdź: `agent.py` → `agent_dynamic.py` → `agent_self_loading.py` (przełączanie w `__init__.py`)",
     "Stwórz skill dynamicznie",
     "Użyj kodu z innego naszego agenta jako skill"],
    ["Skill z własną dokumentacją projektu", "Porównaj: skill vs RAG vs instrukcja"],
    ["Agent ładuje skill dopiero gdy potrzebny", "Nowy skill na liście"],
    ["Nie `adk web .` z wnętrza modułu – ADK uzna `skills/` za aplikację", "Po zmianie `__init__.py` → restart `adk web`"],
    "Nawiąż do slajdu 'plac budowy' (instructions / skills / MCP).")
EX["D2.6"] = exercise("D2.6", "Testy E2E i ewaluacja agenta", "Dzień 2 · Blok 13",
    "d2_06a_evaluation  →  d2_06b_e2e_tester", 40,
    ["d2_06a: dataset + kryteria (trajektoria, odpowiedź), uruchom `adk eval`",
     "Dopisz przypadek testowy dla własnego agenta z dnia 1",
     "d2_06b (pokaz / chętni): `python -m playwright install chromium`",
     "Scenariusz E2E dla własnego agenta → raport testera"],
    ["Test jednostkowy funkcji-węzła z Workflow (pytest)", "Próg jakości w CI"],
    ["Raport testera", "Wynik ewaluacji z metrykami"],
    ["`COMPUTER_USE_MODEL` (preview) – sprawdź dostępność", "Porty 8000/8001 zajęte", "Mail z raportem → sprawdź spam"],
    "")

# ============================================================================= stickers + notes on kept slides
src = list(prs.slides)[:N_SRC]
sticker(src[21], "**ADK 2:** Sequential / Parallel / Loop → `Workflow(edges=...)` – za chwilę", x=8.9, y=6.55, w=4.2, h=0.6)
notes(src[21], "ADK 2: SequentialAgent/ParallelAgent/LoopAgent są deprecated (działają). Nowy kod: Workflow – następne slajdy i moduły d1_06b/d1_07b/d1_08b.")
sticker(src[42], "**ADK 2:** zamiast własnego `_run_async_impl` → funkcja-router `yield Event(route=...)`", x=6.6, y=5.9, w=6.3, h=0.7)
notes(src[42], "Tak wyglądał custom agent w ADK 1. W ADK 2 ten sam 'if condition: agent_A else agent_B' to funkcja-węzeł z Event(route=...) – patrz d1_08b / d1_10x.")
sticker(src[14], "**ADK 2:** Agenci Workflow = `Workflow` (graf węzłów)", x=8.9, y=0.9, w=4.2, h=0.55)
notes(src[46], "Do ćwiczenia D2.6 / ankieta na koniec dnia 2.")

# ============================================================================= ORDER
S = lambda n: src[n - 1]  # noqa: E731
order = [
    S(1), S(2), NEW["agenda"], NEW["day1"],
    # Blok 1 – po co agenci
    S(3), S(4), S(5), S(6), S(7), S(8), S(9), S(11), S(10), S(12), S(13),
    # Blok 2 – pierwszy agent
    S(14), S(44), S(15), NEW["setup"], NEW["code_first"], NEW["cost"], EX["D1.1"], S(16), EX["D1.2"],
    # Blok 3 – RAG
    S(17), S(18), S(19), S(20), EX["D1.3"], EX["D1.4"],
    # Blok 4 – runtime i stan
    S(24), S(45), S(21), S(23), EX["D1.5"],
    # Blok 5 – multi-agent -> workflow
    S(22), NEW["workflow"], NEW["v1v2"], EX["D1.6"], EX["D1.7"], S(43), EX["D1.8"],
    # Blok 6 – callbacki
    S(25), S(26), EX["D1.9"],
    # Blok 7 – delegacja i planowanie
    NEW["delegation"], EX["D1.10"], NEW["planners"], EX["D1.11"],
    # Blok 8 – deploy
    S(27), S(28), S(29), EX["D1.12"], NEW["sum1"],
    # DZIEŃ 2
    NEW["day2"],
    S(36), EX["D2.1"],
    S(46), EX["D2.2"],
    S(37), S(38), S(39), S(40), EX["D2.3"], EX["D2.4"],
    S(41), EX["D2.5"],
    NEW["testing"], EX["D2.6"],
    S(34), S(35), S(32), S(33), S(31), S(30),
    NEW["checklist"], S(47), S(48), S(51),
]
dropped = [S(42), S(49), S(50)]

sld_lst = prs.slides._sldIdLst
by_slide = {}
for sid in list(sld_lst):
    by_slide[prs.part.related_part(sid.rId)] = sid
assert len(order) == len({id(x) for x in order}), "duplicate slide in order"
for sld in dropped:
    sid = by_slide[sld.part]
    prs.part.drop_rel(sid.rId)
    sld_lst.remove(sid)
for sid in list(sld_lst):
    sld_lst.remove(sid)
for sld in order:
    sld_lst.append(by_slide[sld.part])
missing = set(by_slide) - {x.part for x in order} - {x.part for x in dropped}
assert not missing, f"slides not placed: {len(missing)}"

# Source slides/notes still use the old module_XX names -> map to d<day>_<exercise> dirs.
RENAMES = [
    ("module_01_hello_world", "d1_01_hello_agent"), ("module_02_custom_tool", "d1_02_custom_tools"),
    ("module_03_rag_agent", "d1_03_rag_vertex_search"), ("module_05_human_in_loop", "d1_09_hitl_callbacks"),
    ("module_06_cloud_run", "d1_12_deploy_cloud_run"), ("module_07_parallel_agent", "d1_07a_parallel_adk1_legacy"),
    ("module_08_loop_critique", "d1_08a_loop_adk1_legacy"), ("module_09_database_postgres", "d2_03b_database_postgres_mcp"),
    ("module_11_memory_bank", "d2_02_memory_bank"), ("module_12_router_agent", "d1_10a_router_transfer"),
    ("module_15_gmail_integration", "d2_04x_ext_gmail"),
    ("module_03", "d1_03"), ("module_09", "d2_03"), ("module_15", "d2_04x_ext_gmail"),
]


def _rename(text):
    for old, new in RENAMES:
        text = re.sub(re.escape(old) + r"(?![A-Za-z0-9_])", new, text)
    return text


for sl in prs.slides:
    frames = [sh.text_frame for sh in sl.shapes if sh.has_text_frame]
    if sl.has_notes_slide:
        frames.append(sl.notes_slide.notes_text_frame)
    for tf in frames:
        for para in tf.paragraphs:
            for run in para.runs:
                if "module_" in run.text:
                    run.text = _rename(run.text)
prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
