#!/bin/bash

# This script deploys all AGIcore microservices to Google Cloud Run.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Google Cloud Project ID and region.
# **REPLACE WITH YOUR ACTUAL VALUES**.
GCP_PROJECT_ID="your-gcp-project-id"
GCP_REGION="us-central1"
ARTIFACT_REGISTRY_REPO="agicore-repo"

# Service account for the Cloud Run instances.
# It's recommended to use a dedicated service account with minimal permissions.
# **REPLACE WITH YOUR SERVICE ACCOUNT EMAIL**.
SERVICE_ACCOUNT="your-service-account-email@your-gcp-project-id.iam.gserviceaccount.com"

# Base directory for services
SERVICES_DIR="../services"

# --- Pre-flight Checks ---
echo "--- Starting AGIcore Deployment to Cloud Run ---"

if [[ "${GCP_PROJECT_ID}" == "your-gcp-project-id" ]]; then
    echo "ERROR: GCP_PROJECT_ID is not set. Please edit this script and replace 'your-gcp-project-id' with your actual Google Cloud Project ID."
    exit 1
fi

echo "Project: ${GCP_PROJECT_ID}"
echo "Region: ${GCP_REGION}"
echo "-------------------------------------------------"

# --- Main Deployment Loop ---
# Get a list of all service directories
SERVICES=$(ls -d ${SERVICES_DIR}/*/ | xargs -n 1 basename)

for SERVICE in ${SERVICES}; do
  SERVICE_NAME=$(echo "${SERVICE}" | tr '[:upper:]' '[:lower:]') # Cloud Run service names must be lowercase
  IMAGE_TAG="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${SERVICE_NAME}:latest"

  echo "Deploying service: ${SERVICE_NAME}"
  echo "Using image: ${IMAGE_TAG}"

  # Check if the image exists before deploying.
  # The `gcloud container images describe` command will exit with a non-zero status if the image is not found.
  echo "Verifying image exists..."
  gcloud container images describe "${IMAGE_TAG}" --quiet

  # Deploy to Cloud Run
  gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE_TAG}" \
    --region "${GCP_REGION}" \
    --platform "managed" \
    --quiet \
    --allow-unauthenticated \
    --service-account="${SERVICE_ACCOUNT}" \
    --port=8080 \
    # Add any other flags as needed, e.g., environment variables:
    # --set-env-vars="LOG_LEVEL=info"

  SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${GCP_REGION} --format 'value(status.url)')
  echo "Service ${SERVICE_NAME} deployed successfully."
  echo "URL: ${SERVICE_URL}"
  echo "-------------------------------------------------"
done

echo "--- All services deployed successfully! ---"
