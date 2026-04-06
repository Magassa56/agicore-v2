
import os
import json
from google.cloud import pubsub_v1

# --- Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TRADE_SIGNALS_TOPIC = os.getenv("TRADE_SIGNALS_TOPIC", "trade-signals")

def publish_signal():
    """Publishes a sample trade signal to the Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, TRADE_SIGNALS_TOPIC)

    # Create a sample signal
    signal_data = {
        "ticker": "AAPL",
        "action": "buy",
        "confidence": 0.85,
        "quantity": 10,
        "order_type": "limit",
        "price": 150.00
    }

    # Convert to JSON and then to bytes
    message_data = json.dumps(signal_data).encode("utf-8")

    # Publish the message
    future = publisher.publish(topic_path, message_data)
    print(f"Published message ID: {future.result()}")

if __name__ == "__main__":
    if not GCP_PROJECT_ID:
        print("GCP_PROJECT_ID environment variable not set.")
    else:
        publish_signal()
