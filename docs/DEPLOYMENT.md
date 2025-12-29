# AGIcore Deployment Guide

This document provides instructions for deploying and validating the AGIcore services on Google Cloud Run.

## Prerequisites

- Google Cloud SDK (`gcloud`) installed and authenticated.
- You have been granted the necessary IAM permissions in the `ace-forest-420208` GCP project.
- The required secrets (e.g., `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`) have been created in Google Secret Manager.

## CI/CD Workflow

The CI/CD pipeline is defined in `.github/workflows/main-ci-cd.yml`. It is triggered on every push to the `main` branch.

The workflow automatically builds and deploys the `operator` and `trader-agent` services that have been modified in the commit.

### Required GitHub Actions Variables

The following variables must be configured in the GitHub repository's Actions secrets and variables settings:

- **Secrets:**
  - `GCP_SA_KEY`: The JSON service account key for a service account with permissions to deploy to Cloud Run and access Artifact Registry and Secret Manager.
- **Variables:**
  - `GCP_PROJECT_ID`: `ace-forest-420208`
  - `GCP_REGION`: `europe-west1`
  - `GAR_REPOSITORY`: `bama`
  - `GCP_RUN_SERVICE_ACCOUNT`: The email address of the Cloud Run runtime service account.

## Manual Deployment & Validation

### Deploying a Service

To manually deploy a service, use the following `gcloud` command. Replace `[SERVICE_NAME]` with the name of the service (`operator` or `agicore-trader`) and `[IMAGE_TAG]` with the desired image tag from the `bama` Artifact Registry.

```bash
gcloud run deploy [SERVICE_NAME] \
  --image europe-west1-docker.pkg.dev/ace-forest-420208/bama/[SERVICE_NAME]:[IMAGE_TAG] \
  --region europe-west1 \
  --project ace-forest-420208
```

### Injecting Secrets

To update a service with secrets from Secret Manager, use the following commands.

**1. Grant Secret Accessor Role:**

First, grant the Cloud Run service's identity the `Secret Manager Secret Accessor` role for each secret.

```bash
# Example for the trader-agent and ALPACA_API_KEY
GCP_PROJECT_ID="ace-forest-420208"
REGION="europe-west1"
SERVICE_NAME="trader-agent"
SECRET_NAME="ALPACA_API_KEY"

SERVICE_ACCOUNT=$(gcloud run services describe $SERVICE_NAME --region $REGION --project $GCP_PROJECT_ID --format 'value(spec.template.spec.serviceAccountName)')

gcloud secrets add-iam-policy-binding $SECRET_NAME \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/secretmanager.secretAccessor" \
  --project $GCP_PROJECT_ID
```

**2. Update Service with Secrets:**

Then, deploy a new revision of the service, mapping the secrets to environment variables.

```bash
# Example for the trader-agent
gcloud run deploy trader-agent \
  --region europe-west1 \
  --project ace-forest-420208 \
  --update-secrets=ALPACA_API_KEY=ALPACA_API_KEY:latest,ALPACA_SECRET_KEY=ALPACA_SECRET_KEY:latest
```

### Validation Commands

To validate that a service is running correctly, you can use the following commands.

**1. Get Service URL:**

```bash
SERVICE_URL=$(gcloud run services describe [SERVICE_NAME] --region europe-west1 --project ace-forest-420208 --format 'value(status.url)')
echo "Service URL: $SERVICE_URL"
```

**2. Run Smoke Tests:**

```bash
# For the operator service
curl -f "$SERVICE_URL/"
curl -f "$SERVICE_URL/health"

# For the trader-agent service
curl -f "$SERVICE_URL/"
curl -f "$SERVICE_URL/health"
```

A successful smoke test will return a 200 status code and the service's welcome message or health status. The `-f` flag will cause `curl` to exit with an error if the server returns an HTTP status code of 400 or higher.