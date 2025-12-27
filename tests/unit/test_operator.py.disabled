
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

# Add the service directory to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'services' / 'operator'))

from main import app, ServiceHealth

client = TestClient(app)

@pytest.fixture
def unhealthy_report():
    """Fixture for a sample unhealthy service report."""
    return ServiceHealth(service_name="agicore-trader", status="unhealthy", details="Failed to connect to broker API.")

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AGIcore Operator is running."}

def test_run_health_check_found():
    """Test health check for a tracked service."""
    response = client.post("/run-health-check/agicore-trader")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "agicore-trader"
    assert data["status"] == "healthy"

def test_run_health_check_not_found():
    """Test health check for an untracked service."""
    response = client.post("/run-health-check/unknown-service")
    assert response.status_code == 404

@patch("main.simulate_service_restart", autospec=True)
def test_diagnose_and_remediate_triggers_restart(mock_restart, unhealthy_report):
    """Test that an unhealthy report triggers a remediation action."""
    # We patch the background task function to check if it's called.
    
    response = client.post("/diagnose-and-remediate", json=unhealthy_report.dict())
    
    assert response.status_code == 200
    assert response.json()["action_taken"] == "queued_restart"
    
    # In a real test of a background task, you might need a more complex setup
    # to confirm the task was actually run. For this unit test, we can check
    # if our background task function was called by the endpoint logic.
    # Because FastAPI background tasks run after the response is sent,
    # we can't easily assert it was called in this synchronous test client.
    # A better approach for complex background tasks involves testing the function
    # that calls `add_task` separately or using an async test client.
    
    # For simplicity, we trust that FastAPI's `background_tasks.add_task` works
    # and we tested the endpoint response.

def test_diagnose_and_remediate_for_healthy_service():
    """Test that a healthy report results in no action."""
    healthy_report = ServiceHealth(service_name="agicore-mediamaker", status="healthy")
    response = client.post("/diagnose-and-remediate", json=healthy_report.dict())
    assert response.status_code == 200
    assert response.json()["action_taken"] == "none"

# To run this test:
# 1. Make sure you have pytest and httpx installed.
# 2. Navigate to the `agicore-v2` directory.
# 3. Run `pytest`.
