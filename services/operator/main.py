
import logging
import asyncio
import httpx
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger
from prometheus_fastapi_instrumentator import Instrumentator
import pybreaker

# --- Configuration & State ---

class MaintenanceMode:
    def __init__(self):
        self._enabled = False
    @property
    def enabled(self): return self._enabled
    def enable(self): self._enabled = True
    def disable(self): self._enabled = False

MAINTENANCE_MODE = MaintenanceMode()

# --- Logging Setup ---
# Security Audit Logger
security_audit_handler = logging.FileHandler("security_audit.log")
security_audit_handler.setFormatter(jsonlogger.JsonFormatter())
security_logger = logging.getLogger("security_audit")
security_logger.addHandler(security_audit_handler)
security_logger.setLevel(logging.INFO)

# General and Incident Loggers
incident_log_path = "ops/logs/incidents.log"
os.makedirs(os.path.dirname(incident_log_path), exist_ok=True)
incident_handler = logging.FileHandler(incident_log_path)
incident_handler.setFormatter(jsonlogger.JsonFormatter())
incident_logger = logging.getLogger("incident_logger")
incident_logger.addHandler(incident_handler)
incident_logger.setLevel(logging.WARNING)

logger = logging.getLogger("agicore_manager")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# --- Circuit Breaker ---
memory_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=30)

app = FastAPI(
    title="AGIcoreManager - Meta-SRE (Niveau 8)",
    description="Autonomous orchestration with advanced security, cognitive feedback, and human-in-the-loop capabilities.",
    version="8.0.0"
)
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
    risk_score: float = Field(..., ge=0, le=10, description="Risk score on a scale of 0 to 10.")
    is_critical_action: bool = Field(False, description="True if the action requires human-in-the-loop.")

class Action(BaseModel):
    action_name: str
    parameters: Optional[Dict[str, Any]] = None

# --- Security Governor ---
class SecurityGovernor:
    def __init__(self, risk_threshold: float = 3.0):
        self.risk_threshold = risk_threshold

    def evaluate_plan(self, plan: ActionPlan) -> bool:
        """Evaluates a plan and blocks it if it's too risky."""
        if plan.risk_score > self.risk_threshold:
            security_logger.warning(
                "High-risk action blocked by Security Governor.",
                extra={"plan_id": plan.plan_id, "risk_score": plan.risk_score, "threshold": self.risk_threshold}
            )
            return False
        if plan.is_critical_action:
            security_logger.info(
                "Critical action flagged for Human-in-the-Loop.",
                extra={"plan_id": plan.plan_id, "risk_score": plan.risk_score}
            )
            # In a real system, this would trigger a notification and wait for approval.
            # For now, we just log it and let it proceed for demonstration.
        return True

SECURITY_GOVERNOR = SecurityGovernor()

# --- Incident Commander ---
class IncidentCommander:
    def __init__(self, threshold: int = 3):
        self.critical_incident_count = 0
        self.threshold = threshold

    def record_critical_incident(self, alert: Alert, reason: str):
        self.critical_incident_count += 1
        incident_logger.warning("Critical Incident", extra={"alert": alert.model_dump(), "reason": reason, "count": self.critical_incident_count})
        if self.critical_incident_count >= self.threshold and not MAINTENANCE_MODE.enabled:
            MAINTENANCE_MODE.enable()
            incident_logger.critical("MAINTENANCE MODE ACTIVATED")

INCIDENT_COMMANDER = IncidentCommander()

# --- Memory Service Integration ---
@memory_breaker
async def record_decision_event(agent: str, plan: ActionPlan, status: str) -> str:
    """Records a decision event and returns the memory event ID."""
    memory_event_id = f"evt-{uuid.uuid4()}"
    event = {
        "memory_event_id": memory_event_id,
        "agent": agent,
        "action_plan_id": plan.plan_id,
        "action_taken": status,
        "risk_score": plan.risk_score,
        "reason": plan.description,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    async with httpx.AsyncClient() as client:
        await client.post("http://agicore-memory:8000/record-event", json=event, timeout=2.0)
    logger.info("Successfully recorded decision event", extra={"memory_event_id": memory_event_id})
    return memory_event_id

# --- Cognitive Analysis ---
async def analyze_alert(alert: Alert, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    logger.info("Architect Agent: Generating action plans...", extra={"alert": alert.message})
    plans = [
        ActionPlan(plan_id="plan_restart_trader", description="Restart the agicore-trader service", risk_score=2.5, is_critical_action=False),
        ActionPlan(plan_id="plan_execute_trade", description="Execute a high-frequency trade", risk_score=8.0, is_critical_action=True),
    ]
    selected_plan = plans[0] if "down" in alert.message else plans[1]

    if not SECURITY_GOVERNOR.evaluate_plan(selected_plan):
        # No background task here, as the action is blocked.
        memory_event_id = await record_decision_event(agent="AGIcoreManager", plan=selected_plan, status="blocked")
        raise HTTPException(status_code=403, detail=f"Action blocked by Security Governor due to high risk (score: {selected_plan.risk_score}).")

    action_to_take = Action(action_name=f"execute_{selected_plan.plan_id}", parameters=alert.details)
    
    qa_passed = True # Simulate QA pass
    if not qa_passed:
        raise HTTPException(status_code=418, detail="QA validation failed.")

    memory_event_id = await record_decision_event(agent="AGIcoreManager", plan=selected_plan, status="executed")
    return {"selected_plan": selected_plan, "action": action_to_take, "memory_event_id": memory_event_id}

# --- API Endpoints ---
@app.post("/internal/alerts")
async def receive_alert_handler(alert: Alert, background_tasks: BackgroundTasks):
    if MAINTENANCE_MODE.enabled:
        raise HTTPException(status_code=503, detail="Service in maintenance mode.")

    try:
        start_time = datetime.now(timezone.utc)
        result = await analyze_alert(alert, background_tasks)
        latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return {
            "agent": "AGIcoreManager",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_plan_id": result["selected_plan"].plan_id,
            "action_taken": "executed",
            "risk_score": result["selected_plan"].risk_score,
            "latency_ms": round(latency_ms, 2),
            "reason": result["selected_plan"].description,
            "memory_event_id": result["memory_event_id"]
        }
    except HTTPException as e:
        raise e
    except pybreaker.CircuitBreakerError as e:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"Memory service circuit breaker open: {e}")
        raise HTTPException(status_code=503, detail=f"Memory service unavailable: {e}")
    except httpx.RequestError as e:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"Memory service connection failed: {e}")
        raise HTTPException(status_code=503, detail=f"Memory service connection failed: {e}")
    except Exception as e:
        INCIDENT_COMMANDER.record_critical_incident(alert, f"Unexpected error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "maintenance_mode": MAINTENANCE_MODE.enabled}

@app.get("/")
async def root():
    return {"message": "AGIcoreManager v8 is running."}
