#!/bin/bash
set -e

# Configuration is now expected to be in environment variables:
# GCP_PROJECT_ID, GCP_REGION, GAR_REPOSITORY

if [ -z "$GCP_PROJECT_ID" ] || [ -z "$GCP_REGION" ] || [ -z "$GAR_REPOSITORY" ]; then
  echo "::error::GCP_PROJECT_ID, GCP_REGION, and GAR_REPOSITORY must be set as environment variables."
  exit 1
fi

SERVICES_DIR="services"
# Filter out directories that don't have a Dockerfile
SERVICES=$(find "${SERVICES_DIR}" -mindepth 2 -maxdepth 2 -type f -name "Dockerfile" -print | xargs -n 1 dirname | xargs -n 1 basename)

echo "--- Building AGIcore Service Images ---"
echo "Project: ${GCP_PROJECT_ID}, Region: ${GCP_REGION}"
echo "Services to build: ${SERVICES}"

for SERVICE in ${SERVICES}; do
  # The actual path might be different depending on the project structure, adjust if needed
  # Assuming service names with hyphens are valid and need to be found
  SERVICE_PATH=$(find "${SERVICES_DIR}" -type d -name "${SERVICE}" -print -quit)

  if [ -z "${SERVICE_PATH}" ]; then
    echo "::error::Could not find directory for service ${SERVICE}"
    exit 1
  fi
  
  IMAGE_NAME=$(echo "${SERVICE}" | tr '[:upper:]' '[:lower:]')
  IMAGE_TAG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}/${IMAGE_NAME}:latest"

  echo "-----------------------------------------"
  echo "Building image for service: ${SERVICE}"
  echo "Image Tag: ${IMAGE_TAG}"
  echo "-----------------------------------------"

  DOCKER_BUILDKIT=1 docker build -t "${IMAGE_TAG}" "${SERVICE_PATH}"
  echo "Pushing image: ${IMAGE_TAG}"
  docker push "${IMAGE_TAG}"
done

echo "--- All service images built and pushed successfully! ---"