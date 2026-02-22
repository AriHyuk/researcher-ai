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

# 2. Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --image "$IMAGE_TAG" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,LOCATION=$REGION"

echo "✅ Deployment Successful!"
gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)'
