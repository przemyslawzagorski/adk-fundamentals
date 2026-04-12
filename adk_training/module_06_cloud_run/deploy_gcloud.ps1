# =============================================================================
# Module 6: Cloud Run Deployment Script - GCLOUD VERSION (PowerShell)
# =============================================================================
# This script deploys the pirate navigator agent to Cloud Run using gcloud CLI
# Uses Cloud Build to build from source automatically - no local Docker needed!
# =============================================================================

# Load environment variables from .env if it exists
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# =============================================================================
# CONFIGURATION - Modify these values for your project
# =============================================================================
$PROJECT_ID = if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "your-project-id" }
$REGION = if ($env:GOOGLE_CLOUD_LOCATION) { $env:GOOGLE_CLOUD_LOCATION } else { "us-central1" }
$SERVICE_NAME = if ($env:SERVICE_NAME) { $env:SERVICE_NAME } else { "pirate-navigator" }

Write-Host "Launching the Ship to Cloud Run with gcloud!" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host "Project:       $PROJECT_ID"
Write-Host "Region:        $REGION"
Write-Host "Service:       $SERVICE_NAME"
Write-Host "========================================"

# =============================================================================
# STEP 1: Enable required APIs
# =============================================================================
Write-Host ""
Write-Host "Step 1: Enabling required APIs..." -ForegroundColor Yellow
Write-Host ""

gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project=$PROJECT_ID

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to enable APIs. Please check your permissions." -ForegroundColor Red
    exit 1
}

# =============================================================================
# STEP 2: Configure gcloud
# =============================================================================
Write-Host ""
Write-Host "Step 2: Configuring gcloud..." -ForegroundColor Yellow
Write-Host ""

# Set the project
gcloud config set project $PROJECT_ID

# =============================================================================
# STEP 3: Deploy from source using Cloud Build
# =============================================================================
Write-Host ""
Write-Host "Step 3: Deploying from source (Cloud Build will build the image)..." -ForegroundColor Yellow
Write-Host ""

# Deploy directly from source - Cloud Build handles everything!
gcloud run deploy $SERVICE_NAME `
    --source . `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION" `
    --project=$PROJECT_ID `
    --memory=2Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=0

if ($LASTEXITCODE -ne 0) {
    Write-Host "Cloud Run deployment failed!" -ForegroundColor Red
    exit 1
}

# =============================================================================
# STEP 4: Get service URL
# =============================================================================
Write-Host ""
Write-Host "Deployment complete! Fair winds and following seas!" -ForegroundColor Green
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME `
    --region=$REGION `
    --project=$PROJECT_ID `
    --format="value(status.url)"

Write-Host "Service deployed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view service details:"
Write-Host "  gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
Write-Host ""

