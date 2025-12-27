#!/bin/bash
# Fail on any error, undefined variable, or pipe failure
set -euo pipefail

# --- Configuration & Validation ---
# These variables are expected to be set by the CI/CD environment.
# GITHUB_SHA is automatically provided by GitHub Actions.

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
# Use IMAGE_TAG from env, fallback to a truncated GITHUB_SHA if not set.
IMAGE_TAG=${IMAGE_TAG:-$(echo "$GITHUB_SHA" | cut -c1-12)}
if [ -z "${IMAGE_TAG:-}" ]; then
  echo "::error:: IMAGE_TAG could not be determined. Set IMAGE_TAG or ensure GITHUB_SHA is available."
  exit 1
fi

SERVICES_DIR="services"

# --- Main Build Loop ---
echo "--- Building AGIcore Service Images ---"
echo "Project: ${GCP_PROJECT_ID}, Region: ${GCP_REGION}, Repo: ${GAR_REPOSITORY}, Tag: ${IMAGE_TAG}"

# Find all directories inside SERVICES_DIR that contain a Dockerfile
# Use a while loop to handle spaces or special characters in paths safely.
find "${SERVICES_DIR}" -mindepth 2 -maxdepth 2 -type f -name "Dockerfile" -print0 | while IFS= read -r -d '' dockerfile_path; do
  SERVICE_PATH=$(dirname "${dockerfile_path}")
  SERVICE_NAME=$(basename "${SERVICE_PATH}")
  
  # Ensure image name is lowercase, as required by Docker and GAR
  IMAGE_NAME_LOWER=$(echo "${SERVICE_NAME}" | tr '[:upper:]' '[:lower:]')
  IMAGE_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${IMAGE_NAME_LOWER}:${IMAGE_TAG}"

  echo "-----------------------------------------"
  echo "Building image for service: ${SERVICE_NAME}"
  echo "Image URL: ${IMAGE_URL}"
  echo "-----------------------------------------"

  # Use Docker BuildKit for faster builds
  DOCKER_BUILDKIT=1 docker build -t "${IMAGE_URL}" "${SERVICE_PATH}"
  
  echo "Pushing image: ${IMAGE_URL}"
  docker push "${IMAGE_URL}"
done

echo "--- All service images built and pushed successfully! ---"
