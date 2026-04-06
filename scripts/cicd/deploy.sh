#!/bin/bash
set -euo pipefail

# --- Configuration & Validation ---
if [ -z "${GCP_PROJECT_ID:-}" ]; then echo "::error:: Required env var GCP_PROJECT_ID is not set." && exit 1; fi
if [ -z "${GCP_REGION:-}" ]; then echo "::error:: Required env var GCP_REGION is not set." && exit 1; fi
if [ -z "${CLOUD_RUN_SERVICE:-}" ]; then echo "::error:: Required env var CLOUD_RUN_SERVICE (the service to deploy) is not set." && exit 1; fi
if [ -z "${IMAGE_URL:-}" ]; then echo "::error:: Required env var IMAGE_URL is not set." && exit 1; fi

# --- Deploy to Cloud Run ---
echo "--- Deploying to Cloud Run ---"
echo "Service: ${CLOUD_RUN_SERVICE}"
echo "Image: ${IMAGE_URL}"

DEPLOY_CMD=(gcloud run deploy "${CLOUD_RUN_SERVICE}"
  --image "${IMAGE_URL}"
  --region "${GCP_REGION}"
  --project "${GCP_PROJECT_ID}"
  --platform "managed"
  --quiet
  --allow-unauthenticated
)

# Conditionally add the runtime service account
if [ -n "${GCP_RUN_SERVICE_ACCOUNT:-}" ]; then
  echo "Using runtime service account: ${GCP_RUN_SERVICE_ACCOUNT}"
  DEPLOY_CMD+=(--service-account="${GCP_RUN_SERVICE_ACCOUNT}")
fi

# Execute the deploy command
"${DEPLOY_CMD[@]}"

SERVICE_URL=$(gcloud run services describe "${CLOUD_RUN_SERVICE}" --platform managed --region "${GCP_REGION}" --project "${GCP_PROJECT_ID}" --format 'value(status.url)')
echo "✅ Deployment successful. Service available at: ${SERVICE_URL}"
echo "::set-output name=service_url::${SERVICE_URL}"
