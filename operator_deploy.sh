#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="ace-forest-420208"
REGION="europe-west1"
SERVICE="trader-agent"
IMAGE="europe-west1-docker.pkg.dev/ace-forest-420208/agicore/trader-agent:latest"

SECRET_API="alpaca-api-key"
SECRET_SECRET="alpaca-secret-key"

echo "== AGIcore OperatorDeploy =="

echo "[1] Set project & region"
gcloud config set project "$PROJECT_ID" >/dev/null
gcloud config set run/region "$REGION" >/dev/null

echo "[2] Check secrets exist"
gcloud secrets describe "$SECRET_API" >/dev/null
gcloud secrets describe "$SECRET_SECRET" >/dev/null

echo "[3] Check secret versions"
gcloud secrets versions list "$SECRET_API" --limit=1 >/dev/null
gcloud secrets versions list "$SECRET_SECRET" --limit=1 >/dev/null

echo "[4] Deploy Cloud Run"
gcloud run deploy "$SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --set-secrets="ALPACA_API_KEY=$SECRET_API:latest,ALPACA_SECRET_KEY=$SECRET_SECRET:latest"

echo "[5] Service URL"
gcloud run services describe "$SERVICE" \
  --region="$REGION" \
  --format="value(status.url)"
