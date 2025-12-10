#!/bin/bash

# This script builds the Docker images for all AGIcore microservices.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Google Cloud Project ID and Artifact Registry location.
# Replace with your actual values.
GCP_PROJECT_ID="your-gcp-project-id"
GCP_REGION="us-central1"
ARTIFACT_REGISTRY_REPO="agicore-repo"

# Base directory for services
SERVICES_DIR="../services"

# Get a list of all service directories
SERVICES=$(ls -d ${SERVICES_DIR}/*/ | xargs -n 1 basename)

echo "--- Building AGIcore Service Images ---"
echo "Services to build: ${SERVICES}"

# --- Main Build Loop ---
for SERVICE in ${SERVICES}; do
  SERVICE_PATH="${SERVICES_DIR}/${SERVICE}"
  IMAGE_NAME=$(echo "${SERVICE}" | tr '[:upper:]' '[:lower:]') # Ensure image name is lowercase
  IMAGE_TAG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${IMAGE_NAME}:latest"

  echo "-----------------------------------------"
  echo "Building image for service: ${SERVICE}"
  echo "Image Path: ${SERVICE_PATH}"
  echo "Image Tag: ${IMAGE_TAG}"
  echo "-----------------------------------------"

  # Use Docker BuildKit for faster builds
  DOCKER_BUILDKIT=1 docker build -t "${IMAGE_TAG}" "${SERVICE_PATH}"

  # To push the image after building, uncomment the following lines:
  # echo "Pushing image: ${IMAGE_TAG}"
  # docker push "${IMAGE_TAG}"
done

echo "--- All service images built successfully! ---"
echo "To push the images, configure authentication with 'gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev' and uncomment the 'docker push' lines in this script."

