# 🚀 gcloud Cloud Run - Cheat Sheet

## 🔐 Autentykacja

```bash
# Zaloguj się do GCP
gcloud auth login

# Zaloguj aplikację (dla ADK/SDK)
gcloud auth application-default login

# Skonfiguruj Docker dla Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## ⚙️ Konfiguracja projektu

```bash
# Ustaw domyślny projekt
gcloud config set project YOUR-PROJECT-ID

# Ustaw domyślny region
gcloud config set run/region us-central1

# Zobacz aktualną konfigurację
gcloud config list
```

## 📦 Artifact Registry

```bash
# Utwórz repozytorium Docker
gcloud artifacts repositories create REPO-NAME \
    --repository-format=docker \
    --location=us-central1

# Lista repozytoriów
gcloud artifacts repositories list --location=us-central1

# Usuń repozytorium
gcloud artifacts repositories delete REPO-NAME --location=us-central1
```

## 🐳 Docker Build & Push

```bash
# Zbuduj obraz
docker build -t us-central1-docker.pkg.dev/PROJECT-ID/REPO/IMAGE:TAG .

# Wypchnij obraz
docker push us-central1-docker.pkg.dev/PROJECT-ID/REPO/IMAGE:TAG

# Lista obrazów w repozytorium
gcloud artifacts docker images list us-central1-docker.pkg.dev/PROJECT-ID/REPO
```

## 🚀 Cloud Run Deploy

```bash
# Podstawowy deploy
gcloud run deploy SERVICE-NAME \
    --image=IMAGE-URL \
    --region=us-central1

# Deploy z pełną konfiguracją
gcloud run deploy SERVICE-NAME \
    --image=IMAGE-URL \
    --region=us-central1 \
    --allow-unauthenticated \
    --port=8000 \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0 \
    --set-env-vars="KEY1=value1,KEY2=value2"

# Deploy ze źródła (Cloud Build)
gcloud run deploy SERVICE-NAME \
    --source=. \
    --region=us-central1
```

## 📋 Zarządzanie serwisami

```bash
# Lista serwisów
gcloud run services list

# Szczegóły serwisu
gcloud run services describe SERVICE-NAME --region=us-central1

# Pobierz URL serwisu
gcloud run services describe SERVICE-NAME \
    --region=us-central1 \
    --format="value(status.url)"

# Usuń serwis
gcloud run services delete SERVICE-NAME --region=us-central1
```

## 🔧 Update serwisu

```bash
# Zmień zmienne środowiskowe
gcloud run services update SERVICE-NAME \
    --region=us-central1 \
    --set-env-vars="NEW_KEY=new_value"

# Zmień memory/CPU
gcloud run services update SERVICE-NAME \
    --region=us-central1 \
    --memory=4Gi \
    --cpu=4

# Zmień autoscaling
gcloud run services update SERVICE-NAME \
    --region=us-central1 \
    --min-instances=1 \
    --max-instances=20
```

## 📊 Logi i monitoring

```bash
# Zobacz ostatnie logi
gcloud run services logs read SERVICE-NAME --region=us-central1

# Logi z limitem
gcloud run services logs read SERVICE-NAME \
    --region=us-central1 \
    --limit=100

# Logi w czasie rzeczywistym (tail)
gcloud run services logs tail SERVICE-NAME --region=us-central1

# Logi z filtrem
gcloud run services logs read SERVICE-NAME \
    --region=us-central1 \
    --filter="severity>=ERROR"
```

## 🔐 IAM i uprawnienia

```bash
# Zezwól na publiczny dostęp (unauthenticated)
gcloud run services add-iam-policy-binding SERVICE-NAME \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# Usuń publiczny dostęp
gcloud run services remove-iam-policy-binding SERVICE-NAME \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"

# Dodaj dostęp dla konkretnego użytkownika
gcloud run services add-iam-policy-binding SERVICE-NAME \
    --region=us-central1 \
    --member="user:email@example.com" \
    --role="roles/run.invoker"
```

## 🌐 Traffic Management

```bash
# Wyślij 100% ruchu do najnowszej rewizji
gcloud run services update-traffic SERVICE-NAME \
    --region=us-central1 \
    --to-latest

# Podziel ruch między rewizje (canary deployment)
gcloud run services update-traffic SERVICE-NAME \
    --region=us-central1 \
    --to-revisions=REVISION-1=80,REVISION-2=20

# Lista rewizji
gcloud run revisions list --service=SERVICE-NAME --region=us-central1
```

## 🔍 Debugging

```bash
# Sprawdź status deploymentu
gcloud run operations list --region=us-central1

# Szczegóły operacji
gcloud run operations describe OPERATION-ID --region=us-central1

# Testuj lokalnie przed deploymentem
docker run -p 8080:8000 \
    -e GOOGLE_CLOUD_PROJECT=PROJECT-ID \
    IMAGE-TAG
```

## 🛠️ Przydatne flagi

```bash
# --quiet, -q          # Nie pytaj o potwierdzenie
# --format=json        # Wynik w JSON
# --format=yaml        # Wynik w YAML
# --format="value(X)"  # Tylko wartość pola X
# --project=PROJECT    # Nadpisz domyślny projekt
# --region=REGION      # Nadpisz domyślny region
```

## 📝 Przykładowe zmienne środowiskowe dla ADK

```bash
--set-env-vars="\
GOOGLE_GENAI_USE_VERTEXAI=1,\
GOOGLE_CLOUD_PROJECT=your-project-id,\
GOOGLE_CLOUD_LOCATION=us-central1"
```

## 🎯 Szybki deployment (one-liner)

```bash
# Build, push i deploy w jednej komendzie
gcloud run deploy SERVICE-NAME \
    --source=. \
    --region=us-central1 \
    --allow-unauthenticated
```

## 🔗 Przydatne linki

- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [gcloud run reference](https://cloud.google.com/sdk/gcloud/reference/run)
- [Cloud Run pricing](https://cloud.google.com/run/pricing)

