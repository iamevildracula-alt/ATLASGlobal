#!/bin/bash

# ATLASGlobal AI - Manual Deployment Script
# Requirements: gcloud CLI installed and authenticated

PROJECT_ID=$(gcloud config get-value project)
APP_NAME="atlas-global-core"
REGION="us-central1"

echo "🚀 Deploying ATLASGlobal AI to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# 1. Build and Submit Image
echo "📦 Building Container Image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME .

# 2. Deploy to Cloud Run
echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $APP_NAME \
  --image gcr.io/$PROJECT_ID/$APP_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000

echo "✅ Deployment Complete!"
echo "Your Sentient Grid is live."
