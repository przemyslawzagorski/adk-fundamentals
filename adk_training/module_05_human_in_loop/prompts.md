

# 🏴‍☠️ Scenariusze Testowe: Agent Kwatermistrz & Admirał

Poniższe scenariusze pozwalają przetestować logikę **Human-in-the-Loop** (HIL) oraz działanie funkcji **Callback** w agencie ADK. Każdy krok sprawdza inny aspekt kodu: od prostych narzędzi po blokady systemowe.

---

## 🏗️ Przygotowanie

Upewnij się, że Twój agent jest uruchomiony, a w skarbcu znajduje się początkowe **5000 dublonów**.

---

## 1. Test Bazowy: Odczyt stanu skarbca

**Cel:** Sprawdzenie, czy agent poprawnie inicjalizuje stan i korzysta z narzędzia `check_treasury_balance`.

* **Prompt:** `"Hej Kwatermistrzu, ile mamy obecnie złota w skarbcu? Czy stać nas na uzupełnienie zapasów?"`
* **Oczekiwany wynik:** Agent powinien odpowiedzieć, że w skarbcu jest 5000 dublonów, używając pirackiego slangu.

---

## 2. Test Automatyzacji: Mały wydatek (≤ 100)

**Cel:** Sprawdzenie, czy wydatki poniżej progu są zatwierdzane automatycznie bez angażowania Admirała.

* **Prompt:** `"Potrzebuję 45 dublonów na nowe liny i trochę smoły do uszczelnienia burt. Możesz to zatwierdzić?"`
* **Oczekiwany wynik:** Agent powinien potwierdzić transakcję, a stan skarbca powinien spaść o 45 dublonów.

---

## 3. Test Blokady: Duży wydatek (> 100)

**Cel:** Sprawdzenie, czy `before_model_callback` poprawnie wykrywa potrzebę zatwierdzenia.

* **Prompt:** `"Chcemy kupić nową banderę i komplet żagli za 450 dublonów. Wyślij to do realizacji."`
* **Oczekiwany wynik:** Agent powinien poinformować, że kwota przekracza jego uprawnienia i wniosek oczekuje na decyzję Admirała. (Tu uruchamia się logika `pending_approval`).

---

## 4. Test Procesu Decyzyjnego: Zatwierdzenie Admirała

**Cel:** Sprawdzenie wywołania agenta jako narzędzia (`AgentTool`) i aktualizacji stanu po decyzji.

* **Prompt:** `"Dobrze, zapytaj Admirała o te 450 dublonów na żagle. Powiedz mu, że stare są już w strzępach i nie dogonimy żadnego kupca."`
* **Oczekiwany wynik:** Agent `admiral` powinien przeanalizować powód i zwrócić `approved`. Kwatermistrz powinien wtedy potwierdzić sfinalizowanie zakupu.

---

## 5. Test Procesu Decyzyjnego: Odmowa Admirała (Veto)

**Cel:** Sprawdzenie ścieżki odrzucenia wniosku i wyświetlenia powodu (`rejection_reason`).

* **Prompt:** `"Potrzebuję 1200 dublonów na złoty posąg papugi dla kapitana. Zapytaj Admirała, czy da nam na to złoto."`
* **Oczekiwany wynik:** Admirał powinien uznać wydatek za zbędny (`rejected`). Callback powinien przechwycić tę decyzję i wyświetlić specjalny komunikat o odrzuceniu wniosku.

---

## 6. Test Graniczny: Brak środków

**Cel:** Sprawdzenie walidacji danych wewnątrz narzędzia `request_expenditure`.

* **Prompt:** `"Chcemy kupić nową fregatę za 10 000 dublonów. Załatw to szybko!"`
* **Oczekiwany wynik:** Narzędzie powinno zwrócić błąd o niewystarczających środkach, a agent powinien przekazać tę informację bez próby kontaktu z Admirałem.

---

### 💡 Wskazówki dla kursantów:

* Zwracaj uwagę na logi w konsoli (oznaczone jako `🔍 [Callback]`) – tam zobaczysz "podmaskowe" działanie agenta.
* Spróbuj oszukać Kwatermistrza i sprawdź, czy Admirał jest bardziej rygorystyczny!

---
