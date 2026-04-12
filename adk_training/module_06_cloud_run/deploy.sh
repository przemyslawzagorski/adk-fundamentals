#!/bin/bash
# =============================================================================
# Module 6: Cloud Run Deployment Script
# =============================================================================
# This script deploys the pirate navigator agent to Cloud Run
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
APP_NAME="${APP_NAME:-pirate_navigator}"
ADK_VERSION="1.18.0"

echo "🏴‍☠️ Launching the Ship to Cloud Run!"
echo "========================================"
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"
echo "Service:  $SERVICE_NAME"
echo "App:      $APP_NAME"
echo "========================================"

# =============================================================================
# OPTION 1: Simple Deployment with ADK CLI (Recommended for training)
# =============================================================================
# The ADK CLI handles everything automatically:
# - Builds the container image
# - Pushes to Artifact Registry
# - Deploys to Cloud Run
# =============================================================================

echo ""
echo "📦 Deploying with ADK CLI..."
echo ""

adk deploy cloud_run \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --service_name="$SERVICE_NAME" \
    --app_name="$APP_NAME" \
    --with_ui \
    --adk_version="$ADK_VERSION" \
    pirate_navigator

# =============================================================================
# OPTION 2: Custom Docker Build (Advanced - uncomment to use)
# =============================================================================
# Use this when you need custom container configuration
# =============================================================================

# IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
# 
# echo "🔨 Building custom Docker image..."
# docker build \
#     --build-arg GOOGLE_CLOUD_PROJECT="$PROJECT_ID" \
#     --build-arg GOOGLE_CLOUD_LOCATION="$REGION" \
#     -t "$IMAGE_TAG" \
#     .
# 
# echo "📤 Pushing image to Container Registry..."
# docker push "$IMAGE_TAG"
# 
# echo "🚀 Deploying to Cloud Run..."
# gcloud run deploy "$SERVICE_NAME" \
#     --image="$IMAGE_TAG" \
#     --platform=managed \
#     --region="$REGION" \
#     --allow-unauthenticated \
#     --port=8000 \
#     --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=1" \
#     --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
#     --set-env-vars="GOOGLE_CLOUD_LOCATION=$REGION" \
#     --project="$PROJECT_ID"

echo ""
echo "🏴‍☠️ Deployment complete! Fair winds and following seas!"
echo ""
echo "To view your deployed service:"
echo "  gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""

