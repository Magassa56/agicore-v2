#!/bin/bash
set -euo pipefail

# --- Configuration & Validation ---
if [ -z "${GCP_PROJECT_ID:-}" ]; then echo "::error:: Required env var GCP_PROJECT_ID is not set." && exit 1; fi
if [ -z "${GCP_REGION:-}" ]; then echo "::error:: Required env var GCP_REGION is not set." && exit 1; fi
if [ -z "${GAR_REPOSITORY:-}" ]; then echo "::error:: Required env var GAR_REPOSITORY is not set." && exit 1; fi
if [ -z "${DOCKER_IMAGE_NAME:-}" ]; then echo "::error:: Required env var DOCKER_IMAGE_NAME (the image to build) is not set." && exit 1; fi
IMAGE_TAG=${IMAGE_TAG:-$(echo "$GITHUB_SHA" | cut -c1-12)}
if [ -z "${IMAGE_TAG:-}" ]; then echo "::error:: IMAGE_TAG could not be determined." && exit 1; fi

# --- Path and Name Configuration ---
SERVICE_SOURCE_DIR="services/${DOCKER_IMAGE_NAME}"
DOCKER_IMAGE_NAME_LOWER=$(echo "${DOCKER_IMAGE_NAME}" | tr '[:upper:]' '[:lower:]')
IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${DOCKER_IMAGE_NAME_LOWER}:${IMAGE_TAG}"

if [ ! -d "${SERVICE_SOURCE_DIR}" ] || [ ! -f "${SERVICE_SOURCE_DIR}/Dockerfile" ]; then
  echo "::error:: Docker build source directory or Dockerfile not found for '${DOCKER_IMAGE_NAME}' at path '${SERVICE_SOURCE_DIR}'."
  exit 1
fi

# --- Build and Push ---
echo "--- Building and Pushing Image ---"
echo "Source Directory: ${SERVICE_SOURCE_DIR}"
echo "Image URL: ${IMAGE_URL}"

DOCKER_BUILDKIT=1 docker build -t "${IMAGE_URL}" "${SERVICE_SOURCE_DIR}"
docker push "${IMAGE_URL}"

# Also tag and push as 'latest'
LATEST_IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${DOCKER_IMAGE_NAME_LOWER}:latest"
echo "--- Tagging and Pushing 'latest' tag ---"
echo "Latest Image URL: ${LATEST_IMAGE_URL}"
docker tag "${IMAGE_URL}" "${LATEST_IMAGE_URL}"
docker push "${LATEST_IMAGE_URL}"

echo "✅ Image built and pushed successfully."
echo "::set-output name=image_url::${IMAGE_URL}"
