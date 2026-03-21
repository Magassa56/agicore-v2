from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
from typing import Dict

# Import the core AGIcoreManager
from .meta_agents import AGIcoreManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AGIcore - Meta-SRE Core (MCP)",
    description="This service orchestrates the entire AGIcore system using a multi-agent architecture.",
    version="2.0.0"  # Version updated to reflect the evolution
)

class Objective(BaseModel):
    description: str
    params: Dict = {}

@app.post("/execute")
async def execute_objective(objective: Objective, background_tasks: BackgroundTasks):
    """
    Receives a high-level objective and executes it via the autonomous AGIcoreManager.
    The entire process (Plan -> Code -> Test -> Deploy) is handled asynchronously.
    """
    logger.info(f"Received new objective: {objective.description}")

    # The entire complex workflow is delegated to the AGIcoreManager
    # It runs in the background to avoid blocking the API
    background_tasks.add_task(AGIcoreManager.execute_objective, objective.description)

    return {
        "status": "Objective accepted",
        "objective": objective.description,
        "detail": "Processing started in the background. Monitor logs for progress."
    }

@app.get("/")
async def root():
    return {"message": "AGIcore Meta-SRE Core (MCP) v2.0 is running."}
