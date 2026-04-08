# Moduł 1: Komunikacja z AI i eksploracja kodu (E-commerce / Pirate Treasure Shop)

Ten moduł stanowi wprowadzenie do tworzenia aplikacji Spring Boot w kontekście sklepu z pirackimi skarbami, z naciskiem na integrację i eksplorację kodu przy użyciu sztucznej inteligencji, w tym GitHub Copilot.

## Cel Modułu

Głównym celem modułu jest zademonstrowanie, jak efektywnie wykorzystywać narzędzia oparte na AI, takie jak GitHub Copilot, do:
*  Szybkiego generowania boilerplate kodu.
*  Pomocy w implementacji złożonych wzorców projektowych.
*  Refaktoryzacji kodu.
*  Integracji z zewnętrznymi usługami AI (symulowanymi).

## Struktura Projektu

Projekt jest zorganizowany w typowy sposób dla aplikacji Spring Boot, z podziałem na warstwy:

*   `controller`: Obsługuje żądania HTTP i zwraca odpowiedzi.
*   `service`: Zawiera logikę biznesową i koordynuje operacje.
*   `repository`: Odpowiada za dostęp do danych (Spring Data JPA).
*   `model`: Definiuje encje JPA reprezentujące skarby.
*   `dto`: Obiekty transferu danych używane między warstwami.
*   `exception`: Niestandardowe wyjątki dla obsługi błędów.

## Kluczowe Komponenty

### `TreasureController.java`
Kontroler REST udostępniający endpointy CRUD dla zarządzania skarbami. Zawiera TODO comments wskazujące miejsca na wykorzystanie Copilota do rozszerzania funkcjonalności, walidacji i refaktoryzacji.

### `TreasureService.java`
Warstwa usługowa implementująca logikę biznesową dla skarbów. Pokazuje transakcyjność i integrację z `AISuggestionService`.

### `TreasureRepository.java`
Interfejs repozytorium Spring Data JPA do operacji na encji `Treasure`.

### `Treasure.java`
Encja JPA reprezentująca skarb w bazie danych.

### `TreasureDTO.java`
Obiekt DTO do reprezentacji danych skarbu.

### `AISuggestionService.java`
Serwis symulujący komunikację z zewnętrzną usługą AI. Demonstruje, jak można by zintegrować Copilota do tworzenia bardziej zaawansowanych mechanizmów interakcji z AI, np. generowanie podpowiedzi dotyczących skarbów.

### `TreasureNotFoundException.java`
Niestandardowy wyjątek używany w przypadku braku znalezionego skarbu.

## Jak Korzystać z GitHub Copilot w Tym Module

Każdy plik zawiera komentarze `// TODO:` z konkretnymi zadaniami, które mają być wykonane przy użyciu GitHub Copilot. Skup się na:

*   **Agent Mode:** Wykorzystaj tryb agenta do złożonych refaktoryzacji i implementacji obejmujących wiele plików.
*   **`@workspace` context:** Używaj kontekstu `@workspace` do uzyskiwania bardziej trafnych sugestii od Copilota, które uwzględniają całą strukturę projektu.
*   **Self-correction loop:** Eksperymentuj z poprawianiem sugestii Copilota i obserwowaniem, jak dostosowuje się do Twoich zmian.

## Uruchomienie Projektu (przewidywane)

Ten moduł jest fragmentem większej aplikacji Spring Boot. Aby go uruchomić, należałoby:

1.  Sklonować całe repozytorium projektu.
2.  Upewnić się, że masz zainstalowaną Javę 17+ i Maven/Gradle.
3.  Skonfigurować bazę danych (np. H2, PostgreSQL) w `application.properties`/`application.yml`.
4.  Zbudować projekt (np. `mvn clean install` lub `gradle build`).
5.  Uruchomić aplikację Spring Boot.

