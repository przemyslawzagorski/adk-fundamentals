# 🚀 Cloud Run Deployment Guide - gcloud CLI

Ten przewodnik opisuje jak wdrożyć aplikację Pirate Navigator do Google Cloud Run używając **gcloud CLI** zamiast `adk deploy`.

## 📋 Wymagania wstępne

1. **Google Cloud SDK** zainstalowany i skonfigurowany
   ```bash
   gcloud --version
   ```

2. **Projekt GCP** z włączonymi API (skrypt włączy automatycznie):
   - Cloud Run API
   - Cloud Build API

3. **Uprawnienia** w projekcie GCP:
   - `roles/run.admin` - do deploymentu Cloud Run
   - `roles/cloudbuild.builds.editor` - do budowania obrazów
   - `roles/iam.serviceAccountUser` - do używania service account

**UWAGA:** Docker **NIE** jest wymagany! Cloud Build zbuduje obraz w chmurze.

## 🔧 Konfiguracja

### 1. Edytuj plik `.env`

```bash
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### 2. Zaloguj się do GCP

```bash
gcloud auth login
gcloud auth application-default login
```

## 🚢 Deployment

### Opcja A: Użyj gotowego skryptu (ZALECANE)

Skrypt automatycznie:
- Włącza wymagane API
- Buduje obraz w Cloud Build (bez lokalnego Dockera!)
- Deployuje do Cloud Run

#### Linux/Mac/Git Bash:
```bash
chmod +x deploy_gcloud.sh
./deploy_gcloud.sh
```

#### Windows PowerShell:
```powershell
.\deploy_gcloud.ps1
```

### Opcja B: Manualne kroki (deploy from source)

#### 1. Ustaw zmienne środowiskowe

**Linux/Mac:**
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export SERVICE_NAME="pirate-navigator"
```

**Windows PowerShell:**
```powershell
$PROJECT_ID = "your-project-id"
$REGION = "us-central1"
$SERVICE_NAME = "pirate-navigator"
```

#### 2. Włącz wymagane API

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project=$PROJECT_ID
```

#### 3. Skonfiguruj gcloud

```bash
gcloud config set project $PROJECT_ID
```

#### 4. Deploy bezpośrednio ze źródeł (Cloud Build zbuduje obraz)

```bash
gcloud run deploy $SERVICE_NAME \
    --source . \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8000 \
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
    --project=$PROJECT_ID \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0
```

**Uwaga:** Flaga `--source .` powoduje, że Cloud Build automatycznie:
- Wykrywa Dockerfile w katalogu
- Buduje obraz w chmurze
- Pushuje do Artifact Registry
- Deployuje do Cloud Run

Wszystko w jednej komendzie! 🎉

## 🔍 Weryfikacja

### Sprawdź status serwisu

```bash
gcloud run services describe $SERVICE_NAME --region=$REGION
```

### Pobierz URL serwisu

```bash
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)"
```

### Zobacz logi

```bash
gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50
```

### Testuj endpoint

```bash
curl https://YOUR-SERVICE-URL/
```

## 🐛 Rozwiązywanie problemów

### Problem: "API not enabled"

**Rozwiązanie:**
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project=$PROJECT_ID
```

### Problem: "Permission denied"

**Rozwiązanie:** Sprawdź czy masz odpowiednie uprawnienia:
```bash
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --filter="bindings.members:user:$(gcloud config get-value account)"
```

### Problem: "Service deployment failed"

**Sprawdź logi:**
```bash
gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=100
```

**Sprawdź logi Cloud Build:**
```bash
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

## 📊 Różnice vs ADK Deploy

| Aspekt | `adk deploy` | `gcloud run deploy --source` |
|--------|--------------|------------------------------|
| **Prostota** | ✅ Jedna komenda | ✅ Jedna komenda |
| **Kontrola** | ❌ Ograniczona | ✅ Pełna kontrola |
| **Dockerfile** | ✅ Auto-generowany | ⚠️ Musisz dostarczyć |
| **Build** | ✅ Automatyczny | ✅ Automatyczny (Cloud Build) |
| **Registry** | ✅ Auto-tworzony | ✅ Auto-tworzony |
| **Konfiguracja** | ✅ Domyślna | ✅ Pełna customizacja |
| **Docker lokalnie** | ❌ Nie wymagany | ❌ Nie wymagany |

## 🔄 Update serwisu

Aby zaktualizować działający serwis, po prostu uruchom ponownie deployment:

```bash
./deploy_gcloud.sh
```

Lub manualnie:
```bash
gcloud run deploy $SERVICE_NAME --source . --region=$REGION
```

## 🗑️ Usuwanie serwisu

```bash
gcloud run services delete $SERVICE_NAME --region=$REGION
```

## 📚 Dodatkowe zasoby

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [gcloud run deploy Reference](https://cloud.google.com/sdk/gcloud/reference/run/deploy)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)

