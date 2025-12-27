#!/bin/bash
# Fail on any error, undefined variable, or pipe failure
set -euo pipefail

# --- Configuration & Validation ---
# These variables are expected to be set by the CI/CD environment.

if [ -z "${GCP_PROJECT_ID:-}" ]; then
  echo "::error:: Required environment variable GCP_PROJECT_ID is not set."
  exit 1
fi
if [ -z "${GCP_REGION:-}" ]; then
  echo "::error:: Required environment variable GCP_REGION is not set."
  exit 1
fi
if [ -z "${GAR_REPOSITORY:-}" ]; then
  echo "::error:: Required environment variable GAR_REPOSITORY is not set."
  exit 1
fi
# The primary service to deploy, as specified in the workflow
if [ -z "${GCP_SERVICE:-}" ]; then
  echo "::error:: Required environment variable GCP_SERVICE is not set."
  exit 1
fi
# Use IMAGE_TAG from env, fallback to a truncated GITHUB_SHA if not set.
IMAGE_TAG=${IMAGE_TAG:-$(echo "$GITHUB_SHA" | cut -c1-12)}
if [ -z "${IMAGE_TAG:-}" ]; then
  echo "::error:: IMAGE_TAG could not be determined. Set IMAGE_TAG or ensure GITHUB_SHA is available."
  exit 1
fi

# --- Main Deployment Logic ---
echo "--- Deploying AGIcore Service to Cloud Run ---"
echo "Project: ${GCP_PROJECT_ID}, Region: ${GCP_REGION}"
echo "Service to deploy: ${GCP_SERVICE}"
echo "-------------------------------------------------"

# The service name might have underscores from the repo name, but Cloud Run prefers hyphens.
# This ensures consistency.
SERVICE_NAME_LOWER=$(echo "${GCP_SERVICE}" | tr '_' '-' | tr '[:upper:]' '[:lower:]')

# The image name in GAR should correspond to the service name.
# We assume the image was built using the same naming convention.
IMAGE_NAME_LOWER=$(echo "${GCP_SERVICE}" | tr '_' '-' | tr '[:upper:]' '[:lower:]')
IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${IMAGE_NAME_LOWER}:${IMAGE_TAG}"

echo "Verifying image exists: ${IMAGE_URL}"
# The `gcloud artifacts docker images describe` command will exit with a non-zero status if the image is not found.
gcloud artifacts docker images describe "${IMAGE_URL}" --quiet

echo "Deploying service: ${SERVICE_NAME_LOWER}"

# Base deploy command
DEPLOY_CMD=(gcloud run deploy "${SERVICE_NAME_LOWER}"
  --image "${IMAGE_URL}"
  --region "${GCP_REGION}"
  --platform "managed"
  --quiet
  --allow-unauthenticated # WARNING: This makes the service publicly accessible
)

# Conditionally add the runtime service account if the variable is set
if [ -n "${GCP_RUN_SERVICE_ACCOUNT:-}" ]; then
  echo "Using runtime service account: ${GCP_RUN_SERVICE_ACCOUNT}"
  DEPLOY_CMD+=(--service-account="${GCP_RUN_SERVICE_ACCOUNT}")
else
  echo "Using default compute service account."
fi

# Execute the deploy command
"${DEPLOY_CMD[@]}"

SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME_LOWER}" --platform managed --region "${GCP_REGION}" --format 'value(status.url)')
echo "✅ Deployment successful. Service available at: ${SERVICE_URL}"