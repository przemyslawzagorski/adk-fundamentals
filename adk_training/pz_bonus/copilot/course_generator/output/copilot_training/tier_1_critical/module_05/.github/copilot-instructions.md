# Instrukcje dla GitHub Copilot - Inżynieria Kontekstu i Promptów

Ten dokument zawiera ogólne wytyczne dla GitHub Copilot, które mają pomóc w utrzymaniu spójności i jakości kodu w projekcie, a także w efektywnym wykorzystywaniu Copilota w kontekście inżynierii promptów.

## Ogólne wytyczne:

1.  **Język i styl kodowania:** Preferowany język to Java (wersja 17+). Stosuj konwencje kodowania Spring Boot. Pisz czysty, czytelny kod z wyraźnymi nazwami zmiennych i metod.
2.  **Komentarze:** Generuj komentarze Javadoc dla klas, interfejsów i metod publicznych. Komentarze powinny jasno opisywać przeznaczenie, parametry i zwracane wartości.
3.  **Testy:** Podczas generowania testów, preferuj JUnit 5 i Mockito. Skup się na pokryciu kodu i scenariuszach brzegowych.
4.  **Bezpieczeństwo:** Zawsze zwracaj uwagę na potencjalne luki bezpieczeństwa (np. SQL injection, XSS) i staraj się generować bezpieczny kod.
5.  **Wydajność:** Proponuj rozwiązania, które są wydajne i skalowalne, zwłaszcza w kontekście operacji bazodanowych i przetwarzania kolekcji.
6.  **Wzorce projektowe:** Stosuj odpowiednie wzorce projektowe, gdy jest to uzasadnione (np. Factory, Builder, Strategy).

## Wytyczne dotyczące inżynierii kontekstu i promptów:

1.  **Preferuj precyzję:** Zawsze, gdy to możliwe, ograniczaj kontekst do minimum niezbędnego do wykonania zadania (np. używaj `#file` lub zaznaczaj konkretne fragmenty kodu).
2.  **Używaj `@workspace` rozsądnie:** Tylko wtedy, gdy zadanie wymaga analizy zależności między wieloma plikami lub globalnej perspektywy (np. generowanie dokumentacji architektury, refaktoring całej warstwy).
3.  **Formułuj jasne prompty:** Zawsze staraj się formułować prompty w sposób jasny, precyzyjny i jednoznaczny. Określ cel, oczekiwany format wyjściowy i wszelkie ograniczenia.
4.  **Iteruj prompty:** Traktuj tworzenie promptów jako proces iteracyjny. Jeśli pierwsza sugestia Copilota nie jest idealna, zmodyfikuj prompt, dodając więcej szczegółów lub zmieniając podejście.
5.  **Uwzględniaj "token window":** Bądź świadomy ograniczeń kontekstowych modelu. Unikaj zbyt długich promptów lub niepotrzebnie szerokiego kontekstu, które mogą obniżyć jakość sugestii.
6.  **Wykorzystuj role:** Czasami pomocne jest nadanie Copilotowi roli w prompcie, np. "Jako doświadczony programista Spring Boot...", aby ukierunkować styl i perspektywę generowanego kodu.

## Przykłady przydatnych promptów (do wykorzystania w Copilot Chat lub jako komentarz):

-   `// Generuj testy jednostkowe dla tej klasy, używając JUnit 5 i Mockito.`
-   `// Refaktoryzuj tę metodę, aby używała Java Stream API.`
-   `// Wyjaśnij działanie tej funkcji, skupiając się na logice biznesowej.`
-   `// Stwórz adnotacje Swagger/OpenAPI dla tego endpointu.`
-   `// Zoptymalizuj ten fragment kodu pod kątem wydajności.`
-   `// Zmień tę klasę na rekord Java (Java 17).`

--- 

*Pamiętaj, że Copilot jest narzędziem wspomagającym. Zawsze weryfikuj generowany kod i upewnij się, że spełnia on wszystkie wymagania projektu.*