
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import os
import time
import uuid
from pythonjsonlogger import jsonlogger

# --- Loggers ---

# General service logger
logger = logging.getLogger("hmi_service")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Immutable log for physical actions
hmi_log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ops', 'logs', 'hmi_actions.log')
os.makedirs(os.path.dirname(hmi_log_path), exist_ok=True)
hmi_handler = logging.FileHandler(hmi_log_path)
hmi_formatter = logging.Formatter('%(asctime)s - %(message)s') # Plain text for immutability
hmi_handler.setFormatter(hmi_formatter)
hmi_logger = logging.getLogger("hmi_physical_actions")
hmi_logger.addHandler(hmi_handler)
hmi_logger.setLevel(logging.INFO)


# --- In-memory store for pending transactions ---
# In a real system, this would be a persistent store like Redis or a database.
pending_transactions: Dict[str, Dict[str, Any]] = {}


# --- FastAPI App & Models ---
app = FastAPI(
    title="AGIcore - HMI (Human-Machine Interface)",
    description="A service for controlling physical hardware with safety guarantees.",
    version="1.0.0"
)

class ExecutionPayload(BaseModel):
    task: str
    params: Dict[str, Any] = {}

class ExecutionResult(BaseModel):
    task: str
    status: str
    result: Dict[str, Any]

# --- Endpoints ---
@app.post("/execute", response_model=ExecutionResult)
async def execute_task(payload: ExecutionPayload):
    """
    Generic endpoint for handling physical control tasks.
    Implements a two-phase commit for safety.
    """
    task = payload.task
    params = payload.params
    
    if task == "prepare_physical_action":
        action = params.get("action")
        if not action:
            raise HTTPException(status_code=400, detail="Missing 'action' parameter.")
            
        transaction_id = str(uuid.uuid4())
        
        # Store the action, awaiting commit
        pending_transactions[transaction_id] = {"action": action, "status": "prepared"}
        
        # Log to the immutable journal
        hmi_logger.info(f"[PREPARE] transaction_id={transaction_id}, action={action}")
        
        logger.info("Physical action prepared", extra={"transaction_id": transaction_id, "action": action})
        
        return ExecutionResult(
            task=task,
            status="prepared",
            result={"transaction_id": transaction_id, "message": "Action is prepared. Awaiting commit."}
        )

    elif task == "commit_physical_action":
        transaction_id = params.get("transaction_id")
        if not transaction_id or transaction_id not in pending_transactions:
            raise HTTPException(status_code=404, detail="Transaction ID not found or invalid.")
        
        if pending_transactions[transaction_id]["status"] != "prepared":
            raise HTTPException(status_code=400, detail="Transaction is not in a 'prepared' state.")

        action = pending_transactions[transaction_id]["action"]
        
        # --- THIS IS WHERE THE PHYSICAL ACTION WOULD HAPPEN ---
        logger.info(f"Executing physical action: {action}")
        # e.g., send_command_to_robot_arm(action)
        # ----------------------------------------------------
        
        pending_transactions[transaction_id]["status"] = "committed"
        hmi_logger.info(f"[COMMIT] transaction_id={transaction_id}, action={action}")
        
        return ExecutionResult(
            task=task,
            status="committed",
            result={"transaction_id": transaction_id, "message": "Physical action committed successfully."}
        )

    elif task == "rollback_physical_action":
        transaction_id = params.get("transaction_id")
        if not transaction_id or transaction_id not in pending_transactions:
            raise HTTPException(status_code=404, detail="Transaction ID not found or invalid.")
            
        action = pending_transactions[transaction_id]["action"]
        pending_transactions.pop(transaction_id) # Remove from pending
        
        hmi_logger.info(f"[ROLLBACK] transaction_id={transaction_id}, action={action}")
        
        return ExecutionResult(
            task=task,
            status="rolled_back",
            result={"transaction_id": transaction_id, "message": "Physical action rolled back."}
        )
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown task: {task}")

@app.get("/")
async def root():
    return {"message": "AGIcore HMI is running."}
