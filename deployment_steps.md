
# Deployment Steps

## 1. Prerequisites

- A Google Cloud project with the Pub/Sub API enabled.
- An Alpaca paper trading account.
- Python 3.10 or later.
- The `gcloud` CLI installed and configured.

## 2. Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-repo/agicore.git
    cd agicore
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r services/execution_agent/requirements.txt
    ```

3.  **Set up environment variables:**

    Create a `.env` file in the root directory and add the following:

    ```
    GCP_PROJECT_ID="your-gcp-project-id"
    TRADE_SIGNALS_TOPIC="trade-signals"
    ```

4.  **Set up Alpaca API credentials:**

    Store your Alpaca API key ID and secret key in Google Cloud Secret Manager with the names `alpaca_api_key_id` and `alpaca_secret_key`.

5.  **Create the Pub/Sub topic and subscription:**

    ```bash
    gcloud pubsub topics create trade-signals
    gcloud pubsub subscriptions create execution-agent-sub --topic=trade-signals
    ```

## 3. Running the System

1.  **Start the execution agent:**

    ```bash
    uvicorn services.execution_agent.main:app --host 0.0.0.0 --port 8000
    ```

2.  **Publish a test signal:**

    In a separate terminal, run the following command:

    ```bash
    python services/execution_agent/publisher.py
    ```

## 4. Monitoring

-   **View the logs:**

    The execution agent will print logs to the console. You can also view them in the GCP Logging console.

-   **View the trades:**

    You can view the executed trades in your Alpaca paper trading account.

## 5. Kill Switch

To activate the kill switch, create a secret in Google Cloud Secret Manager with the name `kill_switch` and the value `true`. The execution agent will check the value of this secret before executing a trade.
