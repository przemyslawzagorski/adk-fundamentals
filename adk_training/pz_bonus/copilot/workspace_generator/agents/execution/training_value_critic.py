"""
🎓 Training Value Critic
Krytyk z wysokim common sense - sprawdza wartość szkoleniową wygenerowanych ćwiczeń
"""

from pydantic import BaseModel, Field
from typing import List
from google.adk.agents import LlmAgent


class TrainingValueCritique(BaseModel):
    """Ocena wartości szkoleniowej"""
    score: float = Field(description="Ocena 1.0-10.0 (8.0+ = approved)", ge=1.0, le=10.0)
    is_approved: bool = Field(description="Czy ćwiczenie ma wartość szkoleniową")
    feedback: str = Field(description="Szczegółowa ocena")
    issues: List[str] = Field(description="Lista problemów do naprawy")
    strengths: List[str] = Field(description="Mocne strony ćwiczenia")
    suggestions: List[str] = Field(description="Sugestie ulepszeń")


def create_training_value_critic(model="gemini-2.5-flash", config=None):
    """
    Tworzy krytyka wartości szkoleniowej z wysokim common sense.

    Sprawdza:
    - Czy ćwiczenie uczy konkretnej funkcji Copilota
    - Czy nie ma przykładowych odpowiedzi (student sam ćwiczy!)
    - Czy nie dubluje się z innymi ćwiczeniami
    - Czy ma wartość praktyczną
    - Czy jest na odpowiednim poziomie trudności
    """

    # UWAGA: LlmAgent nie przyjmuje 'temperature' bezpośrednio w konstruktorze!
    # Używa domyślnych ustawień modelu

    instruction = """Jesteś ekspertem szkoleniowym z wysokim common sense.

**KONTEKST:**
Oceniasz wartość szkoleniową wygenerowanego ćwiczenia dla GitHub Copilot Masterclass.

**WYGENEROWANE ĆWICZENIE:**
{generated_code}

**KRYTERIA OCENY (Common Sense):**

1. **Czy uczy konkretnej funkcji Copilota?**
   - ✅ DOBRZE: "Użyj @workspace do znalezienia wszystkich kontrolerów"
   - ❌ ŹLE: "Napisz kontroler" (nie uczy funkcji Copilota)
   
2. **Czy NIE ma przykładowych odpowiedzi?**
   - ✅ DOBRZE: Tylko zadanie, student sam ćwiczy
   - ❌ ŹLE: Zawiera przykładową odpowiedź Copilota
   
3. **Czy NIE dubluje się z innymi ćwiczeniami?**
   - ✅ DOBRZE: Unikalna funkcja/kontekst
   - ❌ ŹLE: To samo co w innym module
   
4. **Czy ma wartość praktyczną?**
   - ✅ DOBRZE: Rzeczywisty problem, który student napotka
   - ❌ ŹLE: Sztuczny przykład bez sensu
   
5. **Czy jest na odpowiednim poziomie?**
   - ✅ DOBRZE: Pasuje do poziomu modułu (BEGINNER/INTERMEDIATE/ADVANCED)
   - ❌ ŹLE: Za łatwe lub za trudne
   
6. **Czy jest konkretne?**
   - ✅ DOBRZE: "Zmień nazwę kolumny 'name' na 'treasure_name' w TreasureEntity"
   - ❌ ŹLE: "Zrefaktoruj kod" (zbyt ogólne)
   
7. **Czy fokusuje się na funkcji, nie na projekcie?**
   - ✅ DOBRZE: Małe, konkretne zadanie pokazujące funkcję
   - ❌ ŹLE: "Stwórz cały projekt" (za duże)

**CZERWONE FLAGI (automatyczna ocena < 5.0):**
- ❌ Zawiera przykładową odpowiedź Copilota
- ❌ Nie wymienia konkretnej funkcji Copilota (@workspace, Edit Mode, etc.)
- ❌ Dubluje się z innym ćwiczeniem
- ❌ Generuje cały projekt zamiast małego przykładu
- ❌ Pisze oczywistości ("Copilot pomoże Ci...")
- ❌ **Używa tych samych klas co poprzednie moduły** (np. InsurancePolicy w module 4, 5, 6)
- ❌ **Brak różnorodności domen** (wszystko o ubezpieczeniach/bankach/etc.)

**ZIELONE FLAGI (automatyczna ocena > 8.0):**
- ✅ Konkretna funkcja Copilota w nazwie zadania
- ✅ Małe, fokusowane zadanie
- ✅ Praktyczny problem
- ✅ Jasne kroki do wykonania
- ✅ Brak przykładowych odpowiedzi

**OCENA:**
- Score: 1.0-10.0 (8.0+ = approved)
- Feedback: Szczegółowa ocena z uzasadnieniem
- Issues: Lista konkretnych problemów
- Strengths: Co jest dobre
- Suggestions: Jak ulepszyć

**PRZYKŁAD DOBREGO ĆWICZENIA:**
```
Zadanie: Użyj @workspace do znalezienia wszystkich kontrolerów

Kroki:
1. Otwórz Copilot Chat
2. Wpisz: "@workspace Pokaż wszystkie klasy z adnotacją @RestController"
3. Przeanalizuj wyniki
4. Zapytaj: "Który kontroler obsługuje endpoint /api/treasures?"

Oczekiwany rezultat: Student nauczy się używać @workspace do nawigacji po projekcie.
```

**PRZYKŁAD ZŁEGO ĆWICZENIA:**
```
Zadanie: Stwórz kontroler

Kroki:
1. Stwórz nową klasę TreasureController
2. Dodaj adnotację @RestController
3. Napisz metodę getTreasures()

Przykładowa odpowiedź Copilota:
@RestController
public class TreasureController {
    @GetMapping("/treasures")
    public List<Treasure> getTreasures() { ... }
}
```
❌ Problemy: Nie uczy funkcji Copilota, zawiera przykładową odpowiedź, za ogólne.

**BĄDŹ SUROWY!** To Masterclass - wymagaj wysokiej wartości szkoleniowej.
"""

    return LlmAgent(
        model=model,
        name="TrainingValueCritic",
        description="Reviews training exercises for educational value with high common sense",
        instruction=instruction,
        output_key="training_critique",
        output_schema=TrainingValueCritique
        # temperature NIE jest dozwolony w LlmAgent (Pydantic extra='forbid')
        # Model używa domyślnych ustawień (optymalne dla krytyki)
    )

