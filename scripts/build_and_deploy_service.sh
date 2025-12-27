#!/bin/bash
# Fail on any error, undefined variable, or pipe failure
set -euo pipefail

# --- Configuration & Validation ---
# These variables are expected to be set by the CI/CD environment.
if [ -z "${GCP_PROJECT_ID:-}" ]; then echo "::error:: Required env var GCP_PROJECT_ID is not set." && exit 1; fi
if [ -z "${GCP_REGION:-}" ]; then echo "::error:: Required env var GCP_REGION is not set." && exit 1; fi
if [ -z "${GAR_REPOSITORY:-}" ]; then echo "::error:: Required env var GAR_REPOSITORY is not set." && exit 1; fi
if [ -z "${SERVICE_NAME:-}" ]; then echo "::error:: Required env var SERVICE_NAME is not set." && exit 1; fi
IMAGE_TAG=${IMAGE_TAG:-$(echo "$GITHUB_SHA" | cut -c1-12)}
if [ -z "${IMAGE_TAG:-}" ]; then echo "::error:: IMAGE_TAG could not be determined." && exit 1; fi

# --- Path and Name Configuration ---
SERVICE_DIR="services"
# The directory name must match the service name from the workflow variable
SERVICE_PATH="${SERVICE_DIR}/${SERVICE_NAME}"
# Cloud Run service names prefer hyphens
CLOUD_RUN_SERVICE_NAME=$(echo "${SERVICE_NAME}" | tr '_' '-')
# Docker image names must be lowercase
DOCKER_IMAGE_NAME=$(echo "${SERVICE_NAME}" | tr '[:upper:]' '[:lower:]')
IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${DOCKER_IMAGE_NAME}:${IMAGE_TAG}"

if [ ! -d "${SERVICE_PATH}" ] || [ ! -f "${SERVICE_PATH}/Dockerfile" ]; then
  echo "::error:: Service directory or Dockerfile not found for service '${SERVICE_NAME}' at path '${SERVICE_PATH}'."
  exit 1
fi

# --- 1. Build and Push ---
echo "--- Building and Pushing Image for ${SERVICE_NAME} ---"
echo "Image URL: ${IMAGE_URL}"
DOCKER_BUILDKIT=1 docker build -t "${IMAGE_URL}" "${SERVICE_PATH}"
docker push "${IMAGE_URL}"
echo "✅ Image built and pushed successfully."

# --- 2. Deploy to Cloud Run ---
echo "--- Deploying ${CLOUD_RUN_SERVICE_NAME} to Cloud Run ---"
# Base deploy command
DEPLOY_CMD=(gcloud run deploy "${CLOUD_RUN_SERVICE_NAME}"
  --image "${IMAGE_URL}"
  --region "${GCP_REGION}"
  --platform "managed"
  --quiet
  --allow-unauthenticated # WARNING: Publicly accessible
)
# Conditionally add the runtime service account
if [ -n "${GCP_RUN_SERVICE_ACCOUNT:-}" ]; then
  echo "Using runtime service account: ${GCP_RUN_SERVICE_ACCOUNT}"
  DEPLOY_CMD+=(--service-account="${GCP_RUN_SERVICE_ACCOUNT}")
else
  echo "Using default compute service account."
fi

# Execute the deploy command
"${DEPLOY_CMD[@]}"

SERVICE_URL=$(gcloud run services describe "${CLOUD_RUN_SERVICE_NAME}" --platform managed --region "${GCP_REGION}" --format 'value(status.url)')
echo "✅ Deployment successful. Service available at: ${SERVICE_URL}"
