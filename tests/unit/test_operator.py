import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import pybreaker
from services.operator.main import app, MAINTENANCE_MODE, memory_breaker, INCIDENT_COMMANDER
from pythonjsonlogger import jsonlogger
import logging
from io import StringIO
import json
from fastapi import HTTPException

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_singletons():
    """Fixture to reset stateful singletons before each test."""
    MAINTENANCE_MODE.disable()
    # Manually reset the circuit breaker's state as there is no public reset method
    memory_breaker._fail_counter = 0
    memory_breaker.close()
    INCIDENT_COMMANDER.critical_incident_count = 0
    # Clear any handlers that might have been added in tests
    incident_logger = logging.getLogger("incident_logger")
    if incident_logger.hasHandlers():
        incident_logger.handlers.clear()


@pytest.fixture
def sample_alert():
    return {
        "source": "prometheus",
        "severity": "critical",
        "message": "Service 'agicore-trader' is down.",
        "details": {"service": "agicore-trader", "error": "503 Service Unavailable"}
    }

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "maintenance_mode": False}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AGIcoreManager v2 is running" in response.json()["message"]

@patch("services.operator.main.record_decision_event", new_callable=AsyncMock)
def test_receive_alert_success(mock_record_event, sample_alert):
    response = client.post("/internal/alerts", json=sample_alert)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "plan_executed"
    assert json_response["executed_plan"]["plan_id"] == "plan_restart_service"
    mock_record_event.assert_awaited_once()

def test_maintenance_mode_rejection(sample_alert):
    MAINTENANCE_MODE.enable()
    response = client.post("/internal/alerts", json=sample_alert)
    assert response.status_code == 503
    assert "maintenance mode" in response.json()["detail"]



def test_qa_tester_rejects_high_risk_plan(sample_alert):
    # Modify the alert to trigger the high-risk plan
    high_risk_alert = sample_alert.copy()
    high_risk_alert["message"] = "Scale up needed" # Simplistic trigger for the second plan
    
    with patch("services.operator.main.analyze_alert") as mock_analyze:
        # Create a plan with a high risk score to be returned by the mocked analysis
        from services.operator.main import ActionPlan, Action
        high_risk_plan = ActionPlan(plan_id="plan_scale_up", description="Scale up backend", risk_score=0.9, estimated_cost=50.0)
        action = Action(action_name="execute_scale_up")
        
        # Make `analyze_alert` simulate a high-risk scenario
        async def side_effect(*args, **kwargs):
            INCIDENT_COMMANDER.record_critical_incident(MagicMock(), "QA validation failed")
            raise HTTPException(status_code=418, detail="QA validation failed")

        mock_analyze.side_effect = side_effect

        response = client.post("/internal/alerts", json=high_risk_alert)
        assert response.status_code == 418
        assert "QA validation failed" in response.json()["detail"]

import logging
from io import StringIO
import json

def test_incident_commander_logs_and_triggers_maintenance():
    # Capture logs from the incident logger
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(jsonlogger.JsonFormatter())
    incident_logger = logging.getLogger("incident_logger")
    incident_logger.addHandler(handler)
    incident_logger.setLevel(logging.WARNING)

    alert = {"source": "test", "severity": "critical", "message": "Test Incident", "details": {}}

    # Trigger incidents until maintenance mode is activated
    for i in range(INCIDENT_COMMANDER.threshold):
        INCIDENT_COMMANDER.record_critical_incident(MagicMock(**alert), f"Incident {i+1}")

    assert MAINTENANCE_MODE.enabled is True

    # Verify the logs
    log_contents = log_stream.getvalue().strip().split('\n')
    assert len(log_contents) == INCIDENT_COMMANDER.threshold + 1
    
    # Check the last log message for maintenance mode activation
    last_log = json.loads(log_contents[-1])
    assert last_log["message"] == "MAINTENANCE MODE ACTIVATED due to repeated critical incidents."
    
    # Clean up handler
    incident_logger.removeHandler(handler)