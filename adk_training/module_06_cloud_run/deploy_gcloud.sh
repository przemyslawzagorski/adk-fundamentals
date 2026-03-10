#!/bin/bash
# =============================================================================
# Module 6: Cloud Run Deployment Script - GCLOUD VERSION
# =============================================================================
# This script deploys the pirate navigator agent to Cloud Run using gcloud CLI
# Uses Cloud Build to build from source automatically - no local Docker needed!
# =============================================================================

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# =============================================================================
# CONFIGURATION - Modify these values for your project
# =============================================================================
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-your-project-id}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-pirate-navigator}"

echo "Launching the Ship to Cloud Run with gcloud!"
echo "========================================"
echo "Project:       $PROJECT_ID"
echo "Region:        $REGION"
echo "Service:       $SERVICE_NAME"
echo "========================================"

# =============================================================================
# STEP 1: Enable required APIs
# =============================================================================
echo ""
echo "Step 1: Enabling required APIs..."
echo ""

gcloud services enable run.googleapis.com cloudbuild.googleapis.com --project="$PROJECT_ID"

if [ $? -ne 0 ]; then
    echo "Failed to enable APIs. Please check your permissions."
    exit 1
fi

# =============================================================================
# STEP 2: Configure gcloud
# =============================================================================
echo ""
echo "Step 2: Configuring gcloud..."
echo ""

# Set the project
gcloud config set project "$PROJECT_ID"

# =============================================================================
# STEP 3: Deploy from source using Cloud Build
# =============================================================================
echo ""
echo "Step 3: Deploying from source (Cloud Build will build the image)..."
echo ""

# Deploy directly from source - Cloud Build handles everything!
gcloud run deploy "$SERVICE_NAME" \
    --source . \
    --region="$REGION" \
    --allow-unauthenticated \
    --port=8080 \
    --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
    --project="$PROJECT_ID" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=0

if [ $? -ne 0 ]; then
    echo "Cloud Run deployment failed!"
    exit 1
fi

# =============================================================================
# STEP 4: Get service URL
# =============================================================================
echo ""
echo "Deployment complete! Fair winds and following seas!"
echo ""

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format="value(status.url)")

echo "Service deployed successfully!"
echo ""
echo "Service URL: $SERVICE_URL"
echo ""
echo "To view service details:"
echo "  gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "To view logs:"
echo "  gcloud run services logs read $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""

