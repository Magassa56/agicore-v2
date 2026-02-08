
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import json
import time

# --- Setup & Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AGIcore - Local Worker",
    description="An autonomous worker for edge environments with unreliable connectivity.",
    version="1.0.0"
)

# This queue simulates a persistent outbox. In a real scenario, this would be
# a file-based queue or a lightweight local database like SQLite.
OUTBOX_DIR = "/app/outbox"
os.makedirs(OUTBOX_DIR, exist_ok=True)

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
    Executes tasks that can be handled locally or queues tasks that require cloud access.
    """
    logger.info(f"Local worker received task: {payload.task}")

    if payload.task == "simple_sentiment_analysis":
        # --- Local Execution ---
        # This is a simple, rule-based analysis that can run offline.
        text = payload.params.get("text", "")
        positive_words = ["good", "great", "success", "happy", "love"]
        negative_words = ["bad", "terrible", "failure", "sad", "hate"]
        
        score = 0
        for word in positive_words:
            if word in text.lower():
                score += 1
        for word in negative_words:
            if word in text.lower():
                score -= 1
        
        sentiment = "neutral"
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"
            
        logger.info(f"Performed local sentiment analysis. Result: {sentiment}")
        return ExecutionResult(
            task=payload.task,
            status="completed_local",
            result={"sentiment": sentiment, "score": score}
        )

    else:
        # --- Queue for Cloud Execution ---
        # If the task is not local, add it to the outbox to be sent later.
        logger.warning(f"Task '{payload.task}' cannot be handled locally. Queuing for cloud sync.")
        
        # Create a unique filename for the queued task
        queued_task_path = os.path.join(OUTBOX_DIR, f"{int(time.time())}_{payload.task}.json")
        
        try:
            with open(queued_task_path, "w") as f:
                f.write(payload.json())
        except IOError as e:
            logger.error(f"Failed to write task to outbox: {e}")
            raise HTTPException(status_code=500, detail="Failed to queue task for cloud execution.")

        return ExecutionResult(
            task=payload.task,
            status="queued_for_cloud",
            result={"message": "Task has been saved and will be processed when connectivity is restored."}
        )

@app.get("/outbox")
async def get_outbox():
    """
    Inspects the outbox to see which tasks are waiting for cloud sync.
    In a real system, a separate process would watch this and send the tasks.
    """
    try:
        tasks = os.listdir(OUTBOX_DIR)
        return {"queued_tasks": tasks, "count": len(tasks)}
    except OSError as e:
        logger.error(f"Could not read outbox directory: {e}")
        return {"queued_tasks": [], "count": 0}

@app.get("/")
async def root():
    return {"message": "AGIcore Local Worker is running."}
