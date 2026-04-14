# Computer Use Agent vs Playwright — analiza biznesowa

## Kontekst

Mamy działającego agenta (Gemini Computer Use + ADK), który patrzy na ekran przeglądarki, klika, wpisuje tekst i podejmuje decyzje na podstawie tego, co widzi. Pytanie: **czy to ma sens w produkcji** — np. w systemach OSS/BSS telco (Comarch Inventory, CRM, Order Management)?

---

## 1. Gdzie czysty Playwright wygrywa (i agent jest zbędny)

### Testy regresyjne ze stabilnym UI
Jeśli masz 200 test case'ów na stałych formularzach, gdzie ścieżka jest zawsze taka sama — Playwright jest **10× tańszy, 100× szybszy i deterministyczny**. Selektor CSS `#btn-submit` nie halucynuje.

### Smoke testy po deployu
"Otwórz stronę logowania → zaloguj się → sprawdź czy dashboard się załadował" — zero powodu, żeby płacić za model LLM.

### Testy wydajnościowe / load testy
Agent nie nadaje się do generowania obciążenia. To domena k6, Locust, Artillery.

### Proste scraping / data entry
Jeśli workflow jest powtarzalny i znany z góry, skrypt Playwright jest niezawodny. Agent ma ~5% failure rate nawet na prostych krokach.

**Reguła kciuka**: jeśli potrafisz napisać deterministyczny skrypt — napisz skrypt.

---

## 2. Gdzie agent Computer Use jest lepszy od Playwright

### 2.1. Dynamiczny UI bez stabilnych selektorów

**Problem w Comarch OSS Inventory**: widoki konfiguracyjne zasobów sieciowych (NE, porty, sloty, karty liniowe) są generowane dynamicznie z modelu danych. Każdy operator telco ma inny model zasobów → **inne formularze, inne pola, inne dropdown'y**. Selektory CSS zmieniają się z release na release.

**Agent**: patrzy na ekran i widzi "pole Slot Number" → klika w nie → wpisuje wartość. Nie obchodzi go, czy to `div[data-field-id="x7f3"]` czy nowy `input.resource-slot-field`. **Resilience na zmiany UI jest natywna.**

### 2.2. Eksploracyjne testy na nieznanym UI

**Scenariusz**: nowa wersja Comarch Inventory 2026.1 → QA dostaje build, ale nie ma jeszcze dokumentacji zmian UI. 

- Playwright: nie napiszesz testu na UI, którego nie znasz
- Agent: "Otwórz moduł Inventory → znajdź listę urządzeń sieciowych → spróbuj dodać nowy router → opisz co widzisz i czy formularz działa"

To jest **eksploracyjny QA na sterydach** — agent robi to, co robiłby tester manualny, ale 24/7.

### 2.3. Testy end-to-end przez wiele systemów z różnymi UI

**Typowy flow telco**:
1. CRM → złóż zamówienie (React app)
2. Order Management → sprawdź status (Angular app)
3. Inventory → zweryfikuj alokację zasobów (Comarch Java thick client / webowy)
4. Network Activation → potwierdź provisioning (stary portal JSP)
5. Billing → sprawdź naliczenie (SAP lub custom)

Każdy system ma inny framework, inny CSS, inną konwencję. Utrzymanie selektorów Playwright przez 5 systemów to **koszmar**. Agent widzi ekran i klika — niezależnie czy to React, Angular, JSP czy Swing przez noVNC.

### 2.4. Testy z "ludzkim osądem" (nie tylko assert)

**Playwright**: `expect(page.locator('#status')).toHaveText('Active')` — binarny wynik.

**Agent**: "Otwórz widok zasobu ONT-12345. Czy dane wyglądają spójnie? Czy adres instalacji pasuje do lokalizacji węzła OLT? Czy jest coś podejrzanego?"

