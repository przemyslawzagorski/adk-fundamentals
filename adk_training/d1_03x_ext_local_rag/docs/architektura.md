# Architektura systemu TechCorp - Dokumentacja techniczna

## Przegląd

System TechCorp to platforma e-commerce oparta na architekturze mikroserwisów,
wdrożona na Google Kubernetes Engine (GKE) w regionie europe-west1 (Belgia).

## Stack technologiczny

| Warstwa | Technologia |
|---------|-------------|
| Frontend | React 18 + TypeScript + Next.js 14 |
| API Gateway | Kong Gateway (self-hosted) |
| Backend | Java 21 + Spring Boot 3.3 / Python 3.12 + FastAPI |
| Baza danych | PostgreSQL 16 (Cloud SQL), Redis 7 (Memorystore) |
| Kolejki | Google Pub/Sub |
| Wyszukiwarka | Elasticsearch 8.12 |
| Monitoring | Grafana + Prometheus + Google Cloud Monitoring |
| CI/CD | Jenkins + ArgoCD + Terraform |
| Konteneryzacja | Docker + GKE (Kubernetes 1.29) |

## Mikroserwisy

### 1. user-service (Java)
- Zarządzanie użytkownikami i autentykacja
- Port: 8080
- Baza: `techcorp_users` (Cloud SQL)
- Repozytorum: `github.com/techcorp/user-service`

### 2. product-service (Java)
- Katalog produktów, wyszukiwanie, rekomendacje
- Port: 8081
- Baza: `techcorp_products` (Cloud SQL) + Elasticsearch
- Repozytorum: `github.com/techcorp/product-service`

### 3. order-service (Python)
- Obsługa zamówień, koszyk, płatności
- Port: 8082
- Baza: `techcorp_orders` (Cloud SQL)
- Integracja: Stripe (płatności), DHL/InPost (wysyłka)

### 4. notification-service (Python)
- Powiadomienia email, SMS, push
- Port: 8083
- Pub/Sub topic: `notifications`
- SendGrid (email), Twilio (SMS), Firebase (push)

### 5. analytics-service (Python)
- Zbieranie i analiza danych biznesowych
- Port: 8084
- BigQuery jako warehouse
- Looker Studio dashboardy

## Środowiska

| Środowisko | Cluster | Namespace | URL |
|------------|---------|-----------|-----|
| Dev | dev-eu-west1 | default | dev.techcorp.pl |
| Staging | staging-eu-west1 | staging | staging.techcorp.pl |
| Produkcja | prod-eu-west1 | production | www.techcorp.pl |

## SLA i limity

- Dostępność: 99.9% (max 8h downtime/rok)
- Latency P99: < 500ms
- RPS (requests per second): do 10,000
- Autoscaling: 2-50 podów per serwis
