# Polityka Bezpieczeństwa Informatycznego - Firma TechCorp

## 1. Zarządzanie hasłami

- Minimalna długość hasła: 12 znaków
- Wymagane: wielka litera, mała litera, cyfra, znak specjalny
- Zmiana hasła co 90 dni
- Zakaz ponownego użycia ostatnich 12 haseł
- Dwuskładnikowe uwierzytelnianie (2FA) obowiązkowe dla wszystkich pracowników

## 2. Dostęp do systemów

- Zasada najmniejszych uprawnień (Least Privilege)
- Przegląd uprawnień co kwartał
- Natychmiastowe dezaktywowanie kont po odejściu pracownika
- VPN wymagany przy pracy zdalnej
- Logowanie dostępu do systemów krytycznych

## 3. Klasyfikacja danych

| Poziom | Opis | Przykłady |
|--------|------|-----------|
| Publiczne | Dane dostępne dla wszystkich | Strona www, materiały marketingowe |
| Wewnętrzne | Tylko pracownicy | Procedury, instrukcje operacyjne |
| Poufne | Ograniczony dostęp | Dane klientów, raporty finansowe |
| Ściśle tajne | Zarząd + wyznaczone osoby | Plany strategiczne, M&A |

## 4. Reagowanie na incydenty

1. Wykrycie incydentu → zgłoszenie do SOC w ciągu 15 minut
2. Analiza wstępna → zespół CSIRT w ciągu 1 godziny
3. Eskalacja → CTO/CISO jeśli incydent krytyczny
4. Komunikacja → dział PR przygotowuje komunikat
5. Raport post-mortem → w ciągu 5 dni roboczych

## 5. Backup i odzyskiwanie

- Backup pełny: co niedzielę o 02:00
- Backup przyrostowy: codziennie o 03:00
- Retencja: 30 dni lokalnie, 1 rok w chmurze
- Test odzyskiwania: co kwartał
- RPO (Recovery Point Objective): 24 godziny
- RTO (Recovery Time Objective): 4 godziny
