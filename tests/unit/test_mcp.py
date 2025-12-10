
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the service directory to the Python path to allow imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'services' / 'agicore-mcp'))

# Now import the app
from main import app

client = TestClient(app)

@pytest.fixture
def goal_payload():
    """Fixture for a sample goal payload."""
    return {"description": "Analyze market trends for NVDA", "constraints": ["Use public data only"]}

def test_root_endpoint():
    """Test the root endpoint to ensure the service is running."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AGIcore Multi-Cognitive Planner (MCP) is running."}

def test_create_plan_success(goal_payload):
    """Test the /create-plan endpoint for a successful plan generation."""
    response = client.post("/create-plan", json=goal_payload)
    assert response.status_code == 200
    plan = response.json()
    assert plan["id"] == "plan_001"
    assert plan["status"] == "pending"
    assert len(plan["steps"]) > 0
    assert plan["steps"][0]["service"] == "agicore-analytics"

def test_execute_plan_success():
    """Test the /execute-plan endpoint for a known plan."""
    # This test simulates the execution flow. In a real scenario, you'd mock the HTTP calls.
    with patch('asyncio.sleep', new_callable=MagicMock) as mock_sleep:
        response = client.post("/execute-plan/plan_001")
        assert response.status_code == 200
        assert response.json() == {"plan_id": "plan_001", "status": "completed"}

def test_execute_plan_not_found():
    """Test the /execute-plan endpoint with a non-existent plan ID."""
    response = client.post("/execute-plan/plan_999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Plan not found"}

# To run this test:
# 1. Make sure you have pytest and httpx installed (`pip install pytest httpx`).
# 2. Navigate to the `agicore-v2` directory.
# 3. Run `pytest`.
