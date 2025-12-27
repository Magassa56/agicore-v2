#!/bin/bash
# Fail on any error, undefined variable, or pipe failure
set -euo pipefail

# --- Configuration & Validation ---
# These variables are provided by the GitHub Actions workflow environment.
if [ -z "${GCP_PROJECT_ID:-}" ]; then echo "::error:: Required env var GCP_PROJECT_ID is not set." && exit 1; fi
if [ -z "${GCP_REGION:-}" ]; then echo "::error:: Required env var GCP_REGION is not set." && exit 1; fi
if [ -z "${GAR_REPOSITORY:-}" ]; then echo "::error:: Required env var GAR_REPOSITORY is not set." && exit 1; fi
if [ -z "${DOCKER_IMAGE_NAME:-}" ]; then echo "::error:: Required env var DOCKER_IMAGE_NAME (the image to build) is not set." && exit 1; fi
if [ -z "${CLOUD_RUN_SERVICE:-}" ]; then echo "::error:: Required env var CLOUD_RUN_SERVICE (the service to deploy) is not set." && exit 1; fi
IMAGE_TAG=${IMAGE_TAG:-$(echo "$GITHUB_SHA" | cut -c1-12)}
if [ -z "${IMAGE_TAG:-}" ]; then echo "::error:: IMAGE_TAG could not be determined." && exit 1; fi

# --- Path and Name Configuration ---
# The source directory for the Docker build is based on DOCKER_IMAGE_NAME
SERVICE_SOURCE_DIR="services/${DOCKER_IMAGE_NAME}"
# The target Cloud Run service is defined by CLOUD_RUN_SERVICE
CLOUD_RUN_SERVICE_NAME_LOWER=$(echo "${CLOUD_RUN_SERVICE}" | tr '[:upper:]' '[:lower:]')
# The image in Artifact Registry is named after DOCKER_IMAGE_NAME
DOCKER_IMAGE_NAME_LOWER=$(echo "${DOCKER_IMAGE_NAME}" | tr '[:upper:]' '[:lower:]')
IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${DOCKER_IMAGE_NAME_LOWER}:${IMAGE_TAG}"

# Validate that the source directory for the build exists
if [ ! -d "${SERVICE_SOURCE_DIR}" ] || [ ! -f "${SERVICE_SOURCE_DIR}/Dockerfile" ]; then
  echo "::error:: Docker build source directory or Dockerfile not found for '${DOCKER_IMAGE_NAME}' at path '${SERVICE_SOURCE_DIR}'."
  exit 1
fi

# --- 1. Build and Push ---
echo "--- Building and Pushing Image ---"
echo "Source Directory: ${SERVICE_SOURCE_DIR}"
echo "Image URL: ${IMAGE_URL}"

DOCKER_BUILDKIT=1 docker build -t "${IMAGE_URL}" "${SERVICE_SOURCE_DIR}"
docker push "${IMAGE_URL}"

echo "✅ Image built and pushed successfully."

# --- 2. Deploy to Cloud Run ---
echo "--- Deploying to Cloud Run ---"
echo "Service: ${CLOUD_RUN_SERVICE_NAME_LOWER}"
echo "Image: ${IMAGE_URL}"

DEPLOY_CMD=(gcloud run deploy "${CLOUD_RUN_SERVICE_NAME_LOWER}"
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

SERVICE_URL=$(gcloud run services describe "${CLOUD_RUN_SERVICE_NAME_LOWER}" --platform managed --region "${GCP_REGION}" --format 'value(status.url)')
echo "✅ Deployment successful. Service available at: ${SERVICE_URL}"