Agent potrafi ocenić **semantyczną poprawność** — nie tylko czy pole ma wartość, ale czy ta wartość **ma sens w kontekście biznesowym**. To jest przewaga modelu językowego.

### 2.5. Testowanie integracji z systemami bez API

Wiele systemów OSS/BSS (szczególnie starsze wersje Comarch, Amdocs, Netcracker) **nie mają API testowego**. Jedyny interfejs to UI. Playwright wymaga reverse-engineeringu selektorów. Agent po prostu widzi i klika.

---

## 3. Scenariusze produkcyjne — nie tylko testowanie

### 3.1. RPA (Robotic Process Automation) z inteligencją

**Klasyczny RPA** (UiPath, Blue Prism): nagrywasz makro, odtwarzasz. Łamie się przy każdej zmianie UI.

**Agent Computer Use jako RPA**:
- "Każdego ranka otwórz Comarch Inventory → wejdź w raporty alarmów → wyeksportuj alarmy krytyczne → wklej do Jiry jako tickety"
- Agent **adaptuje się** do zmian layoutu — przycisk się przesunął? Nie szkodzi, agent go znajdzie.
- Agent **podejmuje decyzje**: "Ten alarm to false positive (bo port jest w maintenance window) → pomiń"

**To jest L2/L3 NOC automation** — ogromna wartość w telco.

### 3.2. Asystent operatora (copilot dla NOC / SOC)

Operator sieci mówi agentowi:
> "Sprawdź na Comarch Inventory status wszystkich portów na routerze PE-WAW-01 i powiedz mi, które mają utilization powyżej 80%"

Agent:
1. Otwiera Inventory
2. Wyszukuje router PE-WAW-01
3. Wchodzi w widok portów
4. Czyta dane z tabeli
5. Odpowiada: "Porty Gi0/0/1 (87%) i Gi0/0/3 (92%) przekraczają próg. Gi0/0/3 jest podłączony do klienta Enterprise X — sugeruję eskalację."

**Żaden skrypt Playwright tego nie zrobi** — bo wymaga rozumienia kontekstu i formułowania wniosków.

### 3.3. Migracje danych przez UI (gdy nie ma API)

**Scenariusz**: migracja z Comarch OSS 2023 na 2026. Część danych trzeba przenieść ręcznie przez formularze UI (bo nowy model danych ma inne pola).

- 500 urządzeń do przepisania
- Każde urządzenie wymaga 15 kliknięć i 8 pól
- Tester manualny: 2 tygodnie
- Agent: "Otwórz stary system → odczytaj dane urządzenia X → przejdź do nowego systemu → wypełnij formularz → zapisz → zweryfikuj"

Agent robi to w godziny, a nie tygodnie. I umie obsłużyć edge case'y ("to pole nie istnieje w nowym systemie → zapisz do raportu wyjątków").

### 3.4. Compliance / audyt UI

"Sprawdź czy wszystkie formularze w module Inventory mają walidację na polach wymaganych. Otwórz każdy formularz, spróbuj zapisać pusty i sprawdź czy pojawia się komunikat błędu."

Agent potrafi to zrobić **eksploracyjnie** — bez listy formularzy, sam je znajdzie i przetestuje.

---

## 4. Czy to "żal"? Rzetelna ocena ograniczeń

### Ograniczenia, które trzeba znać:

| Problem | Wpływ | Mitygacja |
|---------|-------|-----------|
| **Koszt** — ~$0.05-0.15 za krok (screenshot + LLM inference) | Droższy niż Playwright przy dużej skali | Używaj agenta tylko tam, gdzie Playwright nie daje rady |
| **Niedeterminizm** — ten sam prompt → różne kliknięcia | ~5-10% flaky rate | Retry + walidacja wyniku + human review |
| **Szybkość** — 10-15s na krok vs 100ms w Playwright | Nie nadaje się do tysięcy testów | Agent na smoke/eksplorację, Playwright na regresję |
| **Halucynacje** — agent "widzi" coś, czego nie ma | Może kliknąć w złe miejsce | Walidacja screenshot'ów, safety guardrails |
| **Bezpieczeństwo** — agent ma dostęp do przeglądarki z credentials | Ryzyko wycieku danych | Izolowane środowisko, tylko test/staging, audit log |
| **Context window** — przy długich sesjach agent "zapomina" | Po ~30 krokach traci kontekst | Dzielenie na krótkie misje, reset stanu |

