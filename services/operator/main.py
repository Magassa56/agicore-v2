
import logging
import asyncio
import httpx
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger
from prometheus_fastapi_instrumentator import Instrumentator
import pybreaker

# --- Configuration & State ---

class MaintenanceMode:
    def __init__(self):
        self._enabled = False

    @property
    def enabled(self):
        return self._enabled

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

MAINTENANCE_MODE = MaintenanceMode()

# --- Logging Setup ---
# Dedicated logger for critical incidents
incident_log_path = "ops/logs/incidents.log"
os.makedirs(os.path.dirname(incident_log_path), exist_ok=True)
incident_handler = logging.FileHandler(incident_log_path)
incident_handler.setFormatter(jsonlogger.JsonFormatter())
incident_logger = logging.getLogger("incident_logger")
incident_logger.addHandler(incident_handler)
incident_logger.setLevel(logging.WARNING)

# General structured logger
logger = logging.getLogger("agicore_manager")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)


# --- Circuit Breaker for Memory Service ---
memory_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

app = FastAPI(
    title="AGIcoreManager - Meta-SRE (v2)",
    description="Orchestrates microservices with a zero-failure tolerance, auto-healing, and a cognitive feedback loop.",
    version="2.1.0"
)

# --- Prometheus Metrics ---
Instrumentator().instrument(app).expose(app)

# --- Data Models ---
class Alert(BaseModel):
    source: str
    severity: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ActionPlan(BaseModel):
    plan_id: str
    description: str
    risk_score: float = Field(..., ge=0, le=1)
    estimated_cost: float

class Action(BaseModel):
    action_name: str
    parameters: Optional[Dict[str, Any]] = None

# --- Incident Commander ---
class IncidentCommander:
    def __init__(self, threshold: int = 3):
        self.critical_incident_count = 0
        self.threshold = threshold

    def record_critical_incident(self, alert: Alert, reason: str):
        self.critical_incident_count += 1
        incident_logger.warning(
            "Critical Incident Recorded",
            extra={
                "alert": alert.model_dump(),
                "reason": reason,
                "incident_count": self.critical_incident_count
            }
        )
        if self.critical_incident_count >= self.threshold and not MAINTENANCE_MODE.enabled:
            MAINTENANCE_MODE.enable()
            incident_logger.critical("MAINTENANCE MODE ACTIVATED due to repeated critical incidents.")

INCIDENT_COMMANDER = IncidentCommander()

# --- Memory Service Integration (with Circuit Breaker) ---
@memory_breaker
async def record_decision_event(agent: str, plan: ActionPlan, action: Action, status: str):
    """Records a decision event in the agicore-memory service."""
    event = {
        "agent": agent,
        "action_plan_id": plan.plan_id,
        "action_taken": status,
        "risk_score": plan.risk_score,
        "reason": plan.description,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post("http://agicore-memory:8000/record-event", json=event, timeout=2.0)
            logger.info("Successfully recorded decision event", extra={"plan_id": plan.plan_id})
    except httpx.RequestError as e:
        # This will be caught by the circuit breaker
        raise pybreaker.CircuitBreakerError(f"Memory service unavailable: {e}")


# --- Cognitive Analysis (Simulating Internal Agents) ---
async def analyze_alert(alert: Alert, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Cognitive analysis simulating Architect, Coder, and QA-Tester agents.
    """
    logger.info("Architect Agent: Generating action plans...", extra={"alert_source": alert.source})
    # 1. Architect Agent: Generate plans based on the alert
    plans = [
        ActionPlan(plan_id="plan_restart_service", description=f"Restart the reported service: {alert.details.get('service')}", risk_score=0.2, estimated_cost=5.0),
        ActionPlan(plan_id="plan_scale_up", description="Scale up the backend service", risk_score=0.5, estimated_cost=15.0),
    ]

    # Simple logic to choose a plan
    if "down" in alert.message:
        selected_plan = plans[0]
    else:
        selected_plan = plans[1]

    logger.info(f"Coder Agent: Preparing patch for plan '{selected_plan.plan_id}'...", extra={"plan": selected_plan.model_dump()})
    # 2. Coder Agent: Define action for the selected plan
    action_to_take = Action(action_name=f"execute_{selected_plan.plan_id}", parameters=alert.details)

    logger.info("QA-Tester Agent: Simulating plan execution and validating KPIs...", extra={"plan_id": selected_plan.plan_id})
    # 3. QA-Tester Agent: Simulate validation. In a real system, this would be a complex check.
    qa_passed = selected_plan.risk_score < 0.7

    if not qa_passed:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"QA validation failed for high-risk plan '{selected_plan.plan_id}'.")
        raise HTTPException(status_code=418, detail="QA validation failed; proposed action is too risky.")

    # 4. Memory Agent: Record the decision
    background_tasks.add_task(
        record_decision_event,
        agent="AGIcoreManager",
        plan=selected_plan,
        action=action_to_take,
        status="executed"
    )

    return {"selected_plan": selected_plan, "action": action_to_take}


# --- API Endpoints ---
@app.post("/internal/alerts")
async def receive_alert_handler(alert: Alert, background_tasks: BackgroundTasks):
    """
    Receives an alert, triggers the cognitive workflow, and executes the plan.
    This endpoint has a low latency target (<50ms p99).
    """
    if MAINTENANCE_MODE.enabled:
        raise HTTPException(status_code=503, detail="Service is in maintenance mode. Non-critical operations are disabled.")

    try:
        analysis_result = await analyze_alert(alert, background_tasks)
        # In a real system, the action would be executed here asynchronously
        # background_tasks.add_task(execute_action, analysis_result["action"])
        
        return {
            "status": "plan_executed",
            "executed_plan": analysis_result["selected_plan"].model_dump(),
            "action": analysis_result["action"].model_dump()
        }
    except HTTPException as e:
        # Re-raise HTTPExceptions from analyze_alert directly
        raise e
    except pybreaker.CircuitBreakerError as e:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"Memory service circuit breaker is open. Reason: {e}")
        raise HTTPException(status_code=503, detail="Memory service is currently unavailable. Circuit breaker is open.")
    except Exception as e:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"An unexpected error occurred during analysis. Reason: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during alert analysis.")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "maintenance_mode": MAINTENANCE_MODE.enabled}

@app.get("/")
async def root():
    return {"message": "AGIcoreManager v2 is running."}
