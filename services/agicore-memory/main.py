
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import os
import datetime
from pythonjsonlogger import jsonlogger

# --- Logger for Persistent Memory ---
# This logger's sole purpose is to write to the append-only memory file.
MEMORY_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'ops', 'memory', 'events.log')
os.makedirs(os.path.dirname(MEMORY_LOG_PATH), exist_ok=True)

memory_handler = logging.FileHandler(MEMORY_LOG_PATH)
# The formatter outputs the JSON of the event directly.
memory_formatter = logging.Formatter('%(message)s')
memory_handler.setFormatter(memory_formatter)

memory_logger = logging.getLogger("agicore_memory")
memory_logger.addHandler(memory_handler)
memory_logger.setLevel(logging.INFO)


# --- FastAPI App & Models ---
app = FastAPI(
    title="AGIcore - Memory Service",
    description="Handles the creation and storage of persistent MemoryEvents.",
    version="1.0.0"
)

class MemoryEvent(BaseModel):
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    agent: str
    signal: str
    hypotheses: List[str]
    action: Dict[str, Any]
    estimated_cost: float
    actual_result: str = "pending"
    delta: float = 0.0
    post_action_confidence: float = 0.0

@app.post("/record-event")
async def record_event(event: MemoryEvent):
    """
    Receives a MemoryEvent and records it to the persistent, append-only log.
    """
    try:
        # The memory_logger is configured to log the raw message, so we pass the JSON dict.
        memory_logger.info(event.json())
        return {"status": "memory_recorded", "event_id": event.timestamp}
    except Exception as e:
        logging.error(f"Failed to record memory event: {e}")
        raise HTTPException(status_code=500, detail="Failed to write to persistent memory.")

@app.get("/")
async def root():
    return {"message": "AGIcore Memory Service is running."}
