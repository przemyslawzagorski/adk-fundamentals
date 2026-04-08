# Analiza Bezpieczeństwa Kodu

**Instrukcja dla Copilota:**
Użytkownik zaznaczył fragment kodu lub wskazał plik/metodę i prosi o analizę potencjalnych luk w bezpieczeństwie. Twoim zadaniem jest zidentyfikowanie typowych podatności (np. SQL Injection, XSS, Path Traversal, deserializacja niezaufanych danych, słabe uwierzytelnianie/autoryzacja) oraz zaproponowanie poprawek i najlepszych praktyk.

**Kroki, które należy wykonać:**
1.  **Identyfikacja Potencjalnych Zagrożeń:** Przeskanuj kod pod kątem wzorców, które mogą prowadzić do luk w bezpieczeństwie.
2.  **Wyjaśnienie Podatności:** Dla każdej zidentyfikowanej luki, wyjaśnij, na czym polega zagrożenie i jakie są jego potencjalne konsekwencje.
3.  **Propozycja Poprawek:** Zaproponuj konkretne zmiany w kodzie, które eliminują lub minimalizują ryzyko podatności, odwołując się do sprawdzonych wzorców bezpieczeństwa (np. użycie Prepared Statements, walidacja danych wejściowych, sanitizacja wyjścia, silne mechanizmy uwierzytelniania).
4.  **Best Practices:** Podaj ogólne najlepsze praktyki w kontekście analizowanego kodu, które pomogą zapobiegać podobnym problemom w przyszłości.
5.  **Dodatkowe Zasoby (opcjonalnie):** Zasugeruj linki do dokumentacji (np. OWASP Cheat Sheet Series) w celu pogłębienia wiedzy.

**Przykład użycia:**
Zaznacz metodę, która przyjmuje dane wejściowe od użytkownika i wstawia je do zapytania SQL, a następnie poproś o analizę bezpieczeństwa.