### Kiedy to jest "żal":

1. **Deterministyczne, znane flows** — nie potrzebujesz LLM do klikania w znany przycisk
2. **Masowe testy regresyjne** — koszt i czas się nie skalują
3. **Systemy z dobrym API** — jeśli możesz testować przez API, rób to
4. **Krytyczne systemy produkcyjne** — nie puszczaj agenta na prod bez sandboxa

### Kiedy to jest **złoto**:

1. **Legacy systemy telco bez API** — jedyny interfejs to UI
2. **Dynamiczny UI z częstymi zmianami** — Comarch co kwartał zmienia layouty
3. **Cross-system E2E** — agent nie dba o framework
4. **Eksploracyjny QA** — agent zastępuje testera manualnego
5. **Inteligentny RPA** — agent podejmuje decyzje, nie tylko klika
6. **Onboarding / demo automation** — "pokaż nowemu pracownikowi jak używać systemu"

---

## 5. Architektura hybrydowa — rekomendacja

Nie "agent albo Playwright". **Oba razem.**

```
┌─────────────────────────────────────────────────────┐
│                CI/CD Pipeline                        │
├──────────────────┬──────────────────────────────────┤
│                  │                                    │
│  Warstwa 1:      │  Warstwa 2:          Warstwa 3:   │
│  API Tests       │  Playwright          Agent CU     │
│  (fastest)       │  (UI regresja)       (inteligentne│
│                  │                       testy)       │
│  • REST/GraphQL  │  • znane formularze  • eksploracja│
│  • unit testy    │  • happy paths       • cross-sys  │
│  • contract      │  • smoke testy       • semantic QA│
│  • 1000+ / min   │  • 100+ / min        • 5-10 / min │
├──────────────────┴──────────────────────────────────┤
│              Wspólny Reporting Layer                  │
│    (Allure / custom dashboard + video recordings)    │
└─────────────────────────────────────────────────────┘
```

Agent Computer Use to **warstwa 3** — najdroższa, najwolniejsza, ale **jedyna która potrafi myśleć**. Uruchamiasz ją na scenariuszach, które inaczej wymagałyby człowieka.

---

## 6. Podsumowanie

| Kryterium | Playwright | Agent Computer Use |
|-----------|------------|-------------------|
| Deterministyczność | ✅ 100% | ⚠️ ~90-95% |
| Szybkość | ✅ 100ms/krok | ❌ 10-15s/krok |
| Koszt | ✅ ~$0 | ⚠️ ~$0.05-0.15/krok |
| Resilience na zmiany UI | ❌ łamie się | ✅ adaptuje się |
| Cross-system | ❌ per-framework | ✅ uniwersalny |
| Semantyczna walidacja | ❌ binarny assert | ✅ rozumie kontekst |
| Eksploracja nieznanego UI | ❌ niemożliwe | ✅ natywne |
| Legacy bez API | ❌ trudne | ✅ idealne |
| Skalowalność | ✅ tysiące | ❌ dziesiątki |

**Werdykt**: Agent Computer Use **nie zastępuje** Playwright — **uzupełnia go** tam, gdzie automatyzacja deterministyczna się kończy, a zaczyna się potrzeba inteligencji. W telco OSS/BSS (Comarch, Amdocs, Netcracker), gdzie UI jest dynamiczny, legacy i cross-systemowy — to realna wartość biznesowa.

Nie jest to "żal" — pod warunkiem, że używasz go we właściwej warstwie piramidy testów.
