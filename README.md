# AGIcore-v2: A Multi-Agent System for Autonomous Operations

AGIcore-v2 is a distributed, multi-agent system designed for autonomous task planning, execution, and self-healing. It follows a microservices architecture, where each agent is an independent, containerized service that can be deployed and scaled individually.

This system is built to be deployed on Google Cloud Run, leveraging other cloud-native services like Artifact Registry for container storage and IAM for secure operations.

## Core Concepts

- **Multi-Cognitive Planner (MCP)**: The "brain" of the system. It receives high-level goals and creates a sequence of steps (a "plan") to achieve them. It then orchestrates the execution of this plan by delegating tasks to other agents.
- **Micro-Agents**: Specialized services that perform specific tasks. Examples include `agicore-trader` (for financial operations), `agicore-mediamaker` (for content generation), and `agicore-analytics` (for data processing).
- **Operator**: The SRE (Site Reliability Engineering) agent. It monitors the health of all other agents, diagnoses problems, and performs automated remediation, such as restarting an unhealthy service. This provides an auto-healing capability to the system.
- **Tools**: A shared library of functions that agents can use to perform common actions, such as making API calls, analyzing data, or interacting with storage.

## Target Architecture

The system is designed as a set of communicating microservices, ready for deployment on a serverless container platform like Google Cloud Run.

```
[ High-Level Goal ]
       |
       v
[ agicore-mcp ]  (Creates & Executes Plan)
       |
       |--------------------------------------------------|
       |                   (Delegates Tasks)              |
       v                                                  v
[ agicore-trader ]                                 [ agicore-mediamaker ]
  (Executes Trades)                                 (Generates Images)
       |                                                  |
       v                                                  v
[ Brokerage API ]                                  [ Generative AI API ]


[ Monitoring System ] -> [ Operator ] -> (Remediates unhealthy services)
                          (Auto-Healing)
```
*(Note: This is a simplified diagram. A full architecture diagram should be generated and placed here.)*

## Project Structure

```
agicore-v2/
├── .github/workflows/      # GitHub Actions CI/CD pipeline
│   └── main-ci-cd.yml
├── services/               # Source code for all micro-agent services
│   ├── agicore-mcp/        # Multi-Cognitive Planner
│   ├── operator/           # Auto-healing SRE agent
│   ├── agicore-trader/
│   ├── agicore-mediamaker/
│   ├── agicore-analytics/
│   └── agicore-storage/
├── scripts/                # DevOps and utility scripts
│   ├── build_images.sh     # Builds all Docker images
│   ├── deploy.sh           # Deploys all services to Cloud Run
│   └── local_dev.sh        # Placeholder for local development setup
├── tests/                  # Automated tests
│   ├── unit/
│   └── integration/
├── tools/                  # Shared tools and utilities
├── pytest.ini              # Pytest configuration
├── run_all_tests.sh        # Master test runner script
└── README.md               # This file
```

## Getting Started

### Prerequisites
- Docker
- Google Cloud SDK (`gcloud`)
- Python 3.9+

### Local Development
While a full local environment is best managed with Docker Compose, you can run individual services directly.

1.  **Navigate to a service directory:**
    ```bash
    cd services/agicore-mcp
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the service:**
    ```bash
    uvicorn main:app --reload --port 8001
    ```
The service will be available at `http://127.0.0.1:8001`.

### Running Tests
To run the entire test suite:
```bash
./run_all_tests.sh
```

## Deployment

The system is designed for automated deployment via the CI/CD pipeline in `.github/workflows/main-ci-cd.yml`.

### Manual Deployment Steps

1.  **Set up Prerequisites**:
    - A Google Cloud Project.
    - An [Artifact Registry repository](https://cloud.google.com/artifact-registry/docs/docker/create-repos).
    - A [Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts) with `Artifact Registry Writer` and `Cloud Run Admin` roles.
    - Save the service account's JSON key.

2.  **Configure Scripts**:
    - Edit `scripts/build_images.sh` and `scripts/deploy.sh` to replace placeholder values (`your-gcp-project-id`, etc.) with your actual GCP configuration.

3.  **Build and Push Images**:
    - Authenticate Docker with GCP:
      ```bash
      gcloud auth configure-docker <your-gcp-region>-docker.pkg.dev
      ```
    - Run the build script:
      ```bash
      cd scripts
      ./build_images.sh
      ```
      *(You may need to uncomment the `docker push` lines in the script).*

4.  **Deploy to Cloud Run**:
    - Run the deploy script:
      ```bash
      ./deploy.sh
      ```

### CI/CD Pipeline
The included GitHub Actions workflow automates the **Test -> Build -> Deploy** process on every push to the `main` branch.

To enable it, you must configure the following secrets in your GitHub repository's settings:
- `GCP_PROJECT_ID`: Your Google Cloud project ID.
- `GCP_REGION`: The region for your services (e.g., `us-central1`).
- `GCP_SA_KEY`: The JSON key for your deployment service account.
- `GCP_RUN_SERVICE_ACCOUNT`: The email of the service account Cloud Run services will use.
