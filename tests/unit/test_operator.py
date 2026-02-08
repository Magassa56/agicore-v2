import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import pybreaker
import json
import logging
from io import StringIO
import httpx
from pythonjsonlogger import jsonlogger

from services.operator.main import app, MAINTENANCE_MODE, memory_breaker, INCIDENT_COMMANDER, SECURITY_GOVERNOR

client = TestClient(app)

# --- Fixtures ---

@pytest.fixture(autouse=True)
def reset_singletons():
    """Fixture to reset stateful singletons before each test."""
    MAINTENANCE_MODE.disable()
    memory_breaker.close()
    INCIDENT_COMMANDER.critical_incident_count = 0
    # Clear handlers to avoid duplicate logs in tests
    for logger_name in ["security_audit", "incident_logger"]:
        logger_instance = logging.getLogger(logger_name)
        if logger_instance.hasHandlers():
            logger_instance.handlers.clear()

@pytest.fixture
def low_risk_alert():
    return {"source": "prometheus", "severity": "warning", "message": "Service agicore-trader is down", "details": {"service": "agicore-trader"}}

@pytest.fixture
def high_risk_alert():
    return {"source": "manual", "severity": "critical", "message": "Execute a high-frequency trade", "details": {"symbol": "BTC/USD"}}

# --- Basic Tests ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "maintenance_mode": False}

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AGIcoreManager v8 is running" in response.json()["message"]

# --- Core Logic Tests ---

@patch("services.operator.main.record_decision_event", new_callable=AsyncMock)
def test_successful_low_risk_alert(mock_record_event, low_risk_alert):
    mock_record_event.return_value = "evt-test-123"
    response = client.post("/internal/alerts", json=low_risk_alert)
    assert response.status_code == 200
    data = response.json()
    assert data["action_taken"] == "executed"
    assert data["action_plan_id"] == "plan_restart_trader"
    assert data["risk_score"] == 2.5
    assert data["memory_event_id"] == "evt-test-123"
    mock_record_event.assert_awaited_once()

def test_maintenance_mode_rejection(low_risk_alert):
    MAINTENANCE_MODE.enable()
    response = client.post("/internal/alerts", json=low_risk_alert)
    assert response.status_code == 503
    assert "maintenance mode" in response.json()["detail"]

# --- Security Governor Tests ---

@patch("fastapi.BackgroundTasks.add_task")
def test_security_governor_blocks_high_risk_plan(mock_add_task, high_risk_alert):
    # This side effect will be executed when add_task is called
    def sync_task(func, *args, **kwargs):
        import asyncio
        loop = asyncio.get_event_loop()
        task = loop.create_task(func(*args, **kwargs))
        loop.run_until_complete(task)

    mock_add_task.side_effect = sync_task

    with patch("services.operator.main.record_decision_event", new_callable=AsyncMock) as mock_record_event:
        # Temporarily set a lower risk threshold for the test
        original_threshold = SECURITY_GOVERNOR.risk_threshold
        SECURITY_GOVERNOR.risk_threshold = 7.0

        response = client.post("/internal/alerts", json=high_risk_alert)
        assert response.status_code == 403
        assert "blocked by Security Governor" in response.json()["detail"]

        # Ensure it was recorded as blocked
        mock_record_event.assert_awaited_once_with(agent="AGIcoreManager", plan=unittest.mock.ANY, status="blocked")

        SECURITY_GOVERNOR.risk_threshold = original_threshold # Restore original threshold

@patch("services.operator.main.security_logger.info")
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
def test_security_governor_flags_critical_action(mock_post, mock_security_log, high_risk_alert):
    # Set threshold high enough to not block the action
    original_threshold = SECURITY_GOVERNOR.risk_threshold
    SECURITY_GOVERNOR.risk_threshold = 9.0

    client.post("/internal/alerts", json=high_risk_alert)

    mock_security_log.assert_called_with(
        "Critical action flagged for Human-in-the-Loop.",
        extra={"plan_id": "plan_execute_trade", "risk_score": 8.0}
    )

    SECURITY_GOVERNOR.risk_threshold = original_threshold

# --- Incident and Circuit Breaker Tests ---

@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
def test_circuit_breaker_opens_and_triggers_incident(mock_post, low_risk_alert):
    mock_post.side_effect = httpx.RequestError("Connection failed")

    # Fail enough times to open the breaker and trigger maintenance mode
    for _ in range(INCIDENT_COMMANDER.threshold):
        client.post("/internal/alerts", json=low_risk_alert)

    # Next call should fail because maintenance mode is active
    response = client.post("/internal/alerts", json=low_risk_alert)
    assert response.status_code == 503
    assert "Service in maintenance mode" in response.json()["detail"]

import unittest.mock

def test_incident_commander_triggers_maintenance_mode():
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(jsonlogger.JsonFormatter())
    incident_logger = logging.getLogger("incident_logger")
    incident_logger.addHandler(handler)
    incident_logger.setLevel(logging.WARNING)

    alert = MagicMock()
    alert.model_dump.return_value = {"source": "test", "message": "Test"}
    
    for _ in range(INCIDENT_COMMANDER.threshold):
        INCIDENT_COMMANDER.record_critical_incident(alert, "Simulated incident")
    
    assert MAINTENANCE_MODE.enabled is True
    
    last_log = json.loads(log_stream.getvalue().strip().split('\n')[-1])
    assert last_log["message"] == "MAINTENANCE MODE ACTIVATED"
    
    incident_logger.removeHandler(handler)
