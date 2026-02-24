#!/bin/bash

# ai-researcher // Cloud Run Deployment Script
set -e

# Default Configurations
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="ai-researcher-backend"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "🚀 Starting Deployment for $SERVICE_NAME..."

# 1. Build & Push to GCR
echo "📦 Building and Pushing Docker Image..."
gcloud builds submit --tag "$IMAGE_TAG" ./backend

# 2. Generate YAML for env vars (more robust for commas/special chars)
echo "📝 Generating env.yaml..."

# Load additional env vars from .env if exists
if [ -f "./backend/.env" ]; then
  # Strip carriage returns and export
  export $(grep -v '^#' ./backend/.env | tr -d '\r' | xargs)
fi

cat <<EOF > ./backend/env.yaml
GOOGLE_CLOUD_PROJECT: $PROJECT_ID
LOCATION: $REGION
API_KEY: $API_KEY
ALLOWED_ORIGINS: $ALLOWED_ORIGINS
EOF

echo "☁️ Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_TAG" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --env-vars-file ./backend/env.yaml

echo "✅ Deployment Successful!"
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)'
